# 📄 Part 2: Advanced Retrieval Strategies

**Level:** Intermediate → Advanced  
**Time:** 10-12 hours  
**Prerequisites:** Part 1 (Chunking completed)

---

## 🎯 Learning Objectives

By the end of this module, you'll be able to:
- [ ] Understand why vector search alone misses 30-40% of relevant results
- [ ] Implement **Hybrid Search** (BM25 keyword + Vector semantic)
- [ ] Integrate **Re-ranking** with Cohere or BGE to improve precision by 35%+
- [ ] Build **Ensemble Retrievers** combining multiple strategies
- [ ] Handle the **"Lost in the Middle"** problem
- [ ] Implement **MMR** (Maximum Marginal Relevance) for diverse results
- [ ] Optimize retrieval performance and costs

---

## ❌ The Problem: Vector Search Limitations

### Scenario: User Asks "Q3 2024 revenue"

#### With Vector-Only Search
```python
# Current implementation
query = "Q3 2024 revenue"
query_embedding = embeddings.embed_query(query)
results = vectorstore.similarity_search_by_vector(query_embedding, k=5)
```

**What Gets Retrieved:**
```
❌ Chunk 1: "The third quarter showed strong performance..." (0.82 similarity)
❌ Chunk 2: "Revenue growth in recent quarters..." (0.79 similarity)
❌ Chunk 3: "Q2 2024 financial results..." (0.78 similarity)
✅ Chunk 4: "Q3 2024 revenue was $5.2M..." (0.76 similarity)
❌ Chunk 5: "Quarterly revenue trends..." (0.75 similarity)
```

