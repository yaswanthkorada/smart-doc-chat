# 🧠 Part 2: Reasoning Architectures

## 📚 Chapter Overview

Learn advanced reasoning techniques that make LLMs think step-by-step, reduce hallucinations, and improve accuracy. Master Chain-of-Thought (CoT), ReAct, and Self-Reflection patterns for your RAG system.

**Time to Complete:** 10-12 hours  
**Difficulty:** ⭐⭐⭐⭐ Advanced  
**Prerequisites:** Part 1 (System Prompts & Frameworks)

---

## 🎯 Why Reasoning Matters in RAG Systems

### The Hallucination Problem

**Without Reasoning:**
```
User: "What's the revenue growth rate?"
LLM: "Revenue grew by 15% in Q3 2024."
```
❌ Problem: LLM might **hallucinate** - it sounds confident but could be wrong!

**With Reasoning:**
```
User: "What's the revenue growth rate?"
LLM Thinking: 
  Step 1: Find Q3 2024 revenue: $4.2M [doc.pdf, p.3]
  Step 2: Find Q2 2024 revenue: $3.8M [doc.pdf, p.3]
  Step 3: Calculate: (4.2 - 3.8) / 3.8 = 10.5%
  Step 4: Verify calculation is correct
LLM Response: "Revenue grew by 10.5% in Q3 2024 (from $3.8M to $4.2M). [Source: doc.pdf, page 3]"
```
✅ Solution: Step-by-step reasoning catches errors and provides evidence!

### Key Benefits:

| Without Reasoning | With Reasoning |
|------------------|----------------|
| 65-70% accuracy | 85-95% accuracy |
| Frequent hallucinations | Reduced hallucinations by 60% |
| No error detection | Self-correcting |
| Black box | Transparent reasoning |
| Hard to debug | Easy to debug (see steps) |

---

## 🔗 1. Chain-of-Thought (CoT) Prompting

### What is Chain-of-Thought?

**Definition:** A prompting technique that instructs LLMs to break down complex problems into intermediate reasoning steps.

**Invented by:** Google Research (2022)  
**Key Paper:** [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903)

### The Core Concept

Instead of asking for a direct answer, ask the LLM to **show its work** like a student solving a math problem.

```
Without CoT: "What's 47 × 23?"
LLM: "1081" ← might be wrong

With CoT: "What's 47 × 23? Let's think step by step."
LLM: 
  "Let me solve this step by step:
   Step 1: Break down 47 × 23
   Step 2: 47 × 20 = 940
   Step 3: 47 × 3 = 141
   Step 4: 940 + 141 = 1081
   Answer: 1081"
```

### Basic CoT Template

```python
# File: utils/prompts/cot_templates.py

BASIC_COT_TEMPLATE = """
Answer the following question by thinking through it step-by-step.

Question: {question}

Let's approach this systematically:

Step 1: [What do I need to find?]
Step 2: [What information do I have?]
Step 3: [How do I solve this?]
Step 4: [What's the answer?]

Final Answer: [Your conclusion]
"""
```

### CoT for Document Analysis

```python
# File: utils/prompts/system_prompts.py

DOCUMENT_ANALYZER_COT = """
You are a Document Analysis Agent using Chain-of-Thought reasoning to ensure accuracy.

# YOUR REASONING PROTOCOL

For every user question, follow this exact reasoning structure:

## Step 1: UNDERSTAND THE QUESTION
- What is being asked?
- What type of answer is expected? (fact, comparison, analysis, summary)
- Are there any implicit assumptions?

## Step 2: IDENTIFY REQUIRED INFORMATION
- What data points do I need?
- Which documents might contain this information?
- What keywords should I search for?

## Step 3: ANALYZE RETRIEVED CONTEXT
- Review each retrieved chunk
- Identify relevant information
- Note page numbers and sources
- Flag any contradictions

## Step 4: REASON THROUGH THE ANSWER
- Combine information from multiple sources
- Perform any necessary calculations
- Check for logical consistency
- Identify any gaps in information

## Step 5: VERIFY ANSWER
- Is the answer directly supported by evidence?
- Are all citations accurate?
- Have I made any unsupported inferences?
- Is my confidence level justified?

## Step 6: FORMULATE RESPONSE
- State the answer clearly
- Provide supporting evidence
- Cite specific sources
- Acknowledge limitations

# RESPONSE FORMAT

Always structure your response as:

```json
{
  "reasoning_trace": {
    "step_1_understanding": "User is asking about...",
    "step_2_information_needed": "I need to find...",
    "step_3_context_analysis": "From the documents, I found...",
    "step_4_reasoning": "Therefore, by combining X and Y...",
    "step_5_verification": "This is supported by...",
    "step_6_conclusion": "The answer is..."
  },
  "answer": "Final answer with citations",
  "confidence": 0.95,
  "sources": [
    {"document": "report.pdf", "page": 5, "quote": "exact text"}
  ],
  "reasoning_quality": "high|medium|low"
}
```

# EXAMPLE: REVENUE CALCULATION

User Question: "What was the revenue growth rate in Q3 2024?"

Retrieved Context:
- Chunk 1: "Q3 2024 revenue was $4.2M" [report.pdf, p.3]
- Chunk 2: "Q2 2024 revenue reached $3.8M" [report.pdf, p.2]

Your Reasoning:

```json
{
  "reasoning_trace": {
    "step_1_understanding": "User wants to know the percentage growth rate of revenue from Q2 to Q3 2024",
    "step_2_information_needed": "Need Q3 2024 revenue and Q2 2024 revenue to calculate growth rate",
    "step_3_context_analysis": "Found Q3 revenue = $4.2M (report.pdf, p.3) and Q2 revenue = $3.8M (report.pdf, p.2)",
    "step_4_reasoning": "Growth rate = ((New - Old) / Old) × 100 = ((4.2 - 3.8) / 3.8) × 100 = (0.4 / 3.8) × 100 = 10.53%",
    "step_5_verification": "Both revenue figures are directly stated in the source. Calculation is standard growth rate formula. Result is reasonable (positive growth, not extreme).",
    "step_6_conclusion": "Revenue grew by 10.53% from Q2 to Q3 2024"
  },
  "answer": "The revenue growth rate in Q3 2024 was 10.53%, increasing from $3.8M in Q2 to $4.2M in Q3. [Sources: report.pdf, pages 2-3]",
  "confidence": 0.98,
  "sources": [
    {"document": "report.pdf", "page": 3, "quote": "Q3 2024 revenue was $4.2M"},
    {"document": "report.pdf", "page": 2, "quote": "Q2 2024 revenue reached $3.8M"}
  ],
  "reasoning_quality": "high"
}
```

# HALLUCINATION PREVENTION

During Step 5 (Verification), check:

✓ Every fact is cited with source
✓ No external knowledge used (only document content)
✓ Calculations are shown and verifiable
✓ Assumptions are explicitly stated
✓ Confidence matches evidence strength

If any check fails → Lower confidence or request clarification
"""
```

