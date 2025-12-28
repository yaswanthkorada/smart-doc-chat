import streamlit as st
from datetime import datetime
from utils.database import db_manager
from components.auth import logout
from loguru import logger
from config import config

def render_sidebar():
    """Render sidebar with conversation history and controls"""
    
    with st.sidebar:
        # User info
        st.markdown(f"### 👤 {st.session_state.get('username', 'User')}")
        st.caption(f"📧 {st.session_state.get('user_email', '')}")
        
        tier = st.session_state.get('subscription_tier', 'free')
        tier_emoji = "🆓" if tier == "free" else "💎" if tier == "pro" else "🏢"
        st.caption(f"{tier_emoji} {tier.title()} Plan")
        
        st.divider()
        
        # Action buttons
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("➕ New Chat", use_container_width=True, help="Start a new conversation"):
                create_new_conversation()
        with col2:
            if st.button("🔓", use_container_width=True, help="Logout", key="logout_button"):
                logout()
        
        st.divider()
        
        # AI Provider Selection
        st.markdown("### 🤖 AI Provider")
        
        # Initialize provider in session state if not set
        if 'ai_provider' not in st.session_state:
            st.session_state.ai_provider = config.AI_PROVIDER
        
        provider_options = {
            "🌟 Gemini (Free)": "gemini",
            "🚀 OpenAI (Premium)": "openai"
        }
        
        current_provider_label = "🌟 Gemini (Free)" if st.session_state.ai_provider == "gemini" else "🚀 OpenAI (Premium)"
        
        selected_provider = st.selectbox(
            "Choose AI Model",
            options=list(provider_options.keys()),
            index=list(provider_options.values()).index(st.session_state.ai_provider),
            key="provider_selector",
            help="Gemini: Free, unlimited\nOpenAI: Premium, GPT-4 quality"
        )
        
        # Update session state when selection changes
        new_provider = provider_options[selected_provider]
        if new_provider != st.session_state.ai_provider:
            st.session_state.ai_provider = new_provider
            st.success(f"✅ Switched to {selected_provider.split()[1]}")
            st.info("🔄 Both LLM and Embeddings updated!")
            st.rerun()
        
        # Show current model info
        if st.session_state.ai_provider == "gemini":
            st.caption("📊 LLM: gemini-2.0-flash-exp")
            st.caption("🧮 Embeddings: models/embedding-001")
            st.caption("💰 Cost: $0/month")
        else:
            st.caption("📊 LLM: gpt-4")
            st.caption("🧮 Embeddings: text-embedding-3-small")
            st.caption("💰 Pay-per-use")
        
        st.divider()
        
        # Conversation history
        st.markdown("### 💬 Conversations")
        
        # Search conversations
        search = st.text_input("🔍", placeholder="Search...", label_visibility="collapsed")
        
        user_id = st.session_state.get('user_id')
        if user_id:
            conversations = db_manager.get_user_conversations(user_id)
            
            # Filter by search
            if search:
                conversations = [c for c in conversations if search.lower() in c.title.lower()]
            
            if conversations:
                for conv in conversations:
                    render_conversation_item(conv)
            else:
                st.info("No conversations yet")
        
        st.divider()
        
        # Storage info
        st.markdown("### 📊 Usage")
        
        if user_id:
            stats = db_manager.get_user_stats(user_id)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Chats", stats.get('total_conversations', 0))
            with col2:
                st.metric("Messages", stats.get('total_messages', 0))
            
            user_docs = db_manager.get_user_documents(user_id)
            total_size = sum(doc.file_size for doc in user_docs) / (1024 * 1024)  # MB
            
            st.metric("Documents", len(user_docs))
            st.metric("Storage", f"{total_size:.2f} MB")
        
        # Document Storage Quick View
        st.divider()
        st.markdown("### 📦 My Storage")
        
        if user_id:
            user_docs = db_manager.get_user_documents(user_id)
            
            if user_docs:
                # Show latest 3 documents
                st.caption(f"📄 Recent Files ({len(user_docs)} total)")
                for doc in user_docs[:3]:
                    status_emoji = "✅" if doc.processed else "⏳"  # processed=True means completed
                    file_size = doc.file_size / 1024  # KB
                    st.caption(f"{status_emoji} {doc.filename[:20]}{'...' if len(doc.filename) > 20 else ''} ({file_size:.1f}KB)")
                
                if len(user_docs) > 3:
                    st.caption(f"... and {len(user_docs) - 3} more")
            else:
                st.info("📁 No files uploaded yet")
            
            # View all documents button
            if st.button("📂 View All Files", use_container_width=True, type="primary"):
                st.switch_page("pages/2_📁_Documents.py")
        
        # Quick links
        st.divider()
        st.markdown("### 🔗 Quick Links")
        if st.button("⚙️ Settings", use_container_width=True):
            st.switch_page("pages/3_⚙️_Settings.py")

