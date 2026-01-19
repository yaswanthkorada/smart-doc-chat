# 📄 Part 3: Agentic RAG Loops (ReAct Pattern)

**Level:** Advanced  
**Time:** 10-12 hours  
**Prerequisites:** Parts 1-2 (Chunking + Advanced Retrieval)

---

## 🎯 Learning Objectives

By the end of this module, you'll be able to:
- [ ] Understand the limitations of static RAG (single retrieval)
- [ ] Implement the **ReAct Pattern** (Reason → Act → Observe loop)
- [ ] Build **Self-RAG** (agent decides when retrieval is needed)
- [ ] Create **Corrective RAG (CRAG)** (evaluate and improve retrieval)
- [ ] Implement **Adaptive RAG** (switch strategies based on query)
- [ ] Handle multi-step reasoning with intermediate retrievals
- [ ] Prevent infinite loops and manage costs

---

## ❌ The Problem: Static RAG Fails for Complex Queries

### Scenario: User Asks Complex Question

**Query:** *"Compare Q3 2024 revenue with Q3 2023, and explain the key drivers of growth."*

#### Current Static RAG
```python
# Single retrieval
docs = retriever.retrieve(query, k=5)

# Generate answer
context = '\n\n'.join([doc.page_content for doc in docs])
answer = llm.invoke(f"Context: {context}\n\nQuestion: {query}")
```

**What Happens:**
```
Retrieved Docs (k=5):
1. "Q3 2024 revenue was $5.2M..." ✅
2. "Revenue growth drivers include..." ✅
3. "Q2 2024 financial performance..." ❌ (Wrong quarter)
4. "Company overview and history..." ❌ (Irrelevant)
5. "Q4 2024 forecast..." ❌ (Wrong quarter)

→ Missing: Q3 2023 data! ❌
→ Agent can't compare without both years' data
→ Answer will be incomplete or hallucinated
```

**Problems with Static RAG:**
1. ⚠️ **No self-awareness**: Agent doesn't know it lacks Q3 2023 data
2. ⚠️ **Can't ask follow-ups**: One retrieval, that's it
3. ⚠️ **No verification**: Can't check if retrieved docs are sufficient
4. ⚠️ **No correction**: If first retrieval fails, game over

---

## ✅ Solution: Agentic RAG with ReAct Pattern

**Concept:** Agent reasons about what it needs, retrieves iteratively, and verifies.

### ReAct Pattern Explained

**ReAct = Reason + Act + Observe**

```
User Query: "Compare Q3 2024 vs Q3 2023 revenue"

Step 1: REASON
─────────────────────────────────────
Agent thinks: "I need two pieces of info:
1. Q3 2024 revenue
2. Q3 2023 revenue
Let me search for Q3 2024 first."

Step 2: ACT
─────────────────────────────────────
Tool: search_documents("Q3 2024 revenue")

Step 3: OBSERVE
─────────────────────────────────────
Retrieved: "Q3 2024 revenue was $5.2M"
Agent thinks: "Good! I have 2024. Now I need 2023."

Step 4: REASON
─────────────────────────────────────
Agent thinks: "I still need Q3 2023 data.
Let me search for that."

Step 5: ACT
─────────────────────────────────────
Tool: search_documents("Q3 2023 revenue")

Step 6: OBSERVE
─────────────────────────────────────
Retrieved: "Q3 2023 revenue was $4.1M"
Agent thinks: "Perfect! I have both. Now I can compare."

Step 7: FINAL ANSWER
─────────────────────────────────────
"Q3 2024 revenue ($5.2M) increased 27% compared to 
Q3 2023 ($4.1M), representing $1.1M growth."
```

**Result:** Self-correcting, multi-step retrieval! 🎉

---

## 💻 Implementation 1: Basic ReAct Agent

### Step 1: Define Retrieval Tool

```python
from langchain.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Your existing retriever
from utils.advanced_retrieval import HybridRetrieverWithReranking

retriever = HybridRetrieverWithReranking(user_id="user_123")

def search_documents_tool(query: str) -> str:
    """
    Search document database for relevant information
    """
    results = retriever.retrieve(query, k=3)
    
    # Format results
    context = "\n\n".join([
        f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
        for doc in results
    ])
    
    return context if context else "No relevant documents found."


# Create LangChain tool
search_tool = Tool(
    name="search_documents",
    func=search_documents_tool,
    description="""
    Search the document database for relevant information.
    Use this when you need to find specific information from documents.
    Input should be a specific search query.
    Returns relevant document excerpts.
    """
)
```

