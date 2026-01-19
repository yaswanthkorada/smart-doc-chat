# 📄 Part 4: Query Transformation Techniques

**Level:** Advanced  
**Time:** 8-10 hours  
**Prerequisites:** Parts 1-3 (Chunking, Retrieval, Agentic RAG)

---

## 🎯 Learning Objectives

By the end of this module, you'll be able to:
- [ ] Understand why single-query retrieval fails for vague questions
- [ ] Implement **Multi-Query Retrieval** (generate multiple search variations)
- [ ] Build **HyDE** (Hypothetical Document Embeddings) for better semantic match
- [ ] Create **Query Decomposition** for complex multi-part questions
- [ ] Use **RAG-Fusion** for reciprocal rank fusion
- [ ] Implement **Step-Back Prompting** for better context
- [ ] Handle ambiguous queries and synonyms

---

## ❌ The Problem: Vague User Queries

### Scenario 1: Ambiguous Query

**User Query:** *"revenue last quarter"*

**Problems:**
1. ⚠️ "last quarter" → Which quarter? Q4 2024? Q3 2024?
2. ⚠️ "revenue" → Total revenue? Revenue by segment? Revenue growth?
3. ⚠️ No semantic context → Vector search struggles

**Naive RAG Retrieval:**
```python
query = "revenue last quarter"
docs = vectorstore.similarity_search(query, k=5)

# Retrieved docs (often poor matches):
1. "Q2 2023 quarterly report..." ❌ (Wrong quarter)
2. "Revenue projections for next year..." ❌ (Future, not past)
3. "Expense breakdown for Q3..." ❌ (Expenses, not revenue)
```

### Scenario 2: Synonym Problem

**User Query:** *"CEO compensation"*

**Documents Use Different Terms:**
- "Executive pay"
- "Leadership remuneration"
- "C-suite salary"
- "Chief Executive Officer total compensation"

**Single-Query Search Misses Variations! ❌**

---

## ✅ Solution 1: Multi-Query Retrieval

**Concept:** Generate multiple query variations, search with each, merge results.

### How It Works

```
User Query: "revenue last quarter"

LLM Generates Multiple Variations:
────────────────────────────────────
1. "What was the revenue in Q4 2024?"
2. "Q4 2024 total revenue figures"
3. "Latest quarter revenue results"
4. "Fourth quarter 2024 financial revenue"

Search with All 4 Queries → Merge Results → Deduplicate
```

**Benefits:**
- ✅ Covers different phrasings
- ✅ Handles ambiguity (Q3 vs Q4)
- ✅ Increases recall (finds more relevant docs)
- ✅ Robust to term variations

### Implementation

#### Step 1: Basic Multi-Query with LangChain

```python
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma

# Initialize components
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
vectorstore = Chroma(...)  # Your vectorstore

# Create multi-query retriever
multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    llm=llm
)

# Single query generates multiple variations internally
query = "revenue last quarter"
docs = multi_query_retriever.get_relevant_documents(query)

# Results: Merged from all query variations
for i, doc in enumerate(docs):
    print(f"{i+1}. {doc.page_content[:100]}...")
```

#### Step 2: Custom Multi-Query with More Control

