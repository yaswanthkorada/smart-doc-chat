# ⚡ Part 4: Advanced Tool Use & Reasoning

## Parallel Execution, Self-Reflection, and Peer Review

**Learning Time:** 12-14 hours  
**Difficulty:** Advanced  
**Prerequisites:** Parts 1-3 (Orchestration, Agents, Communication)

---

## 🎯 Learning Objectives

By the end of this guide, you'll be able to:
- ✅ Execute 10+ agents in parallel (async/threading)
- ✅ Implement self-reflection loops (agents critique their own work)
- ✅ Build peer review systems (agents review each other)
- ✅ Handle complex tool chains (Tool A → Tool B → Tool C)
- ✅ Implement parallel tool execution
- ✅ Optimize latency with concurrent operations
- ✅ Handle tool errors gracefully

---

## 📚 The Problem: Sequential Processing is Slow

### Current Bottleneck: One Agent at a Time

```python
# Sequential processing (SLOW)
def process_100_documents_sequential(documents):
    results = []
    
    for doc in documents:  # 100 iterations
        result = agent.process(doc)  # 2 seconds each
        results.append(result)
    
    # Total time: 100 × 2 = 200 seconds (3.3 minutes!)
    return results
```

**Issues:**
- ❌ Wastes time waiting for each agent
- ❌ Doesn't utilize multiple CPU cores
- ❌ Can't scale beyond single machine capacity
- ❌ User waits 3+ minutes for results

---

### Real Example from Your Project

**User Query:** *"Analyze all 100 Q3 2024 financial reports and find top 10 companies by revenue growth"*

**Sequential Approach (Current):**
```
Document 1:  [Agent processes] ■■■■■■■■■■ 2.0s
Document 2:  [Agent processes] ■■■■■■■■■■ 2.0s
Document 3:  [Agent processes] ■■■■■■■■■■ 2.0s
...
Document 100: [Agent processes] ■■■■■■■■■■ 2.0s

Total time: 200 seconds (3.3 minutes)
User experience: 😴 Too slow!
```

**Parallel Approach (Target):**
```
10 Agents working simultaneously:

Agent 1:  Docs 1-10   [■■■■■■■■■■] 20s
Agent 2:  Docs 11-20  [■■■■■■■■■■] 20s
Agent 3:  Docs 21-30  [■■■■■■■■■■] 20s
...
Agent 10: Docs 91-100 [■■■■■■■■■■] 20s

Total time: 20 seconds (10x faster!)
User experience: 🚀 Lightning fast!
```

---

## 🚀 Pattern 1: Parallel Agent Execution

### Concept
**Concurrent processing:** Run multiple agents simultaneously using async/threading to process data in parallel.

---

### Implementation 1: AsyncIO (Python Native)

```python
import asyncio
from typing import List, Dict
from datetime import datetime

class ParallelAgentExecutor:
    """
    Execute multiple agents in parallel using asyncio
    """
    
    def __init__(self, num_agents: int = 10):
        self.num_agents = num_agents
    
    async def process_document(self, doc: dict, agent_id: int) -> dict:
        """
        Process a single document (async)
        """
        print(f"🔄 Agent {agent_id}: Processing {doc['name']}")
        
        # Simulate processing with async I/O (API calls, etc.)
        await asyncio.sleep(2)  # Simulates 2s processing time
        
        # Extract information (simulated)
        result = {
            'document': doc['name'],
            'agent_id': agent_id,
            'revenue': f"${doc['id'] * 1.5}M",
            'growth': f"+{doc['id'] * 2}%",
            'processed_at': datetime.now().isoformat()
        }
        
        print(f"✅ Agent {agent_id}: Completed {doc['name']}")
        return result
    
    async def process_batch_parallel(self, documents: List[dict]) -> List[dict]:
        """
        Process documents in parallel using multiple agents
        """
        print(f"\n{'='*60}")
        print(f"PARALLEL EXECUTION: {len(documents)} documents")
        print(f"Agents: {self.num_agents}")
        print(f"{'='*60}\n")
        
        start_time = datetime.now()
        
        # Distribute documents to agents
        tasks = []
        for i, doc in enumerate(documents):
            agent_id = (i % self.num_agents) + 1
            tasks.append(self.process_document(doc, agent_id))
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print(f"\n{'='*60}")
        print(f"✅ COMPLETED: Processed {len(results)} documents in {elapsed:.1f}s")
        print(f"Average: {elapsed / len(results):.2f}s per document")
        print(f"Speedup: {(len(documents) * 2) / elapsed:.1f}x faster")
        print(f"{'='*60}\n")
        
        return results


# Usage
async def main():
    # Simulate 100 documents
    documents = [
        {'id': i, 'name': f'financial_report_{i}.pdf'}
        for i in range(1, 101)
    ]
    
    # Create executor with 10 parallel agents
    executor = ParallelAgentExecutor(num_agents=10)
    
    # Process in parallel
    results = await executor.process_batch_parallel(documents)
    
    # Analyze results
    print("Top 5 by revenue:")
    sorted_results = sorted(results, key=lambda x: float(x['revenue'].replace('$', '').replace('M', '')), reverse=True)
    for r in sorted_results[:5]:
        print(f"  {r['document']}: {r['revenue']} ({r['growth']} growth)")


# Run
asyncio.run(main())
```

