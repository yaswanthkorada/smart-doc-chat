# FastAPI Learning Guide - Part 4: Async Programming

## 🎯 Learning Objectives
After this guide, you'll master:
- async/await fundamentals
- When to use async vs sync functions
- asyncio.gather for concurrent operations
- Background tasks in FastAPI
- Thread pools for blocking I/O
- Real-world async patterns

---

## 📚 1. What is Async Programming?

### Traditional Synchronous Code:

```python
import time

def fetch_user(user_id):
    time.sleep(1)  # Simulates database query
    return {"id": user_id, "name": "John"}

def fetch_posts(user_id):
    time.sleep(1)  # Simulates database query
    return [{"id": 1, "title": "Post 1"}]

# Sequential execution
start = time.time()
user = fetch_user(1)       # Wait 1 second
posts = fetch_posts(1)     # Wait another 1 second
print(f"Total time: {time.time() - start:.2f}s")
# Output: Total time: 2.00s
```

### Asynchronous Code:

```python
import asyncio

async def fetch_user(user_id):
    await asyncio.sleep(1)  # Simulates async database query
    return {"id": user_id, "name": "John"}

async def fetch_posts(user_id):
    await asyncio.sleep(1)  # Simulates async database query
    return [{"id": 1, "title": "Post 1"}]

# Concurrent execution
async def main():
    start = time.time()
    # Run both tasks concurrently!
    user, posts = await asyncio.gather(
        fetch_user(1),
        fetch_posts(1)
    )
    print(f"Total time: {time.time() - start:.2f}s")
    # Output: Total time: 1.00s (50% faster!)

asyncio.run(main())
```

### 🔍 Key Differences:

| Synchronous | Asynchronous |
|-------------|--------------|
| Blocks while waiting | Doesn't block |
| Sequential execution | Concurrent execution |
| `def` functions | `async def` functions |
| Direct calls | Must use `await` |
| Simple but slow | Complex but fast |

---

## 🚀 2. Async in FastAPI

### Why FastAPI Uses Async:

```python
# Synchronous endpoint (blocks while processing)
@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = db.query_user(user_id)  # Blocks for 100ms
    # While this runs, NO other requests can be processed!
    return user

# Asynchronous endpoint (doesn't block)
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await db.query_user(user_id)  # Yields control for 100ms
    # While waiting, FastAPI can process other requests!
    return user
```

### 🔍 Your Project Example: [api/routers/chat.py](api/routers/chat.py#L56-L73)

```python
@router.post("/query", response_model=ChatResponse)
async def query_documents(
    query: ChatQuery,
    current_user: dict = Depends(get_current_user)
):
    """
    Async endpoint - can handle multiple concurrent requests
    """
    # Get user ID
    user_id = str(current_user.id)
    
    # Query agent system (might take several seconds)
    result = agent_rag_engine.query(
        question=query.question,
        user_id=user_id
    )
    
    return ChatResponse(...)
```

---

## ⚡ 3. When to Use Async vs Sync

### Use `async def` when:

```python
# ✅ I/O-bound operations (waiting for external resources)
async def fetch_from_api():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
    return response.json()

async def query_database():
    async with database.async_session() as session:
        result = await session.execute(query)
    return result

async def read_file_async():
    async with aiofiles.open("data.txt") as f:
        content = await f.read()
    return content

# ✅ Multiple operations that can run concurrently
async def get_user_dashboard(user_id: int):
    # Fetch all data concurrently
    user, posts, comments, notifications = await asyncio.gather(
        fetch_user(user_id),
        fetch_user_posts(user_id),
        fetch_user_comments(user_id),
        fetch_notifications(user_id)
    )
    return {"user": user, "posts": posts, ...}
```

### Use regular `def` when:

```python
# ✅ CPU-bound operations (calculations)
def calculate_fibonacci(n: int):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# ✅ Synchronous libraries (no async version available)
def process_image(image_path: str):
    from PIL import Image
    img = Image.open(image_path)  # PIL is synchronous
    img = img.resize((800, 600))
    return img

# ✅ Simple, fast operations (no I/O)
def format_response(data: dict):
    return {
        "status": "success",
        "data": data,
        "timestamp": datetime.now()
    }
```

### ⚠️ Common Mistake:

