# 🔐 OAuth Integration Guide - FREE Services

Complete guide to add Google, GitHub, and other OAuth providers to your RAG application.

---

## 🎯 Best FREE Option: **Supabase Auth** (RECOMMENDED)

**Why Supabase?**
- ✅ **100% FREE** up to 50,000 users/month
- ✅ Google, GitHub, Facebook, Twitter, Discord OAuth
- ✅ Email verification included
- ✅ Password reset included
- ✅ Works with your existing database (just for auth)
- ✅ Easy Streamlit integration
- ✅ 5-year track record, production-ready

**Limitations:**
- None for your use case! Perfect for startups to enterprise.

---

## 🚀 Implementation: Supabase OAuth

### Step 1: Setup Supabase (15 minutes)

1. **Create Supabase Account**
   - Go to: https://supabase.com
   - Sign up free with GitHub
   - Create new project
   - Choose region (closest to users)
   - Wait 2 minutes for setup

2. **Get Your Credentials**
   ```
   Project URL: https://xxxxxxxxxxxxx.supabase.co
   Anon Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
   - Find in: Project Settings → API

3. **Enable OAuth Providers**
   - Go to: Authentication → Providers
   - **Enable Google:**
     - Get credentials: https://console.cloud.google.com/apis/credentials
     - Create OAuth 2.0 Client ID
     - Add authorized redirect: `https://xxxxx.supabase.co/auth/v1/callback`
     - Copy Client ID and Secret to Supabase
   
   - **Enable GitHub:**
     - Go to: GitHub Settings → Developer Settings → OAuth Apps
     - Create New OAuth App
     - Homepage URL: `http://localhost:8501` (dev) or your domain
     - Authorization callback: `https://xxxxx.supabase.co/auth/v1/callback`
     - Copy Client ID and Secret to Supabase

### Step 2: Install Dependencies

```bash
pip install supabase streamlit-oauth
```

Add to requirements.txt:
```
supabase==2.3.0
```

### Step 3: Update .env

```env
# ==================== SUPABASE AUTH ====================
ENABLE_OAUTH=True  # Set to False to disable OAuth
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Step 4: Update config/settings.py

Add these lines after Gemini settings:

```python
# Supabase Auth (OAuth)
ENABLE_OAUTH = os.getenv("ENABLE_OAUTH", "False").lower() == "true"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
```

### Step 5: Create OAuth Helper (NEW FILE)

Create `components/oauth.py`:

```python
"""OAuth authentication with Supabase"""
import streamlit as st
from supabase import create_client, Client
from config import config
from utils.database import db_manager
from loguru import logger
import time

# Initialize Supabase client
if config.ENABLE_OAUTH and config.SUPABASE_URL and config.SUPABASE_KEY:
    supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    OAUTH_ENABLED = True
else:
    supabase = None
    OAUTH_ENABLED = False
    logger.info("OAuth disabled or Supabase not configured")

def render_oauth_buttons():
    """Render OAuth login buttons"""
    if not OAUTH_ENABLED:
        return
    
    st.markdown("---")
    st.markdown("### Or sign in with:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Google", use_container_width=True, key="oauth_google"):
            oauth_login("google")
    
    with col2:
        if st.button("🐙 GitHub", use_container_width=True, key="oauth_github"):
            oauth_login("github")

def oauth_login(provider: str):
    """Initiate OAuth login flow"""
    try:
        # Get redirect URL (for production, use your domain)
        redirect_url = "http://localhost:8501"  # Change in production
        
        # Start OAuth flow
        response = supabase.auth.sign_in_with_oauth({
            "provider": provider,
            "options": {
                "redirect_to": redirect_url
            }
        })
        
        # Store provider in session for callback
        st.session_state.oauth_provider = provider
        
        # Redirect to OAuth provider
        if response.url:
            st.markdown(f'<meta http-equiv="refresh" content="0;url={response.url}">', 
                       unsafe_allow_html=True)
            st.info(f"Redirecting to {provider.title()}...")
        
    except Exception as e:
        logger.error(f"OAuth error ({provider}): {e}")
        st.error(f"Failed to login with {provider}: {str(e)}")

