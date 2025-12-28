import streamlit as st
import os
import time
from pathlib import Path
from components.auth import require_auth, check_tier_limit
from components.sidebar import render_sidebar
from utils.database import db_manager
from utils.rag_engine import rag_engine
from utils.storage import storage
from config import config
from loguru import logger

st.set_page_config(
    page_title="Documents - RAG Assistant",
    page_icon="📁",
    layout="wide"
)

# Custom CSS for consistent styling
st.markdown("""
    <style>
    /* Main page background - white */
    .main, .stApp {
        background-color: #ffffff !important;
    }
    
    /* All text - black on white */
    .main *, .stApp * {
        color: #111111 !important;
    }
    
    /* Form inputs */
    .stTextInput input, .stTextInput textarea {
        color: #111111 !important;
        background-color: #ffffff !important;
        border: 1px solid #cccccc !important;
    }
    
    /* ALL Selectbox styling */
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
    
    /* Dropdown menu */
    [data-baseweb="popover"], [data-baseweb="menu"] {
        background-color: #ffffff !important;
    }
    
    [role="listbox"], [role="option"] {
        background-color: #ffffff !important;
        color: #111111 !important;
    }
    
    [role="option"]:hover {
        background-color: #e8e8e8 !important;
    }
    
    /* Labels and headings */
    label, h1, h2, h3, h4, h5, h6 {
        color: #111111 !important;
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
    }
    
    .stButton button[kind="primary"] {
        background-color: #667eea !important;
        color: white !important;
    }
    
    /* File uploader browse button */
    [data-testid="stFileUploadDropzone"] {
        background-color: #f8f9fa !important;
        border: 2px dashed #cccccc !important;
    }
    
    [data-testid="stFileUploadDropzone"] button {
        background-color: #f0f0f0 !important;
        color: #111111 !important;
        border: 1px solid #cccccc !important;
    }
    
    [data-testid="stFileUploadDropzone"] button:hover {
        background-color: #e0e0e0 !important;
    }
    
    [data-testid="stFileUploader"] button {
        background-color: #f0f0f0 !important;
        color: #111111 !important;
        border: 1px solid #cccccc !important;
    }
    
    /* Number inputs */
    input[type="number"] {
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 1px solid #cccccc !important;
    }
    
    /* Tabs - light styling */
    .stTabs [data-baseweb="tab"] {
        color: #111111 !important;
        background-color: #f8f9fa !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

@require_auth
def documents_page():
    render_sidebar()
    
    st.title("📁 Document Management")
    st.markdown("Upload and manage your documents for AI-powered chat")
    
    user_id = st.session_state.get('user_id')
    
    # Check tier limits
    can_upload, current_docs, max_docs = check_tier_limit(user_id, "documents")
    can_store, current_storage, max_storage = check_tier_limit(user_id, "storage")
    
    # Display usage
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Documents", f"{current_docs} / {max_docs}")
    with col2:
        st.metric("Storage Used", f"{current_storage:.2f} / {max_storage:.0f} MB")
    with col3:
        tier = st.session_state.get('subscription_tier', 'free')
        st.metric("Plan", tier.title())
    
    st.divider()
    
    # Upload section
    st.markdown("### ⬆️ Upload Documents")
    
    if not can_upload:
        st.warning(f"⚠️ Document limit reached ({max_docs}). Upgrade your plan to upload more documents.")
    
    if not can_store:
        st.warning(f"⚠️ Storage limit reached ({max_storage} MB). Upgrade your plan or delete old documents.")
    
    # Tabbed upload interface
    tab1, tab2, tab3 = st.tabs(["📁 Upload Files", "🎥 Add YouTube Video", "🌐 Add Website"])
    
    with tab1:
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            accept_multiple_files=True,
            type=config.ALLOWED_FILE_TYPES + ['xlsx', 'xls', 'csv'],
            help="Supported: PDF, DOCX, TXT, PPTX, XLSX, XLS, CSV",
            disabled=(not can_upload or not can_store)
        )
        
        if uploaded_files:
            # Check file count
            if len(uploaded_files) > config.MAX_FILES_PER_UPLOAD:
                st.error(f"Maximum {config.MAX_FILES_PER_UPLOAD} files per upload")
            elif can_upload and can_store:
                if st.button("🚀 Process Documents", use_container_width=True, type="primary"):
                    process_uploaded_files(uploaded_files, user_id)
    
    with tab2:
        st.markdown("**Extract and chat with YouTube video transcripts**")
        youtube_url = st.text_input(
            "YouTube Video URL",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Enter a YouTube video URL. The video must have captions/subtitles enabled.",
            disabled=(not can_upload)
        )
        
        if youtube_url:
            if st.button("🎥 Process YouTube Video", use_container_width=True, type="primary", disabled=(not can_upload)):
                process_youtube_video(youtube_url, user_id)
    
    with tab3:
        st.markdown("**Extract and chat with any website content**")
        website_url = st.text_input(
            "Website URL",
            placeholder="https://example.com/article",
            help="Enter any website URL to extract and chat with its content.",
            disabled=(not can_upload)
        )
        
        if website_url:
            if st.button("🌐 Process Website", use_container_width=True, type="primary", disabled=(not can_upload)):
                process_website(website_url, user_id)
    
    st.divider()
    
    # Documents list
    st.markdown("### 📚 Your Documents")
    
    # Filter options
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("🔍 Search documents", placeholder="Search by filename...")
    with col2:
        filter_status = st.selectbox("Filter by status", ["All", "Completed", "Processing", "Failed"])
    
    documents = db_manager.get_user_documents(user_id)
    
    # Apply filters
    if search:
        documents = [d for d in documents if search.lower() in d.filename.lower()]
    
    if filter_status != "All":
        # Map filter status to processed boolean
        if filter_status.lower() == "completed":
            documents = [d for d in documents if d.processed]
        elif filter_status.lower() == "processing":
            documents = [d for d in documents if not d.processed]
        # Note: "failed" status no longer exists, failed docs show as not processed
    
    if documents:
        for doc in documents:
            render_document_card(doc, user_id)
    else:
        st.info("No documents uploaded yet. Upload some to get started!")
        st.markdown("""
        **Supported formats:**
        - PDF documents
        - Word documents (DOCX)
        - Text files (TXT)
        - PowerPoint (PPTX)
        - Excel (XLSX, CSV)
        """)

def process_uploaded_files(uploaded_files, user_id):
    """Process uploaded files"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Create temp directory
    temp_dir = Path("./temp")
    temp_dir.mkdir(exist_ok=True)
    
    success_count = 0
    failed_files = []
    
    for idx, file in enumerate(uploaded_files):
        status_text.text(f"Processing {file.name}... ({idx + 1}/{len(uploaded_files)})")
        
        # Check file size
        file_size_mb = file.size / (1024 * 1024)
        if file_size_mb > config.MAX_FILE_SIZE_MB:
            st.error(f"❌ {file.name} is too large ({file_size_mb:.2f} MB). Max: {config.MAX_FILE_SIZE_MB} MB")
            failed_files.append((file.name, "File too large"))
            continue
        
        # Save file temporarily
        temp_path = temp_dir / file.name
        
        try:
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())
            
            # Process document
            result = rag_engine.process_document(temp_path, user_id, file.name)
            
            st.success(f"✅ {file.name} processed successfully! ({result['chunks_created']} chunks)")
            success_count += 1
            
        except Exception as e:
            logger.error(f"Error processing {file.name}: {e}")
            st.error(f"❌ Error processing {file.name}: {str(e)}")
            failed_files.append((file.name, str(e)))
        
        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
        
        progress_bar.progress((idx + 1) / len(uploaded_files))
    
    status_text.text("")
    
    # Summary
    st.success(f"✅ Processed {success_count}/{len(uploaded_files)} documents successfully!")
    
    if failed_files:
        with st.expander(f"❌ Failed files ({len(failed_files)})"):
            for filename, error in failed_files:
                st.error(f"**{filename}:** {error}")
    
    time.sleep(2)
    st.rerun()

