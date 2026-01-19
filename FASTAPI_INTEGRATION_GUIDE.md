# 🚀 FastAPI Backend Integration Guide

## Complete REST API for Smart Document Chat with Multi-Agent System

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [API Endpoints](#api-endpoints)
3. [Frontend Integration](#frontend-integration)
4. [Running the API](#running-the-api)
5. [Authentication Flow](#authentication-flow)
6. [Example Code](#example-code)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND                                │
│         (React / Vue / Angular / Streamlit)                  │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/HTTPS
                        │ REST API Calls
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND                            │
│                   (api/main.py)                              │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Auth Router  │  │ Docs Router  │  │ Chat Router  │     │
│  │ /api/auth    │  │ /api/docs    │  │ /api/chat    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                            ▼                                 │
│                 ┌─────────────────────┐                     │
│                 │  Business Logic     │                     │
│                 │  (utils/)           │                     │
│                 └──────────┬──────────┘                     │
└────────────────────────────┼─────────────────────────────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Multi-Agent  │ │ PostgreSQL   │ │  ChromaDB    │
    │   System     │ │  Database    │ │  Vectors     │
    │ (3 Agents)   │ │  (Supabase)  │ │  (Local)     │
    └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 📡 API Endpoints

### **Base URL:** `http://localhost:8000`

### **🔐 Authentication Endpoints**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/signup` | Create new user account | ❌ |
| POST | `/api/auth/login` | Login with email/password | ❌ |
| POST | `/api/auth/logout` | Logout current user | ✅ |
| GET | `/api/auth/verify` | Verify JWT token | ✅ |
| GET | `/api/auth/me` | Get current user profile | ✅ |

### **👤 User Management Endpoints**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/users/profile` | Get user profile | ✅ |
| PATCH | `/api/users/profile` | Update profile | ✅ |
| POST | `/api/users/change-password` | Change password | ✅ |
| DELETE | `/api/users/account` | Delete account | ✅ |
| GET | `/api/users/stats` | Get usage statistics | ✅ |

### **📄 Document Management Endpoints**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/documents/upload` | Upload document | ✅ |
| GET | `/api/documents/list` | List all documents | ✅ |
| GET | `/api/documents/{id}` | Get document details | ✅ |
| DELETE | `/api/documents/{id}` | Delete document | ✅ |
| DELETE | `/api/documents/all` | Delete all documents | ✅ |

### **💬 Chat & Conversation Endpoints**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/chat/query` | Ask question (Multi-Agent) | ✅ |
| GET | `/api/chat/conversations` | List all conversations | ✅ |
| POST | `/api/chat/conversations` | Create new conversation | ✅ |
| GET | `/api/chat/conversations/{id}` | Get conversation + messages | ✅ |
| PATCH | `/api/chat/conversations/{id}` | Update conversation | ✅ |
| DELETE | `/api/chat/conversations/{id}` | Delete conversation | ✅ |
| DELETE | `/api/chat/conversations` | Delete all conversations | ✅ |

### **⚙️ Settings Endpoints**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/settings/ai` | Get AI provider settings | ✅ |
| PATCH | `/api/settings/ai` | Update AI provider | ✅ |
| GET | `/api/settings/system` | Get system settings | ✅ |
| PATCH | `/api/settings/system` | Update system settings | ✅ |
| GET | `/api/settings/agents` | Get agent status | ✅ |

---

## 🔌 Frontend Integration

### **Installation**

```bash
# Install FastAPI dependencies
pip install -r requirements.txt
```

### **Environment Variables**

Create `.env` file:

```env
# Database
DATABASE_URL=your_supabase_database_url

# JWT Secret
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# AI Provider Keys
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
```

---

## 🎯 Running the API

### **Option 1: Direct Run**

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run FastAPI server
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### **Option 2: Using Python**

```bash
# Run from api/main.py
cd api
python main.py
```

### **Option 3: Production with Gunicorn**

```bash
gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### **Access Documentation**

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health

---

## 🔐 Authentication Flow

### **1. Signup**

```javascript
// POST /api/auth/signup
const response = await fetch('http://localhost:8000/api/auth/signup', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'user@example.com',
    username: 'john_doe',
    password: 'secure_password123',
    full_name: 'John Doe'
  })
});

const user = await response.json();
// Response: { id, email, username, subscription_tier, created_at }
```

### **2. Login**

```javascript
// POST /api/auth/login
const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'secure_password123'
  })
});

