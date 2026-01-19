# 🔄 Part 3: Inter-Agent Communication

## Shared State, Hand-offs, and Context Preservation

**Learning Time:** 10-12 hours  
**Difficulty:** Advanced  
**Prerequisites:** Parts 1-2 (Orchestration, Specialized Agents)

---

## 🎯 Learning Objectives

By the end of this guide, you'll be able to:
- ✅ Implement shared state management with LangGraph
- ✅ Design hand-off protocols (when agents pass control)
- ✅ Prevent context loss in multi-agent chains
- ✅ Build a blackboard pattern for async agents
- ✅ Use CrewAI's context and memory features
- ✅ Implement event-driven communication

---

## 📚 The Problem: Context Loss in Multi-Agent Systems

### Current Issue: Agents Don't Remember

```python
# Agent A finds data
researcher_result = researcher.research("What was Q3 revenue?")
# Result: "Q3 2024 revenue was $5.2M"

# Agent B analyzes (but doesn't know about Agent A)
analyst_result = analyst.analyze("Analyze revenue trends")
# ❌ Problem: Analyst doesn't have the $5.2M data!
# Agent B has to re-retrieve the same data (waste of time and money)

# Agent C creates visualization (also doesn't know about A or B)
coder_result = coder.generate_code("Create revenue chart")
# ❌ Problem: Coder doesn't have the data or analysis!
```

**Issues:**
- ❌ Each agent starts from scratch
- ❌ Duplicate work (multiple retrievals)
- ❌ Higher costs (3x the API calls)
- ❌ Lost context (Analyst doesn't see Researcher's citations)
- ❌ Inconsistent data (each agent might retrieve different versions)

---

### Real Example from Your Project

**User Query:** *"Compare Q3 vs Q4 2024 revenue and explain the growth drivers"*

**Without Shared State:**
```
Researcher: Retrieves Q3 data ($5.2M)
→ Returns result, forgets everything

Researcher (again): Retrieves Q4 data ($6.1M)
→ No memory of Q3 data just retrieved!

Analyst: "Compare Q3 vs Q4"
→ ❌ Has to ask Researcher AGAIN for both Q3 and Q4 data
→ Wastes time and money re-retrieving

Coder: "Create comparison chart"
→ ❌ Doesn't have Q3 or Q4 data
→ Has to retrieve AGAIN

Total: 6 retrievals (should be 2!)
Cost: 3x higher
Time: 3x slower
```

**With Shared State:**
```
Researcher: Retrieves Q3 data ($5.2M)
→ Stores in shared state: state['q3_revenue'] = 5.2

Researcher: Retrieves Q4 data ($6.1M)
→ Stores in shared state: state['q4_revenue'] = 6.1

Analyst: Accesses shared state
→ ✅ Already has Q3 and Q4 data!
→ Analyzes: growth = (6.1 - 5.2) / 5.2 = +17.3%
→ Stores in shared state: state['growth_rate'] = 0.173

Coder: Accesses shared state
→ ✅ Has Q3, Q4, and growth_rate
→ Creates chart immediately

Total: 2 retrievals (optimal!)
Cost: 3x cheaper
Time: 3x faster
```

---

## 🗂️ Pattern 1: LangGraph Shared State

### Concept
**Single source of truth:** All agents read from and write to a shared state dictionary that persists across the entire workflow.

### Architecture
```
┌─────────────────────────────────────┐
│       LangGraph Shared State        │
│  {                                  │
│    query: "Compare Q3 vs Q4",      │
│    q3_revenue: 5.2,                │
│    q4_revenue: 6.1,                │
│    growth_rate: 0.173,             │
│    chart_code: "import plotly...", │
│    agent_history: [researcher,     │
│                    analyst, coder] │
│  }                                 │
└─────────────────────────────────────┘
         ↑                 ↑
         │ read/write      │ read/write
         │                 │
    Researcher         Analyst
       Agent            Agent
```

---

### Implementation: LangGraph State Management

