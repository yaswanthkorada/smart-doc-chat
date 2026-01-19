# FastAPI Learning Guide - Part 3: Authentication & Security

## 🎯 Learning Objectives
After this guide, you'll master:
- JWT (JSON Web Tokens) authentication
- Password hashing with bcrypt
- Dependency injection pattern
- Security schemes and bearer tokens
- Protected endpoints
- Middleware for authentication

---

## 📚 1. Authentication Flow Overview

### Your Project's Authentication System:

```
1. User Registration (Signup)
   ↓
   Hash password with bcrypt
   ↓
   Store in database

2. User Login
   ↓
   Verify credentials
   ↓
   Generate JWT token
   ↓
   Return token to client

3. Protected Requests
   ↓
   Client sends token in header: Authorization: Bearer <token>
   ↓
   FastAPI validates token
   ↓
   Extract user info
   ↓
   Allow access to resource
```

---

## 🔐 2. Password Hashing

### Example from Your Project: [api/routers/auth.py](api/routers/auth.py#L34-L42)

```python
from passlib.context import CryptContext

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)
```

### 🔍 Why Hash Passwords?

**❌ NEVER store plain text passwords:**
```python
# WRONG - Don't do this!
user.password = "mypassword123"  # Visible in database
```

**✅ Always hash passwords:**
```python
# CORRECT - Do this!
user.password = get_password_hash("mypassword123")
# Stored as: $2b$12$KIXxkjhsd8fh3kjhf4kjhf4...
```

### How Bcrypt Works:

```python
# Registration
plain_password = "SecurePass123!"
hashed = get_password_hash(plain_password)
# Result: "$2b$12$N9qo8uLOickgx2ZMRZoMye.bF3fIZWhzE7qxWGqYHsW6M9F3P2/6S"

# Login verification
entered_password = "SecurePass123!"
is_valid = verify_password(entered_password, hashed)
# Result: True

# Wrong password
wrong_password = "WrongPass456"
is_valid = verify_password(wrong_password, hashed)
# Result: False
```

**Key Features:**
- **One-way function**: Can't reverse hash to get password
- **Salt**: Adds random data to prevent rainbow table attacks
- **Slow**: Intentionally slow to prevent brute force attacks
- **Adaptive**: Can increase rounds as computers get faster

---

## 🎫 3. JWT Token Authentication

### Example from Your Project: [api/routers/auth.py](api/routers/auth.py#L28-L31)

```python
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
```

### Creating JWT Tokens: [api/routers/auth.py](api/routers/auth.py#L45-L58)

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add standard JWT claims
    to_encode.update({
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow()  # Issued at time
    })
    
    # Encode and sign token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

### 🔍 JWT Structure:

A JWT token has 3 parts separated by dots:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsImVtYWlsIjoiam9obkBleGFtcGxlLmNvbSIsImV4cCI6MTcwNTY4MDAwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
│                 Header                 │                          Payload                          │              Signature              │
```

**1. Header:**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**2. Payload (Your Data):**
```json
{
  "sub": "user_123",        // Subject (user ID)
  "email": "john@example.com",
  "exp": 1705680000,        // Expiration timestamp
  "iat": 1705593600         // Issued at timestamp
}
```

**3. Signature:**
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)
```

### Login Endpoint Example: [api/routers/auth.py](api/routers/auth.py#L176-L218)

```python
@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    User login endpoint
    
    Returns JWT token for authentication
    """
    try:
        # Get user from database
        user = db_manager.get_user_by_email(credentials.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create JWT token
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email
            }
        )
        
        # Update last login
        db_manager.update_user_last_login(str(user.id))
        
        logger.info(f"User logged in: {credentials.email}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )
```

---

## 🛡️ 4. Dependency Injection for Authentication

