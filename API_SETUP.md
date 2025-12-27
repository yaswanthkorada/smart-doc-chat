# Complete API Setup Guide

This guide provides step-by-step instructions for setting up all external APIs and services required for the RAG Assistant application.

## Table of Contents
1. [OpenAI API (REQUIRED)](#1-openai-api-required)
2. [Storage Services (Choose One)](#2-storage-services)
3. [Vector Databases (Choose One)](#3-vector-databases)
4. [Database (Choose One)](#4-database)
5. [Email Service (Optional)](#5-email-service-optional)
6. [Summary & Cost Estimates](#6-summary--cost-estimates)

---

## 1. OpenAI API (REQUIRED)

### Why You Need It:
- Generate text embeddings for documents
- Power the chat responses (GPT-3.5/GPT-4)

### Setup Steps:

1. **Create OpenAI Account**
   - Go to: https://platform.openai.com/signup
   - Sign up with email or Google account

2. **Add Payment Method**
   - Go to: https://platform.openai.com/account/billing
   - Click "Add payment method"
   - Add credit/debit card
   - Set usage limits (recommended: $10-50/month)

3. **Generate API Key**
   - Go to: https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Name it: "RAG Assistant"
   - **IMPORTANT:** Copy the key immediately (starts with `sk-`)
   - Store safely - you can't see it again!

4. **Add to .env File**
   ```env
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
   OPENAI_MODEL=gpt-3.5-turbo
   OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
   ```

### Cost Estimates:
- **GPT-3.5-Turbo:** ~$0.01 per conversation
- **Embeddings:** ~$0.001 per document
- **Monthly (100 users):** ~$50-100

### Testing:
```python
import openai
openai.api_key = "your-key-here"
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

---

## 2. Storage Services

### Option A: Local Storage (Default - FREE) ✅

**Best for:** Development, Testing, Small Deployments

**Setup:**
```env
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./data/user_files
```

**Pros:**
- ✅ Free
- ✅ No setup required
- ✅ Fast for local development

**Cons:**
- ❌ Not scalable
- ❌ Lost if server restarts (unless persistent storage)
- ❌ No redundancy

---

### Option B: AWS S3 (Production)

**Best for:** Enterprise, High Traffic, AWS Ecosystem

**Setup Steps:**

1. **Create AWS Account**
   - Go to: https://aws.amazon.com
   - Sign up (requires credit card)

2. **Create S3 Bucket**
   - Go to S3 Console: https://s3.console.aws.amazon.com
   - Click "Create bucket"
   - Name: `rag-assistant-documents-[yourname]`
   - Region: `us-east-1` (or closest to users)
   - Block public access: ✅ (keep checked)
   - Click "Create bucket"

3. **Create IAM User**
   - Go to IAM Console: https://console.aws.amazon.com/iam
   - Click "Users" → "Add users"
   - Username: `rag-assistant-app`
   - Access type: ✅ Programmatic access
   - Permissions: Attach policy → `AmazonS3FullAccess`
   - Click through and **Download credentials CSV**

4. **Get Access Keys**
   From the CSV file:
   - Access Key ID: `AKIA...`
   - Secret Access Key: `wJalr...`

5. **Add to .env**
   ```env
   STORAGE_TYPE=s3
   AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
   AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=rag-assistant-documents-yourname
   ```

**Cost:** ~$0.023/GB/month + $0.09/GB data transfer

---

### Option C: Cloudflare R2 (RECOMMENDED) 🌟

**Best for:** Cost-Conscious, High Bandwidth

**Setup Steps:**

1. **Create Cloudflare Account**
   - Go to: https://dash.cloudflare.com/sign-up
   - Verify email

2. **Enable R2**
   - Dashboard → R2 Object Storage
   - Click "Purchase R2 Plan"
   - Select plan (Free tier: 10GB)

3. **Create Bucket**
   - Click "Create bucket"
   - Name: `rag-documents`
   - Location: Automatic
   - Click "Create bucket"

4. **Generate API Token**
   - R2 → Overview → "Manage R2 API Tokens"
   - Click "Create API token"
   - Name: "RAG Assistant"
   - Permissions: ✅ Object Read & Write
   - Copy:
     - Access Key ID
     - Secret Access Key
     - Account ID (from URL)

5. **Add to .env**
   ```env
   STORAGE_TYPE=r2
   R2_ACCOUNT_ID=abc123def456
   R2_ACCESS_KEY_ID=your_access_key_id
   R2_SECRET_ACCESS_KEY=your_secret_access_key
   R2_BUCKET_NAME=rag-documents
   R2_ENDPOINT=https://abc123def456.r2.cloudflarestorage.com
   ```

**Cost:** ~$0.015/GB/month + **$0 egress** 🎉

---

## 3. Vector Databases

### Option A: ChromaDB (Default - FREE) ✅

**Best for:** Development, Small Scale

**Setup:**
```env
VECTOR_DB_TYPE=chromadb
CHROMA_PERSIST_DIR=./data/chroma_data
```

**Pros:**
- ✅ Free
- ✅ No setup
- ✅ Local storage

**Cons:**
- ❌ Not distributed
- ❌ Limited scalability

---

### Option B: Pinecone (Production)

**Best for:** Production, Managed Service

**Setup Steps:**

1. **Create Account**
   - Go to: https://www.pinecone.io
   - Sign up (free trial available)

2. **Create Index**
   - Dashboard → "Create Index"
   - Name: `rag-assistant`
   - Dimensions: `1536` (for OpenAI embeddings)
   - Metric: `cosine`
   - Pod type: `p1.x1` (starter)
   - Click "Create Index"

3. **Get API Key**
   - Dashboard → "API Keys"
   - Copy your API key
   - Note your environment (e.g., `us-west1-gcp`)

4. **Add to .env**
   ```env
   VECTOR_DB_TYPE=pinecone
   PINECONE_API_KEY=your-api-key-here
   PINECONE_ENVIRONMENT=us-west1-gcp
   PINECONE_INDEX_NAME=rag-assistant
   ```

**Cost:** $70/month (1 pod)

---

### Option C: Qdrant

**Best for:** Self-Hosted or Cloud Alternative

**Setup Steps:**

**Cloud Option:**
1. Go to: https://cloud.qdrant.io
2. Create cluster (free tier: 1GB)
3. Get API key and URL

**Self-Hosted Option:**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**Add to .env:**
```env
VECTOR_DB_TYPE=qdrant
QDRANT_URL=https://your-cluster-url.qdrant.io
QDRANT_API_KEY=your-api-key
```

**Cost:** Free (self-hosted) or $25+/month (cloud)

---

## 4. Database

### Option A: SQLite (Default - FREE) ✅

**Best for:** Development, Single Server

**Setup:**
```env
DATABASE_URL=sqlite:///./data/rag_app.db
```

**Pros:**
- ✅ Free
- ✅ No setup
- ✅ File-based

**Cons:**
- ❌ Not for multi-server
- ❌ Limited concurrent writes

---

### Option B: PostgreSQL on Supabase (FREE TIER)

**Best for:** Production, Free Tier Available

**Setup Steps:**

1. **Create Supabase Account**
   - Go to: https://supabase.com
   - Sign up with GitHub

2. **Create Project**
   - Dashboard → "New Project"
   - Name: `rag-assistant`
   - Database Password: (create strong password)
   - Region: Closest to users
   - Plan: Free
   - Click "Create Project"

3. **Get Connection String**
   - Project Settings → Database
   - Copy "Connection string" (URI format)
   - Replace `[YOUR-PASSWORD]` with your password

4. **Add to .env**
   ```env
   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
   ```

**Free Tier:**
- 500MB database
- Unlimited API requests
- 50MB file storage

---

### Option C: AWS RDS PostgreSQL

**Setup Steps:**

1. Go to: https://console.aws.amazon.com/rds
2. Create database
3. Engine: PostgreSQL
4. Template: Free tier (or Production)
5. Instance: db.t3.micro (free tier eligible)
6. Set master password
7. Public access: Yes (for development)
8. Create database

**Get connection string:**
```env
DATABASE_URL=postgresql://username:password@your-rds-endpoint.amazonaws.com:5432/dbname
```

**Cost:** Free tier (12 months) → $15+/month

---

## 5. Email Service (Optional)

### Setup SMTP for Email Notifications

**Option A: Gmail**

1. **Enable 2FA**
   - Google Account → Security → 2-Step Verification

2. **Create App Password**
   - Google Account → Security → App passwords
   - Select app: "Mail"
   - Select device: "Other (Custom name)"
   - Name: "RAG Assistant"
   - Copy generated password

3. **Add to .env**
   ```env
   SMTP_ENABLED=True
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SMTP_FROM_EMAIL=your-email@gmail.com
   ```

**Option B: SendGrid**

1. Create account: https://sendgrid.com
2. Create API key
3. Verify sender email

```env
SMTP_ENABLED=True
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM_EMAIL=your-verified@email.com
```

---

## 6. Summary & Cost Estimates

### Recommended Setup for Different Scales:

#### **MVP / Development (FREE)**
```env
OPENAI_API_KEY=sk-...           # ~$10/month usage
STORAGE_TYPE=local
VECTOR_DB_TYPE=chromadb
DATABASE_URL=sqlite:///./data/rag_app.db
```
**Total Cost:** ~$10/month (OpenAI only)

#### **Small Production (< 1000 users)**
```env
OPENAI_API_KEY=sk-...           # ~$50/month
STORAGE_TYPE=r2                  # ~$5/month
VECTOR_DB_TYPE=chromadb         # Free (local) or Qdrant Cloud ($25)
DATABASE_URL=supabase           # Free tier
```
**Total Cost:** ~$55-80/month

#### **Large Production (1000+ users)**
```env
OPENAI_API_KEY=sk-...           # ~$200/month
STORAGE_TYPE=s3                  # ~$50/month
VECTOR_DB_TYPE=pinecone         # $70/month
DATABASE_URL=postgresql (RDS)   # ~$50/month
```
**Total Cost:** ~$370/month

---

## Quick Setup Checklist

- [ ] Create OpenAI account and get API key
- [ ] Choose storage provider (Local/S3/R2)
- [ ] Choose vector database (ChromaDB/Pinecone/Qdrant)
- [ ] Choose database (SQLite/PostgreSQL)
- [ ] Copy `.env.example` to `.env`
- [ ] Fill in all API keys in `.env`
- [ ] Run `pip install -r requirements.txt`
- [ ] Run `streamlit run app.py`
- [ ] Test with demo account (username: `demo`, password: `Demo@123`)

---

## Troubleshooting

### "Invalid API key"
- Double-check key is copied correctly
- Ensure no extra spaces
- Try regenerating the key

### "Permission denied"
- Check IAM permissions (AWS/R2)
- Verify API token has correct permissions

### "Connection refused"
- Check database URL is correct
- Verify firewall allows connections
- Test connection with `psql` or database client

### Need Help?
- Check logs: `tail -f logs/app.log`
- Enable debug mode: `DEBUG=True` in `.env`
- Restart application after .env changes

---

**Need help?** Open an issue on GitHub or email support@ragassistant.com
