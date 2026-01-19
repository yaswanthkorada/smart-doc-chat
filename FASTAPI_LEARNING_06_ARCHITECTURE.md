# FastAPI Learning Guide - Part 6: Real-World Architecture & Best Practices

## 🎯 Learning Objectives
After this guide, you'll master:
- Professional project structure
- Configuration management
- Database integration patterns
- Dependency injection advanced patterns
- Testing strategies
- Performance optimization
- Production deployment considerations

---

## 📁 1. Project Structure

### Your Project's Structure Explained:

```
smart-doc-chat/
│
├── api/                          # FastAPI application
│   ├── __init__.py
│   ├── main.py                   # App initialization, middleware, routers
│   ├── models.py                 # Pydantic models (request/response)
│   │
│   └── routers/                  # Endpoint routers (organized by domain)
│       ├── __init__.py
│       ├── auth.py              # Authentication endpoints
│       ├── chat.py              # Chat/query endpoints
│       ├── documents.py         # Document management
│       ├── settings.py          # User settings
│       └── users.py             # User management
│
├── config/                       # Configuration
│   ├── __init__.py
│   └── settings.py              # App settings, environment variables
│
├── utils/                        # Utility modules
│   ├── __init__.py
│   ├── agent_rag_engine.py      # Multi-agent system
│   ├── agent_tools.py           # Agent tools
│   ├── database.py              # Database manager
│   ├── rag_engine.py            # RAG engine
│   ├── storage.py               # File storage
│   └── supabase_client.py       # Supabase client
│
├── components/                   # Streamlit components (if applicable)
├── data/                         # Data storage
├── logs/                         # Application logs
├── temp/                         # Temporary files
│
├── requirements.txt              # Python dependencies
├── run_api.py                   # API entry point
└── README.md                    # Documentation
```

### 🔍 Why This Structure?

1. **Separation of Concerns**: Each directory has a specific purpose
2. **Scalability**: Easy to add new routers, utilities, or services
3. **Maintainability**: Clear organization makes code easier to find
4. **Testability**: Each module can be tested independently
5. **Team Collaboration**: Multiple developers can work without conflicts

---

## ⚙️ 2. Configuration Management

### Example from Your Project: [config/settings.py](config/settings.py)

```python
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Application settings from environment variables
    """
    # App settings
    app_name: str = "Smart Document Chat"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Security
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # Database
    database_url: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    # AI Providers
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # Storage
    upload_dir: str = "uploads"
    max_upload_size: int = 50 * 1024 * 1024  # 50 MB
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:8501"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Create global settings instance
settings = Settings()
```

### Using Settings in Your App:

```python
# api/main.py
from config.settings import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# CORS with configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# In endpoints
@app.get("/config")
async def get_config():
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug
    }
```

### Environment Variables (.env file):

```bash
# .env file (never commit to git!)
APP_NAME=Smart Document Chat
DEBUG=false

# Security
JWT_SECRET_KEY=your-super-secret-key-here-change-in-production

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# AI APIs
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Storage
UPLOAD_DIR=/var/app/uploads
MAX_UPLOAD_SIZE=104857600

# CORS
CORS_ORIGINS=["https://your-frontend.com","https://app.your-frontend.com"]
```

### Different Configs for Different Environments:

```python
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    environment: Environment = Environment.DEVELOPMENT
    
    # Database URLs by environment
    @property
    def database_url(self) -> str:
        urls = {
            Environment.DEVELOPMENT: "postgresql://localhost/dev_db",
            Environment.STAGING: "postgresql://staging-db/staging_db",
            Environment.PRODUCTION: "postgresql://prod-db/prod_db"
        }
        return os.getenv("DATABASE_URL") or urls[self.environment]
    
    # Debug only in development
    @property
    def debug(self) -> bool:
        return self.environment == Environment.DEVELOPMENT
    
    class Config:
        env_file = f".env.{os.getenv('ENVIRONMENT', 'development')}"

# Load different .env files:
# .env.development
# .env.staging
# .env.production
```

---

## 🗄️ 3. Database Integration Patterns

### Database Manager Pattern: [utils/database.py](utils/database.py)

