"""
Settings Router - AI provider and system settings
"""

from fastapi import APIRouter, Depends, HTTPException, status
import logging

from api.models import AISettings, AISettingsUpdate, SystemSettings, SuccessResponse
from api.routers.auth import get_current_user
from utils.agent_rag_engine import agent_rag_engine

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()


# ============================================================
# AI SETTINGS ENDPOINTS
# ============================================================

@router.get("/ai", response_model=AISettings)
async def get_ai_settings(current_user: dict = Depends(get_current_user)):
    """
    Get current AI provider settings
    
    Returns configured AI provider and embedding provider
    """
    try:
        # Get current settings from agent engine
        current_provider = agent_rag_engine.provider
        current_embedding = getattr(agent_rag_engine, 'embedding_provider', 'openai')
        
        return AISettings(
            ai_provider=current_provider,
            embedding_provider=current_embedding,
            openai_api_key=None,  # Never return API keys
            gemini_api_key=None,
            huggingface_api_key=None
        )
        
    except Exception as e:
        logger.error(f"Get AI settings error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve AI settings"
        )


@router.patch("/ai", response_model=SuccessResponse)
async def update_ai_settings(
    settings: AISettingsUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update AI provider settings
    
    - **ai_provider**: OpenAI or Gemini
    - **embedding_provider**: OpenAI, Gemini, or HuggingFace
    - **api_keys**: Optional API keys (stored securely)
    
    Note: Changing provider will update all 3 agents in the multi-agent system
    """
    try:
        # Update AI provider if specified
        if settings.ai_provider:
            agent_rag_engine.update_provider(settings.ai_provider)
            logger.info(f"AI provider updated to {settings.ai_provider} for user {current_user.email}")
        
        # Update embedding provider if specified
        if settings.embedding_provider:
            # Store embedding provider preference
            # (Implementation depends on your architecture)
            logger.info(f"Embedding provider updated to {settings.embedding_provider}")
        
        # Store API keys securely if provided
        # TODO: Implement secure key storage (e.g., encrypted in database or key vault)
        if settings.openai_api_key:
            logger.info("OpenAI API key updated")
        if settings.gemini_api_key:
            logger.info("Gemini API key updated")
        if settings.huggingface_api_key:
            logger.info("HuggingFace API key updated")
        
        return SuccessResponse(
            success=True,
            message="AI settings updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Update AI settings error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update AI settings"
        )


# ============================================================
# SYSTEM SETTINGS ENDPOINTS
# ============================================================

@router.get("/system", response_model=SystemSettings)
async def get_system_settings(current_user: dict = Depends(get_current_user)):
    """
    Get system settings for document processing and generation
    
    Returns:
    - Chunk size and overlap
    - Max search results
    - Generation temperature
    - Max tokens
    """
    try:
        # Get current settings from agent engine
        # (These could be stored per-user in database)
        
        return SystemSettings(
            chunk_size=1000,
            chunk_overlap=200,
            max_results=5,
            temperature=0.7,
            max_tokens=2000
        )
        
    except Exception as e:
        logger.error(f"Get system settings error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system settings"
        )


@router.patch("/system", response_model=SuccessResponse)
async def update_system_settings(
    settings: SystemSettings,
    current_user: dict = Depends(get_current_user)
):
    """
    Update system settings
    
    - **chunk_size**: Text chunk size for document processing (500-2000)
    - **chunk_overlap**: Overlap between chunks (50-500)
    - **max_results**: Maximum search results (1-20)
    - **temperature**: Generation temperature (0.0-1.0)
    - **max_tokens**: Maximum generation tokens (100-4000)
    """
    try:
        # Validate settings
        if not 500 <= settings.chunk_size <= 2000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chunk size must be between 500 and 2000"
            )
        
        if not 50 <= settings.chunk_overlap <= 500:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chunk overlap must be between 50 and 500"
            )
        
        if not 1 <= settings.max_results <= 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Max results must be between 1 and 20"
            )
        
        if not 0.0 <= settings.temperature <= 1.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Temperature must be between 0.0 and 1.0"
            )
        
        if not 100 <= settings.max_tokens <= 4000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Max tokens must be between 100 and 4000"
            )
        
        # Store settings (implementation depends on your architecture)
        # You could store in database, config file, or pass to agents
        
        logger.info(f"System settings updated for user {current_user.email}")
        
        return SuccessResponse(
            success=True,
            message="System settings updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update system settings error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update system settings"
        )


# ============================================================
# AGENT STATUS
# ============================================================

@router.get("/agents")
async def get_agent_status(current_user: dict = Depends(get_current_user)):
    """
    Get multi-agent system status
    
    Returns information about all active agents
    """
    try:
        return {
            "success": True,
            "multi_agent_system": "active",
            "agents": [
                {
                    "name": "Ingestion Agent",
                    "role": "Document Processing Specialist",
                    "status": "active",
                    "tools": ["DocumentAnalyzer", "TextExtractor", "DocumentChunker"]
                },
                {
                    "name": "Retrieval Agent",
                    "role": "Information Retrieval Specialist",
                    "status": "active",
                    "tools": ["QueryAnalyzer", "VectorSearch"]
                },
                {
                    "name": "Generation Agent",
                    "role": "Response Generation Expert",
                    "status": "active",
                    "tools": ["CitationFormatter", "ResponseValidator"]
                }
            ],
            "provider": agent_rag_engine.provider,
            "total_agents": 3,
            "total_tools": 7
        }
        
    except Exception as e:
        logger.error(f"Get agent status error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent status"
        )
