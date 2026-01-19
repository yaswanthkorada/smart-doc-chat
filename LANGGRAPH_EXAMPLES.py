"""
=============================================================================
LANGGRAPH COMPLETE EXAMPLES - STEP BY STEP
=============================================================================

LangGraph enables:
- Stateful multi-step workflows
- Conditional routing
- Cycles and loops
- Human-in-the-loop
- Complex multi-agent orchestration

Installation: pip install langgraph langchain langchain-openai
"""

import os
from typing import TypedDict, Annotated, Literal
import operator


# =============================================================================
# EXAMPLE 1: SIMPLE LANGGRAPH AGENT WITH STATE
# =============================================================================

def create_simple_langgraph_agent():
    """
    Simple LangGraph Agent with State Management
    
    Workflow:
    START → agent (thinks + calls tools) → should_continue?
                                             ↓YES      ↓NO
                                           tools      END
                                             ↓
                                           agent
    
    Key concept: State is passed between nodes
    """
    print("\n" + "="*80)
    print("📊 LANGGRAPH EXAMPLE 1: Simple Agent with State")
    print("="*80)
    
    from langgraph.graph import StateGraph, END
    from langchain_openai import ChatOpenAI
    from langchain.tools import tool
    
    # Step 1: Define state schema (what data flows through the graph)
    class AgentState(TypedDict):
        """State passed between nodes"""
        messages: Annotated[list, operator.add]  # Append messages
        iterations: int
    
    # Step 2: Define tools
    @tool
    def calculator(expression: str) -> str:
        """Calculate math expressions"""
        try:
            result = eval(expression)
            return f"Result: {result}"
        except:
            return "Error in calculation"
    
    @tool
    def search(query: str) -> str:
        """Search for information"""
        return f"Mock search results for: {query}"
    
    tools = [calculator, search]
    
    # Step 3: Initialize LLM with tools
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    llm_with_tools = llm.bind_tools(tools)
    
    print("\n📦 Tools:", [t.name for t in tools])
    
    # Step 4: Define nodes (processing functions)
    def agent_node(state: AgentState) -> AgentState:
        """Agent reasoning node"""
        print(f"\n🤖 Agent thinking... (iteration {state['iterations']})")
        
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        
        return {
            "messages": [response],
            "iterations": state["iterations"] + 1
        }
    
    def tool_node(state: AgentState) -> AgentState:
        """Tool execution node"""
        print("\n🔧 Executing tools...")
        
        messages = state["messages"]
        last_message = messages[-1]
        
        # Execute tool calls
        tool_outputs = []
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                print(f"   → {tool_name}({tool_args})")
                
                # Find and execute tool
                for tool in tools:
                    if tool.name == tool_name:
                        result = tool.invoke(tool_args)
                        tool_outputs.append({"tool": tool_name, "result": result})
                        break
        
        return {"messages": tool_outputs}
    
    # Step 5: Define conditional routing
    def should_continue(state: AgentState) -> str:
        """Decide whether to continue or end"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If LLM called tools, go to tools node
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        # Otherwise, end
        return "end"
    
    # Step 6: Build graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    workflow.add_edge("tools", "agent")  # After tools, go back to agent
    
    # Compile
    app = workflow.compile()
    
    print("\n✅ LangGraph agent compiled!")
    print("\n📊 Graph structure:")
    print("   START → agent → [conditional]")
    print("              ↓         ↓")
    print("            END      tools")
    print("                       ↓")
    print("                    agent")
    
    return app


# =============================================================================
# EXAMPLE 2: MULTI-STEP WORKFLOW WITH CONDITIONAL ROUTING
# =============================================================================

def create_multi_step_workflow():
    """
    Multi-Step Workflow with Decision Points
    
    Workflow:
    START → classify → [simple/complex]
                ↓            ↓
            quick_answer   research → analyze → write
                ↓                                  ↓
                ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← 
                              ↓
                             END
    
    Use case: Content generation with smart routing
    """
    print("\n" + "="*80)
    print("📊 LANGGRAPH EXAMPLE 2: Multi-Step Conditional Workflow")
    print("="*80)
    
    from langgraph.graph import StateGraph, END
    from langchain_openai import ChatOpenAI
    
    # Define state
    class WorkflowState(TypedDict):
        input: str
        classification: str
        research_data: str
        analysis: str
        final_output: str
        step_count: int
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    
    # Node 1: Classify query
    def classify_query(state: WorkflowState) -> WorkflowState:
        """Classify if query is simple or complex"""
        print(f"\n📋 STEP 1: Classifying query...")
        
        prompt = f"""Classify this query as 'simple' or 'complex':

