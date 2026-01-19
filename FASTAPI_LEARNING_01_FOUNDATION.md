# FastAPI Learning Guide - Part 1: Foundation & Basics

## 🎯 Learning Objectives
After this guide, you'll understand:
- How FastAPI applications are structured
- Routing and path operations
- App initialization and configuration
- Lifespan events (startup/shutdown)
- API documentation (auto-generated)

---

## 📚 1. What is FastAPI?

FastAPI is a modern, fast (high-performance) web framework for building APIs with Python based on standard Python type hints.

### Key Features:
- **Fast**: Very high performance, on par with NodeJS and Go
- **Fast to code**: Increase development speed by about 200-300%
- **Less bugs**: Reduce human errors by about 40%
- **Intuitive**: Great editor support with auto-completion
- **Easy**: Designed to be easy to learn and use
- **Standards-based**: Based on OpenAPI and JSON Schema

---

## 🏗️ 2. Basic App Structure

### Example from Your Project: [api/main.py](api/main.py#L1-L50)

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    print("🚀 Starting FastAPI Server...")
    print("🤖 Multi-Agent RAG System Ready")
    
    yield  # App runs here
    
    # Shutdown
    print("🛑 Shutting down FastAPI Server...")

# Initialize FastAPI app
app = FastAPI(
    title="Smart Document Chat API",
    description="Multi-Agent RAG System with Document Processing",
    version="2.0.0",
    docs_url="/api/docs",    # Swagger UI
    redoc_url="/api/redoc",  # ReDoc UI
    lifespan=lifespan
)
```

### 🔍 Why This Structure?

1. **`lifespan` parameter**: Modern way to handle startup/shutdown events
   - Replaces old `@app.on_event("startup")` decorators
   - Uses Python's async context manager pattern
   - Guarantees cleanup code runs

2. **`docs_url` and `redoc_url`**: Automatic interactive documentation
   - FastAPI generates OpenAPI schema automatically
   - Swagger UI at `/api/docs` (interactive testing)
   - ReDoc at `/api/redoc` (beautiful documentation)

3. **Metadata**: Helps with documentation and client generation
   - `title`: Shows in API docs
   - `description`: Explains what your API does
   - `version`: For API versioning

---

## 🛣️ 3. Routing Basics

### Simple Route Example

```python
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Smart Document Chat API",
        "version": "2.0.0",
        "status": "running"
    }
```

### 🔍 Breaking it down:

1. **`@app.get("/")`**: Decorator that registers route
   - `get`: HTTP method (GET, POST, PUT, DELETE, PATCH)
   - `"/"`: URL path
   
2. **`async def`**: Asynchronous function
   - Can use `await` inside
   - More efficient for I/O operations
   
3. **Return value**: Automatically converted to JSON
   - Dict → JSON object
   - List → JSON array
   - Pydantic model → JSON with validation

---

## 🎭 4. HTTP Methods

### Your Project Uses All CRUD Operations:

```python
# READ - Get data
@app.get("/api/documents/list")
async def list_documents():
    """Get all documents"""
    pass

# CREATE - Add new data
@app.post("/api/documents/upload")
async def upload_document():
    """Upload new document"""
    pass

# UPDATE - Modify existing data
@app.patch("/api/conversations/{conversation_id}")
async def update_conversation(conversation_id: str):
    """Update conversation title"""
    pass

# DELETE - Remove data
@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete document"""
    pass
```

### When to Use Each Method:

| Method | Purpose | Idempotent? | Has Body? |
|--------|---------|-------------|-----------|
| GET | Retrieve data | ✅ Yes | ❌ No |
| POST | Create new resource | ❌ No | ✅ Yes |
| PUT | Replace entire resource | ✅ Yes | ✅ Yes |
| PATCH | Partial update | ❌ Usually No | ✅ Yes |
| DELETE | Remove resource | ✅ Yes | ❌ Usually No |

**Idempotent**: Making the same request multiple times has the same effect as making it once

---

## 📁 5. Router Organization

### Why Use APIRouter?

Your project splits endpoints into separate files using `APIRouter`:

```python
# api/routers/auth.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/signup")
async def signup(user_data: UserSignup):
    """User registration"""
    pass

@router.post("/login")
async def login(credentials: UserLogin):
    """User login"""
    pass
```

### Including Routers in Main App:

```python
# api/main.py
from api.routers import auth, documents, chat

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
```

### 🔍 Why This Pattern?

1. **Separation of Concerns**: Each router handles one domain
2. **Code Organization**: Easier to find and maintain code
3. **Team Collaboration**: Different people can work on different routers
4. **Reusability**: Can reuse routers in different projects
5. **Automatic Grouping**: `tags` parameter groups endpoints in docs

---

## 🌐 6. Path Parameters

### Example from Your Project: [api/routers/chat.py](api/routers/chat.py#L280-L305)

```python
@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation by ID"""
    # conversation_id is extracted from URL
    conversation = db_manager.get_conversation(conversation_id, user_id)
    return conversation