```python
# ❌ BAD - Async function but no await (no benefit!)
async def bad_example():
    result = expensive_calculation()  # Synchronous, blocks anyway
    return result

# ✅ GOOD - Regular function
def good_example():
    result = expensive_calculation()
    return result
```

---

## 🔄 4. asyncio.gather - Concurrent Operations

### Basic Example:

```python
import asyncio

async def task_1():
    await asyncio.sleep(1)
    return "Task 1 done"

async def task_2():
    await asyncio.sleep(2)
    return "Task 2 done"

async def task_3():
    await asyncio.sleep(1.5)
    return "Task 3 done"

async def main():
    # Sequential (slow)
    result1 = await task_1()  # Wait 1s
    result2 = await task_2()  # Wait 2s
    result3 = await task_3()  # Wait 1.5s
    # Total: 4.5 seconds
    
    # Concurrent (fast!)
    results = await asyncio.gather(
        task_1(),
        task_2(),
        task_3()
    )
    # Total: 2 seconds (longest task)
    print(results)  # ["Task 1 done", "Task 2 done", "Task 3 done"]

asyncio.run(main())
```

### Real-World Example from Your Project Pattern:

```python
@router.get("/dashboard")
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    """
    Fetch all dashboard data concurrently
    """
    user_id = str(current_user.id)
    
    # Fetch everything in parallel
    (
        documents,
        conversations,
        usage_stats,
        recent_queries
    ) = await asyncio.gather(
        db_manager.get_user_documents(user_id),
        db_manager.get_user_conversations(user_id),
        db_manager.get_usage_stats(user_id),
        db_manager.get_recent_queries(user_id, limit=10)
    )
    
    return {
        "documents": documents,
        "conversations": conversations,
        "usage_stats": usage_stats,
        "recent_queries": recent_queries
    }
```

### Error Handling with asyncio.gather:

```python
async def fetch_data():
    try:
        results = await asyncio.gather(
            task_1(),
            task_2(),
            task_3(),
            return_exceptions=True  # Don't stop on first error
        )
        
        # Check for exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Task {i+1} failed: {result}")
            else:
                logger.info(f"Task {i+1} succeeded: {result}")
        
    except Exception as e:
        logger.error(f"Gather failed: {e}")
```

---

## 🎭 5. Background Tasks

### Example from FastAPI Documentation:

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    """
    Sending email takes time (5 seconds)
    But we don't want user to wait!
    """
    time.sleep(5)  # Simulates email sending
    print(f"Email sent to {email}: {message}")

@app.post("/send-notification")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    """
    Endpoint returns immediately
    Email is sent in background
    """
    # Add task to background
    background_tasks.add_task(send_email, email, "Welcome!")
    
    # Return immediately (user doesn't wait 5 seconds!)
    return {"message": "Notification scheduled"}
```

### Real-World Use Cases:

```python
from fastapi import BackgroundTasks

def process_large_file(file_path: str, user_id: str):
    """Heavy processing in background"""
    # Extract text, generate embeddings, index in vector DB
    time.sleep(30)  # Simulates processing
    print(f"File processed: {file_path}")

def log_analytics(user_id: str, action: str, metadata: dict):
    """Log to analytics service"""
    requests.post("https://analytics.example.com/log", json={
        "user_id": user_id,
        "action": action,
        "metadata": metadata,
        "timestamp": datetime.now()
    })

def cleanup_temp_files(file_paths: list):
    """Delete temporary files"""
    for path in file_paths:
        os.remove(path)