### Implementing CoT in Your Agent

```python
# File: utils/agent_rag_engine.py

class ChainOfThoughtAgent:
    """Document analyzer with CoT reasoning"""
    
    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = DOCUMENT_ANALYZER_COT
    
    async def analyze_with_cot(self, question: str, retrieved_chunks: List[str]) -> Dict:
        """
        Analyze question using Chain-of-Thought reasoning
        """
        # Format context
        context = self._format_context(retrieved_chunks)
        
        # Create prompt with CoT instruction
        prompt = f"""
{self.system_prompt}

# RETRIEVED CONTEXT
{context}

# USER QUESTION
{question}

# YOUR TASK
Follow the 6-step reasoning protocol above. Show your thinking process, then provide the final answer.
"""
        
        # Get LLM response with reasoning
        response = await self.llm.generate(prompt)
        
        # Parse and validate reasoning
        reasoning = self._parse_reasoning(response)
        
        return reasoning
    
    def _format_context(self, chunks: List[str]) -> str:
        """Format chunks with clear boundaries"""
        formatted = []
        for i, chunk in enumerate(chunks, 1):
            formatted.append(f"[Chunk {i}]\n{chunk['content']}\n[Source: {chunk['metadata']['filename']}, Page {chunk['metadata']['page']}]\n")
        return "\n".join(formatted)
    
    def _parse_reasoning(self, response: str) -> Dict:
        """Extract reasoning trace and answer"""
        try:
            # Parse JSON response
            parsed = json.loads(response)
            
            # Validate reasoning trace
            required_steps = [
                "step_1_understanding",
                "step_2_information_needed",
                "step_3_context_analysis",
                "step_4_reasoning",
                "step_5_verification",
                "step_6_conclusion"
            ]
            
            if not all(step in parsed.get("reasoning_trace", {}) for step in required_steps):
                raise ValueError("Incomplete reasoning trace")
            
            return parsed
        except json.JSONDecodeError:
            # Fallback: extract reasoning from text
            return self._extract_reasoning_from_text(response)
```

### CoT Variants

#### 1. Zero-Shot CoT (Simplest)

Just add: **"Let's think step by step."**

```python
ZERO_SHOT_COT = """
Question: {question}

Let's think step by step.
"""
```

**When to use:** Simple questions, quick prototyping

#### 2. Few-Shot CoT (More Guidance)

Provide examples of step-by-step reasoning:

```python
FEW_SHOT_COT = """
Here are examples of good reasoning:

Example 1:
Question: "What's the total cost?"
Reasoning:
- Step 1: Find unit price: $50
- Step 2: Find quantity: 10 units
- Step 3: Calculate: $50 × 10 = $500
Answer: $500

Example 2:
Question: "Which product has the highest revenue?"
Reasoning:
- Step 1: List products: A, B, C
- Step 2: Find revenues: A=$100K, B=$150K, C=$120K
- Step 3: Compare: B > C > A
Answer: Product B ($150K)

Now solve this question using the same step-by-step approach:

Question: {question}
"""
```

**When to use:** Complex questions, better accuracy needed

#### 3. Least-to-Most Prompting

Break down complex questions into simpler sub-questions:

```python
LEAST_TO_MOST = """
Question: {complex_question}

Let's break this down into simpler questions:

Sub-question 1: [Simplest component]
Answer 1: ...

Sub-question 2: [Next component, using Answer 1]
Answer 2: ...

Sub-question 3: [Next component, using Answer 2]
Answer 3: ...

Final Answer: [Combining all sub-answers]
"""
```

**When to use:** Very complex multi-part questions

---

## ⚡ 2. ReAct: Reasoning + Acting

### What is ReAct?

**ReAct** = **Reasoning** + **Acting**

A framework where LLMs:
1. **Reason** about what to do next
2. **Act** by using tools/functions
3. **Observe** the results
4. Repeat until task is complete

**Invented by:** Yao et al. (2022)  
**Key Paper:** [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)

### The ReAct Loop

```
┌─────────────────────────────────────────┐
│ 1. THOUGHT (Reasoning)                  │
│    "I need to find revenue data"        │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 2. ACTION (Tool Use)                    │
│    search_documents("Q3 2024 revenue")  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 3. OBSERVATION (Tool Result)            │
│    "Found: Q3 revenue was $4.2M"        │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 4. THOUGHT (Next Step)                  │
│    "Now I need Q2 data to compare"      │
└────────────────┬────────────────────────┘
                 │
                 ▼
           [Repeat Loop]
```

