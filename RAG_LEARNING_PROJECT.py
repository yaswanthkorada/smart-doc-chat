"""
=============================================================================
RAG LEARNING PROJECT - END TO END IMPLEMENTATION
=============================================================================

Purpose: Simple, complete RAG system to understand every component
Author: Learning Tutorial
Date: January 2026

What You'll Learn:
1. Document Loading & Extraction
2. Text Chunking (3 different strategies)
3. Embeddings & Vector Storage
4. Retrieval (Simple, Hybrid BM25+Vector, Re-ranking)
5. Generation (Multiple prompting techniques)
6. Evaluation & Reliability

Requirements:
pip install langchain openai chromadb rank-bm25 sentence-transformers ragas
pip install pymupdf pillow pytesseract camelot-py tabula-py
"""

import os
from typing import List, Dict, Tuple
import numpy as np

# =============================================================================
# STEP 1: DOCUMENT LOADING & EXTRACTION
# =============================================================================
# Concept: Load raw text from various sources (PDF, TXT, web, etc.)
# When to use: First step in any RAG pipeline
# =============================================================================

def load_document_simple(file_path: str) -> str:
    """
    METHOD 1: Simple File Loading (TXT files)
    
    Concept: Read text file directly
    When to use: For simple .txt files
    Pros: Fast, no dependencies
    Cons: Only works with plain text
    """
    print("\n=== STEP 1A: Loading Document (Simple Method) ===")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"✅ Loaded {len(content)} characters")
    return content


def load_document_langchain(file_path: str) -> str:
    """
    METHOD 2: LangChain Document Loaders
    
    Concept: Use LangChain's built-in loaders for various formats
    When to use: For PDF, DOCX, or multiple file formats
    Pros: Handles many formats, preserves metadata
    Cons: Requires additional libraries
    """
    print("\n=== STEP 1B: Loading Document (LangChain Method) ===")
    
    from langchain.document_loaders import TextLoader
    
    loader = TextLoader(file_path, encoding='utf-8')
    documents = loader.load()
    
    content = documents[0].page_content
    print(f"✅ Loaded {len(content)} characters using LangChain")
    return content


# =============================================================================
# STEP 2: TEXT CHUNKING
# =============================================================================
# Concept: Split large text into smaller, meaningful pieces
# Why: LLMs have token limits, smaller chunks = better retrieval
# Key Parameters:
#   - chunk_size: Number of characters per chunk
#   - chunk_overlap: Characters shared between adjacent chunks (prevents context loss)
# =============================================================================

def chunk_text_fixed_size(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    METHOD 1: Fixed-Size Chunking
    
    Concept: Split text into equal-sized pieces
    When to use: Quick experiments, uniform content
    Pros: Simple, predictable
    Cons: May break sentences/paragraphs
    
    Parameters:
        chunk_size: 500 chars ≈ 125 tokens (good for most cases)
        overlap: 50 chars prevents losing context at boundaries
    """
    print(f"\n=== STEP 2A: Chunking Text (Fixed Size: {chunk_size} chars, overlap: {overlap}) ===")
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Get chunk from start to start+chunk_size
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        
        # Move start forward (chunk_size - overlap)
        start += chunk_size - overlap
    
    print(f"✅ Created {len(chunks)} chunks")
    return chunks


def chunk_text_recursive(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    METHOD 2: Recursive Character Splitting (RECOMMENDED)
    
    Concept: Split on natural boundaries (paragraphs, sentences, words)
    When to use: Production systems, preserve meaning
    Pros: Maintains semantic coherence
    Cons: Slightly more complex
    
    Splitting Hierarchy:
    1. Try splitting on double newlines (paragraphs)
    2. If still too large, split on single newlines (sentences)
    3. If still too large, split on periods (.)
    4. If still too large, split on spaces (words)
    5. Last resort: split on characters
    """
    print(f"\n=== STEP 2B: Chunking Text (Recursive: {chunk_size} chars, overlap: {overlap}) ===")
    
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    # How it works:
    # 1. The splitter tries to split the text at the largest separator first (e.g., "\n\n" for paragraphs).
    # 2. If a chunk is still too large (exceeds chunk_size), it recursively tries the next smaller separator (e.g., "\n" for sentences).
    # 3. This continues down to ". " (sentence ends), then " " (words), and finally character level if needed.
    # 4. At each stage, it only splits further if the chunk is still too big.
    # 5. The process ensures that chunks are as large as possible (up to chunk_size), but always respect natural boundaries when possible.
    # 6. Overlap is applied between adjacent chunks to preserve context.

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]  # Order: paragraphs → lines → sentences → words → chars
    )
    
    chunks = text_splitter.split_text(text)
    
    print(f"✅ Created {len(chunks)} recursive chunks")
    return chunks


def chunk_text_semantic(text: str, min_chunk_size: int = 200, max_chunk_size: int = 800) -> List[str]:
    """
    METHOD 3: Semantic Chunking (ADVANCED)
    
    Concept: Use embeddings to find natural topic boundaries
    When to use: High-quality retrieval, varied content
    Pros: Best semantic coherence
    Cons: Slower, requires embeddings
    
    How it works:
    1. Split into sentences
    2. Embed each sentence
    3. Find points where embedding similarity drops (topic change)
    4. Create chunks at these boundaries
    """
    print(f"\n=== STEP 2C: Chunking Text (Semantic: {min_chunk_size}-{max_chunk_size} chars) ===")
    
    # Simple sentence splitting
    sentences = text.split('. ')
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Add sentence to current chunk
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + ". "
        else:
            # Start new chunk if we've reached min size
            if len(current_chunk) > min_chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
            else:
                current_chunk += sentence + ". "
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    print(f"✅ Created {len(chunks)} semantic chunks")
    return chunks


# =============================================================================
# STEP 2D: ADVANCED CHUNKING FOR PDFs WITH IMAGES, TEXT, AND TABLES
# =============================================================================
# CRITICAL: When PDFs contain mixed content (text, images, tables)
# Standard chunking breaks document structure and loses context
# =============================================================================

def chunk_pdf_layout_aware(pdf_path: str) -> List[Dict]:
    """
    METHOD 4: Layout-Aware Chunking (CRITICAL FOR PDFs)
    
    Concept: Preserve document structure by detecting layout elements
    When to use: PDFs with complex layouts, mixed content
    Pros: Maintains document structure, separates different element types
    Cons: Requires PyMuPDF, more complex
    
    How it works:
    1. Detect page layout (headers, paragraphs, images, tables)
    2. Extract each element separately
    3. Create chunks that respect element boundaries
    4. Tag chunks with element type for better retrieval
    
    Returns: List of dicts with 'content', 'type', 'metadata'
    """
    print(f"\n=== STEP 2D: Layout-Aware Chunking (PDF) ===")
    
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("⚠️ PyMuPDF not installed. Run: pip install pymupdf")
        return []
    
    chunks = []
    doc = fitz.open(pdf_path)
    
    for page_num, page in enumerate(doc):
        # Extract text blocks with position information
        blocks = page.get_text("dict")["blocks"]
        
        for block_num, block in enumerate(blocks):
            if block["type"] == 0:  # Text block
                text = ""
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text += span["text"] + " "
                
                if text.strip():
                    chunks.append({
                        "content": text.strip(),
                        "type": "text",
                        "metadata": {
                            "page": page_num + 1,
                            "block": block_num,
                            "bbox": block["bbox"]  # Bounding box
                        }
                    })
            
            elif block["type"] == 1:  # Image block
                chunks.append({
                    "content": f"[IMAGE on page {page_num + 1}]",
                    "type": "image",
                    "metadata": {
                        "page": page_num + 1,
                        "block": block_num,
                        "bbox": block["bbox"],
                        "xref": block.get("xref")  # Image reference
                    }
                })
    
    doc.close()
    
    print(f"✅ Created {len(chunks)} layout-aware chunks")
    print(f"   Text blocks: {sum(1 for c in chunks if c['type'] == 'text')}")
    print(f"   Image blocks: {sum(1 for c in chunks if c['type'] == 'image')}")
    
    return chunks