const data = await response.json();
// Response: { access_token, token_type: "bearer", expires_in: 86400 }

// Store token in localStorage or sessionStorage
localStorage.setItem('access_token', data.access_token);
```

### **3. Authenticated Requests**

```javascript
// All protected endpoints require Authorization header
const token = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8000/api/users/profile', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const profile = await response.json();
```

---

## 💻 Frontend Integration Examples

### **React Example**

```javascript
// src/api/client.js
const API_BASE_URL = 'http://localhost:8000';

// API Client with authentication
class APIClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  getToken() {
    return localStorage.getItem('access_token');
  }

  async request(endpoint, options = {}) {
    const token = this.getToken();
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  // Auth methods
  async signup(email, username, password, fullName) {
    return this.request('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, username, password, full_name: fullName })
    });
  }

  async login(email, password) {
    const data = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    localStorage.setItem('access_token', data.access_token);
    return data;
  }

  async logout() {
    await this.request('/api/auth/logout', { method: 'POST' });
    localStorage.removeItem('access_token');
  }

  // Document methods
  async uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);

    const token = this.getToken();
    const response = await fetch(`${this.baseURL}/api/documents/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    return response.json();
  }

  async listDocuments() {
    return this.request('/api/documents/list');
  }

  async deleteDocument(documentId) {
    return this.request(`/api/documents/${documentId}`, {
      method: 'DELETE'
    });
  }

  // Chat methods
  async query(question, conversationId = null) {
    return this.request('/api/chat/query', {
      method: 'POST',
      body: JSON.stringify({ 
        question, 
        conversation_id: conversationId,
        stream: false
      })
    });
  }

  async listConversations() {
    return this.request('/api/chat/conversations');
  }

  async getConversation(conversationId) {
    return this.request(`/api/chat/conversations/${conversationId}`);
  }

  // Settings methods
  async updateAIProvider(provider) {
    return this.request('/api/settings/ai', {
      method: 'PATCH',
      body: JSON.stringify({ ai_provider: provider })
    });
  }

  async getAgentStatus() {
    return this.request('/api/settings/agents');
  }

  // User methods
  async getProfile() {
    return this.request('/api/users/profile');
  }

  async getStats() {
    return this.request('/api/users/stats');
  }
}

export const apiClient = new APIClient();
```

### **React Component Example**

```javascript
// src/components/ChatInterface.jsx
import React, { useState } from 'react';
import { apiClient } from '../api/client';

function ChatInterface() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!question.trim()) return;

    setLoading(true);
    try {
      const result = await apiClient.query(question);
      setResponse(result);
      setQuestion('');
    } catch (error) {
      console.error('Query failed:', error);
      alert('Failed to get response: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      <h2>Ask a Question</h2>
      
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask something about your documents..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Ask'}
        </button>
      </form>

      {response && (
        <div className="response">
          <h3>Response:</h3>
          <p>{response.response}</p>
          
          <h4>Sources:</h4>
          <ul>
            {response.sources.map((source, idx) => (
              <li key={idx}>
                {source.filename} (Page {source.page || 'N/A'})
              </li>
            ))}
          </ul>
          
          <div className="metadata">
            <span>Tokens: {response.tokens_used}</span>
            <span>Time: {response.response_time?.toFixed(2)}s</span>
            <span>Agents: {response.agents_used.join(', ')}</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatInterface;
```

### **React Document Upload Component**

```javascript
// src/components/DocumentUpload.jsx
import React, { useState } from 'react';
import { apiClient } from '../api/client';

function DocumentUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    try {
      const result = await apiClient.uploadDocument(file);
      alert(`Document uploaded successfully! ${result.vector_count} chunks indexed.`);
      setFile(null);
      if (onUploadSuccess) onUploadSuccess();
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="document-upload">
      <h3>Upload Document</h3>
      <input
        type="file"
        onChange={handleFileChange}
        accept=".pdf,.docx,.pptx,.xlsx,.csv,.txt"
        disabled={uploading}
      />
      <button onClick={handleUpload} disabled={!file || uploading}>
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
    </div>
  );
}

export default DocumentUpload;
```

---

## 🐍 Python Client Example

```python
# api_client.py
import requests
from typing import Optional, Dict, Any

class SmartDocChatClient:
    """Python client for Smart Document Chat API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
    
    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def signup(self, email: str, username: str, password: str, full_name: str = None) -> Dict:
        """Create new user account"""
        response = requests.post(
            f"{self.base_url}/api/auth/signup",
            json={
                "email": email,
                "username": username,
                "password": password,
                "full_name": full_name
            }
        )
        response.raise_for_status()
        return response.json()
    
    def login(self, email: str, password: str) -> Dict:
        """Login and get access token"""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["access_token"]
        return data
    
    def upload_document(self, file_path: str) -> Dict:
        """Upload document for processing"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.base_url}/api/documents/upload",
                headers={"Authorization": f"Bearer {self.token}"},
                files=files
            )
        response.raise_for_status()
        return response.json()
    
    def query(self, question: str, conversation_id: Optional[str] = None) -> Dict:
        """Ask question to Multi-Agent system"""
        response = requests.post(
            f"{self.base_url}/api/chat/query",
            headers=self._headers(),
            json={
                "question": question,
                "conversation_id": conversation_id,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()
    
    def list_documents(self) -> Dict:
        """Get list of all documents"""
        response = requests.get(
            f"{self.base_url}/api/documents/list",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        response = requests.get(
            f"{self.base_url}/api/users/stats",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()


# Usage Example
if __name__ == "__main__":
    client = SmartDocChatClient()
    
    # Login
    client.login("user@example.com", "password123")
    
    # Upload document
    result = client.upload_document("research_paper.pdf")
    print(f"Document uploaded: {result['document_id']}")
    
    # Ask question
    response = client.query("What are the main findings?")
    print(f"Answer: {response['response']}")
    print(f"Sources: {response['sources']}")
    
    # Get stats
    stats = client.get_stats()
    print(f"Total documents: {stats['total_documents']}")
```

---

## 🔄 CORS Configuration

The API is configured to accept requests from:
- http://localhost:3000 (React)
- http://localhost:5173 (Vite)
- http://localhost:8501 (Streamlit)

To add more origins, edit `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://your-production-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

---

## 📊 Response Format

All API responses follow consistent format:

### **Success Response**

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### **Error Response**

```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Invalid request parameters",
  "details": { ... }
}
```

### **Chat Query Response**

```json
{
  "success": true,
  "response": "Based on the document, the main findings are...",
  "sources": [
    {
      "filename": "research_paper.pdf",
      "page": 10,
      "chunk_index": 5,
      "relevance_score": 0.92
    }
  ],
  "conversation_id": "conv_xyz789",
  "message_id": "msg_abc123",
  "tokens_used": 450,
  "response_time": 2.3,
  "agents_used": ["Retrieval Agent", "Generation Agent"]
}
```

---

## 🚀 Deployment

### **Docker Deployment**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Environment Variables for Production**

```env
# Production settings
JWT_SECRET_KEY=your-super-secure-production-key-change-me
DATABASE_URL=postgresql://user:pass@host:5432/dbname
ENVIRONMENT=production
DEBUG=false