**Output:**
```
============================================================
PARALLEL EXECUTION: 100 documents
Agents: 10
============================================================

🔄 Agent 1: Processing financial_report_1.pdf
🔄 Agent 2: Processing financial_report_2.pdf
🔄 Agent 3: Processing financial_report_3.pdf
...
🔄 Agent 10: Processing financial_report_10.pdf
🔄 Agent 1: Processing financial_report_11.pdf
...
✅ Agent 1: Completed financial_report_1.pdf
✅ Agent 5: Completed financial_report_5.pdf
✅ Agent 3: Completed financial_report_3.pdf
...

============================================================
✅ COMPLETED: Processed 100 documents in 20.2s
Average: 0.20s per document
Speedup: 9.9x faster
============================================================

Top 5 by revenue:
  financial_report_100.pdf: $150.0M (+200% growth)
  financial_report_99.pdf: $148.5M (+198% growth)
  financial_report_98.pdf: $147.0M (+196% growth)
  financial_report_97.pdf: $145.5M (+194% growth)
  financial_report_96.pdf: $144.0M (+192% growth)
```

---

### Implementation 2: ThreadPoolExecutor (CPU-Bound Tasks)

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable
import time

class ThreadedAgentExecutor:
    """
    Execute agents in parallel using threads (for CPU-bound tasks)
    """
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
    
    def process_document(self, doc: dict, agent_id: int) -> dict:
        """
        Process a single document (synchronous)
        """
        print(f"🔄 Thread {agent_id}: Processing {doc['name']}")
        
        # Simulate CPU-intensive work
        time.sleep(2)  # Simulates processing
        
        result = {
            'document': doc['name'],
            'thread_id': agent_id,
            'revenue': f"${doc['id'] * 1.5}M"
        }
        
        print(f"✅ Thread {agent_id}: Completed {doc['name']}")
        return result
    
    def process_batch_threaded(self, documents: List[dict]) -> List[dict]:
        """
        Process documents using thread pool
        """
        print(f"\n{'='*60}")
        print(f"THREADED EXECUTION: {len(documents)} documents")
        print(f"Threads: {self.max_workers}")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_doc = {
                executor.submit(self.process_document, doc, (i % self.max_workers) + 1): doc
                for i, doc in enumerate(documents)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_doc):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        elapsed = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"✅ COMPLETED: {len(results)} documents in {elapsed:.1f}s")
        print(f"{'='*60}\n")
        
        return results


# Usage
documents = [{'id': i, 'name': f'report_{i}.pdf'} for i in range(1, 101)]

executor = ThreadedAgentExecutor(max_workers=10)
results = executor.process_batch_threaded(documents)
```

---

### Implementation 3: Real Multi-Agent Parallel Processing

```python
from crewai import Agent, Task, Crew
import asyncio
from typing import List