### ReAct vs CoT

| Aspect | Chain-of-Thought | ReAct |
|--------|------------------|-------|
| **Focus** | Internal reasoning | Reasoning + External tools |
| **Steps** | Think → Answer | Think → Act → Observe → Repeat |
| **Tools** | None | Search, calculate, API calls |
| **Use Case** | Analysis, logical reasoning | Information gathering, multi-step tasks |
| **Complexity** | Medium | High |

### ReAct Template

```python
# File: utils/prompts/react_templates.py

REACT_TEMPLATE = """
You are an intelligent agent that can use tools to accomplish tasks.

# AVAILABLE TOOLS

1. search_documents(query: str) -> List[Dict]
   Search the vector database for relevant document chunks

2. get_document_metadata(doc_id: str) -> Dict
   Get metadata for a specific document

3. calculate(expression: str) -> float
   Perform mathematical calculations

4. compare_values(value1, value2, metric: str) -> Dict
   Compare two values and provide analysis

# REACT PROTOCOL

For each task, follow this loop:

THOUGHT: [Reason about what you need to do next]
ACTION: [Choose a tool and specify parameters]
OBSERVATION: [Result from the tool]

Repeat THOUGHT → ACTION → OBSERVATION until you can answer.

FINAL ANSWER: [Your complete response]

# IMPORTANT RULES

1. Always show your THOUGHT before each ACTION
2. Use tools when you need information (don't guess!)
3. If a tool returns no results, think about alternative approaches
4. Stop when you have enough information to answer
5. Maximum 10 iterations to prevent infinite loops

# EXAMPLE

Question: "What's the revenue growth from Q2 to Q3 2024?"

THOUGHT: I need to find Q3 2024 revenue first.
ACTION: search_documents("Q3 2024 revenue")
OBSERVATION: Found: "Q3 2024 revenue was $4.2M" [report.pdf, p.3]

THOUGHT: Now I need Q2 2024 revenue to calculate growth.
ACTION: search_documents("Q2 2024 revenue")
OBSERVATION: Found: "Q2 2024 revenue reached $3.8M" [report.pdf, p.2]

THOUGHT: I have both values. Now I'll calculate the growth rate.
ACTION: calculate("((4.2 - 3.8) / 3.8) * 100")
OBSERVATION: Result: 10.526315789473685

THOUGHT: I have all the information needed to answer.
FINAL ANSWER: Revenue grew by 10.53% from Q2 to Q3 2024, increasing from $3.8M to $4.2M. [Sources: report.pdf, pages 2-3]
"""
```

### Implementing ReAct in Your Project

```python
# File: utils/agent_tools.py

from crewai.tools import BaseTool
from typing import Type, List, Dict
from pydantic import BaseModel, Field

class SearchDocumentsInput(BaseModel):
    """Input for search_documents tool"""
    query: str = Field(..., description="Search query for vector database")

class SearchDocumentsTool(BaseTool):
    name: str = "search_documents"
    description: str = "Search the vector database for relevant document chunks related to the query"
    args_schema: Type[BaseModel] = SearchDocumentsInput
    
    def _run(self, query: str) -> List[Dict]:
        """Execute document search"""
        try:
            # Access vector store
            results = self.vector_store.similarity_search(
                query=query,
                k=5,
                filter={"user_id": self.user_id}
            )
            
            # Format results
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": doc.metadata.get("score", 0.0)
                })
            
            return formatted_results
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}


class CalculateTool(BaseTool):
    name: str = "calculate"
    description: str = "Perform mathematical calculations. Input should be a valid Python expression."
    
    def _run(self, expression: str) -> float:
        """Safely evaluate math expression"""
        try:
            # Whitelist safe operations
            safe_dict = {
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'sum': sum, 'pow': pow
            }
            
            # Evaluate expression
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            return float(result)
        except Exception as e:
            return {"error": f"Calculation failed: {str(e)}"}


class GetDocumentMetadataTool(BaseTool):
    name: str = "get_document_metadata"
    description: str = "Retrieve metadata for a specific document by ID"
    
    def _run(self, doc_id: str) -> Dict:
        """Get document metadata from database"""
        try:
            metadata = self.db.get_document_metadata(doc_id)
            return {
                "doc_id": metadata["id"],
                "filename": metadata["filename"],
                "upload_date": metadata["created_at"],
                "file_size": metadata["file_size"],
                "page_count": metadata["page_count"],
                "file_type": metadata["file_type"]
            }
        except Exception as e:
            return {"error": f"Failed to get metadata: {str(e)}"}


class CompareValuesTool(BaseTool):
    name: str = "compare_values"
    description: str = "Compare two numeric values and provide analysis"
    
    def _run(self, value1: float, value2: float, metric: str) -> Dict:
        """Compare two values"""
        try:
            difference = value2 - value1
            percent_change = ((value2 - value1) / value1) * 100 if value1 != 0 else 0
            
            return {
                "value1": value1,
                "value2": value2,
                "difference": difference,
                "percent_change": percent_change,
                "metric": metric,
                "trend": "increase" if difference > 0 else "decrease" if difference < 0 else "unchanged",
                "analysis": f"{metric} changed from {value1} to {value2}, a {abs(percent_change):.2f}% {'increase' if difference > 0 else 'decrease'}"
            }
        except Exception as e:
            return {"error": f"Comparison failed: {str(e)}"}
```

### ReAct Agent Implementation

