# 🎨 Visual Guide: Tools & Tool Calling

## 📊 Visual Comparison

### **Human with Tools vs AI Agent with Tools**

```
┌─────────────────────────────────────────────────────────────┐
│                    HUMAN CARPENTER                          │
│                                                             │
│  Brain: "I need to cut this wood"                          │
│    ↓                                                        │
│  Decision: "I'll use my SAW"                               │
│    ↓                                                        │
│  Action: Picks up saw, cuts wood                           │
│    ↓                                                        │
│  Result: Wood is cut                                        │
│                                                             │
│  Tools Available:                                           │
│  🪚 Saw - For cutting                                       │
│  🔨 Hammer - For nailing                                    │
│  📏 Ruler - For measuring                                   │
└─────────────────────────────────────────────────────────────┘

                        SAME AS ↓

┌─────────────────────────────────────────────────────────────┐
│                    AI AGENT                                 │
│                                                             │
│  Brain: "I need to read this PDF"                          │
│    ↓                                                        │
│  Decision: "I'll use my PDFReaderTool"                     │
│    ↓                                                        │
│  Action: Calls PDFReaderTool.run("file.pdf")              │
│    ↓                                                        │
│  Result: Text extracted from PDF                            │
│                                                             │
│  Tools Available:                                           │
│  📄 PDFReaderTool - For reading PDFs                       │
│  🔍 SearchTool - For searching                             │
│  ✍️ WriterTool - For generating text                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Tool Calling Flow - Detailed Visual

### **Example: "What's the weather in London?"**

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 1️⃣ USER ASKS QUESTION                                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
  👤 User: "What's the weather in London?"
         ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 2️⃣ AGENT RECEIVES & ANALYZES                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
  🤖 Agent: Received "What's the weather in London?"
  
  🧠 Agent's Internal Thoughts:
     ┌─────────────────────────────────────────┐
     │ "Let me analyze this question..."      │
     │                                         │
     │ Keywords: weather, London               │
     │ Intent: Get current weather data        │
     │ My Knowledge: I don't know current      │
     │              weather (I'm just text)    │
     │                                         │
     │ Do I have a tool for this? Let me check│
     └─────────────────────────────────────────┘
         ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 3️⃣ AGENT CHECKS AVAILABLE TOOLS                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
  🤖 Agent: "Let me see what tools I have..."
  
  📋 Agent's Toolbox:
     ┌─────────────────────────────────────────────────┐
     │ ✅ WeatherTool                                  │
     │    Name: "Weather Checker"                      │
     │    Description: "Gets current weather for       │
     │                  a city. Use when you need      │
     │                  current weather information."  │
     │    Input: city (string)                         │
     │    Output: weather description (string)         │
     ├─────────────────────────────────────────────────┤
     │ ❌ CalculatorTool (not needed for this)        │
     │ ❌ TranslatorTool (not needed for this)        │
     └─────────────────────────────────────────────────┘
  
  💡 Agent Decision:
     "Perfect! WeatherTool is exactly what I need!"
         ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 4️⃣ AGENT PREPARES TOOL CALL                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
  🤖 Agent: "I'll prepare the parameters..."
  
  📝 Preparation:
     ┌─────────────────────────────────────────┐
     │ Tool to call: WeatherTool               │
     │ Function: WeatherTool.run()             │
     │ Parameters needed: city                 │
     │ Value to pass: "London"                 │
     │                                         │
     │ Final call:                             │
     │   WeatherTool.run(city="London")       │
     └─────────────────────────────────────────┘
         ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 5️⃣ TOOL EXECUTES (This is the "Tool Calling")             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
  🛠️ WeatherTool.run(city="London")
  
  ⚙️ Inside the Tool:
     ┌──────────────────────────────────────────┐
     │ def _run(self, city: str) -> str:       │
     │     # 1. Call weather API               │
     │     api_url = f"weather-api.com/{city}"  │
     │     response = requests.get(api_url)     │
     │                                          │
     │     # 2. Parse response                 │
     │     data = response.json()               │
     │     # data = {                           │
     │     #   "temp": 62,                      │
     │     #   "condition": "Rainy"             │
     │     # }                                  │
     │                                          │
     │     # 3. Format result                  │
     │     result = f"Temperature: {data['temp']}°F" │
     │     result += f", Condition: {data['condition']}" │
     │                                          │
     │     # 4. Return to agent                │
     │     return result                        │
     └──────────────────────────────────────────┘
  
  📤 Tool Returns:
     "Temperature: 62°F, Condition: Rainy"
         ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 6️⃣ AGENT RECEIVES RESULT                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
  🤖 Agent: "Great! I got the weather data"
  
  📨 Received from tool:
     "Temperature: 62°F, Condition: Rainy"
  
  🧠 Agent Thinks:
     "Now I can answer the user's question!"
         ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 7️⃣ AGENT CREATES FINAL RESPONSE                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
  🤖 Agent: "Let me craft a nice response..."
  
  ✍️ Agent Generates:
     ┌─────────────────────────────────────────┐
     │ Input from tool:                        │
     │   "Temperature: 62°F, Condition: Rainy" │
     │                                         │
     │ Agent's response:                       │
     │   "The weather in London is currently   │
     │    62°F and rainy. You might want to    │
     │    bring an umbrella!"                  │
     └─────────────────────────────────────────┘
         ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 8️⃣ USER RECEIVES ANSWER                                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
  👤 User sees:
     "The weather in London is currently 62°F and rainy. 
      You might want to bring an umbrella!"
  
  😊 User is happy with accurate, real-time information!
```