```python
from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
import operator

# Define the shared state structure
class MultiAgentState(TypedDict):
    """
    Shared state accessible to all agents in the workflow
    """
    # User input
    query: str
    
    # Research results
    retrieved_documents: List[dict]
    citations: List[str]
    
    # Analysis results
    key_metrics: dict
    insights: List[str]
    
    # Code generation
    visualizations: List[str]
    
    # Quality control
    quality_score: float
    issues_found: List[str]
    
    # Workflow tracking
    agent_history: Annotated[List[str], operator.add]  # Append-only list
    current_step: str
    
    # Final output
    final_answer: Optional[str]


class StatefulMultiAgentSystem:
    """
    Multi-agent system with LangGraph state management
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        
        # Initialize agents (from Part 2)
        from agents.researcher_agent import ResearcherAgent
        from agents.analyst_agent import AnalystAgent
        from agents.coder_agent import CoderAgent
        from agents.critic_agent import CriticAgent
        
        self.researcher = ResearcherAgent(user_id)
        self.analyst = AnalystAgent()
        self.coder = CoderAgent()
        self.critic = CriticAgent()
        
        # Build the state graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow with shared state
        """
        # Define node functions
        def research_node(state: MultiAgentState) -> MultiAgentState:
            """Researcher agent retrieves documents"""
            print(f"\n🔍 Researcher: Processing query...")
            
            # Access query from state
            query = state['query']
            
            # Perform research
            results = self.researcher.research(query)
            
            # Update shared state
            state['retrieved_documents'] = results.get('documents', [])
            state['citations'] = results.get('citations', [])
            state['agent_history'].append('researcher')
            state['current_step'] = 'research_complete'
            
            print(f"   Found {len(state['retrieved_documents'])} documents")
            return state
        
        def analysis_node(state: MultiAgentState) -> MultiAgentState:
            """Analyst agent analyzes the data"""
            print(f"\n📊 Analyst: Analyzing data...")
            
            # Access data from state (no need to re-retrieve!)
            documents = state['retrieved_documents']
            
            # Perform analysis
            analysis = self.analyst.analyze(documents)
            
            # Update shared state
            state['key_metrics'] = analysis.get('metrics', {})
            state['insights'] = analysis.get('insights', [])
            state['agent_history'].append('analyst')
            state['current_step'] = 'analysis_complete'
            
            print(f"   Generated {len(state['insights'])} insights")
            return state
        
        def coding_node(state: MultiAgentState) -> MultiAgentState:
            """Coder agent generates visualizations"""
            print(f"\n💻 Coder: Generating visualizations...")
            
            # Check if visualization needed
            if "visualiz" not in state['query'].lower() and "chart" not in state['query'].lower():
                print("   No visualization requested, skipping")
                state['agent_history'].append('coder_skipped')
                return state
            
            # Access data from state
            metrics = state['key_metrics']
            
            # Generate code
            code = self.coder.generate_visualization(metrics)
            
            # Update shared state
            state['visualizations'] = [code]
            state['agent_history'].append('coder')
            state['current_step'] = 'coding_complete'
            
            print(f"   Created {len(state['visualizations'])} visualizations")
            return state
        
        def critic_node(state: MultiAgentState) -> MultiAgentState:
            """Critic agent reviews the work"""
            print(f"\n🔍 Critic: Reviewing quality...")
            
            # Access all previous work from state
            work_to_review = {
                'documents': state['retrieved_documents'],
                'metrics': state['key_metrics'],
                'insights': state['insights']
            }
            
            # Perform review
            review = self.critic.review(work_to_review)
            
            # Update shared state
            state['quality_score'] = review['score']
            state['issues_found'] = review['issues']
            state['agent_history'].append('critic')
            state['current_step'] = 'review_complete'
            
            print(f"   Quality score: {state['quality_score']}/10")
            return state
        
        def synthesis_node(state: MultiAgentState) -> MultiAgentState:
            """Synthesize final answer"""
            print(f"\n🧩 Synthesizer: Creating final answer...")
            
            # Access all data from state
            final_answer = f"""
## Answer

Based on the analysis of {len(state['retrieved_documents'])} documents:

## Key Findings
{chr(10).join(['- ' + insight for insight in state['insights']])}

## Metrics
{chr(10).join([f'- {k}: {v}' for k, v in state['key_metrics'].items()])}

{"## Visualizations" if state.get('visualizations') else ""}
{chr(10).join(state.get('visualizations', []))}

## Quality Assurance
Quality Score: {state['quality_score']}/10
{"⚠️ Issues: " + ", ".join(state['issues_found']) if state['issues_found'] else "✅ All checks passed"}
"""
            
            state['final_answer'] = final_answer
            state['current_step'] = 'complete'
            
            return state
        
        # Build the graph
        workflow = StateGraph(MultiAgentState)
        
        # Add nodes
        workflow.add_node("research", research_node)
        workflow.add_node("analysis", analysis_node)
        workflow.add_node("coding", coding_node)
        workflow.add_node("critic", critic_node)
        workflow.add_node("synthesis", synthesis_node)
        
        # Define the flow
        workflow.set_entry_point("research")
        workflow.add_edge("research", "analysis")
        workflow.add_edge("analysis", "coding")
        workflow.add_edge("coding", "critic")
        workflow.add_edge("critic", "synthesis")
        workflow.add_edge("synthesis", END)
        
        return workflow.compile()
    
    def query(self, user_query: str) -> dict:
        """
        Execute the multi-agent workflow with shared state
        """
        # Initialize state
        initial_state = {
            'query': user_query,
            'retrieved_documents': [],
            'citations': [],
            'key_metrics': {},
            'insights': [],
            'visualizations': [],
            'quality_score': 0.0,
            'issues_found': [],
            'agent_history': [],
            'current_step': 'started',
            'final_answer': None
        }
        
        # Run workflow
        print(f"\n{'='*60}")
        print(f"MULTI-AGENT WORKFLOW WITH SHARED STATE")
        print(f"Query: {user_query}")
        print(f"{'='*60}")
        
        final_state = self.workflow.invoke(initial_state)
        
        print(f"\n{'='*60}")
        print(f"WORKFLOW COMPLETE")
        print(f"Agents executed: {' → '.join(final_state['agent_history'])}")
        print(f"{'='*60}\n")
        
        return {
            'answer': final_state['final_answer'],
            'state': final_state
        }


# Usage
system = StatefulMultiAgentSystem(user_id="user_1")

result = system.query("Compare Q3 vs Q4 2024 revenue and create visualization")

print(result['answer'])

# Inspect shared state
print("\n📊 Final State:")
print(f"Documents retrieved: {len(result['state']['retrieved_documents'])}")
print(f"Insights generated: {len(result['state']['insights'])}")
print(f"Quality score: {result['state']['quality_score']}")
```

