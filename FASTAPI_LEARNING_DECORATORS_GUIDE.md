# 🎨 Python Decorators - Complete Guide

## 🎯 What You'll Learn
- What decorators are and why they exist
- How decorators work under the hood
- Decorators in FastAPI (@app.get, @router.post, etc.)
- Creating custom decorators
- Real examples from your project

---

## 📚 1. What is a Decorator?

### Simple Analogy:

Imagine you have a gift (a function). A decorator is like **gift wrapping** - it adds something extra to your function without changing what's inside.

```python
# Your function (the gift)
def say_hello():
    return "Hello!"

# Decorator adds extra behavior (gift wrapping)
# Now it logs when the function runs
```

### Technical Definition:

A **decorator** is a function that takes another function and extends its behavior **without explicitly modifying it**.

---

## 🔧 2. Understanding Decorators Step-by-Step

### Level 1: Functions are Objects

In Python, functions are "first-class objects" - they can be:
- Assigned to variables
- Passed as arguments
- Returned from other functions

```python
# Functions are objects!
def greet():
    return "Hello!"

# Assign to variable
my_function = greet
print(my_function())  # Output: Hello!

# Pass as argument
def call_function(func):
    result = func()
    print(result)

call_function(greet)  # Output: Hello!
```

### Level 2: Functions Inside Functions

```python
def outer_function():
    """This is the outer function"""
    
    def inner_function():
        """This is the inner function"""
        return "I'm inside!"
    
    # Return the inner function
    return inner_function

# Get the inner function
my_func = outer_function()

# Call the inner function
print(my_func())  # Output: I'm inside!
```

### Level 3: A Simple Decorator

```python
def my_decorator(func):
    """
    This is a decorator!
    It takes a function and returns a modified version
    """
    def wrapper():
        print("Before the function runs")
        result = func()  # Call original function
        print("After the function runs")
        return result
    
    return wrapper

# Without decorator
def say_hello():
    return "Hello!"

# Manually apply decorator
decorated_function = my_decorator(say_hello)
decorated_function()

# Output:
# Before the function runs
# Hello!
# After the function runs
```

### Level 4: Using @ Symbol (Syntactic Sugar)

```python
# Instead of manually wrapping:
# say_hello = my_decorator(say_hello)

# Python provides the @ syntax:
@my_decorator
def say_hello():
    return "Hello!"

# Now when you call say_hello(), it's automatically wrapped!
say_hello()

# Output:
# Before the function runs
# Hello!
# After the function runs
```

**The `@` symbol is just a shortcut!**

These are **exactly the same**:
```python
# Method 1: Manual
def say_hello():
    return "Hello!"
say_hello = my_decorator(say_hello)

# Method 2: Using @
@my_decorator
def say_hello():
    return "Hello!"
```

---

## 🚀 3. Real-World Example: Timing Functions

### Without Decorator (Repetitive):

```python
import time

def fetch_data():
    start = time.time()
    # Do something
    time.sleep(1)
    result = "Data fetched"
    end = time.time()
    print(f"Time taken: {end - start:.2f}s")
    return result

def process_data():
    start = time.time()
    # Do something
    time.sleep(2)
    result = "Data processed"
    end = time.time()
    print(f"Time taken: {end - start:.2f}s")
    return result

# Lots of repetitive timing code!
```

### With Decorator (Clean):

```python
import time
from functools import wraps

def timer(func):
    """Decorator to time function execution"""
    @wraps(func)  # Preserves original function metadata
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f}s")
        return result
    return wrapper

# Apply decorator
@timer
def fetch_data():
    time.sleep(1)
    return "Data fetched"

@timer
def process_data():
    time.sleep(2)
    return "Data processed"

# Usage
fetch_data()    # Output: fetch_data took 1.00s
process_data()  # Output: process_data took 2.00s
```

---

## 🎭 4. Decorators with Arguments