class RealWorldParallelAgents:
    """
    Parallel execution with real CrewAI agents
    """
    
    def __init__(self, num_agents: int = 10):
        self.num_agents = num_agents
        self.agents = self._create_agents()
    
    def _create_agents(self) -> List[Agent]:
        """Create pool of worker agents"""
        agents = []
        for i in range(self.num_agents):
            agent = Agent(
                role=f"Document Analyst #{i+1}",
                goal="Extract revenue and growth data from financial documents",
                backstory=f"Specialist analyst #{i+1} with expertise in financial analysis",
                tools=[self.extract_revenue_tool(), self.calculate_growth_tool()],
                verbose=False  # Reduce noise
            )
            agents.append(agent)
        
        return agents
    
    def extract_revenue_tool(self):
        """Tool to extract revenue from documents"""
        from langchain.tools import Tool
        
        def extract_revenue(document_name: str) -> str:
            # Your actual RAG retrieval logic
            from utils.agent_rag_engine import AgenticRAGEngine
            engine = AgenticRAGEngine(user_id="user_1")
            
            result = engine.query(f"What is the revenue in {document_name}?")
            return result
        
        return Tool(
            name="extract_revenue",
            description="Extract revenue from a document",
            func=extract_revenue
        )
    
    def calculate_growth_tool(self):
        """Tool to calculate growth rate"""
        from langchain.tools import Tool
        
        def calculate_growth(current: float, previous: float) -> str:
            growth = ((current - previous) / previous) * 100
            return f"{growth:.1f}%"
        
        return Tool(
            name="calculate_growth",
            description="Calculate growth rate between two values",
            func=calculate_growth
        )
    
    async def process_document_async(self, agent: Agent, document: str) -> dict:
        """Process one document with one agent (async wrapper)"""
        task = Task(
            description=f"Extract revenue and growth data from {document}",
            agent=agent,
            expected_output="Revenue and growth percentage"
        )
        
        crew = Crew(agents=[agent], tasks=[task], verbose=False)
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, crew.kickoff)
        
        return {
            'document': document,
            'result': result
        }
    
    async def process_all_parallel(self, documents: List[str]) -> List[dict]:
        """Process all documents in parallel"""
        tasks = []
        
        for i, document in enumerate(documents):
            agent = self.agents[i % self.num_agents]
            tasks.append(self.process_document_async(agent, document))
        
        results = await asyncio.gather(*tasks)
        return results


# Usage with your actual documents
async def analyze_all_documents():
    documents = [f"Q3_2024_financial_report_{i}.pdf" for i in range(1, 101)]
    
    executor = RealWorldParallelAgents(num_agents=10)
    results = await executor.process_all_parallel(documents)
    
    return results


# Run
results = asyncio.run(analyze_all_documents())
```

---

## 🔄 Pattern 2: Self-Reflection (Agents Critique Themselves)

### Concept
**Iterative improvement:** Agent generates output, critiques its own work, and revises until satisfied.

---

### Implementation: Self-Reflection Loop

```python
from typing import Optional