```python
from typing import List
from langchain.schema import Document
from langchain_openai import ChatOpenAI

class CustomMultiQueryRetriever:
    """
    Custom multi-query retrieval with full control
    """
    
    def __init__(self, retriever, llm, num_queries: int = 4):
        self.retriever = retriever
        self.llm = llm
        self.num_queries = num_queries
    
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """
        Generate multiple query variations and retrieve
        """
        # Step 1: Generate query variations
        query_variations = self._generate_queries(query)
        print(f"Generated {len(query_variations)} query variations:")
        for i, q in enumerate(query_variations, 1):
            print(f"  {i}. {q}")
        
        # Step 2: Retrieve with each query
        all_docs = {}  # doc_id -> Document (deduplication)
        
        for q in query_variations:
            docs = self.retriever.retrieve(q, k=k)
            for doc in docs:
                doc_id = self._get_doc_id(doc)
                if doc_id not in all_docs:
                    all_docs[doc_id] = doc
        
        # Step 3: Return unique documents
        unique_docs = list(all_docs.values())
        print(f"\nRetrieved {len(unique_docs)} unique documents")
        
        return unique_docs[:k]
    
    def _generate_queries(self, original_query: str) -> List[str]:
        """
        Generate query variations using LLM
        """
        prompt = f"""
        You are an AI assistant helping to improve document search.
        
        Original query: "{original_query}"
        
        Generate {self.num_queries} different variations of this query that:
        1. Use different phrasings
        2. Cover potential ambiguities
        3. Include relevant synonyms
        4. Ask the same question from different angles
        
        Requirements:
        - Each variation should be a complete search query
        - Keep queries concise (5-15 words)
        - Maintain the original intent
        - Make queries specific and searchable
        
        Return ONLY the {self.num_queries} queries, one per line, without numbering.
        """
        
        response = self.llm.invoke(prompt).content.strip()
        queries = [q.strip() for q in response.split('\n') if q.strip()]
        
        # Include original query
        all_queries = [original_query] + queries[:self.num_queries - 1]
        
        return all_queries
    
    def _get_doc_id(self, doc: Document) -> str:
        """Get unique ID for document"""
        return doc.metadata.get('id', hash(doc.page_content))


# Usage
multi_query = CustomMultiQueryRetriever(
    retriever=hybrid_retriever,  # From Part 2
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.7),
    num_queries=4
)

results = multi_query.retrieve("revenue last quarter", k=5)
```

**Output Example:**
```
Generated 4 query variations:
  1. revenue last quarter
  2. What was the total revenue in Q4 2024?
  3. Latest quarterly revenue figures
  4. Fourth quarter 2024 financial results

Retrieved 12 unique documents
```

---

## ✅ Solution 2: HyDE (Hypothetical Document Embeddings)

**Concept:** Generate a hypothetical answer, embed it, search with that embedding.

### The Insight

**Problem with Query Embeddings:**
```
Query: "What was Q3 revenue?"
Query Embedding: [0.23, -0.45, 0.12, ...]  (short, question-like)

Document: "Q3 2024 revenue was $5.2M, representing..."
Doc Embedding: [0.31, -0.52, 0.18, ...]  (longer, declarative)

→ Embeddings don't match well semantically! ❌
```

**HyDE Solution:**
```
Query: "What was Q3 revenue?"
↓
LLM Generates Hypothetical Answer: 
"Q3 2024 revenue was $5.2M, representing 15% growth..."
↓
Embed the hypothetical answer (declarative, document-like)
↓
Search with that embedding
→ Much better semantic match! ✅
```

### Implementation

#### Step 1: Basic HyDE

```python
from langchain.chains import HypotheticalDocumentEmbedder
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate

# Initialize components
base_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Create HyDE chain
hyde_embeddings = HypotheticalDocumentEmbedder.from_llm(
    llm=llm,
    base_embeddings=base_embeddings,
    prompt_key="web_search"  # Built-in prompt
)

# Use HyDE embeddings in vectorstore
from langchain_community.vectorstores import Chroma

vectorstore_hyde = Chroma(
    embedding_function=hyde_embeddings,
    persist_directory="./chroma_hyde"
)

# Search (automatically generates hypothetical doc internally)
query = "What was Q3 2024 revenue?"
results = vectorstore_hyde.similarity_search(query, k=5)
```

#### Step 2: Custom HyDE with Detailed Control

