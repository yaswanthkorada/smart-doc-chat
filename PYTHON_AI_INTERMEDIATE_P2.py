"""
=============================================================================
PYTHON FOR AI/GenAI - INTERMEDIATE LEVEL PART 2
=============================================================================
Continuation of PYTHON_AI_INTERMEDIATE.py
Covers: Advanced OOP, Type Hints, Functional Programming, Async Programming
"""

import time
from typing import List, Dict, Optional, Union, Tuple, Callable
from functools import reduce
import asyncio

# =============================================================================
# PART 5: ADVANCED OOP FOR AI
# =============================================================================

def demonstrate_advanced_oop():
    """Advanced OOP patterns for AI systems"""
    print("\n" + "="*80)
    print("PART 5: ADVANCED OOP FOR AI")
    print("="*80)
    
    # Class inheritance and composition
    print("\n1. INHERITANCE VS COMPOSITION")
    
    class BaseModel:
        def __init__(self, name):
            self.name = name
            self.metrics = {}
        
        def evaluate(self):
            return self.metrics
    
    class GPTModel(BaseModel):
        def __init__(self, name, max_tokens):
            super().__init__(name)
            self.max_tokens = max_tokens
        
        def generate(self, prompt):
            return f"{self.name}: {prompt[:20]}..."
    
    # Composition (preferred for flexibility)
    class Tokenizer:
        def tokenize(self, text):
            return text.split()
    
    class ModelWithTokenizer:
        def __init__(self, model, tokenizer):
            self.model = model  # Composition
            self.tokenizer = tokenizer
        
        def process(self, text):
            tokens = self.tokenizer.tokenize(text)
            return self.model.generate(text), len(tokens)
    
    model = GPTModel("gpt-4", 1000)
    tokenizer = Tokenizer()
    full_model = ModelWithTokenizer(model, tokenizer)
    
    result, token_count = full_model.process("Hello world")
    print(f"   Result: {result}")
    print(f"   Tokens: {token_count}")
    
    # Abstract base classes
    print("\n2. ABSTRACT BASE CLASSES")
    
    from abc import ABC, abstractmethod
    
    class BaseEmbedding(ABC):
        @abstractmethod
        def embed(self, text: str) -> List[float]:
            pass
    
    class OpenAIEmbedding(BaseEmbedding):
        def embed(self, text: str) -> List[float]:
            return [0.1] * 1536  # Mock embedding
    
    embedder = OpenAIEmbedding()
    embedding = embedder.embed("test")
    print(f"   Embedding dim: {len(embedding)}")
    
    # Magic methods
    print("\n3. MAGIC METHODS")
    
    class TokenCounter:
        def __init__(self):
            self.count = 0
        
        def __call__(self, text):
            """Make instance callable"""
            tokens = len(text.split())
            self.count += tokens
            return tokens
        
        def __repr__(self):
            return f"TokenCounter(total={self.count})"
    
    counter = TokenCounter()
    print(f"   {counter('Hello world')}")
    print(f"   {counter('AI is great')}")
    print(f"   {counter}")


# =============================================================================
# PART 6: TYPE HINTS FOR AI
# =============================================================================

def demonstrate_type_hints():
    """Type hints for better AI code"""
    print("\n" + "="*80)
    print("PART 6: TYPE HINTS FOR AI CODE")
    print("="*80)
    
    print("\n1. BASIC TYPE HINTS")
    
    def generate_text(
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7
    ) -> str:
        """Type-hinted function"""
        return f"Generated (tokens={max_tokens}, temp={temperature})"
    
    result = generate_text("Hello", max_tokens=50)
    print(f"   {result}")
    
    print("\n2. COLLECTION TYPE HINTS")
    
    def process_batch(
        prompts: List[str],
        config: Dict[str, Union[str, int, float]]
    ) -> List[Dict[str, str]]:
        """Process batch of prompts"""
        return [{"prompt": p, "response": "..."} for p in prompts]
    
    results = process_batch(
        ["prompt1", "prompt2"],
        {"model": "gpt-4", "temp": 0.7, "max_tokens": 100}
    )
    print(f"   Processed {len(results)} prompts")
    
    print("\n3. OPTIONAL AND UNION TYPES")
    
    def call_model(
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Union[str, Dict] = "text"
    ) -> Tuple[str, int]:
        """Optional and Union types"""
        tokens = 100
        return "response", tokens
    
    response, tokens = call_model("test", system_prompt="You are helpful")
    print(f"   Response: {response}, Tokens: {tokens}")
    
    print("\n4. CALLABLE TYPE HINTS")
    
    def apply_transformation(
        data: List[str],
        transform: Callable[[str], str]
    ) -> List[str]:
        """Function that takes a function"""
        return [transform(item) for item in data]
    
    result = apply_transformation(["hello", "world"], str.upper)
    print(f"   Transformed: {result}")