---

## 🏢 Multi-Agent Collaboration Visual

### **Scenario: User uploads a PDF and asks a question**

```
┌─────────────────────────────────────────────────────────────────┐
│  USER UPLOADS: "research_paper.pdf"                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
╔═════════════════════════════════════════════════════════════════╗
║  📄 INGESTION AGENT (Document Processor)                        ║
║  "I'm the expert at processing documents!"                      ║
╚═════════════════════════════════════════════════════════════════╝
         │
         │ 🧠 Agent Thinks: "I need to process this PDF"
         │
         ├──► 🛠️ TOOL CALL #1: DocumentAnalyzerTool
         │         Input: "research_paper.pdf"
         │         Output: {type: "pdf", pages: 50, recommend: "PyPDF2"}
         │    ✅ "It's a 50-page PDF. Use PyPDF2."
         │
         ├──► 🛠️ TOOL CALL #2: TextExtractorTool
         │         Input: "research_paper.pdf", strategy: "standard"
         │         Output: "Abstract: This paper...\n[50k characters]"
         │    ✅ "Extracted 50,000 characters of text"
         │
         ├──► 🛠️ TOOL CALL #3: DocumentChunkerTool
         │         Input: [50k chars], chunk_size: 1000, overlap: 200
         │         Output: {chunks: [125 chunks], avg_size: 980}
         │    ✅ "Created 125 intelligent chunks"
         │
         └──► 💾 Stores in Vector Database
              ✅ "Document ready for searching!"

═══════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│  USER ASKS: "What are the main findings?"                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
╔═════════════════════════════════════════════════════════════════╗
║  🔍 RETRIEVAL AGENT (Search Specialist)                         ║
║  "I'm the expert at finding information!"                       ║
╚═════════════════════════════════════════════════════════════════╝
         │
         │ 🧠 Agent Thinks: "I need to find info about findings"
         │
         ├──► 🛠️ TOOL CALL #1: QueryAnalyzerTool
         │         Input: "What are the main findings?"
         │         Output: {
         │           query_type: "factual",
         │           key_terms: ["findings", "results", "conclusions"],
         │           reformulations: ["What were the results?"]
         │         }
         │    ✅ "User wants factual results from the paper"
         │
         ├──► 🛠️ TOOL CALL #2: VectorSearchTool
         │         Input: query: "main findings results", k: 5
         │         Output: [
         │           {content: "The main finding was...", score: 0.91},
         │           {content: "Results showed...", score: 0.88},
         │           {content: "We concluded...", score: 0.85},
         │           {content: "Key discovery...", score: 0.82}
         │         ]
         │    ✅ "Found 4 highly relevant chunks (85-91% match)"
         │
         │ 📦 Agent Packages Results:
         │    {
         │      chunks: [4 relevant pieces],
         │      sources: ["page 8", "page 15", "page 17"],
         │      confidence: 0.89
         │    }
         │
         └──► Passes to Generation Agent ──────┐
                                                │
                                                ▼
╔═════════════════════════════════════════════════════════════════╗
║  ✍️ GENERATION AGENT (Response Writer)                          ║
║  "I'm the expert at creating great responses!"                  ║
╚═════════════════════════════════════════════════════════════════╝
         │
         │ 📥 Receives from Retrieval Agent:
         │    - Original question
         │    - 4 relevant chunks
         │    - Source pages
         │
         │ 🧠 Agent Thinks: "I'll synthesize this into a clear answer"
         │
         ├──► ✍️ Agent Writes Initial Response:
         │         "Based on the research paper, the main findings are:
         │          1. The method achieved 95% accuracy...
         │          2. Processing time reduced by 40%...
         │          3. Results showed statistical significance..."
         │
         ├──► 🛠️ TOOL CALL #1: CitationFormatterTool
         │         Input: [response text], [source metadata]
         │         Output: "...accuracy (Page 8)...time (Page 15)..."
         │    ✅ "Added proper citations"
         │
         ├──► 🛠️ TOOL CALL #2: ResponseValidatorTool
         │         Input: [final response], [original chunks]
         │         Output: {
         │           validation_score: 0.98,
         │           hallucinations: [],
         │           accuracy: "high"
         │         }
         │    ✅ "Response is 98% accurate, no made-up facts"
         │
         └──► 📤 Returns Final Response to User

═══════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│  USER RECEIVES RESPONSE:                                         │
│                                                                  │
│  "Based on the research paper, here are the main findings:      │
│                                                                  │
│  1. **Primary Finding**: The method achieved 95% accuracy,     │
│     significantly outperforming the baseline (Page 8)           │
│                                                                  │
│  2. **Secondary Finding**: Processing time was reduced by 40%  │
│     compared to traditional approaches (Page 15)                │
│                                                                  │
│  3. **Statistical Significance**: All results showed p < 0.001  │
│     indicating high confidence (Page 17)                        │
│                                                                  │
│  **Sources:** Pages 8, 15, and 17 from research_paper.pdf"     │
│                                                                  │
│  😊 User is extremely satisfied!                                │
└─────────────────────────────────────────────────────────────────┘

╔═════════════════════════════════════════════════════════════════╗
║  📊 SUMMARY OF AGENT COLLABORATION:                             ║
║                                                                  ║
║  📄 Ingestion Agent: Made 3 tool calls → Processed document     ║
║  🔍 Retrieval Agent: Made 2 tool calls → Found information      ║
║  ✍️ Generation Agent: Made 2 tool calls → Created response      ║
║                                                                  ║
║  Total: 3 Agents, 7 Tool Calls, 1 Happy User! 🎉              ║
╚═════════════════════════════════════════════════════════════════╝
```