```python
from typing import List
from langchain.schema import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

class CustomHyDERetriever:
    """
    Custom HyDE implementation for RAG
    """
    
    def __init__(self, retriever, llm, embeddings):
        self.retriever = retriever
        self.llm = llm
        self.embeddings = embeddings
    
    def retrieve(self, query: str, k: int = 5, num_hypotheses: int = 3) -> List[Document]:
        """
        Retrieve using HyDE
        
        Args:
            query: User query
            k: Number of documents to retrieve
            num_hypotheses: Number of hypothetical documents to generate
        """
        # Step 1: Generate hypothetical documents
        hypothetical_docs = self._generate_hypothetical_docs(query, num_hypotheses)
        
        print("Generated Hypothetical Documents:")
        for i, doc in enumerate(hypothetical_docs, 1):
            print(f"  {i}. {doc[:100]}...")
        
        # Step 2: Embed hypothetical documents
        hyde_embeddings = self.embeddings.embed_documents(hypothetical_docs)
        
        # Step 3: Search with each hypothetical embedding
        all_docs = {}
        
        for i, embedding in enumerate(hyde_embeddings):
            # Search with hypothetical embedding
            docs = self._search_by_embedding(embedding, k=k)
            
            for doc in docs:
                doc_id = self._get_doc_id(doc)
                if doc_id not in all_docs:
                    all_docs[doc_id] = doc
        
        # Step 4: Return unique documents
        unique_docs = list(all_docs.values())
        return unique_docs[:k]
    
    def _generate_hypothetical_docs(self, query: str, num_docs: int) -> List[str]:
        """
        Generate hypothetical document excerpts
        """
        prompt = f"""
        You are generating hypothetical document excerpts that would answer this question:
        
        Question: {query}
        
        Generate {num_docs} different hypothetical excerpts from documents that would 
        contain the answer to this question.
        
        Requirements:
        - Write as if you're quoting from actual documents
        - Be specific and detailed
        - Use declarative language (not questions)
        - Include numbers, dates, specifics if relevant
        - Each excerpt should be 2-3 sentences
        
        Generate {num_docs} hypothetical excerpts, separated by "---"
        """
        
        response = self.llm.invoke(prompt).content.strip()
        hypotheses = [h.strip() for h in response.split('---') if h.strip()]
        
        return hypotheses[:num_docs]
    
    def _search_by_embedding(self, embedding: List[float], k: int) -> List[Document]:
        """
        Search vectorstore using embedding
        """
        # This depends on your vectorstore implementation
        # For Chroma:
        results = self.retriever.collection.query(
            query_embeddings=[embedding],
            n_results=k
        )
        
        docs = []
        if results['documents']:
            for i, doc_text in enumerate(results['documents'][0]):
                docs.append(Document(
                    page_content=doc_text,
                    metadata=results['metadatas'][0][i] if results['metadatas'] else {}
                ))
        
        return docs
    
    def _get_doc_id(self, doc: Document) -> str:
        """Get document ID"""
        return doc.metadata.get('id', hash(doc.page_content))


# Usage
hyde_retriever = CustomHyDERetriever(
    retriever=hybrid_retriever,
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.7),
    embeddings=OpenAIEmbeddings(model="text-embedding-3-small")
)

results = hyde_retriever.retrieve("What was Q3 2024 revenue?", k=5, num_hypotheses=3)
```

**Example Output:**
```
Generated Hypothetical Documents:
  1. Q3 2024 revenue reached $5.2 million, marking a 15% increase from the previous quarter...
  2. The third quarter of 2024 showed total revenue of $5.2M, driven by strong enterprise...
  3. In Q3 2024, the company reported $5.2 million in revenue, with growth primarily from...

Retrieved 5 documents
```

### When to Use HyDE

✅ **Use When:**
- Queries are vague or ambiguous
- Documents are technical/specific
- Semantic gap between query and document language
- Users ask short questions expecting detailed answers

❌ **Don't Use When:**
- Queries contain exact terms/keywords (use BM25 instead)
- Queries are already document-like
- Very specific factual lookups (dates, numbers)
- Computational cost is a concern

---

## ✅ Solution 3: Query Decomposition

**Concept:** Break complex queries into simpler sub-queries.

### Example: Complex Query

**User Query:** *"Compare Q3 2024 revenue vs Q3 2023 and explain the key growth drivers"*

