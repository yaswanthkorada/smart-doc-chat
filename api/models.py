"""
Pydantic Models for Request/Response Validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================
# ENUMS
# ============================================================

class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class AIProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"


class EmbeddingProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    HUGGINGFACE = "huggingface"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


# ============================================================
# AUTH MODELS
# ============================================================

class UserSignup(BaseModel):
    """User signup request"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores allowed)')
        return v


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    email: str


# ============================================================
# USER MODELS
# ============================================================

class UserProfile(BaseModel):
    """User profile response"""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    subscription_tier: SubscriptionTier
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User profile update request"""
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(..., min_length=8)


# ============================================================
# DOCUMENT MODELS
# ============================================================

class DocumentUploadResponse(BaseModel):
    """Document upload response"""
    success: bool
    document_id: str
    filename: str
    file_type: str
    file_size: int
    page_count: Optional[int]
    vector_count: int
    message: str


class DocumentInfo(BaseModel):
    """Document information"""
    id: str
    document_id: str
    filename: str
    file_type: str
    file_size: int
    uploaded_at: datetime
    is_indexed: bool
    page_count: Optional[int]
    vector_count: Optional[int]
    
    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    """List of documents"""
    documents: List[DocumentInfo]
    total_count: int
    total_size: int


class DocumentDelete(BaseModel):
    """Document deletion response"""
    success: bool
    message: str
    document_id: str


# ============================================================
# CHAT MODELS
# ============================================================

class ChatQuery(BaseModel):
    """Chat query request"""
    question: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    stream: bool = False


class SourceInfo(BaseModel):
    """Source citation information"""
    filename: str
    page: Optional[int]
    chunk_index: Optional[int]
    relevance_score: Optional[float]


class ChatResponse(BaseModel):
    """Chat response"""
    success: bool
    response: str
    sources: List[SourceInfo]
    conversation_id: str
    message_id: str
    tokens_used: Optional[int]
    response_time: Optional[float]
    agents_used: List[str] = []


class Message(BaseModel):
    """Chat message"""
    message_id: str
    role: MessageRole
    content: str
    timestamp: datetime
    sources: Optional[List[SourceInfo]] = None
    tokens_used: Optional[int] = 0
    
    class Config:
        from_attributes = True


class Conversation(BaseModel):
    """Conversation thread"""
    conversation_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    is_pinned: bool
    
    class Config:
        from_attributes = True


class ConversationList(BaseModel):
    """List of conversations"""
    conversations: List[Conversation]
    total_count: int


class ConversationMessages(BaseModel):
    """Conversation with messages"""
    conversation: Conversation
    messages: List[Message]


class ConversationCreate(BaseModel):
    """Create new conversation"""
    title: Optional[str] = "New Conversation"


class ConversationUpdate(BaseModel):
    """Update conversation"""
    title: Optional[str] = None
    is_pinned: Optional[bool] = None


# ============================================================
# SETTINGS MODELS
# ============================================================

class AISettings(BaseModel):
    """AI provider settings"""
    ai_provider: AIProvider
    embedding_provider: EmbeddingProvider
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None


class AISettingsUpdate(BaseModel):
    """Update AI settings"""
    ai_provider: Optional[AIProvider] = None
    embedding_provider: Optional[EmbeddingProvider] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None


class SystemSettings(BaseModel):
    """System settings"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_results: int = 5
    temperature: float = 0.7
    max_tokens: int = 2000


# ============================================================
# ANALYTICS MODELS
# ============================================================

class UsageStats(BaseModel):
    """User usage statistics"""
    total_documents: int
    total_conversations: int
    total_messages: int
    total_tokens_used: int
    storage_used: int  # bytes
    queries_today: int
    queries_this_month: int


class QueryAnalytics(BaseModel):
    """Query analytics"""
    query_id: str
    query_text: str
    response_time: float
    tokens_used: int
    documents_searched: List[str]
    timestamp: datetime
    success: bool


# ============================================================
# GENERIC MODELS
# ============================================================

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