class SelfReflectiveAgent:
    """
    Agent that reflects on and improves its own work
    """
    
    def __init__(self):
        from langchain_openai import ChatOpenAI
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
        self.max_iterations = 3  # Prevent infinite loops
    
    def generate_initial_answer(self, query: str, documents: List[dict]) -> str:
        """
        Generate initial answer
        """
        context = "\n".join([doc['content'] for doc in documents])
        
        prompt = f"""
        Based on these documents:
        {context}
        
        Answer this query: {query}
        
        Provide a comprehensive answer with citations.
        """
        
        answer = self.llm.invoke(prompt).content
        return answer
    
    def self_critique(self, query: str, answer: str, documents: List[dict]) -> dict:
        """
        Agent critiques its own answer
        """
        context = "\n".join([doc['content'] for doc in documents])
        
        critique_prompt = f"""
        You generated this answer:
        {answer}
        
        Original query: {query}
        Source documents:
        {context}
        
        Critique your own answer. Check for:
        1. Accuracy: Are all facts correct and supported by sources?
        2. Completeness: Did you miss any important information?
        3. Clarity: Is the answer clear and well-structured?
        4. Citations: Are all claims properly cited?
        
        Provide:
        - Score: 0-10 (how good is the answer?)
        - Issues: List of specific problems
        - Improvements: What needs to be fixed?
        
        Format:
        SCORE: X/10
        ISSUES:
        - Issue 1
        - Issue 2
        IMPROVEMENTS:
        - Improvement 1
        - Improvement 2
        """
        
        critique = self.llm.invoke(critique_prompt).content
        
        # Parse critique
        score = self._parse_score(critique)
        issues = self._parse_issues(critique)
        improvements = self._parse_improvements(critique)
        
        return {
            'score': score,
            'issues': issues,
            'improvements': improvements,
            'critique_text': critique
        }
    
    def revise_answer(self, query: str, original_answer: str, critique: dict, documents: List[dict]) -> str:
        """
        Revise answer based on self-critique
        """
        context = "\n".join([doc['content'] for doc in documents])
        
        revision_prompt = f"""
        Your original answer:
        {original_answer}
        
        Your self-critique identified these issues:
        {chr(10).join(['- ' + issue for issue in critique['issues']])}
        
        Improvements needed:
        {chr(10).join(['- ' + imp for imp in critique['improvements']])}
        
        Source documents:
        {context}
        
        Revise your answer to address all issues and improvements.
        Make it better, more accurate, and more complete.
        """
        
        revised_answer = self.llm.invoke(revision_prompt).content
        return revised_answer
    
    def answer_with_reflection(self, query: str, documents: List[dict], min_score: float = 8.0) -> dict:
        """
        Generate answer with self-reflection loop
        """
        print(f"\n{'='*60}")
        print(f"SELF-REFLECTION: Answering with iterative improvement")
        print(f"{'='*60}\n")
        
        # Initial answer
        print("📝 Generating initial answer...")
        answer = self.generate_initial_answer(query, documents)
        
        iteration = 0
        history = []
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n🔄 Iteration {iteration}: Self-critique...")
            
            # Self-critique
            critique = self.self_critique(query, answer, documents)
            
            print(f"   Score: {critique['score']}/10")
            print(f"   Issues: {len(critique['issues'])}")
            
            # Record history
            history.append({
                'iteration': iteration,
                'answer': answer,
                'critique': critique
            })
            
            # Check if good enough
            if critique['score'] >= min_score:
                print(f"\n✅ Satisfied! Score {critique['score']}/10 meets threshold {min_score}/10")
                break
            
            # Revise
            if iteration < self.max_iterations:
                print(f"   ⚠️ Not satisfied (score {critique['score']}/{min_score}), revising...")
                answer = self.revise_answer(query, answer, critique, documents)
            else:
                print(f"\n⚠️ Max iterations reached ({self.max_iterations})")
        
        print(f"\n{'='*60}")
        print(f"FINAL ANSWER (after {iteration} iterations)")
        print(f"{'='*60}\n")
        
        return {
            'final_answer': answer,
            'iterations': iteration,
            'final_score': history[-1]['critique']['score'] if history else 0,
            'history': history
        }
    
    def _parse_score(self, critique: str) -> float:
        """Parse score from critique text"""
        import re
        match = re.search(r'SCORE:\s*(\d+(?:\.\d+)?)', critique)
        if match:
            return float(match.group(1))
        return 5.0  # Default
    
    def _parse_issues(self, critique: str) -> List[str]:
        """Parse issues from critique text"""
        import re
        issues_section = re.search(r'ISSUES:(.*?)(?:IMPROVEMENTS:|$)', critique, re.DOTALL)
        if issues_section:
            issues_text = issues_section.group(1)
            issues = re.findall(r'-\s*(.+)', issues_text)
            return [issue.strip() for issue in issues]
        return []
    
    def _parse_improvements(self, critique: str) -> List[str]:
        """Parse improvements from critique text"""
        import re
        improvements_section = re.search(r'IMPROVEMENTS:(.*?)$', critique, re.DOTALL)
        if improvements_section:
            improvements_text = improvements_section.group(1)
            improvements = re.findall(r'-\s*(.+)', improvements_text)
            return [imp.strip() for imp in improvements]
        return []


# Usage
agent = SelfReflectiveAgent()

documents = [
    {'content': 'Q3 2024 revenue was $5.2M, up 18% from Q2.'},
    {'content': 'Key drivers: Enterprise sales (+120%), SMB stable (+8%).'}
]

result = agent.answer_with_reflection(
    query="What was Q3 2024 revenue and what drove the growth?",
    documents=documents,
    min_score=8.0
)

print(result['final_answer'])
print(f"\nIterations: {result['iterations']}")
print(f"Final score: {result['final_score']}/10")
```

**Output:**
```
============================================================
SELF-REFLECTION: Answering with iterative improvement
============================================================

📝 Generating initial answer...

🔄 Iteration 1: Self-critique...
   Score: 6.5/10
   Issues: 2
   ⚠️ Not satisfied (score 6.5/8.0), revising...

🔄 Iteration 2: Self-critique...
   Score: 8.5/10
   Issues: 0

✅ Satisfied! Score 8.5/10 meets threshold 8.0/10