### Level 1: Function with Arguments

```python
def log_decorator(func):
    """Decorator that logs function calls"""
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned: {result}")
        return result
    return wrapper

@log_decorator
def add(a, b):
    return a + b

@log_decorator
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

# Usage
add(5, 3)
# Output:
# Calling add with args=(5, 3), kwargs={}
# add returned: 8

greet("Alice", greeting="Hi")
# Output:
# Calling greet with args=('Alice',), kwargs={'greeting': 'Hi'}
# greet returned: Hi, Alice!
```

### Level 2: Decorator with Arguments

```python
def repeat(times):
    """
    Decorator that repeats function execution
    This is a decorator FACTORY - it returns a decorator
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(times):
                print(f"Execution {i + 1}:")
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

# Use decorator with argument
@repeat(times=3)
def say_hello():
    print("Hello!")

say_hello()
# Output:
# Execution 1:
# Hello!
# Execution 2:
# Hello!
# Execution 3:
# Hello!
```

**How it works:**
```python
# This:
@repeat(times=3)
def say_hello():
    pass

# Is the same as:
decorator = repeat(times=3)  # Returns a decorator
say_hello = decorator(say_hello)  # Apply decorator
```

---

## 🌐 5. Decorators in FastAPI

### How FastAPI Uses Decorators

FastAPI decorators **register** your functions as API endpoints!

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

**What's happening:**
1. `@app.get("/")` is a decorator
2. It registers `read_root` function to handle GET requests to "/"
3. FastAPI automatically converts the return value to JSON

### Example from Your Project: [api/main.py](api/main.py)

```python
from fastapi import FastAPI

app = FastAPI()

# This decorator registers an endpoint
@app.get("/health")
async def health_check():
    """
    The @app.get decorator:
    1. Takes the function health_check
    2. Registers it to handle GET requests to /health
    3. Automatically converts return value to JSON response
    """
    return {
        "status": "healthy",
        "timestamp": time.time()
    }
```

### Behind the Scenes (Simplified):

```python
class FastAPI:
    def __init__(self):
        self.routes = {}
    
    def get(self, path):
        """
        This is a decorator factory!
        It returns a decorator that registers the route
        """
        def decorator(func):
            # Register the function for this path
            self.routes[("GET", path)] = func
            print(f"Registered GET {path} -> {func.__name__}")
            return func
        return decorator

# Usage
app = FastAPI()

@app.get("/users")
def get_users():
    return {"users": []}

# What happens:
# 1. app.get("/users") returns a decorator
# 2. That decorator receives get_users function
# 3. The decorator registers: routes[("GET", "/users")] = get_users
# 4. The decorator returns the original function
```

### Real Example from Your Project: [api/routers/auth.py](api/routers/auth.py)

```python
from fastapi import APIRouter, status

router = APIRouter()

# Decorator with path and response model
@router.post("/signup", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup):
    """
    Multiple things happening:
    1. @router.post - registers POST endpoint at /signup
    2. response_model=UserProfile - validates/formats response
    3. status_code=201 - sets HTTP status code
    """
    # Function code...
    pass
```

---

## 🎯 6. Common Decorator Patterns

### Pattern 1: Authorization Decorator

```python
from functools import wraps
from fastapi import HTTPException

def require_admin(func):
    """Only allow admin users"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get current_user from kwargs (passed by dependency)
        current_user = kwargs.get('current_user')
        
        if not current_user or current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return await func(*args, **kwargs)
    return wrapper

# Usage
@require_admin
async def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    """Only admins can delete users"""
    pass
```

### Pattern 2: Caching Decorator

