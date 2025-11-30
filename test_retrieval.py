import os
from dotenv import load_dotenv
import chromadb
import google.generativeai as genai
from chromadb.utils.embedding_functions import GoogleGenerativeAiEmbeddingFunction

# ================== ENV ==================
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)

CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "hr_policies"
CHAT_MODEL = "models/gemini-2.5-pro"

# ================== CHROMA ==================
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

embedding_fn = GoogleGenerativeAiEmbeddingFunction(
    api_key=GEMINI_KEY,
    model_name="models/text-embedding-004"
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn
)


# ================== RETRIEVAL ==================
def retrieve_chunks(query: str, n_results=5):
    print("\n📡 Searching ChromaDB...")
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    return results


# ================== ANSWERING ==================
def answer_query(query: str):
    results = retrieve_chunks(query)

    docs = results["documents"][0]

    print("\n📄 Top Retrieved Chunks:")
    for i, doc in enumerate(docs):
        print(f"\n--- Chunk {i + 1} ---\n{doc}")

    if not docs:
        print("\nNo matching HR policy found.")
        return

    context = "\n\n".join(docs)

    prompt = f"""
Use ONLY the following context to answer:

Context:
{context}

Question:
{query}

If not found in context, say: "No HR policy information available."
"""

    model = genai.GenerativeModel(CHAT_MODEL)
    response = model.generate_content(prompt)

    print("\n💬 Final Answer:\n", response.text)


if __name__ == "__main__":
    query = input("Enter your question: ")
    answer_query(query)