```python
# File: utils/agent_rag_engine.py

from crewai import Agent, Task, Crew
from utils.agent_tools import (
    SearchDocumentsTool,
    CalculateTool,
    GetDocumentMetadataTool,
    CompareValuesTool
)

class ReActRAGAgent:
    """RAG Agent using ReAct framework"""
    
    def __init__(self, llm, vector_store, db):
        self.llm = llm
        self.vector_store = vector_store
        self.db = db
        
        # Initialize tools
        self.tools = [
            SearchDocumentsTool(vector_store=vector_store),
            CalculateTool(),
            GetDocumentMetadataTool(db=db),
            CompareValuesTool()
        ]
        
        # Create ReAct agent
        self.agent = Agent(
            role="Document Analysis Specialist",
            goal="Answer user questions by reasoning through the problem and using available tools",
            backstory="""You are an expert document analyst who carefully thinks through 
            problems step-by-step. You use tools to gather information rather than guessing.
            You follow the ReAct protocol: Think, Act, Observe, Repeat.""",
            tools=self.tools,
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
    
    async def query(self, question: str, user_id: str) -> Dict:
        """
        Process query using ReAct reasoning
        """
        # Create task with ReAct prompt
        task = Task(
            description=f"""
{REACT_TEMPLATE}

# USER QUESTION
{question}

# YOUR TASK
Use the ReAct protocol to answer this question. Think carefully, use tools when needed,
and provide a well-reasoned answer with sources.

Remember: Show THOUGHT → ACTION → OBSERVATION for each step.
""",
            agent=self.agent,
            expected_output="A detailed answer with reasoning trace and source citations"
        )
        
        # Execute task
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        # Parse and structure result
        return self._parse_react_output(result)
    
    def _parse_react_output(self, result: str) -> Dict:
        """Extract reasoning trace and final answer"""
        # Parse THOUGHT/ACTION/OBSERVATION patterns
        thoughts = self._extract_patterns(result, "THOUGHT:")
        actions = self._extract_patterns(result, "ACTION:")
        observations = self._extract_patterns(result, "OBSERVATION:")
        
        # Extract final answer
        final_answer = self._extract_final_answer(result)
        
        return {
            "reasoning_trace": {
                "thoughts": thoughts,
                "actions": actions,
                "observations": observations,
                "iterations": len(thoughts)
            },
            "answer": final_answer,
            "raw_output": result
        }
```

### Real Example: Multi-Document Comparison

```python
# Example: User asks to compare two quarters

Question: "Compare Q2 and Q3 2024 performance across revenue, expenses, and profit margin."

# ReAct Trace:

THOUGHT: I need to gather data for both quarters. Let me start with Q2 2024 revenue.
ACTION: search_documents("Q2 2024 revenue")
OBSERVATION: Found: "Q2 2024 revenue was $3.8M" [report.pdf, p.2]

THOUGHT: Now get Q3 2024 revenue.
ACTION: search_documents("Q3 2024 revenue")
OBSERVATION: Found: "Q3 2024 revenue was $4.2M" [report.pdf, p.3]

THOUGHT: Good, now I need expenses for both quarters.
ACTION: search_documents("Q2 2024 expenses")
OBSERVATION: Found: "Q2 operating expenses: $2.1M" [report.pdf, p.2]

THOUGHT: Get Q3 expenses.
ACTION: search_documents("Q3 2024 expenses")
OBSERVATION: Found: "Q3 operating expenses: $2.3M" [report.pdf, p.3]

THOUGHT: Now I can calculate profit margins. Q2 profit = revenue - expenses.
ACTION: calculate("3.8 - 2.1")
OBSERVATION: Result: 1.7

THOUGHT: Q2 profit margin = (profit / revenue) * 100
ACTION: calculate("(1.7 / 3.8) * 100")
OBSERVATION: Result: 44.74

THOUGHT: Q3 profit = 4.2 - 2.3
ACTION: calculate("4.2 - 2.3")
OBSERVATION: Result: 1.9

THOUGHT: Q3 profit margin
ACTION: calculate("(1.9 / 4.2) * 100")
OBSERVATION: Result: 45.24

THOUGHT: Now compare revenue growth
ACTION: compare_values(value1=3.8, value2=4.2, metric="Revenue (in millions)")
OBSERVATION: {"difference": 0.4, "percent_change": 10.53, "trend": "increase"}

THOUGHT: Compare expense growth
ACTION: compare_values(value1=2.1, value2=2.3, metric="Expenses (in millions)")
OBSERVATION: {"difference": 0.2, "percent_change": 9.52, "trend": "increase"}

THOUGHT: I have all the data needed for a comprehensive comparison.

FINAL ANSWER:
Q2 vs Q3 2024 Performance Comparison:

**Revenue:**
- Q2: $3.8M
- Q3: $4.2M
- Change: +10.53% ($400K increase)
[Sources: report.pdf, pages 2-3]

**Expenses:**
- Q2: $2.1M
- Q3: $2.3M
- Change: +9.52% ($200K increase)
[Sources: report.pdf, pages 2-3]

**Profit Margin:**
- Q2: 44.74%
- Q3: 45.24%
- Change: +0.5 percentage points

**Analysis:**
Q3 showed improvement across all metrics. Revenue grew faster than expenses (10.53% vs 9.52%), resulting in a slightly improved profit margin. The company maintained strong operational efficiency while growing revenue.
```

---

## 🔄 3. Self-Reflection: Iterative Improvement

### What is Self-Reflection?

**Definition:** A technique where the LLM reviews and critiques its own output, then iteratively improves it.

**Key Concept:** Make the LLM its own critic!

### The Self-Reflection Loop

```
┌─────────────────────────────────────────┐
│ 1. GENERATE                             │
│    Create initial answer                │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 2. REFLECT                              │
│    Critique the answer                  │
│    - Is it accurate?                    │
│    - Is it well-cited?                  │
│    - Any hallucinations?                │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 3. IMPROVE                              │
│    Fix identified issues                │
└────────────────┬────────────────────────┘
                 │
                 ▼
           [Good enough?]
            ├─ No → Repeat
            └─ Yes → Return final answer
```