**Output:**
```
============================================================
MULTI-AGENT WORKFLOW WITH SHARED STATE
Query: Compare Q3 vs Q4 2024 revenue and create visualization
============================================================

🔍 Researcher: Processing query...
   Found 2 documents

📊 Analyst: Analyzing data...
   Generated 4 insights

💻 Coder: Generating visualizations...
   Created 1 visualizations

🔍 Critic: Reviewing quality...
   Quality score: 9/10

🧩 Synthesizer: Creating final answer...

============================================================
WORKFLOW COMPLETE
Agents executed: researcher → analyst → coder → critic
============================================================

## Answer

Based on the analysis of 2 documents:

## Key Findings
- Q3 2024 revenue: $5.2M
- Q4 2024 revenue: $6.1M
- Growth: +17.3% (+$0.9M)
- Q4 marks strongest quarter in company history

## Metrics
- q3_revenue: $5.2M
- q4_revenue: $6.1M
- growth_rate: 17.3%
- growth_amount: $0.9M

## Visualizations
[Python code for interactive Plotly chart]

## Quality Assurance
Quality Score: 9/10
✅ All checks passed

📊 Final State:
Documents retrieved: 2
Insights generated: 4
Quality score: 9.0
```

---

## 🤝 Pattern 2: Hand-off Protocols

