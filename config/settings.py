import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Try to import streamlit for secrets (if running on Streamlit Cloud)
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

def get_config_value(key: str, default=None, secrets_key: str = None):
    """Get config value from Streamlit secrets, environment, or default"""
    # Priority: Streamlit secrets > Environment variables > Default
    if STREAMLIT_AVAILABLE:
        try:
            # Try to get from Streamlit secrets
            if secrets_key:
                # For nested keys like api_keys.GOOGLE_API_KEY
                parts = secrets_key.split('.')
                value = st.secrets
                for part in parts:
                    value = value.get(part)
                    if value is None:
                        break
                if value is not None:
                    return value
            
            # Try direct key
            if key in st.secrets:
                return st.secrets[key]
        except:
            pass
    
    # Fallback to environment variable
    return os.getenv(key, default)

class Config:
    """Application Configuration"""
    
    # Application
    APP_NAME = get_config_value("APP_NAME", "RAG Assistant")
    APP_ENV = get_config_value("APP_ENV", "development")
    SECRET_KEY = get_config_value("SECRET_KEY", "dev-secret-key")
    DEBUG = get_config_value("DEBUG", "True").lower() == "true"
    
    # AI Provider
    AI_PROVIDER = get_config_value("AI_PROVIDER", "openai")
    EMBEDDING_PROVIDER = get_config_value("EMBEDDING_PROVIDER", "openai")
    HUGGINGFACE_MODEL = get_config_value("HUGGINGFACE_MODEL", "sentence-transformers/all-mpnet-base-v2")
    
    # OpenAI - Try both direct and nested secrets
    OPENAI_API_KEY = get_config_value("OPENAI_API_KEY", secrets_key="api_keys.OPENAI_API_KEY")
    OPENAI_MODEL = get_config_value("OPENAI_MODEL", "gpt-5-nano")
    OPENAI_EMBEDDING_MODEL = get_config_value("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Google Gemini - Try both direct and nested secrets
    GEMINI_API_KEY = get_config_value("GEMINI_API_KEY", secrets_key="api_keys.GOOGLE_API_KEY")
    GEMINI_MODEL = get_config_value("GEMINI_MODEL", "gemini-2.0-flash-exp")
    GEMINI_EMBEDDING_MODEL = get_config_value("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
    
    # Supabase
    SUPABASE_URL = get_config_value("SUPABASE_URL", secrets_key="supabase.url")
    SUPABASE_KEY = get_config_value("SUPABASE_KEY", secrets_key="supabase.key")
    SUPABASE_SERVICE_KEY = get_config_value("SUPABASE_SERVICE_KEY", secrets_key="supabase.service_role_key")
    SUPABASE_PROJECT_ID = get_config_value("SUPABASE_PROJECT_ID", secrets_key="supabase.project_id")
    SUPABASE_BUCKET = get_config_value("SUPABASE_BUCKET", "documents", secrets_key="supabase.bucket")
    SUPABASE_DB_PASSWORD = get_config_value("SUPABASE_DB_PASSWORD", secrets_key="supabase.db_password")
    
    # Database - Try multiple sources
    DATABASE_URL = get_config_value("DATABASE_URL", secrets_key="database.connection_string")
    
    # If DATABASE_URL not set, try to construct from Supabase credentials
    if not DATABASE_URL and SUPABASE_URL and SUPABASE_DB_PASSWORD:
        # Extract project ref from Supabase URL (format: https://xxxxx.supabase.co)
        try:
            if SUPABASE_URL:
                project_ref = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
                # Construct PostgreSQL connection string
                # Format: postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
                DATABASE_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@db.{project_ref}.supabase.co:5432/postgres"
        except Exception as e:
            pass
    
    # Fallback to SQLite for local development
    if not DATABASE_URL:
        DATABASE_URL = "sqlite:///./data/rag_app.db"
    
    # Vector Database
    VECTOR_DB_TYPE = get_config_value("VECTOR_DB_TYPE", "chromadb")
    CHROMA_PERSIST_DIR = get_config_value("CHROMA_PERSIST_DIR", "./data/chroma_data")
    
    # Pinecone
    PINECONE_API_KEY = get_config_value("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = get_config_value("PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME = get_config_value("PINECONE_INDEX_NAME")
    
    # Qdrant
    QDRANT_URL = get_config_value("QDRANT_URL")
    QDRANT_API_KEY = get_config_value("QDRANT_API_KEY")
    
    # File Storage
    STORAGE_TYPE = get_config_value("STORAGE_TYPE", "supabase")
    LOCAL_STORAGE_PATH = get_config_value("LOCAL_STORAGE_PATH", "./data/user_files")
    
    # AWS S3
    AWS_ACCESS_KEY_ID = get_config_value("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = get_config_value("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = get_config_value("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME = get_config_value("S3_BUCKET_NAME")
    
    # Cloudflare R2
    R2_ACCOUNT_ID = get_config_value("R2_ACCOUNT_ID")
    R2_ACCESS_KEY_ID = get_config_value("R2_ACCESS_KEY_ID")
    R2_SECRET_ACCESS_KEY = get_config_value("R2_SECRET_ACCESS_KEY")
    R2_BUCKET_NAME = get_config_value("R2_BUCKET_NAME")
    R2_ENDPOINT = get_config_value("R2_ENDPOINT")
    
    # Azure Blob Storage
    AZURE_STORAGE_CONNECTION_STRING = get_config_value("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_CONTAINER_NAME = get_config_value("AZURE_CONTAINER_NAME")
    
    # Google Cloud Storage
    GCS_BUCKET_NAME = get_config_value("GCS_BUCKET_NAME")
    GOOGLE_APPLICATION_CREDENTIALS = get_config_value("GOOGLE_APPLICATION_CREDENTIALS")
    
    # File Upload
    MAX_FILE_SIZE_MB = int(get_config_value("MAX_FILE_SIZE_MB", "100"))
    MAX_FILES_PER_UPLOAD = int(get_config_value("MAX_FILES_PER_UPLOAD", "10"))
    ALLOWED_FILE_TYPES = get_config_value("ALLOWED_FILE_TYPES", "pdf,docx,txt,pptx,xlsx,csv").split(",")
    
    # Subscription Tiers
    FREE_MAX_DOCUMENTS = int(get_config_value("FREE_MAX_DOCUMENTS", "10"))
    FREE_MAX_STORAGE_MB = int(get_config_value("FREE_MAX_STORAGE_MB", "100"))
    FREE_MAX_CONVERSATIONS = int(get_config_value("FREE_MAX_CONVERSATIONS", "50"))
    
    PRO_MAX_DOCUMENTS = int(get_config_value("PRO_MAX_DOCUMENTS", "1000"))
    PRO_MAX_STORAGE_MB = int(get_config_value("PRO_MAX_STORAGE_MB", "10240"))
    PRO_MAX_CONVERSATIONS = int(get_config_value("PRO_MAX_CONVERSATIONS", "1000"))
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = get_config_value("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_REQUESTS_PER_MINUTE = int(get_config_value("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))
    
    # Redis
    REDIS_ENABLED = get_config_value("REDIS_ENABLED", "False").lower() == "true"
    REDIS_URL = get_config_value("REDIS_URL", "redis://localhost:6379/0")
    
    # Email
    SMTP_ENABLED = get_config_value("SMTP_ENABLED", "False").lower() == "true"
    SMTP_HOST = get_config_value("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(get_config_value("SMTP_PORT", "587"))
    SMTP_USERNAME = get_config_value("SMTP_USERNAME")
    SMTP_PASSWORD = get_config_value("SMTP_PASSWORD")
    SMTP_FROM_EMAIL = get_config_value("SMTP_FROM_EMAIL")
    
    # Analytics
    GOOGLE_ANALYTICS_ID = get_config_value("GOOGLE_ANALYTICS_ID")
    POSTHOG_API_KEY = get_config_value("POSTHOG_API_KEY")
    
    # Logging
    LOG_LEVEL = get_config_value("LOG_LEVEL", "INFO")
    LOG_FILE = get_config_value("LOG_FILE", "./logs/app.log")
    
    # Celery
    CELERY_BROKER_URL = get_config_value("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = get_config_value("CELERY_RESULT_BACKEND")
    
    # Security
    JWT_SECRET_KEY = get_config_value("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ALGORITHM = get_config_value("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS = int(get_config_value("JWT_EXPIRATION_HOURS", "24"))
    
    MIN_PASSWORD_LENGTH = int(get_config_value("MIN_PASSWORD_LENGTH", "8"))
    REQUIRE_UPPERCASE = get_config_value("REQUIRE_UPPERCASE", "True").lower() == "true"
    REQUIRE_LOWERCASE = get_config_value("REQUIRE_LOWERCASE", "True").lower() == "true"
    REQUIRE_NUMBERS = get_config_value("REQUIRE_NUMBERS", "True").lower() == "true"
    REQUIRE_SPECIAL_CHARS = get_config_value("REQUIRE_SPECIAL_CHARS", "False").lower() == "true"
    
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
