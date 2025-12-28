import streamlit as st
import re
import hashlib
from utils.supabase_client import supabase
from config import config
from loguru import logger

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < config.MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {config.MIN_PASSWORD_LENGTH} characters"
    
    if config.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if config.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if config.REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    if config.REQUIRE_SPECIAL_CHARS and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"

def login_page():
    """Login interface with Supabase Auth integration"""
    st.title("🔐 Login to RAG Assistant")
    
    # Add Supabase Auth option
    login_method = st.radio("Login Method", ["Username/Password", "Email (Supabase Auth)"], horizontal=True)
    
    if login_method == "Email (Supabase Auth)":
        # Supabase Auth Email Login
        with st.form("supabase_login_form"):
            email = st.text_input("Email", key="supabase_login_email")
            password = st.text_input("Password", type="password", key="supabase_login_password")
            
            submit = st.form_submit_button("Login with Supabase Auth", use_container_width=True, type="primary")
            
            if submit:
                if not email or not password:
                    st.error("Please enter both email and password")
                    return False
                
                try:
                    # Sign in with Supabase Auth
                    auth_response = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    
                    if auth_response.user:
                        user_id = auth_response.user.id
                        
                        # Get or create user in database
                        db_user = supabase.table('users').select('*').eq('id', user_id).execute()
                        
                        if not db_user.data:
                            # Create user record if doesn't exist
                            user_data = {
                                'id': user_id,
                                'email': email,
                                'username': email.split('@')[0],  # Use email prefix as username
                                'full_name': auth_response.user.user_metadata.get('full_name', ''),
                                'subscription_tier': 'free'
                            }
                            supabase.table('users').insert(user_data).execute()
                            db_user_data = user_data
                            logger.info(f"Created new user from Supabase Auth: {email}")
                        else:
                            db_user_data = db_user.data[0]
                            # Update last login
                            supabase.table('users').update({
                                'last_login': 'now()'
                            }).eq('id', user_id).execute()
                        
                        # Set session state
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_id
                        st.session_state.username = db_user_data.get('username', email)
                        st.session_state.user_email = email
                        st.session_state.full_name = db_user_data.get('full_name', '')
                        st.session_state.subscription_tier = db_user_data.get('subscription_tier', 'free')
                        st.session_state.supabase_auth_token = auth_response.session.access_token
                        
                        logger.info(f"User logged in via Supabase Auth: {email}")
                        st.success("✅ Login successful!")
                        st.rerun()
                        return True
                    else:
                        st.error("❌ Invalid email or password")
                        return False
                        
                except Exception as e:
                    logger.error(f"Supabase Auth login error: {e}")
                    st.error(f"Login failed: {str(e)}")
                    return False
    else:
        # Original Username/Password Login
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Login", use_container_width=True, type="primary")
            with col2:
                if st.form_submit_button("Forgot Password?", use_container_width=True):
                    st.info("Please contact support to reset your password")
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                    return False
                
                try:
                    if not supabase:
                        st.error("Database connection not available")
                        return False
                    
                    password_hash = hash_password(password)
                    
                    # Query user from Supabase
                    response = supabase.table('users').select('*').eq('username', username).eq('password_hash', password_hash).execute()
                    
                    if response.data and len(response.data) > 0:
                        user = response.data[0]
                        
                        if not user.get('is_active', True):
                            st.error("❌ Account is deactivated. Please contact support.")
                            return False
                        
                        # Update last login
                        supabase.table('users').update({
                            'last_login': 'now()'
                        }).eq('id', user['id']).execute()
                        
                        # Set session state
                        st.session_state.authenticated = True
                        st.session_state.user_id = user['id']
                        st.session_state.username = user['username']
                        st.session_state.user_email = user['email']
                        st.session_state.full_name = user.get('full_name', '')
                        st.session_state.subscription_tier = user.get('subscription_tier', 'free')
                        
                        logger.info(f"User logged in: {username}")
                        st.success("✅ Login successful!")
                        st.rerun()
                        return True
                    else:
                        logger.warning(f"Failed login attempt for: {username}")
                        st.error("❌ Invalid username or password")
                        return False
                except Exception as e:
                    logger.error(f"Login error: {e}")
                    st.error(f"An error occurred: {str(e)}")
                    return False
    
    return False

