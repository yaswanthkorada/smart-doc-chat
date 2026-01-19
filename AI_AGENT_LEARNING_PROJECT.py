"""
=============================================================================
AI AGENT LEARNING PROJECT - END TO END IMPLEMENTATION
=============================================================================

Purpose: Complete AI Agent system from basics to multi-agent collaboration
Author: Learning Tutorial
Date: January 2026

What You'll Learn:
1. Agent Fundamentals - What is an AI Agent?
2. Agent Architecture - Perception → Reasoning → Action
3. Tool Creation - Give agents capabilities
4. ReAct Pattern - Reasoning + Acting
5. Memory Systems - Short-term and Long-term
6. Agent Frameworks - LangChain vs CrewAI
7. Multi-Agent Systems - Collaboration & Communication
8. Agent Evaluation - Measuring agent performance

Requirements:
pip install langchain openai langchain-openai langgraph
pip install crewai crewai-tools
pip install chromadb faiss-cpu

NOTE: For complete LangGraph step-by-step examples, see:
      LANGGRAPH_EXAMPLES.py (separate file with 3 complete working examples)
"""

import os
from typing import List, Dict, Any, Tuple
import json
from datetime import datetime

# =============================================================================
# PART 1: AGENT FUNDAMENTALS
# =============================================================================
# Concept: An AI Agent is an autonomous system that:
#   1. Perceives its environment (receives input)
#   2. Reasons about what to do (plans actions)
#   3. Acts on the environment (executes actions)
#   4. Learns from outcomes (improves over time)
#
# Key Difference from Simple LLM:
# - LLM: Question → Answer (one-shot)
# - Agent: Goal → [Observe → Think → Act]* → Result (iterative)
# =============================================================================

def demonstrate_simple_llm_vs_agent():
    """
    DEMO: Simple LLM vs AI Agent
    
    This shows the fundamental difference between:
    - Static LLM call (one prompt, one response)
    - Agent loop (multiple iterations, tool use, reasoning)
    """
    print("=" * 80)
    print("PART 1: LLM vs AGENT - FUNDAMENTAL DIFFERENCE")
    print("=" * 80)
    
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    task = "What is the weather in New York and should I bring an umbrella?"
    
    # ========================================
    # Approach 1: Simple LLM (FAILS)
    # ========================================
    print("\n📝 APPROACH 1: Simple LLM Call")
    print(f"Task: {task}")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": task}]
    )
    
    llm_answer = response.choices[0].message.content
    print(f"\n❌ LLM Response:\n{llm_answer}")
    print("\n⚠️ Problem: LLM has no access to real-time weather data!")
    print("   It can only make up information or refuse to answer.")
    
    # ========================================
    # Approach 2: AI Agent (SUCCESS)
    # ========================================
    print("\n\n🤖 APPROACH 2: AI Agent with Tools")
    print(f"Task: {task}")
    
    # Simulate agent thinking process
    print("\n📍 Agent Process:")
    print("   Step 1: PERCEIVE - Understand I need current weather data")
    print("   Step 2: REASON - I need to use weather API tool")
    print("   Step 3: ACT - Call weather_api('New York')")
    print("   Step 4: OBSERVE - Got result: {'temp': 65, 'condition': 'rainy'}")
    print("   Step 5: REASON - It's rainy, so umbrella needed")
    print("   Step 6: ACT - Generate final answer")
    
    agent_answer = """
    The current weather in New York is 65°F with rainy conditions.
    ✅ Yes, you should bring an umbrella!
    """
    
    print(f"\n✅ Agent Response:\n{agent_answer}")
    print("\n💡 Key Difference:")
    print("   - LLM: Single call, no tools, static knowledge")
    print("   - Agent: Iterative, uses tools, accesses real data")
    
    return {
        "llm_response": llm_answer,
        "agent_response": agent_answer
    }


# =============================================================================
# PART 2: AGENT ARCHITECTURE - BUILDING BLOCKS
# =============================================================================
# Every AI agent has these core components:
#   1. Perception: Receive and understand input
#   2. Memory: Store context and history
#   3. Reasoning: Decide what to do
#   4. Tools: Actions the agent can take
#   5. Execution: Perform actions
#   6. Observation: Process action results
# =============================================================================

class SimpleAgent:
    """
    Simple Agent Implementation (EDUCATIONAL)
    
    Concept: Basic agent with perception, reasoning, action loop
    
    Architecture:
    ┌─────────────┐
    │   INPUT     │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  PERCEIVE   │ ← Understand the task
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │   REASON    │ ← Decide what to do
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │    ACT      │ ← Execute action
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  OBSERVE    │ ← Get results
    └──────┬──────┘
           │
           └─────► Loop back to REASON (if needed)
    """
    
    def __init__(self, name: str, tools: List[Any] = None):
        """
        Initialize agent with name and available tools
        
        Parameters:
            name: Agent identifier
            tools: List of callable functions the agent can use
        """
        self.name = name
        self.tools = tools or []
        self.memory = []  # Stores conversation history
        self.max_iterations = 5  # Prevent infinite loops
        
        print(f"\n🤖 Agent '{name}' initialized")
        print(f"   Available tools: {[tool.__name__ for tool in self.tools]}")
    
    def perceive(self, user_input: str) -> Dict:
        """
        STEP 1: Perception
        
        Concept: Understand and structure the input
        Returns: Structured representation of the input
        """
        print(f"\n👁️ PERCEIVE: {user_input}")
        
        perception = {
            "raw_input": user_input,
            "timestamp": datetime.now().isoformat(),
            "intent": "answer_question"  # In real agent, use LLM to classify
        }
        
        return perception
    
    def reason(self, perception: Dict, context: List[Dict]) -> Dict:
        """
        STEP 2: Reasoning
        
        Concept: Decide what action to take based on perception and memory
        Returns: Action plan
        """
        print(f"\n🧠 REASON: Analyzing task...")
        
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Build prompt for reasoning
        tool_descriptions = "\n".join([
            f"- {tool.__name__}: {tool.__doc__}"
            for tool in self.tools
        ])
        
        prompt = f"""You are an AI agent. Analyze this task and decide what to do.

Task: {perception['raw_input']}

Available tools:
{tool_descriptions}

Decide:
1. Which tool to use (or 'none' if you can answer directly)
2. What parameters to pass to the tool

Respond in JSON format:
{{
    "action": "tool_name or 'answer'",
    "parameters": {{}},
    "reasoning": "why you chose this action"
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        try:
            decision = json.loads(response.choices[0].message.content)
        except:
            decision = {
                "action": "answer",
                "parameters": {},
                "reasoning": "Could not parse decision"
            }
        
        print(f"   Decision: {decision['action']}")
        print(f"   Reasoning: {decision['reasoning']}")
        
        return decision
    
    def act(self, decision: Dict) -> Any:
        """
        STEP 3: Action
        
        Concept: Execute the decided action
        Returns: Result of the action
        """
        print(f"\n⚡ ACT: Executing '{decision['action']}'")
        
        action = decision["action"]
        
        # If action is to use a tool
        if action != "answer" and action != "none":
            for tool in self.tools:
                if tool.__name__ == action:
                    result = tool(**decision.get("parameters", {}))
                    return result
            
            return {"error": f"Tool '{action}' not found"}
        
        # If action is to answer directly
        return {"status": "ready_to_answer"}
    
    def observe(self, action_result: Any) -> Dict:
        """
        STEP 4: Observation
        
        Concept: Process and understand the result of the action
        Returns: Observation data
        """
        print(f"\n👁️ OBSERVE: Got result")
        print(f"   Result: {action_result}")
        
        observation = {
            "result": action_result,
            "success": "error" not in str(action_result).lower(),
            "timestamp": datetime.now().isoformat()
        }
        
        return observation
    
    def run(self, user_input: str) -> str:
        """
        Main agent loop: Perceive → Reason → Act → Observe → Repeat
        
        This is the core of the agent - it iteratively:
        1. Perceives the current state
        2. Reasons about what to do
        3. Acts on its decision
        4. Observes the results
        5. Repeats until task is complete
        """
        print(f"\n{'='*80}")
        print(f"🤖 AGENT '{self.name}' STARTING TASK")
        print(f"{'='*80}")
        
        # Step 1: Initial perception
        perception = self.perceive(user_input)
        
        # Agent loop
        for iteration in range(self.max_iterations):
            print(f"\n--- Iteration {iteration + 1} ---")
            
            # Step 2: Reason about what to do
            decision = self.reason(perception, self.memory)
            
            # Step 3: Take action
            action_result = self.act(decision)
            
            # Step 4: Observe results
            observation = self.observe(action_result)
            
            # Store in memory
            self.memory.append({
                "perception": perception,
                "decision": decision,
                "observation": observation
            })
            
            # Check if done
            if decision["action"] in ["answer", "none"] or observation.get("success") == False:
                break
        
        # Generate final answer
        final_answer = self._generate_final_answer(user_input)
        
        print(f"\n{'='*80}")
        print(f"✅ AGENT COMPLETE")
        print(f"{'='*80}")
        
        return final_answer
    
    def _generate_final_answer(self, original_question: str) -> str:
        """Generate final answer based on memory"""
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Compile all observations
        context = "\n".join([
            f"Action: {m['decision']['action']}, Result: {m['observation']['result']}"
            for m in self.memory
        ])
        
        prompt = f"""Based on the actions taken, answer the original question.