### Step 2: Create ReAct Agent

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain import hub

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Get ReAct prompt from LangChain hub
react_prompt = hub.pull("hwchase17/react")

# Create ReAct agent
agent = create_react_agent(
    llm=llm,
    tools=[search_tool],
    prompt=react_prompt
)

# Create agent executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=[search_tool],
    verbose=True,
    max_iterations=5,  # Prevent infinite loops
    handle_parsing_errors=True
)

# Run agent
query = "Compare Q3 2024 revenue with Q3 2023"
response = agent_executor.invoke({"input": query})

print(response["output"])
```

**Output (with verbose=True):**
```
> Entering new AgentExecutor chain...

Thought: I need to find Q3 2024 revenue first.

Action: search_documents
Action Input: "Q3 2024 revenue"

Observation: [Source: financial_report_2024.pdf]
Q3 2024 revenue was $5.2M, representing 15% growth from Q2...

Thought: Good, I have Q3 2024. Now I need Q3 2023.

Action: search_documents
Action Input: "Q3 2023 revenue"

Observation: [Source: financial_report_2023.pdf]
Q3 2023 revenue was $4.1M...

Thought: I now have both Q3 2024 and Q3 2023 revenue figures. I can compare them.

Final Answer: Q3 2024 revenue was $5.2M compared to Q3 2023 revenue of $4.1M, 
representing a 27% increase ($1.1M growth) year-over-year.

> Finished chain.
```

### Step 3: Custom ReAct Prompt for RAG

```python
from langchain.prompts import PromptTemplate

# Custom ReAct prompt optimized for RAG
react_rag_prompt = PromptTemplate(
    input_variables=["tools", "tool_names", "input", "agent_scratchpad"],
    template="""
You are a document analysis assistant with access to a document database.

Your task is to answer questions using ONLY information from the documents.
Use the following process:

1. THINK: What information do I need to answer this question?
2. SEARCH: Use the search_documents tool to find relevant information
3. EVALUATE: Do I have enough information? If not, search again with a different query.
4. ANSWER: Once you have sufficient information, provide a complete answer with citations.

IMPORTANT RULES:
- NEVER make up information. If you can't find it, say so.
- Always cite your sources using [Source: filename]
- If the first search doesn't find what you need, try different search queries
- You can search multiple times with different queries
- Stop searching once you have enough information to answer completely

Available Tools:
{tools}

Tool Names: {tool_names}

Question: {input}

Thought: {agent_scratchpad}
""",
)

# Create agent with custom prompt
agent = create_react_agent(
    llm=llm,
    tools=[search_tool],
    prompt=react_rag_prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=[search_tool],
    verbose=True,
    max_iterations=5
)
```

---

## 🎯 Implementation 2: Self-RAG (Retrieval on Demand)

**Concept:** Agent decides whether retrieval is needed at all.

### The Problem

```python
# Some queries don't need retrieval!

Query 1: "What is 25% of 200?"
→ No retrieval needed (simple math) ❌ Static RAG wastes API call

Query 2: "What was Q3 revenue?"
→ Retrieval needed ✅

Query 3: "Hello, how are you?"
→ No retrieval needed (greeting) ❌ Static RAG wastes API call
```

### Solution: Self-Assessment

```python
from typing import Literal
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

