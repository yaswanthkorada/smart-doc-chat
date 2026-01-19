# FastAPI Learning Guide - Part 5: Advanced Patterns

## 🎯 Learning Objectives
After this guide, you'll master:
- Server-Sent Events (SSE) for streaming
- File uploads and validation
- Global error handling
- Request/Response logging
- Response streaming
- WebSockets basics
- Custom exception handlers

---

## 📡 1. Server-Sent Events (SSE)

### What is SSE?

SSE allows servers to push real-time updates to clients over HTTP. Perfect for:
- Live chat responses (like ChatGPT)
- Progress updates
- Real-time notifications
- Streaming data

### Basic SSE Implementation:

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

async def event_generator():
    """
    Generator function that yields Server-Sent Events
    """
    for i in range(10):
        # Simulate work
        await asyncio.sleep(1)
        
        # SSE format: "data: {json}\n\n"
        data = json.dumps({"count": i, "message": f"Event {i}"})
        yield f"data: {data}\n\n"

@app.get("/stream")
async def stream_events():
    """
    Stream events to client
    """
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

### Client-Side JavaScript:

```javascript
// Connect to SSE endpoint
const eventSource = new EventSource('http://localhost:8000/stream');

// Listen for messages
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
    // Update UI with data
};

// Handle errors
eventSource.onerror = (error) => {
    console.error('SSE Error:', error);
    eventSource.close();
};

// Close connection when done
// eventSource.close();
```

### Real-World Example: Streaming AI Chat Response

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

async def stream_ai_response(question: str):
    """
    Stream AI response token by token (like ChatGPT)
    """
    # Simulate AI generating response word by word
    words = [
        "FastAPI", "is", "a", "modern", "web", "framework",
        "for", "building", "APIs", "with", "Python"
    ]
    
    for word in words:
        # Simulate AI thinking time
        await asyncio.sleep(0.3)
        
        # Send word as SSE
        data = json.dumps({"token": word, "done": False})
        yield f"data: {data}\n\n"
    
    # Send completion signal
    yield f"data: {json.dumps({'done': True})}\n\n"

@app.post("/chat/stream")
async def chat_stream(question: str):
    """
    Stream chat response in real-time
    """
    return StreamingResponse(
        stream_ai_response(question),
        media_type="text/event-stream"
    )
```

### Advanced SSE with Progress Tracking:

```python
async def process_document_with_progress(file_path: str):
    """
    Process document and send progress updates
    """
    steps = [
        "Reading file",
        "Extracting text",
        "Chunking content",
        "Generating embeddings",
        "Indexing vectors",
        "Complete"
    ]
    
    for i, step in enumerate(steps):
        # Simulate processing
        await asyncio.sleep(2)
        
        # Calculate progress
        progress = int((i + 1) / len(steps) * 100)
        
        # Send progress update
        yield f"data: {json.dumps({
            'step': step,
            'progress': progress,
            'complete': progress == 100
        })}\n\n"

@app.post("/documents/upload-stream")
async def upload_with_progress(file: UploadFile):
    """
    Upload and process file with real-time progress
    """
    # Save file
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Stream processing progress
    return StreamingResponse(
        process_document_with_progress(file_path),
        media_type="text/event-stream"
    )
```

### SSE Error Handling:

```python
async def safe_event_stream():
    """
    SSE stream with error handling
    """
    try:
        for i in range(100):
            # Check if client disconnected
            await asyncio.sleep(1)
            
            if i == 50:
                # Simulate error
                raise ValueError("Processing error")
            
            yield f"data: {json.dumps({'count': i})}\n\n"
            
    except Exception as e:
        # Send error to client
        error_data = json.dumps({
            'error': str(e),
            'type': 'stream_error'
        })
        yield f"data: {error_data}\n\n"
    finally:
        # Cleanup
        print("Stream closed")
```

---

## 📤 2. File Uploads

### Basic File Upload: [api/routers/documents.py](api/routers/documents.py#L41-L75)

```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from pathlib import Path