Question: {original_question}

Actions and Results:
{context}

Provide a clear, concise answer:"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        return response.choices[0].message.content


# =============================================================================
# PART 3: TOOL CREATION
# =============================================================================
# Concept: Tools give agents capabilities to interact with the world
# Without tools, agents are just LLMs. With tools, they become powerful!
# =============================================================================

def create_calculator_tool():
    """
    EXAMPLE 1: Calculator Tool (Simple)
    
    Concept: Basic tool that performs calculations
    When to use: Agent needs to do math
    """
    
    def calculator(expression: str) -> Dict:
        """
        Evaluates mathematical expressions
        
        Args:
            expression: Math expression like "2 + 2" or "10 * 5"
        
        Returns:
            Result of calculation
        """
        try:
            # Safety: Only allow basic math operations
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in expression):
                return {"error": "Invalid characters in expression"}
            
            result = eval(expression)
            return {"result": result, "expression": expression}
        except Exception as e:
            return {"error": str(e)}
    
    return calculator


def create_weather_tool():
    """
    EXAMPLE 2: Weather API Tool (External API)
    
    Concept: Tool that calls external service
    When to use: Need real-time data
    
    Note: This is a mock tool. In production, use actual API:
    import requests
    response = requests.get(f"https://api.weather.com/v1/{city}")
    """
    
    def weather_api(city: str) -> Dict:
        """
        Gets current weather for a city
        
        Args:
            city: City name (e.g., "New York", "London")
        
        Returns:
            Weather data including temperature and conditions
        """
        # Mock data (in production, call real API)
        mock_data = {
            "New York": {"temp": 65, "condition": "rainy", "humidity": 75},
            "London": {"temp": 55, "condition": "cloudy", "humidity": 80},
            "Tokyo": {"temp": 70, "condition": "sunny", "humidity": 60}
        }
        
        if city in mock_data:
            return {
                "city": city,
                "data": mock_data[city],
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"error": f"Weather data not available for {city}"}
    
    return weather_api


def create_search_tool():
    """
    EXAMPLE 3: Search Tool (Information Retrieval)
    
    Concept: Tool that searches for information
    When to use: Agent needs to find facts
    
    Note: This is a mock. In production, use:
    - Google Search API
    - Bing Search API
    - DuckDuckGo API
    - Your own knowledge base
    """
    
    def search(query: str) -> Dict:
        """
        Searches for information
        
        Args:
            query: Search query
        
        Returns:
            Search results
        """
        # Mock search results
        mock_results = {
            "machine learning": "Machine learning is a subset of AI that enables computers to learn from data.",
            "python": "Python is a high-level programming language known for its simplicity and readability.",
            "ai agents": "AI agents are autonomous systems that perceive, reason, and act to achieve goals."
        }
        
        # Simple keyword matching
        result = None
        for key, value in mock_results.items():
            if key.lower() in query.lower():
                result = value
                break
        
        if result:
            return {
                "query": query,
                "result": result,
                "source": "Knowledge Base"
            }
        else:
            return {"error": "No results found", "query": query}
    
    return search


def create_langchain_tool():
    """
    EXAMPLE 4: LangChain Tool Creation (Framework)
    
    Concept: Use LangChain's @tool decorator for easy tool creation
    When to use: Building complex agents with many tools
    Pros: Type safety, automatic documentation, integration with LangChain agents
    """
    from langchain.tools import tool
    
    @tool
    def file_reader(file_path: str) -> str:
        """
        Reads content from a file
        
        Args:
            file_path: Path to the file to read
        
        Returns:
            File contents as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"File content ({len(content)} chars): {content[:200]}..."
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    return file_reader


# =============================================================================
# PART 4: REACT PATTERN (Reasoning + Acting)
# =============================================================================
# ReAct = Reason + Act (Interleaved)
# 
# Traditional: Think → Act
# ReAct: Think → Act → Observe → Think → Act → Observe (loop)
#
# Why powerful: Agent can adjust its plan based on results
# =============================================================================

class ReActAgent:
    """
    ReAct Agent Implementation
    
    Concept: Combines reasoning and acting in an interleaved manner
    
    Pattern:
    1. Thought: "I need to find X"
    2. Action: search("X")
    3. Observation: "X is Y"
    4. Thought: "Now I need to verify Y"
    5. Action: calculate("Y")
    6. Observation: "Result is Z"
    7. Thought: "I have enough info"
    8. Answer: "The answer is Z"
    
    Why better than simple planning:
    - Can adapt based on intermediate results
    - More transparent (shows reasoning)
    - Can recover from errors
    """
    
    def __init__(self, tools: List[Any]):
        self.tools = tools
        self.max_iterations = 10
        
    def run(self, task: str) -> str:
        """
        Run ReAct loop
        
        Format:
        Thought: [reasoning]
        Action: [tool to use]
        Action Input: [parameters]
        Observation: [result]
        ... (repeat)
        Thought: I now know the final answer
        Final Answer: [answer]
        """
        print("\n" + "="*80)
        print("🔄 REACT AGENT - REASONING + ACTING")
        print("="*80)
        
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Build tool descriptions
        tool_descriptions = "\n".join([
            f"{i+1}. {tool.__name__}: {tool.__doc__.strip()}"
            for i, tool in enumerate(self.tools)
        ])
        
        # ReAct prompt template
        prompt_template = """Answer the following question using this format:

Thought: [your reasoning about what to do]
Action: [tool name or 'Finish']
Action Input: [parameters for the tool]
Observation: [result will be provided]

Repeat this Thought/Action/Observation cycle until you have enough information.

When you know the final answer:
Thought: I now know the final answer
Final Answer: [your answer here]

Available tools:
{tools}

Question: {question}

