HR AI Assistant – RAG-Based Policy Query System

An intelligent HR Policy Assistant built using Streamlit, Google Gemini, and ChromaDB.
The app allows employees to ask natural-language questions about company HR policies such as Code of Conduct, Leave Policy, and Attendance Policy—with answers grounded strictly in your uploaded PDFs.

This project uses a full Retrieval-Augmented Generation (RAG) pipeline, custom embeddings, document chunking, vector search, and a polished conversational UI.

⭐ 1. Overview

The HR AI Assistant is designed to provide instant, accurate answers to HR-related questions. Instead of manually searching through policy PDFs, employees can simply ask questions and receive precise responses backed by retrieved policy sections.

This assistant is especially useful for:

Quick HR clarifications

New employees onboarding

Reducing HR workload

Improving policy transparency

Using Google Gemini models, the system embeds documents, stores vectors in ChromaDB, retrieves the most relevant chunks, and generates responses in a clean Streamlit chat interface enhanced with custom CSS styling.

✨ 2. Features
🔍 Retrieval-Augmented Generation (RAG)

Extracts text from PDFs

Splits long documents into overlapping chunks

Generates embeddings using Gemini

Stores vectors in ChromaDB

Retrieves top-matching policy chunks

Generates final answers grounded in retrieved evidence

🗂️ Policy Documents Included

Leave Policy

Code of Conduct

Attendance Policy
(You can add as many PDFs as needed.)

💬 Chat-style UI

Clean Streamlit interface

Scrollable chat history

Stylish message bubbles

Professional header and typography

⚡ Smart Greeting Handler

Detects small-talk greetings and replies with a friendly predefined message.

🧩 Error Handling

Missing API key

Failed DB initialization

Retrieval/Generation errors

⚠️ 3. Limitations

Works only on the HR PDFs added by the admin.

Cannot accept PDF uploads from end-users (yet).

Multi-user sessions are not isolated (Streamlit default).

Quality depends on clarity of policy documents.

Requires a valid Gemini API Key.

🏗️ 4. Tech Stack
Frontend

Streamlit

Custom HTML + CSS

Responsive chat interface

Backend & ML

Google Gemini (text-embedding-004, gemini-2.5-pro)

ChromaDB PersistentClient

Python 3.11

Utilities

dotenv

PyPDF text extraction

Custom text splitter

```

📁 5. Project Structure
HR/
│── app.py                     # Streamlit interface
│── embedder.py                # Standalone embedding generator
│── rag_pipeline.py            # RAG pipeline (ingestion, retrieval, generation)
│── requirements.txt
│── .env                       # Gemini API key
│── hr_logo.png                # App logo
│
├── data/
│   └── hr_policies/
│       ├── Leave_policy.pdf
│       ├── Code_of_Conduct.pdf
│       └── Attendance_Policy.pdf
│
├── chroma_db/                # Local vector database
│
└── utils/
    ├── pdf_loader.py
    └── text_splitter.py

🧠 6. Architecture Diagram
                     ┌───────────────────────┐
                     │      User (Query)      │
                     └───────────┬───────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │ Streamlit Chat Input  │
                     └───────────┬───────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │ Greeting Handler ?     │───▶ Yes → Short canned reply
                     └───────────┬───────────┘
                                 │ No
                                 ▼
                     ┌──────────────────────────────┐
                     │ Generate Query Embedding      │
                     │ (Gemini text-embedding-004)   │
                     └───────────┬───────────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────────┐
                  │     ChromaDB Vector Search        │
                  │  Retrieve top-k matching chunks   │
                  └───────────┬───────────────────────┘
                              │
                              ▼
        ┌────────────────────────────────────────────────┐
        │ Gemini LLM (gemini-2.5-pro)                    │
        │ Synthesize final answer strictly from context  │
        └───────────────────┬────────────────────────────┘
                            │
                            ▼
                 ┌────────────────────────┐
                 │ Streamlit Chat Output  │
                 └────────────────────────┘

```

⚙️ 7. Installation & Setup
1. Clone Repository
git clone <your_repo_link>
cd HR

2. Install Dependencies
pip install -r requirements.txt

3. Create .env File
GEMINI_API_KEY=your_actual_key_here

4. Add HR PDFs

Place policy PDFs inside:

data/hr_policies/

🧩 8. Embedding & Ingestion

Before running the app, ingest all PDFs into ChromaDB:

python rag_pipeline.py


This will:

Extract text

Split into chunks

Generate embeddings

Add vectors to ChromaDB

▶️ 9. Running the App

Start the Streamlit interface:

streamlit run app.py


The app will open in your browser with:

Header + Logo

Chat Interface

Automated response with retrieved sources

🧪 10. Test Scripts (Optional)

Test embeddings:

python test_embeddings.py


Test retrieval:

python test_retrieval.py


Test PDF extraction:

python test_pdf.py

🚀 11. Potential Improvements

🔐 Add user authentication

📤 Allow HR admins to upload new PDFs dynamically

📊 Add analytics dashboard (frequent HR queries)

🧵 Improve session isolation for multiple users

🏷 Provide citations with chunk previews

🐳 Add Docker support

📚 Add additional department policies