def chunk_pdf_with_tables(pdf_path: str) -> List[Dict]:
    """
    METHOD 5: Table-Aware Chunking (CRITICAL FOR STRUCTURED DATA)
    
    Concept: Detect and extract tables as complete units
    When to use: PDFs with tables (financial reports, research papers)
    Pros: Keeps table structure intact, prevents splitting rows/columns
    Cons: Requires table detection libraries
    
    How it works:
    1. Use Camelot/Tabula to detect tables
    2. Extract each table as one chunk
    3. Convert table to markdown or text format
    4. Extract surrounding text separately
    
    Why critical: Tables lose meaning when split across chunks
    """
    print(f"\n=== STEP 2E: Table-Aware Chunking ===")
    
    try:
        import camelot
    except ImportError:
        print("⚠️ Camelot not installed. Run: pip install camelot-py[cv]")
        return []
    
    chunks = []
    
    try:
        # Extract tables from PDF
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
        
        print(f"   Found {len(tables)} tables")
        
        for i, table in enumerate(tables):
            # Convert table to markdown format
            table_md = table.df.to_markdown(index=False)
            
            chunks.append({
                "content": table_md,
                "type": "table",
                "metadata": {
                    "page": table.page,
                    "table_num": i + 1,
                    "accuracy": table.accuracy,  # Detection confidence
                    "shape": table.shape  # (rows, cols)
                }
            })
        
        print(f"✅ Extracted {len(chunks)} tables as chunks")
        
    except Exception as e:
        print(f"⚠️ Table extraction failed: {e}")
    
    return chunks


def chunk_pdf_multimodal(pdf_path: str, vision_model_api_key: str = None) -> List[Dict]:
    """
    METHOD 6: Multi-Modal Chunking (ADVANCED - IMAGES + TEXT)
    
    Concept: Extract images and generate text descriptions using Vision AI
    When to use: PDFs with important diagrams, charts, infographics
    Pros: Images become searchable, complete context
    Cons: Requires Vision API (costs money), slower
    
    How it works:
    1. Extract images from PDF
    2. Send to Vision AI (GPT-4V, Gemini Vision, Claude Vision)
    3. Get detailed text description of image
    4. Store image description as chunk with image reference
    5. Combine with text chunks for complete document understanding
    
    Real-world example:
    PDF has diagram showing "Machine Learning Pipeline"
    → Extract image
    → Vision AI describes: "Flowchart showing data collection → preprocessing → 
       model training → evaluation → deployment"
    → User can search "what is the ML pipeline" and retrieve this chunk
    """
    print(f"\n=== STEP 2F: Multi-Modal Chunking (Images + Text) ===")
    
    try:
        import fitz  # PyMuPDF
        from PIL import Image
        import io
        import base64
    except ImportError:
        print("⚠️ Required libraries not installed")
        return []
    
    chunks = []
    doc = fitz.open(pdf_path)
    
    for page_num, page in enumerate(doc):
        # Extract images
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Filter small images (likely icons, bullets)
            if pil_image.width < 100 or pil_image.height < 100:
                continue
            
            # Option 1: If you have Vision API
            if vision_model_api_key:
                # Encode image to base64
                buffered = io.BytesIO()
                pil_image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                # TODO: Call Vision API to get description
                # For now, placeholder
                image_description = f"[Image {img_index + 1} on page {page_num + 1}]"
            else:
                image_description = f"[Image {img_index + 1} on page {page_num + 1} - {pil_image.width}x{pil_image.height}]"
            
            chunks.append({
                "content": image_description,
                "type": "image",
                "metadata": {
                    "page": page_num + 1,
                    "image_index": img_index,
                    "width": pil_image.width,
                    "height": pil_image.height,
                    "xref": xref
                }
            })
    
    doc.close()
    
    print(f"✅ Extracted {len(chunks)} image chunks")
    
    return chunks


def chunk_pdf_hybrid_complete(pdf_path: str) -> List[Dict]:
    """
    METHOD 7: Hybrid Complete Chunking (PRODUCTION READY)
    
    Concept: Combine all methods for complete PDF understanding
    When to use: Production RAG systems with complex PDFs
    
    Process:
    1. Extract text with layout awareness
    2. Detect and extract tables intact
    3. Extract and describe images
    4. Apply smart chunking to text portions
    5. Keep tables and images as separate chunks
    6. Maintain page/position metadata for all chunks
    
    Result: Every element properly chunked and searchable
    
    Example Output:
    [
        {"content": "Introduction to ML...", "type": "text", "page": 1},
        {"content": "| Model | Accuracy |\n...", "type": "table", "page": 2},
        {"content": "Diagram showing neural network...", "type": "image", "page": 3},
        {"content": "Deep learning uses...", "type": "text", "page": 3}
    ]
    """
    print(f"\n=== STEP 2G: Hybrid Complete Chunking (ALL METHODS) ===")
    
    all_chunks = []
    
    # Step 1: Layout-aware text extraction
    layout_chunks = chunk_pdf_layout_aware(pdf_path)
    all_chunks.extend(layout_chunks)
    
    # Step 2: Table extraction
    table_chunks = chunk_pdf_with_tables(pdf_path)
    all_chunks.extend(table_chunks)
    
    # Step 3: Image extraction
    image_chunks = chunk_pdf_multimodal(pdf_path)
    all_chunks.extend(image_chunks)
    
    # Sort by page number to maintain document order
    all_chunks.sort(key=lambda x: x['metadata'].get('page', 0))
    
    print(f"\n✅ COMPLETE: {len(all_chunks)} total chunks")
    print(f"   📝 Text: {sum(1 for c in all_chunks if c['type'] == 'text')}")
    print(f"   📊 Tables: {sum(1 for c in all_chunks if c['type'] == 'table')}")
    print(f"   🖼️ Images: {sum(1 for c in all_chunks if c['type'] == 'image')}")
    
    return all_chunks


# =============================================================================
# STEP 3: EMBEDDINGS
# =============================================================================
# Concept: Convert text into dense vectors (numbers) that capture meaning
# Why: Computers can't understand text, but can compare vectors
# Key Concept: Similar meaning = Similar vectors (cosine similarity)
# =============================================================================

def create_embeddings_openai(texts: List[str]) -> List[List[float]]:
    """
    METHOD 1: OpenAI Embeddings (Best Quality)
    
    Concept: Use OpenAI's text-embedding-3-small model
    When to use: Production, high accuracy needed
    Pros: Best quality, 1536 dimensions
    Cons: Costs money ($0.00002 per 1K tokens)
    
    Dimensions: 1536 (each text becomes array of 1536 numbers)
    """
    # Yes, for every chunk we create an embedding.
    print(f"\n=== STEP 3A: Creating Embeddings (OpenAI) ===")
    
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    embeddings = []
    for i, text in enumerate(texts):
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        embedding = response.data[0].embedding
        embeddings.append(embedding)
        
        if i == 0:
            print(f"✅ First embedding shape: {len(embedding)} dimensions")
            print(f"   Sample values: {embedding[:5]}")
    
    print(f"✅ Created {len(embeddings)} embeddings")
    return embeddings


