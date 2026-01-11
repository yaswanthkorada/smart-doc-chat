"""
Multi-Agent RAG Engine
Uses specialized AI agents for ingestion, retrieval, and generation
Each agent is an expert in their domain with specific tools and reasoning
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from config import config
from utils.agent_tools import (
    get_ingestion_tools,
    get_retrieval_tools,
    get_generation_tools,
    DocumentAnalyzerTool,
    TextExtractorTool,
    DocumentChunkerTool,
    QueryAnalyzerTool,
    VectorSearchTool,
    CitationFormatterTool,
    ResponseValidatorTool
)

# Try importing embedding models
try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI not available")

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    logger.warning("Hugging Face not available")

try:
    from langchain_openai import OpenAIEmbeddings
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI embeddings not available")


class MultiAgentRAGEngine:
    """
    Multi-Agent RAG Engine with specialized agents:
    1. Ingestion Agent - Document processing expert
    2. Retrieval Agent - Search and analysis expert  
    3. Generation Agent - Response writing expert
    """
    
    def __init__(self):
        """Initialize the multi-agent system"""
        logger.info("🤖 Initializing Multi-Agent RAG Engine...")
        
        # Initialize LLM based on provider
        self.current_provider = config.AI_PROVIDER
        self.llm = self._initialize_llm()
        
        # Initialize embeddings
        self.embeddings = self._initialize_embeddings()
        
        # Create specialized agents
        self.ingestion_agent = self._create_ingestion_agent()
        self.retrieval_agent = self._create_retrieval_agent()
        self.generation_agent = self._create_generation_agent()
        
        logger.info(f"✅ Multi-Agent RAG Engine initialized with {self.current_provider}")
        logger.info(f"   Ingestion Agent: {self.ingestion_agent.role}")
        logger.info(f"   Retrieval Agent: {self.retrieval_agent.role}")
        logger.info(f"   Generation Agent: {self.generation_agent.role}")
    
    def _initialize_llm(self):
        """Initialize language model based on provider"""
        if self.current_provider == "gemini":
            if not GEMINI_AVAILABLE or not config.GEMINI_API_KEY:
                raise ValueError("Gemini not available. Check API key.")
            
            genai.configure(api_key=config.GEMINI_API_KEY)
            return ChatGoogleGenerativeAI(
                model=config.GEMINI_MODEL,
                google_api_key=config.GEMINI_API_KEY,
                temperature=0.7
            )
        else:  # OpenAI
            if not OPENAI_AVAILABLE or not config.OPENAI_API_KEY:
                raise ValueError("OpenAI not available. Check API key.")
            
            return ChatOpenAI(
                model=config.OPENAI_MODEL,
                api_key=config.OPENAI_API_KEY,
                temperature=0.7
            )
    
    def _initialize_embeddings(self):
        """Initialize embeddings based on provider"""
        embedding_provider = getattr(config, 'EMBEDDING_PROVIDER', 'huggingface')
        
        if embedding_provider == "huggingface" and HUGGINGFACE_AVAILABLE:
            logger.info("Using HuggingFace embeddings (FREE & LOCAL)")
            return HuggingFaceEmbeddings(
                model_name=config.HUGGINGFACE_MODEL,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        elif embedding_provider == "gemini" and GEMINI_AVAILABLE:
            logger.info("Using Gemini embeddings (FREE)")
            genai.configure(api_key=config.GEMINI_API_KEY)
            return GoogleGenerativeAIEmbeddings(
                model=config.GEMINI_EMBEDDING_MODEL,
                google_api_key=config.GEMINI_API_KEY
            )
        else:
            logger.info("Using OpenAI embeddings")
            return OpenAIEmbeddings(
                model=config.OPENAI_EMBEDDING_MODEL,
                api_key=config.OPENAI_API_KEY
            )
    
    def _create_ingestion_agent(self) -> Agent:
        """Create the document ingestion specialist agent"""
        return Agent(
            role='Document Processing Specialist',
            goal='Extract and prepare documents with maximum quality and intelligence',
            backstory="""You are a world-class expert in document processing with 15+ years of experience.
            You have deep knowledge of PDF structures, Word documents, PowerPoint presentations, 
            Excel spreadsheets, and web content. You understand:
            
            - How to identify document types and structures
            - Optimal extraction strategies for different formats
            - How to preserve important formatting and metadata
            - When to use OCR for scanned documents
            - How to handle corrupted or complex files
            - The best chunking strategies for different content types
            
            You take pride in delivering high-quality, clean, well-structured data that makes
            downstream processing efficient and accurate. You always analyze before processing
            and choose the best approach for each unique document.""",
            llm=self.llm,
            tools=get_ingestion_tools(),
            verbose=True,
            allow_delegation=False,
            max_iter=10
        )
    
    def _create_retrieval_agent(self) -> Agent:
        """Create the information retrieval specialist agent"""
        return Agent(
            role='Information Retrieval Specialist',
            goal='Find the most relevant and accurate information for user queries',
            backstory="""You are an elite search and information retrieval expert with a PhD in 
            Information Science and 10+ years of experience. You excel at:
            
            - Understanding user intent even from vague queries
            - Reformulating queries for better search results
            - Performing semantic search with high precision
            - Ranking results by true relevance, not just similarity scores
            - Identifying when information is missing or incomplete
            - Cross-referencing multiple sources for accuracy
            - Filtering out noise and irrelevant information
            
            You have an uncanny ability to find exactly what users need, even when they
            don't express it clearly. You never return irrelevant results and always
            validate the quality of your findings before passing them forward.""",
            llm=self.llm,
            tools=get_retrieval_tools(),
            verbose=True,
            allow_delegation=False,
            max_iter=10
        )
    
    def _create_generation_agent(self) -> Agent:
        """Create the response generation specialist agent"""
        return Agent(
            role='Response Generation Expert',
            goal='Create clear, accurate, well-structured responses with proper citations',
            backstory="""You are a master communicator and technical writer with expertise in
            synthesizing complex information into clear, accessible content. You have:
            
            - 15+ years of experience in technical writing and communication
            - Deep understanding of different audience needs
            - Expertise in citation and source attribution
            - Strong fact-checking and accuracy validation skills
            - Ability to structure information logically
            - Talent for explaining complex topics simply
            
            You take pride in creating responses that are:
            - Factually accurate (no hallucinations)
            - Well-structured with clear sections
            - Properly cited with sources
            - Easy to understand
            - Complete but concise
            
            You NEVER make up information and always base your responses strictly on
            the provided source material. If information is missing, you clearly state this.""",
            llm=self.llm,
            tools=get_generation_tools(),
            verbose=True,
            allow_delegation=False,
            max_iter=10
        )
    
    def process_document(self, file_path: str, user_id: str, filename: str) -> Dict[str, Any]:
        """
        Process a document using the ingestion agent
        
        Args:
            file_path: Path to the document file
            user_id: User ID for storage organization
            filename: Original filename
            
        Returns:
            Processing result with metadata
        """
        logger.info(f"📄 Processing document with Ingestion Agent: {filename}")
        
        # Create ingestion task
        ingestion_task = Task(
            description=f"""Process this document with expert precision:
            
            File: {file_path}
            User: {user_id}
            Filename: {filename}
            
            Your mission:
            1. Analyze the document type, structure, and content
            2. Choose the optimal extraction strategy
            3. Extract all text and important metadata
            4. Create intelligent chunks suitable for embedding
            5. Preserve important context and structure
            
            Use your tools:
            - Document Analyzer: First analyze the document
            - Text Extractor: Extract based on your analysis
            - Document Chunker: Create optimal chunks
            
            Return a detailed processing report including:
            - Document analysis summary
            - Extraction method used
            - Number of chunks created
            - Quality assessment
            - Any issues encountered""",
            agent=self.ingestion_agent,
            expected_output="Detailed processing report with extracted text and chunks"
        )
        
        # Create crew with just ingestion agent
        ingestion_crew = Crew(
            agents=[self.ingestion_agent],
            tasks=[ingestion_task],
            process=Process.sequential,
            verbose=2
        )
        
        # Execute ingestion
        try:
            result = ingestion_crew.kickoff()
            
            # Now do the actual processing based on agent's recommendations
            doc_id = self._generate_doc_id(file_path)
            extracted_docs = self._extract_and_chunk(file_path, filename)
            
            # Store in vector database
            collection_name = f"user_{user_id}_{self.current_provider}"
            self._store_in_vectordb(extracted_docs, collection_name, doc_id, filename)
            
            processing_result = {
                "success": True,
                "doc_id": doc_id,
                "filename": filename,
                "chunks_created": len(extracted_docs),
                "collection_name": collection_name,
                "agent_analysis": str(result)
            }
            
            logger.info(f"✅ Document processed: {len(extracted_docs)} chunks created")
            return processing_result
            
        except Exception as e:
            logger.error(f"❌ Document processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    def query(self, question: str, user_id: str, document_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Answer a question using retrieval and generation agents
        
        Args:
            question: User's question
            user_id: User ID for collection access
            document_ids: Optional list of specific document IDs to search
            
        Returns:
            Response with answer and metadata
        """
        logger.info(f"❓ Processing query with Multi-Agent System: {question}")
        
        collection_name = f"user_{user_id}_{self.current_provider}"
        
        # Task 1: Retrieval Agent finds relevant information
        retrieval_task = Task(
            description=f"""Find the most relevant information for this query:
            
            Query: "{question}"
            Collection: {collection_name}
            Documents: {document_ids if document_ids else 'All documents'}
            
            Your mission:
            1. Analyze the query to understand user intent
            2. Use Query Analyzer tool to understand what user really wants
            3. Search the vector database using Vector Search tool
            4. Retrieve the top 5 most relevant chunks
            5. Validate that results are actually relevant
            6. If results are poor quality, try reformulating the search
            
            Return:
            - Retrieved chunks with relevance scores
            - Source metadata (filename, page numbers)
            - Confidence assessment
            - Any issues or limitations""",
            agent=self.retrieval_agent,
            expected_output="List of relevant chunks with metadata and confidence scores"
        )
        
        # Task 2: Generation Agent creates the response
        generation_task = Task(
            description=f"""Create an excellent response to this query:
            
            Query: "{question}"
            
            Using the information retrieved by the Retrieval Agent, create a response that is:
            
            1. **Accurate**: Based strictly on retrieved information
            2. **Clear**: Well-structured and easy to understand
            3. **Complete**: Addresses all aspects of the question
            4. **Cited**: Include proper source citations
            5. **Honest**: If information is insufficient, say so
            
            Structure your response:
            - Start with direct answer
            - Provide supporting details
            - Add citations at the end
            
            Use your tools:
            - Citation Formatter: Add proper citations
            - Response Validator: Validate against sources
            
            CRITICAL: Never hallucinate or make up information. Only use what was retrieved.""",
            agent=self.generation_agent,
            expected_output="Well-formatted response with citations",
            context=[retrieval_task]
        )
        
        # Create crew with retrieval and generation agents
        query_crew = Crew(
            agents=[self.retrieval_agent, self.generation_agent],
            tasks=[retrieval_task, generation_task],
            process=Process.sequential,
            verbose=2
        )
        
        # Execute query
        try:
            result = query_crew.kickoff()
            
            # Extract agent outputs
            response_text = str(result)
            
            # Also do actual vector search for sources
            sources = self._get_sources(question, collection_name, document_ids)
            
            query_result = {
                "success": True,
                "response": response_text,
                "sources": sources,
                "agent_process": "Multi-agent collaboration completed"
            }
            
            logger.info("✅ Query processed successfully by agents")
            return query_result
            
        except Exception as e:
            logger.error(f"❌ Query processing failed: {e}")
            return {
                "success": False,
                "response": f"I encountered an error processing your question: {str(e)}",
                "error": str(e)
            }
    
    def _generate_doc_id(self, file_path: str) -> str:
        """Generate unique document ID"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return f"doc_{file_hash[:16]}"
        except:
            return f"doc_{hashlib.md5(str(file_path).encode()).hexdigest()[:16]}"
    
    def _extract_and_chunk(self, file_path: str, filename: str) -> List[Document]:
        """Extract text and create chunks"""
        from utils.rag_engine import RAGEngine
        
        # Use existing extraction logic
        temp_engine = RAGEngine()
        file_type = Path(file_path).suffix.lower().strip('.')
        
        try:
            documents = temp_engine.extract_text_from_file(file_path, file_type)
            chunks = temp_engine.split_documents(documents)
            
            # Add filename to metadata
            for chunk in chunks:
                chunk.metadata['filename'] = filename
                chunk.metadata['doc_id'] = self._generate_doc_id(file_path)
            
            return chunks
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            return []
    
    def _store_in_vectordb(self, documents: List[Document], collection_name: str, 
                          doc_id: str, filename: str):
        """Store documents in ChromaDB"""
        try:
            persist_dir = os.path.join(config.CHROMA_PERSIST_DIR, collection_name)
            os.makedirs(persist_dir, exist_ok=True)
            
            # Create or load vectorstore
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=persist_dir,
                collection_name=collection_name
            )
            
            logger.info(f"✅ Stored {len(documents)} chunks in {collection_name}")
            
        except Exception as e:
            logger.error(f"Vector storage error: {e}")
            raise
    
    def _get_sources(self, query: str, collection_name: str, 
                    document_ids: Optional[List[str]] = None) -> List[Dict]:
        """Get source chunks for a query"""
        try:
            persist_dir = os.path.join(config.CHROMA_PERSIST_DIR, collection_name)
            
            if not os.path.exists(persist_dir):
                return []
            
            vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=self.embeddings,
                collection_name=collection_name
            )
            
            # Search
            results = vectorstore.similarity_search_with_score(query, k=5)
            
            sources = []
            for doc, score in results:
                sources.append({
                    "content": doc.page_content[:300],
                    "filename": doc.metadata.get('filename', 'Unknown'),
                    "page": doc.metadata.get('page', 'N/A'),
                    "score": round(float(score), 3)
                })
            
            return sources
            
        except Exception as e:
            logger.error(f"Source retrieval error: {e}")
            return []
    
    def update_provider(self, new_provider: str):
        """Switch AI provider"""
        logger.info(f"🔄 Switching provider from {self.current_provider} to {new_provider}")
        
        self.current_provider = new_provider
        self.llm = self._initialize_llm()
        self.embeddings = self._initialize_embeddings()
        
        # Recreate agents with new LLM
        self.ingestion_agent = self._create_ingestion_agent()
        self.retrieval_agent = self._create_retrieval_agent()
        self.generation_agent = self._create_generation_agent()
        
        logger.info(f"✅ Provider switched to {new_provider}")
    
    def get_collection_name(self, user_id: str) -> str:
        """Get collection name for user"""
        return f"user_{user_id}_{self.current_provider}"


# Create global instance
agent_rag_engine = MultiAgentRAGEngine()