Query: {state['input']}

Simple: Can be answered in one sentence
Complex: Requires research and analysis

Respond with just 'simple' or 'complex':"""
        
        response = llm.invoke(prompt)
        classification = response.content.strip().lower()
        
        print(f"   Classification: {classification}")
        
        return {
            "classification": classification,
            "step_count": state.get("step_count", 0) + 1
        }
    
    # Node 2: Quick answer (for simple queries)
    def quick_answer(state: WorkflowState) -> WorkflowState:
        """Generate quick answer for simple queries"""
        print(f"\n⚡ STEP 2A: Quick answer...")
        
        prompt = f"Answer this question briefly: {state['input']}"
        response = llm.invoke(prompt)
        
        print(f"   Answer: {response.content[:100]}...")
        
        return {
            "final_output": response.content,
            "step_count": state.get("step_count", 0) + 1
        }
    
    # Node 3: Research (for complex queries)
    def research(state: WorkflowState) -> WorkflowState:
        """Gather information"""
        print(f"\n🔍 STEP 2B: Researching...")
        
        prompt = f"""Research this topic and provide key facts:

Topic: {state['input']}

Provide 3-5 key points:"""
        
        response = llm.invoke(prompt)
        
        print(f"   Research: {len(response.content)} chars")
        
        return {
            "research_data": response.content,
            "step_count": state.get("step_count", 0) + 1
        }
    
    # Node 4: Analyze
    def analyze(state: WorkflowState) -> WorkflowState:
        """Analyze research data"""
        print(f"\n📊 STEP 3: Analyzing...")
        
        prompt = f"""Analyze this research and identify key insights:

Research: {state['research_data']}

Provide analysis:"""
        
        response = llm.invoke(prompt)
        
        print(f"   Analysis: {len(response.content)} chars")
        
        return {
            "analysis": response.content,
            "step_count": state.get("step_count", 0) + 1
        }
    
    # Node 5: Write final output
    def write_output(state: WorkflowState) -> WorkflowState:
        """Create final comprehensive answer"""
        print(f"\n✍️ STEP 4: Writing final output...")
        
        prompt = f"""Write a comprehensive answer based on:

Original question: {state['input']}
Research: {state['research_data']}
Analysis: {state['analysis']}