class SelfRAGAgent:
    """
    Agent that decides whether retrieval is needed
    """
    
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm
    
    def query(self, question: str) -> dict:
        """
        Process query with self-assessment
        """
        # Step 1: Assess if retrieval is needed
        needs_retrieval = self._assess_retrieval_need(question)
        
        if not needs_retrieval:
            # Answer directly without retrieval
            answer = self._answer_without_retrieval(question)
            return {
                "answer": answer,
                "retrieved_docs": [],
                "num_retrievals": 0
            }
        
        # Step 2: Perform retrieval
        docs = self.retriever.retrieve(question, k=5)
        
        # Step 3: Evaluate if retrieved docs are sufficient
        is_sufficient = self._evaluate_sufficiency(question, docs)
        
        if not is_sufficient:
            # Reformulate query and retrieve again
            reformulated_query = self._reformulate_query(question, docs)
            additional_docs = self.retriever.retrieve(reformulated_query, k=5)
            docs.extend(additional_docs)
        
        # Step 4: Generate answer
        answer = self._generate_answer(question, docs)
        
        return {
            "answer": answer,
            "retrieved_docs": docs,
            "num_retrievals": 2 if not is_sufficient else 1
        }
    
    def _assess_retrieval_need(self, question: str) -> bool:
        """
        Decide if retrieval is needed
        """
        assessment_prompt = f"""
        Determine if the following question requires searching documents or can be answered directly.
        
        Question: {question}
        
        Consider:
        - Math/calculation questions → NO retrieval
        - General knowledge → NO retrieval
        - Greetings/chitchat → NO retrieval
        - Specific document information → YES retrieval
        - Company/domain-specific data → YES retrieval
        
        Answer with ONLY "YES" or "NO".
        """
        
        response = self.llm.invoke(assessment_prompt).content.strip().upper()
        return "YES" in response
    
    def _evaluate_sufficiency(self, question: str, docs: list) -> bool:
        """
        Evaluate if retrieved documents are sufficient to answer
        """
        context = '\n\n'.join([doc.page_content for doc in docs])
        
        eval_prompt = f"""
        Question: {question}
        
        Retrieved Context:
        {context}
        
        Can you answer the question COMPLETELY using ONLY the information in the context?
        - If the context contains all necessary information → Answer "YES"
        - If key information is missing → Answer "NO"
        
        Answer with ONLY "YES" or "NO".
        """
        
        response = self.llm.invoke(eval_prompt).content.strip().upper()
        return "YES" in response
    
    def _reformulate_query(self, original_question: str, existing_docs: list) -> str:
        """
        Reformulate query to find missing information
        """
        context = '\n\n'.join([doc.page_content[:200] for doc in existing_docs])
        
        reformulate_prompt = f"""
        Original Question: {original_question}
        
        Already Retrieved:
        {context}
        
        What specific information is still missing to answer the question completely?
        Generate a NEW search query to find the missing information.
        
        Return ONLY the new search query, nothing else.
        """
        
        new_query = self.llm.invoke(reformulate_prompt).content.strip()
        return new_query
    
    def _answer_without_retrieval(self, question: str) -> str:
        """
        Answer questions that don't need retrieval
        """
        return self.llm.invoke(question).content
    
    def _generate_answer(self, question: str, docs: list) -> str:
        """
        Generate answer from retrieved documents
        """
        context = '\n\n'.join([
            f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
            for doc in docs
        ])
        
        answer_prompt = f"""
        Use the following context to answer the question.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer the question using ONLY information from the context.
        Cite sources using [Source: filename].
        If you cannot find the answer in the context, say so clearly.
        """
        
        return self.llm.invoke(answer_prompt).content


# Usage
self_rag_agent = SelfRAGAgent(
    retriever=retriever,
    llm=ChatOpenAI(model="gpt-4o", temperature=0)
)

# Query that needs retrieval
result1 = self_rag_agent.query("What was Q3 2024 revenue?")
print(f"Retrievals: {result1['num_retrievals']}")  # 1 or 2
print(result1['answer'])

# Query that doesn't need retrieval
result2 = self_rag_agent.query("What is 25% of 200?")
print(f"Retrievals: {result2['num_retrievals']}")  # 0 (saved API cost!)
print(result2['answer'])
```

---

## 🔧 Implementation 3: Corrective RAG (CRAG)

**Concept:** Evaluate retrieval quality and take corrective action.

### CRAG Pipeline

```
Query → Retrieve → Evaluate Quality → 
  ├─ HIGH QUALITY → Use docs
  ├─ MEDIUM QUALITY → Filter + Retrieve more
  └─ LOW QUALITY → Web search or fallback
```

### Implementation

```python
from typing import List, Literal
from langchain.schema import Document

