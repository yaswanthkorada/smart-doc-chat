"""
Quick Test Script for Multi-Agent RAG System
Run this to verify agents are working correctly
"""

from utils.agent_rag_engine import agent_rag_engine
from config import config
from loguru import logger

def test_agent_initialization():
    """Test that all agents are initialized"""
    print("\n" + "="*60)
    print("🤖 TESTING MULTI-AGENT SYSTEM")
    print("="*60)
    
    print("\n1️⃣ Testing Agent Initialization...")
    
    try:
        # Check if agents exist
        assert agent_rag_engine.ingestion_agent is not None
        assert agent_rag_engine.retrieval_agent is not None
        assert agent_rag_engine.generation_agent is not None
        
        print("   ✅ Ingestion Agent: " + agent_rag_engine.ingestion_agent.role)
        print("   ✅ Retrieval Agent: " + agent_rag_engine.retrieval_agent.role)
        print("   ✅ Generation Agent: " + agent_rag_engine.generation_agent.role)
        
        print("\n   ✅ ALL AGENTS INITIALIZED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"\n   ❌ FAILED: {e}")
        return False

def test_provider_info():
    """Test provider information"""
    print("\n2️⃣ Testing Provider Configuration...")
    
    try:
        print(f"   Current Provider: {agent_rag_engine.current_provider}")
        print(f"   LLM Model: {config.GEMINI_MODEL if agent_rag_engine.current_provider == 'gemini' else config.OPENAI_MODEL}")
        print(f"   Embedding Model: {config.HUGGINGFACE_MODEL}")
        
        print("\n   ✅ PROVIDER CONFIGURATION OK!")
        return True
        
    except Exception as e:
        print(f"\n   ❌ FAILED: {e}")
        return False

def test_tools():
    """Test that agent tools are available"""
    print("\n3️⃣ Testing Agent Tools...")
    
    try:
        from utils.agent_tools import (
            get_ingestion_tools,
            get_retrieval_tools,
            get_generation_tools
        )
        
        ingestion_tools = get_ingestion_tools()
        retrieval_tools = get_retrieval_tools()
        generation_tools = get_generation_tools()
        
        print(f"   Ingestion Tools: {len(ingestion_tools)} available")
        for tool in ingestion_tools:
            print(f"      - {tool.name}")
        
        print(f"\n   Retrieval Tools: {len(retrieval_tools)} available")
        for tool in retrieval_tools:
            print(f"      - {tool.name}")
        
        print(f"\n   Generation Tools: {len(generation_tools)} available")
        for tool in generation_tools:
            print(f"      - {tool.name}")
        
        print("\n   ✅ ALL TOOLS AVAILABLE!")
        return True
        
    except Exception as e:
        print(f"\n   ❌ FAILED: {e}")
        return False

def test_collection_name():
    """Test collection name generation"""
    print("\n4️⃣ Testing Collection Name Generation...")
    
    try:
        test_user_id = "test_user_123"
        collection_name = agent_rag_engine.get_collection_name(test_user_id)
        
        print(f"   Test User ID: {test_user_id}")
        print(f"   Generated Collection: {collection_name}")
        
        expected_format = f"user_{test_user_id}_{agent_rag_engine.current_provider}"
        assert collection_name == expected_format
        
        print("\n   ✅ COLLECTION NAME GENERATION OK!")
        return True
        
    except Exception as e:
        print(f"\n   ❌ FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "🚀 Starting Multi-Agent System Tests...\n")
    
    tests = [
        test_agent_initialization,
        test_provider_info,
        test_tools,
        test_collection_name
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n   Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n   🎉 ALL TESTS PASSED! Multi-Agent System is ready!")
        print("\n   Next steps:")
        print("   1. Run: streamlit run app.py")
        print("   2. Upload a document")
        print("   3. Watch the agents work!")
    else:
        print("\n   ⚠️ Some tests failed. Check errors above.")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
