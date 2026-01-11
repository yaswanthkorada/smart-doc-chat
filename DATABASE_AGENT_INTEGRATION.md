# 🗄️ Multi-Agent System Database Integration Guide

## 📚 Complete Guide to How Agents Store & Retrieve Data

---

## 🏗️ Database Architecture Overview

Your project uses **TWO types of databases**:

### **1. PostgreSQL/SQLite (Relational Database)**
**Purpose:** Store structured data

**What it stores:**
- 👤 User accounts (email, password, subscription)
- 💬 Conversations (chat threads)
- 📨 Messages (user questions & agent responses)
- 📄 Document metadata (filename, upload date, size)
- 📊 Analytics (query performance, token usage)

### **2. ChromaDB (Vector Database)**
**Purpose:** Store document embeddings for semantic search

**What it stores:**
- 🔢 Text embeddings (vectors)
- 📝 Document chunks (pieces of text)
- 🏷️ Metadata (source, page number, doc_id)

---

## 🔄 Complete Data Flow with Agents

### **Scenario 1: User Signs Up (User Data)**

```
┌─────────────────────────────────────────────────────────────┐
│ USER ACTION: Signs up with email & password                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ components/auth.py (Authentication Component)               │
│                                                             │
│ def signup(email, username, password):                      │
│     # 1. Validate inputs                                   │
│     if not validate_email(email):                          │
│         return "Invalid email"                             │
│                                                             │
│     # 2. Hash password (security!)                         │
│     password_hash = hash_password(password)                │
│                                                             │
│     # 3. Call database manager                             │
│     user = db_manager.create_user(                         │
│         email=email,                                       │
│         username=username,                                 │
│         password=password_hash                             │
│     )                                                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ utils/database.py (Database Manager)                        │
│                                                             │
│ class DatabaseManager:                                      │
│     def create_user(self, email, username, password_hash): │
│         # Create User object                               │
│         user = User(                                       │
│             id=uuid.uuid4(),                               │
│             email=email,                                   │
│             username=username,                             │
│             password_hash=password_hash,                   │
│             created_at=datetime.utcnow(),                  │
│             subscription_tier='free'                       │
│         )                                                   │
│                                                             │
│         # Save to database                                 │
│         session = self.get_session()                       │
│         session.add(user)                                  │
│         session.commit()                                   │
│                                                             │
│         return user                                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ PostgreSQL Database (Supabase)                              │
│                                                             │
│ TABLE: users                                                │
│ ┌────────────┬─────────────────────────────────────────┐   │
│ │ id         │ 550e8400-e29b-41d4-a716-446655440000    │   │
│ │ email      │ user@example.com                        │   │
│ │ username   │ john_doe                                │   │
│ │ password   │ $2b$12$hashed_password_here            │   │
│ │ created_at │ 2026-01-10 10:30:00                     │   │
│ │ tier       │ free                                    │   │
│ └────────────┴─────────────────────────────────────────┘   │
│                                                             │
│ ✅ User account saved!                                      │
└─────────────────────────────────────────────────────────────┘

❌ NO AGENTS INVOLVED IN USER SIGNUP
   (This is handled by authentication system, not AI agents)
```

---

### **Scenario 2: User Uploads Document (Multi-Agent + Database)**

