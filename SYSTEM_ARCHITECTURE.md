# 🏗️ RAG System Architecture - Complete Guide for Beginners

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Storage Systems (3 Databases)](#storage-systems)
3. [Memory Management](#memory-management)
4. [Complete Pipeline Flow](#complete-pipeline-flow)
5. [Switching Between AI Providers](#switching-between-ai-providers)
6. [Cost Optimization](#cost-optimization)

---

## 🎯 System Overview

Your RAG (Retrieval-Augmented Generation) application uses **3 storage systems** and **2 memory types** to provide intelligent document-based chat.

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG ASSISTANT SYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  User Interface (Streamlit)                                  │
│  ↓                                                            │
│  Authentication Layer (SQLite)                               │
│  ↓                                                            │
│  ┌─────────────┬──────────────┬─────────────────┐          │
│  │  Document   │   Vector DB  │   Conversation  │          │
│  │  Storage    │   (ChromaDB) │   DB (SQLite)   │          │
│  │  (Local)    │              │                  │          │
│  └─────────────┴──────────────┴─────────────────┘          │
│  ↓                                                            │
│  RAG Engine (AI Processing)                                  │
│  ↓                                                            │
│  AI Models (Gemini/OpenAI)                                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Storage Systems (3 Databases)

### **1. SQLite Database (Structured Data)**
**Location:** `./data/rag_app.db`
**Purpose:** Store user info, document metadata, and conversation history

#### Tables:
```sql
┌──────────────┐
│   users      │  ← User accounts (username, password, email)
└──────────────┘
       ↓
┌──────────────┐
│  documents   │  ← File metadata (name, size, type, status)
└──────────────┘
       ↓
┌──────────────┐
│conversations │  ← Chat sessions (title, user_id, timestamp)
└──────────────┘
       ↓
┌──────────────┐
│  messages    │  ← All chat messages (user + assistant)
└──────────────┘
```

**What it stores:**
- ✅ User credentials (hashed passwords)
- ✅ Document metadata (filename, size, upload date, processing status)
- ✅ Conversation history (ALL messages - persistent)
- ✅ Message feedback (helpful/not helpful ratings)

**Why SQLite?**
- Fast for structured queries
- No setup needed (file-based)
- Perfect for <100GB data
- Upgrade to PostgreSQL for production

---

### **2. Vector Database - ChromaDB (Embeddings)**
**Location:** `./data/chroma_data/user_{user_id}/`
**Purpose:** Store document embeddings for semantic search

#### How it works:
```
Document Text                    Vector Embedding
"The cat sat on mat"      →     [0.23, -0.45, 0.67, ..., 0.12]
                                  (768 or 1536 dimensions)
```

**What it stores:**
```
Collection: user_1_docs
├── Chunk 1: [0.23, -0.45, ...] + metadata (doc_id, filename, page)
├── Chunk 2: [0.12, 0.89, ...] + metadata
├── Chunk 3: [-0.67, 0.34, ...] + metadata
└── ... (all document chunks as vectors)
```

**Why ChromaDB?**
- Fast similarity search (cosine similarity)
- Stores vectors + metadata together
- Per-user isolation (`user_1/`, `user_2/`)
- Persistent on disk

**Data Structure:**
```python
{
  "id": "doc_abc123_chunk_5",
  "embedding": [0.23, -0.45, 0.67, ...],  # 768/1536 numbers
  "metadata": {
    "doc_id": "doc_abc123",
    "user_id": 1,
    "filename": "report.pdf",
    "page": 5,
    "chunk_index": 5
  },
  "document": "This is the actual text content of chunk 5..."
}
```

---

### **3. Local File Storage (Raw Files)**
**Location:** `./data/user_files/user_{user_id}/documents/`
**Purpose:** Store original uploaded files

```
./data/user_files/
├── user_1/
│   └── documents/
│       ├── report.pdf          ← Original PDF
│       ├── contract.docx       ← Original DOCX
│       └── data.xlsx           ← Original Excel
├── user_2/
│   └── documents/
│       └── presentation.pptx
```

**Why Local Storage?**
- Keep original files for re-processing
- Allow users to download files later
- Backup/audit purposes
- Can switch to S3/Azure Blob for production

---

## 🧠 Memory Management

### **SHORT-TERM MEMORY (Session Context)**

**What:** Last 5 conversation exchanges (10 messages)
**Where:** Loaded into RAM during query
**Purpose:** Maintain conversation context

```python
# Example: Last 5 exchanges
[
  ("What is the revenue?", "Revenue is $5M according to page 3"),
  ("What about expenses?", "Expenses are $3M as shown on page 5"),
  ("Calculate profit", "Profit = Revenue - Expenses = $2M"),
  ("Show profit margin", "Profit margin = 40%"),
  ("Is this good?", "Yes, 40% is excellent for this industry")
]
```

**Code Location:** [rag_engine.py#L305-L313](utils/rag_engine.py#L305-L313)

```python
# Keep only last 5 exchanges
chat_history = chat_history[-5:]
```

**Why only 5?**
- Reduces token usage = lower cost
- Prevents context overflow (models have token limits)
- Keeps responses focused on recent context

---

### **LONG-TERM MEMORY (Persistent Knowledge)**

#### **A. Conversation History (SQLite)**
**What:** ALL messages from ALL conversations
**Where:** `messages` table in SQLite
**Purpose:** Full conversation history, analytics, reloading old chats

```sql
SELECT * FROM messages WHERE conversation_id = 'conv_123';
```

**Stores:**
- message_id
- conversation_id
- role (user/assistant)
- content (the actual message)
- timestamp
- sources (JSON of retrieved documents)
- tokens_used
- feedback (helpful/not_helpful)

---

#### **B. Document Knowledge (ChromaDB)**
**What:** ALL document content as vectors
**Where:** `./data/chroma_data/user_1/`
**Purpose:** Semantic search to find relevant info

**How Semantic Search Works:**
```
User Query: "What is the revenue?"
     ↓
Convert to embedding: [0.23, -0.45, 0.67, ...]
     ↓
Search ChromaDB for similar vectors (cosine similarity)
     ↓
Find top 4 most similar chunks:
  - Chunk 45: "Revenue for Q1 is $5M" (similarity: 0.92)
  - Chunk 103: "Total revenue breakdown..." (similarity: 0.87)
  - Chunk 67: "Revenue increased by 20%" (similarity: 0.81)
  - Chunk 12: "Revenue projections..." (similarity: 0.78)
     ↓
Return these chunks as context for LLM
```

---

## 🔄 Complete Pipeline Flow

### **Pipeline 1: Document Upload & Processing**

```
┌─────────────────────────────────────────────────────────────┐
│                   DOCUMENT PROCESSING PIPELINE               │
└─────────────────────────────────────────────────────────────┘

Step 1: User Uploads File (PDF/DOCX/TXT)
  ↓
Step 2: Save to Local Storage
  → ./data/user_files/user_1/documents/report.pdf
  ↓
Step 3: Add Metadata to SQLite
  → INSERT INTO documents (filename, user_id, status='processing')
  ↓
Step 4: Extract Text
  → PDF: PyPDF2 (page by page)
  → DOCX: python-docx
  → TXT: Direct read
  ↓
Step 5: Split into Chunks
  → RecursiveCharacterTextSplitter
  → chunk_size=1000 characters
  → chunk_overlap=200 characters
  → Example: 50-page PDF → ~200 chunks
  ↓
Step 6: Generate Embeddings
  → Option A: Hugging Face (FREE, local)
    - Model: sentence-transformers/all-mpnet-base-v2
    - Runs on your CPU/GPU
    - Output: 768-dimensional vectors
  → Option B: OpenAI (text-embedding-3-small)
    - API call: $0.02/1M tokens
    - Output: 1536-dimensional vectors
  → Option C: Gemini (models/embedding-001)
    - Free tier: 1000 requests/day
    - Output: 768-dimensional vectors
  ↓
Step 7: Store in ChromaDB
  → For each chunk:
    - Vector: [0.23, -0.45, ...]
    - Metadata: {doc_id, filename, page, chunk_index}
    - Text: actual chunk content
  ↓
Step 8: Update SQLite
  → UPDATE documents SET status='completed', num_chunks=200
  ↓
✅ Document Ready for Querying!
```

**Code Flow:**
1. User uploads in UI → [pages/2_📁_Documents.py](pages/2_📁_Documents.py)
2. `rag_engine.process_document()` → [rag_engine.py#L189](utils/rag_engine.py#L189)
3. `extract_text_from_file()` → [rag_engine.py#L127](utils/rag_engine.py#L127)
4. `split_documents()` → [rag_engine.py#L162](utils/rag_engine.py#L162)
5. `vectorstore.add_texts()` → [rag_engine.py#L239](utils/rag_engine.py#L239)
6. `db_manager.update_document_status()` → [rag_engine.py#L248](utils/rag_engine.py#L248)

---

### **Pipeline 2: Chat Query & Response**

```
┌─────────────────────────────────────────────────────────────┐
│                   QUERY PROCESSING PIPELINE                  │
└─────────────────────────────────────────────────────────────┘

Step 1: User Types Question
  → "What is the total revenue for Q1 2024?"
  ↓
Step 2: Load Short-Term Memory (Last 5 Exchanges)
  → Query SQLite for last 10 messages
  → Format as [(question1, answer1), (question2, answer2), ...]
  ↓
Step 3: Convert Query to Embedding
  → Use same embedding model as documents
  → "What is the total revenue..." → [0.45, -0.23, 0.67, ...]
  ↓
Step 4: Semantic Search in ChromaDB
  → Find top 4 most similar chunks
  → Use cosine similarity between query vector and document vectors
  → Returns:
    [
      {text: "Q1 2024 revenue is $5M", similarity: 0.92, page: 3},
      {text: "Revenue breakdown by...", similarity: 0.87, page: 5},
      {text: "Compared to Q1 2023...", similarity: 0.81, page: 7},
      {text: "Revenue projections...", similarity: 0.78, page: 9}
    ]
  ↓
Step 5: Build Context for LLM
  → Combine:
    - Chat history (last 5 exchanges)
    - Retrieved documents (top 4 chunks)
    - Current query
  → Format into prompt:
    """
    Chat History:
    User: What about expenses?
    Assistant: Expenses are $3M...
    
    Relevant Documents:
    [Document 1]: Q1 2024 revenue is $5M (from report.pdf, page 3)
    [Document 2]: Revenue breakdown by region...
    
    User Question: What is the total revenue for Q1 2024?
    
    Instructions: Answer based on the provided documents. Be specific.
    """
  ↓
Step 6: Send to AI Model
  → Option A: Gemini API
    - Model: gemini-2.0-flash-exp
    - FREE: 1000 requests/day
    - Speed: ~2 seconds
  → Option B: OpenAI API
    - Model: gpt-5-nano (cheapest)
    - Cost: $0.05/1M input, $0.40/1M output
    - Speed: ~1 second
  ↓
Step 7: Get AI Response
  → "Based on the Q1 2024 financial report (page 3), 
     the total revenue is $5M, representing a 20% increase 
     from Q1 2023."
  ↓
Step 8: Save to SQLite (Long-Term Memory)
  → INSERT INTO messages:
    - user message (question)
    - assistant message (answer)
    - sources (JSON with retrieved chunks)
    - tokens_used
    - timestamp
  ↓
Step 9: Display to User
  → Show answer
  → Show sources (with page numbers)
  → Show feedback buttons (👍 👎)
  ↓
✅ Query Complete!
```

**Code Flow:**
1. User types → [app.py#L200](app.py#L200)
2. `rag_engine.query_documents()` → [rag_engine.py#L288](utils/rag_engine.py#L288)
3. Load chat history → [rag_engine.py#L305](utils/rag_engine.py#L305)
4. Semantic search → `vectorstore.similarity_search()`
5. Call LLM → `_query_with_gemini()` or `_query_with_openai()`
6. Save to DB → `db_manager.add_message()`
7. Display → [chat_interface.py#L7](components/chat_interface.py#L7)

---

## 🔀 Switching Between AI Providers

### **Method 1: Environment Variables (.env file)**

```env
# For Development (FREE)
AI_PROVIDER="gemini"                    # Chat: Gemini (free)
EMBEDDING_PROVIDER="huggingface"        # Embeddings: Hugging Face (free)

# When Gemini Quota Exceeded (CHEAP)
AI_PROVIDER="openai"                    # Chat: OpenAI gpt-5-nano
EMBEDDING_PROVIDER="openai"             # Embeddings: text-embedding-3-small
```

### **Method 2: UI Dropdown (Runtime)**

In [app.py#L146](app.py#L146), you can switch providers via dropdown:
```python
ai_provider = st.selectbox(
    "🤖 AI Model",
    options=["gemini", "openai"],
    help="Choose AI provider"
)
```

### **How Switching Works:**

```python
# In rag_engine.py __init__()

# Embeddings
if EMBEDDING_PROVIDER == "huggingface":
    self.embeddings = HuggingFaceEmbeddings(...)  # FREE
elif EMBEDDING_PROVIDER == "openai":
    self.embeddings = OpenAIEmbeddings(...)       # $0.02/1M tokens
else:
    self.embeddings = GoogleGenerativeAIEmbeddings(...)  # Free tier

# Chat
if AI_PROVIDER == "gemini":
    self.model = genai.GenerativeModel(...)       # FREE
else:
    self.llm = ChatOpenAI(...)                    # gpt-5-nano
```

**Important:** If you switch embedding providers, you need to **re-process all documents** because embeddings are incompatible (768 vs 1536 dimensions).

---

## 💰 Cost Optimization

### **Current Setup (FREE for Dev):**
```
Embeddings: Hugging Face (sentence-transformers/all-mpnet-base-v2)
  → Cost: $0 (runs locally on your machine)
  → Speed: ~1 sec per document
  
Chat: Gemini (gemini-2.0-flash-exp)
  → Cost: $0 for first 1000 requests/day
  → After limit: Switch to OpenAI
```

### **OpenAI Backup (When Gemini Quota Exceeded):**
```
Embeddings: text-embedding-3-small
  → Cost: $0.02 per 1M tokens
  → Example: 100 documents (~500 pages) = ~250K tokens = $0.005
  
Chat: gpt-5-nano
  → Cost: $0.05/1M input + $0.40/1M output
  → Example: 100 queries (avg 500 tokens each) = 50K tokens = $0.0025
  
Total: ~$0.01 per day for moderate usage
```

### **Cost Comparison:**
| Provider | Embeddings | Chat | Daily Cost (100 queries) |
|----------|------------|------|--------------------------|
| **Hugging Face + Gemini** | $0 | $0 | **$0.00** ✅ |
| **OpenAI (cheapest)** | $0.005 | $0.025 | **$0.03** |
| **OpenAI (gpt-4)** | $0.005 | $2.50 | **$2.51** |

### **Best Strategy:**
1. **Development:** Use Hugging Face (embeddings) + Gemini (chat) = **FREE**
2. **When Gemini quota exceeded:** Switch to OpenAI gpt-5-nano = **~$0.03/day**
3. **Production (for quality):** OpenAI gpt-5-mini or gpt-4.1-nano

---

## 📊 System Design Summary

### **Data Flow Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                        USER LAYER                            │
│  Streamlit UI (Browser) - Chat, Upload, Settings            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  - app.py (main chat)                                        │
│  - pages/2_📁_Documents.py (upload)                         │
│  - pages/3_⚙️_Settings.py (config)                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                     BUSINESS LOGIC LAYER                     │
│  - utils/rag_engine.py (RAG processing)                      │
│  - utils/database.py (SQL operations)                        │
│  - utils/storage.py (file operations)                        │
│  - components/auth.py (authentication)                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER (3 DBs)                      │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │   SQLite     │   ChromaDB   │Local Storage │            │
│  │ (Metadata)   │  (Vectors)   │  (Files)     │            │
│  └──────────────┴──────────────┴──────────────┘            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      EXTERNAL APIs                           │
│  - Gemini API (chat + embeddings) [FREE]                    │
│  - OpenAI API (chat + embeddings) [PAID]                    │
│  - Hugging Face (local embeddings) [FREE]                   │
└─────────────────────────────────────────────────────────────┘
```

### **Key Design Decisions:**

1. **3 Separate Databases:**
   - SQLite: Fast structured queries (metadata, history)
   - ChromaDB: Optimized for vector similarity search
   - Local Files: Keep originals for re-processing

2. **Hybrid Memory:**
   - Short-term: Last 5 exchanges (performance)
   - Long-term: All data persistent (completeness)

3. **Provider Flexibility:**
   - Free for dev (Hugging Face + Gemini)
   - Cheap for production (OpenAI nano models)
   - Easy switching via config

4. **Per-User Isolation:**
   - Each user has their own vector store
   - Private conversations
   - Scalable to multi-tenant

---

## 🚀 Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure .env
# Already set up with:
# - Gemini API (free)
# - OpenAI API (cheapest models)
# - Hugging Face (free, local)

# 3. Run application
streamlit run app.py

# 4. Switch providers:
# Edit .env:
#   AI_PROVIDER="gemini" or "openai"
#   EMBEDDING_PROVIDER="huggingface" or "openai"
```

---

## 📚 Further Reading

- **RAG Concepts:** [QUICKSTART.md](QUICKSTART.md)
- **Authentication:** [AUTH_UPGRADE_GUIDE.md](AUTH_UPGRADE_GUIDE.md)
- **API Setup:** [API_SETUP.md](API_SETUP.md)
- **Project Summary:** [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

**Made with ❤️ for beginners learning RAG systems**