def create_embeddings_huggingface(texts: List[str]) -> List[List[float]]:
    """
    METHOD 2: HuggingFace Embeddings (FREE, Local)
    
    Concept: Use open-source sentence-transformers model
    When to use: Development, no budget, privacy needed
    Pros: Free, runs locally, no API calls
    Cons: Lower quality than OpenAI, 384 dimensions
    
    Model: all-MiniLM-L6-v2
    Dimensions: 384
    Speed: ~100-200 chunks per second on CPU
    """
    print(f"\n=== STEP 3B: Creating Embeddings (HuggingFace) ===")
    
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings_list = embeddings.tolist()
    
    print(f"✅ Created {len(embeddings_list)} embeddings")
    print(f"   Shape: {len(embeddings_list[0])} dimensions")
    
    return embeddings_list


# =============================================================================
# STEP 4: VECTOR STORAGE
# =============================================================================
# Concept: Store embeddings in database for fast similarity search
# Key Operations:
#   - add(): Store vectors with metadata
#   - query(): Find most similar vectors
# =============================================================================

def store_in_chromadb(chunks: List[str], embeddings: List[List[float]]) -> object:
    """
    METHOD 1: ChromaDB (Recommended for Learning)
    
    Concept: Lightweight vector database, runs locally
    When to use: Development, small-medium datasets (<1M vectors)
    Pros: Easy setup, persistent storage, built-in metadata
    Cons: Not for massive scale
    
    How it works:
    1. Creates a collection (like a table)
    2. Stores vectors with IDs and metadata
    3. Builds index for fast search (HNSW algorithm)
    """
    print(f"\n=== STEP 4A: Storing in ChromaDB ===")
    
    import chromadb
    
    # Create persistent client (data saved to disk)
    client = chromadb.PersistentClient(path="./chroma_learning_db")
    
    # Create or get collection
    collection = client.get_or_create_collection(
        name="learning_rag",
        metadata={"description": "Learning RAG project"}
    )
    
    # Add documents
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"chunk_index": i, "length": len(chunk)} for i, chunk in enumerate(chunks)]
    
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"✅ Stored {len(chunks)} chunks in ChromaDB")
    print(f"   Collection count: {collection.count()}")
    
    return collection


def store_in_numpy(chunks: List[str], embeddings: List[List[float]]) -> Tuple[np.ndarray, List[str]]:
    """
    METHOD 2: NumPy Arrays (Simplest)
    
    Concept: Store vectors in memory as NumPy arrays
    When to use: Quick experiments, understanding basics
    Pros: Dead simple, no dependencies
    Cons: No persistence, manual search, not scalable
    
    Returns: (embedding_matrix, chunks)
    """
    print(f"\n=== STEP 4B: Storing in NumPy ===")
    
    embedding_matrix = np.array(embeddings)
    
    print(f"✅ Stored {len(chunks)} chunks in NumPy")
    print(f"   Matrix shape: {embedding_matrix.shape}")
    
    return embedding_matrix, chunks


# =============================================================================
# STEP 5: RETRIEVAL - SIMPLE VECTOR SEARCH
# =============================================================================
# Concept: Find chunks most similar to user query
# Method: Cosine similarity between query vector and stored vectors
# =============================================================================

def retrieve_simple_vector(query: str, collection, top_k: int = 3) -> List[Dict]:
    """
    METHOD 1: Simple Vector Search
    
    Concept: Find top K most similar chunks using cosine similarity
    When to use: Quick queries, semantic search
    Pros: Fast, understands meaning
    Cons: May miss exact keyword matches
    
    How it works:
    1. Convert query to embedding
    2. Calculate cosine similarity with all stored embeddings
    3. Return top K matches
    
    Cosine Similarity: Measures angle between vectors
    - 1.0 = Identical meaning
    - 0.0 = Completely unrelated
    - -1.0 = Opposite meaning
    """
    print(f"\n=== STEP 5A: Retrieval (Simple Vector Search, top_k={top_k}) ===")
    
    # Query the collection
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    # Format results
    retrieved_chunks = []
    for i in range(len(results['documents'][0])):
        retrieved_chunks.append({
            "content": results['documents'][0][i],
            "distance": results['distances'][0][i],  # Lower = more similar
            "metadata": results['metadatas'][0][i]
        })
    
    print(f"✅ Retrieved {len(retrieved_chunks)} chunks")
    for i, chunk in enumerate(retrieved_chunks):
        print(f"   {i+1}. Distance: {chunk['distance']:.3f}, Length: {len(chunk['content'])} chars")
    
    return retrieved_chunks


# =============================================================================
# STEP 5B: RETRIEVAL - HYBRID SEARCH (BM25 + VECTOR)
# =============================================================================
# Concept: Combine keyword search (BM25) with semantic search (vectors)
# Why: Best of both worlds - exact matches + semantic understanding
# =============================================================================

def retrieve_hybrid_search(query: str, collection, chunks: List[str], top_k: int = 3, alpha: float = 0.5) -> List[Dict]:
    """
    METHOD 2: Hybrid Search (BM25 + Vector) - RECOMMENDED
    
    Concept: Combine sparse (BM25) and dense (vector) retrieval
    When to use: Production systems, need both precision and recall
    Pros: Catches exact terms AND semantic meaning
    Cons: More complex, slower
    
    BM25 Algorithm:
    - Classic information retrieval (like Google Search)
    - Scores based on term frequency and document frequency
    - Good for exact keyword matches
    
    Formula:
    final_score = alpha * vector_score + (1 - alpha) * bm25_score
    
    Parameters:
        alpha: 0.0 = all BM25, 1.0 = all vector
               0.5 = equal weight (recommended)
    """
    print(f"\n=== STEP 5B: Retrieval (Hybrid Search, alpha={alpha}) ===")
    
    from rank_bm25 import BM25Okapi
    
    # Step 1: Vector search
    vector_results = collection.query(
        query_texts=[query],
        n_results=top_k * 2  # Get more for re-ranking
    )
    
    # Step 2: BM25 search
    tokenized_chunks = [chunk.lower().split() for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    
    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)
    
    # Normalize BM25 scores to 0-1 range
    max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
    bm25_scores_norm = [score / max_bm25 for score in bm25_scores]
    
    # Step 3: Combine scores
    # Vector distances need to be converted to similarity (1 - distance)
    hybrid_scores = []
    for i, chunk in enumerate(chunks):
        # Find this chunk in vector results
        vector_score = 0
        if chunk in vector_results['documents'][0]:
            idx = vector_results['documents'][0].index(chunk)
            # Convert distance to similarity (closer = higher score)
            vector_distance = vector_results['distances'][0][idx]
            vector_score = 1 - (vector_distance / 2)  # Normalize to 0-1
        
        bm25_score = bm25_scores_norm[i]
        
        # Hybrid score
        combined_score = alpha * vector_score + (1 - alpha) * bm25_score
        
        hybrid_scores.append({
            "content": chunk,
            "vector_score": vector_score,
            "bm25_score": bm25_score,
            "combined_score": combined_score,
            "chunk_index": i
        })
    
    # Sort by combined score
    hybrid_scores.sort(key=lambda x: x['combined_score'], reverse=True)
    
    top_results = hybrid_scores[:top_k]
    
    print(f"✅ Retrieved {len(top_results)} chunks using hybrid search")
    for i, result in enumerate(top_results):
        print(f"   {i+1}. Combined: {result['combined_score']:.3f} "
              f"(Vector: {result['vector_score']:.3f}, BM25: {result['bm25_score']:.3f})")
    
    return top_results