---

## 🎯 Tool Call Anatomy

### **Breaking Down a Single Tool Call**

```
┌─────────────────────────────────────────────────────────────────┐
│  TOOL CALL STRUCTURE                                             │
└─────────────────────────────────────────────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  BEFORE THE CALL                                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🤖 Agent State:
   ┌──────────────────────────────────────┐
   │ Current Task: "Need to read PDF"    │
   │ Available Tools: [DocumentAnalyzer,  │
   │                   TextExtractor,     │
   │                   DocumentChunker]   │
   │ Decision: "Use TextExtractor"        │
   └──────────────────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  DURING THE CALL                                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📞 Tool Call:
   ┌──────────────────────────────────────────────┐
   │ TextExtractorTool.run(                       │
   │     file_path = "research_paper.pdf",        │
   │     strategy = "standard"                    │
   │ )                                            │
   └──────────────────────────────────────────────┘
        │
        ▼
   ⚙️ Tool Execution:
   ┌──────────────────────────────────────────────┐
   │ 1. Validate inputs ✓                        │
   │    - file_path exists? Yes                  │
   │    - strategy valid? Yes                    │
   │                                              │
   │ 2. Open file                                │
   │    pdf = PyPDF2.PdfReader(file_path)        │
   │                                              │
   │ 3. Extract text from each page              │
   │    for page in pdf.pages:                   │
   │        text += page.extract_text()          │
   │                                              │
   │ 4. Format output                            │
   │    result = "Page 1:\n..." + text           │
   │                                              │
   │ 5. Return result                            │
   │    return result                            │
   └──────────────────────────────────────────────┘
        │
        ▼
   📤 Tool Returns:
   ┌──────────────────────────────────────────────┐
   │ "--- Page 1 ---                              │
   │  Abstract: This paper discusses...           │
   │  --- Page 2 ---                              │
   │  Introduction: Machine learning is...        │
   │  ...                                         │
   │  --- Page 50 ---                             │
   │  Conclusion: Our results show..."            │
   │                                              │
   │ [Total: 50,000 characters]                   │
   └──────────────────────────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  AFTER THE CALL                                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🤖 Agent State Updated:
   ┌──────────────────────────────────────┐
   │ Previous Task: "Read PDF" ✅         │
   │ Result Received: [50k chars]         │
   │ Next Task: "Chunk the text"          │
   │ Next Tool: DocumentChunker           │
   └──────────────────────────────────────┘
```