Begin!
"""
        
        conversation = []
        full_log = ""
        
        for iteration in range(self.max_iterations):
            print(f"\n--- Iteration {iteration + 1} ---")
            
            # Build prompt with history
            if iteration == 0:
                current_prompt = prompt_template.format(
                    tools=tool_descriptions,
                    question=task
                )
            else:
                current_prompt = full_log + "\n\nContinue:"
            
            # Get agent's next thought/action
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": current_prompt}],
                temperature=0.0
            )
            
            agent_response = response.choices[0].message.content
            print(f"\n🤖 Agent:\n{agent_response}")
            
            full_log += "\n" + agent_response
            
            # Check if agent is done
            if "Final Answer:" in agent_response:
                final_answer = agent_response.split("Final Answer:")[-1].strip()
                print(f"\n✅ COMPLETE: {final_answer}")
                return final_answer
            
            # Extract action and execute
            if "Action:" in agent_response and "Action Input:" in agent_response:
                try:
                    action_line = [line for line in agent_response.split('\n') if line.startswith('Action:')][0]
                    action_name = action_line.replace('Action:', '').strip()
                    
                    input_line = [line for line in agent_response.split('\n') if line.startswith('Action Input:')][0]
                    action_input = input_line.replace('Action Input:', '').strip()
                    
                    # Execute tool
                    observation = self._execute_tool(action_name, action_input)
                    
                    print(f"\n👁️ Observation: {observation}")
                    full_log += f"\nObservation: {observation}\n"
                    
                except Exception as e:
                    observation = f"Error: {str(e)}"
                    print(f"\n❌ Error: {observation}")
                    full_log += f"\nObservation: {observation}\n"
        
        return "Maximum iterations reached"
    
    def _execute_tool(self, tool_name: str, tool_input: str) -> str:
        """Execute a tool and return observation"""
        for tool in self.tools:
            if tool.__name__.lower() in tool_name.lower():
                try:
                    result = tool(tool_input)
                    return str(result)
                except Exception as e:
                    return f"Error executing tool: {str(e)}"
        
        return f"Tool '{tool_name}' not found"


# =============================================================================
# PART 5: MEMORY SYSTEMS
# =============================================================================
# Agents need memory to:
# 1. Remember conversation history
# 2. Learn from past interactions
# 3. Maintain context across turns
# =============================================================================

class AgentMemory:
    """
    Agent Memory System
    
    Types of Memory:
    1. Short-term (Working): Current conversation
    2. Long-term (Episodic): Past conversations
    3. Semantic: General knowledge learned
    """
    
    def __init__(self):
        self.short_term = []  # Current session
        self.long_term = []   # Past sessions
        self.semantic = {}    # Learned facts
        
        print("\n🧠 Memory System Initialized")
    
    def add_to_short_term(self, interaction: Dict):
        """
        Add to working memory (current conversation)
        
        Auto-manages memory size to prevent context overflow
        """
        self.short_term.append(interaction)
        
        # Keep only last N interactions in short-term
        max_short_term = 10
        if len(self.short_term) > max_short_term:
            # Move old memories to long-term
            old_memory = self.short_term.pop(0)
            self.long_term.append(old_memory)
        
        print(f"   📝 Short-term: {len(self.short_term)} items")
    
    def add_to_long_term(self, session: List[Dict]):
        """
        Store entire session in long-term memory
        
        Useful for: Learning patterns, personalizing responses
        """
        self.long_term.extend(session)
        print(f"   💾 Long-term: {len(self.long_term)} items")
    
    def add_semantic_knowledge(self, key: str, value: Any):
        """
        Store learned facts (semantic memory)
        
        Example: User prefers formal tone, user is in timezone EST
        """
        self.semantic[key] = value
        print(f"   🧠 Learned: {key} = {value}")
    
    def recall(self, query: str, memory_type: str = "short_term") -> List[Dict]:
        """
        Retrieve relevant memories
        
        In production, use:
        - Vector similarity search
        - Keyword matching
        - Temporal relevance
        """
        if memory_type == "short_term":
            return self.short_term[-5:]  # Last 5 interactions
        elif memory_type == "long_term":
            # In production: semantic search
            return self.long_term[-10:]
        elif memory_type == "semantic":
            return self.semantic
        else:
            return []
    
    def get_context_window(self, max_tokens: int = 2000) -> str:
        """
        Build context string for LLM (respecting token limit)
        
        Strategy:
        1. Always include current conversation (short-term)
        2. Include relevant long-term memories
        3. Include relevant semantic knowledge
        """
        context_parts = []
        
        # Short-term memory (most important)
        if self.short_term:
            recent = "\n".join([
                f"User: {m.get('user', '')}\nAgent: {m.get('agent', '')}"
                for m in self.short_term[-3:]
            ])
            context_parts.append(f"Recent conversation:\n{recent}")
        
        # Semantic knowledge
        if self.semantic:
            facts = "\n".join([f"- {k}: {v}" for k, v in self.semantic.items()])
            context_parts.append(f"\nLearned facts:\n{facts}")
        
        return "\n\n".join(context_parts)


def create_memory_enabled_agent():
    """
    EXAMPLE: Agent with Memory
    
    Demonstrates how memory makes agents more useful
    """
    
    class MemoryAgent:
        def __init__(self):
            self.memory = AgentMemory()
        
        def chat(self, user_input: str) -> str:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Get context from memory
            context = self.memory.get_context_window()
            
            # Build prompt with memory
            prompt = f"""{context}

User: {user_input}
Agent:"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            agent_response = response.choices[0].message.content
            
            # Store in memory
            self.memory.add_to_short_term({
                "user": user_input,
                "agent": agent_response,
                "timestamp": datetime.now().isoformat()
            })
            
            return agent_response
    
    return MemoryAgent()


# =============================================================================
# PART 6: LANGCHAIN & LANGGRAPH - PRODUCTION FRAMEWORKS
# =============================================================================
# LangChain: High-level agent abstractions
# LangGraph: Stateful, multi-step workflows with conditional routing
# =============================================================================

def create_langchain_agent_basic():
    """
    METHOD 1: Basic LangChain Agent (WORKING IMPLEMENTATION)
    
    Concept: Use LangChain's agent executor with tools
    When to use: Quick agent setup, standard patterns
    Pros: Less code, built-in error handling
    Cons: Less control over agent behavior
    
    How it works:
    1. Define tools with clear descriptions
    2. Create LLM instance
    3. Pull ReAct prompt template from hub
    4. Create agent with tools
    5. Wrap in AgentExecutor for execution
    """
    print("\n" + "="*80)
    print("🦜 LANGCHAIN AGENT (Basic)")
    print("="*80)
    
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain.tools import Tool
    from langchain_openai import ChatOpenAI
    from langchain import hub
    
    # Create tools with detailed descriptions
    def safe_calculator(expression: str) -> str:
        """Safely evaluate math expressions"""
        try:
            # Only allow basic math operations
            allowed = set('0123456789+-*/(). ')
            if not all(c in allowed for c in expression):
                return "Error: Invalid characters"
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    tools = [
        Tool(
            name="Calculator",
            func=safe_calculator,
            description="Useful for mathematical calculations. Input should be a math expression like '2+2' or '10*5'."
        ),
        Tool(
            name="Search",
            func=lambda x: f"Search results for '{x}': [Mock data about {x}]",
            description="Useful for finding information. Input should be a search query."
        )
    ]
    
    print("\n📦 Tools configured:")
    for tool in tools:
        print(f"   - {tool.name}: {tool.description[:50]}...")
    
    # Initialize LLM
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    print("\n🤖 LLM: GPT-3.5-turbo")
    
    # Get ReAct prompt template from LangChain hub
    prompt = hub.pull("hwchase17/react")
    print("\n📝 Prompt: ReAct pattern from LangChain hub")
    
    # Create agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create executor (handles execution loop)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True  # Gracefully handle LLM output errors
    )
    
    print("\n✅ LangChain Agent ready!")
    
    return agent_executor


def demonstrate_langchain_agent():
    """
    DEMO: Complete LangChain Agent Workflow
    
    Shows:
    1. Agent creation
    2. Query execution
    3. Tool usage
    4. Result generation
    """
    print("\n" + "="*80)
    print("🦜 LANGCHAIN AGENT DEMONSTRATION")
    print("="*80)
    
    # Create agent
    agent = create_langchain_agent_basic()
    
    # Test queries
    queries = [
        "What is 25 * 4 + 10?",
        "Search for information about Python programming"
    ]
    
    for query in queries:
        print(f"\n{'='*80}")
        print(f"🔍 Query: {query}")
        print(f"{'='*80}")
        
        try:
            result = agent.invoke({"input": query})
            print(f"\n✅ Final Answer: {result['output']}")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    
    return agent


def create_langchain_agent_conversational():
    """
    METHOD 2: Conversational Agent with Memory (WORKING)
    
    Concept: Agent that maintains conversation history
    When to use: Chat applications, multi-turn interactions
    
    Memory types:
    - ConversationBufferMemory: Stores all messages
    - ConversationSummaryMemory: Summarizes old messages
    - ConversationBufferWindowMemory: Keeps last N messages
    """
    print("\n" + "="*80)
    print("💬 LANGCHAIN CONVERSATIONAL AGENT")
    print("="*80)
    
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain.tools import Tool
    from langchain_openai import ChatOpenAI
    from langchain.memory import ConversationBufferMemory
    from langchain import hub
    
    # Tools
    tools = [
        Tool(
            name="Calculator",
            func=lambda x: str(eval(x)),
            description="For math calculations"
        )
    ]
    
    # Memory - stores conversation history
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="output"  # Important: specify which key to store
    )
    
    print("\n🧠 Memory: ConversationBufferMemory (stores all messages)")
    
    # LLM
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    
    # Agent with memory
    prompt = hub.pull("hwchase17/react-chat")
    agent = create_react_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True
    )
    
    print("\n✅ Conversational agent ready!")
    
    return agent_executor


# =============================================================================
# PART 7: CREWAI MULTI-AGENT SYSTEMS
# =============================================================================
# CrewAI: Framework for orchestrating role-based AI agents
# =============================================================================

def create_crewai_agent_simple():
    """
    METHOD 1: Single CrewAI Agent
    
    Concept: Define agent with role, goal, backstory
    When to use: Specialized tasks, need personality
    """
    print("\n" + "="*80)
    print("👥 CREWAI AGENT (Single)")
    print("="*80)
    
    from crewai import Agent, Task, Crew
    from langchain_openai import ChatOpenAI
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    
    # Create specialized agent
    researcher = Agent(
        role="Research Analyst",
        goal="Find accurate and relevant information on any topic",
        backstory="""You are an expert researcher with 10 years of experience 
        in data analysis and information gathering. You're thorough, accurate, 
        and always cite your sources.""",
        verbose=True,
        llm=llm,
        allow_delegation=False
    )
    
    return researcher