def handle_oauth_callback():
    """Handle OAuth callback after user authenticates"""
    try:
        # Check if we're coming from OAuth
        session = supabase.auth.get_session()
        
        if session and session.user:
            user = session.user
            
            # Check if user exists in our database
            email = user.email
            existing_user = db_manager.get_user_by_email(email)
            
            if not existing_user:
                # Create new user from OAuth data
                username = email.split('@')[0]  # Use email prefix as username
                
                # Check if username exists, append number if needed
                counter = 1
                original_username = username
                while db_manager.get_user_by_username(username):
                    username = f"{original_username}{counter}"
                    counter += 1
                
                # Create user (no password needed for OAuth)
                existing_user = db_manager.create_user(
                    email=email,
                    username=username,
                    password=None,  # OAuth users don't have passwords
                    full_name=user.user_metadata.get('full_name', ''),
                    oauth_provider=st.session_state.get('oauth_provider', 'unknown')
                )
                logger.info(f"New OAuth user created: {username}")
            
            # Update last login
            db_manager.update_last_login(existing_user.id)
            
            # Set session state
            st.session_state.authenticated = True
            st.session_state.user_id = existing_user.id
            st.session_state.username = existing_user.username
            st.session_state.user_email = existing_user.email
            st.session_state.subscription_tier = existing_user.subscription_tier
            st.session_state.full_name = existing_user.full_name
            st.session_state.oauth_session = session
            
            logger.info(f"OAuth user logged in: {existing_user.username}")
            return True
            
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        return False
    
    return False

def is_oauth_enabled():
    """Check if OAuth is enabled"""
    return OAUTH_ENABLED
```

### Step 6: Update components/auth.py

Add OAuth buttons to login page:

```python
# At the top, add import
from components.oauth import render_oauth_buttons, handle_oauth_callback, is_oauth_enabled

# In login_page() function, after the login form, add:
def login_page():
    """Login interface"""
    st.title("🔐 Login to RAG Assistant")
    
    with st.form("login_form"):
        # ... existing login form code ...
        pass
    
    # Add OAuth buttons
    if is_oauth_enabled():
        render_oauth_buttons()
    
    return False
```

### Step 7: Update utils/database.py

Add OAuth support to User model:

```python
# In User class, add new column
class User(Base):
    # ... existing columns ...
    oauth_provider = Column(String, nullable=True)  # 'google', 'github', etc.
    
    def set_password(self, password: str):
        """Set password hash"""
        if password:  # Only hash if password provided (OAuth users don't have passwords)
            self.password_hash = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
        else:
            self.password_hash = None
```

Update `create_user` method:

```python
def create_user(self, email: str, username: str, password: str = None, 
                full_name: str = None, subscription_tier: str = "free",
                oauth_provider: str = None) -> User:
    """Create new user"""
    user = User(
        email=email,
        username=username,
        full_name=full_name,
        subscription_tier=subscription_tier,
        oauth_provider=oauth_provider
    )
    if password:
        user.set_password(password)
    
    self.session.add(user)
    self.session.commit()
    return user
```

### Step 8: Update app.py

Handle OAuth callback on startup:

```python
# In app.py, at the very top of main():

@require_auth
def main():
    """Main application"""
    
    # Check for OAuth callback
    if config.ENABLE_OAUTH:
        from components.oauth import handle_oauth_callback
        if handle_oauth_callback():
            st.rerun()
    
    # ... rest of main() code ...
```

### Step 9: Database Migration

Run this to add oauth_provider column:

```python
# Create migration script: migrate_add_oauth.py
from utils.database import db_manager, User
from sqlalchemy import text

def migrate():
    """Add oauth_provider column"""
    try:
        # Add column
        db_manager.session.execute(
            text("ALTER TABLE users ADD COLUMN oauth_provider VARCHAR")
        )
        db_manager.session.commit()
        print("✅ Migration successful!")
    except Exception as e:
        print(f"Migration error (probably already exists): {e}")

if __name__ == "__main__":
    migrate()
```

Run: `python migrate_add_oauth.py`

### Step 10: Test It!

1. Start app: `streamlit run app.py`
2. Click "🔍 Google" or "🐙 GitHub"
3. Authenticate with provider
4. User created automatically
5. Redirected back to app (logged in!)

---

## 🎨 UI Enhancement

Update the auth page to look better with OAuth:

```python
# In auth_page() in components/auth.py

def auth_page():
    # ... existing code ...
    
    with tab1:
        login_page()
        
        # Add OAuth buttons in login tab too
        if is_oauth_enabled():
            st.write("")
            render_oauth_buttons()
        
        st.write("")
        st.markdown("**Demo Account:** username: `demo`, password: `Demo@123`")
```

---

## 📊 How It Works Together

### User Registration Flow:

```
Traditional Signup:
User fills form → Password hashed → Stored in your DB → Login

OAuth Signup (NEW):
User clicks Google/GitHub → 
Redirected to provider → 
User authorizes → 
Callback to your app → 
Check if email exists in your DB:
  - Yes: Login existing user
  - No: Create new user (no password needed) → 
Login successful
```

### Database Structure:

```
users table:
├── id (your primary key)
├── email
├── username
├── password_hash (NULL for OAuth users)
├── oauth_provider ('google', 'github', or NULL)
├── subscription_tier
└── ... other fields