class CorrectiveRAGAgent:
    """
    CRAG: Evaluate and correct retrieval quality
    """
    
    def __init__(self, retriever, llm, relevance_threshold: float = 0.7):
        self.retriever = retriever
        self.llm = llm
        self.relevance_threshold = relevance_threshold
    
    def query(self, question: str) -> dict:
        """
        Process query with corrective RAG
        """
        # Step 1: Initial retrieval
        docs = self.retriever.retrieve(query=question, k=10)
        
        # Step 2: Evaluate each document's relevance
        evaluated_docs = self._evaluate_documents(question, docs)
        
        # Step 3: Filter by relevance
        relevant_docs = [
            doc for doc, score in evaluated_docs
            if score >= self.relevance_threshold
        ]
        
        # Step 4: Determine quality
        quality = self._determine_quality(evaluated_docs)
        
        # Step 5: Take corrective action based on quality
        if quality == "high":
            # Use top documents
            final_docs = relevant_docs[:5]
            correction = None
        
        elif quality == "medium":
            # Keep relevant docs + retrieve more with reformulated query
            reformulated_query = self._reformulate_query(question, relevant_docs)
            additional_docs = self.retriever.retrieve(reformulated_query, k=5)
            final_docs = relevant_docs + additional_docs
            correction = "reformulated_query"
        
        else:  # low quality
            # Fallback: web search or knowledge base
            final_docs = self._fallback_retrieval(question)
            correction = "fallback"
        
        # Step 6: Generate answer
        answer = self._generate_answer(question, final_docs)
        
        return {
            "answer": answer,
            "num_docs_retrieved": len(docs),
            "num_docs_relevant": len(relevant_docs),
            "quality": quality,
            "correction_applied": correction
        }
    
    def _evaluate_documents(
        self,
        question: str,
        docs: List[Document]
    ) -> List[tuple[Document, float]]:
        """
        Evaluate relevance of each document
        """
        evaluated = []
        
        for doc in docs:
            score = self._calculate_relevance(question, doc)
            evaluated.append((doc, score))
        
        # Sort by score
        evaluated.sort(key=lambda x: x[1], reverse=True)
        
        return evaluated
    
    def _calculate_relevance(self, question: str, doc: Document) -> float:
        """
        Calculate relevance score (0-1) using LLM
        """
        eval_prompt = f"""
        Question: {question}
        
        Document:
        {doc.page_content[:500]}
        
        Rate the relevance of this document to the question on a scale of 0.0 to 1.0:
        - 1.0 = Perfectly relevant, directly answers the question
        - 0.7-0.9 = Highly relevant, contains useful information
        - 0.4-0.6 = Somewhat relevant, tangentially related
        - 0.0-0.3 = Not relevant
        
        Return ONLY a number between 0.0 and 1.0, nothing else.
        """
        
        try:
            score_str = self.llm.invoke(eval_prompt).content.strip()
            score = float(score_str)
            return max(0.0, min(1.0, score))  # Clamp to [0, 1]
        except:
            return 0.5  # Default if parsing fails
    
    def _determine_quality(self, evaluated_docs: List[tuple]) -> Literal["high", "medium", "low"]:
        """
        Determine overall retrieval quality
        """
        if not evaluated_docs:
            return "low"
        
        scores = [score for _, score in evaluated_docs]
        avg_score = sum(scores) / len(scores)
        num_high_quality = sum(1 for score in scores if score >= 0.7)
        
        if avg_score >= 0.7 and num_high_quality >= 3:
            return "high"
        elif avg_score >= 0.5 or num_high_quality >= 2:
            return "medium"
        else:
            return "low"
    
    def _reformulate_query(self, question: str, existing_docs: List[Document]) -> str:
        """
        Reformulate query to find better results
        """
        context = '\n'.join([doc.page_content[:200] for doc in existing_docs[:3]])
        
        prompt = f"""
        Original Question: {question}
        
        Current Retrieved Documents (partial):
        {context}
        
        These documents are somewhat relevant but not sufficient.
        Generate a BETTER search query that might find more relevant documents.
        
        Return ONLY the new query, nothing else.
        """
        
        return self.llm.invoke(prompt).content.strip()
    
    def _fallback_retrieval(self, question: str) -> List[Document]:
        """
        Fallback when document retrieval fails
        
        Options:
        1. Web search (Tavily, SerperDev)
        2. General knowledge from LLM
        3. Return empty and explain
        """
        # For this example, return empty
        # In production, you'd integrate web search here
        return []
    
    def _generate_answer(self, question: str, docs: List[Document]) -> str:
        """
        Generate answer from documents
        """
        if not docs:
            return "I couldn't find relevant information in the documents to answer this question."
        
        context = '\n\n'.join([
            f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
            for doc in docs
        ])
        
        prompt = f"""
        Context:
        {context}
        
        Question: {question}
        
        Answer using ONLY the context. Cite sources.
        """
        
        return self.llm.invoke(prompt).content