Provide clear, well-structured answer:"""
        
        response = llm.invoke(prompt)
        
        print(f"   Final output: {len(response.content)} chars")
        
        return {
            "final_output": response.content,
            "step_count": state.get("step_count", 0) + 1
        }
    
    # Routing function
    def route_after_classification(state: WorkflowState) -> Literal["quick", "research"]:
        """Route based on classification"""
        if state["classification"] == "simple":
            return "quick"
        else:
            return "research"
    
    # Build graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("classify", classify_query)
    workflow.add_node("quick_answer", quick_answer)
    workflow.add_node("research", research)
    workflow.add_node("analyze", analyze)
    workflow.add_node("write", write_output)
    
    # Set entry point
    workflow.set_entry_point("classify")
    
    # Add conditional routing after classification
    workflow.add_conditional_edges(
        "classify",
        route_after_classification,
        {
            "quick": "quick_answer",
            "research": "research"
        }
    )
    
    # Add sequential edges for complex path
    workflow.add_edge("research", "analyze")
    workflow.add_edge("analyze", "write")
    
    # Both paths end
    workflow.add_edge("quick_answer", END)
    workflow.add_edge("write", END)
    
    # Compile
    app = workflow.compile()
    
    print("\n✅ Multi-step workflow compiled!")
    print("\n📊 Workflow structure:")
    print("   classify → [simple → quick_answer → END]")
    print("           ↘ [complex → research → analyze → write → END]")
    
    return app


# =============================================================================
# EXAMPLE 3: MULTI-AGENT SUPERVISOR PATTERN
# =============================================================================

def create_supervisor_multi_agent():
    """
    Multi-Agent System with Supervisor Pattern
    
    Workflow:
    START → supervisor → [researcher/analyst/writer/finish]
                ↑              ↓       ↓        ↓
                └ ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← 
    
    Agents:
    - Supervisor: Coordinates and decides next step
    - Researcher: Gathers information
    - Analyst: Analyzes data
    - Writer: Creates content
    """
    print("\n" + "="*80)
    print("📊 LANGGRAPH EXAMPLE 3: Multi-Agent Supervisor System")
    print("="*80)
    
    from langgraph.graph import StateGraph, END
    from langchain_openai import ChatOpenAI
    import json
    
    # Define state
    class MultiAgentState(TypedDict):
        task: str
        research: str
        analysis: str
        content: str
        next_agent: str
        messages: list
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    
    # Supervisor agent
    def supervisor(state: MultiAgentState) -> MultiAgentState:
        """Decides which agent should act next"""
        print(f"\n👔 SUPERVISOR: Deciding next step...")
        
        prompt = f"""You are a supervisor coordinating agents.

Task: {state['task']}
Research completed: {bool(state.get('research'))}
Analysis completed: {bool(state.get('analysis'))}
Content completed: {bool(state.get('content'))}

Which agent should act next?
Options: researcher, analyst, writer, finish

Respond with JSON:
{{"next": "agent_name", "reason": "why"}}"""
        
        response = llm.invoke(prompt)
        try:
            decision = json.loads(response.content)
            next_agent = decision["next"]
            reason = decision["reason"]
        except:
            next_agent = "finish"
            reason = "Error in decision"
        
        print(f"   Decision: {next_agent} - {reason}")
        
        return {
            "next_agent": next_agent,
            "messages": state.get("messages", []) + [f"Supervisor: {reason}"]
        }
    
    # Researcher agent
    def researcher(state: MultiAgentState) -> MultiAgentState:
        """Gathers information"""
        print(f"\n🔍 RESEARCHER: Gathering information...")
        
        prompt = f"Research this topic: {state['task']}\n\nProvide key findings:"
        response = llm.invoke(prompt)
        
        print(f"   Research complete: {len(response.content)} chars")
        
        return {
            "research": response.content,
            "messages": state.get("messages", []) + [f"Researcher: Completed research"]
        }
    
    # Analyst agent
    def analyst(state: MultiAgentState) -> MultiAgentState:
        """Analyzes information"""
        print(f"\n📊 ANALYST: Analyzing data...")
        
        prompt = f"""Analyze this research:

Research: {state.get('research', 'No research yet')}

Provide insights:"""
        
        response = llm.invoke(prompt)
        
        print(f"   Analysis complete: {len(response.content)} chars")
        
        return {
            "analysis": response.content,
            "messages": state.get("messages", []) + [f"Analyst: Completed analysis"]
        }
    
    # Writer agent
    def writer(state: MultiAgentState) -> MultiAgentState:
        """Creates final content"""
        print(f"\n✍️ WRITER: Creating content...")
        
        prompt = f"""Write content based on:

Task: {state['task']}
Research: {state.get('research', '')}
Analysis: {state.get('analysis', '')}