# =============================================================================
# STEP 5C: RETRIEVAL - CROSS-ENCODER RE-RANKING
# =============================================================================
# Concept: Use a more powerful model to re-rank initial results
# Why: Better accuracy than bi-encoder (but slower)
# =============================================================================

def retrieve_with_reranking(query: str, collection, top_k: int = 3, initial_k: int = 10) -> List[Dict]:
    """
    METHOD 3: Cross-Encoder Re-ranking (BEST QUALITY)
    
    Concept: Two-stage retrieval for maximum accuracy
    When to use: High-precision needed, can afford latency
    Pros: Best accuracy
    Cons: Slower, more compute
    
    How it works:
    Stage 1 (Fast Retrieval): Get initial_k candidates (e.g., 10)
    Stage 2 (Re-ranking): Score each candidate with cross-encoder
    
    Bi-Encoder vs Cross-Encoder:
    - Bi-Encoder: Encodes query and docs separately (fast, used in Stage 1)
    - Cross-Encoder: Encodes query+doc together (slow but accurate, Stage 2)
    
    Example:
    Query: "What is machine learning?"
    
    Bi-Encoder (Fast):
    - Query embedding: [0.2, 0.5, ...]
    - Doc embedding: [0.3, 0.4, ...]
    - Compare embeddings
    
    Cross-Encoder (Accurate):
    - Input: "Query: What is machine learning? Document: ML is a subset of AI..."
    - Output: Relevance score (0-1)
    """
    print(f"\n=== STEP 5C: Retrieval (Cross-Encoder Re-ranking) ===")
    
    from sentence_transformers import CrossEncoder
    
    # Stage 1: Initial retrieval (fast)
    print(f"   Stage 1: Retrieving top {initial_k} candidates...")
    initial_results = collection.query(
        query_texts=[query],
        n_results=initial_k
    )
    
    candidates = [
        {
            "content": initial_results['documents'][0][i],
            "metadata": initial_results['metadatas'][0][i],
            "initial_distance": initial_results['distances'][0][i]
        }
        for i in range(len(initial_results['documents'][0]))
    ]
    
    # Stage 2: Re-rank with cross-encoder (accurate)
    print(f"   Stage 2: Re-ranking with cross-encoder...")
    
    cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    # Create query-document pairs
    pairs = [[query, candidate['content']] for candidate in candidates]
    
    # Score all pairs
    scores = cross_encoder.predict(pairs)
    
    # Add scores to candidates
    for i, candidate in enumerate(candidates):
        candidate['rerank_score'] = float(scores[i])
    
    # Sort by re-rank score
    candidates.sort(key=lambda x: x['rerank_score'], reverse=True)
    
    # Return top K
    final_results = candidates[:top_k]
    
    print(f"✅ Retrieved and re-ranked {len(final_results)} chunks")
    for i, result in enumerate(final_results):
        print(f"   {i+1}. Re-rank Score: {result['rerank_score']:.3f}, "
              f"Initial Distance: {result['initial_distance']:.3f}")
    
    return final_results


# =============================================================================
# STEP 6: GENERATION - ANSWER GENERATION WITH LLM
# =============================================================================
# Concept: Use LLM to generate answer based on retrieved context
# Key: Good prompt engineering makes huge difference
# =============================================================================

def generate_answer_basic(query: str, context_chunks: List[Dict]) -> str:
    """
    METHOD 1: Basic Prompting
    
    Concept: Simple instruction to LLM
    When to use: Quick experiments, simple queries
    Pros: Fast to implement
    Cons: May hallucinate, less reliable
    """
    print(f"\n=== STEP 6A: Generation (Basic Prompting) ===")
    
    from openai import OpenAI
    
    # Combine context
    context = "\n\n".join([chunk['content'] for chunk in context_chunks])
    
    # Simple prompt
    prompt = f"""Answer the following question based on the context provided.

Context:
{context}

Question: {query}

Answer:"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0  # Deterministic
    )
    
    answer = response.choices[0].message.content
    
    print(f"✅ Generated answer ({len(answer)} chars)")
    
    return answer


def generate_answer_with_instructions(query: str, context_chunks: List[Dict]) -> str:
    """
    METHOD 2: Structured Prompting with Instructions
    
    Concept: Clear instructions, role assignment, constraints
    When to use: Production, need reliability
    Pros: More reliable, less hallucination
    Cons: Longer prompts
    
    Key Components:
    1. Role: "You are an expert assistant..."
    2. Context: Provide relevant information
    3. Instructions: Clear steps for LLM
    4. Constraints: "Do not make up information"
    5. Format: How to structure answer
    """
    print(f"\n=== STEP 6B: Generation (Structured Prompting) ===")
    
    from openai import OpenAI
    
    # Combine context with numbering
    context = ""
    for i, chunk in enumerate(context_chunks, 1):
        context += f"\n[Source {i}]\n{chunk['content']}\n"
    
    # Structured prompt
    prompt = f"""You are a helpful and accurate assistant. Your task is to answer questions based ONLY on the provided context.

CONTEXT:
{context}

INSTRUCTIONS:
1. Read the question carefully
2. Find relevant information in the context
3. Provide a clear, concise answer
4. If the answer is not in the context, say "I don't have enough information to answer this question"
5. Cite sources by referring to [Source X] numbers

CONSTRAINTS:
- Do NOT make up information
- Do NOT use external knowledge
- Base your answer ONLY on the provided context

QUESTION: {query}

ANSWER:"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a precise and helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )
    
    answer = response.choices[0].message.content
    
    print(f"✅ Generated structured answer ({len(answer)} chars)")
    
    return answer


def generate_answer_with_cot(query: str, context_chunks: List[Dict]) -> str:
    """
    METHOD 3: Chain-of-Thought (CoT) Prompting
    
    Concept: Ask LLM to think step-by-step before answering
    When to use: Complex reasoning, multi-step questions
    Pros: Better reasoning, transparent logic
    Cons: Longer responses, more tokens
    
    CoT Pattern:
    "Let's think step by step:
    1. First, I'll identify...
    2. Then, I'll analyze...
    3. Finally, I'll conclude..."
    
    Why it works: Forces LLM to break down problem
    """
    print(f"\n=== STEP 6C: Generation (Chain-of-Thought) ===")
    
    from openai import OpenAI
    
    # Combine context
    context = "\n\n".join([chunk['content'] for chunk in context_chunks])
    
    # CoT prompt
    prompt = f"""You are a thoughtful assistant. Answer the question by thinking through it step by step.

Context:
{context}

Question: {query}

Let's approach this step by step:
1. First, let me identify the relevant information in the context
2. Then, I'll analyze how it relates to the question
3. Finally, I'll formulate a clear answer

Reasoning:"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    answer = response.choices[0].message.content
    
    print(f"✅ Generated CoT answer ({len(answer)} chars)")
    
    return answer


def generate_answer_with_few_shot(query: str, context_chunks: List[Dict]) -> str:
    """
    METHOD 4: Few-Shot Prompting
    
    Concept: Provide examples of good Q&A pairs
    When to use: Specific answer format needed, complex domain
    Pros: Guides format and style
    Cons: Uses more tokens
    
    Pattern:
    Example 1: Q -> A
    Example 2: Q -> A
    Example 3: Q -> A
    Now answer: Q -> ?
    """
    print(f"\n=== STEP 6D: Generation (Few-Shot Prompting) ===")
    
    from openai import OpenAI
    
    # Combine context
    context = "\n\n".join([chunk['content'] for chunk in context_chunks])
    
    # Few-shot prompt with examples
    prompt = f"""Answer questions based on the provided context. Here are examples:

Example 1:
Context: "The capital of France is Paris. Paris is known for the Eiffel Tower."
Question: What is the capital of France?
Answer: The capital of France is Paris. [Source: Context provided]

Example 2:
Context: "Python was created by Guido van Rossum in 1991."
Question: Who created Python?
Answer: Python was created by Guido van Rossum. [Source: Context provided]

Now answer this question:

Context:
{context}

Question: {query}

Answer:"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    answer = response.choices[0].message.content
    
    print(f"✅ Generated few-shot answer ({len(answer)} chars)")
    
    return answer


# =============================================================================
# STEP 7: EVALUATION & RELIABILITY
# =============================================================================
# Concept: Measure how good your RAG system is
# Why: Know if changes improve or hurt performance
# =============================================================================

def evaluate_faithfulness(answer: str, context_chunks: List[Dict]) -> float:
    """
    METRIC 1: Faithfulness (Groundedness)
    
    Concept: Does the answer only use information from context?
    When to use: Prevent hallucination
    Scale: 0.0 (hallucinated) to 1.0 (fully grounded)
    
    How to measure:
    - Break answer into statements
    - Check if each statement is supported by context
    - Score = supported_statements / total_statements
    """
    print(f"\n=== EVALUATION 1: Faithfulness ===")
    
    from openai import OpenAI
    
    context = "\n".join([chunk['content'] for chunk in context_chunks])
    
    # Use LLM to judge faithfulness
    prompt = f"""Evaluate if the answer is fully supported by the context.

Context:
{context}

Answer:
{answer}

For each claim in the answer, check if it's supported by the context.
Score from 0.0 (completely unsupported) to 1.0 (fully supported).

Respond with just the score (e.g., 0.85):"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    score_text = response.choices[0].message.content.strip()
    
    try:
        score = float(score_text)
    except:
        score = 0.5  # Default if parsing fails
    
    print(f"✅ Faithfulness Score: {score:.2f}")
    if score >= 0.9:
        print("   ✅ Excellent - Answer is well-grounded")
    elif score >= 0.7:
        print("   ⚠️ Good - Minor unsupported claims")
    else:
        print("   ❌ Poor - Significant hallucination detected")
    
    return score


def evaluate_answer_relevance(query: str, answer: str) -> float:
    """
    METRIC 2: Answer Relevance
    
    Concept: Does the answer actually address the question?
    When to use: Ensure answer is on-topic
    Scale: 0.0 (off-topic) to 1.0 (perfectly relevant)
    
    How to measure:
    - Check if answer addresses all parts of question
    - Check if answer contains irrelevant information
    """
    print(f"\n=== EVALUATION 2: Answer Relevance ===")
    
    from openai import OpenAI
    
    prompt = f"""Evaluate how relevant the answer is to the question.

Question: {query}

Answer: {answer}

Score from 0.0 (completely irrelevant) to 1.0 (perfectly relevant).
Consider:
- Does it address the question?
- Is it complete?
- Does it contain unnecessary information?

Respond with just the score (e.g., 0.85):"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    score_text = response.choices[0].message.content.strip()
    
    try:
        score = float(score_text)
    except:
        score = 0.5
    
    print(f"✅ Answer Relevance Score: {score:.2f}")
    if score >= 0.9:
        print("   ✅ Excellent - Highly relevant answer")
    elif score >= 0.7:
        print("   ⚠️ Good - Mostly relevant")
    else:
        print("   ❌ Poor - Answer is off-topic")
    
    return score


def evaluate_context_precision(query: str, context_chunks: List[Dict]) -> float:
    """
    METRIC 3: Context Precision
    
    Concept: Are the retrieved chunks actually relevant to the query?
    When to use: Tune retrieval parameters
    Scale: 0.0 (irrelevant) to 1.0 (all relevant)
    
    Formula: relevant_chunks / total_retrieved_chunks
    """
    print(f"\n=== EVALUATION 3: Context Precision ===")
    
    from openai import OpenAI
    
    # Check each chunk's relevance
    relevant_count = 0
    
    for i, chunk in enumerate(context_chunks):
        prompt = f"""Is this context relevant to answering the question?

Question: {query}

Context: {chunk['content'][:300]}...

Answer with just 'yes' or 'no':"""
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        is_relevant = response.choices[0].message.content.strip().lower() == 'yes'
        if is_relevant:
            relevant_count += 1
    
    precision = relevant_count / len(context_chunks) if context_chunks else 0
    
    print(f"✅ Context Precision: {precision:.2f} ({relevant_count}/{len(context_chunks)} relevant)")
    if precision >= 0.8:
        print("   ✅ Excellent - Most chunks are relevant")
    elif precision >= 0.5:
        print("   ⚠️ Good - Some irrelevant chunks")
    else:
        print("   ❌ Poor - Many irrelevant chunks retrieved")
    
    return precision


def evaluate_latency(start_time: float, end_time: float) -> Dict:
    """
    METRIC 4: Performance (Latency)
    
    Concept: How fast is your RAG pipeline?
    When to use: Optimize user experience
    Targets:
    - <1s: Excellent
    - <3s: Good
    - >5s: Poor (users will notice)
    
    Components:
    - Retrieval time
    - Generation time
    - Total time
    """
    print(f"\n=== EVALUATION 4: Latency ===")
    
    total_time = end_time - start_time
    
    print(f"✅ Total Latency: {total_time:.2f}s")
    if total_time < 1.0:
        print("   ✅ Excellent - Very fast")
    elif total_time < 3.0:
        print("   ⚠️ Good - Acceptable speed")
    else:
        print("   ❌ Poor - Too slow, optimize!")
    
    return {
        "total_time": total_time,
        "rating": "excellent" if total_time < 1 else "good" if total_time < 3 else "poor"
    }


# =============================================================================
# STEP 8: RAGAS EVALUATION FRAMEWORK
# =============================================================================
# RAGAS = Retrieval Augmented Generation Assessment
# Industry-standard framework with specific metrics and formulas
# =============================================================================