---

## 🔄 Agent Decision Tree

### **How Agent Decides Which Tool to Use**

```
                    USER QUESTION
                         │
                         ▼
           ┌─────────────────────────┐
           │  Agent Analyzes Task    │
           └─────────┬───────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
   Need Data?              Have Knowledge?
   (External)              (Internal)
         │                       │
         YES                     NO
         │                       │
         ▼                       ▼
┌─────────────────┐      Use General
│ Check Tools     │      Knowledge
└────────┬────────┘      (No tool needed)
         │
         ▼
┌─────────────────────────────────────┐
│ For each tool:                      │
│   Does tool description match need? │
└────────┬────────────────────────────┘
         │
    ┌────┴────┐
    │         │
    YES       NO
    │         │
    ▼         ▼
Use This   Try Next
Tool!      Tool
    │
    ▼
┌─────────────────┐
│ Prepare Inputs  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Call Tool       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Get Result      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Use Result to   │
│ Answer User     │
└─────────────────┘
```

---

## 📚 Real Code Example Annotated

### **From Your Project: agent_tools.py**

```python
# ============================================================
# THIS IS A TOOL DEFINITION
# ============================================================

class VectorSearchTool(BaseTool):
    """
    This is a TOOL that agents can use.
    
    Think of it as a specialized employee that knows
    how to search through documents.
    """
    
    # --------------------------------------------------------
    # TOOL METADATA (What agents see)
    # --------------------------------------------------------
    
    name: str = "Vector Search"
    # ↑ This is how the agent refers to this tool
    
    description: str = "Searches vector database for semantically similar content"
    # ↑ This tells the agent WHEN to use this tool
    #   Agent thinks: "User wants to search documents? Use Vector Search!"
    
    # --------------------------------------------------------
    # TOOL FUNCTION (What the tool actually does)
    # --------------------------------------------------------
    
    def _run(self, query: str, collection_name: str, n_results: int = 5) -> str:
        """
        This function runs when an agent calls this tool.
        
        Parameters the agent must provide:
        - query: What to search for (e.g., "machine learning")
        - collection_name: Which document collection to search
        - n_results: How many results to return (default: 5)
        
        Returns:
        - String containing search results (usually JSON format)
        """
        
        try:
            # ============================================
            # STEP 1: Load the vector database
            # ============================================
            
            from langchain_community.vectorstores import Chroma
            from langchain_huggingface import HuggingFaceEmbeddings
            
            # Initialize embeddings (converts text to numbers)
            embeddings = HuggingFaceEmbeddings(
                model_name=config.HUGGINGFACE_MODEL
            )
            
            # Load the specific collection
            persist_dir = os.path.join(config.CHROMA_PERSIST_DIR, collection_name)
            
            if not os.path.exists(persist_dir):
                return f"Collection not found: {collection_name}"
            
            vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings
            )
            
            # ============================================
            # STEP 2: Search for similar content
            # ============================================
            
            # Convert query to vector and find similar vectors
            # Example: "machine learning" → [0.23, -0.45, 0.67, ...]
            #          Then find vectors that are mathematically close
            results = vectorstore.similarity_search_with_score(query, k=n_results)
            
            # ============================================
            # STEP 3: Format results for agent
            # ============================================
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content[:500],    # First 500 chars
                    "relevance_score": round(float(score), 3),
                    "metadata": doc.metadata  # filename, page, etc.
                })
            
            # ============================================
            # STEP 4: Return to agent as JSON string
            # ============================================
            
            return json.dumps(formatted_results, indent=2)
            
        except Exception as e:
            # If something goes wrong, tell the agent
            logger.error(f"Vector search error: {e}")
            return f"Error searching: {str(e)}"


# ============================================================
# HOW AN AGENT USES THIS TOOL
# ============================================================

# When Retrieval Agent needs to search:

# Agent thinks: "I need to find documents about 'machine learning'"
# Agent checks tools: "I have VectorSearchTool!"
# Agent reads description: "Searches vector database for similar content" ✓
# Agent decides: "Perfect! This is what I need"

# Agent calls:
result = VectorSearchTool().run(
    query="machine learning",
    collection_name="user_123_gemini",
    n_results=5
)

# Tool executes (all the code above runs)

# Tool returns JSON:
# [
#   {
#     "content": "Machine learning is a subset of AI...",
#     "relevance_score": 0.912,
#     "metadata": {"filename": "ai_book.pdf", "page": 5}
#   },
#   ...
# ]

# Agent receives result and uses it to answer user!
```