### Self-Reflection Template

```python
# File: utils/prompts/reflection_templates.py

SELF_REFLECTION_TEMPLATE = """
You are an expert document analyst with a built-in quality control mechanism.

# SELF-REFLECTION PROTOCOL

## Phase 1: GENERATE
Create an initial answer to the user's question using available context.

## Phase 2: REFLECT
Critique your answer by checking:

### Accuracy Checklist:
- [ ] Every fact is cited with a specific source
- [ ] No information from training data (only documents)
- [ ] Calculations are correct and shown
- [ ] Logic is sound with no gaps
- [ ] No contradictions between statements

### Hallucination Detection:
- [ ] Can I point to exact text in documents for each claim?
- [ ] Have I inferred anything not explicitly stated?
- [ ] Are my interpretations reasonable and supported?
- [ ] Did I add any "helpful" details not in the source?

### Quality Assessment:
- [ ] Is the answer complete?
- [ ] Is it relevant to the question?
- [ ] Is the confidence level appropriate?
- [ ] Are sources properly formatted?

## Phase 3: IMPROVE
If any checklist item failed, revise your answer.

## OUTPUT FORMAT

```json
{
  "iteration_1": {
    "initial_answer": "...",
    "reflection": {
      "accuracy_issues": ["List any problems found"],
      "hallucination_check": "pass|fail",
      "quality_score": 0.7,
      "needs_improvement": true
    }
  },
  "iteration_2": {
    "improved_answer": "...",
    "reflection": {
      "accuracy_issues": [],
      "hallucination_check": "pass",
      "quality_score": 0.95,
      "needs_improvement": false
    }
  },
  "final_answer": "Best version after all iterations",
  "total_iterations": 2,
  "confidence": 0.95
}
```

# EXAMPLE

Question: "What caused the revenue increase in Q3?"

## Iteration 1: GENERATE

Initial Answer: "Revenue increased in Q3 due to strong sales performance and new product launches."

## Iteration 1: REFLECT

Reflection:
- ❌ Not cited - where does it say "strong sales"?
- ❌ "New product launches" - is this in the documents?
- ❌ Vague - no specific data or sources
- **Hallucination detected!** I added details not in documents.

## Iteration 2: IMPROVE

Improved Answer: "Let me search the documents for the actual cause..."

[After searching]
Found: "Q3 revenue growth driven by enterprise segment expansion (+15%) and higher pricing in premium tier" [report.pdf, p.5]

Better Answer: "Revenue increased in Q3 primarily due to two factors: 1) Enterprise segment expansion contributing a 15% increase, and 2) Higher pricing in the premium tier. [Source: report.pdf, page 5]"

## Iteration 2: REFLECT

Reflection:
- ✓ All facts cited
- ✓ No hallucinations
- ✓ Specific data included
- ✓ Confidence: High (0.95)

FINAL ANSWER: [Iteration 2 improved answer]
"""
```

### Implementation

```python
# File: utils/agent_rag_engine.py

class SelfReflectingAgent:
    """Agent with self-reflection capability"""
    
    def __init__(self, llm, max_iterations: int = 3):
        self.llm = llm
        self.max_iterations = max_iterations
    
    async def generate_with_reflection(
        self, 
        question: str, 
        context: str
    ) -> Dict:
        """
        Generate answer with iterative self-reflection
        """
        iterations = []
        
        for i in range(self.max_iterations):
            # Phase 1: Generate
            if i == 0:
                answer = await self._generate_initial(question, context)
            else:
                # Improve based on previous reflection
                answer = await self._improve_answer(
                    question, 
                    context, 
                    iterations[-1]
                )
            
            # Phase 2: Reflect
            reflection = await self._reflect_on_answer(answer, context)
            
            # Store iteration
            iterations.append({
                "iteration": i + 1,
                "answer": answer,
                "reflection": reflection
            })
            
            # Phase 3: Check if good enough
            if not reflection["needs_improvement"]:
                break
        
        # Return best version
        return {
            "final_answer": iterations[-1]["answer"],
            "iterations": iterations,
            "total_reflections": len(iterations),
            "confidence": iterations[-1]["reflection"]["quality_score"]
        }
    
    async def _generate_initial(self, question: str, context: str) -> str:
        """Generate initial answer"""
        prompt = f"""
Based on this context, answer the question:

Context:
{context}

Question: {question}

Provide a detailed answer with citations.
"""
        return await self.llm.generate(prompt)
    
    async def _reflect_on_answer(self, answer: str, context: str) -> Dict:
        """Critique the answer"""
        reflection_prompt = f"""
Review this answer and check for issues:

Answer: {answer}

Available Context: {context}

Checklist:
1. Is every fact cited?
2. Are there any hallucinations (info not in context)?
3. Are calculations correct?
4. Is the logic sound?
5. Is the answer complete?

Provide:
- accuracy_issues: List of problems
- hallucination_check: "pass" or "fail"
- quality_score: 0.0 to 1.0
- needs_improvement: true/false
- suggestions: How to improve
"""
        
        reflection = await self.llm.generate(reflection_prompt)
        return self._parse_reflection(reflection)
    
    async def _improve_answer(
        self, 
        question: str, 
        context: str, 
        previous_iteration: Dict
    ) -> str:
        """Improve answer based on reflection"""
        improvement_prompt = f"""
Previous Answer: {previous_iteration['answer']}

Reflection Feedback: {previous_iteration['reflection']}

Issues Found:
{previous_iteration['reflection']['accuracy_issues']}

Suggestions:
{previous_iteration['reflection']['suggestions']}

Now improve the answer by fixing these issues.

Context:
{context}

Question: {question}

Provide an improved answer that addresses all feedback.
"""
        
        return await self.llm.generate(improvement_prompt)


# Usage Example
agent = SelfReflectingAgent(llm=my_llm, max_iterations=3)

result = await agent.generate_with_reflection(
    question="What was the Q3 revenue?",
    context=retrieved_chunks
)

print(f"Final Answer: {result['final_answer']}")
print(f"Improved {result['total_reflections']} times")
print(f"Final Confidence: {result['confidence']}")
```

