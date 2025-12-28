import os
import hashlib
from typing import List, Dict, Tuple
from pathlib import Path
from loguru import logger
import plotly.express as px
import plotly.graph_objects as go
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import base64
from io import BytesIO
import ssl
import certifi

# Disable SSL verification for corporate networks (office laptops with proxy)
# This is needed when corporate firewalls use self-signed certificates
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass

# Set environment variable to disable SSL verification for HuggingFace
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

try:
    import fitz  # PyMuPDF
    from PIL import Image
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.warning("PyMuPDF not available. Install with: pip install PyMuPDF Pillow")

# Document loaders - use PyPDF2 directly to avoid pwd module issue
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import Document
import PyPDF2
import docx
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from config import config
from utils.storage import storage
from utils.database import db_manager
import json

try:
    import google.generativeai as genai
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI not available. Install with: pip install google-generativeai langchain-google-genai")

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    logger.warning("Hugging Face not available. Install with: pip install sentence-transformers langchain-huggingface")

class RAGEngine:
    """RAG Engine for document processing and querying"""
    
    def __init__(self):
        # Initialize embeddings based on EMBEDDING_PROVIDER (separate from chat AI_PROVIDER)
        embedding_provider = getattr(config, 'EMBEDDING_PROVIDER', 'huggingface')
        
        # Check availability and fallback
        if embedding_provider == "huggingface" and not HUGGINGFACE_AVAILABLE:
            logger.warning("Hugging Face not available, falling back to Gemini (free)")
            embedding_provider = "gemini"
        elif embedding_provider == "gemini" and (not GEMINI_AVAILABLE or not config.GEMINI_API_KEY):
            logger.warning("Gemini embeddings not available, falling back to Hugging Face")
            embedding_provider = "huggingface" if HUGGINGFACE_AVAILABLE else "openai"
        
        # Initialize embeddings
        if embedding_provider == "huggingface":
            # Free local embeddings - no API key needed!
            # Configure SSL context to work with corporate proxies
            try:
                import ssl
                ssl._create_default_https_context = ssl._create_unverified_context
            except:
                pass
            
            try:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=config.HUGGINGFACE_MODEL,
                    model_kwargs={'device': 'cpu'},  # Use 'cuda' if you have GPU
                    encode_kwargs={'normalize_embeddings': True}
                )
                logger.info(f"Using Hugging Face embeddings ({config.HUGGINGFACE_MODEL}) - FREE & LOCAL!")
            except Exception as e:
                logger.error(f"Failed to load HuggingFace embeddings: {e}")
                logger.warning("Falling back to Gemini embeddings (also free)")
                embedding_provider = "gemini"
                if not config.GEMINI_API_KEY:
                    raise ValueError("Both HuggingFace and Gemini failed. Please set GOOGLE_API_KEY in .env file")
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model=config.GEMINI_EMBEDDING_MODEL,
                    google_api_key=config.GEMINI_API_KEY
                )
                logger.info(f"Using Gemini embeddings ({config.GEMINI_EMBEDDING_MODEL}) - FREE!")
        
        if embedding_provider == "openai":
            if not config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set in environment")
            # Initialize OpenAI embeddings
            try:
                self.embeddings = OpenAIEmbeddings(
                    model=config.OPENAI_EMBEDDING_MODEL,
                    api_key=config.OPENAI_API_KEY
                )
                logger.info(f"Using OpenAI embeddings ({config.OPENAI_EMBEDDING_MODEL})")
            except TypeError:
                # Fallback for older versions
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=config.OPENAI_API_KEY
                )
                logger.info(f"Using OpenAI embeddings (default model)")
        else:
            # Gemini embeddings
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=config.GEMINI_EMBEDDING_MODEL,
                google_api_key=config.GEMINI_API_KEY
            )
            logger.info(f"Using Gemini embeddings ({config.GEMINI_EMBEDDING_MODEL})")
        
        # Initialize chat model based on AI_PROVIDER
        if config.AI_PROVIDER == "gemini":
            if not GEMINI_AVAILABLE:
                raise ImportError("Google Generative AI not installed. Run: pip install google-generativeai")
            if not config.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not set in environment")
            
            # Configure Gemini for chat
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.llm = None  # Will use Gemini directly for chat
            self.model = genai.GenerativeModel(config.GEMINI_MODEL)
            logger.info(f"RAG Engine initialized with Gemini chat ({config.GEMINI_MODEL})")
        else:
            # OpenAI for chat
            if not config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set in environment")
            
            try:
                self.llm = ChatOpenAI(
                    model=config.OPENAI_MODEL,
                    api_key=config.OPENAI_API_KEY
                )
                logger.info(f"Using OpenAI model: {config.OPENAI_MODEL}")
            except TypeError:
                # Fallback for older versions
                self.llm = ChatOpenAI(
                    model_name=config.OPENAI_MODEL,
                    openai_api_key=config.OPENAI_API_KEY
                )
                logger.info(f"Using OpenAI model (legacy): {config.OPENAI_MODEL}")
            
            self.model = None
            logger.info(f"RAG Engine initialized with OpenAI chat ({config.OPENAI_MODEL})")
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # Store current provider
        self.current_embedding_provider = embedding_provider
        self.current_ai_provider = config.AI_PROVIDER
    
    def update_provider(self, provider: str):
        """
        Dynamically update both LLM and embeddings provider
        Args:
            provider: 'gemini' or 'openai'
        """
        try:
            logger.info(f"Switching provider to: {provider}")
            
            # Update embeddings
            if provider == "gemini":
                if not GEMINI_AVAILABLE or not config.GEMINI_API_KEY:
                    raise ValueError("Gemini not available. Check API key.")
                
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model=config.GEMINI_EMBEDDING_MODEL,
                    google_api_key=config.GEMINI_API_KEY
                )
                self.model = genai.GenerativeModel(config.GEMINI_MODEL)
                self.llm = None
                logger.info(f"✅ Switched to Gemini: LLM={config.GEMINI_MODEL}, Embeddings={config.GEMINI_EMBEDDING_MODEL}")
                
            elif provider == "openai":
                if not config.OPENAI_API_KEY:
                    raise ValueError("OpenAI API key not set")
                
                try:
                    self.embeddings = OpenAIEmbeddings(
                        model=config.OPENAI_EMBEDDING_MODEL,
                        api_key=config.OPENAI_API_KEY
                    )
                    self.llm = ChatOpenAI(
                        model=config.OPENAI_MODEL,
                        api_key=config.OPENAI_API_KEY
                    )
                except TypeError:
                    # Fallback for older langchain-openai versions
                    self.embeddings = OpenAIEmbeddings(
                        openai_api_key=config.OPENAI_API_KEY
                    )
                    self.llm = ChatOpenAI(
                        model_name=config.OPENAI_MODEL,
                        openai_api_key=config.OPENAI_API_KEY
                    )
                self.model = None
                logger.info(f"✅ Switched to OpenAI: LLM={config.OPENAI_MODEL}, Embeddings={config.OPENAI_EMBEDDING_MODEL}")
            
            self.current_embedding_provider = provider
            self.current_ai_provider = provider
            
            return True
            
        except Exception as e:
            logger.error(f"Error switching provider: {e}")
            return False
    
    def generate_doc_id(self, file_path: str) -> str:
        """Generate unique document ID based on file content"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return f"doc_{file_hash[:16]}"
        except Exception as e:
            logger.error(f"Error generating doc_id: {e}")
            return f"doc_{hashlib.sha256(str(file_path).encode()).hexdigest()[:16]}"
    
    def extract_text_from_file(self, file_path: str, file_type: str) -> List[Document]:
        """Extract text from various file types using direct libraries"""
        try:
            logger.info(f"Extracting text from: {file_path} (type: {file_type})")
            
            documents = []
            
            if file_type == 'pdf':
                # Use PyPDF2 for text extraction
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages):
                        text = page.extract_text()
                        if text.strip():
                            documents.append(Document(
                                page_content=text,
                                metadata={"page": page_num + 1, "source": file_path}
                            ))
                
                # Extract and analyze images if PyMuPDF is available
                if PYMUPDF_AVAILABLE and GEMINI_AVAILABLE:
                    try:
                        image_docs = self.extract_images_from_pdf(file_path)
                        documents.extend(image_docs)
                        logger.info(f"Extracted {len(image_docs)} images from PDF")
                    except Exception as e:
                        logger.warning(f"Could not extract images: {e}")
            
            elif file_type in ['docx', 'doc']:
                # Use python-docx directly
                doc = docx.Document(file_path)
                text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                documents.append(Document(
                    page_content=text,
                    metadata={"source": file_path}
                ))
            
            elif file_type in ['pptx', 'ppt']:
                # Use python-pptx for PowerPoint
                from pptx import Presentation
                prs = Presentation(file_path)
                for slide_num, slide in enumerate(prs.slides):
                    slide_text = []
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            slide_text.append(shape.text)
                    if slide_text:
                        documents.append(Document(
                            page_content='\n'.join(slide_text),
                            metadata={"slide": slide_num + 1, "source": file_path}
                        ))
            
            elif file_type in ['xlsx', 'xls', 'csv']:
                # Excel/CSV processing
                if file_type == 'csv':
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                # Create comprehensive text representation
                text_parts = []
                text_parts.append(f"Dataset Overview:")
                text_parts.append(f"- Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                text_parts.append(f"- Columns: {', '.join(df.columns.tolist())}")
                text_parts.append(f"\nStatistical Summary:\n{df.describe().to_string()}")
                text_parts.append(f"\nData Types:\n{df.dtypes.to_string()}")
                text_parts.append(f"\nFirst 100 rows:\n{df.head(100).to_string()}")
                
                # Store the actual dataframe in metadata for advanced queries
                documents.append(Document(
                    page_content='\n\n'.join(text_parts),
                    metadata={"source": file_path, "type": "tabular_data", "shape": df.shape}
                ))
            
            elif file_type == 'txt':
                # Use TextLoader (no pwd dependency)
                loader = TextLoader(file_path, encoding='utf-8')
                documents = loader.load()
            
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            logger.info(f"Extracted {len(documents)} pages/sections")
            return documents
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            raise e
    
    def extract_images_from_pdf(self, file_path: str) -> List[Document]:
        """Extract and analyze images from PDF using PyMuPDF and Gemini Vision"""
        try:
            if not PYMUPDF_AVAILABLE:
                return []
            
            image_documents = []
            pdf_document = fitz.open(file_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = pdf_document.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        # Convert to PIL Image
                        image = Image.open(BytesIO(image_bytes))
                        
                        # Skip very small images (likely decorative)
                        if image.width < 100 or image.height < 100:
                            continue
                        
                        # Convert to base64 for Gemini
                        buffered = BytesIO()
                        image.save(buffered, format="PNG")
                        img_base64 = base64.b64encode(buffered.getvalue()).decode()
                        
                        # Analyze image with Gemini Vision
                        description = self.analyze_image_with_gemini(img_base64)
                        
                        if description:
                            # Create document with image description
                            image_documents.append(Document(
                                page_content=f"[IMAGE on page {page_num + 1}]: {description}",
                                metadata={
                                    "page": page_num + 1,
                                    "source": file_path,
                                    "type": "image",
                                    "image_index": img_index
                                }
                            ))
                            logger.info(f"Analyzed image {img_index + 1} on page {page_num + 1}")
                    
                    except Exception as e:
                        logger.warning(f"Could not process image {img_index} on page {page_num}: {e}")
                        continue
            
            pdf_document.close()
            return image_documents
        
        except Exception as e:
            logger.error(f"Error extracting images from PDF: {e}")
            return []
    
    def analyze_image_with_gemini(self, image_base64: str) -> str:
        """Analyze image using Gemini Vision API"""
        try:
            if not GEMINI_AVAILABLE:
                return ""
            
            # Create prompt for image analysis
            prompt = """Analyze this image and provide a detailed description. Include:
1. What type of content is this (diagram, chart, photo, table, etc.)
2. Main elements and their relationships
3. Any text visible in the image
4. Key insights or data shown
5. Context that would help someone understand the document

Be concise but thorough. Focus on information that would be useful for answering questions."""
            
            # Use Gemini Vision model
            import google.generativeai as genai
            vision_model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Decode base64 to bytes for Gemini
            import base64
            image_bytes = base64.b64decode(image_base64)
            
            # Create image part
            image_part = {
                'mime_type': 'image/png',
                'data': image_bytes
            }
            
            # Generate description
            response = vision_model.generate_content([prompt, image_part])
            
            return response.text
        
        except Exception as e:
            logger.error(f"Error analyzing image with Gemini: {e}")
            return ""
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        try:
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error splitting documents: {e}")
            raise e
    
    def extract_youtube_transcript(self, youtube_url: str) -> List[Document]:
        """
        Extract transcript from YouTube video
        Args:
            youtube_url: YouTube video URL
        Returns: List of Document objects with transcript
        """
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            import re
            
            logger.info(f"Extracting transcript from: {youtube_url}")
            
            # Extract video ID from URL
            video_id = None
            patterns = [
                r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
                r'(?:embed\/)([0-9A-Za-z_-]{11})',
                r'^([0-9A-Za-z_-]{11})$'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, youtube_url)
                if match:
                    video_id = match.group(1)
                    break
            
            if not video_id:
                raise ValueError("Could not extract video ID from URL")
            
            # Get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Combine transcript segments
            full_transcript = ' '.join([segment['text'] for segment in transcript_list])
            
            # Create document
            documents = [Document(
                page_content=full_transcript,
                metadata={
                    "source": youtube_url,
                    "video_id": video_id,
                    "type": "youtube"
                }
            )]
            
            logger.info(f"Extracted transcript: {len(full_transcript)} characters")
            return documents
            
        except Exception as e:
            logger.error(f"Error extracting YouTube transcript: {e}")
            raise Exception(f"Failed to extract transcript. Make sure the video has captions/subtitles enabled. Error: {str(e)}")
    
    def extract_website_content(self, url: str) -> List[Document]:
        """
        Extract text content from website
        Args:
            url: Website URL
        Returns: List of Document objects with website content
        """
        try:
            logger.info(f"Extracting content from: {url}")
            
            # Fetch webpage
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get title
            title = soup.title.string if soup.title else urlparse(url).netloc
            
            # Extract text from main content areas
            text_content = []
            
            # Try to find main content
            main_content = soup.find(['main', 'article', 'div'], class_=['content', 'main', 'article'])
            if main_content:
                text_content.append(main_content.get_text(separator='\\n', strip=True))
            else:
                # Fallback: extract all paragraphs and headings
                for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li']):
                    text = tag.get_text(strip=True)
                    if text and len(text) > 20:  # Filter out very short snippets
                        text_content.append(text)
            
            # Combine content
            full_text = f"Title: {title}\n\nURL: {url}\n\n" + "\n\n".join(text_content)
            
            # Create document
            documents = [Document(
                page_content=full_text,
                metadata={
                    "source": url,
                    "title": title,
                    "type": "website"
                }
            )]
            
            logger.info(f"Extracted website content: {len(full_text)} characters")
            return documents
            
        except Exception as e:
            logger.error(f"Error extracting website content: {e}")
            raise Exception(f"Failed to extract content from website. Error: {str(e)}")
    
    def process_youtube_video(self, youtube_url: str, user_id: int, doc_id: str = None) -> Dict:
        """
        Process YouTube video: extract transcript and store in vector DB
        Args:
            youtube_url: YouTube video URL
            user_id: User ID
            doc_id: Optional document ID
        Returns: Processing result dictionary
        """
        try:
            logger.info(f"Processing YouTube video for user {user_id}: {youtube_url}")
            
            # Generate doc_id if not provided
            if not doc_id:
                import hashlib
                doc_id = f"yt_{hashlib.sha256(youtube_url.encode()).hexdigest()[:16]}"
            
            # Extract video title (try to get from URL or use placeholder)
            filename = f"YouTube: {youtube_url.split('v=')[-1][:11]}"
            
            # Add to database
            document = db_manager.add_document(
                user_id=user_id,
                filename=filename,
                file_size=0,  # No file size for YouTube
                file_type="youtube",
                file_path=youtube_url
            )
            
            # Store doc_id from the created document
            doc_id = str(document.id)
            
            # Extract transcript
            documents = self.extract_youtube_transcript(youtube_url)
            
            # Split into chunks
            chunks = self.split_documents(documents)
            
            # Add metadata to chunks
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "doc_id": doc_id,
                    "user_id": user_id,
                    "filename": filename,
                    "chunk_index": i,
                    "source": filename,
                    "type": "youtube"
                })
            
            # Get user's vector store
            vectorstore = self.get_user_vectorstore(user_id)
            
            # Add to vector store
            texts = [chunk.page_content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            
            vectorstore.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            # Update document status
            db_manager.update_document_status(
                document_id=doc_id,
                processed=True,
                chunk_count=len(chunks)
            )
            
            logger.info(f"YouTube video processed successfully: {doc_id}")
            
            return {
                "status": "success",
                "doc_id": doc_id,
                "filename": filename,
                "chunks_created": len(chunks),
                "storage_url": youtube_url
            }
        
        except Exception as e:
            logger.error(f"Error processing YouTube video: {e}")
            
            # Update document status to failed
            if doc_id:
                import json
                db_manager.update_document_status(
                    document_id=doc_id,
                    processed=False,
                    metadata=json.dumps({"error": str(e)})
                )
            
            raise e
    
    def process_website(self, url: str, user_id: int, doc_id: str = None) -> Dict:
        """
        Process website: extract content and store in vector DB
        Args:
            url: Website URL
            user_id: User ID
            doc_id: Optional document ID
        Returns: Processing result dictionary
        """
        try:
            logger.info(f"Processing website for user {user_id}: {url}")
            
            # Generate doc_id if not provided
            if not doc_id:
                import hashlib
                doc_id = f"web_{hashlib.sha256(url.encode()).hexdigest()[:16]}"
            
            # Extract title from URL or use domain
            filename = f"Website: {urlparse(url).netloc}"
            
            # Add to database
            document = db_manager.add_document(
                user_id=user_id,
                filename=filename,
                file_size=0,  # No file size for websites
                file_type="website",
                file_path=url
            )
            
            # Store doc_id from the created document
            doc_id = str(document.id)
            
            # Extract website content
            documents = self.extract_website_content(url)
            
            # Split into chunks
            chunks = self.split_documents(documents)
            
            # Add metadata to chunks
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "doc_id": doc_id,
                    "user_id": user_id,
                    "filename": filename,
                    "chunk_index": i,
                    "source": filename,
                    "type": "website"
                })
            
            # Get user's vector store
            vectorstore = self.get_user_vectorstore(user_id)
            
            # Add to vector store
            texts = [chunk.page_content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            
            vectorstore.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            # Update document status
            db_manager.update_document_status(
                document_id=doc_id,
                processed=True,
                chunk_count=len(chunks)
            )
            
            logger.info(f"Website processed successfully: {doc_id}")
            
            return {
                "status": "success",
                "doc_id": doc_id,
                "filename": filename,
                "chunks_created": len(chunks),
                "storage_url": url
            }
        
        except Exception as e:
            logger.error(f"Error processing website: {e}")
            
            # Update document status to failed
            if doc_id:
                import json
                db_manager.update_document_status(
                    document_id=doc_id,
                    processed=False,
                    metadata=json.dumps({"error": str(e)})
                )
            
            raise e
    
    def get_user_vectorstore(self, user_id: int):
        """Get or create vector store for user - separate stores for each provider"""
        # Create provider-specific directory to avoid embedding mismatch
        provider_suffix = self.current_embedding_provider
        persist_directory = f"{config.CHROMA_PERSIST_DIR}/user_{user_id}_{provider_suffix}"
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name=f"user_{user_id}_{provider_suffix}_docs"
        )
        logger.info(f"Using vector store: {persist_directory} with {provider_suffix} embeddings")
        return vectorstore
    
    def process_document(self, file_path: str, user_id: int, filename: str, doc_id: str = None) -> Dict:
        """
        Complete document processing pipeline:
        1. Extract text
        2. Split into chunks
        3. Create embeddings
        4. Store in vector database
        5. Store metadata
        """
        try:
            logger.info(f"Processing document: {filename} for user: {user_id}")
            
            # Generate doc_id if not provided
            if not doc_id:
                doc_id = self.generate_doc_id(file_path)
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_type = filename.split('.')[-1].lower()
            
            # Upload to storage
            storage_url = storage.upload_file(file_path, user_id, filename)
            
            # Add to database with processing status
            document = db_manager.add_document(
                user_id=user_id,
                filename=filename,
                file_size=file_size,
                file_type=file_type,
                file_path=storage_url
            )
            
            # Store doc_id from the created document
            doc_id = str(document.id)
            
            # Extract text
            documents = self.extract_text_from_file(file_path, file_type)
            
            # Split into chunks
            chunks = self.split_documents(documents)
            
            # Add metadata to chunks
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "doc_id": doc_id,
                    "user_id": user_id,
                    "filename": filename,
                    "chunk_index": i,
                    "source": filename
                })
            
            # Get user's vector store
            vectorstore = self.get_user_vectorstore(user_id)
            
            # Add to vector store
            texts = [chunk.page_content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            
            vectorstore.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            # Update document status
            db_manager.update_document_status(
                document_id=doc_id,
                processed=True,
                chunk_count=len(chunks)
            )
            
            logger.info(f"Document processed successfully: {doc_id}")
            
            return {
                "status": "success",
                "doc_id": doc_id,
                "filename": filename,
                "chunks_created": len(chunks),
                "storage_url": storage_url
            }
        
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            
            # Update document status to failed
            if doc_id:
                import json
                db_manager.update_document_status(
                    document_id=doc_id,
                    processed=False,
                    metadata=json.dumps({"error": str(e)})
                )
            
            raise e
    
    def query(self, user_id: int, query: str, conversation_id: str = None, top_k: int = 3, ai_provider: str = None) -> Tuple[str, List[Dict], int]:
        """
        Query user's documents with RAG
        Args:
            user_id: User ID
            query: User's question
            conversation_id: Optional conversation ID for context
            top_k: Number of relevant documents to retrieve
            ai_provider: AI provider to use ('openai' or 'gemini'). If None, uses config default
        Returns: (answer, sources, tokens_used)
        """
        try:
            logger.info(f"Query from user {user_id}: {query}")
            
            # Use provided AI provider or fall back to config
            provider = ai_provider or config.AI_PROVIDER
            logger.info(f"Using AI provider: {provider}")
            
            # Get user's vector store
            vectorstore = self.get_user_vectorstore(user_id)
            
            # Check if vector store has any documents
            if vectorstore._collection.count() == 0:
                return "Please upload some documents first to chat with them! 📁", [], 0
            
            # Get conversation history if conversation_id provided
            chat_history = []
            if conversation_id:
                messages = db_manager.get_conversation_messages(conversation_id)
                # Convert to (question, answer) pairs for last 5 exchanges
                for i in range(0, len(messages) - 1, 2):
                    if i + 1 < len(messages):
                        user_msg = messages[i]
                        assistant_msg = messages[i + 1]
                        if user_msg.role == "user" and assistant_msg.role == "assistant":
                            chat_history.append((user_msg.content, assistant_msg.content))
                
                # Keep only last 5 exchanges
                chat_history = chat_history[-5:]
            
            # Query based on selected AI provider
            if provider == "gemini":
                # Use Gemini for RAG
                result = self._query_with_gemini(query, vectorstore, chat_history, top_k)
            else:
                # Use OpenAI for RAG
                result = self._query_with_openai(query, vectorstore, chat_history, top_k)
            
            # Format sources
            sources = []
            for doc in result.get("source_documents", []):
                sources.append({
                    "filename": doc.metadata.get("filename", "Unknown"),
                    "content": doc.page_content[:300],  # First 300 chars
                    "page": doc.metadata.get("page", "N/A"),
                    "chunk_index": doc.metadata.get("chunk_index", 0)
                })
            
            # Estimate tokens (rough estimate)
            tokens = len(query.split()) + len(result["answer"].split()) + sum(len(s["content"].split()) for s in sources)
            
            logger.info(f"Query completed. Tokens used: ~{tokens}")
            
            return result["answer"], sources, tokens
        
        except Exception as e:
            logger.error(f"Error during query: {e}")
            return f"Sorry, I encountered an error: {str(e)}", [], 0
    
    def delete_document(self, user_id: int, doc_id: str) -> bool:
        """Delete document from vector store and storage"""
        try:
            logger.info(f"Deleting document: {doc_id} for user: {user_id}")
            
            # Get document metadata
            documents = db_manager.get_user_documents(user_id)
            document = next((d for d in documents if str(d.id) == doc_id), None)
            
            if not document:
                logger.warning(f"Document not found: {doc_id}")
                return False
            
            # Delete from vector store
            vectorstore = self.get_user_vectorstore(user_id)
            
            # Get all chunk IDs for this document
            # ChromaDB doesn't support metadata filtering in delete, so we need to get IDs first
            results = vectorstore._collection.get(
                where={"doc_id": doc_id}
            )
            
            if results and results['ids']:
                vectorstore._collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks from vector store")
            
            # Delete from storage
            storage.delete_file(document.file_path)
            
            # Delete from database
            db_manager.delete_document(doc_id)
            
            logger.info(f"Document deleted successfully: {doc_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    def get_user_document_stats(self, user_id: int) -> Dict:
        """Get statistics about user's documents"""
        try:
            documents = db_manager.get_user_documents(user_id)
            
            total_size = sum(doc.file_size for doc in documents)
            total_chunks = sum(doc.chunk_count for doc in documents)
            
            by_status = {}
            for doc in documents:
                status = "completed" if doc.processed else "processing"  # Convert boolean to status string
                by_status[status] = by_status.get(status, 0) + 1
            
            return {
                "total_documents": len(documents),
                "total_size_mb": total_size / (1024 * 1024),
                "total_chunks": total_chunks,
                "by_status": by_status
            }
        except Exception as e:
            logger.error(f"Error getting document stats: {e}")
            return {}

    def _query_with_openai(self, query: str, vectorstore, chat_history: List, top_k: int) -> Dict:
        """Query using OpenAI API"""
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": top_k}
            ),
            return_source_documents=True,
            verbose=config.DEBUG
        )
        
        result = qa_chain({
            "question": query,
            "chat_history": chat_history
        })
        return result
    
    def _query_with_gemini(self, query: str, vectorstore, chat_history: List, top_k: int) -> Dict:
        """Query using Gemini API"""
        # Get relevant documents
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k}
        )
        relevant_docs = retriever.get_relevant_documents(query)
        
        # Build context from relevant documents
        context = "\n\n".join([
            f"Document: {doc.metadata.get('filename', 'Unknown')}\n{doc.page_content}"
            for doc in relevant_docs
        ])
        
        # Build chat history context
        history_context = ""
        if chat_history:
            history_context = "\n\nPrevious conversation:\n"
            for q, a in chat_history:
                history_context += f"User: {q}\nAssistant: {a}\n"
        
        # Create prompt
        prompt = f"""You are a helpful assistant that answers questions based on the provided documents.
        
Context from documents:
{context}
{history_context}

User question: {query}

Please provide a detailed answer based on the documents. If the answer is not in the documents, say so."""
        
        # Generate response with Gemini
        response = self.model.generate_content(prompt)
        
        return {
            "answer": response.text,
            "source_documents": relevant_docs
        }
    
    def summarize_document(self, user_id: int, doc_id: str, ai_provider: str = None) -> str:
        """
        Generate a one-click summary of a document
        Args:
            user_id: User ID
            doc_id: Document ID
            ai_provider: AI provider to use ('openai' or 'gemini')
        Returns: Summary text
        """
        try:
            logger.info(f"Generating summary for doc {doc_id}, user {user_id}")
            
            # Get document metadata
            documents = db_manager.get_user_documents(user_id)
            document = next((d for d in documents if str(d.id) == doc_id), None)
            
            if not document:
                raise ValueError(f"Document not found: {doc_id}")
            
            # Get vector store and retrieve all chunks for this document
            vectorstore = self.get_user_vectorstore(user_id)
            
            # Get all chunks for this document
            results = vectorstore._collection.get(
                where={"doc_id": doc_id},
                limit=50  # Limit to first 50 chunks to avoid token limits
            )
            
            if not results or not results['documents']:
                raise ValueError(f"No content found for document: {doc_id}")
            
            # Combine chunks into text
            full_text = "\n\n".join(results['documents'][:10])  # Use first 10 chunks for summary
            
            # Create summary prompt
            prompt = f"""Please provide a comprehensive summary of the following document.

Document: {document.filename}

Content:
{full_text}

Generate a summary that includes:
1. Main topics and key points
2. Important facts and figures
3. Key takeaways
4. Overall conclusion

Summary:"""
            
            # Use provider
            provider = ai_provider or config.AI_PROVIDER
            
            if provider == "gemini":
                response = self.model.generate_content(prompt)
                summary = response.text
            else:
                # OpenAI
                response = self.llm.invoke(prompt)
                summary = response.content
            
            logger.info(f"Summary generated successfully for {doc_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise e
    
    def query_multi_documents(self, user_id: int, query: str, doc_ids: List[str], conversation_id: str = None, top_k: int = 4, ai_provider: str = None) -> Tuple[str, List[Dict], int]:
        """
        Query across multiple documents simultaneously
        Args:
            user_id: User ID
            query: User's question
            doc_ids: List of document IDs to search across
            conversation_id: Optional conversation ID for context
            top_k: Number of relevant chunks to retrieve per document
            ai_provider: AI provider to use
        Returns: (answer, sources, tokens_used)
        """
        try:
            logger.info(f"Multi-doc query from user {user_id} across {len(doc_ids)} documents: {query}")
            
            # Get vector store
            vectorstore = self.get_user_vectorstore(user_id)
            
            # Search across all specified documents
            all_results = []
            for doc_id in doc_ids:
                # Search within each document
                try:
                    results = vectorstore._collection.query(
                        query_embeddings=[self.embeddings.embed_query(query)],
                        where={"doc_id": doc_id},
                        n_results=top_k
                    )
                    
                    if results and results['documents']:
                        for i, doc_text in enumerate(results['documents'][0]):
                            all_results.append(Document(
                                page_content=doc_text,
                                metadata=results['metadatas'][0][i] if results['metadatas'] else {}
                            ))
                except Exception as e:
                    logger.warning(f"Error querying doc {doc_id}: {e}")
                    continue
            
            if not all_results:
                return "I couldn't find any relevant information in the selected documents.", [], 0
            
            # Load conversation history if provided
            chat_history = []
            if conversation_id:
                messages = db_manager.get_conversation_messages(conversation_id)
                for i in range(0, len(messages) - 1, 2):
                    if i + 1 < len(messages):
                        user_msg = messages[i]
                        assistant_msg = messages[i + 1]
                        if user_msg.role == "user" and assistant_msg.role == "assistant":
                            chat_history.append((user_msg.content, assistant_msg.content))
                chat_history = chat_history[-5:]
            
            # Build context from documents
            context = "\n\n".join([f"[Document {i+1} from {doc.metadata.get('filename', 'Unknown')}]: {doc.page_content}" for i, doc in enumerate(all_results[:10])])
            
            # Build prompt
            history_text = ""
            if chat_history:
                history_text = "\n".join([f"User: {q}\nAssistant: {a}" for q, a in chat_history])
                history_text = f"\nPrevious conversation:\n{history_text}\n"
            
            prompt = f"""You are a helpful AI assistant. Answer the question based on the provided documents from multiple sources.

{history_text}
Documents:
{context}

Question: {query}

Answer based on the documents above. Be specific and mention which document each piece of information comes from."""
            
            # Query based on provider
            provider = ai_provider or config.AI_PROVIDER
            
            if provider == "gemini":
                response = self.model.generate_content(prompt)
                answer = response.text
            else:
                response = self.llm.invoke(prompt)
                answer = response.content
            
            # Format sources
            sources = []
            for doc in all_results[:6]:  # Show top 6 sources
                sources.append({
                    "filename": doc.metadata.get("filename", "Unknown"),
                    "content": doc.page_content[:300],
                    "page": doc.metadata.get("page", "N/A"),
                    "chunk_index": doc.metadata.get("chunk_index", 0),
                    "doc_id": doc.metadata.get("doc_id", "")
                })
            
            tokens = len(query.split()) + len(answer.split()) + sum(len(s["content"].split()) for s in sources)
            
            logger.info(f"Multi-doc query completed. Tokens used: ~{tokens}")
            
            return answer, sources, tokens
        
        except Exception as e:
            logger.error(f"Error during multi-doc query: {e}")
            return f"Sorry, I encountered an error: {str(e)}", [], 0
    
    def generate_visualization(self, user_id: int, doc_id: str, query: str):
        """Generate interactive data visualizations from Excel/CSV files"""
        try:
            logger.info(f"Generating visualization for doc {doc_id}")
            
            # Get the document
            doc = db_manager.get_document(user_id, doc_id)
            if not doc:
                return None, "Document not found"
            
            # Check if it's a data file
            file_ext = doc.filename.split('.')[-1].lower()
            if file_ext not in ['csv', 'xlsx', 'xls']:
                return None, "Only Excel and CSV files support visualization"
            
            # Load the data
            file_path = storage.get_document_path(user_id, doc_id, doc.filename)
            if file_ext == 'csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            logger.info(f"Loaded data: {df.shape}")
            
            # Use AI to determine the best visualization
            prompt = f"""Based on this query: "{query}"
            
Dataset info:
- Columns: {', '.join(df.columns.tolist())}
- Shape: {df.shape[0]} rows × {df.shape[1]} columns
- Data types: {df.dtypes.to_dict()}
- First few rows: {df.head().to_dict()}

Determine the best visualization and respond in JSON format:
{{
    "chart_type": "bar|line|pie|scatter|histogram",
    "x_column": "column name for x-axis",
    "y_column": "column name for y-axis (or value column)",
    "title": "descriptive chart title",
    "aggregate": "sum|mean|count|none"
}}

Choose the chart type based on:
- bar: comparing categories
- line: showing trends over time
- pie: showing proportions
- scatter: showing relationships between two numeric variables
- histogram: showing distribution of a single variable"""
            
            # Get AI recommendation
            if config.AI_PROVIDER == "gemini":
                response = self.model.generate_content(prompt)
                recommendation = response.text
            else:
                response = self.llm.invoke(prompt)
                recommendation = response.content
            
            # Extract JSON from response
            import re
            import json
            json_match = re.search(r'\{[^{}]*\}', recommendation)
            if not json_match:
                return None, "Could not determine visualization type"
            
            viz_config = json.loads(json_match.group())
            
            chart_type = viz_config.get('chart_type', 'bar')
            x_col = viz_config.get('x_column')
            y_col = viz_config.get('y_column')
            title = viz_config.get('title', 'Data Visualization')
            aggregate = viz_config.get('aggregate', 'none')
            
            # Validate columns exist
            if x_col and x_col not in df.columns:
                x_col = df.columns[0]
            if y_col and y_col not in df.columns:
                y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
            
            # Prepare data with aggregation if needed
            if aggregate != 'none' and x_col and y_col:
                if aggregate == 'sum':
                    plot_df = df.groupby(x_col)[y_col].sum().reset_index()
                elif aggregate == 'mean':
                    plot_df = df.groupby(x_col)[y_col].mean().reset_index()
                elif aggregate == 'count':
                    plot_df = df.groupby(x_col)[y_col].count().reset_index()
                else:
                    plot_df = df
            else:
                plot_df = df
            
            # Generate the visualization
            fig = None
            
            if chart_type == 'bar':
                fig = px.bar(plot_df, x=x_col, y=y_col, title=title)
            elif chart_type == 'line':
                fig = px.line(plot_df, x=x_col, y=y_col, title=title)
            elif chart_type == 'pie':
                fig = px.pie(plot_df, names=x_col, values=y_col, title=title)
            elif chart_type == 'scatter':
                fig = px.scatter(plot_df, x=x_col, y=y_col, title=title)
            elif chart_type == 'histogram':
                fig = px.histogram(plot_df, x=x_col, title=title)
            else:
                fig = px.bar(plot_df, x=x_col, y=y_col, title=title)
            
            # Enhance the figure
            fig.update_layout(
                template="plotly_dark",
                hovermode='x unified',
                showlegend=True
            )
            
            logger.info(f"Generated {chart_type} chart successfully")
            
            return fig, f"Generated {chart_type} chart: {title}"
            
        except Exception as e:
            logger.error(f"Error generating visualization: {e}")
            return None, f"Error: {str(e)}"
    
    def convert_to_powerpoint(self, user_id: int, doc_id: str):
        """Convert PDF or Word document to PowerPoint presentation"""
        try:
            logger.info(f"Converting document {doc_id} to PowerPoint")
            
            # Get the document
            doc = db_manager.get_document(user_id, doc_id)
            if not doc:
                return None, "Document not found"
            
            # Check if it's a supported file type
            file_ext = doc.filename.split('.')[-1].lower()
            if file_ext not in ['pdf', 'docx', 'txt']:
                return None, "Only PDF, Word, and Text files can be converted to PowerPoint"
            
            # Extract content from document
            file_path = storage.get_document_path(user_id, doc_id, doc.filename)
            
            if file_ext == 'pdf':
                import PyPDF2
                text_content = []
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        text_content.append({"page": page_num + 1, "content": text})
            elif file_ext == 'docx':
                doc_file = docx.Document(file_path)
                text_content = [{"section": i+1, "content": para.text} for i, para in enumerate(doc_file.paragraphs) if para.text.strip()]
            else:  # txt
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                text_content = [{"section": 1, "content": content}]
            
            # Combine all content
            full_text = "\n\n".join([item['content'] for item in text_content])
            
            # Use AI to structure the content into slides
            prompt = f"""Analyze this document and create a PowerPoint presentation structure.
Document content:
{full_text[:8000]}  # Limit to first 8000 chars

Create a JSON structure for slides with this format:
{{
    "title_slide": {{
        "title": "Main presentation title",
        "subtitle": "Brief subtitle or description"
    }},
    "content_slides": [
        {{
            "title": "Slide title",
            "bullets": ["Point 1", "Point 2", "Point 3"]
        }}
    ]
}}

Guidelines:
- Create 5-10 content slides
- Each slide should have 3-5 bullet points
- Bullet points should be concise (1-2 lines)
- Cover key topics from the document
- Maintain logical flow"""
            
            # Get AI to structure the content
            if config.AI_PROVIDER == "gemini":
                response = self.model.generate_content(prompt)
                slide_structure = response.text
            else:
                response = self.llm.invoke(prompt)
                slide_structure = response.content
            
            # Extract JSON
            import re
            import json
            json_match = re.search(r'\{.*\}', slide_structure, re.DOTALL)
            if not json_match:
                return None, "Could not generate slide structure"
            
            slides_data = json.loads(json_match.group())
            
            # Create PowerPoint presentation
            prs = Presentation()
            
            # Slide dimensions
            prs.slide_width = Inches(10)
            prs.slide_height = Inches(7.5)
            
            # Title Slide
            title_slide_layout = prs.slide_layouts[0]
            slide = prs.slides.add_slide(title_slide_layout)
            title = slide.shapes.title
            subtitle = slide.placeholders[1]
            
            title.text = slides_data['title_slide']['title']
            subtitle.text = slides_data['title_slide']['subtitle']
            
            # Style title slide
            title.text_frame.paragraphs[0].font.size = Pt(44)
            title.text_frame.paragraphs[0].font.bold = True
            title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 32, 96)
            
            subtitle.text_frame.paragraphs[0].font.size = Pt(24)
            subtitle.text_frame.paragraphs[0].font.color.rgb = RGBColor(68, 84, 106)
            
            # Content Slides
            bullet_slide_layout = prs.slide_layouts[1]
            
            for slide_info in slides_data['content_slides']:
                slide = prs.slides.add_slide(bullet_slide_layout)
                title = slide.shapes.title
                body = slide.placeholders[1]
                
                title.text = slide_info['title']
                title.text_frame.paragraphs[0].font.size = Pt(32)
                title.text_frame.paragraphs[0].font.bold = True
                title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 32, 96)
                
                tf = body.text_frame
                tf.clear()
                
                for bullet in slide_info['bullets']:
                    p = tf.add_paragraph()
                    p.text = bullet
                    p.level = 0
                    p.font.size = Pt(20)
                    p.font.color.rgb = RGBColor(68, 84, 106)
                    p.space_before = Pt(12)
            
            # Save PowerPoint
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx', mode='wb') as tmp:
                prs.save(tmp.name)
                pptx_path = tmp.name
            
            logger.info(f"Created PowerPoint with {len(prs.slides)} slides")
            
            return pptx_path, f"Created presentation with {len(prs.slides)} slides"
            
        except Exception as e:
            logger.error(f"Error converting to PowerPoint: {e}")
            return None, f"Error: {str(e)}"
    
    def generate_sql_query(self, user_query: str, connection_string: str, db_type: str) -> str:
        """Generate SQL query from natural language using AI"""
        try:
            from sqlalchemy import create_engine, inspect, text
            
            # Get database schema
            engine = create_engine(connection_string)
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            # Build schema description
            schema_info = []
            for table in tables:
                columns = inspector.get_columns(table)
                col_list = [f"{col['name']} ({col['type']})" for col in columns]
                schema_info.append(f"Table: {table}\nColumns: {', '.join(col_list)}")
            
            schema_text = "\n\n".join(schema_info)
            
            # Create prompt for SQL generation
            prompt = f"""You are a SQL expert. Generate a SQL query based on the user's question.

Database Type: {db_type}
Database Schema:
{schema_text}

User Question: {user_query}

Requirements:
1. Generate ONLY a SELECT query (no INSERT, UPDATE, DELETE, DROP)
2. Use proper SQL syntax for {db_type}
3. Include appropriate WHERE, JOIN, ORDER BY, LIMIT clauses as needed
4. Return ONLY the SQL query, no explanations
5. Do not use markdown code blocks, just the raw SQL

SQL Query:"""
            
            # Generate SQL using AI
            if config.AI_PROVIDER == "gemini":
                response = self.model.generate_content(prompt)
                sql_query = response.text.strip()
            else:
                response = self.llm.invoke(prompt)
                sql_query = response.content.strip()
            
            # Clean up the SQL query
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            
            # Safety check
            if not sql_query.upper().startswith('SELECT'):
                raise ValueError("Generated query is not a SELECT statement")
            
            logger.info(f"Generated SQL query: {sql_query}")
            return sql_query
        
        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            raise e

# Initialize global RAG engine
rag_engine = RAGEngine()
