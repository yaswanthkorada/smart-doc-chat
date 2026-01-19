"""
Documents Router - Document upload, list, delete
Uses Multi-Agent Ingestion System for processing
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List
import logging
import os
import shutil
from pathlib import Path

from api.models import (
    DocumentUploadResponse, DocumentInfo, DocumentList,
    DocumentDelete, SuccessResponse
)
from api.routers.auth import get_current_user
from utils.database import db_manager
from utils.agent_rag_engine import agent_rag_engine
from utils.storage import StorageFactory

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Initialize storage
storage = StorageFactory.get_storage()

# Allowed file types
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.pptx', '.xlsx', '.csv', '.txt'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


# ============================================================
# DOCUMENT ENDPOINTS
# ============================================================

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and process document with Multi-Agent Ingestion System
    
    - **file**: Document file (PDF, DOCX, PPTX, XLSX, CSV, TXT)
    - Maximum size: 50 MB
    - Agents automatically extract, chunk, and index content
    """
    try:
        # Validate file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Create temp directory if not exists
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Save uploaded file temporarily
        temp_file_path = temp_dir / file.filename
        
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            
            # Check file size
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File too large. Maximum size: 50 MB"
                )
            
            buffer.write(content)
        
        logger.info(f"File uploaded: {file.filename} by user {current_user.email}")
        
        # Process document with Multi-Agent Ingestion System
        user_id = str(current_user.id)
        
        try:
            result = agent_rag_engine.process_document(
                file_path=str(temp_file_path),
                user_id=user_id,
                filename=file.filename
            )
            
            if not result or not result.get('success'):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Document processing failed: {result.get('error', 'Unknown error')}"
                )
            
            # Save document metadata to database
            doc_id = result.get('doc_id')
            
            document = db_manager.create_document(
                user_id=user_id,
                filename=file.filename,
                file_type=file_extension[1:],  # Remove dot
                file_size=len(content),
                storage_url=str(temp_file_path),
                doc_id=doc_id,
                page_count=result.get('page_count'),
                vector_count=result.get('chunk_count')
            )
            
            logger.info(f"Document processed successfully: {doc_id}")
            
            return DocumentUploadResponse(
                success=True,
                document_id=doc_id,
                filename=file.filename,
                file_type=file_extension[1:],
                file_size=len(content),
                page_count=result.get('page_count'),
                vector_count=result.get('chunk_count'),
                message=f"Document '{file.filename}' uploaded and processed successfully"
            )
            
        except Exception as e:
            logger.error(f"Document processing error: {e}", exc_info=True)
            
            # Clean up temp file
            if temp_file_path.exists():
                temp_file_path.unlink()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Document processing failed: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/list", response_model=DocumentList)
async def list_documents(current_user: dict = Depends(get_current_user)):
    """
    Get list of all user's documents
    
    Returns document metadata including filename, size, upload date, etc.
    """
    try:
        user_id = str(current_user.id)
        documents = db_manager.get_user_documents(user_id)
        
        document_list = [
            DocumentInfo(
                id=str(doc.id),
                document_id=doc.document_id,
                filename=doc.filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                uploaded_at=doc.uploaded_at,
                is_indexed=doc.is_indexed,
                page_count=doc.page_count,
                vector_count=doc.vector_count
            )
            for doc in documents
        ]
        
        total_size = sum(doc.file_size for doc in documents if doc.file_size)
        
        return DocumentList(
            documents=document_list,
            total_count=len(document_list),
            total_size=total_size
        )
        
    except Exception as e:
        logger.error(f"List documents error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents"
        )


@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific document by ID"""
    try:
        user_id = str(current_user.id)
        document = db_manager.get_document_by_id(document_id, user_id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return DocumentInfo(
            id=str(document.id),
            document_id=document.document_id,
            filename=document.filename,
            file_type=document.file_type,
            file_size=document.file_size,
            uploaded_at=document.uploaded_at,
            is_indexed=document.is_indexed,
            page_count=document.page_count,
            vector_count=document.vector_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get document error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document"
        )


@router.delete("/{document_id}", response_model=DocumentDelete)
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete document and all associated data
    
    - Removes document metadata from database
    - Deletes vector embeddings from ChromaDB
    - Removes physical file from storage
    """
    try:
        user_id = str(current_user.id)
        
        # Get document info
        document = db_manager.get_document_by_id(document_id, user_id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Delete from vector database
        try:
            agent_rag_engine.delete_document(user_id, document_id)
        except Exception as e:
            logger.warning(f"Failed to delete vectors: {e}")
        
        # Delete from database
        db_manager.delete_document(document_id, user_id)
        
        # Delete physical file
        try:
            if document.storage_url and Path(document.storage_url).exists():
                Path(document.storage_url).unlink()
        except Exception as e:
            logger.warning(f"Failed to delete file: {e}")
        
        logger.info(f"Document deleted: {document_id} by user {current_user.email}")
        
        return DocumentDelete(
            success=True,
            message=f"Document '{document.filename}' deleted successfully",
            document_id=document_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete document error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )


@router.delete("/all", response_model=SuccessResponse)
async def delete_all_documents(current_user: dict = Depends(get_current_user)):
    """
    Delete all user's documents
    
    ⚠️ Warning: This action cannot be undone!
    """
    try:
        user_id = str(current_user.id)
        
        # Get all documents
        documents = db_manager.get_user_documents(user_id)
        
        deleted_count = 0
        for document in documents:
            try:
                # Delete vectors
                agent_rag_engine.delete_document(user_id, document.document_id)
                
                # Delete from database
                db_manager.delete_document(document.document_id, user_id)
                
                # Delete file
                if document.storage_url and Path(document.storage_url).exists():
                    Path(document.storage_url).unlink()
                
                deleted_count += 1
                
            except Exception as e:
                logger.error(f"Failed to delete document {document.document_id}: {e}")
        
        logger.info(f"All documents deleted for user {current_user.email}: {deleted_count} documents")
        
        return SuccessResponse(
            success=True,
            message=f"Deleted {deleted_count} document(s) successfully"
        )
        
    except Exception as e:
        logger.error(f"Delete all documents error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete documents"
        )