def create_crewai_multi_agent_system():
    """
    METHOD 2: Multi-Agent Collaboration (POWERFUL)
    
    Concept: Multiple specialized agents work together
    When to use: Complex tasks requiring different skills
    
    Example: Content Creation Pipeline
    - Researcher: Gathers information
    - Writer: Creates content
    - Editor: Reviews and improves
    
    Each agent has:
    - Role: What they do
    - Goal: What they aim to achieve
    - Backstory: Their expertise/personality
    - Tools: What they can use
    """
    print("\n" + "="*80)
    print("👥 CREWAI MULTI-AGENT SYSTEM")
    print("="*80)
    
    from crewai import Agent, Task, Crew, Process
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    
    # Agent 1: Researcher
    researcher = Agent(
        role="Senior Research Analyst",
        goal="Discover groundbreaking insights and accurate information",
        backstory="""You're a seasoned researcher with a PhD in your field. 
        You have access to vast knowledge and always verify facts from multiple sources.
        You're known for your attention to detail and critical thinking.""",
        verbose=True,
        llm=llm,
        allow_delegation=False
    )
    
    # Agent 2: Writer
    writer = Agent(
        role="Content Writer",
        goal="Create engaging and informative content",
        backstory="""You're an award-winning writer with 15 years of experience.
        You excel at taking complex information and making it accessible and engaging.
        Your writing is clear, concise, and compelling.""",
        verbose=True,
        llm=llm,
        allow_delegation=False
    )
    
    # Agent 3: Editor
    editor = Agent(
        role="Senior Editor",
        goal="Ensure content is polished, accurate, and publication-ready",
        backstory="""You're a meticulous editor with an eye for detail.
        You've edited hundreds of articles and have a reputation for excellence.
        You check facts, improve clarity, and ensure consistent style.""",
        verbose=True,
        llm=llm,
        allow_delegation=False
    )
    
    return researcher, writer, editor


def demonstrate_multi_agent_workflow():
    """
    DEMO: Complete Multi-Agent Workflow
    
    Shows how agents collaborate on a task:
    1. Researcher gathers information
    2. Writer creates content based on research
    3. Editor reviews and improves the content
    """
    print("\n" + "="*80)
    print("🔄 MULTI-AGENT WORKFLOW DEMO")
    print("="*80)
    
    from crewai import Agent, Task, Crew, Process
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    
    # Create agents
    researcher, writer, editor = create_crewai_multi_agent_system()
    
    # Define tasks
    research_task = Task(
        description="""Research the topic: 'AI Agents in 2026'
        
        Find information about:
        - Current state of AI agents
        - Key capabilities
        - Popular frameworks
        - Use cases
        
        Provide a comprehensive research summary.""",
        agent=researcher,
        expected_output="Detailed research summary with key findings"
    )
    
    writing_task = Task(
        description="""Using the research provided, write an engaging article about AI Agents in 2026.
        
        The article should:
        - Have a catchy introduction
        - Explain key concepts clearly
        - Include practical examples
        - Be 300-400 words
        - Have a strong conclusion
        
        Make it informative yet accessible.""",
        agent=writer,
        expected_output="Well-written article about AI agents",
        context=[research_task]  # Depends on research task
    )
    
    editing_task = Task(
        description="""Review and improve the article.
        
        Check for:
        - Factual accuracy
        - Grammar and spelling
        - Clarity and flow
        - Consistent tone
        
        Provide the final, polished version.""",
        agent=editor,
        expected_output="Final polished article ready for publication",
        context=[writing_task]  # Depends on writing task
    )
    
    # Create crew
    crew = Crew(
        agents=[researcher, writer, editor],
        tasks=[research_task, writing_task, editing_task],
        process=Process.sequential,  # Tasks run in order
        verbose=True
    )
    
    return crew


# =============================================================================
# PART 7B: AGENTIC AI - AUTONOMOUS & SELF-IMPROVING AGENTS
# =============================================================================
# TERMINOLOGY CLARIFICATION:
# 
# 1. AI Agent: Basic agent with tools (Parts 1-6)
#    - Perceives → Reasons → Acts
#    - Uses tools
#    - Follows instructions
#
# 2. Agentic AI: Autonomous, goal-driven, self-improving (THIS SECTION)
#    - Sets own subgoals
#    - Plans multi-step workflows
#    - Self-reflects and corrects
#    - Learns from failures
#    - Operates autonomously
#
# 3. Multi-Agentic AI: Multiple agentic AIs collaborating (Next section)
#    - Hierarchical organization
#    - Debate and consensus
#    - Specialized roles
# =============================================================================

class AgenticAI:
    """
    Agentic AI Implementation
    
    Key Differences from Basic Agent:
    
    Basic Agent:
    - Reacts to user input
    - Follows instructions step-by-step
    - Limited autonomy
    
    Agentic AI:
    - Sets and pursues long-term goals
    - Decomposes goals into subgoals
    - Plans multi-step strategies
    - Self-reflects on performance
    - Self-corrects mistakes
    - Learns and improves
    
    Core Components:
    1. Goal Decomposition: Break complex goals into tasks
    2. Planning: Create multi-step execution plan
    3. Execution: Carry out plan with tools
    4. Self-Reflection: Evaluate own performance
    5. Self-Correction: Fix mistakes autonomously
    6. Learning: Improve from experience
    """
    
    def __init__(self, tools: List[Any], max_iterations: int = 20):
        self.tools = tools
        self.max_iterations = max_iterations
        self.memory = []
        self.learned_patterns = []  # Store successful strategies
        
        print("\n🧠 Agentic AI Initialized")
        print("   Capabilities: Goal Decomposition, Planning, Self-Reflection")
    
    def decompose_goal(self, high_level_goal: str) -> List[Dict]:
        """
        STEP 1: Goal Decomposition
        
        Concept: Break complex goal into manageable subgoals
        
        Example:
        Goal: "Research and write article about AI agents"
        Subgoals:
        1. Define scope and audience
        2. Research current state of AI agents
        3. Identify key frameworks
        4. Draft outline
        5. Write content
        6. Review and edit
        7. Format and publish
        """
        print(f"\n🎯 GOAL DECOMPOSITION: {high_level_goal}")
        
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        prompt = f"""You are an expert at breaking down complex goals into actionable subgoals.

High-level Goal: {high_level_goal}

Decompose this into 5-7 specific, actionable subgoals.
Each subgoal should be:
- Concrete and measurable
- Achievable with available tools
- Ordered logically

Respond in JSON format:
[
    {{"id": 1, "description": "subgoal description", "dependencies": [], "estimated_effort": "low/medium/high"}},
    ...
]
"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        try:
            subgoals = json.loads(response.choices[0].message.content)
        except:
            # Fallback if JSON parsing fails
            subgoals = [
                {"id": 1, "description": high_level_goal, "dependencies": [], "estimated_effort": "medium"}
            ]
        
        print(f"\n   📋 Decomposed into {len(subgoals)} subgoals:")
        for sg in subgoals:
            print(f"      {sg['id']}. {sg['description']} ({sg['estimated_effort']} effort)")
        
        return subgoals
    
    def create_plan(self, subgoals: List[Dict]) -> Dict:
        """
        STEP 2: Planning
        
        Concept: Create detailed execution plan with contingencies
        
        Plan includes:
        - Sequence of actions
        - Tool usage strategy
        - Success criteria
        - Fallback options
        - Time estimates
        """
        print(f"\n📝 PLANNING: Creating execution strategy")
        
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        tool_descriptions = "\n".join([
            f"- {tool.__name__}: {tool.__doc__}"
            for tool in self.tools
        ])
        
        subgoals_text = "\n".join([
            f"{sg['id']}. {sg['description']}"
            for sg in subgoals
        ])
        
        prompt = f"""Create a detailed execution plan for these subgoals.

Subgoals:
{subgoals_text}

Available Tools:
{tool_descriptions}

For each subgoal, specify:
1. Which tool(s) to use
2. Specific actions to take
3. Success criteria
4. Potential obstacles
5. Fallback strategy