```python
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Centralized database operations
    """
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._connection = None
    
    def connect(self):
        """Initialize database connection"""
        # Initialize connection pool
        logger.info("Database connected")
    
    def disconnect(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            logger.info("Database disconnected")
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._connection is not None
    
    # User operations
    def create_user(self, email: str, username: str, password: str):
        """Create new user"""
        pass
    
    def get_user_by_id(self, user_id: str):
        """Get user by ID"""
        pass
    
    def get_user_by_email(self, email: str):
        """Get user by email"""
        pass
    
    # Document operations
    def create_document(self, user_id: str, filename: str, **kwargs):
        """Create document record"""
        pass
    
    def get_user_documents(self, user_id: str):
        """Get all user's documents"""
        pass
    
    # Conversation operations
    def create_conversation(self, user_id: str, title: str):
        """Create conversation"""
        pass
    
    def get_user_conversations(self, user_id: str):
        """Get user's conversations"""
        pass

# Global instance
db_manager = DatabaseManager(settings.database_url)
```

### Using Database Manager in Endpoints:

```python
from utils.database import db_manager

@router.get("/users/{user_id}")
async def get_user(user_id: str):
    """
    Get user from database
    """
    user = db_manager.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
```

### Async Database with SQLAlchemy:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Create async engine
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    echo=True,
    future=True
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Dependency for database sessions
async def get_db() -> AsyncSession:
    """
    Database session dependency
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Usage in endpoints
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user with dependency injection
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
```

---

## 💉 4. Advanced Dependency Injection

### Dependency Chain:

```python
from fastapi import Depends, HTTPException, Header
from typing import Optional

# Level 1: Basic dependency
async def get_db_session():
    """Database session"""
    session = await create_db_session()
    try:
        yield session
    finally:
        await session.close()

# Level 2: Depends on Level 1
async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db_session)
):
    """Current user from token"""
    token = authorization.replace("Bearer ", "")
    user_id = decode_token(token)
    
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401)
    
    return user

# Level 3: Depends on Level 2
async def get_current_active_user(
    user: User = Depends(get_current_user)
):
    """Verify user is active"""
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")
    
    return user

# Level 4: Depends on Level 3
async def require_admin(
    user: User = Depends(get_current_active_user)
):
    """Verify user is admin"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user

# Usage
@app.get("/admin/users")
async def list_all_users(
    admin: User = Depends(require_admin),  # Full chain executed
    db: AsyncSession = Depends(get_db_session)
):
    """Only admins can list all users"""
    users = await db.execute(select(User))
    return users.scalars().all()
```

### Dependency with Parameters:

```python
from typing import Optional

class Pagination:
    """
    Reusable pagination dependency
    """
    def __init__(
        self,
        page: int = 1,
        limit: int = 10,
        max_limit: int = 100
    ):
        self.page = max(1, page)
        self.limit = min(limit, max_limit)
        self.offset = (self.page - 1) * self.limit

def pagination_params(
    page: int = 1,
    limit: int = 10
) -> Pagination:
    """
    Pagination dependency factory
    """
    return Pagination(page=page, limit=limit)