def render_document_card(doc, user_id):
    """Render a document card"""
    
    # Status emoji and color based on processed boolean
    if doc.processed:
        status_info = {"emoji": "✅", "color": "green", "text": "Completed"}
    else:
        status_info = {"emoji": "⏳", "color": "orange", "text": "Processing"}
    
    with st.container():
        col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 2, 1, 1, 1, 1, 1])
        
        with col1:
            # Show different icons for different file types
            icon_map = {
                "youtube": "🎥",
                "website": "🌐",
                "xlsx": "📊",
                "xls": "📊",
                "csv": "📊",
                "pptx": "📽️",
                "ppt": "📽️",
            }
            icon = icon_map.get(doc.file_type, "📄")
            st.markdown(f"**{icon} {doc.filename}**")
        
        with col2:
            if doc.file_size:
                size_mb = doc.file_size / (1024 * 1024)
                st.text(f"Size: {size_mb:.2f} MB")
            else:
                st.text("Size: N/A")
        
        with col3:
            st.markdown(f":{status_info['color']}[{status_info['emoji']} {status_info['text']}]")
        
        with col4:
            st.text(f"📊 {doc.chunk_count} chunks")
        
        with col5:
            if doc.processed and st.button("📝", key=f"summary_{doc.id}", help="Generate Summary"):
                generate_summary(str(doc.id), doc.filename, user_id)
        
        with col6:
            # Convert to PPT button (only for PDF, DOCX, TXT)
            file_ext = doc.filename.split('.')[-1].lower()
            if doc.processed and file_ext in ['pdf', 'docx', 'txt']:
                if st.button("📊", key=f"ppt_{doc.id}", help="Convert to PowerPoint"):
                    convert_to_ppt(str(doc.id), doc.filename, user_id)
        
        with col7:
            if st.button("🗑️", key=f"delete_{doc.id}", help="Delete document"):
                delete_document(str(doc.id), user_id)
        
        st.caption(f"Uploaded: {doc.upload_date.strftime('%b %d, %Y %I:%M %p')}")
        
        st.divider()

