# Supabase Setup Guide for RAG Application

## Step 1: Create Supabase Account & Project

### 1.1 Sign Up
1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project" or "Sign In"
3. Sign up with GitHub (recommended) or email
4. Verify your email if needed

### 1.2 Create New Project
1. Click "New Project"
2. Fill in the details:
   - **Project Name**: `rag-production` (or your choice)
   - **Database Password**: Create a strong password (SAVE THIS!)
   - **Region**: Choose closest to you (e.g., `ap-south-1` for India, `us-east-1` for US)
   - **Pricing Plan**: Select "Free" (2 projects allowed)
3. Click "Create new project"
4. Wait 2-3 minutes for setup to complete

---

## Step 2: Database Setup

### 2.1 Create Users Table
1. Go to **SQL Editor** in left sidebar
2. Click "New Query"
3. Run this SQL:

```sql
-- Create users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Add index for faster lookups
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

### 2.2 Create Documents Table
```sql
-- Create documents table for RAG
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    file_path TEXT,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    chunk_count INTEGER DEFAULT 0,
    metadata JSONB
);

CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_upload_date ON documents(upload_date);
```

### 2.3 Create Chat History Table
```sql
-- Create chat history table
CREATE TABLE IF NOT EXISTS chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL,
    message TEXT NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    model_used VARCHAR(50),
    tokens_used INTEGER,
    metadata JSONB
);

CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_history_session_id ON chat_history(session_id);
CREATE INDEX idx_chat_history_timestamp ON chat_history(timestamp);
```

### 2.4 Create Settings Table
```sql
-- Create user settings table
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    default_model VARCHAR(50) DEFAULT 'gemini-pro',
    temperature DECIMAL(3,2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 2000,
    theme VARCHAR(20) DEFAULT 'light',
    preferences JSONB,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_settings_user_id ON user_settings(user_id);
```

---

## Step 3: Storage Setup

### 3.1 Create Storage Buckets
1. Go to **Storage** in left sidebar
2. Click "Create a new bucket"

#### Create "documents" bucket:
- **Name**: `documents`
- **Public**: OFF (private)
- **File size limit**: 50 MB
- **Allowed MIME types**: Leave empty or add:
  - `application/pdf`
  - `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
  - `application/vnd.openxmlformats-officedocument.presentationml.presentation`
  - `text/plain`
  - `application/vnd.ms-excel`
  - `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

#### Create "avatars" bucket (optional):
- **Name**: `avatars`
- **Public**: ON
- **File size limit**: 2 MB
- **Allowed MIME types**: `image/jpeg`, `image/png`, `image/webp`

### 3.2 Set Storage Policies
Go to **Storage** → Select bucket → **Policies** → Click "New Policy"

#### Option A: Use Policy Templates (EASIEST - RECOMMENDED)
1. Click "New Policy"
2. Select **"Allow access to authenticated users only"**
3. Click "Use this template"
4. Policy is automatically created!

#### Option B: Create Custom Policy via UI
If you need custom policies, use the UI policy builder:

**Policy 1: Upload Documents**
- Policy name: `Users can upload documents`
- Allowed operation: ✅ INSERT
- Target roles: `authenticated`
- Policy definition:
```sql
bucket_id = 'documents'
```

**Policy 2: Read Documents**  
- Policy name: `Users can read documents`
- Allowed operation: ✅ SELECT
- Target roles: `authenticated`
- Policy definition:
```sql
bucket_id = 'documents'
```

**Policy 3: Delete Documents**
- Policy name: `Users can delete documents`
- Allowed operation: ✅ DELETE
- Target roles: `authenticated`
- Policy definition:
```sql
bucket_id = 'documents'
```

#### Option C: Create Policies via SQL Editor (Advanced)
If you prefer SQL, go to **SQL Editor** and run:
```sql
-- Enable RLS on storage.objects
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Policy: Users can upload documents
CREATE POLICY "Users can upload documents"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'documents');

-- Policy: Users can read documents
CREATE POLICY "Users can read documents"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'documents');

