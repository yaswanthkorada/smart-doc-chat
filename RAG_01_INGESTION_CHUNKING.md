# 📄 Part 1: Data Ingestion & Advanced Chunking Strategies

**Level:** Beginner → Intermediate  
**Time:** 8-10 hours  
**Prerequisites:** Basic understanding of text embeddings and vector stores

---

## 🎯 Learning Objectives

By the end of this module, you'll be able to:
- [ ] Understand why naive chunking fails for complex documents
- [ ] Implement **Semantic Chunking** (chunk by meaning, not by character count)
- [ ] Build **Parent-Document Retrieval** (retrieve summaries, return full context)
- [ ] Handle document structures (tables, lists, multi-column PDFs)
- [ ] Optimize chunk size for your specific use case
- [ ] Measure chunking quality with retrieval metrics

---

## ❌ The Problem: Naive Chunking Breaks Context

### Current Implementation (Your Project)
```python
# utils/rag_engine.py or similar
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Split every 1000 chars
    chunk_overlap=200     # Overlap 200 chars
)

chunks = text_splitter.split_text(document_text)
```

### Why This Fails

#### Example: Financial Report PDF
```
Original Document:
─────────────────────────────────────
Q3 Revenue Analysis

Our Q3 revenue reached $5.2M, representing a 
15% increase compared to Q2. This growth was 
driven by three key factors:

1. Enterprise segment: +$800K
2. SMB segment: +$300K  
3. International: +$200K

The enterprise segment showed exceptional
performance due to our new pricing strategy...
─────────────────────────────────────

Naive Chunking (chunk_size=150):
─────────────────────────────────────
Chunk 1: "Q3 Revenue Analysis\n\nOur Q3 revenue 
reached $5.2M, representing a 15% increase 
compared to Q2. This growth was driven"

Chunk 2: "by three key factors:\n\n1. Enterprise 
segment: +$800K\n2. SMB segment: +$300K\n3. 
International: +$200K\n\nThe enterprise"

Chunk 3: "segment showed exceptional performance 
due to our new pricing strategy and increased"
─────────────────────────────────────
```

**Problems:**
1. ⚠️ **Context Broken**: "driven" is separated from "by three key factors"
2. ⚠️ **Orphaned Lists**: List items split from their intro
3. ⚠️ **Lost Semantics**: "The enterprise segment" separated from its metrics
4. ⚠️ **Arbitrary Splits**: Chunks don't respect semantic boundaries

### Real Impact on Your System

When user asks: *"What drove Q3 revenue growth?"*

**With Naive Chunking:**
```
Retrieved Chunk 1: "Q3 revenue reached $5.2M..."
→ LLM sees the number but not the explanation ❌
```

**With Semantic Chunking:**
```
Retrieved Chunk: "Q3 revenue reached $5.2M... driven by three key factors:
1. Enterprise segment: +$800K
2. SMB segment: +$300K
3. International: +$200K"
→ LLM sees the complete answer ✅
```

---

## ✅ Solution 1: Semantic Chunking

**Concept:** Split by semantic boundaries (meaning changes), not by character count.

### How It Works

```
Semantic Chunking Process:
──────────────────────────
1. Embed each sentence
2. Calculate similarity between consecutive sentences
3. When similarity drops below threshold → CREATE NEW CHUNK
4. Keep semantically related sentences together
```

### Implementation

#### Step 1: Install Dependencies
```bash
pip install langchain-experimental
pip install langchain-openai
pip install sentence-transformers  # For local embeddings
```

#### Step 2: Basic Semantic Chunking
```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

# Initialize semantic chunker
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"  # Cheaper, faster
)

semantic_chunker = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",  # or "standard_deviation", "interquartile"
    breakpoint_threshold_amount=0.95  # Top 5% similarity drops = new chunk
)

# Split document
chunks = semantic_chunker.create_documents([document_text])

# Result: Chunks respect semantic boundaries
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {chunk.page_content[:100]}...")
```

#### Step 3: Advanced - Custom Semantic Chunker