@app.get("/posts")
async def list_posts(
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List posts with pagination
    URL: /posts?page=2&limit=20
    """
    query = select(Post).offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    posts = result.scalars().all()
    
    return {
        "page": pagination.page,
        "limit": pagination.limit,
        "posts": posts
    }
```

### Cached Dependencies:

```python
from functools import lru_cache

@lru_cache()
def get_settings() -> Settings:
    """
    Settings dependency (cached)
    Only created once, reused for all requests
    """
    return Settings()

@app.get("/config")
async def get_config(settings: Settings = Depends(get_settings)):
    """
    Same settings instance used for all requests
    """
    return {
        "app_name": settings.app_name,
        "version": settings.app_version
    }
```

---

## 🧪 5. Testing Strategies

### Test Client Setup:

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from utils.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def client():
    """
    Test client fixture
    """
    # Create test database
    Base.metadata.create_all(bind=engine)
    
    # Override database dependency
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    with TestClient(app) as client:
        yield client
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
```

### Testing Endpoints:

```python
# tests/test_auth.py
def test_signup(client):
    """Test user signup"""
    response = client.post("/api/auth/signup", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "securepass123"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"

def test_login(client):
    """Test user login"""
    # First create user
    client.post("/api/auth/signup", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "securepass123"
    })
    
    # Then login
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "securepass123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_protected_endpoint(client):
    """Test protected endpoint requires auth"""
    # Without token
    response = client.get("/api/users/me")
    assert response.status_code == 401
    
    # With token
    # First login
    login_response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "securepass123"
    })
    token = login_response.json()["access_token"]
    
    # Request with token
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

### Testing with Mocks:

```python
# tests/test_chat.py
from unittest.mock import patch, MagicMock

def test_chat_query(client):
    """Test chat query with mocked AI response"""
    
    # Mock the agent engine
    with patch('api.routers.chat.agent_rag_engine') as mock_agent:
        # Setup mock return value
        mock_agent.query.return_value = {
            'success': True,
            'response': 'Test response',
            'sources': [],
            'tokens': 100
        }
        
        # Make request
        response = client.post(
            "/api/chat/query",
            json={"question": "What is FastAPI?"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Test response"
        assert data["tokens_used"] == 100
        
        # Verify mock was called
        mock_agent.query.assert_called_once()
```

---

## ⚡ 6. Performance Optimization

### Database Query Optimization:

```python
# ❌ BAD - N+1 Query Problem
@app.get("/posts")
async def get_posts(db: AsyncSession = Depends(get_db)):
    posts = await db.execute(select(Post))
    
    result = []
    for post in posts.scalars():
        # Each iteration makes a database query!
        author = await db.get(User, post.author_id)
        result.append({
            "post": post,
            "author": author
        })
    
    return result  # 1 query + N queries = Slow!

# ✅ GOOD - Eager Loading
@app.get("/posts")
async def get_posts(db: AsyncSession = Depends(get_db)):
    # Load posts with authors in single query
    result = await db.execute(
        select(Post).options(selectinload(Post.author))
    )
    posts = result.scalars().all()
    
    return posts  # 1-2 queries total = Fast!
```

### Response Caching:

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

# Initialize cache
@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

# Cache endpoint response
@app.get("/stats")
@cache(expire=60)  # Cache for 60 seconds
async def get_stats():
    """
    Expensive operation cached for 1 minute
    """
    stats = await calculate_expensive_stats()
    return stats
```

### Database Connection Pooling:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=20,           # Number of permanent connections
    max_overflow=10,        # Additional connections when pool is full
    pool_timeout=30,        # Seconds to wait for connection
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True      # Verify connections before using
)
```

### Async I/O for External APIs:

```python
import asyncio
import httpx

# ❌ BAD - Sequential requests
async def get_data_sequential():
    async with httpx.AsyncClient() as client:
        data1 = await client.get("https://api1.com/data")
        data2 = await client.get("https://api2.com/data")
        data3 = await client.get("https://api3.com/data")
    
    return [data1, data2, data3]  # Total: 3 seconds

# ✅ GOOD - Concurrent requests
async def get_data_concurrent():
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            client.get("https://api1.com/data"),
            client.get("https://api2.com/data"),
            client.get("https://api3.com/data")
        )
    
    return results  # Total: 1 second (3x faster!)
```

---

## 🚀 7. Production Deployment

### Running with Uvicorn:

```python
# run_api.py
import uvicorn
from api.main import app

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,              # Multiple worker processes
        reload=False,           # Disable in production
        log_level="info",
        access_log=True
    )
```

### Docker Deployment:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Environment-Specific Settings:

```python
# Production settings
if settings.environment == "production":
    # Strict CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,  # No "*"
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"]
    )
    
    # Security headers
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response
```

---

## 🎓 Key Takeaways

1. **Project Structure**: Organize by domain (routers) and purpose (utils, config)
2. **Configuration**: Use Pydantic Settings for environment variables
3. **Database**: Centralize database operations in manager/repository pattern
4. **Dependencies**: Use dependency injection for reusable logic
5. **Testing**: Write tests for critical endpoints and logic
6. **Performance**: Cache responses, use connection pools, async I/O
7. **Production**: Multiple workers, proper CORS, security headers

---

## 📖 Additional Learning Resources

### Next Steps to Master FastAPI:

1. **Build More Projects**: Practice is key!
2. **Read Source Code**: Study well-architected FastAPI projects on GitHub
3. **Performance Testing**: Use tools like `locust` or `k6`
4. **Monitoring**: Add tools like Prometheus, Grafana
5. **API Documentation**: Customize OpenAPI schema
6. **GraphQL**: Try FastAPI with Strawberry or Graphene
7. **gRPC**: Explore FastAPI with gRPC

### Recommended Projects to Build:

1. **E-commerce API**: Products, orders, payments, inventory
2. **Social Media API**: Posts, comments, likes, follows, feed
3. **Task Management API**: Projects, tasks, subtasks, assignments
4. **Analytics API**: Events tracking, reporting, dashboards
5. **File Storage API**: Upload, download, sharing, permissions

---

## 🔗 Official Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [FastAPI GitHub](https://github.com/tiangolo/fastapi)

---

## 🎉 Congratulations!

You've completed the FastAPI learning guide! You now have comprehensive knowledge of:

✅ FastAPI fundamentals and routing  
✅ Pydantic models and validation  
✅ Authentication and security  
✅ Async programming patterns  
✅ Advanced features (SSE, file uploads, WebSockets)  
✅ Production-ready architecture  

**Keep building and learning! 🚀**