# AI Provider Keys
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

---

## 📝 Testing the API

### **Using cURL**

```bash
# Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Query (with token)
curl -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"question":"What are the main findings?"}'
```

### **Using Postman**

1. Import the API collection from `/api/docs`
2. Set base URL: `http://localhost:8000`
3. Add Authorization header: `Bearer YOUR_TOKEN`

---

## ✅ Complete Integration Checklist

- [x] FastAPI backend created
- [x] JWT authentication implemented
- [x] Multi-agent system integrated
- [x] Document upload/management endpoints
- [x] Chat query endpoints
- [x] User management endpoints
- [x] Settings endpoints
- [x] CORS configured
- [x] Error handling
- [x] API documentation (Swagger/ReDoc)
- [x] Frontend integration examples
- [x] Python client library

---

## 🎉 Summary

Your FastAPI backend is now ready! You have:

✅ **Complete REST API** with 30+ endpoints  
✅ **JWT Authentication** for secure access  
✅ **Multi-Agent System** integrated (Ingestion, Retrieval, Generation)  
✅ **Document Processing** via agents  
✅ **Conversational AI** with source citations  
✅ **Database Integration** (PostgreSQL + ChromaDB)  
✅ **Frontend-Ready** (React, Vue, Angular compatible)  
✅ **Auto-Generated Docs** at `/api/docs`  

**Start the server and build your frontend!** 🚀