```python
from typing import List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class AdvancedSemanticChunker:
    """
    Senior-level semantic chunker with fine-grained control
    """
    
    def __init__(
        self,
        embeddings,
        max_chunk_size: int = 1500,  # Hard limit
        similarity_threshold: float = 0.75,  # Create new chunk if similarity < this
        min_chunk_size: int = 300,  # Don't create tiny chunks
    ):
        self.embeddings = embeddings
        self.max_chunk_size = max_chunk_size
        self.similarity_threshold = similarity_threshold
        self.min_chunk_size = min_chunk_size
    
    def split_text(self, text: str) -> List[str]:
        """Split text into semantic chunks"""
        # Split into sentences
        sentences = self._split_into_sentences(text)
        
        # Embed each sentence
        sentence_embeddings = self._embed_sentences(sentences)
        
        # Find semantic boundaries
        boundaries = self._find_boundaries(sentence_embeddings)
        
        # Create chunks respecting boundaries and size limits
        chunks = self._create_chunks(sentences, boundaries)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences (basic implementation)"""
        import re
        # Handle abbreviations
        text = re.sub(r'\b([A-Z][a-z]?)\.\s', r'\1<dot> ', text)
        sentences = re.split(r'[.!?]\s+', text)
        sentences = [s.replace('<dot>', '.') for s in sentences]
        return [s.strip() for s in sentences if s.strip()]
    
    def _embed_sentences(self, sentences: List[str]) -> np.ndarray:
        """Embed all sentences"""
        embeddings_list = self.embeddings.embed_documents(sentences)
        return np.array(embeddings_list)
    
    def _find_boundaries(self, embeddings: np.ndarray) -> List[int]:
        """Find semantic boundaries based on similarity drops"""
        boundaries = [0]  # Start of first chunk
        
        for i in range(len(embeddings) - 1):
            # Calculate similarity between consecutive sentences
            similarity = cosine_similarity(
                embeddings[i].reshape(1, -1),
                embeddings[i + 1].reshape(1, -1)
            )[0][0]
            
            # If similarity drops below threshold, mark boundary
            if similarity < self.similarity_threshold:
                boundaries.append(i + 1)
        
        boundaries.append(len(embeddings))  # End of last chunk
        return boundaries
    
    def _create_chunks(self, sentences: List[str], boundaries: List[int]) -> List[str]:
        """Create chunks from sentences and boundaries"""
        chunks = []
        
        for i in range(len(boundaries) - 1):
            start_idx = boundaries[i]
            end_idx = boundaries[i + 1]
            
            chunk_sentences = sentences[start_idx:end_idx]
            chunk_text = ' '.join(chunk_sentences)
            
            # Enforce size limits
            if len(chunk_text) > self.max_chunk_size:
                # Split large chunk into smaller ones
                sub_chunks = self._split_large_chunk(chunk_text)
                chunks.extend(sub_chunks)
            elif len(chunk_text) >= self.min_chunk_size:
                chunks.append(chunk_text)
            else:
                # Merge small chunk with previous
                if chunks:
                    chunks[-1] += ' ' + chunk_text
                else:
                    chunks.append(chunk_text)
        
        return chunks
    
    def _split_large_chunk(self, text: str) -> List[str]:
        """Split a large chunk that exceeds max_chunk_size"""
        # Fall back to simple splitting for oversized chunks
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > self.max_chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks


# Usage in your project
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
chunker = AdvancedSemanticChunker(
    embeddings=embeddings,
    max_chunk_size=1500,
    similarity_threshold=0.75,
    min_chunk_size=300
)

chunks = chunker.split_text(document_text)
```

### Pro Tip: Choosing the Right Threshold

```python
def find_optimal_threshold(document: str, test_queries: List[str]):
    """
    Experiment with different thresholds to find the best one
    """
    thresholds = [0.65, 0.70, 0.75, 0.80, 0.85, 0.90]
    results = {}
    
    for threshold in thresholds:
        chunker = AdvancedSemanticChunker(
            embeddings=embeddings,
            similarity_threshold=threshold
        )
        chunks = chunker.split_text(document)
        
        # Test retrieval quality
        vectorstore = create_vectorstore(chunks)
        retrieval_quality = evaluate_retrieval(vectorstore, test_queries)
        
        results[threshold] = {
            "num_chunks": len(chunks),
            "avg_chunk_size": np.mean([len(c) for c in chunks]),
            "retrieval_quality": retrieval_quality
        }
        
        print(f"Threshold {threshold}:")
        print(f"  Chunks: {len(chunks)}")
        print(f"  Avg Size: {results[threshold]['avg_chunk_size']:.0f} chars")
        print(f"  Retrieval Quality: {retrieval_quality:.3f}\n")
    
    return results

# Run experiment
results = find_optimal_threshold(
    document=your_pdf_text,
    test_queries=["What was Q3 revenue?", "Who is the CEO?", ...]
)
```

