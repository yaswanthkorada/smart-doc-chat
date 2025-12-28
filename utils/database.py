from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from typing import Union
import bcrypt
import uuid
import urllib.parse
import sqlalchemy
from config import config
from loguru import logger

Base = declarative_base()

class User(Base):
    """User model for authentication and management"""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(String(50), default='free')  # free, pro, enterprise
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verify password"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password check error: {e}")
            return False
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "subscription_tier": self.subscription_tier,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

class Conversation(Base):
    """Conversation = A complete chat thread"""
    __tablename__ = 'conversations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    title = Column(String(200), default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)
    summary = Column(Text)  # Summary of conversation
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    sessions = relationship("ChatSession", back_populates="conversation", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "conversation_id": self.conversation_id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_pinned": self.is_pinned,
            "message_count": len(self.messages) if self.messages else 0
        }

class ChatSession(Base):
    """Session = A sub-section within a conversation"""
    __tablename__ = 'chat_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)
    conversation_id = Column(String(36), ForeignKey('conversations.conversation_id'), nullable=False)
    session_start = Column(DateTime, default=datetime.utcnow)
    session_end = Column(DateTime)
    is_active = Column(Boolean, default=True)
    device_info = Column(String(200))
    ip_address = Column(String(50))
    
    # Relationships
    conversation = relationship("Conversation", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "session_id": self.session_id,
            "session_start": self.session_start.isoformat() if self.session_start else None,
            "session_end": self.session_end.isoformat() if self.session_end else None,
            "is_active": self.is_active
        }

class Message(Base):
    """Individual message in a conversation/session"""
    __tablename__ = 'messages'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)
    conversation_id = Column(String(36), ForeignKey('conversations.conversation_id'), nullable=False)
    session_id = Column(String(36), ForeignKey('chat_sessions.session_id'), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tokens_used = Column(Integer, default=0)
    sources = Column(Text)  # JSON string
    feedback = Column(String(20))  # 'helpful', 'not_helpful', None
    edited = Column(Boolean, default=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    session = relationship("ChatSession", back_populates="messages")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "message_id": self.message_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "tokens_used": self.tokens_used,
            "sources": self.sources
        }

class Document(Base):
    """Document storage metadata"""
    __tablename__ = 'documents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    file_path = Column(Text)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    chunk_count = Column(Integer, default=0)
    doc_metadata = Column('metadata', Text)  # Map to 'metadata' column in DB, avoiding reserved word
    
    # Relationships
    user = relationship("User", back_populates="documents")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "filename": self.filename,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "file_path": self.file_path,
            "chunk_count": self.chunk_count,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "processed": self.processed,
            "metadata": self.doc_metadata
        }

class QueryAnalytics(Base):
    """Track query analytics for usage dashboard"""
    __tablename__ = 'query_analytics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    conversation_id = Column(String(36), ForeignKey('conversations.conversation_id'))
    query_text = Column(Text, nullable=False)
    response_time = Column(Integer)  # milliseconds
    tokens_used = Column(Integer, default=0)
    documents_searched = Column(Text)  # JSON list of doc_ids
    ai_provider = Column(String(50))  # gemini, openai
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "query_text": self.query_text,
            "response_time": self.response_time,
            "tokens_used": self.tokens_used,
            "ai_provider": self.ai_provider,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "success": self.success
        }