```python
from functools import wraps
import time

cache = {}

def cached(expire_seconds=60):
    """Cache function results for specified time"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = f"{func.__name__}:{args}:{kwargs}"
            
            # Check cache
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < expire_seconds:
                    print(f"Cache hit for {func.__name__}")
                    return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result
        return wrapper
    return decorator

# Usage
@cached(expire_seconds=300)  # Cache for 5 minutes
def expensive_calculation(n):
    print("Calculating...")
    time.sleep(2)  # Simulate expensive operation
    return n ** 2

# First call: slow
result1 = expensive_calculation(5)  # Takes 2 seconds

# Second call: fast (from cache)
result2 = expensive_calculation(5)  # Instant!
```

### Pattern 3: Retry Decorator

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1):
    """Retry function on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        print(f"Failed after {max_attempts} attempts")
                        raise
                    print(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

# Usage
@retry(max_attempts=3, delay=2)
def unreliable_api_call():
    """This might fail sometimes"""
    import random
    if random.random() < 0.7:
        raise Exception("API Error")
    return "Success!"
```

### Pattern 4: Validation Decorator

```python
def validate_positive(func):
    """Ensure all numeric arguments are positive"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check all arguments
        for arg in args:
            if isinstance(arg, (int, float)) and arg < 0:
                raise ValueError(f"Expected positive number, got {arg}")
        
        for key, value in kwargs.items():
            if isinstance(value, (int, float)) and value < 0:
                raise ValueError(f"Expected positive {key}, got {value}")
        
        return func(*args, **kwargs)
    return wrapper

# Usage
@validate_positive
def calculate_area(width, height):
    return width * height

calculate_area(5, 10)     # OK: 50
calculate_area(-5, 10)    # Error: ValueError
```

---

## 🔗 7. Chaining Multiple Decorators

You can stack multiple decorators!

```python
@decorator1
@decorator2
@decorator3
def my_function():
    pass

# Execution order (bottom to top):
# 1. decorator3 wraps my_function
# 2. decorator2 wraps the result
# 3. decorator1 wraps the result
```

### Real Example:

```python
@timer           # 3rd: Times execution
@log_decorator   # 2nd: Logs calls
@cached          # 1st: Caches result
def complex_calculation(n):
    return n ** 2

# When you call complex_calculation(5):
# 1. Cached checks if result is in cache
# 2. If not, log_decorator logs the call
# 3. Timer measures execution time
# 4. Original function runs
```

### Example from Your Project Pattern:

```python
from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/query")                    # Decorator 3: Route registration
@require_authentication                   # Decorator 2: Check auth
@rate_limit(requests_per_minute=60)      # Decorator 1: Rate limiting
async def query_documents(
    query: ChatQuery,
    current_user: dict = Depends(get_current_user)
):
    """
    Execution order:
    1. Rate limit check
    2. Authentication check
    3. Route handler
    """
    pass
```

---

## 🛠️ 8. Creating Your Own Decorators

### Template for Simple Decorator:

```python
from functools import wraps

def my_decorator(func):
    """
    Decorator template
    """
    @wraps(func)  # Preserves original function name and docstring
    def wrapper(*args, **kwargs):
        # Code to run BEFORE function
        print("Before")
        
        # Call original function
        result = func(*args, **kwargs)
        
        # Code to run AFTER function
        print("After")
        
        # Return result
        return result
    
    return wrapper
```

### Template for Decorator with Arguments:

```python
from functools import wraps

def my_decorator(arg1, arg2):
    """
    Decorator factory template
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use arg1 and arg2
            print(f"Args: {arg1}, {arg2}")
            
            # Call original function
            result = func(*args, **kwargs)
            
            return result
        return wrapper
    return decorator

# Usage
@my_decorator(arg1="value1", arg2="value2")
def my_function():
    pass
```

### Async Decorator Template:

```python
from functools import wraps

def async_decorator(func):
    """
    Decorator for async functions
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Code before
        print("Before async function")
        
        # Await the async function
        result = await func(*args, **kwargs)
        
        # Code after
        print("After async function")
        
        return result
    return wrapper

# Usage
@async_decorator
async def fetch_data():
    await asyncio.sleep(1)
    return "Data"