---

## ✅ Key Takeaways

### **1. Tools Are Like Apps on Your Phone**
```
📱 Your Phone:
   📷 Camera App - Takes photos
   🗺️ Maps App - Gives directions
   ☀️ Weather App - Shows weather

🤖 Your Agent:
   📄 PDFReader Tool - Reads PDFs
   🔍 VectorSearch Tool - Searches documents
   ✍️ Writer Tool - Generates text
```

### **2. Tool Calling Is Like Making a Phone Call**
```
You want pizza 🍕:
1. You realize you need pizza (identify need)
2. You find pizza place number (identify tool)
3. You call the number (tool call)
4. They make pizza (tool executes)
5. Pizza arrives (tool returns result)
6. You eat pizza (use result) 😊

Agent wants data 📊:
1. Agent realizes it needs data (identify need)
2. Agent finds the right tool (identify tool)
3. Agent calls the tool (tool call)
4. Tool gets data (tool executes)
5. Tool returns data (tool returns result)
6. Agent uses data (use result) 😊
```

### **3. Multi-Agent Is Like a Restaurant Kitchen**
```
🍽️ Restaurant:
   👨‍🍳 Head Chef - Coordinates everyone
   🥗 Salad Chef - Makes salads
   🍝 Pasta Chef - Makes pasta
   🍰 Pastry Chef - Makes desserts
   
   Result: Better food, faster service!

🤖 Multi-Agent System:
   📄 Ingestion Agent - Processes documents
   🔍 Retrieval Agent - Finds information
   ✍️ Generation Agent - Writes responses
   
   Result: Better answers, higher quality!
```

---

## 🎉 You Now Understand!

**Congratulations!** You can now:
- ✅ Explain what AI agents are
- ✅ Understand what tools do
- ✅ Follow tool calling sequences
- ✅ See how agents collaborate
- ✅ Read and modify the code!

**Your project uses professional AI architecture!** 🏆

Now go read `utils/agent_tools.py` and `utils/agent_rag_engine.py` with your new understanding - everything will make sense! 🚀
