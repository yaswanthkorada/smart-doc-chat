"""
=============================================================================
PYTHON FOR AI/GenAI - ADVANCED LEVEL (COMPLETE GUIDE)
=============================================================================

Purpose: Master advanced Python for production AI systems
Prerequisites: Complete BASICS and INTERMEDIATE levels
Time: 4-5 hours

What You'll Learn:
1. MetaClasses & Descriptors (framework internals)
2. Performance Optimization (profiling, caching)
3. Memory Management (garbage collection, memory leaks)
4. Concurrency & Parallelism (threading, multiprocessing)
5. Design Patterns for AI (singleton, factory, strategy)
6. Testing AI Code (pytest, mocking, fixtures)
7. Packaging & Distribution (setup.py, wheels)
8. Production Best Practices

AI Context: Production-grade AI systems
"""

import time
import sys
from typing import Any, Type
from abc import ABC, abstractmethod

# =============================================================================
# PART 1: METACLASSES & DESCRIPTORS
# =============================================================================

def demonstrate_metaclasses():
    """
    Metaclasses: Classes that create classes
    Use in AI: Framework internals (PyTorch, TensorFlow)
    """
    print("\n" + "="*80)
    print("PART 1: METACLASSES (Advanced)")
    print("="*80)
    
    print("\n1. BASIC METACLASS")
    
    class ModelMeta(type):
        """Metaclass that tracks all model classes"""
        models = []
        
        def __new__(mcs, name, bases, attrs):
            cls = super().__new__(mcs, name, bases, attrs)
            if name != 'BaseModel':
                mcs.models.append(name)
            return cls
    
    class BaseModel(metaclass=ModelMeta):
        pass
    
    class GPTModel(BaseModel):
        pass
    
    class BERTModel(BaseModel):
        pass
    
    print(f"   Registered models: {ModelMeta.models}")
    
    print("\n2. DESCRIPTORS (Property-like behavior)")
    
    class Validator:
        """Descriptor for validated attributes"""
        def __init__(self, min_value=None, max_value=None):
            self.min_value = min_value
            self.max_value = max_value
        
        def __set_name__(self, owner, name):
            self.name = f"_{name}"
        
        def __get__(self, obj, objtype=None):
            if obj is None:
                return self
            return getattr(obj, self.name)
        
        def __set__(self, obj, value):
            if self.min_value is not None and value < self.min_value:
                raise ValueError(f"{self.name} must be >= {self.min_value}")
            if self.max_value is not None and value > self.max_value:
                raise ValueError(f"{self.name} must be <= {self.max_value}")
            setattr(obj, self.name, value)
    
    class ModelConfig:
        temperature = Validator(min_value=0.0, max_value=2.0)
        max_tokens = Validator(min_value=1)
        
        def __init__(self, temperature, max_tokens):
            self.temperature = temperature
            self.max_tokens = max_tokens
    
    try:
        config = ModelConfig(0.7, 1000)
        print(f"   ✅ Valid config: temp={config.temperature}, tokens={config.max_tokens}")
        
        config.temperature = 3.0  # Will raise error
    except ValueError as e:
        print(f"   ❌ {e}")


# =============================================================================
# PART 2: PERFORMANCE OPTIMIZATION
# =============================================================================