**Problems:**
1. 🔴 **Exact match missed**: "Q3 2024 revenue" has LOWER similarity than vague phrases!
2. 🔴 **Semantic drift**: Vector search retrieves "related" but not "exact" content
3. 🔴 **No keyword awareness**: "Q3" and "2024" should be REQUIRED, not optional
4. 🔴 **Wrong ordering**: Most relevant chunk (#4) is ranked #4, not #1

---

## ✅ Solution 1: Hybrid Search (BM25 + Vector)

**Concept:** Combine keyword-based (BM25) + semantic (Vector) search for best of both worlds.

### BM25 Explained (5-Minute Primer)

BM25 (Best Matching 25) is a keyword-based algorithm that:
- Counts how often query terms appear in documents
- Rewards **exact matches**
- Considers **term frequency** (TF) and **document frequency** (IDF)
- Fast and deterministic (no ML needed)

```
Query: "Q3 2024 revenue"

BM25 Scoring:
─────────────────────────────────────
Document 1: "Q3 2024 revenue was $5.2M"
→ Contains all 3 terms: HIGH SCORE ✅

Document 2: "Third quarter revenue trends"  
→ Missing "2024", "Q3": LOW SCORE ❌

Document 3: "Revenue growth in quarters"
→ Only "revenue" matches: MEDIUM SCORE ⚠️
```

### Why Hybrid is Superior

```
Query: "Q3 2024 revenue"

BM25 Results:
─────────────────────────────────────
1. "Q3 2024 revenue was $5.2M" (exact match) ✅
2. "Q3 revenue breakdown by segment" (partial match)
3. "2024 quarterly revenue report" (partial match)

Vector Results:
─────────────────────────────────────
1. "Third quarter financial performance" (semantic) ✅
2. "Revenue growth in recent quarters" (semantic)
3. "Quarterly earnings analysis" (semantic)

Hybrid (BM25 40% + Vector 60%):
─────────────────────────────────────
1. "Q3 2024 revenue was $5.2M" ✅ (top from BM25 + decent vector score)
2. "Third quarter financial performance" ✅ (top from vector + some BM25)
3. "Q3 revenue breakdown by segment" ✅ (good BM25, decent vector)
```

**Result:** Best of both! 🎉

---

## 💻 Implementation: Hybrid Search

### Step 1: Install Dependencies

```bash
pip install rank-bm25
pip install langchain
pip install langchain-community
```

### Step 2: Basic Hybrid Search

```python
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

# Prepare documents
documents = [
    Document(page_content="Q3 2024 revenue was $5.2M, up 15% from Q2.", metadata={"source": "financial_report.pdf"}),
    Document(page_content="Third quarter showed strong performance across all segments.", metadata={"source": "financial_report.pdf"}),
    Document(page_content="Q2 2024 revenue was $4.5M.", metadata={"source": "financial_report.pdf"}),
    # ... more documents
]

# Initialize BM25 retriever (keyword-based)
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 5  # Retrieve top 5

# Initialize Vector retriever (semantic)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory="./chroma_hybrid"
)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Create Ensemble Retriever (combines both)
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.4, 0.6]  # BM25: 40%, Vector: 60%
)

# Retrieve
query = "Q3 2024 revenue"
results = ensemble_retriever.get_relevant_documents(query)

for i, doc in enumerate(results):
    print(f"{i+1}. {doc.page_content[:100]}...")
```

**Output:**
```
1. Q3 2024 revenue was $5.2M, up 15% from Q2...  ✅ (exact match wins!)
2. Third quarter showed strong performance across all segments...
3. Q2 2024 revenue was $4.5M...
```

### Step 3: Production-Ready Hybrid Retriever

```python
import chromadb
from rank_bm25 import BM25Okapi
from typing import List, Tuple
import numpy as np
from langchain.schema import Document

class ProductionHybridRetriever:
    """
    Production-grade hybrid retriever with BM25 + Vector search
    """
    
    def __init__(
        self,
        user_id: str,
        collection_name: str = "documents",
        bm25_weight: float = 0.4,
        vector_weight: float = 0.6,
    ):
        self.user_id = user_id
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight
        
        # Initialize ChromaDB for vector search
        self.chroma_client = chromadb.PersistentClient(
            path=f"./data/chroma_data/{user_id}_hybrid"
        )
        
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embeddings
        from langchain_openai import OpenAIEmbeddings
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # BM25 will be initialized after adding documents
        self.bm25 = None
        self.documents = []  # Cache for BM25
    
    def add_documents(self, documents: List[Document]):
        """
        Add documents to both BM25 and vector store
        """
        self.documents = documents
        
        # Prepare for BM25
        tokenized_docs = [doc.page_content.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        
        # Add to vector store
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        embeddings_list = self.embeddings.embed_documents(texts)
        
        # Generate IDs
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Add to Chroma
        self.collection.add(
            ids=ids,
            embeddings=embeddings_list,
            documents=texts,
            metadatas=metadatas
        )
        
        print(f"Added {len(documents)} documents to hybrid retriever")
    
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve using hybrid search
        """
        # BM25 search
        bm25_scores = self._bm25_search(query, k=k*2)  # Get more candidates
        
        # Vector search
        vector_scores = self._vector_search(query, k=k*2)
        
        # Combine scores using RRF (Reciprocal Rank Fusion)
        combined_scores = self._reciprocal_rank_fusion(bm25_scores, vector_scores)
        
        # Sort by combined score and return top k
        sorted_docs = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:k]
        
        # Return documents
        results = []
        for doc_idx, score in sorted_docs:
            results.append(self.documents[doc_idx])
        
        return results
    
    def _bm25_search(self, query: str, k: int = 10) -> List[Tuple[int, float]]:
        """
        BM25 keyword search
        """
        if self.bm25 is None:
            return []
        
        # Tokenize query
        tokenized_query = query.lower().split()
        
        # Get BM25 scores
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Get top k indices and scores
        top_indices = np.argsort(bm25_scores)[::-1][:k]
        results = [(idx, bm25_scores[idx]) for idx in top_indices if bm25_scores[idx] > 0]
        
        return results
    
    def _vector_search(self, query: str, k: int = 10) -> List[Tuple[int, float]]:
        """
        Vector semantic search
        """
        # Embed query
        query_embedding = self.embeddings.embed_query(query)
        
        # Search in Chroma
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # Convert to (doc_index, score) format
        vector_results = []
        for i, doc_id in enumerate(results['ids'][0]):
            doc_idx = int(doc_id.split('_')[1])
            distance = results['distances'][0][i]
            score = 1 / (1 + distance)  # Convert distance to similarity
            vector_results.append((doc_idx, score))
        
        return vector_results
    
    def _reciprocal_rank_fusion(
        self,
        bm25_results: List[Tuple[int, float]],
        vector_results: List[Tuple[int, float]],
        k: int = 60  # RRF constant
    ) -> dict:
        """
        Combine BM25 and vector scores using Reciprocal Rank Fusion
        
        RRF Formula: score(doc) = Σ(1 / (k + rank_i))
        """
        scores = {}
        
        # Add BM25 scores
        for rank, (doc_idx, _) in enumerate(bm25_results):
            rrf_score = self.bm25_weight / (k + rank + 1)
            scores[doc_idx] = scores.get(doc_idx, 0) + rrf_score
        
        # Add vector scores
        for rank, (doc_idx, _) in enumerate(vector_results):
            rrf_score = self.vector_weight / (k + rank + 1)
            scores[doc_idx] = scores.get(doc_idx, 0) + rrf_score
        
        return scores
    
    def retrieve_with_scores(self, query: str, k: int = 5) -> List[Tuple[Document, float, dict]]:
        """
        Retrieve with detailed scores for debugging
        """
        # Get individual scores
        bm25_results = self._bm25_search(query, k=k*2)
        vector_results = self._vector_search(query, k=k*2)
        
        # Create score mapping
        bm25_scores_dict = {idx: score for idx, score in bm25_results}
        vector_scores_dict = {idx: score for idx, score in vector_results}
        
        # Combine
        combined_scores = self._reciprocal_rank_fusion(bm25_results, vector_results)
        
        # Sort and prepare results
        sorted_docs = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:k]
        
        results = []
        for doc_idx, combined_score in sorted_docs:
            doc = self.documents[doc_idx]
            score_breakdown = {
                "bm25_score": bm25_scores_dict.get(doc_idx, 0),
                "vector_score": vector_scores_dict.get(doc_idx, 0),
                "combined_score": combined_score
            }
            results.append((doc, combined_score, score_breakdown))
        
        return results


# Usage
retriever = ProductionHybridRetriever(
    user_id="user_123",
    bm25_weight=0.4,
    vector_weight=0.6
)

# Add documents
documents = [...]  # Your documents
retriever.add_documents(documents)

# Retrieve
results = retriever.retrieve("Q3 2024 revenue", k=5)

# Or with score breakdown
detailed_results = retriever.retrieve_with_scores("Q3 2024 revenue", k=5)
for doc, score, breakdown in detailed_results:
    print(f"Combined Score: {score:.4f}")
    print(f"  BM25: {breakdown['bm25_score']:.4f}")
    print(f"  Vector: {breakdown['vector_score']:.4f}")
    print(f"  Content: {doc.page_content[:100]}...")
    print("─" * 50)
```

---

## ✅ Solution 2: Re-ranking

**Concept:** Retrieve 20 candidates (fast), then re-rank top 5 (accurate).

### Why Re-ranking Works

```
Initial Retrieval (Hybrid):
─────────────────────────────────────
1. "Q3 revenue analysis shows..." (Score: 0.82)
2. "The quarterly report indicates..." (Score: 0.81)
3. "Q3 2024 revenue was $5.2M" (Score: 0.80) ✅ BEST, but ranked #3
4. "Revenue trends in 2024..." (Score: 0.79)
5. "Financial performance overview..." (Score: 0.78)
...
20. "Company history and background..." (Score: 0.65)

After Re-ranking (Cohere/BGE):
─────────────────────────────────────
1. "Q3 2024 revenue was $5.2M" ✅ (Re-rank score: 0.95)
2. "Q3 revenue analysis shows..." (Re-rank score: 0.88)
3. "Revenue trends in 2024..." (Re-rank score: 0.82)
4. "The quarterly report indicates..." (Re-rank score: 0.79)
5. "Financial performance overview..." (Re-rank score: 0.75)
```

**Result:** Most relevant document moves to #1! 🎯

### Option 1: Cohere Rerank API (Commercial, Best Quality)

```bash
pip install cohere
```

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# Initialize base retriever (hybrid or vector)
base_retriever = hybrid_retriever  # From previous example

# Initialize Cohere reranker
import cohere
cohere_api_key = "your-cohere-api-key"

compressor = CohereRerank(
    cohere_api_key=cohere_api_key,
    top_n=5,  # Return top 5 after reranking
    model="rerank-english-v3.0"  # Latest model
)

# Create compression retriever
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever
)

