import streamlit as st
from datetime import datetime
import json
import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
from loguru import logger

def format_code_blocks(content: str) -> str:
    """Detect and format code blocks with syntax highlighting"""
    
    # Pattern to match code blocks with optional language specification
    # Matches: ```python\ncode\n``` or ```\ncode\n```
    code_block_pattern = r'```(\w+)?\n(.*?)```'
    
    def replace_code_block(match):
        language = match.group(1) or 'python'  # Default to python if no language specified
        code = match.group(2)
        
        try:
            # Try to get lexer for specified language
            lexer = get_lexer_by_name(language, stripall=True)
        except ClassNotFound:
            try:
                # If language not found, try to guess from code
                lexer = guess_lexer(code)
            except:
                # Fallback to text
                from pygments.lexers import TextLexer
                lexer = TextLexer()
        
        # Generate HTML with syntax highlighting
        formatter = HtmlFormatter(style='monokai', noclasses=True, cssclass='code-block')
        highlighted = highlight(code, lexer, formatter)
        
        # Add copy button
        copy_button = f'''
        <div class="code-container">
            <div class="code-header">
                <span class="code-language">{language}</span>
                <button class="copy-btn" onclick="navigator.clipboard.writeText(`{code.replace("`", "\\`")}`); this.innerText='Copied!';" onmouseout="setTimeout(() => this.innerText='Copy', 1000)">Copy</button>
            </div>
            {highlighted}
        </div>
        '''
        return copy_button
    
    # Replace all code blocks
    formatted_content = re.sub(code_block_pattern, replace_code_block, content, flags=re.DOTALL)
    
    # Also format inline code (single backticks)
    formatted_content = re.sub(r'`([^`]+)`', r'<code class="inline-code">\1</code>', formatted_content)
    
    return formatted_content

def display_message(role: str, content: str, timestamp: datetime = None, sources: list = None, message_id: str = None):
    """Display a chat message with code highlighting"""
    
    with st.chat_message(role):
        # Format code blocks if present
        if '```' in content or '`' in content:
            formatted_content = format_code_blocks(content)
            st.markdown(formatted_content, unsafe_allow_html=True)
        else:
            st.markdown(content)
        
        # Show timestamp
        if timestamp:
            st.caption(f"🕐 {timestamp.strftime('%I:%M %p')}")
        
        # Show sources if available
        if sources and role == "assistant":
            with st.expander("📚 View Sources"):
                for idx, source in enumerate(sources, 1):
                    st.markdown(f"**Source {idx}:** {source.get('filename', 'Unknown')}")
                    st.text(source.get('content', '')[:300] + "...")
                    if source.get('page'):
                        st.caption(f"Page: {source.get('page')}")
                    st.divider()
        
        # Feedback buttons for assistant messages
        if role == "assistant" and message_id:
            col1, col2, col3 = st.columns([1, 1, 8])
            with col1:
                if st.button("👍", key=f"helpful_{message_id}", help="Helpful"):
                    update_feedback(message_id, "helpful")
            with col2:
                if st.button("👎", key=f"not_helpful_{message_id}", help="Not helpful"):
                    update_feedback(message_id, "not_helpful")

def render_chat_history(messages: list):
    """Render all messages in chat history"""
    
    if not messages:
        st.info("👋 Start a conversation by typing a message below!")
        st.markdown("""
        **Tips:**
        - Upload documents using the 📁 Documents page
        - Ask questions about your documents
        - View sources for each response
        """)
        return
    
    for msg in messages:
        try:
            sources = json.loads(msg.sources) if msg.sources else None
        except:
            sources = None
        
        display_message(
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp,
            sources=sources,
            message_id=msg.message_id
        )

def update_feedback(message_id: str, feedback: str):
    """Update message feedback"""
    from utils.database import db_manager
    try:
        db_manager.update_message_feedback(message_id, feedback)
        st.success(f"Feedback recorded: {feedback}")
        logger.info(f"Feedback recorded for message {message_id}: {feedback}")
    except Exception as e:
        logger.error(f"Error updating feedback: {e}")
        st.error("Error recording feedback")
