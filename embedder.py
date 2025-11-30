# embedder.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Load API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Embedding Model
EMBEDDING_MODEL = "models/text-embedding-004"

def get_embedding(text: str):
    """Generate embedding using Gemini."""
    response = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_document"   # or "retrieval_query"
    )
    return response["embedding"]