```

---

## 🧪 9. Practical Exercise

### Exercise 1: Create a Logger Decorator

```python
import logging
from functools import wraps

def log_function(func):
    """Log function calls with arguments and results"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # TODO: Log function call with arguments
        # TODO: Call the function
        # TODO: Log the result
        # TODO: Return the result
        pass
    return wrapper

# Test
@log_function
def add(a, b):
    return a + b

add(5, 3)  # Should log: "Calling add with (5, 3)" and "add returned 8"
```

### Exercise 2: Rate Limiting Decorator

```python
import time
from functools import wraps

def rate_limit(calls_per_minute):
    """Limit function calls per minute"""
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # TODO: Track function calls
            # TODO: Check if rate limit exceeded
            # TODO: If exceeded, raise exception
            # TODO: If OK, call function
            pass
        return wrapper
    return decorator

# Test
@rate_limit(calls_per_minute=3)
def api_call():
    print("API called")

# Should allow 3 calls, then block
```

---

## 🎓 10. Key Takeaways

### What Decorators Are:
✅ Functions that modify other functions  
✅ Add behavior without changing original code  
✅ Use `@` symbol for clean syntax  
✅ Can be stacked (multiple decorators)  

### Common Uses:
✅ **Logging** - Track function calls  
✅ **Timing** - Measure performance  
✅ **Caching** - Store results  
✅ **Authentication** - Check permissions  
✅ **Validation** - Verify inputs  
✅ **Retry Logic** - Handle failures  
✅ **Rate Limiting** - Control usage  

### In FastAPI:
✅ `@app.get()` - Register GET endpoints  
✅ `@app.post()` - Register POST endpoints  
✅ `@router.put()` - Register PUT endpoints  
✅ `Depends()` - Dependency injection (special decorator pattern)  

### Best Practices:
✅ Use `@wraps(func)` to preserve function metadata  
✅ Handle `*args, **kwargs` for flexibility  
✅ Keep decorators simple and focused  
✅ Document what your decorator does  
✅ Consider making decorators configurable  

---

## 🔗 11. Decorators in Your Project

### Example 1: Route Decorators
[api/routers/chat.py](api/routers/chat.py#L56)
```python
@router.post("/query", response_model=ChatResponse)
async def query_documents(query: ChatQuery):
    pass
```
**What's happening:**
- `@router.post` registers the function as a POST endpoint
- `response_model=ChatResponse` validates the response

### Example 2: Authentication Decorator
[api/routers/auth.py](api/routers/auth.py#L61)
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    pass
```
**What's happening:**
- `Depends()` is a special decorator pattern
- It injects the result of `security` into the function

### Example 3: Middleware (Decorator Pattern)
[api/main.py](api/main.py#L76)
```python
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    pass
```
**What's happening:**
- `@app.middleware` registers a middleware function
- It wraps ALL requests

---

## 📚 Additional Resources

### Official Documentation:
- [Python Decorators](https://docs.python.org/3/glossary.html#term-decorator)
- [PEP 318 - Decorators](https://www.python.org/dev/peps/pep-0318/)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)

### Tutorials:
- [Real Python - Decorators](https://realpython.com/primer-on-python-decorators/)
- [Python Decorator Tutorial](https://www.datacamp.com/tutorial/decorators-python)

---

## 🎉 Summary

**Decorators are functions that wrap other functions to add extra behavior.**

Simple concept:
```python
# This:
@decorator
def function():
    pass

# Is the same as:
function = decorator(function)
```

In FastAPI, decorators are used to:
- Register routes (`@app.get`, `@router.post`)
- Add middleware (`@app.middleware`)
- Inject dependencies (`Depends()`)
- Configure responses (`response_model`, `status_code`)

**Key takeaway:** Decorators make your code cleaner and more reusable by separating concerns!

---

*Happy decorating! 🎨*