---

## ✅ Solution 2: Parent-Document Retrieval

**Concept:** Retrieve small summaries (fast, precise), but return full parent context (complete).

### The Problem with Fixed-Size Chunks

```
User Question: "Explain our pricing strategy"

Current Approach:
─────────────────
Retrieved Chunk: "...tier involves three components:
basic features, advanced analytics, and..."
→ Missing context: What tier? What's the overall strategy? ❌

Parent-Document Approach:
─────────────────────────
Retrieved Summary: "Section 3: Pricing Strategy Overview"
↓
Return Full Section: "Our pricing strategy uses a three-tier 
model designed for different customer segments. Enterprise 
tier involves three components: basic features, advanced 
analytics, and premium support..."
→ Complete context! ✅
```

### Implementation

#### Step 1: Create Parent-Child Store
```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Initialize components
vectorstore = Chroma(
    collection_name="child_chunks",
    embedding_function=embeddings
)

# Storage for parent documents
parent_store = InMemoryStore()

# Define splitting strategy
child_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,    # Small chunks for retrieval
    chunk_overlap=50
)

parent_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,   # Large parent documents
    chunk_overlap=200
)

# Create parent-document retriever
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=parent_store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

# Add documents
from langchain.schema import Document

documents = [
    Document(page_content=pdf_text, metadata={"source": "financial_report.pdf"})
]

retriever.add_documents(documents)

# Retrieve
query = "What was Q3 revenue?"
results = retriever.get_relevant_documents(query)

# Results contain full parent documents, not just child chunks!
for doc in results:
    print(f"Retrieved {len(doc.page_content)} chars")  # ~2000 chars
    print(doc.page_content[:200])
```

#### Step 2: Production-Ready Implementation