def demonstrate_performance():
    """Performance optimization techniques"""
    print("\n" + "="*80)
    print("PART 2: PERFORMANCE OPTIMIZATION")
    print("="*80)
    
    print("\n1. PROFILING CODE")
    
    import cProfile
    import pstats
    from io import StringIO
    
    def slow_function():
        """Simulated slow function"""
        result = []
        for i in range(1000):
            result.append(i ** 2)
        return result
    
    # Profile function
    profiler = cProfile.Profile()
    profiler.enable()
    slow_function()
    profiler.disable()
    
    # Get stats
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(5)
    print("   Profiling results:")
    print("   " + "\n   ".join(s.getvalue().split("\n")[:10]))
    
    print("\n2. CACHING WITH LRU")
    
    from functools import lru_cache
    
    @lru_cache(maxsize=128)
    def expensive_embedding(text: str):
        """Cached embedding computation"""
        time.sleep(0.01)  # Simulate computation
        return [0.1] * 1536
    
    # First call - slow
    start = time.time()
    emb1 = expensive_embedding("hello")
    time1 = time.time() - start
    
    # Second call - cached, fast!
    start = time.time()
    emb2 = expensive_embedding("hello")
    time2 = time.time() - start
    
    print(f"   First call: {time1:.4f}s")
    print(f"   Cached call: {time2:.4f}s")
    print(f"   Speedup: {time1/time2:.1f}x")
    
    print("\n3. LIST COMPREHENSIONS VS LOOPS")
    
    # Loop (slower)
    start = time.time()
    result1 = []
    for i in range(10000):
        result1.append(i ** 2)
    time1 = time.time() - start
    
    # Comprehension (faster)
    start = time.time()
    result2 = [i ** 2 for i in range(10000)]
    time2 = time.time() - start
    
    print(f"   Loop: {time1:.4f}s")
    print(f"   Comprehension: {time2:.4f}s")
    print(f"   Speedup: {time1/time2:.1f}x")
    
    print("\n4. SLOTS FOR MEMORY EFFICIENCY")
    
    class WithoutSlots:
        def __init__(self, x, y):
            self.x = x
            self.y = y
    
    class WithSlots:
        __slots__ = ['x', 'y']
        def __init__(self, x, y):
            self.x = x
            self.y = y
    
    # Compare memory usage
    obj1 = WithoutSlots(1, 2)
    obj2 = WithSlots(1, 2)
    
    print(f"   Without __slots__: {sys.getsizeof(obj1)} bytes")
    print(f"   With __slots__: {sys.getsizeof(obj2)} bytes")


# =============================================================================
# PART 3: CONCURRENCY & PARALLELISM
# =============================================================================

def demonstrate_concurrency():
    """Threading and multiprocessing for AI"""
    print("\n" + "="*80)
    print("PART 3: CONCURRENCY & PARALLELISM")
    print("="*80)
    
    print("\n1. THREADING (I/O-bound tasks)")
    
    import threading
    
    def fetch_data(url, results, index):
        """Simulated API call"""
        time.sleep(0.1)
        results[index] = f"Data from {url}"
    
    # Sequential
    start = time.time()
    results_seq = {}
    for i, url in enumerate(["api1", "api2", "api3"]):
        fetch_data(url, results_seq, i)
    time_seq = time.time() - start
    
    # Threaded
    start = time.time()
    results_thread = {}
    threads = []
    for i, url in enumerate(["api1", "api2", "api3"]):
        thread = threading.Thread(target=fetch_data, args=(url, results_thread, i))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    time_thread = time.time() - start
    
    print(f"   Sequential: {time_seq:.2f}s")
    print(f"   Threaded: {time_thread:.2f}s")
    print(f"   Speedup: {time_seq/time_thread:.1f}x")
    
    print("\n2. MULTIPROCESSING (CPU-bound tasks)")
    
    from multiprocessing import Pool, cpu_count
    
    def process_text(text):
        """CPU-intensive processing"""
        return len(text.split()) * 2  # Simplified
    
    texts = ["text " * 1000 for _ in range(100)]
    
    # Sequential
    start = time.time()
    results1 = [process_text(t) for t in texts]
    time1 = time.time() - start
    
    # Parallel
    start = time.time()
    with Pool(cpu_count()) as pool:
        results2 = pool.map(process_text, texts)
    time2 = time.time() - start
    
    print(f"   Sequential: {time1:.2f}s")
    print(f"   Parallel ({cpu_count()} cores): {time2:.2f}s")
    print(f"   Speedup: {time1/time2:.1f}x")


# =============================================================================
# PART 4: DESIGN PATTERNS FOR AI
# =============================================================================

