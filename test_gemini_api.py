"""
Test script to verify Gemini API is working
Tests both embeddings and chat responses
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def test_gemini_chat():
    """Test Gemini chat API"""
    print(f"\n{YELLOW}Testing Gemini Chat API...{RESET}")
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print(f"{RED}❌ GEMINI_API_KEY not found in .env file{RESET}")
            return False
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test chat
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content("Say 'Hello from Gemini!' if you can hear me.")
        
        print(f"{GREEN}✅ Gemini Chat Response:{RESET}")
        print(f"   {response.text}")
        return True
        
    except Exception as e:
        print(f"{RED}❌ Gemini Chat Error: {str(e)}{RESET}")
        return False

def test_gemini_embeddings():
    """Test Gemini embeddings API"""
    print(f"\n{YELLOW}Testing Gemini Embeddings API...{RESET}")
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print(f"{RED}❌ GEMINI_API_KEY not found in .env file{RESET}")
            return False
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test embeddings
        text = "This is a test document for embeddings"
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        
        embedding = result['embedding']
        print(f"{GREEN}✅ Gemini Embeddings Working!{RESET}")
        print(f"   Text: '{text}'")
        print(f"   Embedding dimension: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        return True
        
    except Exception as e:
        print(f"{RED}❌ Gemini Embeddings Error: {str(e)}{RESET}")
        print(f"   Note: Free tier has limits (1500 embeddings/day)")
        return False

def test_huggingface_embeddings():
    """Test Hugging Face local embeddings (FREE, no API key needed)"""
    print(f"\n{YELLOW}Testing Hugging Face Local Embeddings...{RESET}")
    
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        
        print(f"   Downloading model (first time only, ~400MB)...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Test embeddings
        text = "This is a test document for embeddings"
        embedding = embeddings.embed_query(text)
        
        print(f"{GREEN}✅ Hugging Face Embeddings Working!{RESET}")
        print(f"   Text: '{text}'")
        print(f"   Embedding dimension: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        print(f"   {GREEN}💡 This is FREE and runs locally - no API limits!{RESET}")
        return True
        
    except Exception as e:
        print(f"{RED}❌ Hugging Face Error: {str(e)}{RESET}")
        print(f"   Install: pip install sentence-transformers langchain-huggingface")
        return False

def main():
    print("=" * 60)
    print("🧪 GEMINI & EMBEDDINGS API TEST")
    print("=" * 60)
    
    # Test Gemini Chat
    chat_ok = test_gemini_chat()
    
    # Test Gemini Embeddings
    embeddings_ok = test_gemini_embeddings()
    
    # Test Hugging Face (backup option)
    hf_ok = test_huggingface_embeddings()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Gemini Chat:        {'✅ PASS' if chat_ok else '❌ FAIL'}")
    print(f"Gemini Embeddings:  {'✅ PASS' if embeddings_ok else '❌ FAIL'}")
    print(f"Hugging Face:       {'✅ PASS' if hf_ok else '❌ FAIL'}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if chat_ok and hf_ok:
        print(f"   {GREEN}✅ Use Gemini for chat + Hugging Face for embeddings (both FREE!){RESET}")
        print(f"   {GREEN}✅ Your current .env setup is perfect!{RESET}")
    elif chat_ok and embeddings_ok:
        print(f"   {GREEN}✅ Gemini is working for both chat and embeddings{RESET}")
        print(f"   {YELLOW}⚠️  Consider Hugging Face for embeddings to avoid quota limits{RESET}")
    elif not chat_ok:
        print(f"   {RED}❌ Add your Gemini API key to .env file{RESET}")
        print(f"   {YELLOW}   Get it here: https://makersuite.google.com/app/apikey{RESET}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