```python
import chromadb
from typing import List, Dict
from langchain.schema import Document

class ProductionParentDocRetriever:
    """
    Production-grade parent-document retrieval with ChromaDB persistence
    """
    
    def __init__(
        self,
        user_id: str,
        collection_name: str = "parent_doc_retrieval",
        child_chunk_size: int = 400,
        parent_chunk_size: int = 2000,
    ):
        self.user_id = user_id
        self.child_chunk_size = child_chunk_size
        self.parent_chunk_size = parent_chunk_size
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=f"./data/chroma_data/{user_id}_parent_doc"
        )
        
        # Create collections
        self.child_collection = self.chroma_client.get_or_create_collection(
            name=f"{collection_name}_children",
            metadata={"description": "Child chunks for retrieval"}
        )
        
        self.parent_collection = self.chroma_client.get_or_create_collection(
            name=f"{collection_name}_parents",
            metadata={"description": "Parent documents"}
        )
        
        # Initialize embeddings
        from langchain_openai import OpenAIEmbeddings
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    def ingest_document(self, document: Document) -> Dict:
        """
        Ingest document with parent-child splitting
        """
        # Create parent chunks
        parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.parent_chunk_size,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        parent_chunks = parent_splitter.split_documents([document])
        
        total_children = 0
        
        for parent_idx, parent_doc in enumerate(parent_chunks):
            parent_id = f"parent_{document.metadata.get('source')}_{parent_idx}"
            
            # Store parent document
            parent_embedding = self.embeddings.embed_documents([parent_doc.page_content])[0]
            self.parent_collection.add(
                ids=[parent_id],
                embeddings=[parent_embedding],
                documents=[parent_doc.page_content],
                metadatas=[{
                    **parent_doc.metadata,
                    "parent_id": parent_id,
                    "chunk_index": parent_idx
                }]
            )
            
            # Create child chunks from this parent
            child_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.child_chunk_size,
                chunk_overlap=50,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            child_chunks = child_splitter.split_text(parent_doc.page_content)
            
            # Store child chunks with reference to parent
            child_ids = []
            child_embeddings = []
            child_metadatas = []
            
            for child_idx, child_text in enumerate(child_chunks):
                child_id = f"{parent_id}_child_{child_idx}"
                child_embedding = self.embeddings.embed_documents([child_text])[0]
                
                child_ids.append(child_id)
                child_embeddings.append(child_embedding)
                child_metadatas.append({
                    **parent_doc.metadata,
                    "parent_id": parent_id,
                    "child_index": child_idx
                })
            
            # Batch add children
            if child_ids:
                self.child_collection.add(
                    ids=child_ids,
                    embeddings=child_embeddings,
                    documents=child_chunks,
                    metadatas=child_metadatas
                )
                total_children += len(child_ids)
        
        return {
            "num_parents": len(parent_chunks),
            "num_children": total_children,
            "avg_children_per_parent": total_children / len(parent_chunks)
        }
    
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve parent documents by searching children
        """
        # Embed query
        query_embedding = self.embeddings.embed_documents([query])[0]
        
        # Search child collection
        child_results = self.child_collection.query(
            query_embeddings=[query_embedding],
            n_results=k * 2  # Retrieve more children, then deduplicate parents
        )
        
        # Get unique parent IDs
        parent_ids = set()
        for metadata in child_results['metadatas'][0]:
            parent_ids.add(metadata['parent_id'])
        
        # Retrieve parent documents
        parent_docs = []
        if parent_ids:
            parent_results = self.parent_collection.get(
                ids=list(parent_ids)
            )
            
            for i, parent_id in enumerate(parent_results['ids']):
                parent_docs.append(Document(
                    page_content=parent_results['documents'][i],
                    metadata=parent_results['metadatas'][i]
                ))
        
        # Return top k parents
        return parent_docs[:k]
    
    def retrieve_with_scores(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """
        Retrieve with relevance scores
        """
        query_embedding = self.embeddings.embed_documents([query])[0]
        
        child_results = self.child_collection.query(
            query_embeddings=[query_embedding],
            n_results=k * 2
        )
        
        # Map parent_id to best child score
        parent_scores = {}
        for i, metadata in enumerate(child_results['metadatas'][0]):
            parent_id = metadata['parent_id']
            distance = child_results['distances'][0][i]
            score = 1 / (1 + distance)  # Convert distance to score
            
            if parent_id not in parent_scores or score > parent_scores[parent_id]:
                parent_scores[parent_id] = score
        
        # Retrieve parent documents with scores
        parent_docs_with_scores = []
        if parent_scores:
            parent_results = self.parent_collection.get(
                ids=list(parent_scores.keys())
            )
            
            for i, parent_id in enumerate(parent_results['ids']):
                doc = Document(
                    page_content=parent_results['documents'][i],
                    metadata=parent_results['metadatas'][i]
                )
                score = parent_scores[parent_id]
                parent_docs_with_scores.append((doc, score))
        
        # Sort by score and return top k
        parent_docs_with_scores.sort(key=lambda x: x[1], reverse=True)
        return parent_docs_with_scores[:k]


# Usage in your project
retriever = ProductionParentDocRetriever(
    user_id="user_123",
    collection_name="documents",
    child_chunk_size=400,
    parent_chunk_size=2000
)

# Ingest document
from langchain.schema import Document
doc = Document(
    page_content=pdf_text,
    metadata={"source": "financial_report.pdf", "doc_id": "doc_123"}
)
stats = retriever.ingest_document(doc)
print(f"Created {stats['num_parents']} parents, {stats['num_children']} children")

# Retrieve
results = retriever.retrieve("What was Q3 revenue?", k=3)
for doc in results:
    print(f"Parent Doc ({len(doc.page_content)} chars):")
    print(doc.page_content[:300])
    print("─" * 50)
```

### When to Use Parent-Document Retrieval

✅ **Use When:**
- Documents have clear hierarchical structure (sections, chapters)
- Users need full context to understand the answer
- You have documents with headings/subheadings
- Context window is large enough (8K+ tokens)

❌ **Don't Use When:**
- Documents are already small (< 1000 chars)
- You need maximum precision (parent docs can be noisy)
- Limited context window (< 4K tokens)
- Simple Q&A where small chunks suffice

---

## 🏗️ Solution 3: Structure-Aware Chunking

**Concept:** Respect document structure (headings, tables, lists) when chunking.

### The Problem

```markdown
# Financial Summary

## Q3 Results
Revenue: $5.2M
Expenses: $3.1M
Net Income: $2.1M

## Q4 Forecast
Expected Revenue: $6.0M
```

**Naive Chunking** might split the table mid-row or separate headings from their content.

**Structure-Aware Chunking** keeps sections together.

### Implementation

```python
from typing import List, Dict
import re

class StructureAwareChunker:
    """
    Chunk documents while respecting structure (headings, lists, tables)
    """
    
    def __init__(
        self,
        max_chunk_size: int = 1500,
        min_chunk_size: int = 300,
        respect_headings: bool = True,
        keep_tables_together: bool = True,
    ):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.respect_headings = respect_headings
        self.keep_tables_together = keep_tables_together
    
    def chunk_document(self, text: str) -> List[Dict]:
        """
        Chunk document with structure awareness
        Returns list of dicts: {content, metadata}
        """
        # Parse document structure
        sections = self._parse_sections(text)
        
        # Create chunks respecting structure
        chunks = []
        for section in sections:
            section_chunks = self._chunk_section(section)
            chunks.extend(section_chunks)
        
        return chunks
    
    def _parse_sections(self, text: str) -> List[Dict]:
        """
        Parse document into sections based on headings
        """
        sections = []
        current_section = {"heading": "", "content": [], "level": 0}
        
        for line in text.split('\n'):
            # Check for markdown heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match and self.respect_headings:
                # Save previous section
                if current_section["content"]:
                    sections.append(current_section)
                
                # Start new section
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2)
                current_section = {
                    "heading": heading_text,
                    "content": [],
                    "level": level
                }
            else:
                current_section["content"].append(line)
        
        # Add last section
        if current_section["content"]:
            sections.append(current_section)
        
        return sections
    
    def _chunk_section(self, section: Dict) -> List[Dict]:
        """
        Chunk a single section
        """
        heading = section["heading"]
        content = '\n'.join(section["content"])
        full_text = f"# {heading}\n\n{content}" if heading else content
        
        # If section is small enough, keep as single chunk
        if len(full_text) <= self.max_chunk_size:
            return [{
                "content": full_text,
                "metadata": {
                    "heading": heading,
                    "level": section["level"],
                    "type": "section"
                }
            }]
        
        # Otherwise, split section into sub-chunks
        chunks = []
        
        # Try to split by paragraphs first
        paragraphs = content.split('\n\n')
        current_chunk = f"# {heading}\n\n" if heading else ""
        
        for para in paragraphs:
            # Check if this is a table
            if self._is_table(para) and self.keep_tables_together:
                # Keep entire table in one chunk
                if current_chunk and len(current_chunk) > len(heading) + 10:
                    chunks.append({
                        "content": current_chunk.strip(),
                        "metadata": {
                            "heading": heading,
                            "level": section["level"],
                            "type": "section"
                        }
                    })
                    current_chunk = f"# {heading}\n\n" if heading else ""
                
                chunks.append({
                    "content": f"# {heading}\n\n{para}" if heading else para,
                    "metadata": {
                        "heading": heading,
                        "level": section["level"],
                        "type": "table"
                    }
                })
                continue
            
            # Add paragraph to current chunk
            test_chunk = current_chunk + '\n\n' + para
            if len(test_chunk) > self.max_chunk_size:
                # Save current chunk
                if len(current_chunk) >= self.min_chunk_size:
                    chunks.append({
                        "content": current_chunk.strip(),
                        "metadata": {
                            "heading": heading,
                            "level": section["level"],
                            "type": "section"
                        }
                    })
                current_chunk = f"# {heading}\n\n{para}" if heading else para
            else:
                current_chunk = test_chunk
        
        # Add remaining chunk
        if current_chunk and len(current_chunk) >= self.min_chunk_size:
            chunks.append({
                "content": current_chunk.strip(),
                "metadata": {
                    "heading": heading,
                    "level": section["level"],
                    "type": "section"
                }
            })
        
        return chunks
    
    def _is_table(self, text: str) -> bool:
        """
        Detect if text contains a table
        """
        lines = text.split('\n')
        if len(lines) < 2:
            return False
        
        # Look for markdown table indicators
        has_pipe = any('|' in line for line in lines)
        has_separator = any(re.match(r'^\s*[\|\-\+\:]+\s*$', line) for line in lines)
        
        return has_pipe or has_separator


# Usage
chunker = StructureAwareChunker(
    max_chunk_size=1500,
    respect_headings=True,
    keep_tables_together=True
)

chunks = chunker.chunk_document(markdown_text)

for chunk_data in chunks:
    print(f"Heading: {chunk_data['metadata']['heading']}")
    print(f"Type: {chunk_data['metadata']['type']}")
    print(f"Content: {chunk_data['content'][:100]}...")
    print("─" * 50)
```

