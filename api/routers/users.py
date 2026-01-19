"""
Users Router - User profile and account management
"""

from fastapi import APIRouter, Depends, HTTPException, status
import logging

from api.models import (
    UserProfile, UserUpdate, PasswordChange,
    UsageStats, SuccessResponse
)
from api.routers.auth import get_current_user, get_password_hash, verify_password
from utils.database import db_manager

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()


# ============================================================
# USER PROFILE ENDPOINTS
# ============================================================

@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile"""
    return UserProfile(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        subscription_tier=current_user.subscription_tier,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.patch("/profile", response_model=UserProfile)
async def update_profile(
    data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update user profile
    
    - **username**: New username (optional)
    - **full_name**: New full name (optional)
    - **email**: New email (optional)
    """
    try:
        user_id = str(current_user.id)
        
        # Check username availability if changing
        if data.username and data.username != current_user.username:
            existing = db_manager.get_user_by_username(data.username)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Check email availability if changing
        if data.email and data.email != current_user.email:
            existing = db_manager.get_user_by_email(data.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Update user
        updated_user = db_manager.update_user(
            user_id=user_id,
            username=data.username,
            full_name=data.full_name,
            email=data.email
        )
        
        logger.info(f"Profile updated for user {current_user.email}")
        
        return UserProfile(
            id=str(updated_user.id),
            email=updated_user.email,
            username=updated_user.username,
            full_name=updated_user.full_name,
            subscription_tier=updated_user.subscription_tier,
            created_at=updated_user.created_at,
            last_login=updated_user.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update profile error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """
    Change user password
    
    - **current_password**: Current password for verification
    - **new_password**: New password (minimum 8 characters)
    """
    try:
        # Verify current password
        if not verify_password(data.current_password, current_user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_password_hash = get_password_hash(data.new_password)
        
        # Update password
        db_manager.update_password(str(current_user.id), new_password_hash)
        
        logger.info(f"Password changed for user {current_user.email}")
        
        return SuccessResponse(
            success=True,
            message="Password changed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.delete("/account", response_model=SuccessResponse)
async def delete_account(current_user: dict = Depends(get_current_user)):
    """
    Delete user account
    
    ⚠️ Warning: This will delete:
    - User profile
    - All documents
    - All conversations
    - All messages
    - All vector embeddings
    
    This action cannot be undone!
    """
    try:
        user_id = str(current_user.id)
        
        # Delete user and all associated data
        db_manager.delete_user(user_id)
        
        logger.info(f"Account deleted: {current_user.email}")
        
        return SuccessResponse(
            success=True,
            message="Account deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Delete account error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )


# ============================================================
# USAGE STATISTICS
# ============================================================

@router.get("/stats", response_model=UsageStats)
async def get_usage_stats(current_user: dict = Depends(get_current_user)):
    """
    Get user's usage statistics
    
    Returns:
    - Total documents uploaded
    - Total conversations
    - Total messages
    - Total tokens used
    - Storage used (bytes)
    - Queries today/this month
    """
    try:
        user_id = str(current_user.id)
        
        # Get statistics from database
        stats = db_manager.get_user_statistics(user_id)
        
        return UsageStats(
            total_documents=stats.get('total_documents', 0),
            total_conversations=stats.get('total_conversations', 0),
            total_messages=stats.get('total_messages', 0),
            total_tokens_used=stats.get('total_tokens_used', 0),
            storage_used=stats.get('storage_used', 0),
            queries_today=stats.get('queries_today', 0),
            queries_this_month=stats.get('queries_this_month', 0)
        )
        
    except Exception as e:
        logger.error(f"Get stats error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )
