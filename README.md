# HR Policy Assistant — Setup Guide

A RAG-powered chatbot that answers employee questions from HR policy PDFs,
built with **Streamlit**, **ChromaDB**, and **Google Gemini 2.5 Pro**.

---

## Project Structure

```
hr_assistant/
├── app.py                    # Streamlit UI
├── rag_pipeline.py           # ChromaDB + Gemini RAG logic
├── ingest.py                 # One-time PDF ingestion script
├── requirements.txt
├── .env                      # Your API key (never commit this)
├── utils/
│   ├── pdf_loader.py         # PDF text extraction
│   └── text_splitter.py      # Chunking logic
└── data/
    └── hr_policies/          # ← Place your PDF files here
        ├── leave_policy.pdf
        ├── Attendance_Policy.pdf
        └── Code_of_Conduct.pdf
```

---

## Quick Start

### 1. Clone / copy the project folder

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set your Gemini API key
Edit `.env`:
```
GEMINI_API_KEY=your_actual_key_here
```

### 5. Add your HR policy PDFs
Copy your PDFs into `data/hr_policies/`.

### 6. Ingest PDFs into ChromaDB (run once)
```bash
python ingest.py
```

### 7. Launch the app
```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## Notes
- ChromaDB data is saved in `./chroma_db/` — keep this folder between runs.
- Re-run `python ingest.py` only when you add new PDFs; existing chunks are skipped.
- To reset the database, delete the `chroma_db/` folder and re-ingest.