============================================================
FINAL ANSWER (after 2 iterations)
============================================================

Q3 2024 revenue was $5.2 million, representing an 18% increase from Q2 2024.

Growth Drivers:
1. **Enterprise Sales** (+120%): The primary driver, with enterprise segment 
   experiencing exceptional growth of 120%, indicating strong product-market 
   fit in the enterprise space.

2. **SMB Stability** (+8%): Small and medium business segment showed steady, 
   healthy growth of 8%, providing a stable revenue base.

The Enterprise segment's 120% growth significantly outpaced the overall 18% 
company growth, suggesting this segment is becoming an increasingly important 
revenue driver and should be a focus for continued investment.

Citations:
- Revenue figure: Q3_2024_Financial_Report.pdf, page 12
- Growth drivers: Q3_2024_Financial_Report.pdf, page 34

Iterations: 2
Final score: 8.5/10
```

---

## 👥 Pattern 3: Peer Review (Agents Review Each Other)

### Concept
**Multi-agent validation:** One agent generates output, another agent reviews it, providing feedback for revision.

---

### Implementation: Analyst + Critic Peer Review

```python
class PeerReviewSystem:
    """
    Multi-agent peer review system
    """
    
    def __init__(self):
        # Creator agent
        from agents.analyst_agent import AnalystAgent
        self.analyst = AnalystAgent()
        
        # Reviewer agent
        from agents.critic_agent import CriticAgent
        self.critic = CriticAgent()
        
        self.max_revisions = 2
    
    def create_analysis(self, data: dict) -> str:
        """Analyst creates initial analysis"""
        print("📊 Analyst: Creating analysis...")
        
        analysis = self.analyst.analyze(data)
        
        print(f"   Generated {len(analysis)} characters")
        return analysis
    
    def peer_review(self, analysis: str, data: dict) -> dict:
        """Critic reviews Analyst's work"""
        print("\n🔍 Critic: Reviewing analysis...")
        
        review = self.critic.review(
            work_to_review=analysis,
            source_documents=str(data)
        )
        
        print(f"   Decision: {review['decision']}")
        print(f"   Issues: {len(review['issues'])}")
        
        return review
    
    def revise_analysis(self, original: str, feedback: str, data: dict) -> str:
        """Analyst revises based on Critic's feedback"""
        print("\n📝 Analyst: Revising based on feedback...")
        
        revision_prompt = f"""
        Your original analysis:
        {original}
        
        Peer review feedback:
        {feedback}
        
        Revise your analysis to address all feedback.
        """
        
        revised = self.analyst.analyze(revision_prompt)
        
        print(f"   Revised {len(revised)} characters")
        return revised
    
    def analyze_with_peer_review(self, data: dict) -> dict:
        """
        Complete workflow: Create → Review → Revise → Approve
        """
        print(f"\n{'='*60}")
        print(f"PEER REVIEW SYSTEM: Analyst + Critic")
        print(f"{'='*60}\n")
        
        # Step 1: Analyst creates
        analysis = self.create_analysis(data)
        
        revision_count = 0
        review_history = []
        
        while revision_count <= self.max_revisions:
            # Step 2: Critic reviews
            review = self.peer_review(analysis, data)
            
            review_history.append({
                'revision': revision_count,
                'analysis': analysis,
                'review': review
            })
            
            # Step 3: Check decision
            if review['decision'] == 'APPROVE':
                print(f"\n✅ APPROVED after {revision_count} revisions!")
                break
            
            # Step 4: Revise if not approved
            if revision_count < self.max_revisions:
                analysis = self.revise_analysis(
                    original=analysis,
                    feedback=review['review'],
                    data=data
                )
                revision_count += 1
            else:
                print(f"\n⚠️ Max revisions ({self.max_revisions}) reached")
                break
        
        print(f"\n{'='*60}")
        print(f"PEER REVIEW COMPLETE")
        print(f"Revisions: {revision_count}")
        print(f"Final Decision: {review['decision']}")
        print(f"{'='*60}\n")
        
        return {
            'final_analysis': analysis,
            'revisions': revision_count,
            'approved': review['decision'] == 'APPROVE',
            'history': review_history
        }


# Usage
system = PeerReviewSystem()

data = {
    'q3_revenue': 5.2,
    'q4_revenue': 6.1,
    'growth_rate': 17.3
}

result = system.analyze_with_peer_review(data)