Respond in JSON format:
{{
    "plan": [
        {{
            "subgoal_id": 1,
            "actions": ["action1", "action2"],
            "tools": ["tool_name"],
            "success_criteria": "what success looks like",
            "fallback": "what to do if it fails"
        }}
    ],
    "estimated_duration": "time estimate",
    "risk_level": "low/medium/high"
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        try:
            plan = json.loads(response.choices[0].message.content)
        except:
            plan = {
                "plan": [{"subgoal_id": sg["id"], "actions": [sg["description"]], "tools": [], "success_criteria": "completed", "fallback": "retry"} for sg in subgoals],
                "estimated_duration": "unknown",
                "risk_level": "medium"
            }
        
        print(f"\n   ✅ Plan created: {len(plan['plan'])} steps")
        print(f"   ⏱️ Estimated duration: {plan['estimated_duration']}")
        print(f"   ⚠️ Risk level: {plan['risk_level']}")
        
        return plan
    
    def execute_with_reflection(self, plan: Dict) -> Dict:
        """
        STEP 3: Execute with Self-Reflection
        
        Concept: Execute plan while continuously monitoring and adjusting
        
        Reflection happens:
        - After each action (micro-reflection)
        - After each subgoal (meso-reflection)
        - After entire plan (macro-reflection)
        
        Reflection questions:
        1. Did the action achieve its goal?
        2. What worked well?
        3. What could be improved?
        4. Should I adjust my strategy?
        """
        print(f"\n⚡ EXECUTION WITH REFLECTION")
        
        results = []
        
        for step in plan['plan']:
            print(f"\n--- Executing Step {step['subgoal_id']} ---")
            print(f"   Actions: {step['actions']}")
            
            step_result = {
                "step_id": step['subgoal_id'],
                "actions_taken": [],
                "success": False,
                "reflection": None
            }
            
            # Execute actions
            for action in step['actions']:
                print(f"   ⚡ Action: {action}")
                
                # Simulate action execution
                action_result = self._execute_action(action, step.get('tools', []))
                step_result['actions_taken'].append(action_result)
                
                # Micro-reflection after each action
                reflection = self._reflect_on_action(action, action_result)
                print(f"   💭 Reflection: {reflection['assessment']}")
                
                # Adjust if needed
                if reflection['should_adjust']:
                    print(f"   🔄 Adjusting strategy: {reflection['adjustment']}")
            
            # Meso-reflection after step
            step_reflection = self._reflect_on_step(step, step_result)
            step_result['reflection'] = step_reflection
            step_result['success'] = step_reflection['success']
            
            print(f"   {'✅' if step_result['success'] else '❌'} Step {step['subgoal_id']}: {step_reflection['summary']}")
            
            results.append(step_result)
            
            # Self-correct if step failed
            if not step_result['success']:
                print(f"   🔄 SELF-CORRECTION: Applying fallback strategy")
                fallback_result = self._apply_fallback(step)
                if fallback_result['success']:
                    step_result['success'] = True
                    print(f"   ✅ Fallback succeeded!")
        
        # Macro-reflection on entire execution
        final_reflection = self._reflect_on_execution(results)
        
        return {
            "results": results,
            "overall_success": final_reflection['success'],
            "reflection": final_reflection,
            "learned_patterns": final_reflection.get('learnings', [])
        }
    
    def _execute_action(self, action: str, tools: List[str]) -> Dict:
        """Execute a single action (simplified)"""
        # In real implementation, match action to tool and execute
        return {
            "action": action,
            "status": "completed",
            "output": f"Executed: {action}"
        }
    
    def _reflect_on_action(self, action: str, result: Dict) -> Dict:
        """
        Micro-reflection: Evaluate single action
        """
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        prompt = f"""Reflect on this action's outcome.

Action: {action}
Result: {result}

Evaluate:
1. Did it achieve the intended goal?
2. Was it efficient?
3. Should we adjust our approach?

Respond in JSON:
{{
    "assessment": "brief evaluation",
    "should_adjust": true/false,
    "adjustment": "what to change if should_adjust is true"
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        try:
            reflection = json.loads(response.choices[0].message.content)
        except:
            reflection = {
                "assessment": "Action completed",
                "should_adjust": False,
                "adjustment": ""
            }
        
        return reflection
    
    def _reflect_on_step(self, step: Dict, result: Dict) -> Dict:
        """
        Meso-reflection: Evaluate entire step
        """
        # Simplified: Check if all actions succeeded
        success = all(
            action.get('status') == 'completed'
            for action in result['actions_taken']
        )
        
        return {
            "success": success,
            "summary": f"Step {step['subgoal_id']} {'completed successfully' if success else 'encountered issues'}"
        }
    
    def _reflect_on_execution(self, results: List[Dict]) -> Dict:
        """
        Macro-reflection: Evaluate entire execution
        
        Key questions:
        1. Did we achieve the overall goal?
        2. What patterns led to success?
        3. What patterns led to failure?
        4. What should we remember for next time?
        """
        print("\n🤔 MACRO-REFLECTION: Analyzing overall performance")
        
        successes = sum(1 for r in results if r['success'])
        total = len(results)
        success_rate = successes / total if total > 0 else 0
        
        overall_success = success_rate >= 0.8
        
        # Extract learnings
        learnings = []
        if overall_success:
            learnings.append("Plan execution was effective")
            learnings.append("Tool selection was appropriate")
        else:
            learnings.append("Need better error handling")
            learnings.append("Consider more fallback strategies")
        
        reflection = {
            "success": overall_success,
            "success_rate": success_rate,
            "summary": f"Completed {successes}/{total} steps successfully",
            "learnings": learnings
        }
        
        print(f"   Success Rate: {success_rate:.1%}")
        print(f"   Learnings:")
        for learning in learnings:
            print(f"      - {learning}")
        
        # Store successful patterns for future use
        if overall_success:
            self.learned_patterns.extend(learnings)
        
        return reflection
    
    def _apply_fallback(self, step: Dict) -> Dict:
        """
        STEP 4: Self-Correction
        
        Concept: Automatically recover from failures
        
        Strategies:
        1. Retry with different parameters
        2. Use alternative tool
        3. Break into smaller steps
        4. Ask for clarification
        """
        fallback_strategy = step.get('fallback', 'retry')
        
        print(f"      Applying fallback: {fallback_strategy}")
        
        # Simulate fallback execution
        return {
            "success": True,
            "method": fallback_strategy
        }
    
    def run_autonomous(self, goal: str) -> Dict:
        """
        Complete Agentic AI Loop
        
        Goal → Decompose → Plan → Execute → Reflect → Learn → Repeat
        
        This is the full autonomous agent that:
        1. Sets its own subgoals
        2. Plans how to achieve them
        3. Executes with self-monitoring
        4. Reflects on performance
        5. Self-corrects mistakes
        6. Learns for future tasks
        """
        print("\n" + "="*80)
        print("🧠 AGENTIC AI - AUTONOMOUS OPERATION")
        print("="*80)
        print(f"\n🎯 High-Level Goal: {goal}")
        
        # Step 1: Decompose goal
        subgoals = self.decompose_goal(goal)
        
        # Step 2: Create plan
        plan = self.create_plan(subgoals)
        
        # Step 3: Execute with reflection
        execution_result = self.execute_with_reflection(plan)
        
        # Step 4: Final learning
        if execution_result['overall_success']:
            print(f"\n✅ GOAL ACHIEVED: {goal}")
        else:
            print(f"\n⚠️ PARTIAL SUCCESS: Some steps failed")
        
        print(f"\n📚 LEARNED PATTERNS:")
        for pattern in execution_result['learned_patterns']:
            print(f"   - {pattern}")
        
        return execution_result


# =============================================================================
# PART 7C: MULTI-AGENTIC AI - ENHANCED COLLABORATION PATTERNS
# =============================================================================
# Beyond basic multi-agent (Part 7), this shows advanced patterns:
# 1. Hierarchical - Manager and worker agents
# 2. Debate - Agents argue different perspectives
# 3. Consensus - Agents vote on best approach
# 4. Competitive - Agents compete for best solution
# =============================================================================

class MultiAgenticSystem:
    """
    Advanced Multi-Agentic AI Patterns
    
    Pattern 1: HIERARCHICAL
    - Manager agent coordinates worker agents
    - Top-down task distribution
    - Use: Complex projects with clear hierarchy
    
    Pattern 2: DEBATE
    - Multiple agents propose different solutions
    - Agents critique each other's approaches
    - Final decision based on strongest argument
    - Use: Problems with multiple valid approaches
    
    Pattern 3: CONSENSUS
    - Agents independently solve problem
    - Compare and vote on best solution
    - Use: Need high confidence in answer
    
    Pattern 4: COLLABORATIVE
    - Agents work together on shared workspace
    - Sequential or parallel contribution
    - Use: Creative tasks requiring diverse skills
    """
    
    def __init__(self):
        print("\n👥 Multi-Agentic System Initialized")


def demonstrate_hierarchical_agents():
    """
    PATTERN 1: Hierarchical Multi-Agent System
    
    Structure:
    
                    [Manager Agent]
                           |
            ┌──────────────┼──────────────┐
            |              |              |
      [Worker 1]      [Worker 2]    [Worker 3]
     (Research)        (Analysis)     (Writing)
    
    How it works:
    1. Manager receives goal
    2. Manager breaks down into tasks
    3. Manager assigns tasks to workers
    4. Workers execute independently
    5. Manager aggregates results
    6. Manager ensures quality
    """
    print("\n" + "="*80)
    print("👔 PATTERN 1: HIERARCHICAL AGENTS")
    print("="*80)
    
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    goal = "Research and summarize the state of AI agents in 2026"
    
    # Manager Agent
    print(f"\n👔 MANAGER: Received goal: {goal}")
    
    manager_prompt = f"""You are a manager agent coordinating worker agents.

Goal: {goal}

You have 3 worker agents:
1. Research Agent - Finds information
2. Analysis Agent - Analyzes trends
3. Writing Agent - Creates summaries

Decompose this goal and assign tasks to workers.

Respond in JSON:
{{
    "task_distribution": [
        {{"worker": "Research", "task": "specific task"}},
        {{"worker": "Analysis", "task": "specific task"}},
        {{"worker": "Writing", "task": "specific task"}}
    ]
}}
"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": manager_prompt}],
        temperature=0.0
    )
    
    try:
        task_distribution = json.loads(response.choices[0].message.content)
    except:
        task_distribution = {
            "task_distribution": [
                {"worker": "Research", "task": "Find latest AI agent frameworks"},
                {"worker": "Analysis", "task": "Identify key trends"},
                {"worker": "Writing", "task": "Write summary"}
            ]
        }
    
    print(f"\n👔 MANAGER: Task distribution:")
    for task in task_distribution['task_distribution']:
        print(f"   → {task['worker']}: {task['task']}")
    
    # Workers execute (simplified)
    worker_results = []
    for task in task_distribution['task_distribution']:
        print(f"\n👷 {task['worker'].upper()}: Executing task...")
        result = f"[{task['worker']} completed: {task['task']}]"
        worker_results.append(result)
        print(f"   ✅ Done")
    
    # Manager aggregates
    print(f"\n👔 MANAGER: Aggregating results...")
    final_output = "\n".join(worker_results)
    print(f"\n📄 FINAL OUTPUT:\n{final_output}")
    
    return final_output