```
┌─────────────────────────────────────────────────────────────┐
│ USER ACTION: Uploads "research_paper.pdf"                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ pages/2_📁_Documents.py (Upload Handler)                    │
│                                                             │
│ 1. Save file temporarily                                    │
│    temp_path = "temp/research_paper.pdf"                   │
│                                                             │
│ 2. Call Multi-Agent System                                 │
│    result = agent_rag_engine.process_document(             │
│        file_path=temp_path,                                │
│        user_id="user_123",                                 │
│        filename="research_paper.pdf"                       │
│    )                                                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 📄 INGESTION AGENT ACTIVATES                                │
│ (utils/agent_rag_engine.py)                                │
│                                                             │
│ def process_document(file_path, user_id, filename):        │
│     # Agent uses tools to process                          │
│     analysis = DocumentAnalyzerTool.run(file_path)         │
│     text = TextExtractorTool.run(file_path)               │
│     chunks = DocumentChunkerTool.run(text)                │
│                                                             │
│     # Generate doc_id for tracking                         │
│     doc_id = self._generate_doc_id(file_path)             │
│     # doc_id = "doc_a1b2c3d4e5f6"                         │
│                                                             │
│     # NOW AGENT INTERACTS WITH DATABASES!                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
            ▼                       ▼
┌─────────────────────┐   ┌─────────────────────────────────┐
│ DATABASE #1         │   │ DATABASE #2                     │
│ PostgreSQL          │   │ ChromaDB (Vector DB)            │
│ (Metadata)          │   │ (Text Embeddings)               │
└─────────────────────┘   └─────────────────────────────────┘


═══════════════════════════════════════════════════════════════
DATABASE #1: PostgreSQL - Document Metadata
═══════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Agent Creates Document Record                       │
│ (utils/database.py - called by agent)                      │
│                                                             │
│ db_manager.create_document(                                │
│     user_id="user_123",                                    │
│     filename="research_paper.pdf",                         │
│     file_type="pdf",                                       │
│     file_size=2500000,  # 2.5 MB                          │
│     storage_url="supabase://bucket/user_123/file.pdf",    │
│     doc_id="doc_a1b2c3d4e5f6",                            │
│     page_count=50,                                         │
│     vector_count=125  # number of chunks                  │
│ )                                                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ PostgreSQL Database                                         │
│                                                             │
│ TABLE: documents                                            │
│ ┌─────────────┬──────────────────────────────────────────┐ │
│ │ id          │ uuid-xxxx-xxxx                           │ │
│ │ document_id │ doc_a1b2c3d4e5f6                         │ │
│ │ user_id     │ user_123                                 │ │
│ │ filename    │ research_paper.pdf                       │ │
│ │ file_type   │ pdf                                      │ │
│ │ file_size   │ 2500000                                  │ │
│ │ storage_url │ supabase://bucket/user_123/file.pdf      │ │
│ │ uploaded_at │ 2026-01-10 10:35:00                      │ │
│ │ is_indexed  │ true                                     │ │
│ │ page_count  │ 50                                       │ │
│ │ vector_count│ 125                                      │ │
│ └─────────────┴──────────────────────────────────────────┘ │
│                                                             │
│ ✅ Document metadata saved!                                 │
└─────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════
DATABASE #2: ChromaDB - Vector Embeddings
═══════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Agent Stores Vectors in ChromaDB                    │
│ (utils/agent_rag_engine.py)                                │
│                                                             │
│ def _store_in_vectordb(documents, collection_name, doc_id):│
│     # Collection name: user_123_gemini                     │
│     persist_dir = "./data/chroma_data/user_123_gemini/"    │
│                                                             │
│     # Convert text to vectors (embeddings)                 │
│     for chunk in documents:                                │
│         # "Machine learning is..." → [0.23, -0.45, ...]   │
│         vector = embeddings.embed_text(chunk.text)         │
│                                                             │
│         # Store in ChromaDB with metadata                  │
│         vectorstore.add(                                   │
│             text=chunk.text,                               │
│             vector=vector,                                 │
│             metadata={                                     │
│                 "doc_id": "doc_a1b2c3d4e5f6",             │
│                 "filename": "research_paper.pdf",          │
│                 "page": 10,                                │
│                 "chunk_index": 25                          │
│             }                                              │
│         )                                                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ ChromaDB File System Storage                                │
│                                                             │
│ Location: ./data/chroma_data/user_123_gemini/              │
│                                                             │
│ chroma.sqlite3 (internal database file)                    │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ CHUNK #1:                                            │   │
│ │ - text: "Abstract: This paper discusses..."          │   │
│ │ - vector: [0.23, -0.45, 0.67, ..., 0.12] (384 dims) │   │
│ │ - metadata: {doc_id: "doc_a1b2c3d4e5f6", page: 1}   │   │
│ │                                                      │   │
│ │ CHUNK #2:                                            │   │
│ │ - text: "Introduction: Machine learning is..."       │   │
│ │ - vector: [0.15, -0.32, 0.89, ..., 0.45]            │   │
│ │ - metadata: {doc_id: "doc_a1b2c3d4e5f6", page: 2}   │   │
│ │                                                      │   │
│ │ ... (125 chunks total)                               │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                             │
│ ✅ Vectors saved! Ready for semantic search                 │
└─────────────────────────────────────────────────────────────┘

🎉 RESULT: Document is stored in BOTH databases!
   - PostgreSQL has metadata (filename, size, etc.)
   - ChromaDB has actual content as vectors
```

