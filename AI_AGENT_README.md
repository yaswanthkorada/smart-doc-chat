# AI Agent Learning Project - Complete Guide

## 🎯 What's Included

This learning project now has **COMPLETE** LangChain and LangGraph implementations with step-by-step code!

### Files:
1. **AI_AGENT_LEARNING_PROJECT.py** - Main tutorial (all agent types)
2. **LANGGRAPH_EXAMPLES.py** - **NEW!** Complete LangGraph workflows
3. **LANGCHAIN_LANGGRAPH_GUIDE.md** - Framework comparison guide

## 📦 Installation

```bash
# Basic requirements
pip install langchain langchain-openai langchain-hub openai

# LangGraph (for advanced workflows)
pip install langgraph

# CrewAI (for multi-agent teams)
pip install crewai crewai-tools

# Optional
pip install chromadb faiss-cpu
```

## 🚀 Running the Code

### Main Tutorial (10 Demos)
```bash
python AI_AGENT_LEARNING_PROJECT.py
```

**Demos included:**
1. ✅ LLM vs Agent comparison
2. ✅ Simple agent with tools
3. ✅ ReAct agent (reasoning + acting)
4. ✅ Agent with memory
5. ✅ **LangChain agents** (basic + conversational)
6. ✅ **LangGraph info** (see separate file)
7. ✅ CrewAI multi-agent system
8. ✅ Agentic AI (autonomous)
9. ✅ Multi-Agentic patterns (hierarchical, debate, consensus)
10. ✅ Agent evaluation

### LangGraph Examples (3 Complete Workflows)
```bash
python LANGGRAPH_EXAMPLES.py
```

**Examples:**
1. ✅ **Simple Agent** with state management
   - Tool calling with state
   - Conditional routing (continue or end)
   
2. ✅ **Multi-Step Workflow** with conditional routing
   - Classify query (simple vs complex)
   - Simple path: direct answer
   - Complex path: research → analyze → write
   
3. ✅ **Multi-Agent Supervisor** system
   - Supervisor coordinates specialized agents
   - Researcher → Analyst → Writer
   - Dynamic task routing based on state

## 🎓 Learning Path

### Beginner
Start with: `AI_AGENT_LEARNING_PROJECT.py` Demos 1-4
- Understand agent basics
- Learn tool creation
- See ReAct pattern

### Intermediate
Continue with: Demos 5-7
- LangChain agents (framework basics)
- CrewAI multi-agent teams
- Read `LANGGRAPH_EXAMPLES.py` code

### Advanced  
Master: Demos 8-10 + Run LangGraph Examples
- Agentic AI (autonomous agents)
- Multi-agentic patterns
- Run `LANGGRAPH_EXAMPLES.py`
- Understand state management, conditional routing, cycles

## 🔑 Key Concepts

### LangChain vs LangGraph

**Use LangChain when:**
- Simple tool-based agents
- Quick prototypes
- Standard query → response pattern

**Use LangGraph when:**
- Multi-step workflows with decision points
- Need state management between steps
- Conditional routing required
- Iterative refinement (cycles/loops)
- Human-in-the-loop needed
- Complex multi-agent orchestration

### LangGraph Key Features

1. **State Management** - TypedDict passed between nodes
2. **Conditional Routing** - Dynamic decision-making
3. **Cycles** - Iterative refinement loops
4. **Visualization** - See your workflow as a graph
5. **Human-in-Loop** - Pause for approval

## 📊 Framework Comparison

| Feature | LangChain | LangGraph | CrewAI |
|---------|-----------|-----------|--------|
| Best For | Simple agents | Complex workflows | Multi-agent teams |
| State Management | Limited | ✅ Excellent | Limited |
| Conditional Flow | ❌ No | ✅ Yes | ❌ No |
| Cycles/Loops | ❌ No | ✅ Yes | ❌ No |
| Multi-Agent | Basic | Advanced | ✅ Excellent |
| Learning Curve | Easy | Moderate | Easy |
| Visualization | ❌ No | ✅ Yes | ❌ No |

## 💡 Code Examples

### LangChain (Simple Agent)
```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

tools = [Tool(name="Calculator", func=eval, description="Math tool")]
llm = ChatOpenAI(model="gpt-3.5-turbo")
agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

result = executor.invoke({"input": "What is 25 * 4?"})
```

### LangGraph (Stateful Workflow)
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class State(TypedDict):
    messages: list
    step: str

def agent_node(state): # process state
def tool_node(state): # execute tools
def router(state): # decide next step

workflow = StateGraph(State)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.add_conditional_edges("agent", router, {"tools": "tools", "end": END})
workflow.add_edge("tools", "agent")

app = workflow.compile()
result = app.invoke({"messages": [...], "step": "start"})
```

## 🎯 What You'll Learn

### Agent Fundamentals
- Difference between LLM and Agent
- Perception → Reasoning → Action loop
- Tool creation and usage

### Frameworks (NEW!)
- **LangChain**: Quick agent setup with tools
- **LangGraph**: Complex stateful workflows
  - State management
  - Conditional routing
  - Multi-step pipelines
  - Supervisor patterns
- **CrewAI**: Role-based collaboration

### Advanced Patterns
- Agentic AI (autonomous, self-reflecting)
- Multi-Agentic (hierarchical, debate, consensus)
- Agent evaluation metrics

## 📚 Next Steps

1. **Run the code**: Start with main tutorial, then LangGraph examples
2. **Experiment**: Modify workflows, add new tools, change routing logic
3. **Build**: Create your own agent for a specific use case
4. **Production**: Add error handling, monitoring, rate limiting

## 🔧 Troubleshooting

### Import Errors
```bash
# LangChain
pip install langchain langchain-openai langchain-hub

# LangGraph
pip install langgraph

# Hub access
pip install langchainhub
```

### API Key
```python
import os
os.environ["OPENAI_API_KEY"] = "your-key-here"
```

## 🌟 Highlights

✅ **10 complete demos** in main tutorial
✅ **3 working LangGraph examples** with full code
✅ **All code is runnable** - not just concepts!
✅ **Step-by-step explanations** with comments
✅ **Multiple techniques** for each concept
✅ **Production-ready patterns** you can use immediately

## 📖 Resources

- **LangChain Docs**: https://python.langchain.com/docs/
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **CrewAI Docs**: https://docs.crewai.com/

---

**Ready to build AI agents?** Start with `python AI_AGENT_LEARNING_PROJECT.py` and work through all 10 demos!