def generate_summary(doc_id: str, filename: str, user_id: int):
    """Generate and display document summary"""
    try:
        with st.spinner(f"Generating summary for {filename}..."):
            ai_provider = st.session_state.get('ai_provider_selector', config.AI_PROVIDER)
            summary = rag_engine.summarize_document(user_id, doc_id, ai_provider)
        
        # Display summary in a dialog/expander
        with st.expander(f"📝 Summary: {filename}", expanded=True):
            st.markdown(summary)
            st.caption(f"Generated using {ai_provider.upper()}")
        
        logger.info(f"Summary generated for {doc_id}")
    
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        st.error(f"Error generating summary: {str(e)}")

def convert_to_ppt(doc_id: str, filename: str, user_id: int):
    """Convert document to PowerPoint"""
    try:
        ai_provider = st.session_state.get('selected_ai_provider', config.AI_PROVIDER)
        with st.spinner(f"📊 Converting {filename} to PowerPoint presentation..."):
            pptx_path, message = rag_engine.convert_to_powerpoint(user_id, doc_id)
        
        if pptx_path:
            st.success(f"✅ {message}")
            
            # Offer download
            with open(pptx_path, 'rb') as f:
                pptx_data = f.read()
            
            # Generate output filename
            output_name = filename.rsplit('.', 1)[0] + '_presentation.pptx'
            
            st.download_button(
                label="⬇️ Download PowerPoint",
                data=pptx_data,
                file_name=output_name,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True,
                type="primary"
            )
            
            logger.info(f"PowerPoint created for {doc_id}")
            
            # Clean up temp file
            import os
            os.unlink(pptx_path)
        else:
            st.error(f"❌ {message}")
    
    except Exception as e:
        logger.error(f"Error converting to PowerPoint: {e}")
        st.error(f"Error converting to PowerPoint: {str(e)}")

def process_youtube_video(youtube_url: str, user_id: int):
    """Process YouTube video transcript"""
    try:
        with st.spinner("🎥 Extracting transcript from YouTube video..."):
            result = rag_engine.process_youtube_video(youtube_url, user_id)
        
        st.success(f"✅ YouTube video processed successfully! ({result['chunks_created']} chunks)")
        logger.info(f"YouTube video processed: {youtube_url}")
        time.sleep(2)
        st.rerun()
    
    except Exception as e:
        logger.error(f"Error processing YouTube video: {e}")
        st.error(f"❌ Error processing YouTube video: {str(e)}")
        st.info("💡 **Tip:** Make sure the video has captions/subtitles enabled.")

def process_website(website_url: str, user_id: int):
    """Process website content"""
    try:
        with st.spinner("🌐 Extracting content from website..."):
            result = rag_engine.process_website(website_url, user_id)
        
        st.success(f"✅ Website processed successfully! ({result['chunks_created']} chunks)")
        logger.info(f"Website processed: {website_url}")
        time.sleep(2)
        st.rerun()
    
    except Exception as e:
        logger.error(f"Error processing website: {e}")
        st.error(f"❌ Error processing website: {str(e)}")
        st.info("💡 **Tip:** Make sure the URL is accessible and contains text content.")

def delete_document(doc_id: str, user_id: int):
    """Delete a document"""
    try:
        with st.spinner("Deleting document..."):
            success = rag_engine.delete_document(user_id, doc_id)
        
        if success:
            st.success("Document deleted successfully!")
            logger.info(f"Document deleted: {doc_id}")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Failed to delete document")
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    documents_page()