---

## 🎯 Integration into Your Project

### Step 1: Update `utils/rag_engine.py`

```python
# utils/rag_engine.py

from utils.advanced_chunking import AdvancedChunkingPipeline
from langchain_openai import OpenAIEmbeddings

class ImprovedRAGEngine:
    def __init__(self, user_id: str, ai_provider: str = "openai"):
        self.user_id = user_id
        self.ai_provider = ai_provider
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        
        # Initialize advanced chunking
        self.chunking_pipeline = AdvancedChunkingPipeline(
            user_id=user_id,
            embeddings=self.embeddings,
            strategy="parent_document"  # or "semantic", "structure_aware"
        )
    
    def ingest_document(self, document_path: str, document_id: str):
        """
        Ingest document with advanced chunking
        """
        # Extract text from PDF/DOCX
        text = self._extract_text(document_path)
        
        # Chunk with advanced strategy
        stats = self.chunking_pipeline.ingest(
            text=text,
            metadata={
                "document_id": document_id,
                "source": document_path
            }
        )
        
        print(f"Ingested {stats['num_chunks']} chunks")
        return stats
    
    def query(self, question: str, k: int = 5):
        """
        Query with advanced retrieval
        """
        # Retrieve relevant chunks
        results = self.chunking_pipeline.retrieve(question, k=k)
        
        # Generate answer
        context = '\n\n'.join([doc.page_content for doc in results])
        answer = self._generate_answer(question, context)
        
        return {
            "answer": answer,
            "sources": results
        }
```

### Step 2: Create Unified Chunking Module

```python
# utils/advanced_chunking.py

from typing import List, Dict, Literal
from langchain.schema import Document

class AdvancedChunkingPipeline:
    """
    Unified interface for all advanced chunking strategies
    """
    
    def __init__(
        self,
        user_id: str,
        embeddings,
        strategy: Literal["semantic", "parent_document", "structure_aware"] = "parent_document"
    ):
        self.user_id = user_id
        self.embeddings = embeddings
        self.strategy = strategy
        
        # Initialize appropriate chunker
        if strategy == "semantic":
            from utils.semantic_chunker import AdvancedSemanticChunker
            self.chunker = AdvancedSemanticChunker(
                embeddings=embeddings,
                max_chunk_size=1500,
                similarity_threshold=0.75
            )
        elif strategy == "parent_document":
            from utils.parent_doc_retriever import ProductionParentDocRetriever
            self.chunker = ProductionParentDocRetriever(
                user_id=user_id,
                child_chunk_size=400,
                parent_chunk_size=2000
            )
        elif strategy == "structure_aware":
            from utils.structure_chunker import StructureAwareChunker
            self.chunker = StructureAwareChunker(
                max_chunk_size=1500,
                respect_headings=True,
                keep_tables_together=True
            )
    
    def ingest(self, text: str, metadata: Dict) -> Dict:
        """
        Ingest document with selected strategy
        """
        doc = Document(page_content=text, metadata=metadata)
        
        if self.strategy == "parent_document":
            return self.chunker.ingest_document(doc)
        else:
            chunks = self.chunker.split_text(text) if hasattr(self.chunker, 'split_text') else self.chunker.chunk_document(text)
            # Store in vectorstore...
            return {"num_chunks": len(chunks)}
    
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve with selected strategy
        """
        if self.strategy == "parent_document":
            return self.chunker.retrieve(query, k=k)
        else:
            # Use standard retrieval...
            pass
```