# Usage
crag_agent = CorrectiveRAGAgent(
    retriever=retriever,
    llm=ChatOpenAI(model="gpt-4o", temperature=0),
    relevance_threshold=0.7
)

result = crag_agent.query("Compare Q3 2024 vs Q3 2023 revenue")

print(f"Quality: {result['quality']}")
print(f"Retrieved: {result['num_docs_retrieved']}")
print(f"Relevant: {result['num_docs_relevant']}")
print(f"Correction: {result['correction_applied']}")
print(f"\nAnswer:\n{result['answer']}")
```

---

## 🧠 Implementation 4: Adaptive RAG

**Concept:** Choose retrieval strategy based on query complexity.

### Query Classification

```python
from enum import Enum
from typing import Literal

class QueryComplexity(str, Enum):
    SIMPLE = "simple"          # Single-fact retrieval
    MODERATE = "moderate"      # Multiple facts, same document
    COMPLEX = "complex"        # Multi-document, comparison, reasoning
    CONVERSATIONAL = "conversational"  # No retrieval needed

class AdaptiveRAGAgent:
    """
    Adaptive RAG: Choose strategy based on query type
    """
    
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm
        
        # Different agent strategies
        self.simple_rag = self._simple_rag_strategy
        self.moderate_rag = self._moderate_rag_strategy
        self.complex_rag = self._complex_rag_strategy
        self.no_rag = self._no_rag_strategy
    
    def query(self, question: str) -> dict:
        """
        Process query with adaptive strategy
        """
        # Step 1: Classify query complexity
        complexity = self._classify_query(question)
        
        # Step 2: Route to appropriate strategy
        if complexity == QueryComplexity.SIMPLE:
            result = self.simple_rag(question)
        elif complexity == QueryComplexity.MODERATE:
            result = self.moderate_rag(question)
        elif complexity == QueryComplexity.COMPLEX:
            result = self.complex_rag(question)
        else:  # CONVERSATIONAL
            result = self.no_rag(question)
        
        result["complexity"] = complexity
        return result
    
    def _classify_query(self, question: str) -> QueryComplexity:
        """
        Classify query complexity
        """
        classification_prompt = f"""
        Classify the complexity of this question:
        
        Question: {question}
        
        Classification criteria:
        - SIMPLE: Single fact/number (e.g., "What was Q3 revenue?")
        - MODERATE: Multiple related facts (e.g., "What were Q3 revenue and expenses?")
        - COMPLEX: Comparison, analysis, multi-step (e.g., "Compare Q3 2024 vs 2023 and explain why")
        - CONVERSATIONAL: Greeting, chitchat, no document needed
        
        Return ONLY one word: SIMPLE, MODERATE, COMPLEX, or CONVERSATIONAL
        """
        
        response = self.llm.invoke(classification_prompt).content.strip().upper()
        
        if "SIMPLE" in response:
            return QueryComplexity.SIMPLE
        elif "MODERATE" in response:
            return QueryComplexity.MODERATE
        elif "COMPLEX" in response:
            return QueryComplexity.COMPLEX
        else:
            return QueryComplexity.CONVERSATIONAL
    
    def _simple_rag_strategy(self, question: str) -> dict:
        """
        Simple RAG: Single retrieval, top result
        """
        docs = self.retriever.retrieve(question, k=3)
        answer = self._generate_answer(question, docs)
        
        return {
            "answer": answer,
            "strategy": "simple_rag",
            "num_retrievals": 1,
            "docs_used": len(docs)
        }
    
    def _moderate_rag_strategy(self, question: str) -> dict:
        """
        Moderate RAG: Single retrieval, more docs
        """
        docs = self.retriever.retrieve(question, k=7)
        answer = self._generate_answer(question, docs)
        
        return {
            "answer": answer,
            "strategy": "moderate_rag",
            "num_retrievals": 1,
            "docs_used": len(docs)
        }
    
    def _complex_rag_strategy(self, question: str) -> dict:
        """
        Complex RAG: Multi-step retrieval with ReAct
        """
        # Use ReAct agent for complex queries
        react_agent = create_react_agent(...)  # From earlier implementation
        response = react_agent.invoke({"input": question})
        
        return {
            "answer": response["output"],
            "strategy": "complex_rag_react",
            "num_retrievals": "multiple",
            "docs_used": "multiple"
        }
    
    def _no_rag_strategy(self, question: str) -> dict:
        """
        No RAG: Direct LLM response
        """
        answer = self.llm.invoke(question).content
        
        return {
            "answer": answer,
            "strategy": "no_rag",
            "num_retrievals": 0,
            "docs_used": 0
        }
    
    def _generate_answer(self, question: str, docs: list) -> str:
        """Generate answer from docs"""
        context = '\n\n'.join([doc.page_content for doc in docs])
        prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        return self.llm.invoke(prompt).content