# Configuration
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.csv'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload single file
    """
    # Validate file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: 50 MB"
        )
    
    # Save file
    upload_path = Path("uploads") / file.filename
    upload_path.parent.mkdir(exist_ok=True)
    
    with open(upload_path, "wb") as f:
        f.write(content)
    
    return {
        "filename": file.filename,
        "size": len(content),
        "content_type": file.content_type,
        "path": str(upload_path)
    }
```

### Multiple File Uploads:

```python
from typing import List

@app.post("/upload-multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """
    Upload multiple files at once
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 files allowed"
        )
    
    uploaded_files = []
    
    for file in files:
        # Validate and save each file
        content = await file.read()
        
        # Save file
        upload_path = Path("uploads") / file.filename
        with open(upload_path, "wb") as f:
            f.write(content)
        
        uploaded_files.append({
            "filename": file.filename,
            "size": len(content)
        })
    
    return {
        "files_uploaded": len(uploaded_files),
        "files": uploaded_files
    }
```

### File Upload with Form Data:

```python
from fastapi import Form

@app.post("/upload-with-metadata")
async def upload_with_metadata(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(None),
    tags: List[str] = Form([])
):
    """
    Upload file with additional metadata
    """
    content = await file.read()
    
    # Save file
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Save metadata to database
    document = {
        "filename": file.filename,
        "title": title,
        "description": description,
        "tags": tags,
        "size": len(content),
        "path": file_path
    }
    
    return document
```

### Streaming File Upload (Memory Efficient):

```python
@app.post("/upload-stream")
async def upload_stream(file: UploadFile = File(...)):
    """
    Stream file upload without loading entire file into memory
    Perfect for large files!
    """
    file_path = f"uploads/{file.filename}"
    
    # Stream file in chunks
    with open(file_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            f.write(chunk)
    
    return {"filename": file.filename, "status": "uploaded"}
```

### File Download:

```python
from fastapi.responses import FileResponse

@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download file
    """
    file_path = Path("uploads") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )
```

---

## ⚠️ 3. Error Handling

### Global Exception Handler: [api/main.py](api/main.py#L87-L99)

```python
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch all unhandled exceptions
    """
    logger.error(f"Global exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc),
            "path": request.url.path
        }
    )
```

### Custom Exception Classes:

```python
from fastapi import HTTPException, status

class DocumentNotFoundError(HTTPException):
    def __init__(self, document_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

class InsufficientCreditsError(HTTPException):
    def __init__(self, required: int, available: int):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Required: {required}, Available: {available}"
        )

class RateLimitExceededError(HTTPException):
    def __init__(self, retry_after: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Retry after {retry_after} seconds",
            headers={"Retry-After": str(retry_after)}
        )

# Usage
@app.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    document = db.get_document(doc_id)
    
    if not document:
        raise DocumentNotFoundError(doc_id)
    
    return document
```

### Specific Exception Handlers:

```python
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Handle ValueError specifically
    """
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid value", "detail": str(exc)}
    )

@app.exception_handler(DocumentNotFoundError)
async def document_not_found_handler(request: Request, exc: DocumentNotFoundError):
    """
    Custom handler for document errors
    """
    logger.warning(f"Document not found: {request.url.path}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Document not found",
            "message": exc.detail,
            "suggestions": [
                "Check if document ID is correct",
                "Verify you have access to this document"
            ]
        }
    )
```

### Validation Error Customization:

```python
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom validation error response
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation failed",
            "details": errors
        }
    )
```

---

## 📝 4. Request & Response Logging

### Request Logging Middleware:

```python
import time
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all requests with timing and unique ID
    """
    # Generate unique request ID
    request_id = str(uuid4())
    
    # Log request
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} "
        f"- Client: {request.client.host}"
    )
    
    # Process request
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Log response
    logger.info(
        f"[{request_id}] Completed in {duration:.2f}s "
        f"- Status: {response.status_code}"
    )
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(duration)
    
    return response
```

### Detailed Request Logging:

```python
@app.middleware("http")
async def detailed_logging(request: Request, call_next):
    """
    Log request details including headers and body
    """
    # Read body (for POST/PUT requests)
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
        # Restore body for endpoint
        request._body = body
    
    # Log request details
    logger.info({
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "body": body.decode() if body else None,
        "client": request.client.host
    })
    
    response = await call_next(request)
    return response
```

### Structured Logging:

```python
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """
    Format logs as JSON for better parsing
    """
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

---

## 🎨 5. Response Customization

### Custom Response Models:

```python
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """
    Standardized API response format
    """
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Usage
class UserData(BaseModel):
    id: int
    username: str

@app.get("/users/{user_id}", response_model=APIResponse[UserData])
async def get_user(user_id: int):
    user = db.get_user(user_id)
    
    return APIResponse(
        success=True,
        data=user,
        message="User retrieved successfully"
    )
```

### Custom Response Headers:

```python
from fastapi import Response

@app.get("/custom-headers")
async def custom_headers(response: Response):
    """
    Add custom headers to response
    """
    response.headers["X-Custom-Header"] = "CustomValue"
    response.headers["X-Rate-Limit-Remaining"] = "100"
    response.headers["X-Rate-Limit-Reset"] = "1640000000"
    
    return {"message": "Check response headers"}
```

### Different Response Types:

```python
from fastapi.responses import (
    HTMLResponse,
    PlainTextResponse,
    RedirectResponse,
    JSONResponse
)

@app.get("/html", response_class=HTMLResponse)
async def html_response():
    """Return HTML"""
    return "<html><body><h1>Hello World</h1></body></html>"

@app.get("/text", response_class=PlainTextResponse)
async def text_response():
    """Return plain text"""
    return "This is plain text"

@app.get("/redirect")
async def redirect():
    """Redirect to another URL"""
    return RedirectResponse(url="/docs")

@app.get("/custom-json")
async def custom_json():
    """Custom JSON response"""
    return JSONResponse(
        content={"message": "Custom JSON"},
        status_code=201,
        headers={"X-Custom": "Value"}
    )
```

---

## 🌐 6. WebSockets (Bonus)

### Basic WebSocket:

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Basic WebSocket connection
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            # Send response back
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        print("Client disconnected")
```

### Chat Room with WebSockets:

```python
from typing import List

class ConnectionManager:
    """
    Manage WebSocket connections
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        """Send message to all connected clients"""
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/chat")
async def chat_endpoint(websocket: WebSocket, username: str):
    """
    Multi-user chat room
    """
    await manager.connect(websocket)
    await manager.broadcast(f"{username} joined the chat")
    
    try:
        while True:
            # Receive message
            message = await websocket.receive_text()
            
            # Broadcast to all users
            await manager.broadcast(f"{username}: {message}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{username} left the chat")
```

---

## 🧪 7. Practical Exercise: Advanced API

```python
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, WebSocket
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

# SSE for progress updates
async def process_file_stream(filename: str):
    """Stream processing progress"""
    steps = ["Uploading", "Processing", "Analyzing", "Completing"]
    
    for i, step in enumerate(steps):
        await asyncio.sleep(2)
        progress = int((i + 1) / len(steps) * 100)
        
        yield f"data: {json.dumps({
            'step': step,
            'progress': progress
        })}\n\n"

@app.post("/upload-with-progress")
async def upload_with_progress(file: UploadFile):
    """Upload file and stream progress"""
    # Save file
    content = await file.read()
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(content)
    
    # Stream progress
    return StreamingResponse(
        process_file_stream(file.filename),
        media_type="text/event-stream"
    )

# Custom error handling
class ProcessingError(Exception):
    pass

@app.exception_handler(ProcessingError)
async def processing_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Processing failed", "detail": str(exc)}
    )

# Request logging
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response: {response.status_code}")
    return response

# Run with: uvicorn filename:app --reload
```

---

## 🎓 Key Takeaways

1. **SSE for Streaming**: Real-time updates without WebSockets complexity
2. **File Validation**: Always validate file type and size
3. **Global Error Handling**: Catch all exceptions consistently
4. **Custom Exceptions**: Create domain-specific error classes
5. **Request Logging**: Track all requests for debugging
6. **Response Standardization**: Consistent API response format
7. **WebSockets for Real-Time**: Two-way communication when needed

---

## 📖 What's Next?

In **Part 6: Real-World Architecture**, you'll learn:
- Project structure best practices
- Configuration management
- Database integration patterns
- Testing strategies
- Deployment considerations
- Performance optimization

---

## 🔗 Resources

- [FastAPI Advanced Guide](https://fastapi.tiangolo.com/advanced/)
- [Server-Sent Events Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [WebSockets Documentation](https://fastapi.tiangolo.com/advanced/websockets/)
- [File Uploads Best Practices](https://fastapi.tiangolo.com/tutorial/request-files/)