```

### URL: `/api/chat/conversations/abc-123-xyz`
- `conversation_id` = `"abc-123-xyz"`

### Type Validation:

```python
# String parameter (any text)
@router.get("/items/{item_id}")
async def get_item(item_id: str):
    pass

# Integer parameter (automatic validation!)
@router.get("/items/{item_id}")
async def get_item(item_id: int):
    # If URL is /items/abc → FastAPI returns 422 error automatically
    # If URL is /items/123 → item_id = 123 (converted to int)
    pass

# Enum parameter (limited choices)
from enum import Enum

class ModelName(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"

@router.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    # Only accepts "openai" or "gemini"
    # Returns 422 for invalid values
    pass
```

---

## 🔍 7. Query Parameters

### Example: Filtering and Pagination

```python
@router.get("/documents/search")
async def search_documents(
    query: str,                    # Required: ?query=machine+learning
    page: int = 1,                 # Optional with default: ?page=2
    limit: int = 10,               # Optional with default: ?limit=20
    sort_by: Optional[str] = None  # Optional can be None: ?sort_by=date
):
    """
    Search documents
    
    URL examples:
    - /documents/search?query=AI
    - /documents/search?query=AI&page=2
    - /documents/search?query=AI&page=2&limit=20&sort_by=date
    """
    offset = (page - 1) * limit
    # Use query, offset, limit, sort_by
    pass
```

### 🔍 Query Parameter Rules:

1. **Required**: No default value → Must be in URL
2. **Optional with default**: Has `= value` → Can omit from URL
3. **Optional nullable**: `Optional[type] = None` → Can be None

---

## 📊 8. Response Models

### Your Project Example: [api/routers/chat.py](api/routers/chat.py#L56-L73)

```python
@router.post("/query", response_model=ChatResponse)
async def query_documents(query: ChatQuery):
    """Query documents"""
    result = agent_rag_engine.query(question=query.question)
    
    return ChatResponse(
        success=True,
        response=result['response'],
        sources=format_sources(result['sources']),
        conversation_id=conversation_id,
        message_id=message_id,
        tokens_used=tokens_used,
        response_time=response_time
    )
```

### 🔍 Why Use `response_model`?

1. **Output Validation**: Ensures response matches schema
2. **Documentation**: Shows response structure in API docs
3. **Serialization**: Converts data to JSON automatically
4. **Security**: Hides sensitive fields not in model

---

## 🎯 9. Status Codes

### Example from Your Project: [api/routers/auth.py](api/routers/auth.py#L113-L115)

```python
@router.post("/signup", 
             response_model=UserProfile, 
             status_code=status.HTTP_201_CREATED)  # Returns 201 instead of 200
async def signup(user_data: UserSignup):
    pass
```

### Common Status Codes:

```python
from fastapi import status

# Success codes
status.HTTP_200_OK                # Default for successful GET/PUT/PATCH
status.HTTP_201_CREATED           # Successful POST (resource created)
status.HTTP_204_NO_CONTENT        # Successful DELETE (no content returned)

# Client error codes
status.HTTP_400_BAD_REQUEST       # Invalid request data
status.HTTP_401_UNAUTHORIZED      # Not authenticated
status.HTTP_403_FORBIDDEN         # Authenticated but no permission
status.HTTP_404_NOT_FOUND         # Resource doesn't exist
status.HTTP_422_UNPROCESSABLE_ENTITY  # Validation failed

# Server error codes
status.HTTP_500_INTERNAL_SERVER_ERROR  # Server error
```

---

## 🧪 10. Practical Exercise

### Create a Simple Todo API:

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Todo API")

# In-memory storage
todos = []

# Models
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class Todo(TodoCreate):
    id: int

# Endpoints
@app.get("/todos", response_model=List[Todo])
async def list_todos():
    """Get all todos"""
    return todos

@app.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate):
    """Create new todo"""
    new_todo = Todo(id=len(todos) + 1, **todo.dict())
    todos.append(new_todo)
    return new_todo

@app.get("/todos/{todo_id}", response_model=Todo)
async def get_todo(todo_id: int):
    """Get todo by ID"""
    for todo in todos:
        if todo.id == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int):
    """Delete todo"""
    for i, todo in enumerate(todos):
        if todo.id == todo_id:
            todos.pop(i)
            return
    raise HTTPException(status_code=404, detail="Todo not found")

# Run with: uvicorn filename:app --reload
```

---

## 🎓 Key Takeaways

1. **FastAPI = Function + Decorator**: Each endpoint is just a function with a decorator
2. **Type Hints Are Magic**: FastAPI uses them for validation, docs, and serialization
3. **Automatic Documentation**: Swagger UI and ReDoc generated for free
4. **Router Organization**: Split large APIs into multiple files with APIRouter
5. **Status Codes Matter**: Use correct HTTP status codes for semantic clarity

---

## 📖 What's Next?

In **Part 2: Pydantic Models**, you'll learn:
- Request/response validation
- Custom validators
- Enums and field constraints
- Nested models
- Real examples from your authentication system

---

## 🔗 Official Resources

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [FastAPI Advanced Guide](https://fastapi.tiangolo.com/advanced/)
- [OpenAPI Specification](https://swagger.io/specification/)