# Usage
adaptive_agent = AdaptiveRAGAgent(
    retriever=retriever,
    llm=ChatOpenAI(model="gpt-4o", temperature=0)
)

# Different query types
queries = [
    "What was Q3 revenue?",  # SIMPLE
    "What were Q3 revenue and expenses?",  # MODERATE
    "Compare Q3 2024 vs 2023 and explain key growth drivers",  # COMPLEX
    "Hello, how are you?",  # CONVERSATIONAL
]

for query in queries:
    result = adaptive_agent.query(query)
    print(f"\nQuery: {query}")
    print(f"Complexity: {result['complexity']}")
    print(f"Strategy: {result['strategy']}")
    print(f"Retrievals: {result['num_retrievals']}")
    print(f"Answer: {result['answer'][:100]}...")
```

---

## 💡 Pro Tips from a Senior AI Engineer

### Tip #1: Always Set max_iterations

```python
# ❌ WRONG: No limit = $$$$ in API costs
agent_executor = AgentExecutor(
    agent=agent,
    tools=[search_tool],
    verbose=True
)

# ✅ CORRECT: Limit iterations
agent_executor = AgentExecutor(
    agent=agent,
    tools=[search_tool],
    verbose=True,
    max_iterations=5,  # Stop after 5 steps
    max_execution_time=30  # Or 30 seconds timeout
)
```

### Tip #2: Add Cost Tracking

```python
import time
from typing import List

class CostTrackingAgent:
    """
    Track API costs during agent execution
    """
    
    def __init__(self, agent_executor):
        self.agent_executor = agent_executor
        self.total_cost = 0
        self.call_log = []
    
    def query(self, question: str) -> dict:
        """
        Execute query with cost tracking
        """
        start_time = time.time()
        
        # Wrap LLM to track tokens
        from langchain.callbacks import get_openai_callback
        
        with get_openai_callback() as cb:
            response = self.agent_executor.invoke({"input": question})
            
            # Log costs
            cost = cb.total_cost
            self.total_cost += cost
            
            self.call_log.append({
                "query": question,
                "cost": cost,
                "tokens": cb.total_tokens,
                "latency": time.time() - start_time
            })
        
        return {
            "answer": response["output"],
            "cost": cost,
            "total_cost": self.total_cost
        }
    
    def get_stats(self) -> dict:
        """Get cost statistics"""
        if not self.call_log:
            return {}
        
        return {
            "total_queries": len(self.call_log),
            "total_cost": self.total_cost,
            "avg_cost_per_query": self.total_cost / len(self.call_log),
            "total_tokens": sum(log["tokens"] for log in self.call_log),
            "avg_latency": sum(log["latency"] for log in self.call_log) / len(self.call_log)
        }

# Usage
cost_tracker = CostTrackingAgent(agent_executor)

result = cost_tracker.query("Compare Q3 2024 vs 2023")
print(f"Query cost: ${result['cost']:.4f}")

stats = cost_tracker.get_stats()
print(f"Total cost: ${stats['total_cost']:.4f}")
print(f"Avg cost per query: ${stats['avg_cost_per_query']:.4f}")
```

### Tip #3: Cache Intermediate Results

```python
class CachedReActAgent:
    """
    Cache intermediate retrieval results
    """
    
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm
        self.cache = {}  # query -> docs
    
    def search_with_cache(self, query: str) -> List[Document]:
        """
        Search with caching
        """
        # Check cache
        if query in self.cache:
            print(f"Cache hit for: {query}")
            return self.cache[query]
        
        # Retrieve
        docs = self.retriever.retrieve(query, k=5)
        
        # Cache
        self.cache[query] = docs
        
        return docs