**Decomposition:**
```
Main Query → Sub-Queries:
────────────────────────────────────
1. "What was Q3 2024 revenue?"
2. "What was Q3 2023 revenue?"
3. "What were the key growth drivers in Q3 2024?"

Search Each Sub-Query → Merge Results → Synthesize Answer
```

### Implementation

```python
from typing import List, Dict
from langchain.schema import Document
from langchain_openai import ChatOpenAI

class QueryDecomposer:
    """
    Decompose complex queries into sub-queries
    """
    
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm
    
    def query(self, complex_query: str) -> Dict:
        """
        Process complex query with decomposition
        """
        # Step 1: Decompose query
        sub_queries = self._decompose_query(complex_query)
        
        print(f"Decomposed into {len(sub_queries)} sub-queries:")
        for i, sq in enumerate(sub_queries, 1):
            print(f"  {i}. {sq}")
        
        # Step 2: Retrieve for each sub-query
        all_docs = []
        sub_results = {}
        
        for sub_q in sub_queries:
            docs = self.retriever.retrieve(sub_q, k=3)
            sub_results[sub_q] = docs
            all_docs.extend(docs)
        
        # Step 3: Deduplicate
        unique_docs = self._deduplicate_docs(all_docs)
        
        # Step 4: Synthesize answer from all sub-query results
        answer = self._synthesize_answer(complex_query, sub_results)
        
        return {
            "query": complex_query,
            "sub_queries": sub_queries,
            "documents": unique_docs,
            "answer": answer
        }
    
    def _decompose_query(self, query: str) -> List[str]:
        """
        Decompose complex query into sub-queries
        """
        decompose_prompt = f"""
        Decompose this complex query into simpler sub-queries:
        
        Complex Query: {query}
        
        Break it down into 2-5 simpler questions that:
        1. Can be answered independently
        2. Together provide all info needed for the original question
        3. Are specific and searchable
        
        Return ONLY the sub-queries, one per line, without numbering.
        """
        
        response = self.llm.invoke(decompose_prompt).content.strip()
        sub_queries = [q.strip() for q in response.split('\n') if q.strip()]
        
        return sub_queries
    
    def _deduplicate_docs(self, docs: List[Document]) -> List[Document]:
        """Remove duplicate documents"""
        seen = set()
        unique = []
        
        for doc in docs:
            doc_id = doc.metadata.get('id', hash(doc.page_content))
            if doc_id not in seen:
                seen.add(doc_id)
                unique.append(doc)
        
        return unique
    
    def _synthesize_answer(self, original_query: str, sub_results: Dict) -> str:
        """
        Synthesize final answer from sub-query results
        """
        # Prepare context from all sub-queries
        context_parts = []
        for sub_q, docs in sub_results.items():
            context_parts.append(f"### Sub-question: {sub_q}\n")
            for doc in docs:
                context_parts.append(f"{doc.page_content}\n")
        
        context = '\n'.join(context_parts)
        
        synthesis_prompt = f"""
        Original Question: {original_query}
        
        Context from sub-queries:
        {context}
        
        Synthesize a comprehensive answer to the original question using the context.
        Make sure to:
        1. Address all parts of the original question
        2. Cite sources using [Source: filename]
        3. Be specific with numbers and dates
        4. Explain relationships (e.g., comparisons, causation)
        
        Answer:
        """
        
        answer = self.llm.invoke(synthesis_prompt).content
        return answer


# Usage
decomposer = QueryDecomposer(
    retriever=hybrid_retriever,
    llm=ChatOpenAI(model="gpt-4o", temperature=0)
)

result = decomposer.query(
    "Compare Q3 2024 revenue vs Q3 2023 and explain the key growth drivers"
)

print(f"\nAnswer:\n{result['answer']}")
```

**Output:**
```
Decomposed into 3 sub-queries:
  1. What was Q3 2024 revenue?
  2. What was Q3 2023 revenue?
  3. What were the key growth drivers in Q3 2024?

Answer:
Q3 2024 revenue was $5.2M [Source: financial_report_2024.pdf], compared to 
Q3 2023 revenue of $4.1M [Source: financial_report_2023.pdf], representing 
a 27% year-over-year increase.

The key growth drivers were:
1. Enterprise segment growth of $800K
2. International expansion contributing $200K
3. New pricing strategy boosting ARPU by 12%
[Source: financial_report_2024.pdf]
```

