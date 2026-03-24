# app.py — HR Policy Assistant (ABC Corp)

import streamlit as st
from rag_pipeline import initialize_chroma_db, get_or_create_collection, rag_query, ingest_pdfs
import os
from dotenv import load_dotenv

load_dotenv()

PDF_FOLDER = "./data/hr_policies"

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# GLOBAL CSS (Updated for Fixed Header & Native Scrolling)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=DM+Serif+Display&display=swap');

html, body, .stApp {
    font-family: 'DM Sans', sans-serif;
    background: #f5f4f0 !important;
    color: #1a1a2e;
}

/* Scrollable Container Fix: Let Streamlit scroll naturally */
.main-scroll-container {
    margin-top: 80px;
    padding-bottom: 100px;
    padding-left: 20px;
    padding-right: 20px;
    display: flex;
    flex-direction: column;
}

/* hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── HEADER ── */
.hr-header {
    background: #0f2044;
    padding: 16px 40px;
    display: flex;
    align-items: center;
    gap: 14px;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    width: 100%;
    z-index: 9999;
    box-shadow: 0 2px 16px rgba(0,0,0,.3);
}
.hr-header-icon {
    width: 42px; height: 42px;
    background: #1e3a6e;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
}
.hr-header-title {
    font-family: 'DM Serif Display', serif;
    font-size: 19px;
    color: #ffffff;
}
.hr-header-sub {
    font-size: 11.5px;
    color: #8aaad4;
    font-weight: 300;
}

/* ── CHAT BUBBLES ── */
.chat-turn { display: flex; gap: 10px; margin-bottom: 16px; animation: fadeUp .25s ease; }
.chat-turn.user-turn { flex-direction: row-reverse; }
.avatar { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 15px; }
.avatar.bot-av { background: #0f2044; }
.avatar.user-av { background: #dde5f5; }
.bubble { max-width: 78%; padding: 13px 17px; border-radius: 16px; font-size: 14.5px; line-height: 1.7; box-shadow: 0 1px 5px rgba(0,0,0,.07); }
.bubble.bot-bubble { background: #ffffff; color: #1a1a2e; border-top-left-radius: 4px; }
.bubble.user-bubble { background: #0f2044; color: #deeaff; border-top-right-radius: 4px; }

.src-tag { display: inline-block; background: #eef3ff; color: #1e40af; font-size: 11px; padding: 2px 10px; border-radius: 12px; margin: 2px 3px 2px 0; border: 1px solid #c7d7ff; }

/* ── STICKY INPUT ── */
.stChatInputContainer {
    position: fixed !important;
    bottom: 0 !important;
    background: #f0efe9 !important;
    padding: 15px !important;
    z-index: 1000 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
GREETINGS = {"hi", "hello", "hey"}
GREETING_REPLY = "Hello! 👋 I'm your HR Policy Assistant. Ask me about Leave, Attendance, or Code of Conduct."

def render_bot(content: str, sources: list = None):
    src_html = ""
    if sources:
        tags = "".join(f'<span class="src-tag">📄 {s}</span>' for s in sorted(set(sources)))
        src_html = f'<hr style="border-top:1px solid #eee; margin:10px 0;"><div style="font-size:10px; color:#999;">SOURCES</div>{tags}'
    st.markdown(f'<div class="chat-turn"><div class="avatar bot-av">🛡️</div><div class="bubble bot-bubble">{content}{src_html}</div></div>', unsafe_allow_html=True)

def render_user(content: str):
    st.markdown(f'<div class="chat-turn user-turn"><div class="avatar user-av">👤</div><div class="bubble user-bubble">{content}</div></div>', unsafe_allow_html=True)

def auto_ingest(collection):
    """Automatically ingest PDFs if the collection is empty (first run only)."""
    if collection.count() > 0:
        return  # Already has data — skip

    pdf_paths = [
        os.path.join(PDF_FOLDER, f)
        for f in os.listdir(PDF_FOLDER)
        if f.lower().endswith(".pdf")
    ] if os.path.isdir(PDF_FOLDER) else []

    if not pdf_paths:
        st.warning("⚠️ No PDFs found in `data/hr_policies/`. Add policy PDFs and restart.")
        return

    with st.spinner(f"📚 First-time setup: Indexing {len(pdf_paths)} policy document(s)... This takes ~30 seconds."):
        ingest_pdfs(pdf_paths, collection)

    st.success(f"✅ {len(pdf_paths)} policy document(s) indexed! Ready to answer questions.")
    st.rerun()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hr-header">
    <div class="hr-header-icon">🛡️</div>
    <div>
        <div class="hr-header-title">HR Policy Assistant</div>
        <div class="hr-header-sub">ABC Corp · Llama 3.3 (Groq) + HF Local</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INITIALIZATION — DB + AUTO-INGEST
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "collection" not in st.session_state:
    if not os.getenv("GROQ_API_KEY"):
        st.error("⚠️ `GROQ_API_KEY` not set in .env")
    else:
        try:
            client = initialize_chroma_db()
            st.session_state.collection = get_or_create_collection(client)
            # ── Runs automatically on first launch ──
            auto_ingest(st.session_state.collection)
        except Exception as e:
            st.error(f"❌ Database Error: {e}")

# ─────────────────────────────────────────────
# RENDER CHAT
# ─────────────────────────────────────────────
st.markdown('<div class="main-scroll-container">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.info("👋 Welcome! Type your HR query below to search policy documents.")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        render_user(msg["content"])
    else:
        render_bot(msg["content"], msg.get("sources"))

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INPUT
# ─────────────────────────────────────────────
prompt = st.chat_input("Ask about leave, attendance...")

if prompt:
    # 1. Append user prompt
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Generate response
    if prompt.lower() in GREETINGS:
        reply, sources = GREETING_REPLY, []
    else:
        with st.spinner("Searching..."):
            result = rag_query(prompt, st.session_state.collection)
            reply = result["response"]
            sources = result.get("sources", [])

    # 3. Append assistant response
    st.session_state.messages.append({"role": "assistant", "content": reply, "sources": sources})

    # 4. Rerun to show new messages alongside old ones
    st.rerun()