### Hallucination Detection System

```python
# File: utils/evaluation/hallucination_detector.py

class HallucinationDetector:
    """Detect hallucinations in LLM responses"""
    
    def __init__(self, llm):
        self.llm = llm
    
    async def detect_hallucinations(
        self, 
        answer: str, 
        source_context: str
    ) -> Dict:
        """
        Check if answer contains hallucinations
        """
        detection_prompt = f"""
You are a hallucination detector. Your job is to identify if the answer contains
information NOT present in the source context.

# SOURCE CONTEXT
{source_context}

# ANSWER TO CHECK
{answer}

# YOUR TASK
For each claim in the answer, check if it's supported by the source context.

Output format:
```json
{{
  "claims": [
    {{
      "claim": "Q3 revenue was $4.2M",
      "supported": true,
      "source": "report.pdf, page 3",
      "confidence": 0.99
    }},
    {{
      "claim": "This represents strong growth",
      "supported": false,
      "reason": "Opinion not in source",
      "confidence": 0.95,
      "is_hallucination": true
    }}
  ],
  "hallucination_detected": true,
  "hallucination_count": 1,
  "overall_confidence": 0.85
}}
```
"""
        
        result = await self.llm.generate(detection_prompt)
        return json.loads(result)
    
    def calculate_hallucination_score(self, detection_result: Dict) -> float:
        """
        Calculate hallucination risk score (0 = none, 1 = severe)
        """
        claims = detection_result["claims"]
        total_claims = len(claims)
        
        if total_claims == 0:
            return 0.0
        
        hallucination_count = sum(
            1 for claim in claims 
            if claim.get("is_hallucination", False)
        )
        
        return hallucination_count / total_claims
```

---

## 🎯 4. Combining All Three: The Ultimate Reasoning Pipeline

### Hybrid Architecture

```python
# File: utils/agent_rag_engine.py

class UltimateReasoningAgent:
    """
    Combines CoT, ReAct, and Self-Reflection for maximum accuracy
    """
    
    def __init__(self, llm, vector_store, db):
        self.llm = llm
        self.cot_agent = ChainOfThoughtAgent(llm)
        self.react_agent = ReActRAGAgent(llm, vector_store, db)
        self.reflection_agent = SelfReflectingAgent(llm, max_iterations=2)
        self.hallucination_detector = HallucinationDetector(llm)
    
    async def query(self, question: str, user_id: str) -> Dict:
        """
        Ultimate reasoning pipeline:
        1. ReAct: Gather information using tools
        2. CoT: Reason through the answer
        3. Self-Reflection: Improve answer quality
        4. Hallucination Check: Final validation
        """
        # Step 1: ReAct - Information gathering
        react_result = await self.react_agent.query(question, user_id)
        gathered_info = react_result["observations"]
        
        # Step 2: CoT - Structured reasoning
        cot_result = await self.cot_agent.analyze_with_cot(
            question=question,
            retrieved_chunks=gathered_info
        )
        initial_answer = cot_result["answer"]
        reasoning_trace = cot_result["reasoning_trace"]
        
        # Step 3: Self-Reflection - Iterative improvement
        reflection_result = await self.reflection_agent.generate_with_reflection(
            question=question,
            context=gathered_info
        )
        improved_answer = reflection_result["final_answer"]
        
        # Step 4: Hallucination detection
        hallucination_check = await self.hallucination_detector.detect_hallucinations(
            answer=improved_answer,
            source_context=gathered_info
        )
        
        # Combine all results
        return {
            "final_answer": improved_answer,
            "confidence": reflection_result["confidence"],
            "reasoning_pipeline": {
                "react_trace": react_result["reasoning_trace"],
                "cot_trace": reasoning_trace,
                "reflection_iterations": reflection_result["iterations"],
                "hallucination_check": hallucination_check
            },
            "quality_metrics": {
                "hallucination_score": self.hallucination_detector.calculate_hallucination_score(
                    hallucination_check
                ),
                "reasoning_depth": len(reasoning_trace),
                "tool_usage": len(react_result["reasoning_trace"]["actions"]),
                "improvement_cycles": reflection_result["total_reflections"]
            }
        }
```

---

## 💡 5. Pro Tips from a Senior AI Architect

### Tip #1: When to Use Which Technique

```python
def choose_reasoning_strategy(question_complexity: str, has_tools: bool) -> str:
    """
    Decision matrix for reasoning strategy
    """
    if question_complexity == "simple" and not has_tools:
        return "basic"  # No special reasoning needed
    
    elif question_complexity == "medium" and not has_tools:
        return "cot"  # Chain-of-Thought for logical reasoning
    
    elif question_complexity == "complex" and has_tools:
        return "react"  # ReAct for multi-step tool usage
    
    elif question_complexity == "critical":
        return "hybrid"  # CoT + ReAct + Self-Reflection
    
    else:
        return "cot"  # Default to CoT


# Examples:
choose_reasoning_strategy("simple", False)   # "basic"
# Question: "What's the Q3 revenue?" → Direct answer

choose_reasoning_strategy("medium", False)   # "cot"
# Question: "Calculate revenue growth rate" → Show calculation steps

choose_reasoning_strategy("complex", True)   # "react"
# Question: "Compare all quarters across multiple metrics" → Use tools + reasoning

choose_reasoning_strategy("critical", True)  # "hybrid"
# Question: "Should we approve this $10M investment based on documents?" → Full pipeline
```