class DatabaseManager:
    """Database manager for all operations"""
    
    def __init__(self, db_url: str = None):
        try:
            if db_url is None:
                db_url = config.DATABASE_URL
            
            # Handle password encoding in PostgreSQL URLs
            if db_url.startswith("postgresql://"):
                db_url = self._encode_postgres_password(db_url)
            
            logger.info(f"Initializing database: {db_url.replace(db_url.split('@')[0].split(':')[-1], '***') if '@' in db_url else db_url}")
            
            # Add connection arguments for better reliability
            engine_args = {"echo": config.DEBUG}
            
            # For PostgreSQL, add connection pool settings
            if db_url.startswith("postgresql://"):
                engine_args.update({
                    "pool_pre_ping": True,  # Verify connections before using
                    "pool_recycle": 3600,   # Recycle connections after 1 hour
                    "connect_args": {
                        "connect_timeout": 10,
                        "options": "-c timezone=utc"
                    }
                })
            
            self.engine = create_engine(db_url, **engine_args)
            
            # Test the connection before creating tables
            with self.engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT 1"))
            
            Base.metadata.create_all(self.engine)
            self.SessionLocal = sessionmaker(bind=self.engine)
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            logger.error(f"Database URL format: {db_url.split('@')[1] if '@' in db_url else 'local SQLite'}")
            # Re-raise to prevent silent failures
            raise
    
    def _encode_postgres_password(self, db_url: str) -> str:
        """Encode password in PostgreSQL URL if it contains special characters"""
        try:
            # Parse: postgresql://user:password@host:port/database
            if "://" not in db_url:
                return db_url
            
            protocol, rest = db_url.split("://", 1)
            
            # Find the LAST @ which separates credentials from host
            # This handles passwords that contain @ symbols
            last_at_index = rest.rfind("@")
            if last_at_index == -1:
                return db_url
            
            credentials = rest[:last_at_index]
            host_db = rest[last_at_index + 1:]
            
            if ":" not in credentials:
                return db_url
            
            # Split username and password (password may contain :)
            username, password = credentials.split(":", 1)
            
            # Only encode if password contains special characters and isn't already encoded
            if any(char in password for char in ['@', ':', '/', '?', '#', '[', ']']) and '%' not in password:
                encoded_password = urllib.parse.quote_plus(password)
                return f"{protocol}://{username}:{encoded_password}@{host_db}"
            
            return db_url
        except Exception as e:
            logger.warning(f"Could not encode password in URL: {e}")
            return db_url
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, email: str, username: str, password: str, full_name: str = None):
        """Create a new user"""
        session = self.get_session()
        try:
            user = User(email=email, username=username, full_name=full_name)
            user.set_password(password)
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"Created user: {username}")
            return user
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating user: {e}")
            raise e
        finally:
            session.close()
    
    def get_user_by_username(self, username: str):
        """Get user by username"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if user:
                session.expunge(user)
            return user
        finally:
            session.close()
    
    def get_user_by_email(self, email: str):
        """Get user by email"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if user:
                session.expunge(user)
            return user
        finally:
            session.close()
    
    def update_last_login(self, user_id: Union[str, uuid.UUID]):
        """Update user's last login time"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.last_login = datetime.utcnow()
                session.commit()
                logger.info(f"Updated last login for user_id: {user_id}")
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
        finally:
            session.close()
    
    # ==================== CONVERSATION OPERATIONS ====================
    
    def create_conversation(self, user_id: Union[str, uuid.UUID], title: str = "New Conversation"):
        """Create a new conversation"""
        session = self.get_session()
        try:
            conversation = Conversation(user_id=user_id, title=title)
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            session.expunge(conversation)
            logger.info(f"Created conversation: {conversation.conversation_id}")
            return conversation
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating conversation: {e}")
            raise e
        finally:
            session.close()
    
    def get_user_conversations(self, user_id: Union[str, uuid.UUID], limit: int = 50):
        """Get all conversations for a user"""
        session = self.get_session()
        try:
            conversations = session.query(Conversation).filter(
                Conversation.user_id == user_id,
                Conversation.is_active == True
            ).order_by(
                Conversation.is_pinned.desc(),
                Conversation.updated_at.desc()
            ).limit(limit).all()
            
            result = []
            for conv in conversations:
                session.expunge(conv)
                result.append(conv)
            return result
        finally:
            session.close()
    
    def get_conversation(self, conversation_id: str):
        """Get specific conversation"""
        session = self.get_session()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()
            if conversation:
                session.expunge(conversation)
            return conversation
        finally:
            session.close()
    
    def update_conversation_title(self, conversation_id: str, new_title: str):
        """Update conversation title"""
        session = self.get_session()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()
            if conversation:
                conversation.title = new_title
                conversation.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"Updated conversation title: {conversation_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating conversation title: {e}")
            return False
        finally:
            session.close()
    
    def pin_conversation(self, conversation_id: str):
        """Pin/unpin conversation"""
        session = self.get_session()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()
            if conversation:
                conversation.is_pinned = not conversation.is_pinned
                session.commit()
                return conversation.is_pinned
            return False
        finally:
            session.close()
    
    def delete_conversation(self, conversation_id: str):
        """Soft delete conversation"""
        session = self.get_session()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()
            if conversation:
                conversation.is_active = False
                session.commit()
                logger.info(f"Deleted conversation: {conversation_id}")
                return True
            return False
        finally:
            session.close()
    
    # ==================== SESSION OPERATIONS ====================
    
    def create_session(self, conversation_id: str, device_info: str = None, ip_address: str = None):
        """Create a new chat session"""
        session = self.get_session()
        try:
            chat_session = ChatSession(
                conversation_id=conversation_id,
                device_info=device_info,
                ip_address=ip_address
            )
            session.add(chat_session)
            session.commit()
            session.refresh(chat_session)
            session.expunge(chat_session)
            logger.info(f"Created session: {chat_session.session_id}")
            return chat_session
        finally:
            session.close()
    
    def get_active_session(self, conversation_id: str):
        """Get or create active session for conversation"""
        session = self.get_session()
        try:
            active_session = session.query(ChatSession).filter(
                ChatSession.conversation_id == conversation_id,
                ChatSession.is_active == True
            ).order_by(ChatSession.session_start.desc()).first()
            
            if active_session:
                session.expunge(active_session)
                return active_session
            
            session.close()
            return self.create_session(conversation_id)
        finally:
            if session.is_active:
                session.close()
    
    def end_session(self, session_id: str):
        """End a chat session"""
        session = self.get_session()
        try:
            chat_session = session.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            if chat_session:
                chat_session.session_end = datetime.utcnow()
                chat_session.is_active = False
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def get_conversation_sessions(self, conversation_id: str):
        """Get all sessions for a conversation"""
        session = self.get_session()
        try:
            sessions = session.query(ChatSession).filter(
                ChatSession.conversation_id == conversation_id
            ).order_by(ChatSession.session_start.desc()).all()
            
            result = []
            for s in sessions:
                session.expunge(s)
                result.append(s)
            return result
        finally:
            session.close()
    
    # ==================== MESSAGE OPERATIONS ====================
    
    def add_message(self, conversation_id: str, session_id: str, role: str, 
                    content: str, sources: str = None, tokens_used: int = 0):
        """Add a message to conversation and session"""
        session = self.get_session()
        try:
            message = Message(
                conversation_id=conversation_id,
                session_id=session_id,
                role=role,
                content=content,
                sources=sources,
                tokens_used=tokens_used
            )
            session.add(message)
            
            # Update conversation timestamp
            conversation = session.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()
            if conversation:
                conversation.updated_at = datetime.utcnow()
            
            session.commit()
            session.refresh(message)
            session.expunge(message)
            return message
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding message: {e}")
            raise e
        finally:
            session.close()
    
    def get_conversation_messages(self, conversation_id: str, limit: int = 100):
        """Get all messages in a conversation"""
        session = self.get_session()
        try:
            messages = session.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp.asc()).limit(limit).all()
            
            result = []
            for msg in messages:
                session.expunge(msg)
                result.append(msg)
            return result
        finally:
            session.close()
    
    def get_session_messages(self, session_id: str):
        """Get all messages in a specific session"""
        session = self.get_session()
        try:
            messages = session.query(Message).filter(
                Message.session_id == session_id
            ).order_by(Message.timestamp.asc()).all()
            
            result = []
            for msg in messages:
                session.expunge(msg)
                result.append(msg)
            return result
        finally:
            session.close()
    
    def update_message_feedback(self, message_id: str, feedback: str):
        """Update message feedback"""
        session = self.get_session()
        try:
            message = session.query(Message).filter(
                Message.message_id == message_id
            ).first()
            if message:
                message.feedback = feedback
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    # ==================== DOCUMENT OPERATIONS ====================
    
    def add_document(self, user_id: Union[str, uuid.UUID], filename: str, 
                    file_size: int, file_type: str, file_path: str):
        """Add document metadata"""
        session = self.get_session()
        try:
            document = Document(
                user_id=user_id,
                filename=filename,
                file_size=file_size,
                file_type=file_type,
                file_path=file_path,
                processed=False,
                chunk_count=0
            )
            session.add(document)
            session.commit()
            session.refresh(document)
            session.expunge(document)
            logger.info(f"Added document: {filename}")
            return document
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding document: {e}")
            raise e
        finally:
            session.close()
    
    def update_document_status(self, document_id: str, processed: bool = False, chunk_count: int = 0, metadata: str = None):
        """Update document processing status"""
        session = self.get_session()
        try:
            document = session.query(Document).filter(Document.id == document_id).first()
            if document:
                document.processed = processed
                document.chunk_count = chunk_count
                if metadata:
                    document.doc_metadata = metadata
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def get_user_documents(self, user_id: Union[str, uuid.UUID]):
        """Get all documents for a user"""
        session = self.get_session()
        try:
            documents = session.query(Document).filter(
                Document.user_id == user_id
            ).order_by(Document.upload_date.desc()).all()
            
            result = []
            for doc in documents:
                session.expunge(doc)
                result.append(doc)
            return result
        finally:
            session.close()
    
    def delete_document(self, document_id: str):
        """Delete document metadata"""
        session = self.get_session()
        try:
            document = session.query(Document).filter(Document.id == document_id).first()
            if document:
                session.delete(document)
                session.commit()
                logger.info(f"Deleted document: {document.filename}")
                return True
            return False
        finally:
            session.close()
    
    # ==================== ANALYTICS ====================
    
    def log_query_analytics(self, user_id: Union[str, uuid.UUID], conversation_id: str, query_text: str, 
                           response_time: int, tokens_used: int, documents_searched: list,
                           ai_provider: str, success: bool = True, error_message: str = None):
        """Log query analytics for dashboard"""
        session = self.get_session()
        try:
            import json
            analytics = QueryAnalytics(
                user_id=user_id,
                conversation_id=conversation_id,
                query_text=query_text,
                response_time=response_time,
                tokens_used=tokens_used,
                documents_searched=json.dumps(documents_searched) if documents_searched else None,
                ai_provider=ai_provider,
                success=success,
                error_message=error_message
            )
            session.add(analytics)
            session.commit()
            logger.debug(f"Logged analytics for user {user_id}")
        except Exception as e:
            logger.error(f"Error logging analytics: {e}")
            session.rollback()
        finally:
            session.close()
    
    def get_user_analytics(self, user_id: int, days: int = 30):
        """Get analytics for user dashboard"""
        session = self.get_session()
        try:
            from datetime import timedelta
            from sqlalchemy import func
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Total queries
            total_queries = session.query(func.count(QueryAnalytics.id)).filter(
                QueryAnalytics.user_id == user_id,
                QueryAnalytics.timestamp >= cutoff_date
            ).scalar() or 0
            
            # Queries by day
            queries_by_day = session.query(
                func.date(QueryAnalytics.timestamp).label('date'),
                func.count(QueryAnalytics.id).label('count')
            ).filter(
                QueryAnalytics.user_id == user_id,
                QueryAnalytics.timestamp >= cutoff_date
            ).group_by(func.date(QueryAnalytics.timestamp)).all()
            
            # Popular documents
            popular_docs = session.query(
                QueryAnalytics.documents_searched,
                func.count(QueryAnalytics.id).label('count')
            ).filter(
                QueryAnalytics.user_id == user_id,
                QueryAnalytics.timestamp >= cutoff_date,
                QueryAnalytics.documents_searched.isnot(None)
            ).group_by(QueryAnalytics.documents_searched).order_by(
                func.count(QueryAnalytics.id).desc()
            ).limit(10).all()
            
            # Average response time
            avg_response_time = session.query(
                func.avg(QueryAnalytics.response_time)
            ).filter(
                QueryAnalytics.user_id == user_id,
                QueryAnalytics.timestamp >= cutoff_date,
                QueryAnalytics.response_time.isnot(None)
            ).scalar() or 0
            
            # Total tokens used
            total_tokens = session.query(
                func.sum(QueryAnalytics.tokens_used)
            ).filter(
                QueryAnalytics.user_id == user_id,
                QueryAnalytics.timestamp >= cutoff_date
            ).scalar() or 0
            
            # Success rate
            total_attempts = session.query(func.count(QueryAnalytics.id)).filter(
                QueryAnalytics.user_id == user_id,
                QueryAnalytics.timestamp >= cutoff_date
            ).scalar() or 1
            
            successful_queries = session.query(func.count(QueryAnalytics.id)).filter(
                QueryAnalytics.user_id == user_id,
                QueryAnalytics.timestamp >= cutoff_date,
                QueryAnalytics.success == True
            ).scalar() or 0
            
            success_rate = (successful_queries / total_attempts * 100) if total_attempts > 0 else 0
            
            # AI provider usage
            provider_usage = session.query(
                QueryAnalytics.ai_provider,
                func.count(QueryAnalytics.id).label('count')
            ).filter(
                QueryAnalytics.user_id == user_id,
                QueryAnalytics.timestamp >= cutoff_date
            ).group_by(QueryAnalytics.ai_provider).all()
            
            return {
                'total_queries': total_queries,
                'queries_by_day': [{'date': str(date), 'count': count} for date, count in queries_by_day],
                'popular_documents': popular_docs,
                'avg_response_time': int(avg_response_time) if avg_response_time else 0,
                'total_tokens': total_tokens,
                'success_rate': round(success_rate, 2),
                'provider_usage': {provider: count for provider, count in provider_usage}
            }
        finally:
            session.close()
    
    def get_user_stats(self, user_id: int):
        """Get user statistics"""
        session = self.get_session()
        try:
            total_conversations = session.query(Conversation).filter(
                Conversation.user_id == user_id,
                Conversation.is_active == True
            ).count()
            
            total_messages = session.query(Message).join(Conversation).filter(
                Conversation.user_id == user_id
            ).count()
            
            total_tokens = session.query(Message).join(Conversation).filter(
                Conversation.user_id == user_id
            ).with_entities(Message.tokens_used).all()
            
            tokens_sum = sum(t[0] for t in total_tokens if t[0])
            
            total_documents = session.query(Document).filter(
                Document.user_id == user_id
            ).count()
            
            return {
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "total_tokens_used": tokens_sum,
                "total_documents": total_documents
            }
        finally:
            session.close()

# Initialize global database manager
db_manager = DatabaseManager()
