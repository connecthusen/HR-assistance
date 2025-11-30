import streamlit as st
from rag_pipeline import initialize_chroma_db, get_or_create_collection, rag_query
import time
import os

# -------------------- PAGE CONFIG --------------------
# Using a neutral icon for the page tab
st.set_page_config(page_title="HR AI Assistant", page_icon="🤖", layout="wide")

# -------------------- CUSTOM STYLING --------------------
st.markdown(
    """
    <style>
    /* Set a professional font stack globally and ensure normal size */
    html, body, .stApp, .stChatMessage p {
        font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
        font-size: 16px; /* Normal size */
    }

    /* Main layout container for the chat history, making it scrollable and visually distinct */
    .stApp > div:nth-child(1) > div:nth-child(1) > div.main > div.block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .header-container {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 15px 0;
    }
    .header-icon {
        /* Using a neutral blue background for a professional logo feel */
        background-color: #eef3ff;
        padding: 10px;
        border-radius: 12px;
        font-size: 22px;
        color: #1e40af; /* Deep blue color for icon, replacing the emoji */
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .header-title {
        font-size: 26px;
        font-weight: 600;
        color: #2b2b2b;
    }
    .header-desc {
        font-size: 14px;
        color: #6e6e6e;
        margin-top: -5px;
    }
    /* Style the chat input box */
    .stChatInputContainer textarea {
        background: #f8f9fc !important;
        border-radius: 12px !important;
        padding: 12px;
    }
    /* Custom styling for the assistant message to make sources stand out */
    /* Targeting the assistant message bubble for background color */
    .stChatMessage.st-lc.st-la .st-by { 
        background-color: #f0f4ff; /* Light blue background for assistant */
        border-radius: 12px;
        padding: 15px;
    }
    /* Targeting the user message bubble */
    .stChatMessage.st-lc.st-lb .st-by { 
        background-color: #ffffff; /* White background for user */
        border-radius: 12px;
        padding: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -------------------- GREETING HANDLER --------------------
def handle_greeting(query: str):
    """Checks if the query is a simple greeting and returns a canned, professional response."""
    clean_query = query.lower().strip()

    # Check for common greetings
    greetings = ["hi", "hello", "hlo", "hey", "how are you", "good morning", "good afternoon", "greetings", "yo"]

    if any(g in clean_query for g in greetings) and len(clean_query.split()) < 4:
        # Professional, welcoming response, fulfilling the user's request
        return "Welcome! I'm your dedicated HR AI Assistant, here to provide fast and accurate information from our official policy documents. How can I assist you with your policy questions today?"

    return None  # Indicates it's not a greeting and should proceed to RAG


# -------------------- HEADER --------------------
# Using a slightly wider column for the title and description
col1, col2 = st.columns([0.1, 1])
with col1:
    # Using a neutral silhouette for the header icon (filled circle for professional look)
    st.markdown('<div class="header-icon">🤖</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="header-title">HR AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-desc">Ask me anything about company HR policies!</div>', unsafe_allow_html=True)

# -------------------- INITIALIZE SESSION STATE --------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Welcome! I'm ready to answer your HR policy questions.",
         "id": 0}
    ]
if "msg_counter" not in st.session_state:
    st.session_state["msg_counter"] = 1  # counter for unique message IDs

# -------------------- INITIALIZE DB & COLLECTION ONCE --------------------
if not os.getenv("GEMINI_API_KEY"):
    st.warning("⚠️ Warning: GEMINI_API_KEY environment variable is not set. RAG functionality may be limited.")

# Initialize ChromaDB and Collection
try:
    if "chroma" not in st.session_state:
        st.session_state["chroma"] = initialize_chroma_db()
    if "collection" not in st.session_state:
        st.session_state["collection"] = get_or_create_collection(st.session_state["chroma"])
except Exception as e:
    st.error(f"❌ Failed to initialize RAG database. Please check `rag_pipeline.py` and environment setup. Error: {e}")
    st.session_state["rag_initialized"] = False
else:
    st.session_state["rag_initialized"] = True

# -------------------- PROCESS USER INPUT --------------------
prompt = st.chat_input("Type your question about HR policies...")

if prompt:
    # 1. Store user message with unique ID
    user_msg = {"role": "user", "content": prompt, "id": st.session_state["msg_counter"]}
    st.session_state["messages"].append(user_msg)
    st.session_state["msg_counter"] += 1

    # 2. Check for simple greetings first
    greeting_response = handle_greeting(prompt)

    if greeting_response:
        final_content = greeting_response
    elif not st.session_state.get("rag_initialized"):
        # Handle case where RAG failed to initialize
        final_content = "I apologize, but my policy database is currently unavailable. Please check the system logs or try again later."
    else:
        # 3. Get RAG response (show spinner while processing)
        with st.spinner("🔍 Searching policy documents and generating response..."):
            try:
                # This calls your rag_pipeline function
                rag_result = rag_query(prompt, st.session_state["collection"])

                # 4. Extract, format, and store actual assistant response
                answer = rag_result.get("response", "An error occurred while generating the response.")
                sources = rag_result.get("sources", [])

                # Format sources for display (deduplicate and link)
                source_str = ""
                if sources:
                    # Deduplicate and sort sources for cleaner presentation
                    unique_sources = sorted(list(set(sources)))
                    # Format as a nice Markdown section
                    source_str = "\n\n---\n\n**Sources Used:**\n" + "\n".join(
                        [f"- *{s}*" for s in unique_sources]  # Using italics for source names
                    )

                final_content = answer + source_str

            except Exception as e:
                # Catch any runtime errors during RAG process
                final_content = f"An unexpected error occurred during policy retrieval: {e}"

    # Store actual assistant response
    st.session_state["messages"].append({
        "role": "assistant",
        "content": final_content,
        "id": st.session_state["msg_counter"]
    })
    st.session_state["msg_counter"] += 1

    # Rerun the script to clear the input box and display the new messages immediately
    st.rerun()

# -------------------- DISPLAY CHAT HISTORY (Using native st.chat_message) --------------------
# Set a fixed height for the chat history container to enable scrolling
chat_box = st.container(height=550)
with chat_box:
    for msg in st.session_state["messages"]:
        # Set avatar for user to the '🤖' emoji and assistant to the image file 'hr_logo.png'
        # The 'name' parameter is set to None to remove the default name label
        if msg["role"] == "user":
            with st.chat_message("user", avatar="hr_logo.png"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.write(msg["content"])