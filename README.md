# 🛡️ HR Policy Assistant
### AI-Powered Policy Q&A for ABC Corp

> An intelligent RAG chatbot that answers employee questions directly from HR policy documents — instantly, accurately, and with source citations.

---

## 📌 Overview

The **HR Policy Assistant** is a production-ready Retrieval-Augmented Generation (RAG) application built for ABC Corp. Employees can ask natural-language questions about company HR policies and receive precise, grounded answers — no more digging through PDF documents manually.

| Feature | Detail |
|---|---|
| **LLM** | Llama 3.3 70B (via Groq) |
| **Embeddings** | `all-MiniLM-L6-v2` (local, Hugging Face) |
| **Vector Store** | ChromaDB (persistent, local) |
| **Frontend** | Streamlit |
| **Policies Covered** | Leave · Attendance · Code of Conduct |

---

## 🏗️ Architecture

```
User Question
     │
     ▼
[Streamlit UI]  ──────────────────────────────────────┐
     │                                                 │
     ▼                                                 │
[HF Embeddings]  →  [ChromaDB Vector Store]           │
  (local model)       (semantic search)               │
                           │                          │
                           ▼                          │
                    [Top-4 Relevant Chunks]            │
                           │                          │
                           ▼                          │
                  [Groq — Llama 3.3 70B]  ◄───────────┘
                           │
                           ▼
                  [Answer + Source Tags]
```

---

## 📁 Project Structure

```
hr_assistant/
│
├── app.py                    # Streamlit chat interface
├── rag_pipeline.py           # Core RAG logic (embed, retrieve, generate)
├── ingest.py                 # One-time PDF ingestion script
├── requirements.txt          # Python dependencies
├── .env                      # API keys (never commit)
├── README.md
│
├── utils/
│   ├── pdf_loader.py         # PDF text extraction (pypdf)
│   └── text_splitter.py      # Chunking with overlap
│
└── data/
    └── hr_policies/          # ← Place your HR PDF files here
        ├── leave_policy.pdf
        ├── Attendance_Policy.pdf
        └── Code_of_Conduct.pdf
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.10 or higher
- A free [Groq API key](https://console.groq.com)

---

### Step 1 — Clone or copy the project

```bash
# If using git
git clone <your-repo-url>
cd hr_assistant

# Or just copy the folder to your machine
```

---

### Step 2 — Create a virtual environment

```bash
python -m venv venv

# Activate (macOS / Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

---

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** The first run will download the `all-MiniLM-L6-v2` embedding model (~90 MB) and cache it to `./model_cache/`. This is a one-time download.

---

### Step 4 — Configure API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your free key at → [console.groq.com](https://console.groq.com)

---

### Step 5 — Add HR policy PDFs

Place your PDF files in the `data/hr_policies/` folder:

```
data/
└── hr_policies/
    ├── leave_policy.pdf
    ├── Attendance_Policy.pdf
    └── Code_of_Conduct.pdf
```

---

### Step 6 — Ingest PDFs into ChromaDB *(run once)*

```bash
python ingest.py
```

Expected output:
```
──────────────────────────────────────────────────
  HR Policy Assistant — PDF Ingestion (HF + Groq Edition)
──────────────────────────────────────────────────
Found 3 PDFs. Starting local ingestion...
✓ Ingested 42 new chunks.
✓ SUCCESS! Total chunks in DB: 42
You can now run 'streamlit run app.py'
```

> **Re-run ingestion** only when you add new PDF files. Existing chunks are automatically skipped.

---

### Step 7 — Launch the app

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## 💬 Usage

| Query Type | Example |
|---|---|
| Leave entitlement | *"How many casual leaves do I get per year?"* |
| Sick leave rules | *"Do I need a medical certificate for sick leave?"* |
| Attendance | *"What are the office hours at ABC Corp?"* |
| Code of conduct | *"What is the policy on using company equipment?"* |
| Maternity/paternity | *"How many weeks of maternity leave am I entitled to?"* |

The assistant will respond with a clear, grounded answer and display the **source document(s)** it referenced.

---

## 🔄 Adding New Policies

1. Drop the new PDF into `data/hr_policies/`
2. Re-run ingestion:
   ```bash
   python ingest.py
   ```
3. Restart the Streamlit app

No code changes needed.

---

## 🗄️ Resetting the Database

To wipe ChromaDB and start fresh:

```bash
rm -rf ./chroma_db
python ingest.py
```

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web chat interface |
| `chromadb` | Local vector database |
| `sentence-transformers` | Local HF embedding model |
| `groq` | Llama 3.3 70B via Groq API |
| `pypdf` | PDF text extraction |
| `python-dotenv` | Environment variable management |

---

## 🔐 Security Notes

- **Never commit `.env`** — add it to `.gitignore`
- The `chroma_db/` folder contains your embedded policy data — keep it secure
- All embeddings are generated **locally** (no data sent to external servers for embeddings)
- Only the final query + retrieved context is sent to Groq for generation

---

## 🛠️ Troubleshooting

| Issue | Fix |
|---|---|
| `GROQ_API_KEY not set` | Create `.env` with your Groq key |
| `0 chunks in DB` | Check that PDFs have selectable text (not scanned images) |
| Embedding model slow on first run | Normal — model downloads once to `./model_cache` |
| `collection not found` | Run `python ingest.py` before launching the app |
| Port 8501 in use | Run `streamlit run app.py --server.port 8502` |

---

## 📄 License

Internal use only — ABC Corp © 2025