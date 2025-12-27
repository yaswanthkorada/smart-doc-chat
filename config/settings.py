import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Application Configuration"""
    
    # Application
    APP_NAME = os.getenv("APP_NAME", "RAG Assistant")
    APP_ENV = os.getenv("APP_ENV", "development")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # AI Provider
    AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")  # openai or gemini
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "huggingface")  # huggingface, openai, or gemini
    HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "sentence-transformers/all-mpnet-base-v2")
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
    
    # Google Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/rag_app.db")
    
    # Vector Database
    VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chromadb")
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_data")
    
    # Pinecone
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
    
    # Qdrant
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    
    # File Storage
    STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local")
    LOCAL_STORAGE_PATH = os.getenv("LOCAL_STORAGE_PATH", "./data/user_files")
    
    # AWS S3
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    
    # Cloudflare R2
    R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
    R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
    R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
    R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
    R2_ENDPOINT = os.getenv("R2_ENDPOINT")
    
    # Azure Blob Storage
    AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")
    
    # Google Cloud Storage
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # File Upload
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 100))
    MAX_FILES_PER_UPLOAD = int(os.getenv("MAX_FILES_PER_UPLOAD", 10))
    ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "pdf,docx,txt,pptx,xlsx,csv").split(",")
    
    # Subscription Tiers
    FREE_MAX_DOCUMENTS = int(os.getenv("FREE_MAX_DOCUMENTS", 10))
    FREE_MAX_STORAGE_MB = int(os.getenv("FREE_MAX_STORAGE_MB", 100))
    FREE_MAX_CONVERSATIONS = int(os.getenv("FREE_MAX_CONVERSATIONS", 50))
    
    PRO_MAX_DOCUMENTS = int(os.getenv("PRO_MAX_DOCUMENTS", 1000))
    PRO_MAX_STORAGE_MB = int(os.getenv("PRO_MAX_STORAGE_MB", 10240))
    PRO_MAX_CONVERSATIONS = int(os.getenv("PRO_MAX_CONVERSATIONS", 1000))
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", 60))
    
    # Redis
    REDIS_ENABLED = os.getenv("REDIS_ENABLED", "False").lower() == "true"
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Email
    SMTP_ENABLED = os.getenv("SMTP_ENABLED", "False").lower() == "true"
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")
    
    # Analytics
    GOOGLE_ANALYTICS_ID = os.getenv("GOOGLE_ANALYTICS_ID")
    POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "./logs/app.log")
    
    # Celery
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
    
    # Security
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 24))
    
    MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", 8))
    REQUIRE_UPPERCASE = os.getenv("REQUIRE_UPPERCASE", "True").lower() == "true"
    REQUIRE_LOWERCASE = os.getenv("REQUIRE_LOWERCASE", "True").lower() == "true"
    REQUIRE_NUMBERS = os.getenv("REQUIRE_NUMBERS", "True").lower() == "true"
    REQUIRE_SPECIAL_CHARS = os.getenv("REQUIRE_SPECIAL_CHARS", "False").lower() == "true"
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration"""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")
        
        if cls.STORAGE_TYPE == "s3" and not all([cls.AWS_ACCESS_KEY_ID, cls.AWS_SECRET_ACCESS_KEY, cls.S3_BUCKET_NAME]):
            errors.append("S3 configuration incomplete")
        
        if cls.VECTOR_DB_TYPE == "pinecone" and not all([cls.PINECONE_API_KEY, cls.PINECONE_ENVIRONMENT]):
            errors.append("Pinecone configuration incomplete")
        
        return errors
    
    @classmethod
    def get_tier_limits(cls, tier: str):
        """Get limits for subscription tier"""
        tier = tier.lower()
        
        if tier == "free":
            return {
                "max_documents": cls.FREE_MAX_DOCUMENTS,
                "max_storage_mb": cls.FREE_MAX_STORAGE_MB,
                "max_conversations": cls.FREE_MAX_CONVERSATIONS
            }
        elif tier == "pro":
            return {
                "max_documents": cls.PRO_MAX_DOCUMENTS,
                "max_storage_mb": cls.PRO_MAX_STORAGE_MB,
                "max_conversations": cls.PRO_MAX_CONVERSATIONS
            }
        else:  # enterprise
            return {
                "max_documents": float('inf'),
                "max_storage_mb": float('inf'),
                "max_conversations": float('inf')
            }

# Create necessary directories
def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        "data",
        "data/user_files",
        "data/chroma_data",
        "logs",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

# Initialize
create_directories()

# Export config instance
config = Config()