def demonstrate_debate_agents():
    """
    PATTERN 2: Debate-Based Multi-Agent System
    
    Process:
    1. Problem presented to multiple agents
    2. Each agent proposes solution
    3. Agents critique each other's proposals
    4. Agents refine their proposals
    5. Judge agent selects best solution
    
    Why powerful:
    - Explores multiple perspectives
    - Identifies flaws in reasoning
    - Results in more robust solutions
    
    Use cases:
    - Medical diagnosis (multiple doctors debate)
    - Legal analysis (different perspectives)
    - Strategic planning (pros/cons debate)
    """
    print("\n" + "="*80)
    print("⚖️ PATTERN 2: DEBATE AGENTS")
    print("="*80)
    
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    problem = "Should our company invest in building custom AI agents or use existing frameworks?"
    
    print(f"\n❓ PROBLEM: {problem}")
    
    # Agent 1: Pro Custom
    print("\n🔵 AGENT 1 (Pro Custom):")
    agent1_prompt = f"""You are debating: {problem}

Your position: BUILD CUSTOM

Argue why building custom AI agents is better.
Provide 3 strong arguments.
"""
    
    response1 = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": agent1_prompt}],
        temperature=0.7
    )
    
    argument1 = response1.choices[0].message.content
    print(argument1[:300] + "...")
    
    # Agent 2: Pro Frameworks
    print("\n🟢 AGENT 2 (Pro Frameworks):")
    agent2_prompt = f"""You are debating: {problem}

Your position: USE EXISTING FRAMEWORKS

Argue why using existing frameworks is better.
Provide 3 strong arguments.
"""
    
    response2 = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": agent2_prompt}],
        temperature=0.7
    )
    
    argument2 = response2.choices[0].message.content
    print(argument2[:300] + "...")
    
    # Agent 1 critiques Agent 2
    print("\n🔵 AGENT 1: Critique of Agent 2's argument")
    critique_prompt = f"""Critique this argument:

{argument2}

Provide counter-arguments.
"""
    
    critique = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": critique_prompt}],
        temperature=0.7
    )
    print(critique.choices[0].message.content[:200] + "...")
    
    # Judge Agent
    print("\n⚖️ JUDGE AGENT: Evaluating arguments")
    judge_prompt = f"""You are a neutral judge evaluating this debate.

Problem: {problem}

Agent 1 argues for custom: {argument1[:500]}
Agent 2 argues for frameworks: {argument2[:500]}

Who has the stronger argument? Provide:
1. Winner
2. Key strengths of winning argument
3. Recommended approach
"""
    
    judgment = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": judge_prompt}],
        temperature=0.0
    )
    
    print(judgment.choices[0].message.content)
    
    return judgment.choices[0].message.content


def demonstrate_consensus_agents():
    """
    PATTERN 3: Consensus-Based Multi-Agent System
    
    Process:
    1. Problem given to N agents independently
    2. Each agent solves it separately
    3. Agents compare solutions
    4. Vote on best solution or merge approaches
    5. High-confidence answer emerges
    
    Why powerful:
    - Reduces individual agent errors
    - Increases confidence in answer
    - Identifies edge cases
    
    Use cases:
    - Medical diagnosis (multiple AI doctors)
    - Code review (multiple AI reviewers)
    - Risk assessment (multiple perspectives)
    """
    print("\n" + "="*80)
    print("🤝 PATTERN 3: CONSENSUS AGENTS")
    print("="*80)
    
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    problem = "What is the derivative of f(x) = 3x^2 + 2x + 1?"
    
    print(f"\n❓ PROBLEM: {problem}")
    print(f"\n🔄 Running 3 independent agents...\n")
    
    # Run multiple agents independently
    solutions = []
    for i in range(3):
        print(f"🤖 Agent {i+1}: Solving...")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"Solve this math problem: {problem}\n\nProvide:
1. Your solution
2. Step-by-step reasoning"
            }],
            temperature=0.3  # Some variation
        )
        
        solution = response.choices[0].message.content
        solutions.append(solution)
        print(f"   ✅ Solution: {solution[:100]}...\n")
    
    # Consensus phase
    print("🤝 CONSENSUS: Comparing solutions...")
    
    consensus_prompt = f"""Compare these 3 solutions to: {problem}

Solution 1:
{solutions[0]}

Solution 2:
{solutions[1]}

Solution 3:
{solutions[2]}

Determine:
1. Do they agree?
2. If yes, what is the consensus answer?
3. If no, which solution is most likely correct and why?
4. Confidence level (0-100%)
"""
    
    consensus = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": consensus_prompt}],
        temperature=0.0
    )
    
    print("\n📊 CONSENSUS RESULT:")
    print(consensus.choices[0].message.content)
    
    return consensus.choices[0].message.content


# =============================================================================
# PART 8: AGENT EVALUATION
# =============================================================================
# How do we know if our agent is good?
# =============================================================================