### HTTP Bearer Security: [api/routers/auth.py](api/routers/auth.py#L33-L34)

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()
```

### Get Current User Dependency: [api/routers/auth.py](api/routers/auth.py#L61-L94)

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency that validates JWT token and returns user
    
    This is called automatically by FastAPI before endpoint function
    """
    # Create exception for invalid credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from Authorization header
        token = credentials.credentials
        
        # Decode and verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract user info from token
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None or email is None:
            raise credentials_exception
            
        token_data = TokenData(user_id=user_id, email=email)
        
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception
    
    # Verify user still exists in database
    user = db_manager.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user
```

### 🔍 How Dependency Injection Works:

```python
from fastapi import Depends

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Protected endpoint - requires authentication
    
    FastAPI automatically:
    1. Extracts Authorization header: "Bearer eyJhbGciOiJI..."
    2. Calls get_current_user() function
    3. Validates token
    4. Returns user object
    5. Passes user to this function as current_user parameter
    
    If token is invalid:
    - Returns 401 Unauthorized
    - Endpoint function never executes
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username
    }
```

### Client Request Example:

```bash
# Without token (fails)
curl http://localhost:8000/api/users/profile
# Response: 401 Unauthorized

# With token (succeeds)
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     http://localhost:8000/api/users/profile
# Response: {"id": "user_123", "email": "john@example.com", ...}
```

---

## 🔒 5. Protected Endpoints

### Example from Your Project: [api/routers/documents.py](api/routers/documents.py#L41-L47)

```python
@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)  # Requires authentication!
):
    """
    Upload document - Protected endpoint
    
    Only authenticated users can upload documents
    """
    user_id = str(current_user.id)  # Get user ID from token
    # Process document for this specific user
    pass
```

### Multiple Dependency Example:

```python
from typing import Optional

async def get_optional_user(
    authorization: Optional[str] = Header(None)
) -> Optional[dict]:
    """Optional authentication - doesn't fail if no token"""
    if not authorization:
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        return db_manager.get_user_by_id(user_id)
    except:
        return None

@router.get("/posts")
async def list_posts(
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Public endpoint - but shows different content for logged-in users
    """
    if current_user:
        # Show user's private posts + public posts
        return get_all_posts(user_id=current_user.id)
    else:
        # Show only public posts
        return get_public_posts()
```

---

## 🌐 6. CORS Middleware

### Example from Your Project: [api/main.py](api/main.py#L54-L69)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React frontend
        "http://localhost:5173",  # Vite frontend
        "http://localhost:8501",  # Streamlit app
        "*"  # Allow all origins (only in development!)
    ],
    allow_credentials=True,  # Allow cookies and Authorization header
    allow_methods=["*"],     # Allow all HTTP methods
    allow_headers=["*"],     # Allow all headers
    expose_headers=["*"]     # Expose all headers to JavaScript
)
```

### 🔍 Why CORS?

**CORS (Cross-Origin Resource Sharing)** prevents JavaScript from making requests to different domains.

**Without CORS:**
```
Frontend: http://localhost:3000
API: http://localhost:8000

Browser blocks the request! ❌
```

**With CORS middleware:**
```
Frontend: http://localhost:3000
API: http://localhost:8000 (with CORS enabled)

Browser allows the request! ✅
```

### Production CORS Configuration:

```python
# ❌ DON'T do this in production:
allow_origins=["*"]  # Allows ANY website to access your API!

# ✅ DO this in production:
allow_origins=[
    "https://your-frontend.com",
    "https://app.your-frontend.com"
]
```

---

## ⏱️ 7. Custom Middleware

### Example from Your Project: [api/main.py](api/main.py#L76-L84)

```python
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add response time to all responses"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate time taken
    process_time = time.time() - start_time
    
    # Add custom header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response
```

### 🔍 How Middleware Works:

```
Client Request
    ↓
Middleware 1 (CORS)
    ↓
Middleware 2 (Process Time)
    ↓
Middleware 3 (Authentication)
    ↓
Your Endpoint Function
    ↓
Response
    ↓
Middleware 3 (adds headers)
    ↓
Middleware 2 (adds headers)
    ↓
Middleware 1 (adds headers)
    ↓
