import os
import sys
from dotenv import load_dotenv
# This imports your NEW Hugging Face + Groq logic
from rag_pipeline import initialize_chroma_db, get_or_create_collection, ingest_pdfs

load_dotenv()
PDF_FOLDER = "./data/hr_policies"

if __name__ == "__main__":
    print("─" * 50)
    print("  HR Policy Assistant — PDF Ingestion (HF + Groq Edition)")
    print("─" * 50)

    # 1. Check for Groq instead of Gemini
    if not os.getenv("GROQ_API_KEY"):
        print("✗ ERROR: GROQ_API_KEY not found in .env file.")
        sys.exit(1)

    # 2. Initialize DB (Now using Local Hugging Face Embeddings)
    client = initialize_chroma_db()
    collection = get_or_create_collection(client)

    # 3. Find PDFs
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
        print(f"Created folder: {PDF_FOLDER}. Please put your PDFs there.")
        sys.exit(0)

    pdf_paths = [os.path.join(PDF_FOLDER, f) for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]
    
    if pdf_paths:
        print(f"Found {len(pdf_paths)} PDFs. Starting local ingestion...")
        ingest_pdfs(pdf_paths, collection)
        
        # 4. FINAL VERIFICATION
        count = collection.count()
        if count > 0:
            print(f"\n✓ SUCCESS! Total chunks in DB: {count}")
            print("You can now run 'streamlit run app.py'")
        else:
            print("\n✗ ERROR: Ingestion completed but 0 chunks were added. Check your PDF text.")
    else:
        print(f"✗ No PDFs found in {PDF_FOLDER}")