-- Policy: Users can delete documents
CREATE POLICY "Users can delete documents"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'documents');
```

**Note**: The simplified policies above allow ANY authenticated user to access ANY file in the bucket. This is fine for testing. For production with user isolation, see "Advanced: User-Specific Access" section below.

---

### 3.3 Advanced: User-Specific File Access (Optional)

If you want users to ONLY see their own files, use this approach:

**Structure your file paths as:** `user_id/filename.ext`

Then update policies in SQL Editor:

```sql
-- Upload: Users can only upload to their own folder
CREATE POLICY "Users upload to own folder"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'documents' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Read: Users can only read from their own folder
CREATE POLICY "Users read own folder"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'documents' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Delete: Users can only delete from their own folder
CREATE POLICY "Users delete own files"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'documents' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);
```

**Important**: If you use user-specific access, update your upload code to include user_id in the path:
```python
storage_path = f"{user_id}/{filename}"  # ✅ Correct
# NOT: storage_path = f"{filename}"  # ❌ Wrong - won't work with RLS
```

---

## Step 4: Authentication Setup

### 4.1 Configure Auth Settings
1. Go to **Authentication** → **Settings**
2. Configure:
   - **Site URL**: Your Streamlit app URL (e.g., `https://your-app.streamlit.app`)
   - **Redirect URLs**: Add your app URL + `/callback`

### 4.2 Enable Auth Providers
In **Authentication** → **Providers**:
- ✅ **Email** (enabled by default)
- Optional: Enable Google, GitHub OAuth if needed

### 4.3 Email Templates (Optional)
In **Authentication** → **Email Templates**:
- Customize confirmation, reset password emails
- Or keep defaults

---

## Step 5: Get API Keys & Connection Details

### 5.1 Get Project Credentials
1. Go to **Settings** → **API**
2. Copy these values:

```
Project URL: https://xxxxx.supabase.co
API Key (anon public): eyJhbGci...
API Key (service_role): eyJhbGci... (Keep SECRET!)
```

### 5.2 Get Database Connection String
1. Go to **Settings** → **Database**
2. Copy **Connection string** → **URI** format:

```
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

---

## Step 6: Configure Streamlit App

### 6.1 Install Supabase Python Client
```bash
pip install supabase
```

### 6.2 Create `.streamlit/secrets.toml`
Create this file in your project root:

```toml
# .streamlit/secrets.toml
[supabase]
url = "https://xxxxx.supabase.co"
key = "eyJhbGci..." # anon public key
service_role_key = "eyJhbGci..." # service role key (for admin operations)

[database]
connection_string = "postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres"

[api_keys]
GOOGLE_API_KEY = "your-gemini-api-key"
OPENAI_API_KEY = "your-openai-api-key"
```

### 6.3 Create Supabase Client Helper
Create `utils/supabase_client.py`:

```python
import streamlit as st
from supabase import create_client, Client
import os

def get_supabase_client() -> Client:
    """Initialize and return Supabase client"""
    try:
        # Try to get from Streamlit secrets first (for deployed app)
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
    except:
        # Fallback to environment variables (for local development)
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("Supabase credentials not found!")
    
    return create_client(url, key)

# Initialize client
supabase: Client = get_supabase_client()
```

---

## Step 7: Update Your App Code

### 7.1 Update Authentication (`components/auth.py`)
```python
import streamlit as st
from utils.supabase_client import supabase
import hashlib

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def login(username: str, password: str) -> bool:
    """Login user with Supabase"""
    try:
        password_hash = hash_password(password)
        
        # Query user from database
        response = supabase.table('users').select('*').eq('username', username).eq('password_hash', password_hash).execute()
        
        if response.data and len(response.data) > 0:
            user = response.data[0]
            
            # Update last login
            supabase.table('users').update({
                'last_login': 'now()'
            }).eq('id', user['id']).execute()
            
            # Store in session state
            st.session_state['authenticated'] = True
            st.session_state['user_id'] = user['id']
            st.session_state['username'] = user['username']
            st.session_state['user_email'] = user['email']
            
            return True
        return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False

def signup(username: str, email: str, password: str, full_name: str = None) -> bool:
    """Register new user"""
    try:
        password_hash = hash_password(password)
        
        # Insert new user
        response = supabase.table('users').insert({
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'full_name': full_name
        }).execute()
        
        if response.data:
            st.success("Account created successfully! Please login.")
            return True
        return False
    except Exception as e:
        st.error(f"Signup error: {str(e)}")
        return False