---

## ✅ Solution 4: RAG-Fusion

**Concept:** Combine multiple retrieval strategies with Reciprocal Rank Fusion.

### How RAG-Fusion Works

```
Query: "revenue growth"

Strategy 1: Vector Search
────────────────────────────────────
1. "Q3 revenue increased 15%..." (rank 1)
2. "Revenue growth drivers..." (rank 2)
3. "Annual revenue trends..." (rank 3)

Strategy 2: Multi-Query
────────────────────────────────────
1. "Revenue growth drivers..." (rank 1) ← Also rank 2 in Strategy 1
2. "Q3 revenue increased 15%..." (rank 2) ← Also rank 1 in Strategy 1
3. "YoY revenue comparison..." (rank 3)

Strategy 3: HyDE
────────────────────────────────────
1. "Revenue growth drivers..." (rank 1) ← Appears in multiple strategies!
2. "Market expansion revenue..." (rank 2)
3. "Q3 revenue increased 15%..." (rank 3)

RAG-Fusion (RRF):
────────────────────────────────────
Score = Σ(1 / (60 + rank_i))

Doc: "Revenue growth drivers..."
  Strategy 1: rank 2 → 1/(60+2) = 0.0161
  Strategy 2: rank 1 → 1/(60+1) = 0.0164
  Strategy 3: rank 1 → 1/(60+1) = 0.0164
  Total: 0.0489 → HIGHEST SCORE! ✅

Final Ranking:
1. "Revenue growth drivers..." (appears in all 3, high RRF score)
2. "Q3 revenue increased 15%..." (appears in 2 strategies)
3. "Annual revenue trends..."
```

### Implementation

```python
from typing import List, Dict
from langchain.schema import Document
import numpy as np

class RAGFusion:
    """
    Combine multiple retrieval strategies with RRF
    """
    
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm
        
        # Initialize different retrieval strategies
        self.multi_query = CustomMultiQueryRetriever(retriever, llm)
        self.hyde = CustomHyDERetriever(retriever, llm, embeddings)
    
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve using RAG-Fusion
        """
        # Step 1: Retrieve with multiple strategies
        results_standard = self.retriever.retrieve(query, k=10)
        results_multi_query = self.multi_query.retrieve(query, k=10)
        results_hyde = self.hyde.retrieve(query, k=10, num_hypotheses=2)
        
        # Step 2: Apply Reciprocal Rank Fusion
        fused_results = self._reciprocal_rank_fusion([
            results_standard,
            results_multi_query,
            results_hyde
        ])
        
        # Step 3: Return top k
        return fused_results[:k]
    
    def _reciprocal_rank_fusion(
        self,
        retrieval_results: List[List[Document]],
        k: int = 60
    ) -> List[Document]:
        """
        Combine multiple retrieval results using RRF
        
        RRF score = Σ(1 / (k + rank_i))
        """
        # Map doc_id to Document
        doc_map = {}
        
        # Map doc_id to RRF score
        rrf_scores = {}
        
        # Process each retrieval strategy
        for strategy_results in retrieval_results:
            for rank, doc in enumerate(strategy_results, start=1):
                doc_id = self._get_doc_id(doc)
                
                # Store document
                if doc_id not in doc_map:
                    doc_map[doc_id] = doc
                
                # Calculate RRF contribution
                rrf_contribution = 1 / (k + rank)
                rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + rrf_contribution
        
        # Sort by RRF score
        sorted_doc_ids = sorted(
            rrf_scores.keys(),
            key=lambda x: rrf_scores[x],
            reverse=True
        )
        
        # Return sorted documents
        return [doc_map[doc_id] for doc_id in sorted_doc_ids]
    
    def _get_doc_id(self, doc: Document) -> str:
        """Get document ID"""
        return doc.metadata.get('id', hash(doc.page_content))


# Usage
rag_fusion = RAGFusion(
    retriever=hybrid_retriever,
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
)

results = rag_fusion.retrieve("revenue growth", k=5)

for i, doc in enumerate(results, 1):
    print(f"{i}. {doc.page_content[:100]}...")
```