def evaluate_agent_performance(agent, test_cases: List[Dict]) -> Dict:
    """
    Agent Evaluation Framework
    
    Metrics:
    1. Task Success Rate: Did it complete the task?
    2. Efficiency: How many steps did it take?
    3. Tool Usage: Did it use the right tools?
    4. Answer Quality: Is the answer correct and helpful?
    5. Error Recovery: Did it handle errors gracefully?
    
    Parameters:
        agent: The agent to evaluate
        test_cases: List of {input, expected_output, expected_tools}
    """
    print("\n" + "="*80)
    print("📊 AGENT EVALUATION")
    print("="*80)
    
    results = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "avg_steps": 0,
        "tool_accuracy": 0
    }
    
    total_steps = 0
    correct_tools = 0
    total_tool_uses = 0
    
    for i, test_case in enumerate(test_cases):
        print(f"\n📝 Test Case {i+1}: {test_case['input']}")
        
        try:
            # Run agent
            output = agent.run(test_case['input'])
            
            # Check success
            expected = test_case.get('expected_output', '')
            if expected.lower() in output.lower() or output.lower() in expected.lower():
                results['passed'] += 1
                print("   ✅ PASSED")
            else:
                results['failed'] += 1
                print("   ❌ FAILED")
            
            # Count steps (from agent memory if available)
            if hasattr(agent, 'memory'):
                steps = len(agent.memory)
                total_steps += steps
                print(f"   Steps taken: {steps}")
            
            # Check tool usage
            if hasattr(agent, 'memory'):
                for memory in agent.memory:
                    tool_used = memory.get('decision', {}).get('action')
                    expected_tools = test_case.get('expected_tools', [])
                    
                    if tool_used and tool_used != 'answer':
                        total_tool_uses += 1
                        if tool_used in expected_tools:
                            correct_tools += 1
        
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results['failed'] += 1
    
    # Calculate metrics
    results['success_rate'] = results['passed'] / results['total'] if results['total'] > 0 else 0
    results['avg_steps'] = total_steps / results['total'] if results['total'] > 0 else 0
    results['tool_accuracy'] = correct_tools / total_tool_uses if total_tool_uses > 0 else 0
    
    # Print summary
    print("\n" + "="*80)
    print("📊 EVALUATION SUMMARY")
    print("="*80)
    print(f"✅ Success Rate: {results['success_rate']:.1%} ({results['passed']}/{results['total']})")
    print(f"⚡ Avg Steps: {results['avg_steps']:.1f}")
    print(f"🔧 Tool Accuracy: {results['tool_accuracy']:.1%}")
    
    if results['success_rate'] >= 0.8:
        print("\n🎉 EXCELLENT: Agent performs well!")
    elif results['success_rate'] >= 0.6:
        print("\n⚠️ GOOD: Agent works but needs improvement")
    else:
        print("\n❌ POOR: Agent needs significant work")
    
    return results


def evaluate_agent_with_llm_judge():
    """
    LLM-as-a-Judge for Agent Evaluation
    
    Concept: Use another LLM to judge agent performance
    When to use: Subjective qualities (helpfulness, clarity, tone)
    
    Criteria:
    - Helpfulness: Did it solve the user's problem?
    - Clarity: Is the answer easy to understand?
    - Efficiency: Did it take a reasonable approach?
    - Safety: Did it avoid harmful actions?
    """
    print("\n" + "="*80)
    print("⚖️ LLM-AS-A-JUDGE AGENT EVALUATION")
    print("="*80)
    
    from openai import OpenAI
    
    def judge_agent_response(task: str, agent_output: str, agent_process: str) -> Dict:
        """
        Have an LLM judge the agent's performance
        """
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        judge_prompt = f"""You are evaluating an AI agent's performance.

TASK: {task}

AGENT'S PROCESS:
{agent_process}

AGENT'S FINAL ANSWER:
{agent_output}

Evaluate on these criteria (score 1-10 each):
1. Helpfulness: Did it solve the problem?
2. Clarity: Is the answer clear?
3. Efficiency: Was the approach reasonable?
4. Correctness: Is the answer accurate?

Provide scores and brief explanations:
"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": judge_prompt}],
            temperature=0.0
        )
        
        judgment = response.choices[0].message.content
        
        print(f"\n⚖️ Judge's Evaluation:\n{judgment}")
        
        return {"judgment": judgment}
    
    return judge_agent_response


# =============================================================================
# MAIN: COMPLETE AGENT DEMONSTRATIONS
# =============================================================================

def main():
    """
    Complete AI Agent Learning Journey
    
    Demonstrates:
    1. Basic agent vs LLM
    2. Simple agent with tools
    3. ReAct agent
    4. Agent with memory
    5. LangChain agents
    6. Multi-agent systems
    7. Agent evaluation
    """
    
    print("="*80)
    print("🤖 AI AGENT LEARNING PROJECT - COMPLETE GUIDE")
    print("="*80)
    print("\nThis tutorial covers everything from basic agents to multi-agent systems.")
    print("Each part builds on the previous one.\n")
    
    # =============================================================================
    # DEMO 1: LLM vs Agent
    # =============================================================================
    input("\n▶ Press Enter to see DEMO 1: LLM vs Agent...")
    demonstrate_simple_llm_vs_agent()
    
    # =============================================================================
    # DEMO 2: Simple Agent with Tools
    # =============================================================================
    input("\n▶ Press Enter to see DEMO 2: Simple Agent with Tools...")
    
    # Create tools
    calculator = create_calculator_tool()
    weather = create_weather_tool()
    search = create_search_tool()
    
    # Create agent
    simple_agent = SimpleAgent(
        name="Assistant",
        tools=[calculator, weather, search]
    )
    
    # Test agent
    result = simple_agent.run("What is 25 * 4 + 10?")
    print(f"\n📝 Final Answer: {result}")
    
    # =============================================================================
    # DEMO 3: ReAct Agent
    # =============================================================================
    input("\n▶ Press Enter to see DEMO 3: ReAct Agent (Reasoning + Acting)...")
    
    react_agent = ReActAgent(tools=[calculator, search])
    result = react_agent.run("What is machine learning and calculate 10 * 5")
    
    # =============================================================================
    # DEMO 4: Agent with Memory
    # =============================================================================
    input("\n▶ Press Enter to see DEMO 4: Agent with Memory...")
    
    memory_agent = create_memory_enabled_agent()
    
    print("\n💬 Conversation with Memory:")
    response1 = memory_agent.chat("My name is Alex")
    print(f"Agent: {response1}")
    
    response2 = memory_agent.chat("What's my name?")
    print(f"Agent: {response2}")
    
    response3 = memory_agent.chat("I like Python programming")
    print(f"Agent: {response3}")
    
    response4 = memory_agent.chat("What do I like?")
    print(f"Agent: {response4}")
    
    # =============================================================================
    # DEMO 5: LangChain Agents (Framework Demo)
    # =============================================================================
    input("\n▶ Press Enter to see DEMO 5: LangChain Agents...")
    
    try:
        # Basic LangChain agent with tools
        demonstrate_langchain_agent()
        
        # Conversational agent with memory
        print("\n" + "="*80)
        print("💬 BONUS: Conversational Agent with Memory")
        print("="*80)
        conv_agent = create_langchain_agent_conversational()
        
        # Test conversation
        print("\n📝 Testing memory:")
        resp1 = conv_agent.invoke({"input": "What is 5 * 6?"})
        print(f"Turn 1: {resp1.get('output', 'Error')[:100]}")
        
        resp2 = conv_agent.invoke({"input": "Add 10 to that result"})
        print(f"Turn 2: {resp2.get('output', 'Error')[:100]}")
        
    except Exception as e:
        print(f"\n⚠️ LangChain demo error: {str(e)}")
        print("   Install with: pip install langchain langchain-openai langchain-hub")
    
    # =============================================================================
    # DEMO 6: LangGraph Workflows (Advanced - Separate File!)
    # =============================================================================
    input("\n▶ Press Enter for DEMO 6 info: LangGraph...")
    
    print("\n" + "="*80)
    print("📊 LANGGRAPH - STATEFUL MULTI-STEP WORKFLOWS")
    print("="*80)
    
    print("""
LangGraph enables advanced agent workflows with:
✅ Stateful execution (pass data between steps)
✅ Conditional routing (if-then-else logic)  
✅ Cycles and loops (iterative refinement)
✅ Human-in-the-loop (pause for approval)
✅ Multi-agent orchestration (supervisor pattern)

📂 Complete working examples in: LANGGRAPH_EXAMPLES.py

To run LangGraph examples separately:
    python LANGGRAPH_EXAMPLES.py

Examples included:
1. Simple Agent with State Management
   - Tool calling with state
   - Conditional routing (continue or end)
   
2. Multi-Step Conditional Workflow
   - Classify query (simple vs complex)
   - Simple → quick answer
   - Complex → research → analyze → write
   
3. Multi-Agent Supervisor System
   - Supervisor coordinates 3 specialized agents
   - Researcher → Analyst → Writer
   - Dynamic task routing