@app.post("/upload")
async def upload_file(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Upload file and process in background
    """
    # Save file quickly
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Schedule background tasks
    background_tasks.add_task(
        process_large_file, 
        file_path, 
        current_user.id
    )
    background_tasks.add_task(
        log_analytics,
        current_user.id,
        "file_upload",
        {"filename": file.filename}
    )
    
    # Return immediately
    return {"message": "File uploaded, processing in background"}
```

### 🔍 Background Task Limitations:

```python
# ⚠️ Limitations:
# 1. No guarantee of completion if server restarts
# 2. Can't track progress or status
# 3. Not suitable for long-running tasks (use Celery instead)
# 4. Runs in same process (doesn't scale)

# For production, use task queues:
# - Celery with Redis/RabbitMQ
# - Huey
# - Dramatiq
```

---

## 🧵 6. Thread Pools for Blocking Operations

### Problem: Blocking Sync Functions in Async Code

```python
import time

def blocking_operation():
    """
    This is synchronous and blocks the event loop
    Even if called from async function!
    """
    time.sleep(5)  # Blocks everything!
    return "Done"

# ❌ BAD - Blocks event loop
@app.get("/bad")
async def bad_endpoint():
    result = blocking_operation()  # Blocks for 5 seconds
    # No other requests can be processed during this time!
    return {"result": result}
```

### Solution: Run in Thread Pool

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)

# ✅ GOOD - Runs in thread pool
@app.get("/good")
async def good_endpoint():
    loop = asyncio.get_event_loop()
    
    # Run blocking function in thread pool
    result = await loop.run_in_executor(
        executor,
        blocking_operation
    )
    # Event loop not blocked!
    return {"result": result}
```

### Real-World Example: Image Processing

```python
from PIL import Image
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

def process_image_sync(image_path: str):
    """
    PIL is synchronous (no async version)
    This would block the event loop
    """
    img = Image.open(image_path)
    img = img.resize((800, 600))
    img = img.convert("RGB")
    img.save(f"processed_{image_path}")
    return f"processed_{image_path}"

@app.post("/process-image")
async def process_image(file: UploadFile):
    """
    Process image without blocking event loop
    """
    # Save uploaded file
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Process in thread pool
    loop = asyncio.get_event_loop()
    processed_path = await loop.run_in_executor(
        executor,
        process_image_sync,
        file_path
    )
    
    return {"processed_file": processed_path}
```

### Multiple Blocking Operations Concurrently:

```python
async def process_multiple_images(image_paths: list):
    """
    Process multiple images concurrently in thread pool
    """
    loop = asyncio.get_event_loop()
    
    # Create tasks for all images
    tasks = [
        loop.run_in_executor(executor, process_image_sync, path)
        for path in image_paths
    ]
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks)
    return results
```

---

## 🔥 7. Advanced Async Patterns

### Pattern 1: Timeout for Slow Operations

```python
import asyncio

@app.get("/search")
async def search_with_timeout(query: str):
    """
    Search with 5-second timeout
    """
    try:
        result = await asyncio.wait_for(
            perform_search(query),
            timeout=5.0
        )
        return {"result": result}
    except asyncio.TimeoutError:
        return {"error": "Search took too long"}
```

### Pattern 2: Retry with Exponential Backoff

```python
async def retry_async(func, max_retries=3, base_delay=1):
    """
    Retry async function with exponential backoff
    """
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise  # Last attempt failed
            
            # Exponential backoff: 1s, 2s, 4s
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
            await asyncio.sleep(delay)

@app.get("/external-api")
async def call_external_api():
    """Call external API with retries"""
    result = await retry_async(
        lambda: httpx.get("https://api.example.com/data")
    )
    return result.json()
```

### Pattern 3: Async Context Managers

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_connection():
    """
    Async context manager for database connections
    """
    # Setup
    conn = await asyncpg.connect("postgresql://...")
    try:
        yield conn
    finally:
        # Cleanup (guaranteed to run)
        await conn.close()

# Usage
async def query_user(user_id: int):
    async with get_db_connection() as conn:
        result = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1",
            user_id
        )
        return result
```

### Pattern 4: Async Generators

```python
async def fetch_items_paginated(page_size: int = 100):
    """
    Async generator for pagination
    """
    offset = 0
    while True:
        # Fetch page
        items = await db.fetch_items(offset, page_size)
        
        if not items:
            break  # No more items
        
        # Yield items one by one
        for item in items:
            yield item
        
        offset += page_size

# Usage
async def process_all_items():
    async for item in fetch_items_paginated():
        await process_item(item)
```

---

## 📡 8. Async HTTP Requests

### Using httpx (Async HTTP Client):

```python
import httpx

# ❌ BAD - Using synchronous requests library
import requests

@app.get("/weather")
async def get_weather():
    # This blocks the event loop!
    response = requests.get("https://api.weather.com/current")
    return response.json()

# ✅ GOOD - Using async httpx
@app.get("/weather")
async def get_weather():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.weather.com/current")
        return response.json()
```

### Multiple API Calls Concurrently:

```python
async def fetch_user_data(user_id: str):
    """
    Fetch data from multiple APIs concurrently
    """
    async with httpx.AsyncClient() as client:
        # Fetch all concurrently
        profile_task = client.get(f"https://api1.com/users/{user_id}")
        posts_task = client.get(f"https://api2.com/users/{user_id}/posts")
        followers_task = client.get(f"https://api3.com/users/{user_id}/followers")
        
        # Wait for all
        profile_res, posts_res, followers_res = await asyncio.gather(
            profile_task,
            posts_task,
            followers_task
        )
        
        return {
            "profile": profile_res.json(),
            "posts": posts_res.json(),
            "followers": followers_res.json()
        }
```

---

## 🧪 9. Practical Exercise: Build Async API

```python
from fastapi import FastAPI, BackgroundTasks
import asyncio
import httpx
from datetime import datetime

app = FastAPI()

# Simulated async database
async def async_db_query(query: str, delay: float = 0.5):
    """Simulate async database query"""
    await asyncio.sleep(delay)
    return {"query": query, "result": "data"}

# Background task
def send_email_notification(email: str, subject: str):
    """Simulate email sending"""
    print(f"Sending email to {email}: {subject}")
    # In production: use SendGrid, AWS SES, etc.

@app.get("/user/{user_id}")
async def get_user(user_id: int):
    """
    Fetch user data from multiple sources concurrently
    """
    start = datetime.now()
    
    # Fetch concurrently
    profile, posts, settings = await asyncio.gather(
        async_db_query(f"SELECT * FROM users WHERE id={user_id}"),
        async_db_query(f"SELECT * FROM posts WHERE user_id={user_id}"),
        async_db_query(f"SELECT * FROM settings WHERE user_id={user_id}")
    )
    
    duration = (datetime.now() - start).total_seconds()
    
    return {
        "profile": profile,
        "posts": posts,
        "settings": settings,
        "fetch_time": f"{duration:.2f}s"
    }

@app.post("/signup")
async def signup(
    email: str,
    username: str,
    background_tasks: BackgroundTasks
):
    """
    Create user and send welcome email in background
    """
    # Create user (quick)
    await async_db_query(f"INSERT INTO users (email, username) VALUES ...")
    
    # Send welcome email in background (don't wait)
    background_tasks.add_task(
        send_email_notification,
        email,
        "Welcome to our platform!"
    )
    
    return {"message": "Account created, check your email"}

@app.get("/external-data")
async def fetch_external_data():
    """
    Fetch from multiple external APIs concurrently
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Make requests concurrently
        responses = await asyncio.gather(
            client.get("https://jsonplaceholder.typicode.com/posts/1"),
            client.get("https://jsonplaceholder.typicode.com/users/1"),
            client.get("https://jsonplaceholder.typicode.com/comments/1"),
            return_exceptions=True
        )
        
        # Process responses
        results = []
        for response in responses:
            if isinstance(response, Exception):
                results.append({"error": str(response)})
            else:
                results.append(response.json())
        
        return results

@app.get("/slow-operation")
async def slow_operation():
    """
    Run blocking operation in thread pool
    """
    import time
    
    def blocking_task():
        time.sleep(3)  # Blocking operation
        return "Operation complete"
    
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, blocking_task)
    
    return {"result": result}

# Test the endpoints to see async in action!
# Multiple requests to /user/1 will be handled concurrently
```

---

## 🎓 Key Takeaways

1. **Use `async def` for I/O-bound operations** (API calls, database queries)
2. **Use regular `def` for CPU-bound operations** (calculations, data processing)
3. **`asyncio.gather`** runs multiple async tasks concurrently
4. **Background tasks** for fire-and-forget operations
5. **Thread pools** for blocking sync operations
6. **Async doesn't mean faster** - it means more concurrent!
7. **Don't block the event loop** - use executor for blocking code

---

## 📖 What's Next?

In **Part 5: Advanced Patterns**, you'll learn:
- Server-Sent Events (SSE) for streaming
- File uploads and processing
- WebSockets for real-time communication
- Error handling and logging
- Request validation
- Response streaming

---

## 🔗 Resources

- [FastAPI Async Documentation](https://fastapi.tiangolo.com/async/)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [Real Python Async Guide](https://realpython.com/async-io-python/)
- [HTTPX Documentation](https://www.python-httpx.org/)