---

## 📊 Measuring Chunking Quality

### Metrics to Track

```python
class ChunkingEvaluator:
    """
    Evaluate chunking quality
    """
    
    def evaluate_chunking(
        self,
        chunks: List[str],
        test_queries: List[str],
        ground_truth_answers: List[str]
    ) -> Dict:
        """
        Evaluate chunking strategy
        """
        metrics = {
            "chunk_stats": self._calculate_chunk_stats(chunks),
            "retrieval_quality": self._evaluate_retrieval(chunks, test_queries, ground_truth_answers),
            "context_completeness": self._evaluate_completeness(chunks, test_queries)
        }
        return metrics
    
    def _calculate_chunk_stats(self, chunks: List[str]) -> Dict:
        """Basic chunk statistics"""
        lengths = [len(c) for c in chunks]
        return {
            "num_chunks": len(chunks),
            "avg_length": np.mean(lengths),
            "std_length": np.std(lengths),
            "min_length": min(lengths),
            "max_length": max(lengths)
        }
    
    def _evaluate_retrieval(
        self,
        chunks: List[str],
        test_queries: List[str],
        ground_truth: List[str]
    ) -> Dict:
        """
        Evaluate retrieval quality
        """
        # Create vectorstore from chunks
        vectorstore = self._create_vectorstore(chunks)
        
        hits = 0
        total_queries = len(test_queries)
        
        for query, expected in zip(test_queries, ground_truth):
            # Retrieve top 5 chunks
            results = vectorstore.similarity_search(query, k=5)
            retrieved_text = '\n'.join([r.page_content for r in results])
            
            # Check if expected answer is in retrieved text
            if expected.lower() in retrieved_text.lower():
                hits += 1
        
        recall = hits / total_queries
        return {
            "recall@5": recall,
            "hits": hits,
            "total": total_queries
        }
    
    def _evaluate_completeness(
        self,
        chunks: List[str],
        test_queries: List[str]
    ) -> float:
        """
        Check if retrieved chunks have complete context
        """
        # TODO: Implement context completeness check
        # Use LLM to verify if retrieved context is sufficient
        pass


# Usage
evaluator = ChunkingEvaluator()

# Compare naive vs semantic chunking
naive_chunks = naive_chunker.split_text(document)
semantic_chunks = semantic_chunker.split_text(document)

naive_metrics = evaluator.evaluate_chunking(
    chunks=naive_chunks,
    test_queries=["What was Q3 revenue?", "Who is the CEO?"],
    ground_truth_answers=["$5.2M", "John Smith"]
)

semantic_metrics = evaluator.evaluate_chunking(
    chunks=semantic_chunks,
    test_queries=["What was Q3 revenue?", "Who is the CEO?"],
    ground_truth_answers=["$5.2M", "John Smith"]
)

print("Naive Chunking:")
print(f"  Recall@5: {naive_metrics['retrieval_quality']['recall@5']:.3f}")

print("\nSemantic Chunking:")
print(f"  Recall@5: {semantic_metrics['retrieval_quality']['recall@5']:.3f}")
```

---

## 💡 Pro Tips from a Senior AI Engineer

### Tip #1: Start with Structure-Aware, Then Add Semantic

```python
# Best practice: Combine both strategies
def hybrid_chunking(document: str):
    # Step 1: Split by structure (sections, headings)
    structure_chunker = StructureAwareChunker()
    sections = structure_chunker.chunk_document(document)
    
    # Step 2: For large sections, apply semantic chunking
    semantic_chunker = AdvancedSemanticChunker()
    final_chunks = []
    
    for section in sections:
        if len(section['content']) > 2000:
            # Large section → semantic chunking
            sub_chunks = semantic_chunker.split_text(section['content'])
            final_chunks.extend(sub_chunks)
        else:
            # Small section → keep as is
            final_chunks.append(section['content'])
    
    return final_chunks
```

