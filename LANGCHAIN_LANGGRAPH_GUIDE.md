# LangChain & LangGraph Complete Guide

## Installation

```bash
# LangChain
pip install langchain langchain-openai langchain-hub

# LangGraph
pip install langgraph

# Optional tools
pip install tavily-python  # For search
```

## Running the Demos

The AI_AGENT_LEARNING_PROJECT.py file now includes:

### Demo 5A: LangChain Agents
- Basic ReAct agent with tools
- Conversational agent with memory

### Demo 5B: LangGraph Workflows  
- Simple agent with state management
- Multi-step conditional workflows
- Multi-agent supervisor system

### Demo 5C: CrewAI Multi-Agent
- Role-based agents
- Sequential task execution

### Demo 5D: Agentic AI
- Autonomous goal decomposition
- Self-reflection and correction

### Demo 5E: Multi-Agentic Patterns
- Hierarchical (manager + workers)
- Debate (multiple perspectives)
- Consensus (voting)

## LangChain vs LangGraph

### Use LangChain when:
- Simple tool-based agents
- Quick prototypes
- Standard patterns

### Use LangGraph when:
- Complex multi-step workflows
- Conditional routing needed
- State management required
- Cycles/loops needed
- Human-in-the-loop
- Need to visualize workflow

## Key LangGraph Concepts

1. **State**: Shared data structure
2. **Nodes**: Processing functions
3. **Edges**: Connections between nodes
4. **Conditional Edges**: Dynamic routing
5. **Cycles**: Iterative refinement

## Examples in the Project

All code is working and runnable! Just need OpenAI API key:

```python
import os
os.environ["OPENAI_API_KEY"] = "your-key-here"

python AI_AGENT_LEARNING_PROJECT.py
```

Navigate through the demos to see each framework in action!