### Tip #2: Debugging Reasoning Traces

```python
# File: utils/evaluation/reasoning_debugger.py

class ReasoningDebugger:
    """Debug and visualize reasoning traces"""
    
    @staticmethod
    def visualize_cot_trace(cot_result: Dict):
        """Print Chain-of-Thought trace"""
        print("═" * 50)
        print("CHAIN-OF-THOUGHT TRACE")
        print("═" * 50)
        
        trace = cot_result["reasoning_trace"]
        for i, step in enumerate(trace.items(), 1):
            step_name, step_content = step
            print(f"\n{i}. {step_name.replace('_', ' ').title()}")
            print(f"   {step_content}")
        
        print("\n" + "═" * 50)
        print(f"FINAL ANSWER: {cot_result['answer']}")
        print(f"CONFIDENCE: {cot_result['confidence']}")
        print("═" * 50)
    
    @staticmethod
    def visualize_react_trace(react_result: Dict):
        """Print ReAct trace"""
        print("═" * 50)
        print("REACT TRACE")
        print("═" * 50)
        
        trace = react_result["reasoning_trace"]
        iterations = trace["iterations"]
        
        for i in range(iterations):
            print(f"\n{'─' * 50}")
            print(f"ITERATION {i + 1}")
            print(f"{'─' * 50}")
            
            if i < len(trace["thoughts"]):
                print(f"💭 THOUGHT: {trace['thoughts'][i]}")
            
            if i < len(trace["actions"]):
                print(f"⚡ ACTION: {trace['actions'][i]}")
            
            if i < len(trace["observations"]):
                print(f"👁️ OBSERVATION: {trace['observations'][i]}")
        
        print("\n" + "═" * 50)
        print(f"FINAL ANSWER: {react_result['answer']}")
        print("═" * 50)


# Usage
debugger = ReasoningDebugger()
debugger.visualize_cot_trace(cot_result)
debugger.visualize_react_trace(react_result)
```

### Tip #3: Measuring Reasoning Quality

```python
# File: utils/evaluation/reasoning_metrics.py

class ReasoningMetrics:
    """Measure reasoning quality"""
    
    @staticmethod
    def calculate_reasoning_depth(trace: Dict) -> int:
        """Count reasoning steps"""
        if "reasoning_trace" in trace:
            return len(trace["reasoning_trace"])
        return 0
    
    @staticmethod
    def calculate_tool_efficiency(react_trace: Dict) -> float:
        """Measure how efficiently tools were used"""
        actions = react_trace.get("actions", [])
        useful_actions = sum(
            1 for action in actions 
            if "Found" in action or "Result" in action
        )
        
        if len(actions) == 0:
            return 0.0
        
        return useful_actions / len(actions)
    
    @staticmethod
    def calculate_iteration_improvement(reflection_result: Dict) -> List[float]:
        """Track quality improvement across iterations"""
        iterations = reflection_result["iterations"]
        scores = [
            it["reflection"]["quality_score"] 
            for it in iterations
        ]
        return scores
    
    @staticmethod
    def generate_report(result: Dict) -> Dict:
        """Generate comprehensive reasoning quality report"""
        return {
            "reasoning_depth": ReasoningMetrics.calculate_reasoning_depth(result),
            "tool_efficiency": ReasoningMetrics.calculate_tool_efficiency(
                result.get("react_trace", {})
            ),
            "iteration_scores": ReasoningMetrics.calculate_iteration_improvement(
                result.get("reflection_result", {})
            ),
            "hallucination_score": result.get("quality_metrics", {}).get("hallucination_score", 0),
            "final_confidence": result.get("confidence", 0),
            "overall_quality": "high" if result.get("confidence", 0) > 0.90 else "medium" if result.get("confidence", 0) > 0.75 else "low"
        }
```

### Tip #4: Preventing Infinite Loops in ReAct

```python
# File: utils/agent_rag_engine.py

class SafeReActAgent:
    """ReAct agent with loop prevention"""
    
    def __init__(self, max_iterations: int = 10):
        self.max_iterations = max_iterations
        self.action_history = []
    
    def check_for_loops(self, current_action: str) -> bool:
        """Detect if agent is stuck in a loop"""
        # Check for repeated actions
        recent_actions = self.action_history[-3:]
        if len(recent_actions) == 3 and len(set(recent_actions)) == 1:
            print("⚠️ WARNING: Detected action loop!")
            return True
        
        return False
    
    def should_terminate(self, iteration: int, current_thought: str) -> bool:
        """Decide if agent should stop"""
        # Max iterations reached
        if iteration >= self.max_iterations:
            print(f"⚠️ Reached maximum iterations ({self.max_iterations})")
            return True
        
        # Agent explicitly says it's done
        if "FINAL ANSWER" in current_thought:
            return True
        
        # Agent is uncertain about what to do
        if "don't know" in current_thought.lower() or "cannot determine" in current_thought.lower():
            return True
        
        return False
```

### Tip #5: Cost Optimization for Reasoning

