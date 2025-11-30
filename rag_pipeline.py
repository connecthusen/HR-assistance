# rag_pipeline.py

import os
import logging
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import GoogleGenerativeAiEmbeddingFunction
import google.generativeai as genai

from utils.pdf_loader import extract_text_from_pdf
from utils.text_splitter import split_text_into_chunks

# ================== LOGGING ==================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== LOAD ENV ==================
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)

# ================== CONFIG ==================
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "hr_policies"
EMBEDDING_MODEL = "models/text-embedding-004"
CHAT_MODEL = "models/gemini-2.5-pro"

# ================== CHROMA DB ==================
def initialize_chroma_db():
    try:
        client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        logger.info(f"✓ Chroma DB initialized at {CHROMA_DB_PATH}")
        return client
    except Exception as e:
        logger.error(f"✗ Failed to initialize Chroma: {e}")
        raise


def get_or_create_collection(client):
    embedding_fn = GoogleGenerativeAiEmbeddingFunction(
        api_key=GEMINI_KEY,
        model_name=EMBEDDING_MODEL
    )
    try:
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"✓ Collection '{COLLECTION_NAME}' ready. Docs: {collection.count()}")
        return collection
    except Exception as e:
        logger.error(f"✗ Failed to create collection: {e}")
        raise

# ================== INGESTION ==================
def ingest_pdfs(pdf_paths: list, collection):
    documents, metadatas, ids = [], [], []

    for pdf_path in pdf_paths:
        logger.info(f"Processing PDF: {pdf_path}")
        text = extract_text_from_pdf(pdf_path)
        if not text:
            logger.warning(f"No text found in {pdf_path}")
            continue

        chunks = split_text_into_chunks(text, chunk_size=800, overlap=200)
        filename = os.path.basename(pdf_path)

        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({"source": filename, "chunk_id": i})
            ids.append(f"{filename}_chunk_{i}")

    if documents:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        logger.info(f"✓ Ingested {len(documents)} chunks from {len(pdf_paths)} PDFs")
    else:
        logger.warning("✗ No documents to ingest")


# ================== RETRIEVAL ==================
def retrieve_chunks(query: str, collection, n_results=3):
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

        retrieved = []
        if results and results.get("documents"):
            for i, (doc, meta, dist) in enumerate(
                zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
            ):
                retrieved.append({
                    "rank": i + 1,
                    "content": doc,
                    "source": meta.get("source", "Unknown"),
                    "similarity": 1 - dist
                })
        return retrieved
    except Exception as e:
        logger.error(f"✗ Retrieval error: {e}")
        return []

# ================== GENERATION ==================
def generate_response(query: str, retrieved_docs: list):
    if not retrieved_docs:
        return "No HR policy information available."

    context = "\n\n".join(f"[Source: {d['source']}]\n{d['content']}" for d in retrieved_docs)
    prompt = f"""
Answer the question based ONLY on this context:

{context}

Question: {query}

If answer not found, say "No HR policy information available."
"""
    try:
        model = genai.GenerativeModel(CHAT_MODEL)
        response = model.generate_content(contents=prompt)
        return response.text
    except Exception as e:
        logger.error(f"✗ Gemini generation failed: {e}")
        return f"Error: {e}"

# ================== RAG QUERY ==================
def rag_query(query: str, collection, n_results=3):
    logger.info(f"\n📌 Query: {query}")
    retrieved = retrieve_chunks(query, collection, n_results)
    answer = generate_response(query, retrieved)

    return {
        "response": answer,
        "sources": [d["source"] for d in retrieved],
        "metadata": {"docs_retrieved": len(retrieved), "model": CHAT_MODEL}
    }
if __name__ == "__main__":
    client = initialize_chroma_db()
    collection = get_or_create_collection(client)

    # Read ALL PDFs automatically from folder
    folder = "data/hr_policies"
    pdf_paths = [
        os.path.join(folder, filename)
        for filename in os.listdir(folder)
        if filename.endswith(".pdf")
    ]

    print("PDFs found:", pdf_paths)

    ingest_pdfs(pdf_paths, collection)

    print("Ingestion done!")
