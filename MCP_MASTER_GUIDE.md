# 🔌 MODEL CONTEXT PROTOCOL (MCP) - BEGINNER TO EXPERT GUIDE

> **Created**: January 12, 2026  
> **Author**: Senior AI Systems Architect  
> **Target**: Smart Document Chat Project Enhancement  
> **Time Commitment**: 15-20 hours (over 2 weeks)

---

## 📋 TABLE OF CONTENTS

1. [What is MCP & Why It Matters](#part-1-foundations)
2. [MCP Architecture & Core Concepts](#part-2-architecture)
3. [Building Your First MCP Server](#part-3-first-server)
4. [Integrating MCP with Your RAG System](#part-4-integration)
5. [Advanced MCP Patterns](#part-5-advanced)
6. [Production Deployment](#part-6-production)

**Learning Path**: Foundation → Implementation → Integration → Production

**Prerequisites**: 
- Python 3.9+
- Understanding of your multi-agent system
- Basic knowledge of JSON-RPC
- Familiarity with async programming

---

## 🎯 LEARNING OUTCOMES

After completing this guide, you will:

✅ Understand MCP protocol fundamentals  
✅ Build custom MCP servers for your tools  
✅ Connect your CrewAI agents to MCP servers  
✅ Use community MCP servers (GitHub, Google Drive, etc.)  
✅ Implement security and permissions  
✅ Deploy MCP in production  

---

## 📊 YOUR TRANSFORMATION ROADMAP

### **Current State (Your Project)**
```
Smart Document Chat
├── Manual Tool Integration
│   ├── DocumentAnalyzerTool (custom)
│   ├── TextExtractorTool (custom)
│   ├── VectorSearchTool (custom)
│   └── 4 more custom tools
├── Direct Database Access
│   ├── ChromaDB (direct connection)
│   ├── Supabase (direct connection)
│   └── File system (direct access)
└── Limited Extensibility
    └── Adding new tools requires code changes
```

### **Target State (With MCP)**
```
Smart Document Chat + MCP
├── MCP Client Integration
│   └── Unified interface for all tools
├── MCP Servers (Standardized)
│   ├── Document Processing Server
│   ├── ChromaDB MCP Server
│   ├── Supabase MCP Server
│   ├── GitHub MCP Server (new!)
│   ├── Google Drive MCP Server (new!)
│   └── Web Search MCP Server (new!)
├── Better Security
│   ├── Permission-based access
│   ├── Isolated server processes
│   └── Audit logging
└── Easy Extensibility
    └── Add new servers without code changes
```

### **Expected Benefits**
- **Development Speed**: 40% faster to add new tools
- **Security**: Isolated permissions per server
- **Maintainability**: Use community servers (less custom code)
- **Flexibility**: Swap servers without changing agent code
- **Scalability**: Run servers on separate machines

---

## 🏗️ PART 1: FOUNDATIONS

### **What is MCP?**

**Model Context Protocol** is an open-source standard (created by Anthropic, Nov 2024) that defines how AI applications communicate with external data sources and tools.

**Core Idea**: Just like USB standardized hardware connections, MCP standardizes AI-to-tool connections.

### **Key Components**

```
┌──────────────────────────────────────────────────┐
│                  MCP CLIENT                       │
│  (Lives in your AI application)                  │
│  - Discovers available tools                     │
│  - Sends requests to servers                     │
│  - Receives responses                            │
└───────────────┬──────────────────────────────────┘
                │
                │ JSON-RPC over stdio/HTTP
                │
┌───────────────▼──────────────────────────────────┐
│                  MCP SERVER                       │
│  (Standalone process)                            │
│  - Exposes tools/resources/prompts               │
│  - Handles requests                              │
│  - Returns results                               │
└───────────────┬──────────────────────────────────┘
                │
                │ Direct access
                │
        ┌───────▼────────┐
        │  DATA SOURCE   │
        │  (ChromaDB,    │
        │   Files, APIs) │
        └────────────────┘
```

### **MCP vs Traditional Integration**

| Aspect | Traditional (Your Current) | MCP Standard |
|--------|---------------------------|--------------|
| **Tool Definition** | Custom Python classes | JSON schema |
| **Communication** | Direct function calls | JSON-RPC protocol |
| **Discovery** | Hard-coded | Dynamic discovery |
| **Security** | Shared process space | Isolated processes |
| **Reusability** | Project-specific | Cross-project |
| **Updates** | Manual code changes | Server updates |

### **MCP Protocol Basics**

MCP uses **JSON-RPC 2.0** for communication:

```json
// Request from Client
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_documents",
    "arguments": {
      "query": "revenue Q3 2024",
      "top_k": 5
    }
  }
}

// Response from Server
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Found 5 documents matching your query..."
      }
    ],
    "isError": false
  }
}
```

### **Three Core MCP Capabilities**

#### **1. Tools** (Functions agents can call)
```python
# Example: Document search tool
{
  "name": "search_documents",
  "description": "Search for documents by semantic similarity",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {"type": "string"},
      "top_k": {"type": "integer", "default": 5}
    }
  }
}
```

#### **2. Resources** (Data agents can read)
```python
# Example: Document resource
{
  "uri": "doc://user_1/financial_report.pdf",
  "name": "Financial Report 2024",
  "mimeType": "application/pdf",
  "description": "Q3 2024 financial analysis"
}
```

#### **3. Prompts** (Pre-built templates)
```python
# Example: Analysis prompt
{
  "name": "analyze_document",
  "description": "Analyze document with expert perspective",
  "arguments": [
    {"name": "doc_id", "required": true},
    {"name": "focus", "required": false}
  ]
}
```

---

## 🏗️ PART 2: MCP ARCHITECTURE

### **Communication Patterns**

#### **Pattern 1: Stdio Transport (Local)**
```python
# MCP Client launches server as subprocess
# Communication via stdin/stdout

CLIENT                    SERVER
  |                         |
  |---spawn subprocess----> |
  |                         |
  |--JSON-RPC over stdio--> |
  |                         |
  |<---JSON-RPC response--- |
  |                         |
```

**Use Case**: Local tools (file system, local DB, document processing)

#### **Pattern 2: HTTP/SSE Transport (Remote)**
```python
# MCP Client connects to remote server
# Communication via HTTP with Server-Sent Events

CLIENT                    SERVER
  |                         |
  |---HTTP POST request---> |
  |                         |
  |<--SSE stream response-- |
  |                         |
```

**Use Case**: Remote APIs (GitHub, Google Drive, web services)

### **Your Project's Ideal Architecture**

```
┌─────────────────────────────────────────────────────┐
│         Smart Document Chat (Streamlit)             │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │       Multi-Agent RAG Engine                  │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐     │ │
│  │  │Ingestion │ │Retrieval │ │Generation│     │ │
│  │  │  Agent   │ │  Agent   │ │  Agent   │     │ │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘     │ │
│  │       │            │            │            │ │
│  │       └────────────┼────────────┘            │ │
│  │                    │                         │ │
│  └────────────────────┼─────────────────────────┘ │
│                       │                           │
│              ┌────────▼────────┐                  │
│              │   MCP CLIENT    │                  │
│              │  (mcp library)  │                  │
│              └────────┬────────┘                  │
└───────────────────────┼───────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   ┌────▼─────┐   ┌────▼─────┐   ┌────▼─────┐
   │Document  │   │ChromaDB  │   │GitHub    │
   │Processing│   │Vector    │   │Repository│
   │Server    │   │Server    │   │Server    │
   │(Local)   │   │(Local)   │   │(Remote)  │
   └──────────┘   └──────────┘   └──────────┘
       │              │               │
   File System    ChromaDB       GitHub API
```

### **Server Lifecycle**

```python
# 1. Server Initialization
server = Server("document-processing-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(name="analyze_pdf", ...),
        Tool(name="extract_tables", ...),
    ]

# 2. Client Connection
client = MCPClient()
await client.connect_to_server("stdio", "document-processing-server")

# 3. Tool Discovery
tools = await client.list_tools()
# Returns: [analyze_pdf, extract_tables]

# 4. Tool Execution
result = await client.call_tool("analyze_pdf", {"path": "report.pdf"})

# 5. Server Shutdown
await client.disconnect()
await server.shutdown()
```

---

## 🛠️ PART 3: BUILDING YOUR FIRST MCP SERVER

### **Step 1: Install MCP SDK**

```bash
# Install official MCP Python SDK
pip install mcp

# Verify installation
python -c "from mcp import Server; print('MCP Ready!')"
```

### **Step 2: Create Simple Document Search Server**

Create `servers/document_search_server.py`:

```python
"""
MCP Server for Document Search
Exposes your ChromaDB vector search as an MCP tool
"""

import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config import config

# Initialize server
server = Server("document-search-server")

# Initialize embeddings and vector store
embeddings = HuggingFaceEmbeddings(
    model_name=config.HUGGINGFACE_MODEL,
    model_kwargs={'device': 'cpu'}
)

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_documents",
            description="Search documents by semantic similarity using vector embeddings",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID to search their documents"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query text"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5
                    },
                    "ai_provider": {
                        "type": "string",
                        "description": "AI provider (openai or gemini)",
                        "enum": ["openai", "gemini"],
                        "default": "gemini"
                    }
                },
                "required": ["user_id", "query"]
            }
        ),
        Tool(
            name="list_user_documents",
            description="List all documents for a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID"
                    }
                },
                "required": ["user_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute tool based on name"""
    
    if name == "search_documents":
        # Extract parameters
        user_id = arguments["user_id"]
        query = arguments["query"]
        top_k = arguments.get("top_k", 5)
        ai_provider = arguments.get("ai_provider", "gemini")
        
        try:
            # Load user's vector store
            collection_name = f"user_{user_id}_{ai_provider}"
            persist_dir = os.path.join(config.CHROMA_PERSIST_DIR, collection_name)
            
            if not os.path.exists(persist_dir):
                return [TextContent(
                    type="text",
                    text=f"No documents found for user {user_id}"
                )]
            
            # Create vector store connection
            vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings,
                collection_name=collection_name
            )
            
            # Perform search
            results = vectorstore.similarity_search_with_score(query, k=top_k)
            
            # Format results
            formatted_results = []
            for idx, (doc, score) in enumerate(results, 1):
                formatted_results.append(f"""
Result {idx} (Relevance: {1 - score:.2f}):
Content: {doc.page_content[:300]}...
Source: {doc.metadata.get('filename', 'Unknown')}
Page: {doc.metadata.get('page', 'N/A')}
""")
            
            response = f"Found {len(results)} relevant documents:\n\n" + "\n---\n".join(formatted_results)
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error searching documents: {str(e)}"
            )]
    
    elif name == "list_user_documents":
        user_id = arguments["user_id"]
        
        try:
            from utils.database import db_manager
            documents = db_manager.get_user_documents(user_id)
            
            if not documents:
                return [TextContent(
                    type="text",
                    text=f"No documents found for user {user_id}"
                )]
            
            doc_list = []
            for doc in documents:
                doc_list.append(f"- {doc.filename} ({doc.file_type}) - {doc.chunk_count} chunks")
            
            response = f"Documents for user {user_id}:\n" + "\n".join(doc_list)
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error listing documents: {str(e)}"
            )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### **Step 3: Test Your MCP Server**

Create `test_mcp_server.py`:

```python
"""
Test your MCP server
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_document_search():
    """Test document search MCP server"""
    
    # Server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["servers/document_search_server.py"],
        env=None
    )
    
    # Connect to server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            print("✅ Connected to MCP server")
            
            # List available tools
            tools_result = await session.list_tools()
            print(f"\n📦 Available tools: {len(tools_result.tools)}")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Call search_documents tool
            print("\n🔍 Testing document search...")
            search_result = await session.call_tool(
                "search_documents",
                arguments={
                    "user_id": "1",
                    "query": "revenue growth Q3 2024",
                    "top_k": 3
                }
            )
            
            print("\n📄 Search Results:")
            for content in search_result.content:
                print(content.text)
            
            # List user documents
            print("\n📚 Testing document listing...")
            list_result = await session.call_tool(
                "list_user_documents",
                arguments={"user_id": "1"}
            )
            
            print("\n📋 User Documents:")
            for content in list_result.content:
                print(content.text)

if __name__ == "__main__":
    asyncio.run(test_document_search())
```

**Run the test:**
```bash
python test_mcp_server.py
```

**Expected Output:**
```
✅ Connected to MCP server
📦 Available tools: 2
  - search_documents: Search documents by semantic similarity
  - list_user_documents: List all documents for a user

🔍 Testing document search...
📄 Search Results:
Found 3 relevant documents:

Result 1 (Relevance: 0.89):
Content: Q3 2024 revenue growth reached 15% compared to Q2...
Source: Financial_Report.pdf
Page: 12

Result 2 (Relevance: 0.85):
Content: Revenue performance in Q3 shows strong momentum...
Source: Financial_Report.pdf
Page: 13

---

📚 Testing document listing...
📋 User Documents:
Documents for user 1:
- Financial_Report.pdf (pdf) - 45 chunks
- Sales_Data.csv (csv) - 12 chunks
```

---

## 🔗 PART 4: INTEGRATING MCP WITH YOUR RAG SYSTEM

### **Step 1: Create MCP Client Wrapper**

Create `utils/mcp_client.py`:

```python
"""
MCP Client for Smart Document Chat
Manages connections to MCP servers
"""

import asyncio
from typing import Dict, List, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from loguru import logger

class MCPClientManager:
    """Manages multiple MCP server connections"""
    
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.servers: Dict[str, dict] = {
            "document-search": {
                "command": "python",
                "args": ["servers/document_search_server.py"],
                "description": "Document search and listing"
            },
            # Add more servers here
        }
    
    async def connect_server(self, server_name: str):
        """Connect to an MCP server"""
        if server_name in self.sessions:
            logger.info(f"Already connected to {server_name}")
            return
        
        if server_name not in self.servers:
            raise ValueError(f"Unknown server: {server_name}")
        
        server_config = self.servers[server_name]
        server_params = StdioServerParameters(
            command=server_config["command"],
            args=server_config["args"]
        )
        
        try:
            # This creates a context manager, we need to keep it alive
            # In production, use proper async context management
            read, write = await stdio_client(server_params).__aenter__()
            session = await ClientSession(read, write).__aenter__()
            await session.initialize()
            
            self.sessions[server_name] = session
            logger.info(f"✅ Connected to {server_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to {server_name}: {e}")
            raise
    
    async def list_tools(self, server_name: str) -> List[Any]:
        """List tools from a server"""
        if server_name not in self.sessions:
            await self.connect_server(server_name)
        
        session = self.sessions[server_name]
        result = await session.list_tools()
        return result.tools
    
    async def call_tool(
        self, 
        server_name: str, 
        tool_name: str, 
        arguments: dict
    ) -> str:
        """Call a tool on a server"""
        if server_name not in self.sessions:
            await self.connect_server(server_name)
        
        session = self.sessions[server_name]
        
        try:
            result = await session.call_tool(tool_name, arguments=arguments)
            
            # Extract text from result
            if result.content:
                return result.content[0].text
            return "No response"
            
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return f"Error: {str(e)}"
    
    async def disconnect_all(self):
        """Disconnect from all servers"""
        for server_name, session in self.sessions.items():
            try:
                # Proper cleanup would use __aexit__ but simplified here
                logger.info(f"Disconnecting from {server_name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {server_name}: {e}")
        
        self.sessions.clear()

# Global instance
mcp_client = MCPClientManager()
```

### **Step 2: Create MCP-Enabled CrewAI Tools**

Create `utils/mcp_tools.py`:

```python
"""
CrewAI tools that use MCP servers
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import asyncio
from utils.mcp_client import mcp_client

class MCPDocumentSearchInput(BaseModel):
    """Input for MCP document search"""
    user_id: str = Field(..., description="User ID")
    query: str = Field(..., description="Search query")
    top_k: int = Field(default=5, description="Number of results")

class MCPDocumentSearchTool(BaseTool):
    name: str = "MCP Document Search"
    description: str = "Search documents using MCP-powered vector search"
    
    def _run(self, user_id: str, query: str, top_k: int = 5) -> str:
        """Search documents via MCP server"""
        
        async def search():
            return await mcp_client.call_tool(
                server_name="document-search",
                tool_name="search_documents",
                arguments={
                    "user_id": user_id,
                    "query": query,
                    "top_k": top_k
                }
            )
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(search())
        loop.close()
        
        return result

class MCPListDocumentsInput(BaseModel):
    """Input for listing documents"""
    user_id: str = Field(..., description="User ID")

class MCPListDocumentsTool(BaseTool):
    name: str = "MCP List Documents"
    description: str = "List all user documents via MCP"
    
    def _run(self, user_id: str) -> str:
        """List documents via MCP server"""
        
        async def list_docs():
            return await mcp_client.call_tool(
                server_name="document-search",
                tool_name="list_user_documents",
                arguments={"user_id": user_id}
            )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(list_docs())
        loop.close()
        
        return result

# Export tools
def get_mcp_retrieval_tools():
    """Get MCP-powered retrieval tools for agents"""
    return [
        MCPDocumentSearchTool(),
        MCPListDocumentsTool()
    ]
```

### **Step 3: Update Your Retrieval Agent**

Modify `utils/agent_rag_engine.py`:

```python
# Add at top
from utils.mcp_tools import get_mcp_retrieval_tools

# Update _create_retrieval_agent method
def _create_retrieval_agent(self) -> Agent:
    """Create the information retrieval specialist agent"""
    return Agent(
        role='Information Retrieval Specialist',
        goal='Find the most relevant and accurate information for user queries',
        backstory="""You are an elite search and information retrieval expert...""",
        llm=self.llm,
        tools=get_mcp_retrieval_tools(),  # 🔥 Now uses MCP tools!
        verbose=True,
        allow_delegation=False,
        max_iter=10
    )
```

### **Step 4: Test Integration**

```python
# test_mcp_integration.py

from utils.agent_rag_engine import MultiAgentRAGEngine

async def test_mcp_retrieval():
    """Test agent with MCP tools"""
    
    engine = MultiAgentRAGEngine()
    
    result = await engine.query(
        question="What was the revenue growth in Q3 2024?",
        user_id="1"
    )
    
    print("✅ Query Result:")
    print(result['response'])
    print("\n📚 Sources:")
    for source in result['sources']:
        print(f"  - {source['filename']} (Page {source['page']})")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_mcp_retrieval())
```

---

## 🚀 PART 5: ADVANCED MCP PATTERNS

### **Pattern 1: Multi-Server Orchestration**

```python
# servers/orchestrator_server.py
"""
Meta-server that coordinates multiple MCP servers
"""

from mcp.server import Server
from mcp.types import Tool
import asyncio

server = Server("orchestrator-server")

# Connect to multiple servers
document_server = MCPClient("document-search")
github_server = MCPClient("github")
web_search_server = MCPClient("web-search")

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Route tool calls to appropriate server"""
    
    if name.startswith("doc_"):
        # Route to document server
        return await document_server.call_tool(
            name.replace("doc_", ""),
            arguments
        )
    elif name.startswith("github_"):
        # Route to GitHub server
        return await github_server.call_tool(
            name.replace("github_", ""),
            arguments
        )
    elif name.startswith("web_"):
        # Route to web search server
        return await web_search_server.call_tool(
            name.replace("web_", ""),
            arguments
        )
```

### **Pattern 2: Caching & Performance**

```python
# utils/mcp_cache.py
"""
Cache MCP tool results for performance
"""

from functools import lru_cache
from typing import Any
import hashlib
import json

class MCPCache:
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
    
    def _cache_key(self, server: str, tool: str, args: dict) -> str:
        """Generate cache key"""
        key_data = f"{server}:{tool}:{json.dumps(args, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_or_call(
        self, 
        server: str, 
        tool: str, 
        args: dict,
        ttl: int = 300  # 5 minutes
    ) -> Any:
        """Get from cache or call server"""
        cache_key = self._cache_key(server, tool, args)
        
        if cache_key in self.cache:
            cached_value, timestamp = self.cache[cache_key]
            if time.time() - timestamp < ttl:
                return cached_value
        
        # Call server
        result = await mcp_client.call_tool(server, tool, args)
        
        # Store in cache
        self.cache[cache_key] = (result, time.time())
        
        # Evict old entries if cache is full
        if len(self.cache) > self.max_size:
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k][1]
            )
            del self.cache[oldest_key]
        
        return result

mcp_cache = MCPCache()
```

### **Pattern 3: Error Handling & Retries**

```python
# utils/mcp_retry.py
"""
Robust MCP call with retries
"""

import asyncio
from typing import Any
from loguru import logger

async def mcp_call_with_retry(
    server: str,
    tool: str,
    arguments: dict,
    max_retries: int = 3,
    backoff: float = 1.0
) -> Any:
    """Call MCP tool with exponential backoff retry"""
    
    for attempt in range(max_retries):
        try:
            result = await mcp_client.call_tool(server, tool, arguments)
            return result
            
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"MCP call failed after {max_retries} attempts: {e}")
                raise
            
            wait_time = backoff * (2 ** attempt)
            logger.warning(f"MCP call failed (attempt {attempt + 1}), retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)
```

### **Pattern 4: Permission System**

```python
# utils/mcp_permissions.py
"""
Permission-based access to MCP servers
"""

from typing import Dict, Set
from enum import Enum

class Permission(Enum):
    READ_DOCUMENTS = "read_documents"
    WRITE_DOCUMENTS = "write_documents"
    DELETE_DOCUMENTS = "delete_documents"
    ADMIN = "admin"

class PermissionManager:
    def __init__(self):
        self.user_permissions: Dict[str, Set[Permission]] = {}
    
    def grant_permission(self, user_id: str, permission: Permission):
        """Grant permission to user"""
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = set()
        self.user_permissions[user_id].add(permission)
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has permission"""
        if user_id not in self.user_permissions:
            return False
        
        # Admin has all permissions
        if Permission.ADMIN in self.user_permissions[user_id]:
            return True
        
        return permission in self.user_permissions[user_id]
    
    async def call_tool_with_permission(
        self,
        user_id: str,
        server: str,
        tool: str,
        arguments: dict,
        required_permission: Permission
    ):
        """Call MCP tool if user has permission"""
        if not self.has_permission(user_id, required_permission):
            raise PermissionError(
                f"User {user_id} does not have {required_permission.value} permission"
            )
        
        return await mcp_client.call_tool(server, tool, arguments)

permission_manager = PermissionManager()
```

---

## 🏭 PART 6: PRODUCTION DEPLOYMENT

### **Step 1: Environment Configuration**

Update `.env`:
```bash
# MCP Configuration
MCP_ENABLED=true
MCP_SERVERS_DIR=./servers
MCP_LOG_LEVEL=INFO
MCP_TIMEOUT_SECONDS=30
MCP_MAX_RETRIES=3

# Server-specific configs
MCP_DOCUMENT_SEARCH_ENABLED=true
MCP_GITHUB_ENABLED=false
MCP_GDRIVE_ENABLED=false
```

### **Step 2: Server Management Script**

Create `scripts/manage_mcp_servers.py`:

```python
"""
Manage MCP servers lifecycle
"""

import asyncio
import signal
import sys
from typing import Dict, List
from loguru import logger
from utils.mcp_client import mcp_client

class MCPServerManager:
    def __init__(self):
        self.running = True
        self.health_check_interval = 60  # seconds
    
    async def start_all_servers(self):
        """Start all configured MCP servers"""
        logger.info("🚀 Starting MCP servers...")
        
        servers = ["document-search"]  # Add more as needed
        
        for server in servers:
            try:
                await mcp_client.connect_server(server)
                logger.info(f"✅ Started {server}")
            except Exception as e:
                logger.error(f"❌ Failed to start {server}: {e}")
    
    async def health_check(self):
        """Periodic health check for all servers"""
        while self.running:
            for server_name in mcp_client.sessions.keys():
                try:
                    # Try to list tools as health check
                    await mcp_client.list_tools(server_name)
                    logger.debug(f"✅ {server_name} healthy")
                except Exception as e:
                    logger.warning(f"⚠️ {server_name} unhealthy: {e}")
                    # Attempt reconnect
                    try:
                        await mcp_client.connect_server(server_name)
                    except Exception as reconnect_error:
                        logger.error(f"Failed to reconnect {server_name}: {reconnect_error}")
            
            await asyncio.sleep(self.health_check_interval)
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down MCP servers...")
        self.running = False
        await mcp_client.disconnect_all()
        logger.info("✅ All servers stopped")
    
    def handle_signal(self, sig):
        """Handle shutdown signals"""
        logger.info(f"Received signal {sig}, initiating shutdown...")
        asyncio.create_task(self.shutdown())

async def main():
    manager = MCPServerManager()
    
    # Setup signal handlers
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: manager.handle_signal(sig))
    
    # Start servers
    await manager.start_all_servers()
    
    # Run health checks
    await manager.health_check()

if __name__ == "__main__":
    asyncio.run(main())
```

### **Step 3: Docker Deployment**

Create `docker/mcp-servers.Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install mcp

# Copy application
COPY . .

# Expose MCP server ports (if using HTTP transport)
EXPOSE 8000-8010

# Run server manager
CMD ["python", "scripts/manage_mcp_servers.py"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # Main application
  smart-doc-chat:
    build: .
    ports:
      - "8501:8501"
    environment:
      - MCP_ENABLED=true
    depends_on:
      - mcp-servers
    volumes:
      - ./data:/app/data
  
  # MCP servers
  mcp-servers:
    build:
      context: .
      dockerfile: docker/mcp-servers.Dockerfile
    environment:
      - MCP_LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./servers:/app/servers
  
  # ChromaDB (if separate)
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma

volumes:
  chroma_data:
```

### **Step 4: Monitoring & Logging**

Create `utils/mcp_monitor.py`:

```python
"""
Monitor MCP server performance
"""

from typing import Dict, List
import time
from dataclasses import dataclass
from loguru import logger

@dataclass
class ServerMetrics:
    server_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_latency: float = 0.0
    avg_latency: float = 0.0

class MCPMonitor:
    def __init__(self):
        self.metrics: Dict[str, ServerMetrics] = {}
    
    async def track_call(
        self,
        server_name: str,
        tool_name: str,
        func
    ):
        """Track a tool call with timing and success metrics"""
        if server_name not in self.metrics:
            self.metrics[server_name] = ServerMetrics(server_name)
        
        metrics = self.metrics[server_name]
        start_time = time.time()
        
        try:
            result = await func()
            
            # Track success
            metrics.successful_calls += 1
            metrics.total_calls += 1
            
            # Track latency
            latency = time.time() - start_time
            metrics.total_latency += latency
            metrics.avg_latency = metrics.total_latency / metrics.total_calls
            
            logger.debug(f"✅ {server_name}.{tool_name} completed in {latency:.2f}s")
            
            return result
            
        except Exception as e:
            metrics.failed_calls += 1
            metrics.total_calls += 1
            
            logger.error(f"❌ {server_name}.{tool_name} failed: {e}")
            raise
    
    def get_dashboard(self) -> str:
        """Generate monitoring dashboard"""
        dashboard = "=== MCP Server Metrics ===\n\n"
        
        for server_name, metrics in self.metrics.items():
            success_rate = (
                (metrics.successful_calls / metrics.total_calls * 100)
                if metrics.total_calls > 0 else 0
            )
            
            dashboard += f"""
Server: {server_name}
  Total Calls: {metrics.total_calls}
  Successful: {metrics.successful_calls} ({success_rate:.1f}%)
  Failed: {metrics.failed_calls}
  Avg Latency: {metrics.avg_latency:.3f}s
"""
        
        return dashboard

mcp_monitor = MCPMonitor()
```

---

## 📚 PART 7: USING COMMUNITY MCP SERVERS

### **Popular MCP Servers for Your Project**

#### **1. GitHub MCP Server**

```bash
# Install
npm install -g @modelcontextprotocol/server-github

# Configure
{
  "mcpServers": {
    "github": {
      "command": "mcp-server-github",
      "args": [],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

**Use Case**: Search code repositories, read issues, create PRs

```python
# Example: Search GitHub for relevant code
result = await mcp_client.call_tool(
    "github",
    "search_code",
    {"query": "document chunking python", "repo": "langchain-ai/langchain"}
)
```

#### **2. Google Drive MCP Server**

```bash
# Install
npm install -g @modelcontextprotocol/server-gdrive
```

**Use Case**: Access documents from Google Drive

#### **3. Brave Search MCP Server**

```bash
# Install
npm install -g @modelcontextprotocol/server-brave-search
```

**Use Case**: Web search for augmenting document answers

### **Integration Example**

```python
# utils/enhanced_mcp_client.py

class EnhancedMCPClient(MCPClientManager):
    """Extended MCP client with community servers"""
    
    def __init__(self):
        super().__init__()
        
        # Add community servers
        self.servers.update({
            "github": {
                "command": "mcp-server-github",
                "args": [],
                "description": "GitHub repository access"
            },
            "brave-search": {
                "command": "mcp-server-brave-search",
                "args": [],
                "description": "Web search"
            }
        })
    
    async def hybrid_search(
        self,
        user_id: str,
        query: str,
        include_web: bool = False
    ):
        """Search both documents and web"""
        
        # Search local documents
        doc_results = await self.call_tool(
            "document-search",
            "search_documents",
            {"user_id": user_id, "query": query}
        )
        
        results = {"documents": doc_results}
        
        # Optionally search web
        if include_web:
            web_results = await self.call_tool(
                "brave-search",
                "search",
                {"query": query, "count": 5}
            )
            results["web"] = web_results
        
        return results
```

---

## 🎯 PART 8: MIGRATION PATH FOR YOUR PROJECT

### **Phase 1: Pilot (Week 1)**
✅ Build document search MCP server  
✅ Test with existing retrieval agent  
✅ Measure performance vs current implementation  

### **Phase 2: Core Integration (Week 2)**
✅ Migrate all ingestion tools to MCP  
✅ Migrate all retrieval tools to MCP  
✅ Update agent configurations  
✅ Add monitoring  

### **Phase 3: Enhancement (Week 3)**
✅ Add community MCP servers (GitHub, Google Drive)  
✅ Implement caching layer  
✅ Add permission system  
✅ Performance optimization  

### **Phase 4: Production (Week 4)**
✅ Docker deployment  
✅ Load testing  
✅ Documentation  
✅ Rollout to users  

---

## 📊 EXPECTED IMPROVEMENTS

| Metric | Before MCP | After MCP | Improvement |
|--------|-----------|-----------|-------------|
| **Tool Addition Time** | 4 hours | 30 minutes | 87% faster |
| **Code Maintainability** | Custom tools | Standard protocol | Much better |
| **Extensibility** | Limited | Unlimited | Infinite |
| **Security** | Shared process | Isolated | Better |
| **Community Tools** | 0 | 100+ | Huge ecosystem |

---

## 🎓 LEARNING RESOURCES

### **Official Documentation**
- MCP Specification: https://spec.modelcontextprotocol.io
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Server Examples: https://github.com/modelcontextprotocol/servers

### **Community**
- Discord: https://discord.gg/modelcontextprotocol
- GitHub Discussions: https://github.com/modelcontextprotocol/discussions

### **Video Tutorials**
- "Building MCP Servers" - Anthropic
- "MCP for Python Developers"

---

## ✅ COMPLETION CHECKLIST

**After completing this guide, you should be able to:**

- [ ] Explain MCP architecture and benefits
- [ ] Build custom MCP servers for your tools
- [ ] Connect MCP servers to your agents
- [ ] Use community MCP servers
- [ ] Implement caching and error handling
- [ ] Deploy MCP in production
- [ ] Monitor MCP performance
- [ ] Troubleshoot MCP issues

---

## 🚀 NEXT STEPS

1. **Start with Part 3** - Build your first MCP server
2. **Test thoroughly** - Use test_mcp_server.py
3. **Integrate gradually** - One agent at a time
4. **Monitor performance** - Track metrics
5. **Expand ecosystem** - Add community servers

**Remember**: MCP is a tool to enhance your system, not replace it. Start small, measure impact, scale gradually.

---

## 💬 QUESTIONS & SUPPORT

If you encounter issues:
1. Check server logs
2. Verify JSON-RPC protocol compliance
3. Test with simple examples first
4. Consult MCP Discord community

**Happy Building with MCP!** 🎉