# Retrieve with reranking
query = "What was Q3 2024 revenue?"
reranked_docs = compression_retriever.get_relevant_documents(query)

for i, doc in enumerate(reranked_docs):
    print(f"{i+1}. {doc.page_content[:100]}...")
```

**Cost:**
- First 1,000 searches/month: FREE
- After: $1 per 1,000 searches
- **Recommendation:** Use for production, cost is negligible vs. quality gain

### Option 2: BGE Reranker (Open-Source, Free)

```bash
pip install sentence-transformers
pip install torch
```

```python
from sentence_transformers import CrossEncoder
from typing import List, Tuple
from langchain.schema import Document

class BGEReranker:
    """
    Open-source reranker using BGE (BAAI General Embedding) model
    """
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-large"):
        """
        Initialize BGE reranker
        
        Models:
        - BAAI/bge-reranker-base: Fast, good quality
        - BAAI/bge-reranker-large: Slower, best quality
        """
        self.model = CrossEncoder(model_name, max_length=512)
    
    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        Rerank documents
        """
        # Prepare query-document pairs
        pairs = [[query, doc.page_content] for doc in documents]
        
        # Get rerank scores
        scores = self.model.predict(pairs)
        
        # Sort by score
        doc_score_pairs = list(zip(documents, scores))
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k
        return doc_score_pairs[:top_k]


# Usage
reranker = BGEReranker(model_name="BAAI/bge-reranker-large")

# First retrieve candidates with hybrid search
candidates = hybrid_retriever.retrieve(query, k=20)  # Get 20 candidates

# Then rerank to get top 5
reranked_results = reranker.rerank(
    query="What was Q3 2024 revenue?",
    documents=candidates,
    top_k=5
)

for i, (doc, score) in enumerate(reranked_results):
    print(f"{i+1}. Score: {score:.4f}")
    print(f"   {doc.page_content[:100]}...")
    print()
```

### Production Integration

```python
class HybridRetrieverWithReranking:
    """
    Complete pipeline: Hybrid Search + Reranking
    """
    
    def __init__(
        self,
        user_id: str,
        use_cohere: bool = False,  # True for Cohere, False for BGE
        cohere_api_key: str = None
    ):
        self.user_id = user_id
        
        # Initialize hybrid retriever
        self.hybrid_retriever = ProductionHybridRetriever(
            user_id=user_id,
            bm25_weight=0.4,
            vector_weight=0.6
        )
        
        # Initialize reranker
        if use_cohere and cohere_api_key:
            from langchain.retrievers.document_compressors import CohereRerank
            self.reranker = CohereRerank(
                cohere_api_key=cohere_api_key,
                top_n=5
            )
            self.reranker_type = "cohere"
        else:
            self.reranker = BGEReranker(model_name="BAAI/bge-reranker-large")
            self.reranker_type = "bge"
    
    def add_documents(self, documents: List[Document]):
        """Add documents to hybrid retriever"""
        self.hybrid_retriever.add_documents(documents)
    
    def retrieve(self, query: str, k: int = 5, num_candidates: int = 20) -> List[Document]:
        """
        Two-stage retrieval:
        1. Hybrid search for candidates (fast, broad)
        2. Reranking for precision (slow, accurate)
        """
        # Stage 1: Hybrid retrieval (get more candidates)
        candidates = self.hybrid_retriever.retrieve(query, k=num_candidates)
        
        # Stage 2: Reranking (narrow down to top k)
        if self.reranker_type == "cohere":
            # Cohere reranking
            reranked = self._cohere_rerank(query, candidates, k)
        else:
            # BGE reranking
            reranked_with_scores = self.reranker.rerank(query, candidates, top_k=k)
            reranked = [doc for doc, score in reranked_with_scores]
        
        return reranked
    
    def _cohere_rerank(self, query: str, documents: List[Document], k: int) -> List[Document]:
        """Cohere reranking implementation"""
        # Prepare documents
        docs_text = [doc.page_content for doc in documents]
        
        # Rerank
        results = self.reranker.compress_documents(
            documents=documents,
            query=query
        )
        
        return results[:k]
    
    def retrieve_with_explanation(self, query: str, k: int = 5) -> dict:
        """
        Retrieve with detailed explanation of ranking
        """
        # Stage 1: Hybrid retrieval
        candidates = self.hybrid_retriever.retrieve_with_scores(query, k=20)
        
        print(f"\n🔍 Stage 1: Hybrid Search (BM25 + Vector)")
        print(f"Retrieved {len(candidates)} candidates\n")
        
        for i, (doc, score, breakdown) in enumerate(candidates[:5], 1):
            print(f"{i}. Combined Score: {score:.4f}")
            print(f"   BM25: {breakdown['bm25_score']:.4f} | Vector: {breakdown['vector_score']:.4f}")
            print(f"   {doc.page_content[:80]}...")
            print()
        
        # Stage 2: Reranking
        candidate_docs = [doc for doc, _, _ in candidates]
        
        if self.reranker_type == "bge":
            reranked = self.reranker.rerank(query, candidate_docs, top_k=k)
            
            print(f"\n🎯 Stage 2: Reranking (BGE)")
            print(f"Top {k} after reranking:\n")
            
            for i, (doc, score) in enumerate(reranked, 1):
                print(f"{i}. Rerank Score: {score:.4f}")
                print(f"   {doc.page_content[:80]}...")
                print()
            
            final_docs = [doc for doc, _ in reranked]
        else:
            final_docs = self._cohere_rerank(query, candidate_docs, k)
            
            print(f"\n🎯 Stage 2: Reranking (Cohere)")
            for i, doc in enumerate(final_docs, 1):
                print(f"{i}. {doc.page_content[:80]}...")
                print()
        
        return {
            "query": query,
            "num_candidates": len(candidates),
            "final_results": final_docs
        }


# Usage
retriever = HybridRetrieverWithReranking(
    user_id="user_123",
    use_cohere=False  # Use BGE (free) instead of Cohere
)

# Add documents
documents = [...]
retriever.add_documents(documents)

# Retrieve with explanation
results = retriever.retrieve_with_explanation(
    query="What was Q3 2024 revenue?",
    k=5
)
```

---

## 🎨 Solution 3: Maximum Marginal Relevance (MMR)

**Problem:** Sometimes top 5 results are too similar (redundant).

```
Query: "company revenue"

Standard Retrieval:
─────────────────────────────────────
1. "Q1 revenue was $4.0M"
2. "Q2 revenue was $4.5M"
3. "Q3 revenue was $5.2M"
4. "Q4 revenue forecast: $6.0M"
5. "Annual revenue target: $20M"

→ All about revenue, but no diversity! ❌
```

**MMR Solution:** Balance relevance + diversity.

```
MMR Retrieval:
─────────────────────────────────────
1. "Q3 revenue was $5.2M" (relevant)
2. "Profit margin increased to 25%" (diverse)
3. "Customer acquisition cost decreased" (diverse)
4. "Market share grew to 15%" (diverse)
5. "Q2 revenue was $4.5M" (relevant)

→ Relevant + diverse information! ✅
```

### Implementation

```python
from langchain_community.vectorstores import Chroma

# Standard retrieval
results_standard = vectorstore.similarity_search("company revenue", k=5)

# MMR retrieval
results_mmr = vectorstore.max_marginal_relevance_search(
    query="company revenue",
    k=5,
    fetch_k=20,  # Fetch 20 candidates, select 5 diverse ones
    lambda_mult=0.7  # 0.7 = 70% relevance, 30% diversity
)

# Compare
print("Standard Retrieval:")
for i, doc in enumerate(results_standard, 1):
    print(f"{i}. {doc.page_content[:80]}...")

print("\nMMR Retrieval (More Diverse):")
for i, doc in enumerate(results_mmr, 1):
    print(f"{i}. {doc.page_content[:80]}...")
```

### Pro Tip: When to Use MMR

```python
def should_use_mmr(query: str) -> bool:
    """
    Decide whether to use MMR based on query type
    """
    # Use MMR for broad queries
    broad_keywords = ["overview", "summary", "analysis", "report", "all"]
    if any(keyword in query.lower() for keyword in broad_keywords):
        return True
    
    # Use standard for specific queries
    specific_patterns = [
        r"\d{4}",  # Year (e.g., "2024")
        r"Q[1-4]",  # Quarter (e.g., "Q3")
        r"\$\d+",  # Money (e.g., "$5M")
    ]
    import re
    if any(re.search(pattern, query) for pattern in specific_patterns):
        return False
    
    return True

# Usage
query = "Give me an overview of company performance"
if should_use_mmr(query):
    results = vectorstore.max_marginal_relevance_search(query, k=5, lambda_mult=0.7)
else:
    results = vectorstore.similarity_search(query, k=5)
```

---

## 🚨 Solution 4: Handling "Lost in the Middle"

**Problem:** LLMs pay less attention to middle context, more to start/end.

### The Research

[Lost in the Middle Paper](https://arxiv.org/abs/2307.03172) found:
- Documents at START: 80% attention
- Documents in MIDDLE: 40% attention ❌
- Documents at END: 75% attention

### Solution Strategies

#### Strategy 1: Reorder by Relevance (Best First & Last)

```python
def reorder_for_llm(documents: List[Document], scores: List[float]) -> List[Document]:
    """
    Reorder documents to avoid "lost in the middle" problem
    
    Pattern: Best → Worst → 2nd Best → 2nd Worst → 3rd Best → ...
    
    Example:
    Input:  [Doc1(0.95), Doc2(0.90), Doc3(0.85), Doc4(0.80), Doc5(0.75)]
    Output: [Doc1(0.95), Doc5(0.75), Doc2(0.90), Doc4(0.80), Doc3(0.85)]
                ↑ BEST      ↑ WORST   ↑ 2nd BEST  ↑ 2nd WORST  ↑ MIDDLE
    """
    # Sort by score
    doc_score_pairs = list(zip(documents, scores))
    doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
    
    # Reorder: best first, worst second, 2nd best third, etc.
    reordered = []
    left = 0
    right = len(doc_score_pairs) - 1
    toggle = True
    
    while left <= right:
        if toggle:
            reordered.append(doc_score_pairs[left][0])
            left += 1
        else:
            reordered.append(doc_score_pairs[right][0])
            right -= 1
        toggle = not toggle
    
    return reordered


# Usage
query = "What was Q3 revenue?"
docs_with_scores = retriever.retrieve_with_scores(query, k=10)

documents = [doc for doc, score, _ in docs_with_scores]
scores = [score for _, score, _ in docs_with_scores]

reordered_docs = reorder_for_llm(documents, scores)

# Now pass reordered_docs to LLM
context = '\n\n'.join([doc.page_content for doc in reordered_docs])
```

#### Strategy 2: Use Fewer, Better Chunks

```python
# Instead of 10 mediocre chunks
standard_results = retriever.retrieve(query, k=10)

# Use 3-5 BEST chunks with reranking
reranked_results = retriever_with_reranking.retrieve(query, k=5, num_candidates=20)

# Quality > Quantity for LLMs
```

#### Strategy 3: Contextual Compression

```python
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import ChatOpenAI

# Extract only relevant parts from retrieved documents
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

compressor = LLMChainExtractor.from_llm(llm)

# Compress retrieved documents
compressed_docs = compressor.compress_documents(
    documents=retrieved_docs,
    query=query
)

# Result: Only relevant excerpts, not full chunks
for doc in compressed_docs:
    print(doc.page_content)  # Shorter, more focused
```

---

## 📊 Benchmarking Retrieval Strategies

```python
class RetrievalBenchmark:
    """
    Compare different retrieval strategies
    """
    
    def __init__(self, test_queries: List[str], ground_truth: List[List[str]]):
        """
        Args:
            test_queries: List of test questions
            ground_truth: For each query, list of document IDs that should be retrieved
        """
        self.test_queries = test_queries
        self.ground_truth = ground_truth
    
    def evaluate_retriever(
        self,
        retriever,
        k: int = 5,
        name: str = "Retriever"
    ) -> dict:
        """
        Evaluate retriever performance
        """
        total_precision = 0
        total_recall = 0
        total_mrr = 0
        
        for query, relevant_docs in zip(self.test_queries, self.ground_truth):
            # Retrieve
            results = retriever.retrieve(query, k=k)
            retrieved_ids = [doc.metadata.get("id", "") for doc in results]
            
            # Calculate metrics
            precision = self._precision(retrieved_ids, relevant_docs)
            recall = self._recall(retrieved_ids, relevant_docs)
            mrr = self._mrr(retrieved_ids, relevant_docs)
            
            total_precision += precision
            total_recall += recall
            total_mrr += mrr
        
        num_queries = len(self.test_queries)
        return {
            "name": name,
            "precision@k": total_precision / num_queries,
            "recall@k": total_recall / num_queries,
            "mrr": total_mrr / num_queries,
            "f1": self._f1(total_precision / num_queries, total_recall / num_queries)
        }
    
    def _precision(self, retrieved: List[str], relevant: List[str]) -> float:
        """Precision: % of retrieved docs that are relevant"""
        if not retrieved:
            return 0.0
        hits = len(set(retrieved) & set(relevant))
        return hits / len(retrieved)
    
    def _recall(self, retrieved: List[str], relevant: List[str]) -> float:
        """Recall: % of relevant docs that were retrieved"""
        if not relevant:
            return 0.0
        hits = len(set(retrieved) & set(relevant))
        return hits / len(relevant)
    
    def _mrr(self, retrieved: List[str], relevant: List[str]) -> float:
        """Mean Reciprocal Rank: 1 / rank of first relevant doc"""
        for i, doc_id in enumerate(retrieved, 1):
            if doc_id in relevant:
                return 1.0 / i
        return 0.0
    
    def _f1(self, precision: float, recall: float) -> float:
        """F1 score: harmonic mean of precision and recall"""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    def compare_retrievers(self, retrievers: List[Tuple[str, any]]):
        """
        Compare multiple retrievers
        """
        results = []
        
        for name, retriever in retrievers:
            metrics = self.evaluate_retriever(retriever, k=5, name=name)
            results.append(metrics)
        
        # Print comparison
        print("\n" + "="*70)
        print("RETRIEVAL STRATEGY COMPARISON")
        print("="*70)
        print(f"{'Strategy':<30} {'Precision@5':<15} {'Recall@5':<15} {'MRR':<10}")
        print("-"*70)
        
        for r in results:
            print(f"{r['name']:<30} {r['precision@k']:<15.3f} {r['recall@k']:<15.3f} {r['mrr']:<10.3f}")
        
        print("="*70)
        
        return results


# Usage
benchmark = RetrievalBenchmark(
    test_queries=[
        "What was Q3 2024 revenue?",
        "Who is the CEO?",
        "What is our pricing strategy?",
        # ... more test queries
    ],
    ground_truth=[
        ["doc_15", "doc_32"],  # Relevant docs for query 1
        ["doc_8"],              # Relevant docs for query 2
        ["doc_45", "doc_67", "doc_89"],  # Relevant docs for query 3
        # ...
    ]
)

# Compare strategies
results = benchmark.compare_retrievers([
    ("Vector Only", vector_retriever),
    ("Hybrid (BM25 + Vector)", hybrid_retriever),
    ("Hybrid + Cohere Rerank", hybrid_with_cohere),
    ("Hybrid + BGE Rerank", hybrid_with_bge),
])
```

**Expected Results:**
```
======================================================================
RETRIEVAL STRATEGY COMPARISON
======================================================================
Strategy                       Precision@5     Recall@5        MRR       
----------------------------------------------------------------------
Vector Only                    0.620           0.580           0.710
Hybrid (BM25 + Vector)         0.740           0.720           0.820
Hybrid + Cohere Rerank         0.880           0.850           0.940
Hybrid + BGE Rerank            0.860           0.830           0.920
======================================================================
```

---

## 💡 Pro Tips from a Senior AI Engineer

### Tip #1: Adjust BM25/Vector Weights by Query Type

```python
def adaptive_weights(query: str) -> Tuple[float, float]:
    """
    Adjust BM25 vs Vector weights based on query characteristics
    """
    # Keyword-heavy query → Higher BM25 weight
    if re.search(r'\d{4}|Q[1-4]|\$\d+|[A-Z]{2,}', query):
        return (0.6, 0.4)  # BM25: 60%, Vector: 40%
    
    # Semantic query → Higher Vector weight
    if any(word in query.lower() for word in ["how", "why", "explain", "describe"]):
        return (0.3, 0.7)  # BM25: 30%, Vector: 70%
    
    # Default: Balanced
    return (0.4, 0.6)

# Usage
bm25_weight, vector_weight = adaptive_weights(query)
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[bm25_weight, vector_weight]
)
```

### Tip #2: Cache Reranking Results

```python
from functools import lru_cache
import hashlib

class CachedReranker:
    """
    Cache reranking results to save API costs
    """
    
    def __init__(self, reranker):
        self.reranker = reranker
        self.cache = {}
    
    def rerank(self, query: str, documents: List[Document], top_k: int = 5):
        # Create cache key
        doc_ids = [doc.metadata.get("id", hash(doc.page_content)) for doc in documents]
        cache_key = f"{query}_{','.join(map(str, doc_ids))}_{top_k}"
        cache_hash = hashlib.md5(cache_key.encode()).hexdigest()
        
        # Check cache
        if cache_hash in self.cache:
            print("Cache hit!")
            return self.cache[cache_hash]
        
        # Rerank
        results = self.reranker.rerank(query, documents, top_k)
        
        # Store in cache
        self.cache[cache_hash] = results
        
        return results
```

### Tip #3: Monitor Retrieval Quality in Production

```python
import time
from datetime import datetime

class RetrievalMonitor:
    """
    Monitor retrieval performance in production
    """
    
    def __init__(self):
        self.metrics = []
    
    def log_retrieval(
        self,
        query: str,
        num_results: int,
        latency: float,
        user_clicked: List[int] = None
    ):
        """
        Log retrieval metrics
        
        Args:
            user_clicked: Indices of results user clicked (for CTR calculation)
        """
        self.metrics.append({
            "timestamp": datetime.now(),
            "query": query,
            "num_results": num_results,
            "latency_ms": latency * 1000,
            "user_clicked": user_clicked or []
        })
    
    def get_stats(self) -> dict:
        """Get retrieval statistics"""
        if not self.metrics:
            return {}
        
        latencies = [m["latency_ms"] for m in self.metrics]
        clicks = [len(m["user_clicked"]) > 0 for m in self.metrics]
        
        return {
            "total_queries": len(self.metrics),
            "avg_latency_ms": sum(latencies) / len(latencies),
            "p95_latency_ms": sorted(latencies)[int(len(latencies) * 0.95)],
            "ctr": sum(clicks) / len(clicks),  # Click-through rate
        }

# Usage
monitor = RetrievalMonitor()

start = time.time()
results = retriever.retrieve(query, k=5)
latency = time.time() - start

monitor.log_retrieval(
    query=query,
    num_results=len(results),
    latency=latency,
    user_clicked=[0, 2]  # User clicked results #0 and #2
)

print(monitor.get_stats())
```

---

## ✅ Exercises

### Exercise 1: Implement Hybrid Search
1. Convert your current vector-only retriever to hybrid
2. Test with 10 queries, measure precision improvement
3. Experiment with different BM25/Vector weight ratios

### Exercise 2: Add Reranking
1. Implement BGE reranker (free)
2. Compare top 5 results before/after reranking
3. Measure latency increase vs. quality gain

### Exercise 3: Benchmark Strategies
1. Create a test set of 20 queries with ground truth
2. Compare: Vector Only, Hybrid, Hybrid + Rerank
3. Calculate precision@5, recall@5, MRR for each

---

## 🎯 Next Steps

Continue to [Part 3: Agentic RAG Loops →](RAG_03_AGENTIC_LOOPS.md)

You'll learn:
- ReAct pattern for self-correcting retrieval
- Self-RAG (agent decides when to retrieve)
- Corrective RAG (evaluate retrieval quality)
- Multi-step reasoning with adaptive retrieval

---

*Part of the Advanced RAG Mastery series for Smart Document Chat*  
*Last Updated: January 11, 2026*