Client Response
```

### More Middleware Examples:

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    """Simple rate limiting"""
    client_ip = request.client.host
    
    # Check rate limit (simplified)
    if is_rate_limited(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error": "Too many requests"}
        )
    
    return await call_next(request)
```

---

## 🎯 8. Role-Based Access Control (RBAC)

### Advanced Pattern - Not in Your Project Yet:

```python
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

def require_role(required_role: UserRole):
    """Dependency factory for role-based access"""
    async def check_role(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", UserRole.USER)
        
        # Define role hierarchy
        roles_hierarchy = {
            UserRole.USER: 0,
            UserRole.MODERATOR: 1,
            UserRole.ADMIN: 2
        }
        
        if roles_hierarchy[user_role] < roles_hierarchy[required_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role or higher"
            )
        
        return current_user
    
    return check_role

# Usage
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """Only admins can delete users"""
    pass

@router.post("/posts/{post_id}/approve")
async def approve_post(
    post_id: str,
    current_user: dict = Depends(require_role(UserRole.MODERATOR))
):
    """Moderators and admins can approve posts"""
    pass
```

---

## 🔐 9. API Keys (Alternative Authentication)

```python
from fastapi import Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: str = Security(api_key_header)):
    """Validate API key"""
    # Check if API key exists in database
    user = db_manager.get_user_by_api_key(api_key)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return user

@router.get("/data")
async def get_data(user: dict = Depends(get_api_key)):
    """Endpoint protected by API key"""
    return {"data": "sensitive information"}

# Client request:
# curl -H "X-API-Key: sk_live_abc123..." http://localhost:8000/data
```

---

## 🧪 10. Practical Exercise: Build Authentication System

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"])

SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"

# In-memory user storage (use database in production!)
users_db = {}

# Models
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class User(BaseModel):
    id: int
    email: str
    username: str

# Helper functions
def create_token(user_id: int, email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {"sub": str(user_id), "email": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
        
        if user_id not in users_db:
            raise HTTPException(status_code=401, detail="User not found")
        
        return users_db[user_id]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Endpoints
@app.post("/register", response_model=User)
async def register(user: UserRegister):
    """Register new user"""
    # Check if email exists
    if any(u["email"] == user.email for u in users_db.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = len(users_db) + 1
    hashed_password = pwd_context.hash(user.password)
    
    users_db[user_id] = {
        "id": user_id,
        "email": user.email,
        "username": user.username,
        "password": hashed_password
    }
    
    return User(id=user_id, email=user.email, username=user.username)

@app.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login and get JWT token"""
    # Find user
    user = next(
        (u for u in users_db.values() if u["email"] == credentials.email),
        None
    )
    
    if not user or not pwd_context.verify(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    token = create_token(user["id"], user["email"])
    return Token(access_token=token)

@app.get("/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return User(**{k: v for k, v in current_user.items() if k != "password"})

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    """Protected endpoint - requires authentication"""
    return {"message": f"Hello {current_user['username']}!"}

# Test flow:
# 1. POST /register with {"email": "test@example.com", "username": "testuser", "password": "secure123"}
# 2. POST /login with {"email": "test@example.com", "password": "secure123"}
# 3. Copy the access_token from response
# 4. GET /me with Authorization: Bearer <access_token>
```

---

## 🎓 Key Takeaways

1. **Never Store Plain Passwords**: Always use bcrypt or similar
2. **JWT for Stateless Auth**: Tokens contain user info, no session storage needed
3. **Dependency Injection**: Elegant way to protect endpoints
4. **HTTP Bearer Tokens**: Standard way to send JWT tokens
5. **Middleware**: Process all requests/responses in one place
6. **CORS**: Required for frontend-backend communication
7. **Role-Based Access**: Control what users can do

---

## 📖 What's Next?

In **Part 4: Async Programming**, you'll learn:
- async/await fundamentals
- asyncio.gather for concurrent operations
- Background tasks
- Thread pools for blocking operations
- Real async patterns from your project

---

## 🔗 Resources

- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io - Token Debugger](https://jwt.io/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Python-JOSE Documentation](https://python-jose.readthedocs.io/)