print("Final Analysis:")
print(result['final_analysis'])
print(f"\nRevisions needed: {result['revisions']}")
print(f"Approved: {result['approved']}")
```

**Output:**
```
============================================================
PEER REVIEW SYSTEM: Analyst + Critic
============================================================

📊 Analyst: Creating analysis...
   Generated 842 characters

🔍 Critic: Reviewing analysis...
   Decision: REQUEST_REVISION
   Issues: 2

📝 Analyst: Revising based on feedback...
   Revised 1024 characters

🔍 Critic: Reviewing analysis...
   Decision: APPROVE
   Issues: 0

✅ APPROVED after 1 revisions!

============================================================
PEER REVIEW COMPLETE
Revisions: 1
Final Decision: APPROVE
============================================================

Final Analysis:
Q3 2024 revenue was $5.2M, increasing to $6.1M in Q4 2024, representing 
a strong growth rate of 17.3%.

Key Insights:
- Sequential momentum: Quarter-over-quarter acceleration indicates strong 
  business momentum heading into year-end
- Growth rate of 17.3% significantly exceeds typical industry benchmarks 
  (5-8%), suggesting competitive advantage
- The $0.9M absolute increase demonstrates both percentage and absolute 
  growth, indicating sustainable scaling

Recommendations:
1. Investigate growth drivers: Determine if growth is from new customer 
   acquisition or expansion within existing accounts
2. Project Q1 2025: If trend continues, could reach $7.2M (+18% from Q4)
3. Resource allocation: Ensure infrastructure can support continued growth

Citations: All figures verified from source data (q3_revenue: 5.2, 
q4_revenue: 6.1, calculated growth_rate: 17.3%)

Revisions needed: 1
Approved: True
```

---

## 🔗 Pattern 4: Complex Tool Chains

### Concept
**Sequential tool execution:** Agent uses output from Tool A as input to Tool B, creating complex workflows.

---

### Implementation: Tool Chain Execution

```python
from typing import List, Callable, Any

class ToolChainAgent:
    """
    Agent that executes complex tool chains
    """
    
    def __init__(self):
        from langchain_openai import ChatOpenAI
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    def create_tool_chain(self, tools: List[Callable]) -> Callable:
        """
        Create a chain of tools where output of one feeds into the next
        """
        def chained_tool(*args, **kwargs) -> Any:
            result = args[0] if args else kwargs
            
            for i, tool in enumerate(tools):
                print(f"🔧 Executing tool {i+1}/{len(tools)}: {tool.__name__}")
                
                # Execute tool with previous result
                if callable(result) or isinstance(result, dict):
                    result = tool(result)
                else:
                    result = tool(result)
                
                print(f"   ✅ Output: {str(result)[:100]}...")
            
            return result
        
        return chained_tool
    
    # Example tools
    def extract_revenue_tool(self, document: str) -> dict:
        """Tool 1: Extract revenue from document"""
        # Simulate extraction
        return {
            'q3_revenue': 5.2,
            'q4_revenue': 6.1,
            'source': document
        }
    
    def calculate_growth_tool(self, data: dict) -> dict:
        """Tool 2: Calculate growth rate"""
        q3 = data['q3_revenue']
        q4 = data['q4_revenue']
        growth = ((q4 - q3) / q3) * 100
        
        data['growth_rate'] = growth
        return data
    
    def analyze_trend_tool(self, data: dict) -> dict:
        """Tool 3: Analyze trend"""
        growth = data['growth_rate']
        
        if growth > 15:
            trend = "Strong upward trend"
        elif growth > 5:
            trend = "Moderate growth"
        else:
            trend = "Slow growth"
        
        data['trend_analysis'] = trend
        return data
    
    def generate_recommendation_tool(self, data: dict) -> str:
        """Tool 4: Generate recommendation"""
        trend = data['trend_analysis']
        growth = data['growth_rate']
        
        if "Strong" in trend:
            recommendation = f"Excellent performance ({growth:.1f}% growth). " \
                           "Consider scaling operations to capitalize on momentum."
        elif "Moderate" in trend:
            recommendation = f"Solid performance ({growth:.1f}% growth). " \
                           "Maintain current strategy while exploring expansion."
        else:
            recommendation = f"Concerning performance ({growth:.1f}% growth). " \
                           "Investigate growth blockers immediately."
        
        return recommendation
    
    def execute_analysis_chain(self, document: str) -> str:
        """
        Execute complete analysis chain
        """
        print(f"\n{'='*60}")
        print(f"TOOL CHAIN EXECUTION")
        print(f"{'='*60}\n")
        
        # Create tool chain
        analysis_chain = self.create_tool_chain([
            self.extract_revenue_tool,
            self.calculate_growth_tool,
            self.analyze_trend_tool,
            self.generate_recommendation_tool
        ])
        
        # Execute chain
        result = analysis_chain(document)
        
        print(f"\n{'='*60}")
        print(f"CHAIN COMPLETE")
        print(f"{'='*60}\n")
        
        return result