Your documents/conversations/messages:
├── Still use user_id to link to users table
└── Works exactly the same way!
```

**Key Point:** Supabase only handles authentication. Your database still stores all user data, documents, conversations. Perfect separation!

---

## 🔒 Security Features (Included FREE)

- ✅ **Email Verification:** Automatic with OAuth
- ✅ **Password Reset:** Built-in (for non-OAuth users)
- ✅ **Session Management:** Secure tokens
- ✅ **Rate Limiting:** Prevents abuse
- ✅ **2FA/MFA:** Available in settings
- ✅ **Audit Logs:** Track auth events

---

## 🌍 Production Deployment

### Update Redirect URLs:

In production, change:
```python
# components/oauth.py
redirect_url = "https://yourdomain.com"  # Your production URL
```

In Supabase dashboard:
- Authentication → URL Configuration
- Site URL: `https://yourdomain.com`
- Redirect URLs: Add `https://yourdomain.com/**`

In Google/GitHub OAuth settings:
- Update authorized redirect URIs to production Supabase callback

---

## 💰 Cost Comparison

| Users | Supabase | Auth0 | Firebase | Your Cost |
|-------|----------|-------|----------|-----------|
| 0-50K | FREE | FREE (7K) | FREE | $0 |
| 100K | FREE | $240/mo | FREE | $0 |
| 500K | $25/mo | $1,200/mo | FREE | $25 |
| 1M+ | $99/mo | $2,400/mo | FREE | $99 |

**Supabase is FREE forever up to 50,000 users!** Perfect for your project.

---

## 🔄 Keeping Both Auth Methods

You can keep your current username/password AND add OAuth:

**Benefits:**
- ✅ Flexibility: Users choose their preferred method
- ✅ Backward compatible: Existing users keep working
- ✅ Future-proof: Easy to disable OAuth if needed
- ✅ No migration needed: Just add OAuth alongside

**How to decide:**
```python
# User login flow
if user.oauth_provider:
    # OAuth user - can't login with password
    st.info("Please login with {user.oauth_provider}")
else:
    # Traditional user - can login with password
    # Allow password login
```

---

## 🎯 Quick Start (5 Minutes)

**Want me to implement this for you right now?**

Just need:
1. ✅ Create Supabase account (2 min): https://supabase.com
2. ✅ Get URL and Key from dashboard
3. ✅ Paste in .env

I'll:
- ✅ Add all code files
- ✅ Update auth.py
- ✅ Add oauth.py
- ✅ Update database.py
- ✅ Create migration script
- ✅ Test and verify

**Total time: 5 minutes for you, 20 minutes for me to code it!**

---

## 🐛 Troubleshooting

### "OAuth provider not configured"
- Check SUPABASE_URL and SUPABASE_KEY in .env
- Set ENABLE_OAUTH=True

### "Redirect URL mismatch"
- Update redirect URL in OAuth provider settings
- Must match Supabase callback URL exactly

### "User already exists"
- Email is already registered
- User should use existing login method

### "Module 'supabase' not found"
- Run: `pip install supabase`

---

## 📚 Additional Free Services

### Alternative 1: **Google OAuth Only** (No Supabase)

**Pros:** Simplest, no external service
**Cons:** Only Google login, more code

Use: `streamlit-google-oauth`
```bash
pip install streamlit-google-oauth
```

### Alternative 2: **GitHub OAuth Only**

Use: `streamlit-oauth`
```bash
pip install streamlit-oauth
```

### Alternative 3: **Auth0** (More Features)

**FREE Tier:** 7,000 users
**Pros:** More enterprise features
**Cons:** Lower free limit

---

## ✅ Recommendation

**For your project, use Supabase because:**

1. ✅ **50,000 free users** (way more than competitors)
2. ✅ **Multiple OAuth providers** (Google, GitHub, etc.)
3. ✅ **Email features** included (verification, reset)
4. ✅ **Easy Streamlit integration**
5. ✅ **Production-ready** (used by thousands of companies)
6. ✅ **No credit card needed** for free tier
7. ✅ **Works with your existing database** (just adds auth)

**Implementation time:** 30 minutes
**Cost:** FREE forever (up to 50K users)
**Maintenance:** Zero - Supabase handles everything

---

## 🚀 Next Steps

1. **Now:** Create Supabase account → Get credentials
2. **Tell me:** "Add OAuth with Supabase" 
3. **I'll implement:** All code in 20 minutes
4. **You test:** Click Google/GitHub login button
5. **Done:** Production-ready OAuth! 🎉

**Ready to add OAuth now?**