```

### Tip #4: Graceful Degradation

```python
def safe_agent_query(agent_executor, question: str, timeout: int = 30):
    """
    Execute agent query with graceful failure handling
    """
    try:
        # Try agent query with timeout
        response = agent_executor.invoke(
            {"input": question},
            config={"max_execution_time": timeout}
        )
        return response["output"]
    
    except TimeoutError:
        # Fallback: Simple RAG without agent
        print("Agent timeout. Falling back to simple RAG...")
        docs = retriever.retrieve(question, k=5)
        context = '\n\n'.join([doc.page_content for doc in docs])
        return llm.invoke(f"Context: {context}\n\nQuestion: {question}").content
    
    except Exception as e:
        # Fallback: Direct LLM
        print(f"Agent error: {e}. Using direct LLM...")
        return llm.invoke(question).content
```

---

## 📊 Integration with CrewAI (Your Project)

Your project already uses CrewAI! Let's integrate agentic RAG:

```python
# utils/agent_rag_engine.py

from crewai import Agent, Task, Crew
from langchain.tools import Tool

class AgenticRAGEngine:
    """
    Integrate ReAct pattern with your existing CrewAI agents
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.retriever = HybridRetrieverWithReranking(user_id=user_id)
        
        # Define tools
        self.search_tool = Tool(
            name="search_documents",
            func=self._search_documents,
            description="Search document database for specific information"
        )
        
        # Create agents
        self.retrieval_agent = Agent(
            role="Document Retrieval Specialist",
            goal="Find the most relevant documents for user queries",
            tools=[self.search_tool],
            backstory="Expert at searching and retrieving relevant information"
        )
        
        self.analysis_agent = Agent(
            role="Document Analyst",
            goal="Analyze retrieved documents and provide accurate answers",
            backstory="Expert at analyzing documents and synthesizing information"
        )
    
    def _search_documents(self, query: str) -> str:
        """Search tool implementation"""
        docs = self.retriever.retrieve(query, k=5)
        return '\n\n'.join([
            f"[{doc.metadata.get('source')}]\n{doc.page_content}"
            for doc in docs
        ])
    
    def query(self, question: str) -> str:
        """
        Process query with multi-agent system
        """
        # Create tasks
        retrieval_task = Task(
            description=f"""
            Find relevant documents to answer: {question}
            
            Use the search_documents tool multiple times with different queries if needed.
            Your goal is to gather all necessary information to fully answer the question.
            """,
            agent=self.retrieval_agent
        )
        
        analysis_task = Task(
            description=f"""
            Using the documents retrieved, answer the question: {question}
            
            Provide a comprehensive answer citing sources.
            If information is missing, clearly state what's missing.
            """,
            agent=self.analysis_agent
        )
        
        # Create crew
        crew = Crew(
            agents=[self.retrieval_agent, self.analysis_agent],
            tasks=[retrieval_task, analysis_task],
            verbose=True
        )
        
        # Execute
        result = crew.kickoff()
        return result


# Usage (drop-in replacement for your existing RAG engine)
rag_engine = AgenticRAGEngine(user_id="user_123")
answer = rag_engine.query("Compare Q3 2024 vs Q3 2023 revenue")
print(answer)
```

---

## ✅ Exercises

### Exercise 1: Build Basic ReAct Agent
1. Implement ReAct agent with search_documents tool
2. Test with multi-step queries
3. Monitor number of retrievals per query

### Exercise 2: Implement Self-RAG
1. Add retrieval need assessment
2. Test with mix of queries (some need retrieval, some don't)
3. Measure cost savings

### Exercise 3: Create CRAG Pipeline
1. Implement document relevance evaluation
2. Add query reformulation
3. Compare answer quality before/after corrections

---

## 🎯 Next Steps

Continue to [Part 4: Query Transformation →](RAG_04_QUERY_TRANSFORMATION.md)

You'll learn:
- Multi-Query Retrieval (generate multiple search variations)
- HyDE (Hypothetical Document Embeddings)
- Query decomposition for complex questions
- RAG-Fusion for better ranking

---

*Part of the Advanced RAG Mastery series for Smart Document Chat*  
*Last Updated: January 11, 2026*