---

### **Scenario 3: User Asks Question (Agents + Databases)**

```
┌─────────────────────────────────────────────────────────────┐
│ USER ACTION: Asks "What are the main findings?"             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ app.py (Main Application)                                   │
│                                                             │
│ 1. Get current conversation_id from session                │
│    conversation_id = st.session_state.conversation_id      │
│    # conversation_id = "conv_xyz789"                       │
│                                                             │
│ 2. FIRST: Save user's message to database                 │
│    db_manager.add_message(                                 │
│        conversation_id="conv_xyz789",                      │
│        role="user",                                        │
│        content="What are the main findings?"               │
│    )                                                        │
│                                                             │
│ 3. THEN: Call Multi-Agent System                          │
│    result = agent_rag_engine.query(                        │
│        question="What are the main findings?",             │
│        user_id="user_123"                                  │
│    )                                                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
            ▼                       ▼


═══════════════════════════════════════════════════════════════
DATABASE INTERACTION #1: Save User Message
═══════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│ utils/database.py                                           │
│                                                             │
│ def add_message(conversation_id, role, content):           │
│     message = Message(                                     │
│         message_id=str(uuid.uuid4()),                      │
│         conversation_id=conversation_id,                   │
│         session_id=current_session_id,                     │
│         role="user",  # or "assistant"                     │
│         content="What are the main findings?",             │
│         timestamp=datetime.utcnow(),                       │
│         tokens_used=0  # calculated later                  │
│     )                                                       │
│     session.add(message)                                   │
│     session.commit()                                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ PostgreSQL Database                                         │
│                                                             │
│ TABLE: messages                                             │
│ ┌───────────────┬─────────────────────────────────────────┐ │
│ │ message_id    │ msg_abc123                              │ │
│ │ conversation  │ conv_xyz789                             │ │
│ │ session_id    │ session_456                             │ │
│ │ role          │ user                                    │ │
│ │ content       │ What are the main findings?             │ │
│ │ timestamp     │ 2026-01-10 10:40:00                     │ │
│ │ tokens_used   │ 0                                       │ │
│ │ sources       │ NULL (user messages don't have sources) │ │
│ └───────────────┴─────────────────────────────────────────┘ │
│                                                             │
│ ✅ User message saved!                                      │
└─────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════
AGENT PROCESSING: Retrieval Agent Searches Database
═══════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│ 🔍 RETRIEVAL AGENT ACTIVATES                                │
│                                                             │
│ Agent receives: "What are the main findings?"               │
│                                                             │
│ Agent uses: VectorSearchTool                               │
│                                                             │
│ VectorSearchTool.run(                                       │
│     query="What are the main findings?",                   │
│     collection_name="user_123_gemini",                     │
│     n_results=5                                            │
│ )                                                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ VectorSearchTool Accesses ChromaDB                          │
│ (utils/agent_tools.py)                                     │
│                                                             │
│ def _run(query, collection_name, n_results):               │
│     # 1. Convert query to vector                          │
│     query_vector = embeddings.embed(query)                 │
│     # "What are the main findings?"                        │
│     # → [0.12, -0.34, 0.56, ..., 0.78]                    │
│                                                             │
│     # 2. Load ChromaDB collection                          │
│     vectorstore = Chroma(                                  │
│         persist_directory="./data/chroma_data/user_123_gemini/"│
│     )                                                       │
│                                                             │
│     # 3. Search for similar vectors                        │
│     results = vectorstore.similarity_search(               │
│         query_vector,                                      │
│         k=5                                                │
│     )                                                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ ChromaDB Returns Similar Chunks                             │
│                                                             │
│ Results:                                                    │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ CHUNK 1 (Score: 0.91):                               │   │
│ │ "The main finding was a 95% accuracy rate..."        │   │
│ │ Metadata: {doc_id: "doc_a1b2c3d4e5f6", page: 8}     │   │
│ │                                                      │   │
│ │ CHUNK 2 (Score: 0.88):                               │   │
│ │ "Results showed significant improvement..."          │   │
│ │ Metadata: {doc_id: "doc_a1b2c3d4e5f6", page: 15}    │   │
│ │                                                      │   │
│ │ CHUNK 3 (Score: 0.85):                               │   │
│ │ "We concluded that the method is effective..."       │   │
│ │ Metadata: {doc_id: "doc_a1b2c3d4e5f6", page: 17}    │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                             │
│ ✅ Relevant chunks retrieved from vector database!          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ Retrieval Agent passes results to Generation Agent         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ ✍️ GENERATION AGENT ACTIVATES                               │
│                                                             │
│ Agent receives:                                             │
│ - Original question                                         │
│ - 3 relevant chunks from database                          │
│                                                             │
│ Agent creates response:                                     │
│ "Based on the research paper, the main findings are:       │
│  1. The method achieved 95% accuracy (Page 8)              │
│  2. Results showed significant improvement (Page 15)       │
│  3. The method proved effective (Page 17)"                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼


═══════════════════════════════════════════════════════════════
DATABASE INTERACTION #2: Save Agent Response
═══════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│ app.py (Save agent's response)                              │
│                                                             │
│ db_manager.add_message(                                     │
│     conversation_id="conv_xyz789",                          │
│     role="assistant",                                       │
│     content="Based on the research paper...",               │
│     sources=json.dumps([                                    │
│         {"filename": "research_paper.pdf", "page": 8},      │
│         {"filename": "research_paper.pdf", "page": 15},     │
│         {"filename": "research_paper.pdf", "page": 17}      │
│     ]),                                                     │
│     tokens_used=450                                         │
│ )                                                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ PostgreSQL Database                                         │
│                                                             │
│ TABLE: messages (NEW ROW)                                   │
│ ┌───────────────┬─────────────────────────────────────────┐ │
│ │ message_id    │ msg_def456                              │ │
│ │ conversation  │ conv_xyz789                             │ │
│ │ session_id    │ session_456                             │ │
│ │ role          │ assistant                               │ │
│ │ content       │ Based on the research paper, the main...│ │
│ │ timestamp     │ 2026-01-10 10:40:03                     │ │
│ │ tokens_used   │ 450                                     │ │
│ │ sources       │ [{"filename":"research_paper.pdf",...}] │ │
│ └───────────────┴─────────────────────────────────────────┘ │
│                                                             │
│ ✅ Agent response saved!                                    │
│                                                             │
│ NOW: conversation has 2 messages (user + assistant)         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Database Schema Reference

### **PostgreSQL Tables Used by Agents**

```sql
-- 1. USERS TABLE (Authentication)
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    subscription_tier VARCHAR(50) DEFAULT 'free'
);