### Concept
**Explicit transitions:** Agents explicitly decide when to hand off control to the next agent, with conditions and context.

### Implementation: Conditional Hand-offs

```python
from typing import Literal

class HandoffProtocol:
    """
    Manages agent-to-agent hand-offs with conditions
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    def researcher_handoff(self, state: MultiAgentState) -> Literal["analyst", "end", "retry"]:
        """
        Researcher decides what to do next
        
        Returns:
            - "analyst": Hand off to analyst (documents found)
            - "end": End workflow (no documents found)
            - "retry": Try research again with different query
        """
        docs = state['retrieved_documents']
        
        # Check if we found anything
        if len(docs) == 0:
            print("⚠️ Researcher: No documents found, ending workflow")
            return "end"
        
        # Check if we have enough information
        elif len(docs) < 3:
            print("⚠️ Researcher: Only found {len(docs)} documents, might need retry")
            
            # Ask LLM if this is sufficient
            decision_prompt = f"""
            Query: {state['query']}
            Documents found: {len(docs)}
            
            Is this sufficient to answer the query?
            Respond with: SUFFICIENT or INSUFFICIENT
            """
            
            decision = self.llm.invoke(decision_prompt).content.strip()
            
            if "SUFFICIENT" in decision:
                print("✅ Researcher: Sufficient information, handing off to Analyst")
                return "analyst"
            else:
                print("🔄 Researcher: Insufficient information, retrying with broader query")
                return "retry"
        
        else:
            print(f"✅ Researcher: Found {len(docs)} documents, handing off to Analyst")
            return "analyst"
    
    def analyst_handoff(self, state: MultiAgentState) -> Literal["coder", "synthesis", "researcher"]:
        """
        Analyst decides what to do next
        
        Returns:
            - "coder": Need visualization
            - "synthesis": Skip coding, go straight to synthesis
            - "researcher": Need more data
        """
        query = state['query'].lower()
        metrics = state['key_metrics']
        
        # Check if visualization requested
        if "visualiz" in query or "chart" in query or "graph" in query:
            print("✅ Analyst: Visualization requested, handing off to Coder")
            return "coder"
        
        # Check if we have enough metrics
        elif len(metrics) == 0:
            print("⚠️ Analyst: No metrics calculated, need more data from Researcher")
            return "researcher"
        
        else:
            print("✅ Analyst: Analysis complete, skipping Coder, going to Synthesis")
            return "synthesis"
    
    def coder_handoff(self, state: MultiAgentState) -> Literal["critic", "analyst"]:
        """
        Coder decides what to do next
        
        Returns:
            - "critic": Code generated successfully
            - "analyst": Need different data format
        """
        if len(state['visualizations']) > 0:
            print("✅ Coder: Visualization created, handing off to Critic")
            return "critic"
        else:
            print("⚠️ Coder: Couldn't create visualization, asking Analyst for different format")
            return "analyst"
    
    def critic_handoff(self, state: MultiAgentState) -> Literal["synthesis", "researcher", "analyst"]:
        """
        Critic decides what to do next based on quality
        
        Returns:
            - "synthesis": Quality acceptable, proceed to final answer
            - "researcher": Data quality issues, need re-retrieval
            - "analyst": Analysis has errors, need revision
        """
        quality_score = state['quality_score']
        issues = state['issues_found']
        
        if quality_score >= 8.0:
            print(f"✅ Critic: Quality excellent ({quality_score}/10), proceeding to Synthesis")
            return "synthesis"
        
        elif any("citation" in issue.lower() or "source" in issue.lower() for issue in issues):
            print(f"⚠️ Critic: Citation issues found ({quality_score}/10), sending back to Researcher")
            return "researcher"
        
        elif any("calculation" in issue.lower() or "metric" in issue.lower() for issue in issues):
            print(f"⚠️ Critic: Analysis errors found ({quality_score}/10), sending back to Analyst")
            return "analyst"
        
        else:
            print(f"✅ Critic: Acceptable quality ({quality_score}/10), proceeding to Synthesis")
            return "synthesis"


# Integrate hand-offs into workflow
def build_workflow_with_handoffs():
    """
    Build workflow with conditional hand-offs
    """
    handoff = HandoffProtocol()
    workflow = StateGraph(MultiAgentState)
    
    # Add all nodes (same as before)
    workflow.add_node("research", research_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("coding", coding_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("synthesis", synthesis_node)
    
    # Entry point
    workflow.set_entry_point("research")
    
    # Conditional edges based on hand-off decisions
    workflow.add_conditional_edges(
        "research",
        handoff.researcher_handoff,
        {
            "analyst": "analysis",
            "end": END,
            "retry": "research"  # Loop back
        }
    )
    
    workflow.add_conditional_edges(
        "analysis",
        handoff.analyst_handoff,
        {
            "coder": "coding",
            "synthesis": "synthesis",
            "researcher": "research"
        }
    )
    
    workflow.add_conditional_edges(
        "coding",
        handoff.coder_handoff,
        {
            "critic": "critic",
            "analyst": "analysis"
        }
    )
    
    workflow.add_conditional_edges(
        "critic",
        handoff.critic_handoff,
        {
            "synthesis": "synthesis",
            "researcher": "research",
            "analyst": "analysis"
        }
    )
    
    workflow.add_edge("synthesis", END)
    
    return workflow.compile()
```