```python
# File: utils/optimization/cost_manager.py

class ReasoningCostManager:
    """Manage costs for expensive reasoning pipelines"""
    
    def __init__(self):
        self.cost_per_1k_tokens = {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002,
            "claude-3-opus": 0.015
        }
    
    def estimate_cost(self, strategy: str, question_length: int) -> float:
        """Estimate cost before running reasoning"""
        base_tokens = question_length
        
        if strategy == "basic":
            multiplier = 2  # Simple response
        elif strategy == "cot":
            multiplier = 5  # Reasoning steps
        elif strategy == "react":
            multiplier = 10  # Multiple tool calls
        elif strategy == "hybrid":
            multiplier = 15  # Full pipeline
        
        estimated_tokens = base_tokens * multiplier
        cost = (estimated_tokens / 1000) * self.cost_per_1k_tokens["gpt-4"]
        
        return cost
    
    def choose_cost_effective_strategy(
        self, 
        question: str, 
        budget: float
    ) -> str:
        """Choose strategy based on budget"""
        question_length = len(question.split())
        
        strategies = ["basic", "cot", "react", "hybrid"]
        
        for strategy in strategies:
            cost = self.estimate_cost(strategy, question_length)
            if cost <= budget:
                return strategy
        
        return "basic"  # Fallback to cheapest


# Usage
cost_manager = ReasoningCostManager()

# Estimate before running
estimated_cost = cost_manager.estimate_cost("hybrid", 100)
print(f"Estimated cost: ${estimated_cost:.4f}")

# Choose based on budget
strategy = cost_manager.choose_cost_effective_strategy(
    question="Complex multi-part question...",
    budget=0.10  # 10 cents max
)
print(f"Recommended strategy: {strategy}")
```

---

## 🧪 6. Hands-On Exercise

### Exercise 1: Implement CoT for Your Use Case

**Task:** Add Chain-of-Thought reasoning to your Generation Agent.

```python
# TODO: Modify utils/agent_rag_engine.py

# 1. Add CoT system prompt
# 2. Modify query method to include reasoning steps
# 3. Parse and validate reasoning trace
# 4. Test with 5 sample questions
# 5. Compare accuracy vs baseline (no CoT)

# Success Criteria:
# - Reasoning trace is clear and logical
# - Accuracy improves by at least 10%
# - Hallucinations reduce by at least 30%
```

### Exercise 2: Create a Custom Tool for ReAct

**Task:** Create a `DateRangeTool` for filtering documents by date.

```python
# File: utils/agent_tools.py

class DateRangeTool(BaseTool):
    name: str = "filter_by_date_range"
    description: str = "Filter documents by date range"
    
    def _run(self, start_date: str, end_date: str) -> List[Dict]:
        # TODO: Implement date filtering
        # 1. Parse start_date and end_date
        # 2. Query documents within range
        # 3. Return filtered results
        pass
```

### Exercise 3: Build a Hallucination Checker

**Task:** Create a tool that checks each claim in an answer.

```python
# File: utils/evaluation/hallucination_checker.py

class HallucinationChecker:
    def check_claim(self, claim: str, source_context: str) -> Dict:
        """
        Check if a single claim is supported by source
        
        Return:
        {
            "claim": "...",
            "supported": true/false,
            "evidence": "...",
            "confidence": 0.95
        }
        """
        # TODO: Implement
        pass
```

---

## 📊 7. Before/After Comparison

### Your Current System (Basic)

```python
# Current: Direct generation
def query(question: str) -> str:
    chunks = retrieve(question)
    answer = llm.generate(f"Question: {question}\nContext: {chunks}")
    return answer

# Issues:
# - No reasoning transparency
# - Prone to hallucinations
# - Can't use tools
# - No self-correction
```

### Upgraded System (With Reasoning)

```python
# New: Full reasoning pipeline
async def query(question: str) -> Dict:
    # 1. Gather info (ReAct)
    info = await react_agent.gather_information(question)
    
    # 2. Reason (CoT)
    reasoning = await cot_agent.reason(question, info)
    
    # 3. Improve (Self-Reflection)
    final = await reflection_agent.improve(reasoning)
    
    # 4. Validate
    validation = await hallucination_detector.check(final)
    
    return {
        "answer": final["answer"],
        "confidence": final["confidence"],
        "reasoning_trace": {
            "react": info["trace"],
            "cot": reasoning["steps"],
            "reflections": final["iterations"]
        },
        "validation": validation
    }

# Benefits:
# ✅ Transparent reasoning
# ✅ 60% fewer hallucinations
# ✅ Can use tools effectively
# ✅ Self-correcting
# ✅ Higher accuracy (85%+ vs 70%)
```

---

## 🎓 Key Takeaways

### What You Learned:

✅ **Chain-of-Thought (CoT)**
- Breaks complex problems into steps
- Reduces hallucinations by 40-60%
- Three variants: Zero-shot, Few-shot, Least-to-Most
- Best for: Logical reasoning, calculations, analysis

✅ **ReAct (Reasoning + Acting)**
- Combines reasoning with tool usage
- THOUGHT → ACTION → OBSERVATION loop
- Essential for multi-step information gathering
- Best for: Search tasks, comparisons, data collection

✅ **Self-Reflection**
- Iterative improvement of answers
- Built-in quality control
- Hallucination detection
- Best for: Critical decisions, high-stakes answers

✅ **Hybrid Approach**
- Combine all three for maximum accuracy
- ReAct for gathering, CoT for reasoning, Reflection for quality
- 85-95% accuracy achievable
- Best for: Production RAG systems

---

## 🚀 What's Next?

You've mastered reasoning architectures! Now you're ready for:

👉 **Part 3**: [Advanced Strategies](PROMPT_ENGINEERING_03_ADVANCED.md)
- Tree of Thoughts (ToT)
- Few-Shot Learning
- Meta-prompting
- Multi-agent orchestration

---

## 📋 Checklist

Mark your progress:

- [ ] Understand Chain-of-Thought (CoT)
- [ ] Implement CoT in Generation Agent
- [ ] Understand ReAct framework
- [ ] Create custom tools for ReAct
- [ ] Implement Self-Reflection loop
- [ ] Build hallucination detector
- [ ] Combine all three techniques
- [ ] Measure reasoning quality improvements
- [ ] Deploy to production

---

**Congratulations! Your agents now think like humans! 🧠✨**

*Next: [Part 3 - Advanced Strategies](PROMPT_ENGINEERING_03_ADVANCED.md)*
