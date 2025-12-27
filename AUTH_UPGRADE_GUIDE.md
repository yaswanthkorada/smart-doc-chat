# 🔐 Authentication Upgrade Guide

This guide helps you choose and implement the right authentication strategy for your RAG application.

---

## Current Implementation

**Type:** Session-based authentication with Streamlit session state  
**Security:** bcrypt password hashing, server-side validation  
**Storage:** SQLite/PostgreSQL database

### How It Works:
1. User logs in with username/password
2. Password verified against bcrypt hash in database
3. Session state stores user info (authenticated, user_id, etc.)
4. `require_auth` decorator protects pages
5. Session lasts until logout or browser close

### Current Features:
- ✅ Secure password hashing (bcrypt)
- ✅ Password strength validation
- ✅ User registration
- ✅ Demo account auto-creation
- ✅ Subscription tier management

### Current Limitations:
- ❌ No JWT tokens
- ❌ No OAuth (Google, GitHub, etc.)
- ❌ No email verification
- ❌ No password reset
- ❌ Sessions don't persist across server restarts
- ❌ No API authentication for external integrations

---

## 🎯 Choose Your Auth Strategy

### Option 1: Keep Current System (**Recommended for MVP/Internal Tools**)

**Best For:**
- Internal company tools (5-100 users)
- MVP/Testing phase
- You control user management
- Budget: **FREE**

**Pros:**
- ✅ Already implemented
- ✅ Simple and fast
- ✅ No external dependencies
- ✅ Full control

**Cons:**
- ❌ No OAuth support
- ❌ Manual user management
- ❌ Limited scalability

**Upgrade Path:**
```bash
# Add these features to current system
1. Email verification (SendGrid free tier)
2. Password reset via email
3. Session timeout
4. Two-factor authentication (TOTP)
```

---

### Option 2: Add JWT Tokens (**Recommended for Production**)

**Best For:**
- Production applications
- Multiple services/microservices
- API access needed
- Mobile app integration
- Budget: **FREE**

**What Changes:**
- Keep current login/signup
- Add JWT token generation on login
- Store tokens in session state + optional cookies
- Add token validation decorator
- Enable API endpoints with Bearer token authentication

**Implementation:**
```python
# Install
pip install python-jose[cryptography]

# Add to config/settings.py
JWT_SECRET_KEY = "your-super-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
```

**Benefits:**
- ✅ Stateless authentication
- ✅ Works with APIs
- ✅ Token expiration/refresh
- ✅ Can share across services
- ✅ Still use current database

**Cost:** FREE - No external service needed

---

### Option 3: OAuth 2.0 (Google, GitHub) (**Best User Experience**)

**Best For:**
- Public-facing applications
- Quick signup needed
- Professional appearance
- Budget: **FREE** (but requires setup)

**Services to Use:**

#### **A) Supabase Auth (Recommended - Easiest)**
- **Cost:** FREE (50,000 users/month)
- **Features:** OAuth (Google, GitHub, etc.), email verification, password reset
- **Setup Time:** 30 minutes
- **Docs:** https://supabase.com/docs/guides/auth

**Quick Start:**
```bash
pip install supabase

# .env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key
```

#### **B) Auth0**
- **Cost:** FREE (7,000 users/month)
- **Features:** OAuth, MFA, enterprise SSO
- **Setup Time:** 1 hour
- **Docs:** https://auth0.com/docs

#### **C) Firebase Auth**
- **Cost:** FREE (unlimited users)
- **Features:** OAuth, phone auth, anonymous auth
- **Setup Time:** 45 minutes
- **Docs:** https://firebase.google.com/docs/auth

#### **D) Google OAuth (Direct)**
- **Cost:** FREE
- **Features:** Google login only
- **Setup Time:** 1 hour
- **Use:** streamlit-google-oauth

---

### Option 4: Enterprise SSO/SAML (**For Corporate Clients**)

**Best For:**
- Enterprise customers
- Active Directory integration
- Corporate security requirements
- Budget: **$$$**

**Services:**
- **Okta:** $2-5 per user/month
- **Azure AD B2C:** $0.015 per authentication
- **AWS Cognito:** $0.0055 per monthly active user

---

## 📊 Decision Matrix

| Scenario | Recommended Solution | Cost | Setup Time |
|----------|---------------------|------|------------|
| **Internal company tool (< 50 users)** | Keep current + add email verification | FREE | 2 hours |
| **MVP for testing** | Keep current system | FREE | 0 hours (done!) |
| **Production SaaS (100-10K users)** | Current + JWT tokens | FREE | 4 hours |
| **Public app (need social login)** | Supabase Auth | FREE | 3 hours |
| **Need API access** | Current + JWT tokens | FREE | 4 hours |
| **Enterprise clients** | Current + JWT + SSO option | $2-5/user | 1-2 weeks |
| **Maximum flexibility** | Supabase Auth (OAuth + JWT) | FREE | 5 hours |

---

## 🛠️ Implementation Guides

### Quick Win: Add Email Verification (Keep Current System)

**Step 1:** Install SendGrid (100 emails/day free)
```bash
pip install sendgrid
```

**Step 2:** Add to .env
```env
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
```

**Step 3:** Update User model (add email_verified field)
```python
# utils/database.py - User model
email_verified = Column(Boolean, default=False)
verification_token = Column(String, nullable=True)
```