### Tip #2: Overlap is Still Important (Even with Semantic)

```python
# Add overlap to prevent context loss at boundaries
def add_overlap(chunks: List[str], overlap_sentences: int = 2) -> List[str]:
    """
    Add overlap between chunks (last N sentences of previous chunk)
    """
    overlapped = []
    
    for i, chunk in enumerate(chunks):
        if i > 0:
            # Get last N sentences from previous chunk
            prev_sentences = chunks[i-1].split('. ')[-overlap_sentences:]
            overlap_text = '. '.join(prev_sentences) + '. '
            overlapped.append(overlap_text + chunk)
        else:
            overlapped.append(chunk)
    
    return overlapped
```

### Tip #3: Different Document Types Need Different Strategies

```python
def choose_chunking_strategy(document_type: str, document_text: str):
    """
    Choose strategy based on document type
    """
    strategies = {
        # Technical documents with code → structure-aware
        "technical_doc": StructureAwareChunker(keep_tables_together=True),
        
        # Narrative documents (reports, articles) → semantic
        "narrative": AdvancedSemanticChunker(similarity_threshold=0.75),
        
        # Legal/contracts with long paragraphs → parent-document
        "legal": ProductionParentDocRetriever(parent_chunk_size=3000),
        
        # Mixed documents → hybrid
        "mixed": HybridChunker()
    }
    
    return strategies.get(document_type, AdvancedSemanticChunker())
```

### Tip #4: Monitor Chunk Size Distribution

```python
import matplotlib.pyplot as plt

def visualize_chunk_distribution(chunks: List[str]):
    """
    Visualize chunk size distribution
    """
    lengths = [len(c) for c in chunks]
    
    plt.figure(figsize=(10, 6))
    plt.hist(lengths, bins=30, edgecolor='black')
    plt.axvline(np.mean(lengths), color='red', linestyle='--', label=f'Mean: {np.mean(lengths):.0f}')
    plt.axvline(np.median(lengths), color='green', linestyle='--', label=f'Median: {np.median(lengths):.0f}')
    plt.xlabel('Chunk Size (characters)')
    plt.ylabel('Frequency')
    plt.title('Chunk Size Distribution')
    plt.legend()
    plt.show()
    
    print(f"Total chunks: {len(chunks)}")
    print(f"Mean: {np.mean(lengths):.0f} chars")
    print(f"Std Dev: {np.std(lengths):.0f} chars")
    print(f"Min: {min(lengths)} chars")
    print(f"Max: {max(lengths)} chars")

# Usage
naive_chunks = naive_chunker.split_text(document)
semantic_chunks = semantic_chunker.split_text(document)

print("Naive Chunking:")
visualize_chunk_distribution(naive_chunks)

print("\nSemantic Chunking:")
visualize_chunk_distribution(semantic_chunks)
```

---

## ✅ Exercises

### Exercise 1: Implement Semantic Chunking
1. Take one of your existing PDF documents
2. Implement `AdvancedSemanticChunker`
3. Compare chunk boundaries with naive chunking
4. Measure retrieval quality improvement

### Exercise 2: Build Parent-Document Retrieval
1. Implement `ProductionParentDocRetriever`
2. Ingest a multi-page document
3. Test retrieval with complex queries
4. Compare context quality with regular chunking

### Exercise 3: Evaluate Chunking Strategies
1. Create a test set of 10 questions for your documents
2. Test 3 strategies: naive, semantic, parent-document
3. Measure recall@5 for each
4. Choose the best strategy for your use case

---

## 🎯 Next Steps

Continue to [Part 2: Advanced Retrieval Strategies →](RAG_02_ADVANCED_RETRIEVAL.md)

You'll learn:
- Hybrid Search (BM25 + Vector)
- Re-ranking with Cohere/BGE
- Handling "Lost in the Middle" problem
- Ensemble retrieval strategies

---

*Part of the Advanced RAG Mastery series for Smart Document Chat*  
*Last Updated: January 11, 2026*
