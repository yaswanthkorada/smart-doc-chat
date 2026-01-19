"""
FastAPI Main Application
Complete REST API for Smart Document Chat with Multi-Agent System
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import time
import logging
from contextlib import asynccontextmanager

# Import routers
from api.routers import auth, documents, chat, users, settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    logger.info("🚀 Starting FastAPI Server...")
    logger.info("🤖 Multi-Agent RAG System Ready")
    logger.info("📊 Database connections initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down FastAPI Server...")


# Initialize FastAPI app
app = FastAPI(
    title="Smart Document Chat API",
    description="Multi-Agent RAG System with Document Processing and Conversational AI",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)


# ============================================================
# MIDDLEWARE CONFIGURATION
# ============================================================

# CORS - Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default
        "http://localhost:5173",  # Vite default
        "http://localhost:8501",  # Streamlit default
        "http://localhost:8080",
        "*"  # Allow all in development (restrict in production!)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# GZip compression for responses
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add response time header to all requests"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc)
        }
    )


# ============================================================
# ROUTERS
# ============================================================

# Include all API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])


# ============================================================
# ROOT ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Smart Document Chat API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/api/docs",
        "features": {
            "multi_agent_system": True,
            "document_processing": True,
            "conversational_ai": True,
            "vector_search": True,
            "jwt_authentication": True
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from utils.database import db_manager
    
    db_status = "connected" if db_manager.is_connected() else "disconnected"
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "database": db_status,
        "multi_agent_system": "active"
    }


@app.get("/api")
async def api_info():
    """API information"""
    return {
        "name": "Smart Document Chat API",
        "version": "2.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "users": "/api/users",
            "documents": "/api/documents",
            "chat": "/api/chat",
            "settings": "/api/settings"
        },
        "documentation": {
            "swagger": "/api/docs",
            "redoc": "/api/redoc"
        }
    }


# ============================================================
# STARTUP MESSAGE
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 Smart Document Chat API Server")
    print("="*60)
    print("📖 API Docs: http://localhost:8000/api/docs")
    print("🔍 ReDoc: http://localhost:8000/api/redoc")
    print("🤖 Multi-Agent System: ACTIVE")
    print("="*60 + "\n")
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
