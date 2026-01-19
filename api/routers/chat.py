"""
Chat Router - Multi-Agent conversational AI endpoints
Handles queries with Retrieval and Generation agents
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging
import time
import json

from api.models import (
    ChatQuery, ChatResponse, SourceInfo,
    Conversation, ConversationList, ConversationMessages,
    ConversationCreate, ConversationUpdate, Message,
    SuccessResponse
)
from api.routers.auth import get_current_user
from utils.database import db_manager
from utils.agent_rag_engine import agent_rag_engine

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_sources(sources: List[dict]) -> List[SourceInfo]:
    """Format sources from agent response"""
    formatted_sources = []
    
    for source in sources:
        formatted_sources.append(
            SourceInfo(
                filename=source.get('filename', 'Unknown'),
                page=source.get('page'),
                chunk_index=source.get('chunk_index'),
                relevance_score=source.get('score')
            )
        )
    
    return formatted_sources


# ============================================================
# CHAT ENDPOINTS
# ============================================================

@router.post("/query", response_model=ChatResponse)
async def query_documents(
    query: ChatQuery,
    current_user: dict = Depends(get_current_user)
):
    """
    Query documents using Multi-Agent System
    
    - **question**: User's question (1-2000 characters)
    - **conversation_id**: Optional conversation thread ID
    - **stream**: Enable streaming response (not yet implemented)
    
    **Multi-Agent Process:**
    1. Retrieval Agent searches vector database
    2. Generation Agent creates contextualized response
    3. Response validated and cited with sources
    """
    try:
        user_id = str(current_user.id)
        start_time = time.time()
        
        # Get or create conversation
        if query.conversation_id:
            conversation = db_manager.get_conversation(query.conversation_id, user_id)
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            conversation_id = query.conversation_id
        else:
            # Create new conversation
            conversation = db_manager.create_conversation(
                user_id=user_id,
                title=query.question[:50]  # Use first 50 chars as title
            )
            conversation_id = conversation.conversation_id
        
        # Save user message
        user_message = db_manager.add_message(
            conversation_id=conversation_id,
            role="user",
            content=query.question
        )
        
        logger.info(f"Query from user {current_user.email}: {query.question[:100]}")
        
        # Query Multi-Agent System
        try:
            result = agent_rag_engine.query(
                question=query.question,
                user_id=user_id
            )
            
            if not result or not result.get('success'):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Agent system failed to process query"
                )
            
            # Extract response data
            response_text = result.get('response', '')
            sources = result.get('sources', [])
            tokens_used = result.get('tokens', 0)
            
            # Save assistant message
            assistant_message = db_manager.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=response_text,
                sources=json.dumps(sources),
                tokens_used=tokens_used
            )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Log analytics
            db_manager.log_query_analytics(
                user_id=user_id,
                conversation_id=conversation_id,
                query_text=query.question,
                response_time=response_time,
                tokens_used=tokens_used,
                documents_searched=[s.get('doc_id') for s in sources if s.get('doc_id')],
                ai_provider=agent_rag_engine.provider,
                success=True
            )
            
            logger.info(f"Query successful: {response_time:.2f}s, {tokens_used} tokens")
            
            return ChatResponse(
                success=True,
                response=response_text,
                sources=format_sources(sources),
                conversation_id=conversation_id,
                message_id=assistant_message.message_id,
                tokens_used=tokens_used,
                response_time=response_time,
                agents_used=["Retrieval Agent", "Generation Agent"]
            )
            
        except Exception as e:
            logger.error(f"Agent query error: {e}", exc_info=True)
            
            # Log failed query
            db_manager.log_query_analytics(
                user_id=user_id,
                conversation_id=conversation_id,
                query_text=query.question,
                response_time=time.time() - start_time,
                tokens_used=0,
                documents_searched=[],
                ai_provider=agent_rag_engine.provider,
                success=False
            )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Query processing failed: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process query"
        )


# ============================================================
# CONVERSATION ENDPOINTS
# ============================================================

@router.get("/conversations", response_model=ConversationList)
async def list_conversations(current_user: dict = Depends(get_current_user)):
    """
    Get list of all user's conversations
    
    Returns conversations sorted by most recent first
    """
    try:
        user_id = str(current_user.id)
        conversations = db_manager.get_user_conversations(user_id)
        
        conversation_list = [
            Conversation(
                conversation_id=conv.conversation_id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=db_manager.get_conversation_message_count(conv.conversation_id),
                is_pinned=conv.is_pinned
            )
            for conv in conversations
        ]
        
        return ConversationList(
            conversations=conversation_list,
            total_count=len(conversation_list)
        )
        
    except Exception as e:
        logger.error(f"List conversations error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )


@router.post("/conversations", response_model=Conversation, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    data: ConversationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new conversation"""
    try:
        user_id = str(current_user.id)
        
        conversation = db_manager.create_conversation(
            user_id=user_id,
            title=data.title
        )
        
        return Conversation(
            conversation_id=conversation.conversation_id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=0,
            is_pinned=False
        )
        
    except Exception as e:
        logger.error(f"Create conversation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationMessages)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get conversation with all messages
    
    Returns full conversation history including user questions and agent responses
    """
    try:
        user_id = str(current_user.id)
        
        # Get conversation
        conversation = db_manager.get_conversation(conversation_id, user_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get messages
        messages = db_manager.get_conversation_messages(conversation_id)
        
        message_list = [
            Message(
                message_id=msg.message_id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
                sources=json.loads(msg.sources) if msg.sources else None,
                tokens_used=msg.tokens_used
            )
            for msg in messages
        ]
        
        return ConversationMessages(
            conversation=Conversation(
                conversation_id=conversation.conversation_id,
                title=conversation.title,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                message_count=len(message_list),
                is_pinned=conversation.is_pinned
            ),
            messages=message_list
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get conversation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation"
        )


@router.patch("/conversations/{conversation_id}", response_model=Conversation)
async def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update conversation (title, pinned status)"""
    try:
        user_id = str(current_user.id)
        
        # Verify ownership
        conversation = db_manager.get_conversation(conversation_id, user_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Update conversation
        updated = db_manager.update_conversation(
            conversation_id=conversation_id,
            title=data.title,
            is_pinned=data.is_pinned
        )
        
        return Conversation(
            conversation_id=updated.conversation_id,
            title=updated.title,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
            message_count=db_manager.get_conversation_message_count(conversation_id),
            is_pinned=updated.is_pinned
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update conversation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update conversation"
        )


@router.delete("/conversations/{conversation_id}", response_model=SuccessResponse)
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete conversation and all messages
    
    ⚠️ Warning: This action cannot be undone!
    """
    try:
        user_id = str(current_user.id)
        
        # Verify ownership
        conversation = db_manager.get_conversation(conversation_id, user_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Delete conversation and messages
        db_manager.delete_conversation(conversation_id, user_id)
        
        logger.info(f"Conversation deleted: {conversation_id} by user {current_user.email}")
        
        return SuccessResponse(
            success=True,
            message="Conversation deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete conversation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )


@router.delete("/conversations", response_model=SuccessResponse)
async def delete_all_conversations(current_user: dict = Depends(get_current_user)):
    """
    Delete all user's conversations
    
    ⚠️ Warning: This action cannot be undone!
    """
    try:
        user_id = str(current_user.id)
        
        # Get all conversations
        conversations = db_manager.get_user_conversations(user_id)
        
        deleted_count = 0
        for conversation in conversations:
            try:
                db_manager.delete_conversation(conversation.conversation_id, user_id)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete conversation {conversation.conversation_id}: {e}")
        
        logger.info(f"All conversations deleted for user {current_user.email}: {deleted_count} conversations")
        
        return SuccessResponse(
            success=True,
            message=f"Deleted {deleted_count} conversation(s) successfully"
        )
        
    except Exception as e:
        logger.error(f"Delete all conversations error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversations"
        )