-- 2. CONVERSATIONS TABLE (Chat Threads)
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    conversation_id VARCHAR(36) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
    title VARCHAR(200) DEFAULT 'New Conversation',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    is_pinned BOOLEAN DEFAULT FALSE
);

-- 3. MESSAGES TABLE (User + Agent Messages)
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    message_id VARCHAR(36) UNIQUE NOT NULL,
    conversation_id VARCHAR(36) REFERENCES conversations(conversation_id),
    session_id VARCHAR(36) REFERENCES chat_sessions(session_id),
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    tokens_used INTEGER DEFAULT 0,
    sources TEXT,  -- JSON string with source metadata
    feedback VARCHAR(20)  -- 'helpful' or 'not_helpful'
);

-- 4. DOCUMENTS TABLE (File Metadata)
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    document_id VARCHAR(36) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT,
    storage_url TEXT,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    is_indexed BOOLEAN DEFAULT FALSE,
    page_count INTEGER,
    vector_count INTEGER  -- Number of chunks/embeddings
);

-- 5. ANALYTICS TABLE (Usage Tracking)
CREATE TABLE analytics (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    conversation_id VARCHAR(36),
    query_text TEXT,
    response_time FLOAT,
    tokens_used INTEGER,
    documents_searched TEXT[],
    ai_provider VARCHAR(50),
    timestamp TIMESTAMP DEFAULT NOW(),
    success BOOLEAN DEFAULT TRUE
);
```

---

## 🔍 How Agents Access Databases

### **Code Flow: Agent → Database Manager → Database**

```python
# ============================================================
# EXAMPLE 1: Ingestion Agent Saves Document Metadata
# ============================================================