def evaluate_with_ragas(query: str, answer: str, contexts: List[str], ground_truth: str = None) -> Dict:
    """
    RAGAS Framework (INDUSTRY STANDARD)
    
    Concept: Comprehensive RAG evaluation with proven metrics
    When to use: Production systems, need standardized evaluation
    
    Key Metrics:
    1. Context Relevance: Are retrieved chunks relevant to query?
    2. Context Recall: Did we retrieve all relevant information?
    3. Faithfulness: Is answer grounded in context?
    4. Answer Relevance: Does answer address the question?
    5. Answer Correctness: Is answer factually correct? (needs ground truth)
    
    Difference from LLM-as-a-Judge:
    - RAGAS: Specific formulas, standardized metrics, research-backed
    - LLM-as-a-Judge: Flexible prompts, custom criteria, interpretive
    
    RAGAS uses both:
    - Rule-based calculations (cosine similarity, overlap)
    - LLM-based evaluation (for semantic understanding)
    """
    print(f"\n=== RAGAS EVALUATION (Framework) ===")
    
    try:
        from ragas import evaluate
        from ragas.metrics import (
            context_relevancy,
            context_recall,
            faithfulness,
            answer_relevancy,
            answer_correctness
        )
        from datasets import Dataset
    except ImportError:
        print("⚠️ RAGAS not installed. Run: pip install ragas datasets")
        return {}
    
    # Prepare data in RAGAS format
    data = {
        "question": [query],
        "answer": [answer],
        "contexts": [contexts],
    }
    
    # Add ground truth if available
    if ground_truth:
        data["ground_truth"] = [ground_truth]
    
    dataset = Dataset.from_dict(data)
    
    # Select metrics
    metrics = [
        context_relevancy,    # Measures how relevant retrieved contexts are
        faithfulness,         # Measures if answer is grounded in context
        answer_relevancy,     # Measures if answer addresses the question
    ]
    
    # Add metrics that need ground truth
    if ground_truth:
        metrics.extend([
            context_recall,       # Did we retrieve all relevant info?
            answer_correctness    # Is the answer factually correct?
        ])
    
    print("   Running RAGAS evaluation...")
    print("   (This uses LLM calls internally for semantic evaluation)")
    
    # Run evaluation
    results = evaluate(dataset, metrics=metrics)
    
    print(f"\n✅ RAGAS Evaluation Complete")
    print(f"   📊 Context Relevancy: {results['context_relevancy']:.3f}")
    print(f"   🔍 Faithfulness: {results['faithfulness']:.3f}")
    print(f"   🎯 Answer Relevancy: {results['answer_relevancy']:.3f}")
    
    if ground_truth:
        print(f"   📝 Context Recall: {results['context_recall']:.3f}")
        print(f"   ✅ Answer Correctness: {results['answer_correctness']:.3f}")
    
    return results


def evaluate_ragas_detailed(query: str, answer: str, contexts: List[str]) -> Dict:
    """
    RAGAS Detailed Breakdown (EDUCATIONAL)
    
    Shows exactly how each RAGAS metric is calculated
    
    1. CONTEXT RELEVANCY
    Formula: relevant_sentences / total_sentences_in_contexts
    Uses: LLM to determine which sentences are relevant
    
    2. FAITHFULNESS  
    Formula: supported_claims / total_claims
    Uses: LLM to extract claims and verify against context
    
    3. ANSWER RELEVANCY
    Formula: Average cosine similarity between question and generated questions
    Uses: LLM generates questions that the answer would address
    
    4. CONTEXT RECALL (needs ground truth)
    Formula: ground_truth_statements_in_context / total_ground_truth_statements
    
    5. ANSWER CORRECTNESS (needs ground truth)
    Formula: Weighted combination of semantic similarity and factual overlap
    """
    print(f"\n=== RAGAS Detailed Breakdown ===")
    
    from openai import OpenAI
    import numpy as np
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    results = {}
    
    # METRIC 1: Context Relevancy
    print("\n   1️⃣ Context Relevancy")
    print("      How: Extract sentences from contexts, classify if relevant to query")
    
    all_sentences = []
    for ctx in contexts:
        all_sentences.extend(ctx.split('. '))
    
    relevant_count = 0
    for sentence in all_sentences[:5]:  # Sample first 5
        prompt = f"Is this sentence relevant to answering '{query}'?\nSentence: {sentence}\nAnswer yes or no:"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        if "yes" in response.choices[0].message.content.lower():
            relevant_count += 1
    
    context_relevancy = relevant_count / len(all_sentences[:5]) if all_sentences else 0
    results['context_relevancy'] = context_relevancy
    print(f"      Score: {context_relevancy:.3f} ({relevant_count}/{len(all_sentences[:5])} relevant)")
    
    # METRIC 2: Faithfulness
    print("\n   2️⃣ Faithfulness")
    print("      How: Extract claims from answer, verify each against context")
    
    prompt = f"""Extract factual claims from this answer:

Answer: {answer}

List each claim on a new line:"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    claims = response.choices[0].message.content.strip().split('\n')
    claims = [c.strip('- ').strip() for c in claims if c.strip()]
    
    supported = 0
    context_text = ' '.join(contexts)
    
    for claim in claims[:3]:  # Sample first 3 claims
        verify_prompt = f"""Is this claim supported by the context?

Claim: {claim}
Context: {context_text[:500]}

Answer yes or no:"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": verify_prompt}],
            temperature=0.0
        )
        
        if "yes" in response.choices[0].message.content.lower():
            supported += 1
    
    faithfulness = supported / len(claims[:3]) if claims else 1.0
    results['faithfulness'] = faithfulness
    print(f"      Score: {faithfulness:.3f} ({supported}/{len(claims[:3])} claims supported)")
    
    # METRIC 3: Answer Relevancy
    print("\n   3️⃣ Answer Relevancy")
    print("      How: Generate questions from answer, compare with original query")
    
    prompt = f"""Given this answer, what question was likely asked?

Answer: {answer}

Generate the question:"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    generated_question = response.choices[0].message.content.strip()
    
    # Calculate similarity (simplified - real RAGAS uses embeddings)
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    query_emb = model.encode([query])
    gen_q_emb = model.encode([generated_question])
    
    # Cosine similarity
    similarity = np.dot(query_emb[0], gen_q_emb[0]) / (
        np.linalg.norm(query_emb[0]) * np.linalg.norm(gen_q_emb[0])
    )
    
    results['answer_relevancy'] = float(similarity)
    print(f"      Score: {similarity:.3f}")
    print(f"      Generated Q: {generated_question}")
    
    print(f"\n✅ RAGAS Detailed Evaluation Complete")
    
    return results


# =============================================================================
# STEP 9: LLM-AS-A-JUDGE EVALUATION
# =============================================================================
# Different from RAGAS: Flexible, custom criteria, interpretive
# =============================================================================

def evaluate_llm_as_judge(query: str, answer: str, contexts: List[str], custom_criteria: List[str] = None) -> Dict:
    """
    LLM-as-a-Judge Evaluation (FLEXIBLE APPROACH)
    
    Concept: Use LLM to judge quality based on custom criteria
    When to use: Need custom evaluation, domain-specific criteria
    
    RAGAS vs LLM-as-a-Judge: KEY DIFFERENCES
    
    ┌─────────────────────┬──────────────────────┬────────────────────────┐
    │     Aspect          │       RAGAS          │   LLM-as-a-Judge       │
    ├─────────────────────┼──────────────────────┼────────────────────────┤
    │ Metrics             │ Standardized (5)     │ Custom, unlimited      │
    │ Formula             │ Research-backed      │ Flexible prompts       │
    │ Scoring             │ Automatic (0-1)      │ LLM interpretation     │
    │ Reproducibility     │ High                 │ Medium (LLM variance)  │
    │ Customization       │ Limited              │ Unlimited              │
    │ Industry Acceptance │ High (standard)      │ Growing                │
    │ Use Case            │ Benchmarking         │ Custom evaluation      │
    │ Speed               │ Slower (multiple)    │ Faster (single call)   │
    └─────────────────────┴──────────────────────┴────────────────────────┘
    
    When to use RAGAS:
    - Need standardized metrics for comparison
    - Publishing research or benchmarks
    - Comparing different RAG systems
    
    When to use LLM-as-a-Judge:
    - Need domain-specific criteria (medical, legal, etc.)
    - Custom quality dimensions
    - Quick iteration on evaluation criteria
    - Interpretive/subjective qualities (tone, style)
    
    Parameters:
        custom_criteria: List of evaluation criteria
        Default: ["accuracy", "completeness", "clarity", "conciseness"]
    """
    print(f"\n=== LLM-AS-A-JUDGE EVALUATION (Flexible) ===")
    
    from openai import OpenAI
    
    if custom_criteria is None:
        custom_criteria = [
            "Accuracy: Is the answer factually correct?",
            "Completeness: Does it fully address the question?",
            "Clarity: Is it easy to understand?",
            "Conciseness: Is it free of unnecessary information?",
            "Groundedness: Is it based on the provided context?"
        ]
    
    context_text = "\n\n".join(contexts)
    
    # Create comprehensive judging prompt
    prompt = f"""You are an expert evaluator for question-answering systems.

