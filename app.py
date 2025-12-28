import streamlit as st
import os
from components.auth import auth_page, require_auth
from components.sidebar import render_sidebar
from components.chat_interface import render_chat_history, display_message
from utils.database import db_manager
from utils.rag_engine import rag_engine
from config import config
from loguru import logger
import json

# Configure logging
logger.add(config.LOG_FILE, rotation="500 MB", retention="10 days", level=config.LOG_LEVEL)

# Page config
st.set_page_config(
    page_title="RAG Assistant – Sign In",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load global CSS
try:
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Add custom floating sidebar toggle button with JavaScript
st.markdown("""
<style>
/* Floating sidebar toggle - always visible */
.floating-sidebar-toggle {
    position: fixed;
    top: 70px;
    left: 16px;
    z-index: 999999;
    background: white;
    border: 2px solid #3B82F6;
    border-radius: 10px;
    width: 46px;
    height: 46px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 24px;
    color: #111827;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    transition: all 0.3s ease;
    user-select: none;
}
.floating-sidebar-toggle:hover {
    background: #3B82F6;
    color: white;
    transform: scale(1.1);
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.5);
}
.floating-sidebar-toggle:active {
    transform: scale(0.95);
}

/* Ensure it's above everything */
.floating-sidebar-toggle {
    pointer-events: all !important;
}
</style>

<div class="floating-sidebar-toggle" onclick="toggleSidebar()" title="Toggle Sidebar">
    ☰
</div>

<script>
function toggleSidebar() {
    // Method 1: Try to click Streamlit's native toggle
    const streamlitToggle = document.querySelector('button[kind="header"]') || 
                           document.querySelector('button[data-testid="collapsedControl"]') ||
                           document.querySelector('[data-testid="baseButton-header"]');
    
    if (streamlitToggle) {
        streamlitToggle.click();
        return;
    }
    
    // Method 2: Toggle sidebar visibility directly
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        const isCollapsed = sidebar.getAttribute('aria-expanded') === 'false' || 
                          window.getComputedStyle(sidebar).marginLeft.startsWith('-');
        
        if (isCollapsed) {
            sidebar.style.marginLeft = '0';
            sidebar.setAttribute('aria-expanded', 'true');
        } else {
            sidebar.style.marginLeft = '-21rem';
            sidebar.setAttribute('aria-expanded', 'false');
        }
    }
}

// Also make sure the floating button is always on top
document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.querySelector('.floating-sidebar-toggle');
    if (toggle) {
        document.body.appendChild(toggle);
    }
});
</script>
""", unsafe_allow_html=True)

# Custom CSS (legacy - can be removed once styles.css is confirmed working)
st.markdown("""
    <style>
    /* Main page background - white */
    .main, .stApp {
        background-color: #ffffff !important;
    }
    
    /* All main content text - black */
    .main *, .stApp > div {
        color: #111111 !important;
    }
    
    /* Form text inputs - black text on white background */
    .stTextInput input, .stTextInput textarea {
        color: #111111 !important;
        background-color: #ffffff !important;
        border: 1px solid #cccccc !important;
    }
    
    /* ALL Selectbox styling - white background */
    .stSelectbox, .stSelectbox > div, .stSelectbox select {
        background-color: #ffffff !important;
        color: #111111 !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        background-color: #ffffff !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #111111 !important;
    }
    
    /* Dropdown popover and menu */
    [data-baseweb="popover"], [data-baseweb="menu"] {
        background-color: #ffffff !important;
    }
    
    /* Selectbox dropdown menu items */
    [role="listbox"] {
        background-color: #ffffff !important;
    }
    
    [role="option"] {
        color: #111111 !important;
        background-color: #ffffff !important;
    }
    
    [role="option"]:hover {
        background-color: #e8e8e8 !important;
        color: #111111 !important;
    }
    
    /* Form labels - always dark */
    .stTextInput label, .stSelectbox label, .stCheckbox label, label {
        color: #111111 !important;
        font-weight: 500 !important;
    }
    
    /* Titles and headings - always dark */
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #111111 !important;
    }
    
    /* Chat message styling - light background, dark text */
    .stChatMessage {
        background-color: #f8f9fa !important;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #111111 !important;
    }
    
    .stChatMessage * {
        color: #111111 !important;
    }
    
    /* User messages */
    .stChatMessage[data-testid="user-message"] {
        background-color: #e3f2fd !important;
    }
    
    /* Assistant messages */
    .stChatMessage[data-testid="assistant-message"] {
        background-color: #f1f3f4 !important;
    }
    
    /* Chat input text */
    .stChatInput input, .stChatInput textarea {
        color: #111111 !important;
        background-color: #ffffff !important;
    }
    
    /* File uploader - white background */
    [data-testid="stFileUploader"], .stFileUploader {
        background-color: #ffffff !important;
    }
    
    [data-testid="stFileUploader"] section {
        background-color: #f8f9fa !important;
        border: 2px dashed #cccccc !important;
        color: #111111 !important;
    }
    
    [data-testid="stFileUploader"] * {
        color: #111111 !important;
    }
    
    /* Buttons - light background */
    .stButton button {
        background-color: #f0f0f0 !important;
        color: #111111 !important;
        border: 1px solid #cccccc !important;
    }
    
    .stButton button:hover {
        background-color: #e0e0e0 !important;
        border: 1px solid #999999 !important;
    }
    
    .stButton button[kind="primary"] {
        background-color: #667eea !important;
        color: white !important;
        border: none !important;
    }
    
    .stButton button[kind="primary"]:hover {
        background-color: #5568d3 !important;
    }
    
    /* Secondary/tertiary buttons (like Forgot Password) */
    button[kind="secondary"], button[kind="tertiary"] {
        background-color: #f0f0f0 !important;
        color: #111111 !important;
        border: 1px solid #cccccc !important;
    }
    
    button[kind="secondary"]:hover, button[kind="tertiary"]:hover {
        background-color: #e0e0e0 !important;
        color: #000000 !important;
    }
    
    button[data-testid="baseButton-secondary"] {
        background-color: #f0f0f0 !important;
        color: #111111 !important;
        border: 1px solid #cccccc !important;
    }
    
    button[data-testid="baseButton-secondary"]:hover {
        background-color: #e0e0e0 !important;
    }
    
    /* Ensure all buttons have visible text */
    button {
        color: #111111 !important;
    }
    
    button[kind="primary"] {
        color: white !important;
    }
    
    /* Expander - white background */
    .streamlit-expanderHeader {
        background-color: #f8f9fa !important;
        color: #111111 !important;
    }
    
    .streamlit-expanderContent {
        background-color: #ffffff !important;
        color: #111111 !important;
    }
    
    /* Tabs - light styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f8f9fa !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #111111 !important;
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #ffffff !important;
        color: #667eea !important;
    }
    
    /* Text areas and multiline inputs */
    textarea {
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 1px solid #cccccc !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Sidebar text - white */
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton button {
        background-color: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: rgba(255, 255, 255, 0.25) !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Sidebar selectbox - semi-transparent white */
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {
        background-color: transparent !important;
        color: white !important;
    }
    
    /* Sidebar text input */
    [data-testid="stSidebar"] .stTextInput input {
        background-color: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    [data-testid="stSidebar"] .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    
    /* Voice/Audio input - light background */
    [data-testid="stAudioInput"], .stAudioInput {
        background-color: #f0f0f0 !important;
    }
    
    [data-testid="stAudioInput"] button {
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 1px solid #cccccc !important;
    }
    
    audio {
        background-color: #f0f0f0 !important;
    }
    
    /* Number input (for Port, etc) */
    input[type="number"] {
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 1px solid #cccccc !important;
    }
    
    .stNumberInput input {
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 1px solid #cccccc !important;
    }
    
    /* Code blocks and pre-formatted text */
    code, pre {
        background-color: #f5f5f5 !important;
        color: #111111 !important;
        padding: 0.2em 0.4em !important;
        border-radius: 3px !important;
    }
    
    /* Text area for links/code display */
    [data-baseweb="textarea"] {
        background-color: #ffffff !important;
    }
    
    [data-baseweb="textarea"] textarea {
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 1px solid #cccccc !important;
    }
    
    /* File uploader browse button */
    [data-testid="stFileUploadDropzone"] button {
        background-color: #f0f0f0 !important;
        color: #111111 !important;
        border: 1px solid #cccccc !important;
    }
    
    [data-testid="stFileUploadDropzone"] button:hover {
        background-color: #e0e0e0 !important;
    }
    
    /* Chat input styling */
    .stChatInputContainer {
        border-top: 2px solid #e0e0e0;
        padding-top: 1rem;
        background-color: #ffffff !important;
    }
    
    /* Session badge */
    .session-badge {
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: bold;
        color: #111111 !important;
    }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #111111 !important;
    }
    
    /* All markdown and text */
    .stMarkdown, .stMarkdown *, p, span, div {
        color: #111111 !important;
    }
    
    /* Selectbox, input labels */
    label, .stTextInput label, .stSelectbox label {
        color: #111111 !important;
    }
    
    /* Input fields */
    input, textarea, select {
        color: #111111 !important;
        background-color: #ffffff !important;
    }
    
    /* Code Syntax Highlighting Styles */
    .code-container {
        position: relative;
        margin: 1rem 0;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .code-header {
        background: #1e1e1e;
        padding: 0.5rem 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #333;
    }
    
    .code-language {
        color: #4ec9b0;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        font-family: 'Courier New', monospace;
    }
    
    .copy-btn {
        background: #2d2d2d;
        color: #ffffff;
        border: 1px solid #444;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.8rem;
        transition: all 0.2s;
    }
    
    .copy-btn:hover {
        background: #3d3d3d;
        border-color: #666;
    }
    
    .code-block {
        margin: 0;
        padding: 1rem;
        background: #1e1e1e;
        overflow-x: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    .code-block pre {
        margin: 0;
        color: #d4d4d4;
    }
    
    .inline-code {
        background: #f5f5f5;
        color: #e01e5a;
        padding: 0.2rem 0.4rem;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
        border: 1px solid #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

@require_auth
def main():
    """Main application"""
    
    # Render sidebar
    render_sidebar()
    
    # Logo and header
    col_logo, col_title = st.columns([1, 11])
    with col_logo:
        st.markdown("# 🤖")
    with col_title:
        st.title(config.APP_NAME)
        st.markdown("Chat with your documents using AI")
    
    # Developer credit
    st.markdown("""
    <div style="position: fixed; bottom: 16px; right: 16px; background: white; border: 1px solid #E5E7EB; 
                border-radius: 8px; padding: 12px 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); 
                font-size: 12px; color: #6B7280; z-index: 1000;">
        Developed by <a href="mailto:yaswanthkorada321@gmail.com" style="color: #3B82F6; text-decoration: none; font-weight: 500;">Yaswanth Korada</a>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content area
    col1, col2, col3 = st.columns([5, 2, 1])
    with col1:
        pass  # Content moved to header above
    with col2:
        # AI Provider selector
        ai_provider = st.selectbox(
            "🤖 AI Model",
            options=["gemini", "openai"],
            index=1 if config.AI_PROVIDER == "openai" else 0,
            help="Choose AI provider: Gemini (Free 1000 req/day) or OpenAI (Paid)",
            key="ai_provider_selector"
        )
        st.session_state.selected_ai_provider = ai_provider
    with col3:
        if st.session_state.get('current_session_id'):
            st.markdown('<div class="session-badge">🟢 Active</div>', unsafe_allow_html=True)
    
    # Initialize conversation & session
    if 'current_conversation_id' not in st.session_state:
        user_id = st.session_state.get('user_id')
        conversations = db_manager.get_user_conversations(user_id)
        
        if not conversations:
            # Create first conversation
            conversation = db_manager.create_conversation(user_id, "New Conversation")
            st.session_state.current_conversation_id = conversation.conversation_id
            logger.info(f"Created first conversation for user {user_id}")
        else:
            st.session_state.current_conversation_id = conversations[0].conversation_id
    
    current_conversation_id = st.session_state.get('current_conversation_id')
    
    if not current_conversation_id:
        st.info("👈 Create a new conversation to get started!")
        return
    
    # Get or create session
    if 'current_session_id' not in st.session_state or not st.session_state.current_session_id:
        session = db_manager.get_active_session(current_conversation_id)
        st.session_state.current_session_id = session.session_id
    
    current_session_id = st.session_state.get('current_session_id')
    
    # Display conversation info
    conversation = db_manager.get_conversation(current_conversation_id)
    if conversation:
        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            st.caption(f"📝 **Conversation:** {conversation.title}")
        with col2:
            sessions = db_manager.get_conversation_sessions(current_conversation_id)
            st.caption(f"📊 **Sessions:** {len(sessions)}")
        with col3:
            if st.button("🔄 New Session", help="Start a new session in this conversation"):
                # End current session and create new one
                db_manager.end_session(current_session_id)
                new_session = db_manager.create_session(current_conversation_id)
                st.session_state.current_session_id = new_session.session_id
                logger.info(f"Started new session: {new_session.session_id}")
                st.rerun()
    
    st.divider()
    
    # Multi-document selector
    user_id = st.session_state.get('user_id')
    documents = db_manager.get_user_documents(user_id)
    completed_docs = [d for d in documents if d.processed]  # processed=True means completed
    
    if completed_docs:
        with st.expander("🔍 Select Documents to Query (Optional - default: all documents)", expanded=False):
            st.markdown("**Select specific documents to focus your search:**")
            selected_docs = st.multiselect(
                "Documents",
                options=[str(d.id) for d in completed_docs],
                format_func=lambda x: next((d.filename for d in completed_docs if str(d.id) == x), x),
                help="Select one or more documents to search across. Leave empty to search all documents.",
                key="selected_documents"
            )
            if selected_docs:
                st.success(f"✅ Will search across {len(selected_docs)} selected document(s)")
    
    # Load and display messages
    messages = db_manager.get_conversation_messages(current_conversation_id)
    
    # Display chat history
    render_chat_history(messages)
    
    # Voice input option
    col1, col2 = st.columns([10, 2])
    with col2:
        st.caption("🎤 Voice")
        audio_input = st.audio_input("Record your question", key="voice_input", label_visibility="collapsed")
    
    # Chat input
    user_input = st.chat_input("Ask me anything about your documents...")
    
    # Process voice input if provided
    if audio_input:
        try:
            with st.spinner("🎤 Transcribing your voice..."):
                # Save audio temporarily
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_audio:
                    tmp_audio.write(audio_input.getvalue())
                    audio_path = tmp_audio.name
                
                # Transcribe using OpenAI Whisper (if available) or show message
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=config.OPENAI_API_KEY)
                    with open(audio_path, 'rb') as audio_file:
                        transcript = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file
                        )
                    user_input = transcript.text
                    st.info(f"🎤 Transcribed: {user_input}")
                except Exception as e:
                    st.warning("Voice transcription requires OpenAI API key. Please type your question instead.")
                    logger.error(f"Voice transcription error: {e}")
                    user_input = None
                
                # Clean up temp file
                import os
                os.unlink(audio_path)
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            st.error("Error processing voice input. Please try typing instead.")
            user_input = None
    
    if user_input:
        # Display user message immediately
        display_message("user", user_input)
        
        # Add to database
        db_manager.add_message(
            conversation_id=current_conversation_id,
            session_id=current_session_id,
            role="user",
            content=user_input
        )
        
        # Get selected provider from session state (set by sidebar dropdown)
        selected_provider = st.session_state.get('ai_provider', config.AI_PROVIDER)
        
        # Update RAG engine provider if it changed
        if selected_provider != rag_engine.current_ai_provider:
            with st.spinner(f"🔄 Switching to {selected_provider.upper()}..."):
                success = rag_engine.update_provider(selected_provider)
                if not success:
                    st.error(f"Failed to switch to {selected_provider}. Using current provider.")
                    selected_provider = rag_engine.current_ai_provider
        
        selected_docs = st.session_state.get('selected_documents', [])
        provider_emoji = "✨" if selected_provider == "gemini" else "🧠"
        
        with st.spinner(f"{provider_emoji} Thinking with {selected_provider.upper()}..."):
            import time
            start_time = time.time()
            
            try:
                # Check if query is asking for visualization
                viz_keywords = ['chart', 'graph', 'plot', 'visualize', 'visualization', 'show me a', 'bar chart', 'line graph', 'pie chart', 'histogram', 'scatter']
                is_viz_request = any(keyword in user_input.lower() for keyword in viz_keywords)
                
                # If visualization requested and only one Excel/CSV document selected, generate chart
                if is_viz_request and len(selected_docs) == 1:
                    doc = db_manager.get_document(st.session_state.user_id, selected_docs[0])
                    file_ext = doc.filename.split('.')[-1].lower() if doc else None
                    
                    if file_ext in ['csv', 'xlsx', 'xls']:
                        fig, viz_message = rag_engine.generate_visualization(
                            user_id=st.session_state.user_id,
                            doc_id=selected_docs[0],
                            query=user_input
                        )
                        
                        if fig:
                            response = viz_message
                            sources = [{"filename": doc.filename, "content": "Data visualization generated", "page": "N/A"}]
                            tokens = len(user_input.split())
                            
                            # Store visualization in session state to display
                            st.session_state['current_visualization'] = fig
                        else:
                            # Fall back to regular query
                            is_viz_request = False
                
                # Regular query if not visualization
                if not is_viz_request or 'current_visualization' not in st.session_state:
                    # Use multi-document query if documents are selected
                    if selected_docs:
                        response, sources, tokens = rag_engine.query_multi_documents(
                            user_id=st.session_state.user_id,
                            query=user_input,
                            doc_ids=selected_docs,
                            conversation_id=current_conversation_id,
                            ai_provider=selected_provider
                        )
                    else:
                        # Default: search all documents
                        response, sources, tokens = rag_engine.query(
                            user_id=st.session_state.user_id,
                            query=user_input,
                            conversation_id=current_conversation_id,
                            ai_provider=selected_provider
                        )
                
                # Calculate response time
                response_time = int((time.time() - start_time) * 1000)  # milliseconds
                
                # Log analytics
                db_manager.log_query_analytics(
                    user_id=st.session_state.user_id,
                    conversation_id=current_conversation_id,
                    query_text=user_input,
                    response_time=response_time,
                    tokens_used=tokens,
                    documents_searched=selected_docs if selected_docs else ['all'],
                    ai_provider=selected_provider,
                    success=True
                )
                
            except Exception as e:
                logger.error(f"Error getting RAG response: {e}")
                response = f"Sorry, I encountered an error: {str(e)}"
                sources = []
                tokens = 0
                response_time = int((time.time() - start_time) * 1000)
                
                # Log error analytics
                db_manager.log_query_analytics(
                    user_id=st.session_state.user_id,
                    conversation_id=current_conversation_id,
                    query_text=user_input,
                    response_time=response_time,
                    tokens_used=0,
                    documents_searched=selected_docs if selected_docs else ['all'],
                    ai_provider=selected_provider,
                    success=False,
                    error_message=str(e)
                )
        
        # Display assistant message
        display_message("assistant", response, sources=sources)
        
        # Display visualization if generated
        if 'current_visualization' in st.session_state:
            st.plotly_chart(st.session_state['current_visualization'], use_container_width=True)
            del st.session_state['current_visualization']  # Clean up after display
        
        # Add assistant message to database
        sources_json = json.dumps(sources) if sources else None
        db_manager.add_message(
            conversation_id=current_conversation_id,
            session_id=current_session_id,
            role="assistant",
            content=response,
            sources=sources_json,
            tokens_used=tokens
        )
        
        # Auto-update conversation title with first message
        if len(messages) == 0:
            title = user_input[:50] + "..." if len(user_input) > 50 else user_input
            db_manager.update_conversation_title(current_conversation_id, title)
        
        st.rerun()

if __name__ == "__main__":
    # Validate configuration
    errors = config.validate_config()
    if errors:
        st.error("Configuration errors:")
        for error in errors:
            st.error(f"- {error}")
        st.stop()
    
    # Check authentication
    if not st.session_state.get('authenticated', False):
        auth_page()
    else:
        try:
            main()
        except Exception as e:
            logger.error(f"Application error: {e}")
            st.error(f"An error occurred: {str(e)}")
            st.error("Please refresh the page or contact support if the issue persists.")
