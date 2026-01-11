# Supabase Auth Integration & Gemini AI Default

## ✅ Changes Completed

### 1. **Supabase Auth Integration**

#### Login Options
- **Username/Password**: Original authentication method (uses password hash)
- **Email (Supabase Auth)**: New Supabase Auth method with email confirmation

#### How It Works
```python
# Supabase Auth Login Flow:
1. User enters email + password
2. App calls supabase.auth.sign_in_with_password()
3. On success, gets user_id (UUID) from Supabase Auth
4. Creates or updates user record in `users` table
5. Stores auth token in session_state.supabase_auth_token
```

#### Signup Options
- **Username/Password**: Original signup (manual user creation)
- **Email (Supabase Auth)**: Supabase Auth signup with email confirmation

#### User Data Storage
When user signs up via Supabase Auth:
```python
user_data = {
    'id': user_id,  # UUID from Supabase Auth
    'email': email,
    'username': email.split('@')[0],  # Auto-generated from email
    'full_name': full_name,
    'subscription_tier': 'free'
}
supabase.table('users').insert(user_data).execute()
```

#### Session State Variables
```python
st.session_state.authenticated = True
st.session_state.user_id = user_id  # UUID
st.session_state.username = username
st.session_state.user_email = email
st.session_state.subscription_tier = 'free'
st.session_state.supabase_auth_token = auth_response.session.access_token
```

---

### 2. **Gemini AI as Default**

#### Configuration Changes
**config/settings.py:**
```python
# Changed from:
AI_PROVIDER = get_config_value("AI_PROVIDER", "openai")
EMBEDDING_PROVIDER = get_config_value("EMBEDDING_PROVIDER", "openai")

# To:
AI_PROVIDER = get_config_value("AI_PROVIDER", "gemini")  # FREE!
EMBEDDING_PROVIDER = get_config_value("EMBEDDING_PROVIDER", "gemini")  # FREE!
```

#### UI Changes
**app.py** - AI Provider Dropdown:
```python
ai_provider = st.selectbox(
    "🤖 AI Model",
    options=["gemini", "openai"],  # Gemini first
    index=0,  # Default to Gemini (first option)
    format_func=lambda x: "✨ Gemini AI (Free)" if x == "gemini" else "🤖 OpenAI (Paid)",
    help="Gemini: Free 1000 req/day with automatic embeddings | OpenAI: Paid with automatic embeddings"
)
```

---

### 3. **Automatic LLM & Embeddings Switching**

#### Dynamic Provider Switching
When user changes dropdown, **both** LLM and embeddings switch automatically:

```python
# Detect provider change
if st.session_state.previous_ai_provider != ai_provider:
    # Update RAG engine with new provider
    if rag_engine.update_provider(ai_provider):
        st.success(f"✅ Switched to {ai_provider.upper()} (LLM + Embeddings)")
    st.session_state.previous_ai_provider = ai_provider
```

#### What Gets Switched
1. **LLM Model**: `gemini-2.0-flash-exp` ↔ `gpt-5-nano`
2. **Embeddings**: `models/embedding-001` ↔ `text-embedding-3-small`
3. **Vector Store**: Separate ChromaDB collections per provider

---

### 4. **Fixed update_document_status() Errors**

#### Problem
```python
# Old (WRONG):
db_manager.update_document_status(
    doc_id=doc_id,  # ❌ Parameter doesn't exist
    status="completed",  # ❌ Should be 'processed' boolean
    num_chunks=len(chunks)  # ❌ Should be 'chunk_count'
)
```

#### Solution
```python
# New (CORRECT):
db_manager.update_document_status(
    document_id=doc_id,  # ✅ Correct parameter
    processed=True,  # ✅ Boolean instead of string
    chunk_count=len(chunks)  # ✅ Correct parameter name
)
```

#### Files Fixed
- `utils/rag_engine.py` - 6 occurrences fixed:
  - YouTube processing (success + error)
  - Website processing (success + error)
  - Document processing (success + error)

---

### 5. **Fixed SQLAlchemy Reserved Word Error**

#### Problem
```python
# WRONG - 'metadata' is reserved by SQLAlchemy
class Document(Base):
    metadata = Column(Text)  # ❌ Conflict with Base.metadata
```

#### Solution
```python
# CORRECT - Use 'doc_metadata' in Python, map to 'metadata' in DB
class Document(Base):
    doc_metadata = Column('metadata', Text)  # ✅ No conflict
```

---

## 🔐 Supabase Auth Setup Required

### 1. Enable Auth in Supabase Dashboard
Go to: **Authentication → Sign In / Providers**

Settings (Already Done):
- ✅ Allow new users to sign up: **ON**
- ✅ Confirm email: **ON**
- ❌ Allow anonymous sign-ins: **OFF**