---

## ✅ Solution 5: Step-Back Prompting

**Concept:** Ask a broader question first to get better context.

### Example

**User Query:** *"What was the Q3 revenue breakdown by segment?"*

**Standard Approach:**
```
Search: "Q3 revenue breakdown by segment"
→ Might miss high-level context
```

**Step-Back Approach:**
```
Step 1: Generate step-back question
  Original: "What was the Q3 revenue breakdown by segment?"
  Step-back: "What is the overall company revenue structure?"

Step 2: Retrieve with both questions
  - Step-back query → Gets high-level context
  - Original query → Gets specific details

Step 3: Combine contexts
  → Better answer with full context!
```

### Implementation

```python
class StepBackRetriever:
    """
    Step-back prompting for better context
    """
    
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm
    
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve with step-back prompting
        """
        # Step 1: Generate step-back question
        step_back_query = self._generate_step_back_question(query)
        
        print(f"Original query: {query}")
        print(f"Step-back query: {step_back_query}")
        
        # Step 2: Retrieve with both queries
        specific_docs = self.retriever.retrieve(query, k=k)
        context_docs = self.retriever.retrieve(step_back_query, k=k)
        
        # Step 3: Combine and deduplicate
        all_docs = specific_docs + context_docs
        unique_docs = self._deduplicate_docs(all_docs)
        
        return unique_docs[:k*2]  # Return more docs for richer context
    
    def _generate_step_back_question(self, query: str) -> str:
        """
        Generate broader, step-back question
        """
        prompt = f"""
        Given this specific question, generate a broader, higher-level question 
        that would provide useful context.
        
        Specific Question: {query}
        
        Generate a step-back question that:
        1. Is more general/abstract
        2. Asks about concepts, not specific details
        3. Would help understand the context
        
        Example:
        Specific: "What was Q3 revenue by segment?"
        Step-back: "How is company revenue structured?"
        
        Return ONLY the step-back question, nothing else.
        """
        
        return self.llm.invoke(prompt).content.strip()
    
    def _deduplicate_docs(self, docs: List[Document]) -> List[Document]:
        """Remove duplicates"""
        seen = set()
        unique = []
        for doc in docs:
            doc_id = doc.metadata.get('id', hash(doc.page_content))
            if doc_id not in seen:
                seen.add(doc_id)
                unique.append(doc)
        return unique


# Usage
step_back_retriever = StepBackRetriever(
    retriever=hybrid_retriever,
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
)

results = step_back_retriever.retrieve(
    "What was the Q3 revenue breakdown by segment?",
    k=5
)
```

---

## 🎯 Complete Query Transformation Pipeline

Combine all techniques:

```python
class AdvancedQueryTransformer:
    """
    Complete query transformation pipeline
    """
    
    def __init__(self, retriever, llm, embeddings):
        self.retriever = retriever
        self.llm = llm
        self.embeddings = embeddings
        
        # Initialize all transformers
        self.multi_query = CustomMultiQueryRetriever(retriever, llm)
        self.hyde = CustomHyDERetriever(retriever, llm, embeddings)
        self.decomposer = QueryDecomposer(retriever, llm)
        self.step_back = StepBackRetriever(retriever, llm)
        self.rag_fusion = RAGFusion(retriever, llm)
    
    def retrieve(
        self,
        query: str,
        strategy: str = "auto",
        k: int = 5
    ) -> Dict:
        """
        Retrieve with automatic or manual strategy selection
        
        Args:
            query: User query
            strategy: "auto", "multi_query", "hyde", "decompose", "step_back", "fusion"
            k: Number of documents to retrieve
        """
        if strategy == "auto":
            strategy = self._select_strategy(query)
        
        print(f"Selected strategy: {strategy}")
        
        # Apply selected strategy
        if strategy == "multi_query":
            docs = self.multi_query.retrieve(query, k=k)
        elif strategy == "hyde":
            docs = self.hyde.retrieve(query, k=k)
        elif strategy == "decompose":
            result = self.decomposer.query(query)
            docs = result["documents"]
        elif strategy == "step_back":
            docs = self.step_back.retrieve(query, k=k)
        elif strategy == "fusion":
            docs = self.rag_fusion.retrieve(query, k=k)
        else:
            docs = self.retriever.retrieve(query, k=k)
        
        return {
            "query": query,
            "strategy": strategy,
            "documents": docs
        }
    
    def _select_strategy(self, query: str) -> str:
        """
        Automatically select best strategy for query
        """
        selection_prompt = f"""
        Select the best retrieval strategy for this query:
        
        Query: {query}
        
        Strategies:
        - multi_query: For ambiguous or vague queries
        - hyde: For queries with semantic gap from documents
        - decompose: For complex multi-part questions
        - step_back: For specific questions needing broader context
        - fusion: For important queries requiring maximum recall
        - standard: For simple, clear queries
        
        Return ONLY the strategy name, nothing else.
        """
        
        return self.llm.invoke(selection_prompt).content.strip().lower()


# Usage
transformer = AdvancedQueryTransformer(
    retriever=hybrid_retriever,
    llm=ChatOpenAI(model="gpt-4o", temperature=0),
    embeddings=OpenAIEmbeddings(model="text-embedding-3-small")
)

# Auto-select strategy
result = transformer.retrieve(
    "Compare Q3 2024 vs 2023 and explain growth drivers",
    strategy="auto",  # Likely selects "decompose"
    k=5
)

print(f"Used strategy: {result['strategy']}")
print(f"Retrieved {len(result['documents'])} documents")
```

---

## 💡 Pro Tips from a Senior AI Engineer

### Tip #1: Cache Query Variations

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_query_generation(query: str, technique: str) -> List[str]:
    """Cache generated queries to save LLM costs"""
    # Generate queries...
    pass
```

### Tip #2: Monitor Strategy Performance

```python
class StrategyMonitor:
    def __init__(self):
        self.stats = {}
    
    def log(self, strategy: str, query: str, user_satisfied: bool):
        if strategy not in self.stats:
            self.stats[strategy] = {"success": 0, "total": 0}
        
        self.stats[strategy]["total"] += 1
        if user_satisfied:
            self.stats[strategy]["success"] += 1
    
    def get_best_strategy(self) -> str:
        best = max(
            self.stats.items(),
            key=lambda x: x[1]["success"] / x[1]["total"]
        )
        return best[0]
```

### Tip #3: Combine Strategies Intelligently

```python
# DON'T: Use all strategies all the time (expensive!)
# DO: Use appropriate strategy based on query

def smart_retrieval(query: str):
    if is_simple_query(query):
        return standard_retrieval(query)
    elif is_ambiguous(query):
        return multi_query_retrieval(query)
    elif is_complex(query):
        return decompose_then_retrieve(query)
    else:
        return rag_fusion(query)  # When quality matters most
```

---

## ✅ Exercises

### Exercise 1: Implement Multi-Query
1. Build CustomMultiQueryRetriever
2. Test with vague queries
3. Measure recall improvement vs single query

### Exercise 2: Build HyDE Pipeline
1. Implement CustomHyDERetriever
2. Compare with standard vector search
3. Measure semantic match improvement

### Exercise 3: Create Query Decomposition
1. Implement QueryDecomposer
2. Test with complex multi-part questions
3. Verify all parts are answered

---

## 🎯 Next Steps

Continue to [Part 5: Evaluation & Guardrails →](RAG_05_EVALUATION_GUARDRAILS.md)

You'll learn:
- RAGAS evaluation framework
- Hallucination detection
- Context filtering
- Production monitoring

---

*Part of the Advanced RAG Mastery series for Smart Document Chat*  
*Last Updated: January 11, 2026*