def signup_page():
    """Signup interface with Supabase Auth integration"""
    st.title("📝 Create Account")
    
    # Add Supabase Auth option
    signup_method = st.radio("Signup Method", ["Username/Password", "Email (Supabase Auth)"], horizontal=True)
    
    if signup_method == "Email (Supabase Auth)":
        # Supabase Auth Email Signup
        with st.form("supabase_signup_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                email = st.text_input("Email*", key="supabase_signup_email")
                full_name = st.text_input("Full Name", key="supabase_signup_fullname")
            
            with col2:
                password = st.text_input("Password*", type="password", key="supabase_signup_password")
                confirm_password = st.text_input("Confirm Password*", type="password", key="supabase_signup_confirm")
            
            # Show password requirements
            with st.expander("Password Requirements"):
                st.markdown(f"""
                - At least {config.MIN_PASSWORD_LENGTH} characters
                {'- At least one uppercase letter' if config.REQUIRE_UPPERCASE else ''}
                {'- At least one lowercase letter' if config.REQUIRE_LOWERCASE else ''}
                {'- At least one number' if config.REQUIRE_NUMBERS else ''}
                {'- At least one special character' if config.REQUIRE_SPECIAL_CHARS else ''}
                """)
            
            agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            
            submit = st.form_submit_button("Create Account with Supabase Auth", use_container_width=True, type="primary")
            
            if submit:
                # Validation
                if not all([email, password, confirm_password]):
                    st.error("Please fill in all required fields")
                    return False
                
                if not validate_email(email):
                    st.error("Please enter a valid email address")
                    return False
                
                if password != confirm_password:
                    st.error("Passwords do not match")
                    return False
                
                is_valid, message = validate_password(password)
                if not is_valid:
                    st.error(message)
                    return False
                
                if not agree:
                    st.error("Please agree to the Terms of Service")
                    return False
                
                try:
                    # Sign up with Supabase Auth
                    auth_response = supabase.auth.sign_up({
                        "email": email,
                        "password": password,
                        "options": {
                            "data": {
                                "full_name": full_name
                            }
                        }
                    })
                    
                    if auth_response.user:
                        user_id = auth_response.user.id
                        
                        # Create user record in database
                        user_data = {
                            'id': user_id,
                            'email': email,
                            'username': email.split('@')[0],  # Use email prefix as username
                            'full_name': full_name if full_name else None,
                            'subscription_tier': 'free'
                        }
                        
                        supabase.table('users').insert(user_data).execute()
                        
                        logger.info(f"New user created via Supabase Auth: {email}")
                        st.success("✅ Account created successfully! Please check your email to confirm, then login.")
                        st.balloons()
                        return True
                    else:
                        st.error("Error creating account. Please try again.")
                        return False
                        
                except Exception as e:
                    logger.error(f"Supabase Auth signup error: {e}")
                    st.error(f"Error creating account: {str(e)}")
                    return False
    else:
        # Original Username/Password Signup
        with st.form("signup_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username*", key="signup_username", max_chars=50)
                email = st.text_input("Email*", key="signup_email")
            
            with col2:
                full_name = st.text_input("Full Name", key="signup_fullname")
                subscription_tier = st.selectbox(
                    "Subscription Plan",
                    options=["free", "pro", "enterprise"],
                    format_func=lambda x: f"{x.title()} Plan"
                )
            
            password = st.text_input("Password*", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password*", type="password", key="signup_confirm")
            
            # Show password requirements
            with st.expander("Password Requirements"):
                st.markdown(f"""
                - At least {config.MIN_PASSWORD_LENGTH} characters
                {'- At least one uppercase letter' if config.REQUIRE_UPPERCASE else ''}
                {'- At least one lowercase letter' if config.REQUIRE_LOWERCASE else ''}
                {'- At least one number' if config.REQUIRE_NUMBERS else ''}
                {'- At least one special character' if config.REQUIRE_SPECIAL_CHARS else ''}
                """)
            
            agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            
            submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            
            if submit:
                # Validation
                if not all([username, email, password, confirm_password]):
                    st.error("Please fill in all required fields")
                    return False
                
                if len(username) < 3:
                    st.error("Username must be at least 3 characters long")
                    return False
                
                if not validate_email(email):
                    st.error("Please enter a valid email address")
                    return False
                
                if password != confirm_password:
                    st.error("Passwords do not match")
                    return False
                
                is_valid, message = validate_password(password)
                if not is_valid:
                    st.error(message)
                    return False
                
                if not agree:
                    st.error("Please agree to the Terms of Service")
                    return False
                
                try:
                    if not supabase:
                        st.error("Database connection not available")
                        return False
                    
                    # Check if username exists
                    check_username = supabase.table('users').select('id').eq('username', username).execute()
                    if check_username.data and len(check_username.data) > 0:
                        st.error("Username already exists. Please choose another.")
                        return False
                    
                    # Check if email exists
                    check_email = supabase.table('users').select('id').eq('email', email).execute()
                    if check_email.data and len(check_email.data) > 0:
                        st.error("Email already registered. Please login or use another email.")
                        return False
                    
                    # Create user
                    password_hash = hash_password(password)
                    user_data = {
                        'username': username,
                        'email': email,
                        'password_hash': password_hash,
                        'full_name': full_name if full_name else None,
                        'subscription_tier': subscription_tier
                    }
                    
                    response = supabase.table('users').insert(user_data).execute()
                    
                    if response.data:
                        logger.info(f"New user created: {username}")
                        st.success("✅ Account created successfully! Please login.")
                        st.balloons()
                        return True
                    else:
                        st.error("Error creating account. Please try again.")
                        return False
                    
                except Exception as e:
                    logger.error(f"Signup error: {e}")
                    st.error(f"Error creating account: {str(e)}")
                    return False
    
    return False

def auth_page():
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        div[data-testid="stForm"] {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stForm"]) {
            background: white;
            padding: 1rem;
            border-radius: 10px;
        }
        /* Fix input text visibility */
        .stTextInput input, .stSelectbox select {
            color: #000000 !important;
            background-color: #ffffff !important;
        }
        .stTextInput label, .stSelectbox label {
            color: #333333 !important;
        }
        /* Form container text */
        div[data-testid="stForm"] * {
            color: #333333 !important;
        }
        /* Ensure input text is dark */
        input[type="text"], input[type="email"], input[type="password"] {
            color: #000000 !important;
            background-color: #f8f9fa !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Logo and title (black text for visibility)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #111;'>🤖 RAG Assistant</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #222; font-size: 1.2rem;'>Chat with your documents using AI</p>", unsafe_allow_html=True)

    st.write("")
    st.write("")

    # Tabs for login/signup
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab1:
        # Black text for login title
        st.markdown("<h2 style='color: #111;'>Login</h2>", unsafe_allow_html=True)
        login_page()
        st.write("")
        st.markdown("<span style='color: #333;'><b>Demo Account:</b> username: <code>demo</code>, password: <code>Demo@123</code></span>", unsafe_allow_html=True)

    with tab2:
        # Black text for signup title
        st.markdown("<h2 style='color: #111;'>Create Account</h2>", unsafe_allow_html=True)
        signup_page()

    # Footer
    st.write("")
    st.write("")
    st.markdown("<p style='text-align: center; color: #222; font-size: 0.8rem;'>© 2024 RAG Assistant. All rights reserved.</p>", unsafe_allow_html=True)

def logout():
    """Logout function"""
    username = st.session_state.get('username', 'Unknown')
    logger.info(f"User logged out: {username}")
    
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    st.success("Logged out successfully!")
    st.rerun()

def require_auth(func):
    """Decorator to require authentication"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            auth_page()
            st.stop()
            return None
        return func(*args, **kwargs)
    return wrapper

def check_tier_limit(user_id: str, limit_type: str) -> tuple:
    """
    Check if user has reached tier limit - uses Supabase
    Returns: (can_proceed, current_count, limit)
    user_id: UUID string
    """
    tier = st.session_state.get('subscription_tier', 'free')
    limits = config.get_tier_limits(tier)
    
    if limit_type == "documents":
        # Query documents from Supabase
        result = supabase.table('documents').select('*').eq('user_id', user_id).execute()
        current_count = len(result.data) if result.data else 0
        limit = limits["max_documents"]
    elif limit_type == "storage":
        # Query documents and sum file sizes
        result = supabase.table('documents').select('file_size').eq('user_id', user_id).execute()
        current_count = sum(doc.get('file_size', 0) for doc in (result.data or [])) / (1024 * 1024)  # MB
        limit = limits["max_storage_mb"]
    elif limit_type == "conversations":
        # Query conversations from Supabase
        result = supabase.table('conversations').select('*').eq('user_id', user_id).execute()
        current_count = len(result.data) if result.data else 0
        limit = limits["max_conversations"]
    else:
        return True, 0, float('inf')
    
    can_proceed = current_count < limit
    return can_proceed, current_count, limit

# Create demo user on first run
def create_demo_user():
    """Create demo user if doesn't exist - uses Supabase"""
    try:
        # Check if demo user exists in Supabase
        result = supabase.table('users').select('*').eq('username', 'demo').execute()
        
        if not result.data or len(result.data) == 0:
            # Create demo user
            password_hash = hash_password("Demo@123")
            supabase.table('users').insert({
                'email': 'demo@ragassistant.com',
                'username': 'demo',
                'password_hash': password_hash,
                'full_name': 'Demo User',
                'subscription_tier': 'free'
            }).execute()
            logger.info("Demo user created in Supabase")
    except Exception as e:
        logger.error(f"Error creating demo user: {e}")

# Create demo user on module import
create_demo_user()