```

### 7.2 Update Document Upload
```python
from utils.supabase_client import supabase
import uuid

def upload_document(file, user_id: str):
    """Upload document to Supabase Storage"""
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_ext = file.name.split('.')[-1]
        storage_path = f"{user_id}/{file_id}.{file_ext}"
        
        # Upload to storage
        supabase.storage.from_('documents').upload(
            storage_path,
            file.read(),
            file_options={"content-type": file.type}
        )
        
        # Save metadata to database
        supabase.table('documents').insert({
            'user_id': user_id,
            'filename': file.name,
            'file_type': file.type,
            'file_size': file.size,
            'file_path': storage_path
        }).execute()
        
        return True
    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return False
```

### 7.3 Save Chat History
```python
def save_chat_message(user_id: str, session_id: str, message: str, role: str, model: str = None):
    """Save chat message to database"""
    try:
        supabase.table('chat_history').insert({
            'user_id': user_id,
            'session_id': session_id,
            'message': message,
            'role': role,
            'model_used': model
        }).execute()
    except Exception as e:
        print(f"Error saving chat: {e}")

def get_chat_history(user_id: str, session_id: str = None, limit: int = 50):
    """Retrieve chat history"""
    try:
        query = supabase.table('chat_history').select('*').eq('user_id', user_id)
        
        if session_id:
            query = query.eq('session_id', session_id)
        
        response = query.order('timestamp', desc=True).limit(limit).execute()
        return response.data
    except Exception as e:
        print(f"Error getting chat history: {e}")
        return []
```

---

## Step 8: Deploy to Streamlit Cloud

### 8.1 Push to GitHub
```bash
git add .
git commit -m "Add Supabase integration"
git push origin main
```

### 8.2 Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your GitHub repository
4. Set main file: `app.py`
5. **Advanced settings** → Add secrets from your `.streamlit/secrets.toml`
6. Click "Deploy"

### 8.3 Add Secrets in Streamlit Cloud
In deployment settings, paste your secrets:
```toml
[supabase]
url = "https://xxxxx.supabase.co"
key = "your-anon-key"

[api_keys]
GOOGLE_API_KEY = "your-key"
```

---

## Step 9: Testing Checklist

- [ ] User can sign up
- [ ] User can login
- [ ] User can upload documents
- [ ] Documents appear in Supabase Storage
- [ ] Chat messages save to database
- [ ] Chat history loads correctly
- [ ] User settings save/load
- [ ] File size limits enforced (50 MB)
- [ ] Only user's own files are visible

---

## Step 10: Monitor Usage

### Check Free Tier Usage:
1. Go to Supabase Dashboard → **Settings** → **Usage**
2. Monitor:
   - Database size (500 MB limit)
   - Storage (1 GB limit)
   - Bandwidth (10 GB/month)
   - API requests

### Auto-Pause Warning:
- Projects pause after 7 days of inactivity
- Visit your app weekly to keep it active
- Or upgrade to Pro ($25/month) for always-on

---

## Troubleshooting

### Issue: "Project is paused"
- **Solution**: Go to Supabase dashboard → Click "Resume project"
- Takes 1-2 minutes to wake up

### Issue: "Storage limit exceeded"
- **Solution**: Delete old documents or upgrade plan

### Issue: "Database connection failed"
- **Solution**: Check connection string and password
- Verify IP whitelist (usually not needed for Supabase)

### Issue: "Auth error"
- **Solution**: Verify Site URL and Redirect URLs in Auth settings

---

## Security Best Practices

1. **Never commit** `.streamlit/secrets.toml` to GitHub
2. Add to `.gitignore`:
   ```
   .streamlit/secrets.toml
   .env
   ```
3. Use **service_role_key** only for admin operations, never in client code
4. Enable Row Level Security (RLS) on all tables
5. Use proper storage policies to restrict access

---

## Quick Reference: Environment Variables

For local development, create `.env`:
```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
GOOGLE_API_KEY=your-gemini-key
```

Load with:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Next Steps

1. ✅ Create Supabase project
2. ✅ Set up database tables
3. ✅ Configure storage buckets
4. ✅ Get API keys
5. ✅ Update app code
6. ✅ Deploy to Streamlit Cloud
7. 🚀 Test everything!

**Your app will now work properly in the deployed environment, bypassing your office laptop's SSL issues!**