def demonstrate_design_patterns():
    """Common design patterns in AI systems"""
    print("\n" + "="*80)
    print("PART 4: DESIGN PATTERNS FOR AI")
    print("="*80)
    
    print("\n1. SINGLETON PATTERN (single instance)")
    
    class ModelManager:
        """Singleton: Only one instance exists"""
        _instance = None
        
        def __new__(cls):
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.models = {}
            return cls._instance
        
        def register(self, name, model):
            self.models[name] = model
    
    manager1 = ModelManager()
    manager2 = ModelManager()
    
    manager1.register("gpt-4", "GPT4Model")
    print(f"   manager1 models: {manager1.models}")
    print(f"   manager2 models: {manager2.models}")
    print(f"   Same instance: {manager1 is manager2}")
    
    print("\n2. FACTORY PATTERN (object creation)")
    
    class ModelFactory:
        """Factory: Create models based on type"""
        
        @staticmethod
        def create_model(model_type: str):
            if model_type == "gpt":
                return GPTModel()
            elif model_type == "bert":
                return BERTModel()
            else:
                raise ValueError(f"Unknown model: {model_type}")
    
    class GPTModel:
        def generate(self):
            return "GPT response"
    
    class BERTModel:
        def classify(self):
            return "BERT classification"
    
    model = ModelFactory.create_model("gpt")
    print(f"   Created: {type(model).__name__}")
    print(f"   Output: {model.generate()}")
    
    print("\n3. STRATEGY PATTERN (interchangeable algorithms)")
    
    class EmbeddingStrategy(ABC):
        @abstractmethod
        def embed(self, text: str):
            pass
    
    class OpenAIEmbedding(EmbeddingStrategy):
        def embed(self, text: str):
            return [0.1] * 1536
    
    class HuggingFaceEmbedding(EmbeddingStrategy):
        def embed(self, text: str):
            return [0.2] * 768
    
    class EmbeddingService:
        def __init__(self, strategy: EmbeddingStrategy):
            self.strategy = strategy
        
        def embed(self, text: str):
            return self.strategy.embed(text)
    
    # Can switch strategies easily
    service = EmbeddingService(OpenAIEmbedding())
    embedding1 = service.embed("test")
    print(f"   OpenAI embedding: {len(embedding1)} dims")
    
    service.strategy = HuggingFaceEmbedding()
    embedding2 = service.embed("test")
    print(f"   HuggingFace embedding: {len(embedding2)} dims")


# =============================================================================
# PART 5: TESTING AI CODE
# =============================================================================

def demonstrate_testing():
    """Testing strategies for AI code"""
    print("\n" + "="*80)
    print("PART 5: TESTING AI CODE")
    print("="*80)
    
    print("\n1. UNIT TESTING")
    
    # Function to test
    def preprocess_text(text: str) -> str:
        return text.lower().strip()
    
    # Tests
    assert preprocess_text("  HELLO  ") == "hello"
    assert preprocess_text("World") == "world"
    print("   ✅ All unit tests passed")
    
    print("\n2. MOCKING EXTERNAL APIS")
    
    from unittest.mock import Mock, patch
    
    def call_llm_api(prompt: str) -> dict:
        """Function that calls external API"""
        # In real code: requests.post(...)
        return {"response": "mock response"}
    
    # Mock the API
    with patch('__main__.call_llm_api') as mock_api:
        mock_api.return_value = {"response": "mocked!"}
        result = call_llm_api("test")
        print(f"   Mocked result: {result}")
    
    print("\n3. PROPERTY-BASED TESTING")
    
    def normalize_score(score: float) -> float:
        """Normalize to 0-1"""
        return max(0.0, min(1.0, score))
    
    # Test properties
    for score in [-0.5, 0.0, 0.5, 1.0, 1.5]:
        result = normalize_score(score)
        assert 0.0 <= result <= 1.0
        print(f"   normalize({score}) = {result}")
    print("   ✅ Property tests passed")


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Run all advanced demonstrations"""
    print("="*80)
    print("PYTHON FOR AI - ADVANCED LEVEL")
    print("="*80)
    
    demonstrate_metaclasses()
    input("\nPress Enter to continue...")
    
    demonstrate_performance()
    input("\nPress Enter to continue...")
    
    demonstrate_concurrency()
    input("\nPress Enter to continue...")
    
    demonstrate_design_patterns()
    input("\nPress Enter to continue...")
    
    demonstrate_testing()
    
    print("\n" + "="*80)
    print("✅ ADVANCED LEVEL COMPLETE!")
    print("="*80)
    print("""
📚 What You Learned:
✅ Metaclasses & descriptors
✅ Performance optimization
✅ Concurrency & parallelism
✅ Design patterns for AI
✅ Testing strategies

🎯 Next: python PYTHON_AI_FRAMEWORKS.py
Learn all major AI libraries!
""")

if __name__ == "__main__":
    main()