Create polished output:"""
        
        response = llm.invoke(prompt)
        
        print(f"   Content complete: {len(response.content)} chars")
        
        return {
            "content": response.content,
            "messages": state.get("messages", []) + [f"Writer: Completed content"]
        }
    
    # Routing function
    def route_to_agent(state: MultiAgentState) -> str:
        """Route to next agent based on supervisor decision"""
        next_agent = state.get("next_agent", "finish")
        return next_agent
    
    # Build graph
    workflow = StateGraph(MultiAgentState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("researcher", researcher)
    workflow.add_node("analyst", analyst)
    workflow.add_node("writer", writer)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Add conditional routing from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "writer": "writer",
            "finish": END
        }
    )
    
    # All agents return to supervisor
    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("analyst", "supervisor")
    workflow.add_edge("writer", "supervisor")
    
    # Compile
    app = workflow.compile()
    
    print("\n✅ Multi-agent system compiled!")
    print("\n📊 System structure:")
    print("   supervisor → [researcher/analyst/writer/finish]")
    print("        ↑           ↓       ↓        ↓")
    print("        └ ← ← ← ← ← ← ← ← ← ← ← ← ← ")
    
    return app


# =============================================================================
# MAIN DEMONSTRATION
# =============================================================================

def demonstrate_all_langgraph():
    """Run all LangGraph examples"""
    
    print("\n" + "="*80)
    print("📊 LANGGRAPH COMPLETE DEMONSTRATIONS")
    print("="*80)
    
    # Example 1: Simple agent
    print("\n" + "="*80)
    print("EXAMPLE 1: Simple Agent with State")
    print("="*80)
    
    try:
        app1 = create_simple_langgraph_agent()
        
        # Test query
        query = "What is 15 * 8?"
        print(f"\n🔍 Query: {query}")
        
        result = app1.invoke({
            "messages": [{"role": "user", "content": query}],
            "iterations": 0
        })
        
        print(f"\n✅ Final result: {result['messages'][-1]}")
        
    except Exception as e:
        print(f"\n⚠️ Example 1 error: {str(e)}")
    
    # Example 2: Multi-step workflow
    input("\n▶ Press Enter for Example 2: Multi-Step Workflow...")
    
    print("\n" + "="*80)
    print("EXAMPLE 2: Multi-Step Conditional Workflow")
    print("="*80)
    
    try:
        app2 = create_multi_step_workflow()
        
        queries = [
            "What is 2+2?",  # Simple
            "Explain quantum computing"  # Complex
        ]
        
        for query in queries:
            print(f"\n{'='*80}")
            print(f"🔍 Query: {query}")
            print(f"{'='*80}")
            
            result = app2.invoke({
                "input": query,
                "step_count": 0
            })
            
            print(f"\n✅ Final Output:\n{result['final_output'][:300]}...")
            print(f"\n📊 Steps taken: {result['step_count']}")
        
    except Exception as e:
        print(f"\n⚠️ Example 2 error: {str(e)}")
    
    # Example 3: Multi-agent supervisor
    input("\n▶ Press Enter for Example 3: Multi-Agent System...")
    
    print("\n" + "="*80)
    print("EXAMPLE 3: Multi-Agent Supervisor System")
    print("="*80)
    
    try:
        app3 = create_supervisor_multi_agent()
        
        task = "Research and summarize AI agents"
        print(f"\n🎯 Task: {task}")
        
        result = app3.invoke({
            "task": task,
            "messages": []
        })
        
        print(f"\n✅ Final Content:\n{result.get('content', 'Not completed')[:300]}...")
        print(f"\n📝 Messages:")
        for msg in result.get('messages', []):
            print(f"   - {msg}")
        
    except Exception as e:
        print(f"\n⚠️ Example 3 error: {str(e)}")
    
    print("\n" + "="*80)
    print("✅ All LangGraph examples completed!")
    print("="*80)


if __name__ == "__main__":
    # Requires OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ Please set OPENAI_API_KEY environment variable")
    else:
        demonstrate_all_langgraph()