Install: pip install langgraph
""")
    
    # =============================================================================
    # DEMO 7: CrewAI Multi-Agent System
    # =============================================================================
    try:
        input("\n▶ Press Enter to see DEMO 7: Multi-Agent System (CrewAI)...")
        
        crew = demonstrate_multi_agent_workflow()
        
        print("\n🚀 Running multi-agent crew...")
        print("   (This may take 1-2 minutes)")
        
        # Run the crew
        result = crew.kickoff()
        
        print("\n" + "="*80)
        print("📄 FINAL OUTPUT FROM MULTI-AGENT SYSTEM:")
        print("="*80)
        print(result)
        
    except ImportError:
        print("\n⚠️ CrewAI not installed. Skipping multi-agent demo.")
        print("   Install with: pip install crewai crewai-tools")
    
    # =============================================================================
    # DEMO 8: Agentic AI (Autonomous Goal-Driven Agent)
    # =============================================================================
    input("\n▶ Press Enter to see DEMO 8: Agentic AI (Autonomous & Self-Improving)...")
    
    # Create agentic AI
    agentic_ai = AgenticAI(tools=[calculator, search])
    
    # Run autonomous task
    goal = "Research machine learning basics and create a simple explanation"
    result = agentic_ai.run_autonomous(goal)
    
    # =============================================================================
    # DEMO 9: Multi-Agentic AI Patterns
    # =============================================================================
    input("\n▶ Press Enter to see DEMO 9: Multi-Agentic AI Patterns...")
    
    # Pattern 1: Hierarchical
    print("\n" + "="*80)
    print("Testing Pattern 1: HIERARCHICAL")
    print("="*80)
    demonstrate_hierarchical_agents()
    
    input("\n▶ Press Enter to see Pattern 2: DEBATE...")
    
    # Pattern 2: Debate
    demonstrate_debate_agents()
    
    input("\n▶ Press Enter to see Pattern 3: CONSENSUS...")
    
    # Pattern 3: Consensus
    demonstrate_consensus_agents()
    
    # =============================================================================
    # DEMO 10: Agent Evaluation
    # =============================================================================
    input("\n▶ Press Enter to see DEMO 10: Agent Evaluation...")
    
    # Create test cases
    test_cases = [
        {
            "input": "What is 15 * 8?",
            "expected_output": "120",
            "expected_tools": ["calculator"]
        },
        {
            "input": "Search for information about Python",
            "expected_output": "Python is a programming language",
            "expected_tools": ["search"]
        }
    ]
    
    # Evaluate
    evaluation = evaluate_agent_performance(simple_agent, test_cases)
    
    # =============================================================================
    # FINAL SUMMARY
    # =============================================================================
    
    print("\n" + "="*80)
    print("🎓 LEARNING COMPLETE!")
    print("="*80)
    
    print("""
📚 What You Learned:

1. ✅ Agent Fundamentals
   - Difference between LLM and Agent
   - Perception → Reasoning → Action loop
   
2. ✅ Agent Architecture
   - Core components: perception, reasoning, tools, memory
   - How agents make decisions
   
3. ✅ Tool Creation
   - Calculator, search, API tools
   - LangChain tool decorator
   
4. ✅ ReAct Pattern
   - Interleaved reasoning and acting
   - More transparent and adaptive
   
5. ✅ Memory Systems
   - Short-term (working memory)
   - Long-term (episodic memory)
   - Semantic (learned knowledge)
   
6. ✅ Frameworks
   - LangChain agents
   - CrewAI multi-agent systems
   
7. ✅ Agentic AI (NEW!)
   - Goal decomposition
   - Multi-step planning
   - Self-reflection and self-correction
   - Autonomous operation
   
8. ✅ Multi-Agentic AI Patterns (NEW!)
   - Hierarchical (Manager + Workers)
   - Debate (Multiple perspectives)
   - Consensus (Voting on best solution)
   
9. ✅ Evaluation
   - Success rate, efficiency, tool accuracy
   - LLM-as-a-judge

🎯 Next Steps:

1. Build Your Own Agent:
   - Pick a specific use case (customer support, data analysis, etc.)
   - Define tools it needs
   - Create specialized agent with memory
   
2. Advanced Topics to Explore:
   - LangGraph for complex agent workflows
   - Agent fine-tuning
   - Multi-modal agents (vision + text)
   - Autonomous agents with continuous operation
   
3. Production Considerations:
   - Error handling and recovery
   - Rate limiting and cost control
   - Monitoring and logging
   - Safety and alignment

📖 Recommended Reading:
- LangChain Agents: https://python.langchain.com/docs/modules/agents/
- CrewAI Docs: https://docs.crewai.com/
- ReAct Paper: https://arxiv.org/abs/2210.03629
- Agent Frameworks Comparison: LangChain vs CrewAI vs AutoGen

🚀 You're now ready to build production AI agents!
""")


# =============================================================================
# COMPARISON REFERENCE
# =============================================================================

"""
TERMINOLOGY EXPLAINED:

1. AI AGENT (Basic):
   - Definition: System that perceives, reasons, and acts
   - Autonomy: Follows user instructions
   - Components: Tools, memory, reasoning
   - Example: ChatGPT with plugins
   - When to use: Task automation, simple workflows

2. AGENTIC AI (Advanced):
   - Definition: Autonomous, goal-driven, self-improving system
   - Autonomy: Sets own subgoals, operates independently
   - Components: Goal decomposition, planning, self-reflection
   - Example: AutoGPT, BabyAGI
   - When to use: Complex long-term goals, research, autonomous tasks

3. MULTI-AGENTIC AI (Collaborative):
   - Definition: Multiple agentic AIs working together
   - Autonomy: Distributed, collaborative decision-making
   - Components: Communication, coordination, specialization
   - Example: MetaGPT, CrewAI teams
   - When to use: Complex projects requiring diverse skills

┌──────────────────┬──────────────┬──────────────┬─────────────────┐
│   Capability     │  AI Agent    │  Agentic AI  │ Multi-Agentic   │
├──────────────────┼──────────────┼──────────────┼─────────────────┤
│ Follows commands │      ✅      │      ✅      │       ✅        │
│ Uses tools       │      ✅      │      ✅      │       ✅        │
│ Sets own goals   │      ❌      │      ✅      │       ✅        │
│ Self-reflects    │      ❌      │      ✅      │       ✅        │
│ Plans multi-step │      ❌      │      ✅      │       ✅        │
│ Self-corrects    │      ❌      │      ✅      │       ✅        │
│ Collaboration    │      ❌      │      ❌      │       ✅        │
│ Specialization   │      ❌      │      ❌      │       ✅        │
└──────────────────┴──────────────┴──────────────┴─────────────────┘

AGENT FRAMEWORKS COMPARISON:

┌────────────────────┬─────────────────┬─────────────────┬──────────────────┐
│     Framework      │    LangChain    │     CrewAI      │     AutoGen      │
├────────────────────┼─────────────────┼─────────────────┼──────────────────┤
│ Best For           │ General agents  │ Multi-agent     │ Code generation  │
│ Complexity         │ Medium          │ Low             │ High             │
│ Learning Curve     │ Moderate        │ Easy            │ Steep            │
│ Multi-agent        │ Possible        │ Excellent       │ Excellent        │
│ Tool Support       │ Extensive       │ Good            │ Limited          │
│ Memory             │ Built-in        │ Limited         │ Custom           │
│ Documentation      │ Excellent       │ Good            │ Good             │
│ Community          │ Large           │ Growing         │ Growing          │
│ Production Ready   │ Yes             │ Yes             │ Research-focused │
└────────────────────┴─────────────────┴─────────────────┴──────────────────┘

WHEN TO USE WHAT:

1. LangChain:
   - Single agent with many tools
   - Need extensive tool ecosystem
   - Standard agent patterns
   
2. CrewAI:
   - Multiple specialized agents collaborating
   - Role-based task distribution
   - Sequential or hierarchical workflows
   
3. Custom Agent:
   - Specific requirements not met by frameworks
   - Need full control over agent behavior
   - Research or experimental agents

AGENT PATTERNS:

1. ReAct Agent:
   - Interleaved reasoning and acting
   - Best for: Tasks requiring multiple steps
   
2. Function Calling Agent:
   - Direct function/tool invocation
   - Best for: Simple tool use
   
3. Planning Agent:
   - Plans entire workflow upfront
   - Best for: Complex tasks with clear steps
   
4. Conversational Agent:
   - Maintains dialogue context
   - Best for: Chat applications
   
5. Multi-Agent:
   - Specialized agents collaborate
   - Best for: Complex tasks requiring different skills

PRODUCTION CHECKLIST:

✅ Error Handling:
   - Graceful failure recovery
   - Retry logic for API calls
   - Timeout protection
   
✅ Cost Control:
   - Token usage monitoring
   - Max iteration limits
   - Caching for repeated queries
   
✅ Safety:
   - Input validation
   - Output filtering
   - Tool access restrictions
   
✅ Monitoring:
   - Log all agent actions
   - Track success/failure rates
   - Measure latency
   
✅ Testing:
   - Unit tests for tools
   - Integration tests for agent workflows
   - Evaluation on test cases
"""


if __name__ == "__main__":
    # Set your OpenAI API key
    # os.environ["OPENAI_API_KEY"] = "your-key-here"
    
    # Run the complete tutorial
    main()
