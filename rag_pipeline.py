import os
import logging
from dotenv import load_dotenv
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from groq import Groq
from sentence_transformers import SentenceTransformer

from utils.pdf_loader import extract_text_from_pdf
from utils.text_splitter import split_text_into_chunks

# ── Setup ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()
GROQ_KEY = os.getenv("GROQ_API_KEY", "")

CHROMA_DB_PATH  = "./chroma_db"
COLLECTION_NAME = "hr_policies_hf"
LLM_MODEL       = "llama-3.3-70b-versatile"

# ── Singleton Clients ────────────────────────────────────────────────────────
_groq_client = None
_embed_model  = None

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        if not GROQ_KEY:
            raise ValueError("GROQ_API_KEY not found in .env")
        _groq_client = Groq(api_key=GROQ_KEY)
    return _groq_client

def get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        logger.info("Loading embedding model (cached to ./model_cache)...")
        _embed_model = SentenceTransformer(
            'all-MiniLM-L6-v2',
            cache_folder="./model_cache"
        )
        logger.info("Embedding model ready.")
    return _embed_model

# ─────────────────────────────────────────────────────────────────────────────
# EMBEDDING FUNCTION — inherits ChromaDB's official EmbeddingFunction base
# This is the CORRECT interface. ChromaDB calls __call__ for both ingestion
# and queries. No embed_query needed or wanted.
# ─────────────────────────────────────────────────────────────────────────────

class HFEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        if isinstance(input, str):
            input = [input]
        model = get_embed_model()
        return model.encode(list(input), show_progress_bar=False).tolist()

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────────────────────────────────────

def initialize_chroma_db():
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)

def get_or_create_collection(client):
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=HFEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"},
    )

# ─────────────────────────────────────────────────────────────────────────────
# INGESTION
# ─────────────────────────────────────────────────────────────────────────────

def ingest_pdfs(pdf_paths: list, collection):
    existing_ids = set(collection.get()["ids"])
    documents, metadatas, ids = [], [], []

    for pdf_path in pdf_paths:
        text = extract_text_from_pdf(pdf_path)
        if not text:
            logger.warning(f"No text extracted from {pdf_path}, skipping.")
            continue

        chunks   = split_text_into_chunks(text, chunk_size=700, overlap=100)
        filename = os.path.basename(pdf_path)

        for i, chunk in enumerate(chunks):
            doc_id = f"{filename}_{i}"
            if doc_id in existing_ids:
                continue
            documents.append(chunk)
            metadatas.append({"source": filename})
            ids.append(doc_id)

    if documents:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        logger.info(f"✓ Ingested {len(documents)} new chunks.")
    else:
        logger.info("No new chunks to ingest.")

# ─────────────────────────────────────────────────────────────────────────────
# QUERY
# ─────────────────────────────────────────────────────────────────────────────

def rag_query(query: str, collection, n_results: int = 4) -> dict:
    try:
        total_docs = collection.count()
        if total_docs == 0:
            return {
                "response": "⚠️ The policy database is empty. Please run `python ingest.py` first.",
                "sources": [],
            }

        safe_n = min(n_results, total_docs)
        results = collection.query(query_texts=[query], n_results=safe_n)

        if not results or not results.get("documents") or not results["documents"][0]:
            return {
                "response": "⚠️ No relevant policy information found. Try rephrasing your question.",
                "sources": [],
            }

        retrieved_docs = [
            {"content": doc, "source": meta.get("source", "Unknown")}
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ]
        context = "\n\n---\n\n".join(d["content"] for d in retrieved_docs)

        groq_client = get_groq_client()
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful HR Assistant for ABC Corp. "
                        "Answer ONLY based on the provided policy context. "
                        "If the answer is not in the context, politely say you don't have that information. "
                        "Use clear bullet points in your response."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {query}",
                },
            ],
            model=LLM_MODEL,
            temperature=0.1,
            max_tokens=800,
            top_p=1,
            stream=False,
        )

        return {
            "response": chat_completion.choices[0].message.content,
            "sources":  list({d["source"] for d in retrieved_docs}),
        }

    except Exception as e:
        logger.error(f"Groq RAG Error: {e}")
        return {"response": f"Error: {str(e)}", "sources": []}