def render_conversation_item(conversation):
    """Render a single conversation item"""
    
    is_current = st.session_state.get('current_conversation_id') == conversation.conversation_id
    
    # Truncate title
    title = conversation.title[:35] + "..." if len(conversation.title) > 35 else conversation.title
    
    # Pin emoji
    pin_emoji = "📌 " if conversation.is_pinned else ""
    current_emoji = "🟢 " if is_current else ""
    
    # Conversation button
    if st.button(
        f"{pin_emoji}{current_emoji}{title}",
        key=f"conv_{conversation.conversation_id}",
        use_container_width=True,
        type="primary" if is_current else "secondary"
    ):
        load_conversation(conversation.conversation_id)
    
    # Time and sessions info
    time_ago = format_time_ago(conversation.updated_at)
    sessions = db_manager.get_conversation_sessions(conversation.conversation_id)
    session_info = f"📊 {len(sessions)} session{'s' if len(sessions) != 1 else ''}"
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"🕐 {time_ago} • {session_info}")
    with col2:
        # Context menu
        with st.popover("⋮", use_container_width=True):
            if st.button(
                "📌 Unpin" if conversation.is_pinned else "📍 Pin",
                key=f"pin_{conversation.conversation_id}",
                use_container_width=True
            ):
                db_manager.pin_conversation(conversation.conversation_id)
                st.rerun()
            
            if st.button("✏️ Rename", key=f"rename_{conversation.conversation_id}", use_container_width=True):
                st.session_state[f'rename_{conversation.conversation_id}'] = True
                st.rerun()
            
            if st.button("🗑️ Delete", key=f"delete_{conversation.conversation_id}", use_container_width=True):
                delete_conversation(conversation.conversation_id)
    
    # Show rename dialog if flagged
    if st.session_state.get(f'rename_{conversation.conversation_id}'):
        with st.form(f"rename_form_{conversation.conversation_id}"):
            new_title = st.text_input("New title", value=conversation.title)
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Save", use_container_width=True):
                    db_manager.update_conversation_title(conversation.conversation_id, new_title)
                    st.session_state[f'rename_{conversation.conversation_id}'] = False
                    st.rerun()
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state[f'rename_{conversation.conversation_id}'] = False
                    st.rerun()
    
    st.divider()

def format_time_ago(timestamp: datetime) -> str:
    """Format timestamp as 'time ago'"""
    if not timestamp:
        return "Unknown"
    
    now = datetime.utcnow()
    diff = now - timestamp
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days}d ago"
    else:
        return timestamp.strftime("%b %d")

def create_new_conversation():
    """Create a new conversation"""
    user_id = st.session_state.get('user_id')
    if user_id:
        try:
            conversation = db_manager.create_conversation(user_id, "New Conversation")
            st.session_state.current_conversation_id = conversation.conversation_id
            st.session_state.current_session_id = None
            logger.info(f"Created new conversation: {conversation.conversation_id}")
            st.rerun()
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            st.error(f"Error creating conversation: {str(e)}")

def load_conversation(conversation_id: str):
    """Load a specific conversation"""
    try:
        st.session_state.current_conversation_id = conversation_id
        
        # Get or create active session
        session = db_manager.get_active_session(conversation_id)
        st.session_state.current_session_id = session.session_id
        
        logger.info(f"Loaded conversation: {conversation_id}")
        st.rerun()
    except Exception as e:
        logger.error(f"Error loading conversation: {e}")
        st.error(f"Error loading conversation: {str(e)}")

def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    try:
        db_manager.delete_conversation(conversation_id)
        
        # If deleted conversation was current, clear it
        if st.session_state.get('current_conversation_id') == conversation_id:
            st.session_state.current_conversation_id = None
            st.session_state.current_session_id = None
        
        logger.info(f"Deleted conversation: {conversation_id}")
        st.rerun()
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        st.error(f"Error deleting conversation: {str(e)}")