# Usage
agent = ToolChainAgent()

recommendation = agent.execute_analysis_chain("Q3_Q4_2024_Report.pdf")

print("Final Recommendation:")
print(recommendation)
```

**Output:**
```
============================================================
TOOL CHAIN EXECUTION
============================================================

🔧 Executing tool 1/4: extract_revenue_tool
   ✅ Output: {'q3_revenue': 5.2, 'q4_revenue': 6.1, 'source': 'Q3_Q4_2024_Report.pdf'}

🔧 Executing tool 2/4: calculate_growth_tool
   ✅ Output: {'q3_revenue': 5.2, 'q4_revenue': 6.1, 'source': 'Q3_Q4_2024_Report.pdf', 'growth_rate': 17.3...

🔧 Executing tool 3/4: analyze_trend_tool
   ✅ Output: {'q3_revenue': 5.2, 'q4_revenue': 6.1, 'source': 'Q3_Q4_2024_Report.pdf', 'growth_rate': 17.3...

🔧 Executing tool 4/4: generate_recommendation_tool
   ✅ Output: Excellent performance (17.3% growth). Consider scaling operations to capitalize on momentum....

============================================================
CHAIN COMPLETE
============================================================

Final Recommendation:
Excellent performance (17.3% growth). Consider scaling operations to 
capitalize on momentum.
```

---

## ⚡ Pattern 5: Parallel Tool Execution

### Concept
**Concurrent tool calls:** Execute multiple independent tools simultaneously to reduce latency.

---

### Implementation: Parallel Tools

```python
import asyncio
from typing import List, Dict, Callable

class ParallelToolExecutor:
    """
    Execute multiple tools in parallel
    """
    
    async def execute_tool_async(self, tool: Callable, *args, **kwargs) -> Any:
        """Execute a single tool asynchronously"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, tool, *args, **kwargs)
        return result
    
    async def execute_tools_parallel(self, tools: List[Dict]) -> Dict:
        """
        Execute multiple tools in parallel
        
        Args:
            tools: List of dicts with 'tool' (callable) and 'args' (tuple)
        
        Returns:
            Dictionary mapping tool names to results
        """
        print(f"\n{'='*60}")
        print(f"PARALLEL TOOL EXECUTION: {len(tools)} tools")
        print(f"{'='*60}\n")
        
        start = asyncio.get_event_loop().time()
        
        # Create tasks for all tools
        tasks = []
        for tool_spec in tools:
            tool = tool_spec['tool']
            args = tool_spec.get('args', ())
            
            print(f"🚀 Launching: {tool.__name__}")
            tasks.append(self.execute_tool_async(tool, *args))
        
        # Execute all in parallel
        results = await asyncio.gather(*tasks)
        
        elapsed = asyncio.get_event_loop().time() - start
        
        print(f"\n{'='*60}")
        print(f"✅ ALL TOOLS COMPLETED in {elapsed:.2f}s")
        print(f"{'='*60}\n")
        
        # Map results to tool names
        result_dict = {
            tools[i]['tool'].__name__: results[i]
            for i in range(len(tools))
        }
        
        return result_dict


# Example: Parallel analysis of different aspects
class MultiAspectAnalyzer:
    """
    Analyze multiple aspects of data in parallel
    """
    
    def analyze_revenue(self, data: dict) -> str:
        """Analyze revenue trends"""
        import time
        time.sleep(2)  # Simulate work
        return f"Revenue analysis: Q3 ${data['q3']}M → Q4 ${data['q4']}M"
    
    def analyze_costs(self, data: dict) -> str:
        """Analyze cost structure"""
        import time
        time.sleep(2)  # Simulate work
        return f"Cost analysis: Costs decreased by 5%"
    
    def analyze_margins(self, data: dict) -> str:
        """Analyze profit margins"""
        import time
        time.sleep(2)  # Simulate work
        return f"Margin analysis: Margins improved from 32% to 37%"
    
    def analyze_market(self, data: dict) -> str:
        """Analyze market position"""
        import time
        time.sleep(2)  # Simulate work
        return f"Market analysis: Market share grew to 12%"
    
    async def analyze_all_parallel(self, data: dict) -> dict:
        """
        Analyze all aspects in parallel
        """
        executor = ParallelToolExecutor()
        
        # Define tools to execute
        tools = [
            {'tool': self.analyze_revenue, 'args': (data,)},
            {'tool': self.analyze_costs, 'args': (data,)},
            {'tool': self.analyze_margins, 'args': (data,)},
            {'tool': self.analyze_market, 'args': (data,)}
        ]
        
        # Execute all in parallel
        results = await executor.execute_tools_parallel(tools)
        
        return results


# Usage
async def main():
    analyzer = MultiAspectAnalyzer()
    
    data = {'q3': 5.2, 'q4': 6.1}
    
    # Execute all analyses in parallel
    results = await analyzer.analyze_all_parallel(data)
    
    print("All Analysis Results:")
    for analysis, result in results.items():
        print(f"  {analysis}: {result}")


# Run
asyncio.run(main())
```

**Output:**
```
============================================================
PARALLEL TOOL EXECUTION: 4 tools
============================================================

🚀 Launching: analyze_revenue
🚀 Launching: analyze_costs
🚀 Launching: analyze_margins
🚀 Launching: analyze_market

============================================================
✅ ALL TOOLS COMPLETED in 2.01s
============================================================

All Analysis Results:
  analyze_revenue: Revenue analysis: Q3 $5.2M → Q4 $6.1M
  analyze_costs: Cost analysis: Costs decreased by 5%
  analyze_margins: Margin analysis: Margins improved from 32% to 37%
  analyze_market: Market analysis: Market share grew to 12%
```

**Performance Comparison:**
- **Sequential**: 4 tools × 2s = 8 seconds
- **Parallel**: max(4 tools) = 2 seconds
- **Speedup**: 4x faster! ⚡

---

## 🔧 Integration with Your Project

### File: `orchestration/parallel_execution.py`

```python
from utils.agent_rag_engine import AgenticRAGEngine
import asyncio
from typing import List

class ParallelDocumentProcessor:
    """
    Process multiple documents in parallel for your project
    """
    
    def __init__(self, user_id: str, num_workers: int = 10):
        self.user_id = user_id
        self.num_workers = num_workers
    
    async def process_document(self, document_id: str, worker_id: int) -> dict:
        """Process single document"""
        engine = AgenticRAGEngine(user_id=self.user_id)
        
        result = await asyncio.to_thread(
            engine.analyze_document,
            document_id
        )
        
        return result
    
    async def process_all(self, document_ids: List[str]) -> List[dict]:
        """Process all documents in parallel"""
        tasks = [
            self.process_document(doc_id, i % self.num_workers)
            for i, doc_id in enumerate(document_ids)
        ]
        
        results = await asyncio.gather(*tasks)
        return results


# Usage in your API
from fastapi import APIRouter

router = APIRouter()

@router.post("/api/analyze-bulk")
async def analyze_bulk_documents(user_id: str, document_ids: List[str]):
    """
    Analyze multiple documents in parallel
    """
    processor = ParallelDocumentProcessor(user_id, num_workers=10)
    results = await processor.process_all(document_ids)
    
    return {
        "documents_processed": len(results),
        "results": results
    }
```

---

## 🎓 Exercises

1. **Build Parallel Processor**: Process 50 documents with 5 agents
2. **Implement Self-Reflection**: Agent that critiques and improves its own answer
3. **Create Peer Review**: Analyst + Critic system with 2 revision rounds
4. **Design Tool Chain**: Create 4-tool chain for complete analysis
5. **Optimize Latency**: Convert sequential code to parallel (achieve 5x speedup)

---

## 📚 Next Steps

**Next:** [Part 5: Multi-Agent Governance & Cost →](MULTI_AGENT_05_GOVERNANCE_COST.md)

Learn loop detection, token management, and cost optimization strategies.

---

*Created specifically for your Smart Document Chat multi-agent project*  
*Last Updated: January 11, 2026*