### 2. Required SQL for Documents Table
```sql
-- Allow authenticated users to insert/update their own documents
CREATE POLICY "Allow authenticated users to manage their documents"
ON documents
FOR ALL
USING (auth.uid()::text = user_id::text);
```

### 3. Required SQL for Users Table
```sql
-- Add subscription_tier column if missing
ALTER TABLE users
ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(50) DEFAULT 'free';
```

---

## 🚀 Deployment Checklist

### Before Deploying to Streamlit Cloud:

1. **Commit and Push Changes**
   ```bash
   git add .
   git commit -m "Integrate Supabase Auth + Gemini Default + Auto-switch"
   git push origin feature/supabase
   ```

2. **Update Streamlit Secrets**
   Add to `secrets.toml`:
   ```toml
   [api_keys]
   GOOGLE_API_KEY = "your_gemini_api_key"
   OPENAI_API_KEY = "your_openai_api_key"
   
   [supabase]
   url = "https://xxxxx.supabase.co"
   key = "your_anon_key"
   service_role_key = "your_service_role_key"
   db_password = "your_database_password"
   ```

3. **Reboot Streamlit App**
   - Go to https://docgenius-ai.streamlit.app/
   - Click "Manage app" → "Reboot"

4. **Test Supabase Auth**
   - Click "Sign Up" → Choose "Email (Supabase Auth)"
   - Register with email
   - Check email for confirmation link
   - Login after confirmation

5. **Test Provider Switching**
   - Login to app
   - Change dropdown from "✨ Gemini AI (Free)" to "🤖 OpenAI (Paid)"
   - Should see: "✅ Switched to OPENAI (LLM + Embeddings)"
   - Upload a document - should work with selected provider

---

## 📊 How User Data is Stored

### With Username/Password Auth:
```
users table:
├── id (UUID, auto-generated)
├── username (user-provided)
├── email (user-provided)
├── password_hash (SHA256)
├── subscription_tier (default: 'free')
└── created_at
```

### With Supabase Auth:
```
1. Supabase Auth (auth.users):
   ├── id (UUID, from Supabase)
   ├── email (from signup)
   └── confirmed_at (after email confirmation)

2. App Database (users table):
   ├── id (UUID, same as Supabase Auth id)
   ├── email (from Supabase Auth)
   ├── username (auto: email prefix)
   ├── subscription_tier (default: 'free')
   └── created_at

3. Session State:
   ├── user_id (UUID)
   ├── username
   ├── user_email
   ├── subscription_tier
   └── supabase_auth_token (JWT for RLS policies)
```

### How Documents Link to Users:
```sql
documents table:
├── id (UUID, primary key)
├── user_id (UUID, foreign key to users.id)  -- Links to authenticated user
├── filename
├── file_path (Supabase Storage path)
├── chunk_count
├── processed (boolean)
└── doc_metadata (JSONB as text)
```

---

## 🔑 Key Benefits

1. **Dual Authentication**: Users can choose Username or Email signup
2. **Free by Default**: Gemini AI is free (1000 req/day) vs OpenAI paid
3. **Seamless Switching**: Change AI provider without restarting app
4. **Secure**: Row Level Security (RLS) uses `auth.uid()` for authorization
5. **Email Confirmation**: Supabase Auth requires email verification
6. **Automatic User Creation**: App auto-creates user records in database

---

## 🐛 Issues Fixed

1. ✅ `metadata` reserved word conflict → `doc_metadata`
2. ✅ `update_document_status()` parameter errors → Fixed 6 occurrences
3. ✅ Default to Gemini instead of OpenAI
4. ✅ Manual LLM/embeddings switching → Automatic
5. ✅ Row Level Security 403 errors → Need to add RLS policies

---

## 📝 Next Steps

1. **Test Locally**: Run `streamlit run app.py` and test:
   - Supabase Auth signup/login
   - Provider switching
   - Document upload

2. **Add RLS Policies**: Run the SQL commands in Supabase SQL Editor

3. **Deploy**: Push to GitHub and reboot Streamlit Cloud

4. **Monitor**: Check Streamlit Cloud logs for any errors

---

## 🔧 Troubleshooting

### Issue: "403 Unauthorized - row-level security policy"
**Solution**: Add RLS policy to allow authenticated users:
```sql
CREATE POLICY "Allow authenticated users"
ON documents FOR ALL
USING (auth.uid()::text = user_id::text);
```

### Issue: "column subscription_tier does not exist"
**Solution**: Add column to users table:
```sql
ALTER TABLE users ADD COLUMN subscription_tier VARCHAR(50) DEFAULT 'free';
```

### Issue: Provider switching doesn't work
**Solution**: Check that `rag_engine.update_provider()` is called and API keys are set

---

**Created**: December 28, 2025
**Status**: ✅ Ready for Testing & Deployment