**Benefits:**
- ✅ Self-correcting (Critic can send work back for revision)
- ✅ Adaptive (skips Coder if no visualization needed)
- ✅ Efficient (doesn't waste time on unnecessary steps)

---

## 📋 Pattern 3: Blackboard Pattern (Async Agents)

### Concept
**Shared workspace:** Agents work asynchronously, reading from and writing to a central "blackboard" without direct communication.

### Use Case
Multiple agents processing documents in parallel, each contributing findings to a shared board.

---

### Implementation: Async Blackboard

```python
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import threading

class Blackboard:
    """
    Shared workspace for async multi-agent collaboration
    """
    
    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()
        self._subscribers = {}  # Agent callbacks
    
    def write(self, key: str, value: Any, agent_id: str):
        """
        Write data to blackboard
        """
        with self._lock:
            timestamp = datetime.now().isoformat()
            
            self._data[key] = {
                'value': value,
                'agent_id': agent_id,
                'timestamp': timestamp
            }
            
            print(f"📝 [{agent_id}] wrote to blackboard: {key}")
            
            # Notify subscribers
            self._notify_subscribers(key, value)
    
    def read(self, key: str) -> Any:
        """
        Read data from blackboard
        """
        with self._lock:
            if key in self._data:
                return self._data[key]['value']
            return None
    
    def read_all(self) -> Dict:
        """
        Read all data from blackboard
        """
        with self._lock:
            return {k: v['value'] for k, v in self._data.items()}
    
    def subscribe(self, key: str, callback, agent_id: str):
        """
        Subscribe to changes on a specific key
        """
        if key not in self._subscribers:
            self._subscribers[key] = []
        
        self._subscribers[key].append({
            'agent_id': agent_id,
            'callback': callback
        })
    
    def _notify_subscribers(self, key: str, value: Any):
        """
        Notify all subscribers of a key change
        """
        if key in self._subscribers:
            for subscriber in self._subscribers[key]:
                subscriber['callback'](value)


class AsyncWorkerAgent:
    """
    Worker agent that operates asynchronously using blackboard
    """
    
    def __init__(self, agent_id: str, blackboard: Blackboard):
        self.agent_id = agent_id
        self.blackboard = blackboard
    
    async def process_document(self, document: dict):
        """
        Process a document and write results to blackboard
        """
        print(f"🔄 [{self.agent_id}] Processing {document['name']}...")
        
        # Simulate processing
        await asyncio.sleep(2)  # Simulate work
        
        # Extract revenue (simulated)
        revenue = f"${document['id'] * 1.2}M"
        
        # Write to blackboard
        self.blackboard.write(
            key=f"document_{document['id']}_revenue",
            value=revenue,
            agent_id=self.agent_id
        )
        
        print(f"✅ [{self.agent_id}] Completed {document['name']}")
        
        return revenue


class BlackboardOrchestrator:
    """
    Orchestrates async agents using blackboard pattern
    """
    
    def __init__(self, num_workers: int = 5):
        self.blackboard = Blackboard()
        self.num_workers = num_workers
        self.workers = [
            AsyncWorkerAgent(f"worker_{i}", self.blackboard)
            for i in range(num_workers)
        ]
    
    async def process_documents_parallel(self, documents: List[dict]):
        """
        Process documents in parallel using blackboard
        """
        print(f"\n{'='*60}")
        print(f"BLACKBOARD PATTERN: Processing {len(documents)} documents")
        print(f"Workers: {self.num_workers}")
        print(f"{'='*60}\n")
        
        # Distribute documents to workers
        tasks = []
        for i, document in enumerate(documents):
            worker = self.workers[i % self.num_workers]
            tasks.append(worker.process_document(document))
        
        # Execute all in parallel
        await asyncio.gather(*tasks)
        
        # Read all results from blackboard
        results = self.blackboard.read_all()
        
        print(f"\n{'='*60}")
        print(f"BLACKBOARD FINAL STATE:")
        print(f"{'='*60}")
        for key, value in results.items():
            print(f"{key}: {value}")
        
        return results


# Usage
async def main():
    # Simulate 20 documents
    documents = [
        {'id': i, 'name': f'financial_report_{i}.pdf'}
        for i in range(1, 21)
    ]
    
    # Create orchestrator with 5 workers
    orchestrator = BlackboardOrchestrator(num_workers=5)
    
    # Process in parallel
    results = await orchestrator.process_documents_parallel(documents)
    
    print(f"\n✅ Processed {len(results)} documents")


# Run
asyncio.run(main())
```

**Output:**
```
============================================================
BLACKBOARD PATTERN: Processing 20 documents
Workers: 5
============================================================

🔄 [worker_0] Processing financial_report_1.pdf...
🔄 [worker_1] Processing financial_report_2.pdf...
🔄 [worker_2] Processing financial_report_3.pdf...
🔄 [worker_3] Processing financial_report_4.pdf...
🔄 [worker_4] Processing financial_report_5.pdf...
🔄 [worker_0] Processing financial_report_6.pdf...
...

📝 [worker_0] wrote to blackboard: document_1_revenue
✅ [worker_0] Completed financial_report_1.pdf
📝 [worker_1] wrote to blackboard: document_2_revenue
✅ [worker_1] Completed financial_report_2.pdf
...

============================================================
BLACKBOARD FINAL STATE:
============================================================
document_1_revenue: $1.2M
document_2_revenue: $2.4M
document_3_revenue: $3.6M
...
document_20_revenue: $24.0M

✅ Processed 20 documents
```

---

## 🧠 Pattern 4: CrewAI Context & Memory

### Concept
**Built-in context passing:** CrewAI provides native support for passing context between tasks and maintaining memory.

---

### Implementation: CrewAI Sequential Tasks with Context

```python
from crewai import Agent, Task, Crew, Process
from crewai.tasks.task_output import TaskOutput

class CrewAIContextSystem:
    """
    Multi-agent system using CrewAI's context features
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        
        # Create agents
        self.researcher = Agent(
            role="Research Analyst",
            goal="Find and extract information from documents",
            backstory="Expert at document research",
            verbose=True
        )
        
        self.analyst = Agent(
            role="Data Analyst",
            goal="Analyze data and provide insights",
            backstory="Expert at data analysis",
            verbose=True
        )
        
        self.coder = Agent(
            role="Visualization Specialist",
            goal="Create visualizations",
            backstory="Expert at data visualization",
            verbose=True
        )
    
    def query(self, user_query: str):
        """
        Execute query with context passing
        """
        # Task 1: Research
        research_task = Task(
            description=f"Research the following query: {user_query}",
            agent=self.researcher,
            expected_output="Document findings with citations"
        )
        
        # Task 2: Analysis (gets Task 1 output as context)
        analysis_task = Task(
            description="""
            Analyze the research findings and provide insights.
            
            Use the research findings from the previous task.
            """,
            agent=self.analyst,
            expected_output="Analysis with key metrics and insights",
            context=[research_task]  # ✅ Gets output from research_task
        )
        
        # Task 3: Visualization (gets Task 1 and 2 outputs as context)
        visualization_task = Task(
            description="""
            Create a visualization based on the analysis.
            
            Use the research findings and analysis from previous tasks.
            """,
            agent=self.coder,
            expected_output="Python code for visualization",
            context=[research_task, analysis_task]  # ✅ Gets both previous outputs
        )
        
        # Create crew
        crew = Crew(
            agents=[self.researcher, self.analyst, self.coder],
            tasks=[research_task, analysis_task, visualization_task],
            process=Process.sequential,  # Sequential with context passing
            verbose=True
        )
        
        # Execute
        result = crew.kickoff()
        
        return result


# Usage
system = CrewAIContextSystem(user_id="user_1")

result = system.query("Compare Q3 vs Q4 2024 revenue")

print(result)
```

**Benefits:**
- ✅ Automatic context passing (no manual state management)
- ✅ Task dependencies handled by CrewAI
- ✅ Memory persists across tasks
- ✅ Simple API (just use `context=[task1, task2]`)

---

### CrewAI Memory Features

```python
from crewai import Agent, Task, Crew
from crewai.memory import ConversationMemory, EntityMemory

class CrewAIMemorySystem:
    """
    Using CrewAI's memory features
    """
    
    def __init__(self):
        # Enable memory
        self.crew = Crew(
            agents=[...],
            tasks=[...],
            memory=True,  # ✅ Enable memory
            verbose=True
        )
    
    def query_with_memory(self, query: str):
        """
        Query with conversation memory
        """
        # First query
        result1 = self.crew.kickoff(inputs={'query': "What was Q3 revenue?"})
        # CrewAI remembers: "Q3 revenue was $5.2M"
        
        # Second query (uses memory from first query)
        result2 = self.crew.kickoff(inputs={'query': "How does that compare to Q2?"})
        # ✅ Agent knows "that" refers to $5.2M from previous query
        
        return result2


# Advanced: Custom memory
from crewai.memory import Memory

class CustomDocumentMemory(Memory):
    """
    Custom memory for document context
    """
    
    def __init__(self):
        super().__init__()
        self.document_cache = {}
    
    def save(self, key: str, value: Any):
        """Save to memory"""
        self.document_cache[key] = value
    
    def load(self, key: str) -> Any:
        """Load from memory"""
        return self.document_cache.get(key)
    
    def clear(self):
        """Clear memory"""
        self.document_cache = {}
```

---

## 🎯 Pattern Comparison

| Pattern | Complexity | Control | Best For |
|---------|-----------|---------|----------|
| **LangGraph State** | ⭐⭐⭐ High | 🎚️ Full control | Complex workflows, custom logic |
| **Hand-off Protocols** | ⭐⭐ Medium | 🎚️ Conditional flow | Self-correcting systems |
| **Blackboard** | ⭐⭐⭐ High | 🎚️ Async coordination | Parallel processing |
| **CrewAI Context** | ⭐ Easy | 🎚️ Simple | Quick prototyping, sequential tasks |

---

## 💡 Pro Tips: Preventing Context Loss

### Tip #1: Always Log State Changes

```python
def log_state_change(state: MultiAgentState, agent_name: str):
    """
    Log every state change for debugging
    """
    print(f"""
    ┌─ State Change: {agent_name} ─────────────
    │ Documents: {len(state['retrieved_documents'])}
    │ Metrics: {len(state['key_metrics'])}
    │ Insights: {len(state['insights'])}
    │ Quality: {state['quality_score']}/10
    │ History: {' → '.join(state['agent_history'])}
    └────────────────────────────────────────────
    """)
```

### Tip #2: Validate Hand-offs

```python
def validate_handoff(from_agent: str, to_agent: str, state: MultiAgentState):
    """
    Ensure necessary data is available before hand-off
    """
    if to_agent == "analyst" and len(state['retrieved_documents']) == 0:
        raise ValueError(f"Cannot hand off to Analyst: No documents retrieved")
    
    if to_agent == "coder" and len(state['key_metrics']) == 0:
        raise ValueError(f"Cannot hand off to Coder: No metrics available")
    
    print(f"✅ Hand-off validated: {from_agent} → {to_agent}")
```

### Tip #3: Implement State Snapshots

```python
class StateSnapshot:
    """
    Save state at each step for debugging and rollback
    """
    
    def __init__(self):
        self.snapshots = []
    
    def save(self, state: MultiAgentState, step_name: str):
        """Save state snapshot"""
        import copy
        self.snapshots.append({
            'step': step_name,
            'state': copy.deepcopy(state),
            'timestamp': datetime.now()
        })
    
    def rollback(self, steps_back: int = 1) -> MultiAgentState:
        """Rollback to previous state"""
        if len(self.snapshots) >= steps_back:
            return self.snapshots[-(steps_back + 1)]['state']
        return None
```

---

## 🔧 Integration with Your Project

### File: `orchestration/state_management.py`

```python
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from agents.researcher_agent import ResearcherAgent
from agents.analyst_agent import AnalystAgent
from agents.coder_agent import CoderAgent
from agents.critic_agent import CriticAgent

class DocumentAnalysisState(TypedDict):
    """State for your document analysis project"""
    query: str
    user_id: str
    documents: List[dict]
    analysis: dict
    visualizations: List[str]
    quality_score: float
    final_answer: str
    agent_history: List[str]


def create_stateful_workflow(user_id: str):
    """
    Create LangGraph workflow for your project
    """
    # Initialize agents
    researcher = ResearcherAgent(user_id)
    analyst = AnalystAgent()
    coder = CoderAgent()
    critic = CriticAgent()
    
    # Build workflow
    workflow = StateGraph(DocumentAnalysisState)
    
    # Add nodes
    workflow.add_node("research", lambda s: researcher.process(s))
    workflow.add_node("analysis", lambda s: analyst.process(s))
    workflow.add_node("coding", lambda s: coder.process(s))
    workflow.add_node("critic", lambda s: critic.process(s))
    
    # Define flow
    workflow.set_entry_point("research")
    workflow.add_edge("research", "analysis")
    workflow.add_edge("analysis", "coding")
    workflow.add_edge("coding", "critic")
    workflow.add_edge("critic", END)
    
    return workflow.compile()
```

---

## 🎓 Exercises

1. **Implement LangGraph State**: Build a 3-agent workflow with shared state
2. **Add Hand-off Conditions**: Implement conditional routing based on state
3. **Build Blackboard**: Create async processing for 50 documents
4. **Use CrewAI Context**: Chain 3 tasks with context passing
5. **Debug Context Loss**: Find and fix a context loss bug

---

## 📚 Next Steps

**Next:** [Part 4: Advanced Tool Use & Reasoning →](MULTI_AGENT_04_TOOLS_REASONING.md)

Learn parallel execution, self-reflection, and peer review patterns.

---

*Created specifically for your Smart Document Chat multi-agent project*  
*Last Updated: January 11, 2026*