# File: utils/agent_rag_engine.py (Ingestion Agent)
class MultiAgentRAGEngine:
    def process_document(self, file_path, user_id, filename):
        # Agent processes document with tools
        chunks = self._extract_and_chunk(file_path, filename)
        doc_id = self._generate_doc_id(file_path)
        
        # ✅ AGENT CALLS DATABASE MANAGER
        from utils.database import db_manager
        
        db_manager.create_document(
            user_id=user_id,
            filename=filename,
            file_type="pdf",
            storage_url="path/to/file",
            doc_id=doc_id,
            vector_count=len(chunks)
        )
        
        # Agent also stores in vector database
        self._store_in_vectordb(chunks, collection_name, doc_id)

# ============================================================
# DATABASE MANAGER LAYER
# ============================================================

# File: utils/database.py
class DatabaseManager:
    def create_document(self, user_id, filename, file_type, 
                       storage_url, doc_id, vector_count):
        """Database manager handles actual SQL operations"""
        
        # Create document object
        document = Document(
            id=uuid.uuid4(),
            document_id=doc_id,
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            storage_url=storage_url,
            uploaded_at=datetime.utcnow(),
            is_indexed=True,
            vector_count=vector_count
        )
        
        # Save to PostgreSQL using SQLAlchemy
        session = self.get_session()
        session.add(document)
        session.commit()
        
        return document


# ============================================================
# EXAMPLE 2: Retrieval Agent Gets Document List
# ============================================================

# Retrieval Agent needs to know what documents user has
def query(self, question, user_id):
    # ✅ AGENT ASKS DATABASE MANAGER FOR USER'S DOCUMENTS
    from utils.database import db_manager
    
    user_documents = db_manager.get_user_documents(user_id)
    # Returns: [
    #   {id: "doc_123", filename: "paper1.pdf"},
    #   {id: "doc_456", filename: "paper2.pdf"}
    # ]
    
    # Agent uses this info to search correct collections
    collection_name = f"user_{user_id}_gemini"
    
    # Search in vector database
    results = VectorSearchTool().run(
        query=question,
        collection_name=collection_name
    )


# ============================================================
# EXAMPLE 3: Generation Agent Saves Message
# ============================================================

# File: app.py (After agent generates response)
def handle_user_input(user_input):
    # Get response from agents
    result = agent_rag_engine.query(
        question=user_input,
        user_id=st.session_state.user_id
    )
    
    # ✅ SAVE AGENT'S RESPONSE TO DATABASE
    from utils.database import db_manager
    
    db_manager.add_message(
        conversation_id=current_conversation_id,
        session_id=current_session_id,
        role="assistant",  # Agent's response
        content=result['response'],
        sources=json.dumps(result['sources']),
        tokens_used=result.get('tokens', 0)
    )
```

---

## 🔄 Complete Multi-Agent Database Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER SIGNS UP                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
                   ┌──────────────┐
                   │ PostgreSQL   │
                   │ users table  │
                   └──────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     USER LOGS IN                                │
│         (Session created, conversation initialized)             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
                   ┌──────────────┐
                   │ PostgreSQL   │
                   │ conversations│
                   │ table        │
                   └──────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  USER UPLOADS DOCUMENT                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
    ┌──────────────┐          ┌──────────────┐
    │ 📄 INGESTION │          │ PostgreSQL   │
    │    AGENT     │────────→ │ documents    │
    │              │   (1)    │ table        │
    └──────┬───────┘          └──────────────┘
           │                         
           │ (2)                     
           ▼                         
    ┌──────────────┐                
    │  ChromaDB    │                
    │  Vectors     │                
    └──────────────┘                
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   USER ASKS QUESTION                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ├──► PostgreSQL (save user message)
                         │
                         ▼
                   ┌──────────────┐
                   │ 🔍 RETRIEVAL │
                   │    AGENT     │
                   └──────┬───────┘
                          │
                          ├──► ChromaDB (search vectors)
                          │
                          ▼
                   ┌──────────────┐
                   │ ✍️ GENERATION│
                   │    AGENT     │
                   └──────┬───────┘
                          │
                          ├──► PostgreSQL (save agent response)
                          │
                          ▼
                   ┌──────────────┐
                   │ PostgreSQL   │
                   │ messages     │
                   │ table        │
                   └──────────────┘
                          │
                          ├──► PostgreSQL (save analytics)
                          │
                          ▼
                   ┌──────────────┐
                   │ PostgreSQL   │
                   │ analytics    │
                   │ table        │
                   └──────────────┘
```

---

## 💾 Storage Locations

