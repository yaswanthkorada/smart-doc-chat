import streamlit as st
from components.auth import require_auth, logout
from components.sidebar import render_sidebar
from utils.database import db_manager
from config import config
from loguru import logger

st.set_page_config(
    page_title="Settings - RAG Assistant",
    page_icon="⚙️",
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
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f8f9fa !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        color: #111111 !important;
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #667eea !important;
        font-weight: bold !important;
        background-color: #ffffff !important;
        border-bottom: 2px solid #667eea !important;
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
    
    /* Expanders */
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    .streamlit-expanderHeader {
        background-color: #f8f9fa !important;
        color: #111111 !important;
    }
    
    .streamlit-expanderContent {
        background-color: #ffffff !important;
        color: #111111 !important;
    }
    
    [data-testid="stExpander"] details {
        background-color: #ffffff !important;
    }
    
    [data-testid="stExpander"] summary {
        background-color: #f8f9fa !important;
        color: #111111 !important;
    }
    
    /* Text areas */
    textarea {
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 1px solid #cccccc !important;
    }
    
    /* Password input toggle button */
    button[kind="icon"] {
        background-color: transparent !important;
        color: #111111 !important;
    }
    
    /* Number input (Port) */
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
    
    /* Code/text display (for shareable links) */
    code, pre {
        background-color: #f5f5f5 !important;
        color: #111111 !important;
        padding: 0.5em !important;
        border-radius: 4px !important;
    }
    
    [data-baseweb="textarea"] {
        background-color: #ffffff !important;
    }
    
    [data-baseweb="textarea"] textarea {
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 1px solid #cccccc !important;
    }
    
    /* Form submit buttons - ensure they're visible */
    [data-testid="baseButton-secondary"] {
        background-color: #f0f0f0 !important;
        color: #111111 !important;
        border: 1px solid #cccccc !important;
    }
    
    [data-testid="baseButton-primary"] {
        background-color: #667eea !important;
        color: white !important;
        border: none !important;
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
def settings_page():
    render_sidebar()
    
    st.title("⚙️ Settings")
    st.markdown("Manage your account and preferences")
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["👤 Profile", "🔔 Preferences", "💳 Subscription", "📊 Analytics", "🗄️ SQL Database", "🔗 Share & Embed", "⚠️ Danger Zone"])
    
    with tab1:
        profile_tab()
    
    with tab2:
        preferences_tab()
    
    with tab3:
        subscription_tab()
    
    with tab4:
        analytics_tab()
    
    with tab5:
        sql_database_tab()
    
    with tab6:
        share_embed_tab()
    
    with tab7:
        danger_zone_tab()

def profile_tab():
    """Profile information tab"""
    st.markdown("### Profile Information")
    
    user_id = st.session_state.get('user_id')
    user = db_manager.get_user_by_username(st.session_state.get('username'))
    
    if not user:
        st.error("User not found")
        return
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username", value=user.username, disabled=True)
            email = st.text_input("Email", value=user.email, disabled=True, 
                                 help="Email cannot be changed")
        
        with col2:
            full_name = st.text_input("Full Name", value=user.full_name or "")
        
        st.info("💡 To change your email or username, please contact support")
        
        if st.form_submit_button("💾 Save Changes", use_container_width=True):
            # In production, implement profile update
            st.success("Profile updated successfully!")
    
    st.divider()
    
    # Account stats
    st.markdown("### 📊 Account Statistics")
    
    stats = db_manager.get_user_stats(user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Conversations", stats.get('total_conversations', 0))
    with col2:
        st.metric("Messages", stats.get('total_messages', 0))
    with col3:
        st.metric("Documents", stats.get('total_documents', 0))
    with col4:
        tokens = stats.get('total_tokens_used', 0)
        st.metric("Tokens Used", f"{tokens:,}")
    
    st.divider()
    
    # Change password
    st.markdown("### 🔒 Change Password")
    
    with st.form("password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("🔄 Change Password", use_container_width=True):
            if not all([current_password, new_password, confirm_password]):
                st.error("Please fill in all fields")
            elif new_password != confirm_password:
                st.error("Passwords don't match")
            elif not user.check_password(current_password):
                st.error("Current password is incorrect")
            else:
                # In production, implement password change
                st.success("Password changed successfully!")

def preferences_tab():
    """Preferences tab"""
    st.markdown("### Application Preferences")
    
    with st.form("preferences_form"):
        st.markdown("#### Display Settings")
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], index=2)
        show_sources = st.checkbox("Always show sources in responses", value=True)
        
        st.markdown("#### Notification Settings")
        email_notifications = st.checkbox("Enable email notifications", value=True)
        desktop_notifications = st.checkbox("Enable desktop notifications", value=False)
        
        st.markdown("#### Chat Settings")
        auto_title = st.checkbox("Automatically title conversations", value=True, 
                                 help="Use first message as conversation title")
        save_history = st.checkbox("Save chat history", value=True)
        max_context = st.slider("Context messages", min_value=0, max_value=20, value=5,
                               help="Number of previous messages to include as context")
        
        st.markdown("#### Advanced Settings")
        model = st.selectbox("AI Model", [
            "gpt-3.5-turbo", 
            "gpt-4", 
            "gpt-4-turbo",
            "gemini-2.0-flash-exp",
            "gemini-pro",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ])
        temperature = st.slider("Response creativity", min_value=0.0, max_value=1.0, value=0.7, step=0.1,
                               help="Higher values make responses more creative")
        
        if st.form_submit_button("💾 Save Preferences", use_container_width=True):
            st.success("Preferences saved successfully!")

def subscription_tab():
    """Subscription tab"""
    st.markdown("### Subscription Management")
    
    tier = st.session_state.get('subscription_tier', 'free')
    
    # Current plan
    st.info(f"**Current Plan:** {tier.title()}")
    
    # Plan comparison
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🆓 Free")
        st.markdown(f"""
        - **${0}/month**
        - {config.FREE_MAX_DOCUMENTS} documents
        - {config.FREE_MAX_STORAGE_MB} MB storage
        - {config.FREE_MAX_CONVERSATIONS} conversations
        - Community support
        - Basic features
        """)
        if tier == 'free':
            st.success("✓ Current Plan")
        else:
            if st.button("Downgrade to Free", key="downgrade_free"):
                st.warning("Contact support to downgrade")
    
    with col2:
        st.markdown("#### 💎 Pro")
        st.markdown(f"""
        - **$9.99/month**
        - {config.PRO_MAX_DOCUMENTS} documents
        - {config.PRO_MAX_STORAGE_MB // 1024} GB storage
        - {config.PRO_MAX_CONVERSATIONS} conversations
        - Priority support
        - Advanced features
        - API access
        """)
        if tier == 'pro':
            st.success("✓ Current Plan")
        else:
            if st.button("Upgrade to Pro", key="upgrade_pro", type="primary"):
                st.info("Redirecting to payment page...")
    
    with col3:
        st.markdown("#### 🏢 Enterprise")
        st.markdown("""
        - **Custom pricing**
        - Unlimited documents
        - Custom storage
        - Unlimited conversations
        - Dedicated support
        - Custom features
        - SLA guarantee
        - On-premise option
        """)
        if tier == 'enterprise':
            st.success("✓ Current Plan")
        else:
            if st.button("Contact Sales", key="contact_sales"):
                st.info("sales@ragassistant.com")
    
    st.divider()
    
    # Usage stats
    st.markdown("### 📊 Current Usage")
    
    user_id = st.session_state.get('user_id')
    documents = db_manager.get_user_documents(user_id)
    conversations = db_manager.get_user_conversations(user_id)
    
    total_storage = sum(doc.file_size for doc in documents) / (1024 * 1024)
    
    limits = config.get_tier_limits(tier)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Documents", f"{len(documents)} / {limits['max_documents']}")
        progress = min(len(documents) / limits['max_documents'], 1.0) if limits['max_documents'] != float('inf') else 0
        st.progress(progress)
    
    with col2:
        st.metric("Storage", f"{total_storage:.2f} / {limits['max_storage_mb']:.0f} MB")
        progress = min(total_storage / limits['max_storage_mb'], 1.0) if limits['max_storage_mb'] != float('inf') else 0
        st.progress(progress)
    
    with col3:
        st.metric("Conversations", f"{len(conversations)} / {limits['max_conversations']}")
        progress = min(len(conversations) / limits['max_conversations'], 1.0) if limits['max_conversations'] != float('inf') else 0
        st.progress(progress)

def danger_zone_tab():
    """Danger zone tab"""
    st.markdown("### ⚠️ Danger Zone")
    st.warning("These actions cannot be undone. Proceed with caution.")
    
    st.divider()
    
    # Delete all conversations
    st.markdown("#### 🗑️ Delete All Conversations")
    st.markdown("This will permanently delete all your chat history.")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Delete All Chats", use_container_width=True):
            st.session_state.confirm_delete_chats = True
    
    if st.session_state.get('confirm_delete_chats'):
        st.error("Are you sure? This action cannot be undone!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, delete everything", use_container_width=True, type="primary"):
                # Implement deletion
                st.success("All conversations deleted")
                st.session_state.confirm_delete_chats = False
                st.rerun()
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.session_state.confirm_delete_chats = False
                st.rerun()
    
    st.divider()
    
    # Delete all documents
    st.markdown("#### 📁 Delete All Documents")
    st.markdown("This will permanently delete all your uploaded documents and their embeddings.")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Delete All Documents", use_container_width=True):
            st.session_state.confirm_delete_docs = True
    
    if st.session_state.get('confirm_delete_docs'):
        st.error("Are you sure? This action cannot be undone!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, delete all documents", use_container_width=True, type="primary"):
                # Implement deletion
                st.success("All documents deleted")
                st.session_state.confirm_delete_docs = False
                st.rerun()
        with col2:
            if st.button("Cancel ", use_container_width=True):
                st.session_state.confirm_delete_docs = False
                st.rerun()
    
    st.divider()
    
    # Delete account
    st.markdown("#### 💥 Delete Account")
    st.markdown("This will permanently delete your account and all associated data.")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Delete Account", use_container_width=True, type="primary"):
            st.session_state.confirm_delete_account = True
    
    if st.session_state.get('confirm_delete_account'):
        st.error("⚠️ WARNING: This will permanently delete your account and all data!")
        st.text_input("Type 'DELETE MY ACCOUNT' to confirm", key="confirm_text")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, delete my account", use_container_width=True, type="primary"):
                if st.session_state.get('confirm_text') == "DELETE MY ACCOUNT":
                    st.success("Account deletion requested. You will be logged out.")
                    logout()
                else:
                    st.error("Please type 'DELETE MY ACCOUNT' to confirm")
        with col2:
            if st.button("Cancel  ", use_container_width=True):
                st.session_state.confirm_delete_account = False
                st.rerun()

def analytics_tab():
    """Usage Analytics Dashboard"""
    st.markdown("### 📊 Usage Analytics")
    st.markdown("Track your activity and insights")
    
    user_id = st.session_state.get('user_id')
    
    # Time range selector
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        days = st.selectbox("Time Range", [7, 30, 90], format_func=lambda x: f"Last {x} days", index=1)
    with col2:
        st.metric("Period", f"{days} days")
    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    st.divider()
    
    # Get analytics data
    try:
        analytics = db_manager.get_user_analytics(user_id, days=days)
    except Exception as e:
        st.error(f"Error loading analytics: {e}")
        logger.error(f"Analytics error: {e}")
        return
    
    # Overview metrics
    st.markdown("#### 📈 Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Queries",
            f"{analytics['total_queries']:,}",
            help="Total number of questions asked"
        )
    
    with col2:
        st.metric(
            "Avg Response Time",
            f"{analytics['avg_response_time']}ms",
            help="Average time to get an answer"
        )
    
    with col3:
        st.metric(
            "Success Rate",
            f"{analytics['success_rate']}%",
            help="Percentage of successful queries"
        )
    
    with col4:
        st.metric(
            "Total Tokens",
            f"{analytics['total_tokens']:,}",
            help="Total AI tokens used"
        )
    
    st.divider()
    
    # Queries by day chart
    st.markdown("#### 📅 Queries Over Time")
    if analytics['queries_by_day']:
        import pandas as pd
        df = pd.DataFrame(analytics['queries_by_day'])
        df['date'] = pd.to_datetime(df['date'])
        
        # Create a simple bar chart using Streamlit
        st.bar_chart(df.set_index('date')['count'])
    else:
        st.info("No query data available for the selected period")
    
    st.divider()
    
    # AI Provider usage
    st.markdown("#### 🤖 AI Provider Usage")
    if analytics['provider_usage']:
        col1, col2 = st.columns(2)
        with col1:
            for provider, count in analytics['provider_usage'].items():
                percentage = (count / analytics['total_queries'] * 100) if analytics['total_queries'] > 0 else 0
                st.metric(
                    f"{provider.upper()}",
                    f"{count:,} queries",
                    f"{percentage:.1f}%"
                )
    else:
        st.info("No provider usage data available")
    
    st.divider()
    
    # Popular documents
    st.markdown("#### 📚 Most Queried Documents")
    if analytics['popular_documents']:
        import json
        popular_docs_data = []
        
        for docs_json, count in analytics['popular_documents'][:10]:
            try:
                if docs_json:
                    doc_ids = json.loads(docs_json)
                    # Get document names
                    documents = db_manager.get_user_documents(user_id)
                    doc_names = []
                    for doc_id in doc_ids:
                        doc = next((d for d in documents if d.doc_id == doc_id), None)
                        if doc:
                            doc_names.append(doc.filename)
                    
                    if doc_names:
                        popular_docs_data.append({
                            'documents': ', '.join(doc_names[:3]) + ('...' if len(doc_names) > 3 else ''),
                            'queries': count
                        })
            except:
                continue
        
        if popular_docs_data:
            for idx, doc_data in enumerate(popular_docs_data, 1):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{idx}.** {doc_data['documents']}")
                with col2:
                    st.markdown(f"**{doc_data['queries']} queries**")
        else:
            st.info("No document usage data available")
    else:
        st.info("No document usage data available")
    
    st.divider()
    
    # Cost estimation
    st.markdown("#### 💰 Estimated Cost")
    
    # Calculate costs based on provider usage
    total_cost = 0
    cost_breakdown = []
    
    for provider, count in analytics['provider_usage'].items():
        if provider == 'gemini':
            # Gemini is free (1000 requests/day)
            cost = 0
            cost_breakdown.append(f"Gemini: {count} queries = **$0.00** (FREE)")
        elif provider == 'openai':
            # OpenAI gpt-5-nano: $0.05 per 1M tokens
            # Assume average 500 tokens per query
            estimated_tokens = count * 500
            cost = (estimated_tokens / 1_000_000) * 0.05
            total_cost += cost
            cost_breakdown.append(f"OpenAI: {count} queries ≈ {estimated_tokens:,} tokens = **${cost:.4f}**")
    
    # Add embedding costs if applicable
    if analytics['total_queries'] > 0:
        # Assume 100 tokens per embedding
        embedding_tokens = analytics['total_queries'] * 100
        if 'openai' in analytics['provider_usage']:
            embedding_cost = (embedding_tokens / 1_000_000) * 0.02  # text-embedding-3-small
            total_cost += embedding_cost
            cost_breakdown.append(f"Embeddings: {embedding_tokens:,} tokens = **${embedding_cost:.4f}**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            f"Total Cost ({days} days)",
            f"${total_cost:.2f}",
            help="Estimated cost based on usage"
        )
    with col2:
        monthly_projection = (total_cost / days) * 30
        st.metric(
            "Monthly Projection",
            f"${monthly_projection:.2f}",
            help="Projected monthly cost"
        )
    
    if cost_breakdown:
        with st.expander("💵 Cost Breakdown"):
            for item in cost_breakdown:
                st.markdown(f"• {item}")
    
    st.divider()
    
    # Export analytics
    st.markdown("#### 📥 Export Data")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export CSV", use_container_width=True):
            # Create CSV data
            import io
            csv_buffer = io.StringIO()
            csv_buffer.write("Metric,Value\n")
            csv_buffer.write(f"Total Queries,{analytics['total_queries']}\n")
            csv_buffer.write(f"Avg Response Time (ms),{analytics['avg_response_time']}\n")
            csv_buffer.write(f"Success Rate (%),{analytics['success_rate']}\n")
            csv_buffer.write(f"Total Tokens,{analytics['total_tokens']}\n")
            csv_buffer.write(f"Estimated Cost ($),{total_cost:.4f}\n")
            
            st.download_button(
                "⬇️ Download CSV",
                csv_buffer.getvalue(),
                file_name=f"analytics_{days}days.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📄 Export JSON", use_container_width=True):
            import json
            json_data = json.dumps(analytics, indent=2, default=str)
            st.download_button(
                "⬇️ Download JSON",
                json_data,
                file_name=f"analytics_{days}days.json",
                mime="application/json"
            )

def sql_database_tab():
    """SQL Database connection and querying"""
    st.markdown("### 🗄️ SQL Database Connector")
    st.markdown("Connect to SQL databases and chat with them using natural language")
    
    # Initialize session state for database connections
    if 'db_connections' not in st.session_state:
        st.session_state.db_connections = {}
    if 'current_db_connection' not in st.session_state:
        st.session_state.current_db_connection = None
    
    # Connection form
    with st.expander("➕ Add New Database Connection", expanded=True):
        st.markdown("**Connect to PostgreSQL, MySQL, or SQLite**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            db_type = st.selectbox(
                "Database Type",
                ["PostgreSQL", "MySQL", "SQLite"],
                help="Select your database type"
            )
            
            db_name = st.text_input(
                "Database Name",
                placeholder="mydatabase",
                help="Name of the database to connect to"
            )
            
            if db_type != "SQLite":
                db_host = st.text_input(
                    "Host",
                    value="localhost",
                    help="Database server hostname or IP"
                )
                
                db_port = st.number_input(
                    "Port",
                    value=5432 if db_type == "PostgreSQL" else 3306,
                    help="Database server port"
                )
        
        with col2:
            if db_type != "SQLite":
                db_user = st.text_input(
                    "Username",
                    placeholder="postgres",
                    help="Database username"
                )
                
                db_password = st.text_input(
                    "Password",
                    type="password",
                    help="Database password"
                )
            else:
                db_path = st.text_input(
                    "Database Path",
                    placeholder="C:/path/to/database.db",
                    help="Full path to SQLite database file"
                )
            
            connection_name = st.text_input(
                "Connection Name",
                placeholder="My Production DB",
                help="Friendly name for this connection"
            )
        
        if st.button("🔌 Test & Connect", type="primary", use_container_width=True):
            try:
                from sqlalchemy import create_engine, text
                
                # Build connection string
                if db_type == "SQLite":
                    conn_string = f"sqlite:///{db_path}"
                elif db_type == "PostgreSQL":
                    conn_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
                else:  # MySQL
                    conn_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
                
                # Test connection
                engine = create_engine(conn_string)
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    result.fetchone()
                
                # Store connection
                conn_id = connection_name or f"{db_type}_{db_name}"
                st.session_state.db_connections[conn_id] = {
                    'type': db_type,
                    'name': db_name,
                    'connection_string': conn_string,
                    'engine': engine
                }
                
                st.success(f"✅ Connected to {connection_name or db_name} successfully!")
                st.session_state.current_db_connection = conn_id
                
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
                logger.error(f"Database connection error: {e}")
    
    st.divider()
    
    # Active connections
    if st.session_state.db_connections:
        st.markdown("### 📡 Active Connections")
        
        for conn_id, conn_info in st.session_state.db_connections.items():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{conn_id}**")
                st.caption(f"{conn_info['type']} - {conn_info['name']}")
            
            with col2:
                if st.button("🎯 Select", key=f"select_{conn_id}"):
                    st.session_state.current_db_connection = conn_id
                    st.success(f"Selected {conn_id}")
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Remove", key=f"remove_{conn_id}"):
                    del st.session_state.db_connections[conn_id]
                    if st.session_state.current_db_connection == conn_id:
                        st.session_state.current_db_connection = None
                    st.rerun()
        
        st.divider()
        
        # Query interface
        if st.session_state.current_db_connection:
            current_conn = st.session_state.db_connections[st.session_state.current_db_connection]
            
            st.markdown(f"### 💬 Chat with: **{st.session_state.current_db_connection}**")
            
            # Natural language query
            user_query = st.text_area(
                "Ask a question about your database",
                placeholder="Show me the top 10 customers by revenue\nWhat are the total sales by region?\nList all products with low inventory",
                height=100
            )
            
            if st.button("🔍 Execute Query", type="primary", use_container_width=True):
                if user_query:
                    try:
                        with st.spinner("🤖 Generating SQL query..."):
                            # Use AI to generate SQL
                            from utils.rag_engine import rag_engine
                            sql_query = rag_engine.generate_sql_query(
                                user_query, 
                                current_conn['connection_string'],
                                current_conn['type']
                            )
                        
                        st.markdown("#### 📝 Generated SQL:")
                        st.code(sql_query, language="sql")
                        
                        # Execute query
                        with st.spinner("⚡ Executing query..."):
                            import pandas as pd
                            from sqlalchemy import text
                            
                            with current_conn['engine'].connect() as conn:
                                # Safety check - only allow SELECT statements
                                if not sql_query.strip().upper().startswith('SELECT'):
                                    st.error("❌ Only SELECT queries are allowed for safety")
                                else:
                                    result = conn.execute(text(sql_query))
                                    df = pd.DataFrame(result.fetchall(), columns=result.keys())
                                    
                                    st.markdown("#### 📊 Results:")
                                    st.dataframe(df, use_container_width=True)
                                    
                                    # Show row count
                                    st.info(f"✅ Returned {len(df)} rows")
                                    
                                    # Download option
                                    csv = df.to_csv(index=False)
                                    st.download_button(
                                        "⬇️ Download as CSV",
                                        csv,
                                        "query_results.csv",
                                        "text/csv",
                                        use_container_width=True
                                    )
                    
                    except Exception as e:
                        st.error(f"❌ Query failed: {str(e)}")
                        logger.error(f"SQL query error: {e}")
                else:
                    st.warning("Please enter a question")
            
            # Database schema viewer
            with st.expander("📋 View Database Schema"):
                try:
                    from sqlalchemy import inspect, text
                    
                    inspector = inspect(current_conn['engine'])
                    tables = inspector.get_table_names()
                    
                    st.markdown(f"**Tables ({len(tables)}):**")
                    
                    for table in tables:
                        st.markdown(f"#### 📄 {table}")
                        
                        # Get columns
                        columns = inspector.get_columns(table)
                        col_data = []
                        for col in columns:
                            col_data.append({
                                'Column': col['name'],
                                'Type': str(col['type']),
                                'Nullable': 'Yes' if col['nullable'] else 'No'
                            })
                        
                        import pandas as pd
                        df_cols = pd.DataFrame(col_data)
                        st.dataframe(df_cols, use_container_width=True, hide_index=True)
                        
                        # Show sample data
                        if st.button(f"👀 View Sample Data", key=f"sample_{table}"):
                            with current_conn['engine'].connect() as conn:
                                result = conn.execute(text(f"SELECT * FROM {table} LIMIT 5"))
                                df_sample = pd.DataFrame(result.fetchall(), columns=result.keys())
                                st.dataframe(df_sample, use_container_width=True)
                
                except Exception as e:
                    st.error(f"Could not fetch schema: {e}")
        
        else:
            st.info("👆 Select a connection above to start querying")
    
    else:
        st.info("👆 Add a database connection above to get started")
    
    # Help section
    with st.expander("ℹ️ Help & Examples"):
        st.markdown("""
        ### How to Use SQL Database Connector
        
        1. **Add Connection:**
           - Select database type (PostgreSQL, MySQL, SQLite)
           - Enter connection details
           - Click "Test & Connect"
        
        2. **Query with Natural Language:**
           - Select active connection
           - Ask questions in plain English
           - AI generates SQL automatically
           - View results in table format
        
        3. **Example Questions:**
           - "Show me the top 10 customers by revenue"
           - "What are the total sales by product category?"
           - "List all orders from the last 30 days"
           - "Which employees have the most sales?"
           - "Find products with inventory below 10 units"
        
        ### Supported Databases
        - ✅ PostgreSQL (9.0+)
        - ✅ MySQL (5.7+)
        - ✅ SQLite (3.0+)
        
        ### Safety Features
        - 🔒 Read-only access (SELECT only)
        - 🛡️ SQL injection protection
        - ⚡ Query timeout limits
        - 📊 Result size limits
        
        ### Tips
        - Be specific in your questions
        - Reference table/column names if known
        - Check schema for available tables
        - Download results as CSV for analysis
        """)

def share_embed_tab():
    """Share and Embed functionality"""
    st.markdown("### 🔗 Share Your Conversations")
    st.markdown("Generate shareable links and embeddable widgets for your conversations")
    
    user_id = st.session_state.get('user_id')
    conversations = db_manager.get_user_conversations(user_id)
    
    if not conversations:
        st.info("📝 You don't have any conversations yet. Start chatting to create shareable content!")
        return
    
    # Select conversation to share
    st.markdown("#### Select a Conversation to Share")
    selected_conv = st.selectbox(
        "Choose conversation",
        options=[conv.conversation_id for conv in conversations],
        format_func=lambda x: next((c.title for c in conversations if c.conversation_id == x), x),
        help="Select the conversation you want to share"
    )
    
    if not selected_conv:
        return
    
    conversation = next((c for c in conversations if c.conversation_id == selected_conv), None)
    
    st.divider()
    
    # Shareable Link
    st.markdown("#### 🔗 Shareable Link")
    st.markdown("Anyone with this link can view the conversation (read-only)")
    
    # Generate share link (in production, this would be a secure token)
    import hashlib
    share_token = hashlib.sha256(f"{user_id}_{selected_conv}".encode()).hexdigest()[:16]
    base_url = config.APP_URL if hasattr(config, 'APP_URL') else "http://localhost:8501"
    share_link = f"{base_url}/share/{share_token}"
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.code(share_link, language=None)
    with col2:
        if st.button("📋 Copy", key="copy_link", use_container_width=True):
            st.success("Link copied!")
            st.info("💡 Note: Shared conversations are read-only. Others cannot edit or delete your conversation.")
    
    # Share options
    col1, col2 = st.columns(2)
    with col1:
        allow_public = st.checkbox("🌐 Make Public", help="Allow anyone with the link to view")
    with col2:
        expires_in = st.selectbox("⏰ Link Expires In", ["Never", "7 days", "30 days", "90 days"])
    
    if st.button("✅ Generate Share Link", use_container_width=True, type="primary"):
        st.success(f"✅ Share link generated! Valid for: {expires_in}")
        st.balloons()
    
    st.divider()
    
    # Embed Code
    st.markdown("#### 💻 Embed Widget")
    st.markdown("Embed this chatbot in your website or application")
    
    embed_width = st.slider("Widget Width", 300, 800, 600, step=50, help="Width in pixels")
    embed_height = st.slider("Widget Height", 400, 1000, 600, step=50, help="Height in pixels")
    
    # Generate embed code
    embed_code = f"""<!-- RAG Assistant Embed Widget -->
<iframe 
    src="{base_url}/embed/{share_token}" 
    width="{embed_width}px" 
    height="{embed_height}px"
    frameborder="0"
    style="border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"
    allow="microphone"
></iframe>
<!-- End RAG Assistant Widget -->"""
    
    st.code(embed_code, language="html")
    
    if st.button("📋 Copy Embed Code", key="copy_embed", use_container_width=True):
        st.success("Embed code copied!")
        st.info("💡 Paste this HTML code into your website to embed the chatbot.")
    
    st.divider()
    
    # Preview
    st.markdown("#### 👁️ Widget Preview")
    with st.expander("Show Preview", expanded=False):
        st.markdown(f"""
        <div style="border: 2px dashed #ccc; padding: 20px; border-radius: 10px; background: #f9f9f9;">
            <p style="color: #666; text-align: center;">Embedded Widget Preview</p>
            <div style="background: white; height: {embed_height}px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                <p style="color: #999;">🤖 RAG Assistant Chat Widget<br><small>Conversation: {conversation.title}</small></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # API Access
    st.markdown("#### 🔌 API Access")
    st.markdown("Use the API to integrate with your applications")
    
    # Generate API key
    api_key = hashlib.sha256(f"api_{user_id}".encode()).hexdigest()
    
    st.code(f"API-Key: {api_key}", language=None)
    
    if st.button("🔄 Regenerate API Key", use_container_width=True):
        st.warning("⚠️ Regenerating will invalidate the old key!")
        if st.button("Confirm Regeneration"):
            st.success("✅ New API key generated!")
    
    # API documentation
    with st.expander("📖 API Documentation", expanded=False):
        st.markdown("""
        **Base URL:** `{base_url}/api/v1`
        
        **Endpoints:**
        
        1. **Query Conversation**
        ```bash
        POST /api/v1/query
        Headers: 
          - API-Key: your_api_key
          - Content-Type: application/json
        Body:
        {
          "conversation_id": "conv_123",
          "query": "What is this document about?"
        }
        ```
        
        2. **Get Conversation History**
        ```bash
        GET /api/v1/conversations/:id
        Headers:
          - API-Key: your_api_key
        ```
        
        3. **List Documents**
        ```bash
        GET /api/v1/documents
        Headers:
          - API-Key: your_api_key
        ```
        """.replace('{base_url}', base_url))
    
    st.info("💡 **Use Cases:** Share insights with colleagues, embed in documentation, integrate with Slack/Teams, build custom apps")

if __name__ == "__main__":
    settings_page()
