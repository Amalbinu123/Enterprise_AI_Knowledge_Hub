import streamlit as st
import os
import shutil
from dotenv import load_dotenv
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

# Load existing environment variables from .env file
load_dotenv()

# Ensure directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("chroma_db", exist_ok=True)

# Set page config
st.set_page_config(
    page_title="Enterprise AI Knowledge Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Premium Glassmorphic Stylesheet
st.markdown("""
<style>
/* Import Outfit font */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Apply Outfit font globally */
html, body, [class*="css"], .stApp {
    font-family: 'Outfit', sans-serif !important;
}

/* Background gradient */
.stApp {
    background: radial-gradient(circle at 50% 50%, #0f172a 0%, #020617 100%) !important;
    color: #f8fafc !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: rgba(15, 23, 42, 0.95) !important;
    border-right: 1px solid rgba(99, 102, 241, 0.15) !important;
}

/* Sidebar headers */
[data-testid="stSidebar"] h2 {
    color: #a5b4fc !important;
    font-size: 1.3rem !important;
    font-weight: 600 !important;
    margin-top: 1.5rem !important;
}

/* Glassmorphic card styling */
.glass-card {
    background: rgba(30, 41, 59, 0.45);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.25);
}

.glow-card {
    border-color: rgba(99, 102, 241, 0.3);
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.08);
}

/* Custom badges */
.status-badge {
    background: rgba(16, 185, 129, 0.12);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.25);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 15px;
}

.status-badge-error {
    background: rgba(239, 68, 68, 0.12);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.25);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 15px;
}

/* Title Gradient style */
.gradient-title {
    background: linear-gradient(135deg, #c7d2fe 0%, #818cf8 50%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 2.8rem;
    margin-bottom: 0.2rem;
}

/* Styled Scrollbars */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.5);
}
::-webkit-scrollbar-thumb {
    background: rgba(99, 102, 241, 0.3);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(99, 102, 241, 0.5);
}
</style>
""", unsafe_allow_html=True)

# Import backend components after setting env variables and initializing directories
from utils.vector_store import get_vector_store, add_document_to_store, delete_document_from_store
from utils.rag_chain import get_conversational_rag_chain

# --- SIDEBAR: AUTHENTICATION & UPLOAD ---
with st.sidebar:
    st.markdown("<h1 style='font-size: 1.6rem; font-weight: 700; margin-bottom: 5px; color: #fff;'>💡 Enterprise AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.85rem; color: #94a3b8; margin-top: 0; margin-bottom: 20px;'>Retrieval-Augmented Generation Hub</p>", unsafe_allow_html=True)
    
    st.header("🔑 Authentication")
    
    # Check if Google API Key is in env
    env_api_key = os.getenv("GOOGLE_API_KEY", "")
    api_key_override = None
    
    # Check overriding
    api_key_override = st.text_input("Gemini API Key:", type="password", placeholder="AQ. or AIza...", help="Enter a new API Key to override the .env configuration.")
    if api_key_override:
        if api_key_override.startswith("AIza") or api_key_override.startswith("AQ."):
            os.environ["GOOGLE_API_KEY"] = api_key_override
            st.markdown('<div class="status-badge">🟢 Override Key Connected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge-error">🔴 Invalid API Key Format</div>', unsafe_allow_html=True)
    elif env_api_key:
        st.markdown('<div class="status-badge">🟢 Connected via .env</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge-error">🔴 API Key Missing</div>', unsafe_allow_html=True)
        st.info("💡 Please add a valid Gemini API Key to proceed.")
        st.stop()

    st.header("🗂️ Document Management")
    uploaded_files = st.file_uploader(
        "Ingest documents into Hub:",
        type=["pdf", "docx", "txt", "md", "html", "htm"],
        accept_multiple_files=True
    )
    
    # Process uploaded files
    if uploaded_files:
        new_file_processed = False
        for uploaded_file in uploaded_files:
            file_path = os.path.join("data", uploaded_file.name)
            
            # Check if file is already stored to avoid redundant processing
            if not os.path.exists(file_path):
                with st.spinner(f"Ingesting {uploaded_file.name}..."):
                    # Save to local file
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Index in vector store
                    try:
                        add_document_to_store(file_path)
                        st.toast(f"✅ Ingested: {uploaded_file.name}", icon="🎉")
                        new_file_processed = True
                    except Exception as e:
                        if os.path.exists(file_path):
                            os.remove(file_path) # Clean up if indexing fails
                        st.error(f"Failed to process {uploaded_file.name}: {e}")
        # Force a refresh to show uploaded files in the dashboard ONLY if a new file was processed
        if new_file_processed:
            st.rerun()

    # Dashboard listing uploaded files
    st.header("📁 Uploaded Documents")
    files_in_dir = os.listdir("data")
    if files_in_dir:
        for idx, filename in enumerate(files_in_dir):
            col_name, col_del = st.columns([0.8, 0.2])
            with col_name:
                ext = os.path.splitext(filename)[1].upper()[1:]
                st.markdown(f"<span style='font-size: 0.9rem; color: #cbd5e1;'>📄 **{filename}** ({ext})</span>", unsafe_allow_html=True)
            with col_del:
                if st.button("🗑️", key=f"del_{idx}"):
                    with st.spinner(f"Deleting {filename}..."):
                        # Delete from ChromaDB
                        try:
                            delete_document_from_store(filename)
                        except Exception as e:
                            st.warning(f"Could not delete from vector DB: {e}")
                        # Delete local file
                        file_to_remove = os.path.join("data", filename)
                        if os.path.exists(file_to_remove):
                            os.remove(file_to_remove)
                        st.toast(f"Removed: {filename}")
                    st.rerun()
    else:
        st.markdown("<p style='font-size: 0.85rem; color: #64748b;'>No documents uploaded yet.</p>", unsafe_allow_html=True)

# --- CHAT MEMORY AND STATE INITIALIZATION ---
if "store" not in st.session_state:
    st.session_state.store = {}
    st.session_state.chat_history = []

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in st.session_state.store:
        st.session_state.store[session_id] = ChatMessageHistory()
    return st.session_state.store[session_id]

# Initial setup check
db = None
chain = None
is_api_key_valid = True
api_key_error_msg = ""

if os.getenv("GOOGLE_API_KEY"):
    try:
        db = get_vector_store()
        # Auto-index logic if ChromaDB is empty but data folder has files
        try:
            db_size = len(db.get(limit=1)["ids"])
        except Exception:
            db_size = 0
            
        if db_size == 0 and os.listdir("data"):
            with st.spinner("Synchronizing database index with your documents folder..."):
                for filename in os.listdir("data"):
                    file_path = os.path.join("data", filename)
                    add_document_to_store(file_path)
            # Fetch fresh vector store reference
            db = get_vector_store()
            
        # Build conversational chain
        chain = get_conversational_rag_chain(db, get_session_history)
    except Exception as e:
        is_api_key_valid = False
        api_key_error_msg = str(e)

# --- MAIN DISPLAY PANEL ---
st.markdown("<h1 class='gradient-title'>💼 Enterprise AI Knowledge Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.05rem; color: #94a3b8; margin-top: 0; margin-bottom: 25px;'>Securely search and analyze enterprise knowledge bases using Retrieval-Augmented Generation (RAG).</p>", unsafe_allow_html=True)

# Handling invalid API key error gracefully
if not is_api_key_valid:
    st.markdown(f"""
    <div style="background-color: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 10px; padding: 20px; margin-bottom: 25px;">
        <h4 style="color: #f87171; margin-top: 0; font-weight: 600;">⚠️ Startup Initialization Error</h4>
        <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.5; margin-bottom: 10px;">
            An error occurred while setting up the AI database or model:
        </p>
        <code style="color: #f87171; background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; display: block; margin-bottom: 15px; overflow-x: auto;">{api_key_error_msg}</code>
        <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.5; margin-bottom: 0;">
            <strong>To fix this:</strong> Please verify your API Key and ensure the correct models are available. You can paste a new key in the sidebar to override if necessary.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Welcome Screen if no documents exist
if not os.listdir("data"):
    st.markdown("""
    <div class="glass-card glow-card">
        <h3 style="color: #a5b4fc; font-weight: 600; margin-top: 0;">👋 Welcome to your Knowledge Hub!</h3>
        <p style="color: #cbd5e1; line-height: 1.6;">
            Build a local searchable knowledge database using your company's documents. To get started, please follow these steps:
        </p>
        <ol style="color: #cbd5e1; line-height: 1.8;">
            <li>Ensure your <strong>Gemini API Key</strong> is authenticated in the sidebar.</li>
            <li>Ingest documents using the file uploader (supports <strong>PDF, DOCX, TXT, MD, HTML</strong>).</li>
            <li>Once uploaded, documents are parsed, chunked, and embedded into a local <strong>ChromaDB</strong>.</li>
            <li>Ask questions in natural language and receive answers with precise source citations.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
else:
    # --- RENDER CHAT INTERFACE ---
    
    # Container for message history
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])
            
            # Render Source expanders if present
            if "sources" in chat and chat["sources"]:
                for idx, source in enumerate(chat["sources"]):
                    with st.expander(f"📄 Source Citation {idx + 1}: {source['name']} (Page {source['page']})"):
                        st.caption("Extracted Text Snippet:")
                        st.write(source["text"])

    # Chat input bar
    user_query = st.chat_input("Ask a question about your enterprise documents:", disabled=not is_api_key_valid)

    if user_query:
        print(f"\n[DEBUG] === Received user query: '{user_query}' ===")
        if not chain:
            print("[DEBUG] Error: RAG chain is not initialized!")
            st.error("RAG chain is not initialized. Please verify your API Key and verify that documents are present.")
        else:
            print("[DEBUG] Chain is initialized. Displaying user message in UI...")
            # Display user query in UI
            with st.chat_message("user"):
                st.markdown(user_query)
            
            # Invoke conversational RAG Chain and display response dynamically
            with st.chat_message("assistant"):
                with st.spinner("Searching database and thinking..."):
                    try:
                        config = {"configurable": {"session_id": "global_user_session"}}
                        print("[DEBUG] Invoking conversational RAG chain...")
                        response = chain.invoke(
                            {"input": user_query},
                            config=config
                        )
                        print("[DEBUG] Chain invocation successful!")
                        
                        # Extract answer and sources
                        answer = response["answer"]
                        retrieved_docs = response.get("context", [])
                        print(f"[DEBUG] Retrieved {len(retrieved_docs)} chunks from ChromaDB.")
                        
                        sources = []
                        for doc in retrieved_docs:
                            sources.append({
                                "name": doc.metadata.get("source", "Uploaded Document"),
                                "page": doc.metadata.get("page", 0) + 1,
                                "text": doc.page_content
                            })
                        
                        # Render answer and citations
                        st.markdown(answer)
                        if sources:
                            print(f"[DEBUG] Rendering {len(sources)} source citations expanders...")
                            for idx, source in enumerate(sources):
                                with st.expander(f"📄 Source Citation {idx + 1}: {source['name']} (Page {source['page']})"):
                                    st.caption("Extracted Text Snippet:")
                                    st.write(source["text"])
                        
                        # Save to state (will render via loop on next rerun)
                        st.session_state.chat_history.append({"role": "user", "content": user_query})
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })
                        print("[DEBUG] Appended query and response to session state chat_history.")
                        
                    except Exception as e:
                        print(f"[DEBUG] Exception caught during chain.invoke: {e}")
                        import traceback
                        traceback.print_exc()
                        st.error(f"Error generating answer: {e}")