**Step 4:** Send verification email on signup
```python
# components/auth.py
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_verification_email(user_email, token):
    message = Mail(
        from_email=config.SENDGRID_FROM_EMAIL,
        to_emails=user_email,
        subject='Verify Your Email',
        html_content=f'Click to verify: <a href="https://yourapp.com/verify?token={token}">Verify Email</a>'
    )
    sg = SendGridAPIClient(config.SENDGRID_API_KEY)
    sg.send(message)
```

**Cost:** FREE (100 emails/day)  
**Time:** 2-3 hours

---

### Add JWT Tokens (Production-Ready)

**Step 1:** Install dependencies
```bash
pip install python-jose[cryptography] passlib
```

**Step 2:** Create auth utils
```python
# utils/jwt_auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from config import config

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=config.JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
```

**Step 3:** Update login to generate token
```python
# components/auth.py - in login_page()
if user and user.check_password(password):
    # Generate JWT token
    token = create_access_token({"sub": user.username, "user_id": user.id})
    st.session_state.auth_token = token
    st.session_state.authenticated = True
    # ... rest of login
```

**Step 4:** Add API authentication decorator
```python
# For FastAPI/Flask API endpoints
from fastapi import Depends, HTTPException, Header

async def verify_jwt_token(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload
```

**Cost:** FREE  
**Time:** 4-6 hours

---

### Integrate Supabase Auth (Full OAuth Solution)

**Step 1:** Create Supabase project (https://supabase.com)
- Sign up free
- Create new project
- Enable Auth providers (Google, GitHub, etc.)

**Step 2:** Install Supabase
```bash
pip install supabase
```

**Step 3:** Add to .env
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key
```

**Step 4:** Replace auth.py with Supabase auth
```python
# components/auth.py
from supabase import create_client
from config import config

supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

def login_with_supabase(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        return None

def login_with_google():
    supabase.auth.sign_in_with_oauth({"provider": "google"})
```

**Step 5:** Keep your database for documents/conversations
- Use Supabase for authentication only
- Keep your current database.py for app data
- Link via user_id

**Cost:** FREE (50,000 users)  
**Time:** 3-5 hours

---

## 🎯 My Recommendation for You

Based on your project (production-ready RAG app for companies and users):

### **Phase 1: Now (MVP/Testing) ✅**
- ✅ Keep current system - **it's already good!**
- ✅ Add email verification (SendGrid free tier)
- ✅ Add password reset functionality
- **Time:** 2-3 hours
- **Cost:** FREE

### **Phase 2: Before Launch (1-2 weeks)**
- Add JWT tokens for API access
- Add session timeout (auto-logout after 1 hour inactivity)
- Add rate limiting to prevent brute force
- **Time:** 1 day
- **Cost:** FREE

### **Phase 3: After Launch (When You Have Users)**
- Add Supabase Auth for OAuth (Google, GitHub login)
- Keep JWT for API access
- Migrate existing users gradually
- **Time:** 2 days
- **Cost:** FREE (up to 50K users)

### **Phase 4: Enterprise Features (When Needed)**
- Add SSO/SAML for enterprise clients
- Add two-factor authentication (TOTP)
- Add audit logs
- **Time:** 1 week
- **Cost:** Pay per user for SSO

---

## 📧 Recommended Email Services

For email verification and password reset:

### **SendGrid (Recommended)**
- **FREE Tier:** 100 emails/day
- **Paid:** $15/mo for 40K emails
- **Setup:** 30 minutes
- **Docs:** https://docs.sendgrid.com

### **Resend (Modern Alternative)**
- **FREE Tier:** 3,000 emails/month
- **Paid:** $20/mo for 50K emails
- **Great API/docs**
- **Docs:** https://resend.com/docs

### **AWS SES**
- **Cost:** $0.10 per 1,000 emails
- **FREE Tier:** 3,000 emails/month (if on EC2)
- **Most scalable**

---

## 🔒 Security Best Practices (Already Implemented ✅)

Your current system already has:
- ✅ Password hashing with bcrypt
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Password strength requirements
- ✅ Input validation
- ✅ User activation/deactivation

**Add These:**
- [ ] Rate limiting on login (max 5 attempts per minute)
- [ ] Session timeout (auto-logout after inactivity)
- [ ] HTTPS only in production
- [ ] CSRF protection
- [ ] Email verification
- [ ] Password reset token expiration (1 hour)

---

## 🚀 Quick Start: Add Email Verification

I can implement email verification for you right now. It takes 2 hours and is FREE (SendGrid: 100 emails/day).

**What you need:**
1. SendGrid account (sign up free: https://signup.sendgrid.com/)
2. Get API key from SendGrid dashboard
3. Add to .env: `SENDGRID_API_KEY=your-key`

**What I'll add:**
- Email verification on signup
- Resend verification email button
- Verify email endpoint
- Block unverified users from uploading documents

**Want me to implement this now?**

---

## 📚 Additional Resources

- **JWT Best Practices:** https://jwt.io/introduction
- **OAuth 2.0 Guide:** https://oauth.net/2/
- **Supabase Auth Docs:** https://supabase.com/docs/guides/auth
- **OWASP Auth Cheatsheet:** https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html

---

## 💡 Summary

**Current State:** ✅ Your auth is already solid for MVP/internal use  
**Next Step:** Add email verification (2 hours, FREE)  
**Production:** Add JWT tokens (1 day, FREE)  
**Scale:** Add OAuth with Supabase (2 days, FREE up to 50K users)

**Your current system is production-ready for internal tools or MVPs!** Just add email verification and you're good to go. 🚀