### **PostgreSQL/Supabase (Cloud)**
```
Database: Hosted on Supabase servers
Connection: Via DATABASE_URL in .env
Access: Through db_manager (SQLAlchemy)

Tables:
- users
- conversations
- messages
- documents
- analytics
```

### **ChromaDB (Local Files)**
```
Location: ./data/chroma_data/

Structure:
data/
└── chroma_data/
    ├── user_1_gemini/
    │   └── chroma.sqlite3     (vector database file)
    ├── user_1_openai/
    │   └── chroma.sqlite3
    └── user_2_gemini/
        └── chroma.sqlite3

Each user has separate collections for:
- Different AI providers (gemini vs openai)
- Different embedding models
```

---

## 🔐 Data Security

### **How Agents Ensure Data Security**

```python
# 1. USER ISOLATION
# Each user's data is completely separate
collection_name = f"user_{user_id}_gemini"
# User 1: user_1_gemini
# User 2: user_2_gemini
# ✅ Users can't access each other's data

# 2. DATABASE LEVEL SECURITY (Row Level Security in Supabase)
# PostgreSQL policies ensure:
db_manager.get_user_documents(user_id)
# Only returns documents where document.user_id == user_id

# 3. PASSWORD SECURITY
# Passwords are hashed with bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
# Original password is NEVER stored

# 4. SESSION MANAGEMENT
# User sessions are tracked
if not st.session_state.get('authenticated'):
    redirect_to_login()
```

---

## 📈 Analytics Tracking

### **How System Tracks Usage**

```python
# After each query, system logs analytics
db_manager.log_query_analytics(
    user_id=user_id,
    conversation_id=conversation_id,
    query_text="What are the main findings?",
    response_time=2300,  # milliseconds
    tokens_used=450,
    documents_searched=["doc_123", "doc_456"],
    ai_provider="gemini",
    success=True
)

# This data is used for:
# - Performance monitoring
# - Cost calculation
# - Usage statistics
# - Error tracking
```

---

## 🎯 Key Takeaways

### **1. Agents DON'T Directly Access Databases**

```
❌ BAD: Agent → SQL Query → Database
✅ GOOD: Agent → Database Manager → Database

Agents use db_manager as an abstraction layer
```

### **2. Two Database Types Work Together**

```
PostgreSQL: Structured data (user, messages, metadata)
    ↕️
ChromaDB: Unstructured data (text embeddings for search)

Both are needed for complete functionality
```

### **3. Every Message is Saved**

```
User message → PostgreSQL
Agent response → PostgreSQL
Conversation history → Easily retrievable
```

### **4. Document Storage is Hybrid**

```
File metadata → PostgreSQL (filename, size, date)
File content vectors → ChromaDB (for searching)
Actual file → Supabase Storage (binary file)
```

---

## 📚 Complete Data Flow Summary

```
USER SIGNUP
    ↓
PostgreSQL (users table)
    ↓
USER UPLOADS DOC
    ↓
Ingestion Agent processes
    ↓
    ├→ PostgreSQL (documents table) - metadata
    └→ ChromaDB - text embeddings
    ↓
USER ASKS QUESTION
    ↓
PostgreSQL (messages table) - save user message
    ↓
Retrieval Agent searches
    ↓
ChromaDB - find relevant chunks
    ↓
Generation Agent creates response
    ↓
PostgreSQL (messages table) - save agent response
    ↓
PostgreSQL (analytics table) - log metrics
    ↓
USER SEES RESPONSE with sources!
```

---

## 🎉 Conclusion

**Your multi-agent system uses databases intelligently:**

✅ **PostgreSQL** - All structured data (users, messages, metadata)  
✅ **ChromaDB** - Vector embeddings for semantic search  
✅ **Database Manager** - Abstraction layer for clean code  
✅ **Agents** - Don't directly touch databases (good design!)  
✅ **Security** - User isolation, hashed passwords, RLS policies  
✅ **Analytics** - Every query tracked for monitoring  

**The agents focus on AI tasks while the database manager handles all data persistence!** 🎯

---

## 🔍 Want to See the Code?

**Check these files:**
- `utils/database.py` - Database manager & models
- `utils/agent_rag_engine.py` - How agents call database
- `app.py` - Message saving flow
- `pages/2_📁_Documents.py` - Document upload flow

**Everything is connected and working together!** 🚀