# =============================================================================
# PART 7: FUNCTIONAL PROGRAMMING
# =============================================================================

def demonstrate_functional():
    """Functional programming for AI"""
    print("\n" + "="*80)
    print("PART 7: FUNCTIONAL PROGRAMMING FOR AI")
    print("="*80)
    
    print("\n1. MAP - Transform all items")
    
    prompts = ["what is ai", "explain ml", "define dl"]
    capitalized = list(map(str.upper, prompts))
    print(f"   Original: {prompts}")
    print(f"   Capitalized: {capitalized}")
    
    # Map with lambda
    scores = [85, 92, 78, 95]
    normalized = list(map(lambda x: x/100, scores))
    print(f"   Scores: {scores}")
    print(f"   Normalized: {normalized}")
    
    print("\n2. FILTER - Select items")
    
    scores = [0.85, 0.92, 0.78, 0.95, 0.88]
    high_scores = list(filter(lambda x: x >= 0.90, scores))
    print(f"   All: {scores}")
    print(f"   High (≥0.90): {high_scores}")
    
    print("\n3. REDUCE - Combine items")
    
    from functools import reduce
    
    # Sum all scores
    total = reduce(lambda a, b: a + b, scores)
    print(f"   Total: {total}")
    
    # Find max
    max_score = reduce(lambda a, b: a if a > b else b, scores)
    print(f"   Max: {max_score}")
    
    print("\n4. PARTIAL - Partial function application")
    
    from functools import partial
    
    def call_llm(prompt, model, temperature):
        return f"{model}(temp={temperature}): {prompt}"
    
    # Create specialized functions
    gpt4_call = partial(call_llm, model="gpt-4", temperature=0.7)
    gpt35_call = partial(call_llm, model="gpt-3.5", temperature=0.5)
    
    print(f"   {gpt4_call('Hello')}")
    print(f"   {gpt35_call('Hello')}")


# =============================================================================
# PART 8: ASYNC PROGRAMMING FOR AI
# =============================================================================

def demonstrate_async():
    """Async programming for concurrent AI calls"""
    print("\n" + "="*80)
    print("PART 8: ASYNC PROGRAMMING FOR AI")
    print("="*80)
    
    print("\n1. BASIC ASYNC/AWAIT")
    
    async def async_llm_call(prompt: str, delay: float = 0.1):
        """Simulated async LLM call"""
        await asyncio.sleep(delay)
        return f"Response to: {prompt}"
    
    async def process_single():
        result = await async_llm_call("What is AI?")
        print(f"   Single: {result}")
    
    asyncio.run(process_single())
    
    print("\n2. CONCURRENT ASYNC CALLS")
    
    async def process_multiple():
        """Process multiple prompts concurrently"""
        prompts = ["What is AI?", "Explain ML", "Define DL"]
        
        # Sequential (slow)
        start = time.time()
        results_seq = []
        for p in prompts:
            result = await async_llm_call(p, delay=0.1)
            results_seq.append(result)
        seq_time = time.time() - start
        
        # Concurrent (fast!)
        start = time.time()
        tasks = [async_llm_call(p, delay=0.1) for p in prompts]
        results_concurrent = await asyncio.gather(*tasks)
        concurrent_time = time.time() - start
        
        print(f"   Sequential: {seq_time:.2f}s")
        print(f"   Concurrent: {concurrent_time:.2f}s")
        print(f"   Speedup: {seq_time/concurrent_time:.1f}x")
    
    asyncio.run(process_multiple())
    
    print("\n3. ERROR HANDLING IN ASYNC")
    
    async def safe_llm_call(prompt: str):
        """Async call with error handling"""
        try:
            if "error" in prompt:
                raise ValueError("Simulated error")
            return await async_llm_call(prompt)
        except ValueError as e:
            return f"Error: {e}"
    
    async def process_with_errors():
        prompts = ["Good prompt", "error prompt", "Another good"]
        tasks = [safe_llm_call(p) for p in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            print(f"   {i+1}. {result}")
    
    asyncio.run(process_with_errors())


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Run all demonstrations"""
    print("="*80)
    print("PYTHON FOR AI - INTERMEDIATE LEVEL (PART 2)")
    print("="*80)
    
    demonstrate_advanced_oop()
    input("\nPress Enter to continue...")
    
    demonstrate_type_hints()
    input("\nPress Enter to continue...")
    
    demonstrate_functional()
    input("\nPress Enter to continue...")
    
    demonstrate_async()
    
    print("\n" + "="*80)
    print("✅ INTERMEDIATE LEVEL COMPLETE!")
    print("="*80)
    print("""
📚 What You Learned:
- Advanced OOP (ABC, magic methods, composition)
- Type hints for better code
- Functional programming (map, filter, reduce)
- Async programming for concurrent calls

🎯 Next: python PYTHON_AI_ADVANCED.py
""")

if __name__ == "__main__":
    main()