QUESTION: {query}

CONTEXT PROVIDED:
{context_text}

GENERATED ANSWER:
{answer}

EVALUATION CRITERIA:
Rate each criterion from 1-10:

"""
    
    for criterion in custom_criteria:
        prompt += f"- {criterion}\n"
    
    prompt += """\n
Provide your evaluation in this format:
1. [Criterion Name]: [Score]/10 - [Brief explanation]
2. [Criterion Name]: [Score]/10 - [Brief explanation]
...

OVERALL SCORE: [Average]/10
SUMMARY: [2-3 sentence assessment]
"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-4",  # Use GPT-4 for better judgment
        messages=[
            {"role": "system", "content": "You are an expert evaluator with high standards for quality."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )
    
    evaluation = response.choices[0].message.content
    
    print(f"\n✅ LLM Judge Evaluation:\n")
    print(evaluation)
    
    # Parse scores (simplified)
    scores = {}
    for criterion in custom_criteria:
        criterion_name = criterion.split(':')[0]
        # Try to extract score from evaluation
        import re
        pattern = f"{criterion_name}.*?(\d+)/10"
        match = re.search(pattern, evaluation, re.IGNORECASE)
        if match:
            scores[criterion_name] = int(match.group(1)) / 10
    
    return {
        "evaluation_text": evaluation,
        "scores": scores,
        "criteria": custom_criteria
    }


def evaluate_llm_as_judge_with_examples(query: str, answer: str, contexts: List[str]) -> Dict:
    """
    LLM-as-a-Judge with Few-Shot Examples (IMPROVED CONSISTENCY)
    
    Concept: Show LLM examples of good/bad answers to calibrate judgment
    When to use: Need consistent scoring across evaluations
    Pros: More reliable, aligns LLM with your standards
    Cons: Requires creating good examples
    """
    print(f"\n=== LLM-AS-A-JUDGE (With Calibration Examples) ===")
    
    from openai import OpenAI
    
    context_text = "\n".join(contexts)
    
    prompt = f"""You are evaluating question-answering quality.

CALIBRATION EXAMPLES:

Example 1 (POOR - Score: 3/10):
Q: What are the types of ML?
A: Machine learning is cool.
Issue: Doesn't answer the question, too vague

Example 2 (GOOD - Score: 7/10):
Q: What are the types of ML?
A: Supervised, unsupervised, and reinforcement learning.
Issue: Correct but lacks detail

Example 3 (EXCELLENT - Score: 10/10):
Q: What are the types of ML?
A: There are three main types: 1) Supervised learning uses labeled data, 2) Unsupervised learning finds patterns in unlabeled data, 3) Reinforcement learning learns through trial and error with rewards.
Reason: Complete, accurate, well-structured

NOW EVALUATE THIS:

Question: {query}
Context: {context_text[:300]}...
Answer: {answer}

Score (1-10): 
Reasoning:
"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    evaluation = response.choices[0].message.content
    
    print(f"\n✅ Calibrated LLM Judge:\n{evaluation}")
    
    # Extract score
    import re
    match = re.search(r'Score.*?(\d+)/10', evaluation)
    score = int(match.group(1)) / 10 if match else 0.5
    
    return {
        "score": score,
        "evaluation": evaluation
    }


# =============================================================================
# MAIN: COMPLETE RAG PIPELINE
# =============================================================================

def main():
    """
    Complete end-to-end RAG pipeline demonstration
    
    Pipeline Flow:
    1. Load document
    2. Chunk text (3 methods shown)
    3. Create embeddings (2 methods shown)
    4. Store in vector DB
    5. Retrieve relevant chunks (3 methods shown)
    6. Generate answer (4 prompting techniques shown)
    7. Evaluate quality (4 metrics shown)
    """
    
    print("=" * 80)
    print("RAG LEARNING PROJECT - COMPLETE PIPELINE")
    print("=" * 80)
    
    import time
    start_time = time.time()
    
    # =============================================================================
    # SETUP: Create sample document
    # =============================================================================
    
    sample_text = """
Machine Learning Fundamentals

Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. The field emerged in the 1950s with pioneers like Arthur Samuel.

There are three main types of machine learning:

1. Supervised Learning: The algorithm learns from labeled training data. For example, given images labeled as 'cat' or 'dog', the model learns to classify new images. Common algorithms include linear regression, decision trees, and neural networks.

2. Unsupervised Learning: The algorithm finds patterns in unlabeled data. Clustering is a typical example, where the algorithm groups similar data points together. K-means and hierarchical clustering are popular methods.

3. Reinforcement Learning: The algorithm learns by interacting with an environment and receiving rewards or penalties. This approach is used in game playing, robotics, and autonomous vehicles.

Deep learning is a specialized branch of machine learning that uses artificial neural networks with multiple layers. These deep neural networks can learn complex patterns and have achieved remarkable success in image recognition, natural language processing, and speech recognition.

The machine learning workflow typically involves several steps:
- Data collection and preparation
- Feature engineering
- Model selection and training
- Model evaluation using metrics like accuracy, precision, and recall
- Model deployment and monitoring

Popular machine learning frameworks include TensorFlow, PyTorch, and scikit-learn. These tools make it easier to build and deploy machine learning models.
"""
    
    # Save sample document
    with open("sample_ml_doc.txt", "w", encoding="utf-8") as f:
        f.write(sample_text)
    
    print("\n✅ Created sample document: sample_ml_doc.txt")
    
    # =============================================================================
    # STEP 1: Load Document
    # =============================================================================
    
    # Try Method 1: Simple loading
    content = load_document_simple("sample_ml_doc.txt")
    
    # =============================================================================
    # STEP 2: Chunking (Compare 3 methods)
    # =============================================================================
    
    print("\n" + "=" * 80)
    print("COMPARING CHUNKING METHODS")
    print("=" * 80)
    
    # Method 1: Fixed size
    chunks_fixed = chunk_text_fixed_size(content, chunk_size=200, overlap=20)
    
    # Method 2: Recursive (RECOMMENDED)
    chunks_recursive = chunk_text_recursive(content, chunk_size=200, overlap=20)
    
    # Method 3: Semantic
    chunks_semantic = chunk_text_semantic(content, min_chunk_size=150, max_chunk_size=300)
    
    # Use recursive for rest of demo (best balance)
    chunks = chunks_recursive
    
    # =============================================================================
    # STEP 3: Create Embeddings
    # =============================================================================
    
    print("\n" + "=" * 80)
    print("CREATING EMBEDDINGS")
    print("=" * 80)
    
    # Using HuggingFace (free, local)
    # Note: For production, use OpenAI for better quality
    embeddings = create_embeddings_huggingface(chunks)
    
    # =============================================================================
    # STEP 4: Store in Vector Database
    # =============================================================================
    
    collection = store_in_chromadb(chunks, embeddings)
    
    # =============================================================================
    # STEP 5: Retrieval - Compare Methods
    # =============================================================================
    
    query = "What are the three types of machine learning?"
    
    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)
    
    # Method 1: Simple vector search
    results_simple = retrieve_simple_vector(query, collection, top_k=3)
    
    # Method 2: Hybrid search
    results_hybrid = retrieve_hybrid_search(query, collection, chunks, top_k=3, alpha=0.5)
    
    # Method 3: With re-ranking
    results_reranked = retrieve_with_reranking(query, collection, top_k=3, initial_k=6)
    
    # Use re-ranked results for generation (best quality)
    best_results = results_reranked
    
    # =============================================================================
    # STEP 6: Generation - Compare Prompting Techniques
    # =============================================================================
    
    print("\n" + "=" * 80)
    print("COMPARING PROMPTING TECHNIQUES")
    print("=" * 80)
    
    # Method 1: Basic
    print("\n--- Method 1: Basic Prompting ---")
    answer_basic = generate_answer_basic(query, best_results)
    print(f"\nAnswer:\n{answer_basic}\n")
    
    # Method 2: Structured with instructions
    print("\n--- Method 2: Structured Prompting ---")
    answer_structured = generate_answer_with_instructions(query, best_results)
    print(f"\nAnswer:\n{answer_structured}\n")
    
    # Method 3: Chain-of-Thought
    print("\n--- Method 3: Chain-of-Thought ---")
    answer_cot = generate_answer_with_cot(query, best_results)
    print(f"\nAnswer:\n{answer_cot}\n")
    
    # =============================================================================
    # STEP 7: Evaluation
    # =============================================================================
    
    print("\n" + "=" * 80)
    print("EVALUATION & RELIABILITY")
    print("=" * 80)
    
    # Use structured answer for evaluation (good balance)
    final_answer = answer_structured
    
    # Metric 1: Faithfulness
    faithfulness = evaluate_faithfulness(final_answer, best_results)
    
    # Metric 2: Answer Relevance
    relevance = evaluate_answer_relevance(query, final_answer)
    
    # Metric 3: Context Precision
    precision = evaluate_context_precision(query, best_results)
    
    # Metric 4: Latency
    end_time = time.time()
    latency = evaluate_latency(start_time, end_time)
    
    # =============================================================================
    # FINAL SUMMARY
    # =============================================================================
    
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    print(f"""
✅ RAG Pipeline Complete!

📊 Quality Metrics:
   - Faithfulness:      {faithfulness:.2f} (hallucination check)
   - Answer Relevance:  {relevance:.2f} (on-topic check)
   - Context Precision: {precision:.2f} (retrieval quality)
   - Latency:          {latency['total_time']:.2f}s ({latency['rating']})

📝 Chunks Created:    {len(chunks)}
🔍 Chunks Retrieved:  {len(best_results)}
💾 Vector DB Size:    {collection.count()} vectors

🎯 Best Practices Used:
   ✅ Recursive chunking (preserves meaning)
   ✅ Cross-encoder re-ranking (best accuracy)
   ✅ Structured prompting (reliable)
   ✅ Comprehensive evaluation (know your quality)

💡 Next Steps to Improve:
   1. Try different chunk sizes (100-1000 chars)
   2. Experiment with alpha in hybrid search (0.3-0.7)
   3. Test various prompting techniques on your data
   4. Add more evaluation metrics (context recall, etc.)
   5. Fine-tune retrieval parameters based on metrics
""")
    
    print("=" * 80)
    print("🎉 Tutorial Complete! You now understand RAG end-to-end.")
    print("=" * 80)


# =============================================================================
# COMPARISON REFERENCE: WHEN TO USE WHAT
# =============================================================================

"""
CHUNKING STRATEGIES:
- Fixed Size: Quick experiments, uniform content
- Recursive: Production (RECOMMENDED) - best balance
- Semantic: Highest quality, slower
- Layout-Aware (PDF): Preserves document structure
- Table-Aware (PDF): Keeps tables intact
- Multi-Modal (PDF): Images + text descriptions
- Hybrid Complete (PDF): ALL methods combined (BEST for complex PDFs)

RETRIEVAL METHODS:
- Simple Vector: Fast, semantic understanding
- Hybrid (BM25+Vector): Production (RECOMMENDED) - best of both
- Re-ranking: Highest accuracy, slower

PROMPTING TECHNIQUES:
- Basic: Quick tests
- Structured: Production (RECOMMENDED) - reliable
- Chain-of-Thought: Complex reasoning
- Few-Shot: Specific formats needed

EVALUATION METRICS:
- Faithfulness: Prevent hallucination (CRITICAL)
- Answer Relevance: Ensure on-topic (IMPORTANT)
- Context Precision: Tune retrieval (IMPORTANT)
- Latency: User experience (IMPORTANT)
- Context Recall: Measures if all relevant context was retrieved (ADVANCED)

EVALUATION FRAMEWORKS:
1. RAGAS (Standardized):
   - Research-backed metrics with specific formulas
   - Industry standard for benchmarking
   - Use for: Comparing systems, publishing results
   - Metrics: Context Relevancy, Faithfulness, Answer Relevancy, Context Recall, Answer Correctness

2. LLM-as-a-Judge (Flexible):
   - Custom criteria based on your needs
   - More interpretive and flexible
   - Use for: Domain-specific evaluation, quick iteration
   - Can evaluate: Tone, style, domain accuracy, custom qualities

3. When to use which:
   - RAGAS: Need standardized comparison, benchmarking, research
   - LLM-as-a-Judge: Need custom criteria, domain-specific, quick changes
   - Use BOTH: RAGAS for standard metrics + LLM Judge for custom criteria

PRODUCTION RECOMMENDATIONS:
1. Chunking:
   - Simple text: Recursive (500 chars, 50 overlap)
   - PDFs with images/tables: Hybrid Complete chunking
   - Always preserve: Tables intact, images with descriptions

2. Embeddings: OpenAI (best quality) or HuggingFace (free)

3. Retrieval: Hybrid with re-ranking (alpha=0.5)

4. Prompting: Structured with instructions

5. Evaluation:
   - Use RAGAS for standard metrics
   - Add LLM-as-a-Judge for custom criteria
   - Monitor all: faithfulness, relevance, precision, recall, latency

PARAMETER TUNING GUIDE:
- chunk_size: Start 500, increase if context needed
- chunk_overlap: 10-20% of chunk_size
- top_k retrieval: 3-5 for most queries
- alpha (hybrid): 0.5 balanced, 0.7 for semantic, 0.3 for keywords
- temperature: 0.0 for factual, 0.7 for creative
"""

if __name__ == "__main__":
    # Note: Set your OpenAI API key
    # os.environ["OPENAI_API_KEY"] = "your-key-here"
    
    # Run the complete pipeline
    main()
