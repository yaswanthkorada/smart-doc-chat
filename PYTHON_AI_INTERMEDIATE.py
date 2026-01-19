"""
=============================================================================
PYTHON FOR AI/GenAI - INTERMEDIATE LEVEL (COMPLETE GUIDE)
=============================================================================

Purpose: Master intermediate Python concepts for AI/ML development
Prerequisites: Complete PYTHON_AI_BASICS.py first
Time: 3-4 hours to complete all examples

What You'll Learn:
1. List/Dict Comprehensions (efficient data processing)
2. Generators & Iterators (memory-efficient data loading)
3. Decorators (function enhancement, logging)
4. Context Managers (resource management)
5. Advanced OOP (inheritance, composition)
6. Modules & Packages (code organization)
7. Type Hints (code clarity, IDE support)
8. Functional Programming (map, filter, reduce)

AI Context: These concepts are heavily used in:
- PyTorch/TensorFlow codebases
- Data preprocessing pipelines
- Model training loops
- API clients and wrappers
"""

# =============================================================================
# PART 1: COMPREHENSIONS - PYTHONIC DATA PROCESSING
# =============================================================================
# AI Context: Comprehensions are everywhere in AI code:
# - Data preprocessing
# - Batch creation
# - Feature extraction
# - Result filtering
# =============================================================================

def demonstrate_comprehensions():
    """
    List/Dict/Set Comprehensions for AI
    
    Why use:
    - More readable than loops
    - Faster execution
    - More Pythonic
    - Less code
    
    When to use in AI:
    - Data transformation
    - Batch processing
    - Feature engineering
    """
    print("\n" + "="*80)
    print("PART 1: COMPREHENSIONS FOR AI")
    print("="*80)
    
    # =============================================================================
    # List Comprehensions
    # =============================================================================
    print("\n1. LIST COMPREHENSIONS")
    
    # Basic: Transform data
    prompts = ["what is ai", "explain ml", "define dl"]
    
    # Old way (verbose)
    capitalized_old = []
    for p in prompts:
        capitalized_old.append(p.upper())
    
    # New way (comprehension)
    capitalized_new = [p.upper() for p in prompts]
    
    print(f"   Original: {prompts}")
    print(f"   Capitalized: {capitalized_new}")
    
    # With condition: Filter and transform
    scores = [0.85, 0.92, 0.78, 0.95, 0.88, 0.73]
    high_scores = [s for s in scores if s >= 0.90]
    print(f"\n   All scores: {scores}")
    print(f"   High scores (≥0.90): {high_scores}")
    
    # Transform and filter
    scaled_high = [s * 100 for s in scores if s >= 0.90]
    print(f"   Scaled high scores: {scaled_high}")
    
    # Nested loops: Create training pairs
    models = ["gpt-3.5", "gpt-4"]
    temperatures = [0.5, 0.7, 0.9]
    configs = [(m, t) for m in models for t in temperatures]
    print(f"\n   Model configs (model, temp):")
    for config in configs:
        print(f"   - {config}")
    
    # Complex: Tokenize and count
    texts = ["Hello world", "AI is great", "Python rocks"]
    word_counts = [len(text.split()) for text in texts]
    print(f"\n   Texts: {texts}")
    print(f"   Word counts: {word_counts}")
    
    # Conditional expression in comprehension
    labels = [1, 0, 1, 1, 0]
    label_names = ["positive" if l == 1 else "negative" for l in labels]
    print(f"\n   Labels: {labels}")
    print(f"   Names: {label_names}")
    
    # =============================================================================
    # Dictionary Comprehensions
    # =============================================================================
    print("\n2. DICTIONARY COMPREHENSIONS")
    
    # Create model config dict
    params = ["temperature", "max_tokens", "top_p"]
    values = [0.7, 1000, 0.9]
    config = {p: v for p, v in zip(params, values)}
    print(f"   Config: {config}")
    
    # Filter dictionary
    api_response = {
        "id": "chatcmpl-123",
        "model": "gpt-4",
        "created": 1234567890,
        "choices": [...],
        "usage": {"total_tokens": 100}
    }
    # Extract only important fields
    important = {k: v for k, v in api_response.items() if k in ["model", "usage"]}
    print(f"\n   Important fields: {important}")
    
    # Transform dict values
    raw_scores = {"model_a": 85, "model_b": 92, "model_c": 78}
    normalized = {k: v/100 for k, v in raw_scores.items()}
    print(f"\n   Raw scores: {raw_scores}")
    print(f"   Normalized: {normalized}")
    
    # Invert dictionary (swap keys and values)
    model_ids = {"gpt-3.5": 1, "gpt-4": 2, "claude": 3}
    id_to_model = {v: k for k, v in model_ids.items()}
    print(f"\n   Model to ID: {model_ids}")
    print(f"   ID to Model: {id_to_model}")
    
    # =============================================================================
    # Set Comprehensions
    # =============================================================================
    print("\n3. SET COMPREHENSIONS")
    
    # Extract unique words from multiple texts
    documents = [
        "AI and ML are related",
        "ML is part of AI",
        "DL is a type of ML"
    ]
    vocabulary = {word.lower() for doc in documents for word in doc.split()}
    print(f"\n   Documents: {documents}")
    print(f"   Vocabulary: {sorted(vocabulary)}")
    
    # Get unique labels
    predictions = [1, 0, 1, 1, 0, 1, 0]
    unique_labels = {p for p in predictions}
    print(f"\n   Predictions: {predictions}")
    print(f"   Unique labels: {unique_labels}")
    
    # =============================================================================
    # Generator Expressions (memory efficient!)
    # =============================================================================
    print("\n4. GENERATOR EXPRESSIONS (memory efficient)")
    
    # List comprehension: Creates full list in memory
    squares_list = [x**2 for x in range(1000000)]
    print(f"\n   List: Uses memory for all 1M items")
    
    # Generator expression: Computes on demand
    squares_gen = (x**2 for x in range(1000000))
    print(f"   Generator: Computes items as needed")
    print(f"   Type: {type(squares_gen)}")
    
    # Use generator
    first_5 = [next(squares_gen) for _ in range(5)]
    print(f"   First 5 squares: {first_5}")
    
    # Real AI use case: Process large dataset
    def load_large_dataset():
        """Simulate loading large dataset"""
        for i in range(10):
            yield {"id": i, "text": f"Document {i}", "label": i % 2}
    
    # Process without loading all in memory
    positive_count = sum(1 for item in load_large_dataset() if item["label"] == 1)
    print(f"\n   Positive samples: {positive_count}")


# =============================================================================
# PART 2: GENERATORS & ITERATORS
# =============================================================================
# AI Context: Essential for:
# - Large dataset loading (can't fit in RAM)
# - Streaming data processing
# - Batch generation
# - Memory-efficient training
# =============================================================================

def demonstrate_generators():
    """
    Generators for Memory-Efficient AI
    
    When to use:
    - Large datasets (GB/TB scale)
    - Streaming data
    - Infinite sequences
    - Batch processing
    
    Benefit: Only load data when needed
    """
    print("\n" + "="*80)
    print("PART 2: GENERATORS FOR MEMORY-EFFICIENT AI")
    print("="*80)
    
    # =============================================================================
    # Basic Generator
    # =============================================================================
    print("\n1. BASIC GENERATOR FUNCTION")
    
    def simple_generator():
        """Generate sequence without storing all values"""
        print("   Generating 1...")
        yield 1
        print("   Generating 2...")
        yield 2
        print("   Generating 3...")
        yield 3
    
    gen = simple_generator()
    print("   Generator created (no values generated yet)")
    print(f"   next(gen) = {next(gen)}")
    print(f"   next(gen) = {next(gen)}")
    print(f"   next(gen) = {next(gen)}")
    
    # =============================================================================
    # Data Batch Generator (COMMON PATTERN)
    # =============================================================================
    print("\n2. BATCH GENERATOR (most common in AI)")
    
    def batch_generator(data, batch_size):
        """
        Generate batches from data
        
        Use case: Training loop with mini-batches
        """
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            yield batch
    
    # Simulate dataset
    dataset = list(range(100))  # 100 samples
    
    print(f"   Dataset size: {len(dataset)}")
    print(f"   Batch size: 32")
    print("\n   Processing batches:")
    
    for batch_num, batch in enumerate(batch_generator(dataset, 32), 1):
        print(f"   Batch {batch_num}: {len(batch)} samples (first={batch[0]}, last={batch[-1]})")
    
    # =============================================================================
    # Infinite Generator (for continuous data streams)
    # =============================================================================
    print("\n3. INFINITE GENERATOR (data streams)")
    
    def infinite_data_stream():
        """Generate infinite stream of data"""
        epoch = 0
        while True:
            epoch += 1
            # In real scenario: fetch from API, database, etc.
            yield {"epoch": epoch, "data": f"Batch from epoch {epoch}"}
    
    stream = infinite_data_stream()
    print("   Infinite stream created")
    print("   Getting first 3 batches:")
    for _ in range(3):
        batch = next(stream)
        print(f"   - {batch}")
    
    # =============================================================================
    # Generator with State (stateful data loading)
    # =============================================================================
    print("\n4. STATEFUL GENERATOR")
    
    def augmented_data_generator(base_data, augmentations=2):
        """
        Generate augmented versions of data
        
        Use case: Data augmentation for training
        """
        for item in base_data:
            # Original
            yield {"data": item, "augmented": False}
            
            # Augmented versions
            for aug_num in range(augmentations):
                yield {
                    "data": f"{item}_aug_{aug_num}",
                    "augmented": True
                }
    
    base_images = ["image1.jpg", "image2.jpg"]
    print(f"\n   Base data: {base_images}")
    print("   With 2 augmentations per image:")
    
    count = 0
    for item in augmented_data_generator(base_images, augmentations=2):
        count += 1
        print(f"   {count}. {item}")
    
    # =============================================================================
    # Generator Expression vs Generator Function
    # =============================================================================
    print("\n5. GENERATOR EXPRESSION vs FUNCTION")
    
    # Generator expression (simple)
    squares_expr = (x**2 for x in range(5))
    print("   Expression: (x**2 for x in range(5))")
    print(f"   Values: {list(squares_expr)}")
    
    # Generator function (complex logic)
    def squares_func(n):
        for x in range(n):
            print(f"   Computing {x}^2")
            yield x**2
    
    squares_gen = squares_func(5)
    print("\n   Function: More control, can add logic")
    result = list(squares_gen)
    print(f"   Values: {result}")
    
    # =============================================================================
    # Real AI Example: Text Data Loader
    # =============================================================================
    print("\n6. REAL AI EXAMPLE: Text Data Loader")
    
    def text_data_loader(file_paths, batch_size=2):
        """
        Load and batch text data from multiple files
        
        Memory efficient: Doesn't load all files at once
        """
        batch = []
        
        for file_path in file_paths:
            # Simulate reading file
            texts = [f"Text from {file_path} - line {i}" for i in range(3)]
            
            for text in texts:
                batch.append(text)
                
                if len(batch) == batch_size:
                    yield batch
                    batch = []
        
        # Yield remaining
        if batch:
            yield batch
    
    files = ["file1.txt", "file2.txt"]
    print(f"   Files: {files}")
    print(f"   Batch size: 2")
    print("\n   Loaded batches:")
    
    for i, batch in enumerate(text_data_loader(files, batch_size=2), 1):
        print(f"   Batch {i}: {len(batch)} texts")
        for text in batch:
            print(f"      - {text}")


# =============================================================================
# PART 3: DECORATORS
# =============================================================================
# AI Context: Decorators are used for:
# - Timing model inference
# - Logging API calls
# - Caching results
# - Input validation
# - Retry logic
# =============================================================================

def demonstrate_decorators():
    """
    Decorators for AI Development
    
    What: Functions that modify other functions
    When: Logging, timing, caching, validation
    Why: Clean, reusable, maintainable code
    """
    print("\n" + "="*80)
    print("PART 3: DECORATORS FOR AI")
    print("="*80)
    
    import time
    import functools
    
    # =============================================================================
    # Basic Decorator - Timing
    # =============================================================================
    print("\n1. TIMING DECORATOR (measure inference time)")
    
    def timer(func):
        """Measure function execution time"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f"   ⏱️ {func.__name__} took {end - start:.4f}s")
            return result
        return wrapper
    
    @timer
    def model_inference(prompt):
        """Simulate model inference"""
        time.sleep(0.1)  # Simulate processing
        return f"Response to: {prompt}"
    
    result = model_inference("What is AI?")
    print(f"   Result: {result}")
    
    # =============================================================================
    # Decorator with Arguments
    # =============================================================================
    print("\n2. DECORATOR WITH ARGUMENTS (retry logic)")
    
    def retry(max_attempts=3, delay=1):
        """Retry function on failure"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(1, max_attempts + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_attempts:
                            print(f"   ❌ Failed after {max_attempts} attempts")
                            raise
                        print(f"   ⚠️ Attempt {attempt} failed: {e}")
                        print(f"   Retrying in {delay}s...")
                        time.sleep(delay)
            return wrapper
        return decorator
    
    attempt_count = 0
    
    @retry(max_attempts=3, delay=0.1)
    def unstable_api_call():
        """Simulate unstable API"""
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError("API temporarily unavailable")
        return "Success!"
    
    result = unstable_api_call()
    print(f"   Result: {result}")
    
    # =============================================================================
    # Caching Decorator
    # =============================================================================
    print("\n3. CACHING DECORATOR (avoid recomputation)")
    
    def cache(func):
        """Cache function results"""
        cached_results = {}
        
        @functools.wraps(func)
        def wrapper(*args):
            if args in cached_results:
                print(f"   💾 Cache hit for {args}")
                return cached_results[args]
            
            print(f"   🔄 Computing for {args}")
            result = func(*args)
            cached_results[args] = result
            return result
        return wrapper
    
    @cache
    def expensive_embedding(text):
        """Simulate expensive embedding computation"""
        time.sleep(0.1)
        return [0.1, 0.2, 0.3]  # Mock embedding
    
    # First call - computed
    emb1 = expensive_embedding("Hello")
    # Second call - cached
    emb2 = expensive_embedding("Hello")
    # Different input - computed
    emb3 = expensive_embedding("World")
    
    # =============================================================================
    # Logging Decorator
    # =============================================================================
    print("\n4. LOGGING DECORATOR (track function calls)")
    
    def log_calls(func):
        """Log all function calls"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args_str = ", ".join(map(str, args))
            kwargs_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            all_args = ", ".join(filter(None, [args_str, kwargs_str]))
            
            print(f"   📝 Calling {func.__name__}({all_args})")
            result = func(*args, **kwargs)
            print(f"   📝 {func.__name__} returned: {result}")
            return result
        return wrapper
    
    @log_calls
    def generate_text(prompt, temperature=0.7):
        """Generate text"""
        return f"Generated for: {prompt[:20]}..."
    
    generate_text("What is Python?", temperature=0.8)
    
    # =============================================================================
    # Stacking Decorators
    # =============================================================================
    print("\n5. STACKING DECORATORS (combine multiple)")
    
    @timer
    @retry(max_attempts=2, delay=0.1)
    @log_calls
    def complex_model_call(prompt):
        """Model call with timing, retry, and logging"""
        time.sleep(0.05)
        return f"Response: {prompt}"
    
    result = complex_model_call("Explain AI")
    
    # =============================================================================
    # Class-based Decorator
    # =============================================================================
    print("\n6. CLASS-BASED DECORATOR")
    
    class CountCalls:
        """Count function calls"""
        def __init__(self, func):
            self.func = func
            self.count = 0
        
        def __call__(self, *args, **kwargs):
            self.count += 1
            print(f"   📊 Call #{self.count} to {self.func.__name__}")
            return self.func(*args, **kwargs)
    
    @CountCalls
    def api_request(endpoint):
        return f"Response from {endpoint}"
    
    api_request("/generate")
    api_request("/chat")
    api_request("/embeddings")
    print(f"   Total calls: {api_request.count}")


# =============================================================================
# PART 4: CONTEXT MANAGERS
# =============================================================================
# AI Context: Essential for:
# - File handling (datasets, models)
# - Database connections
# - API sessions
# - GPU memory management
# =============================================================================

def demonstrate_context_managers():
    """
    Context Managers for Resource Management
    
    What: with statement for resource cleanup
    When: Files, connections, locks, GPU memory
    Why: Automatic cleanup, exception safety
    """
    print("\n" + "="*80)
    print("PART 4: CONTEXT MANAGERS FOR AI")
    print("="*80)
    
    from contextlib import contextmanager
    import time
    
    # =============================================================================
    # Basic Context Manager - File handling
    # =============================================================================
    print("\n1. BASIC WITH STATEMENT (file handling)")
    
    # Write data
    with open("temp_training_data.txt", "w") as f:
        f.write("sample1,positive\n")
        f.write("sample2,negative\n")
    print("   ✅ File written and automatically closed")
    
    # Read data
    with open("temp_training_data.txt", "r") as f:
        data = f.readlines()
    print(f"   ✅ File read: {len(data)} lines")
    
    # Cleanup
    import os
    os.remove("temp_training_data.txt")
    
    # =============================================================================
    # Multiple Context Managers
    # =============================================================================
    print("\n2. MULTIPLE CONTEXT MANAGERS")
    
    # Open multiple files
    with open("temp_input.txt", "w") as f1, \
         open("temp_output.txt", "w") as f2:
        f1.write("input data")
        f2.write("output data")
    print("   ✅ Both files written and closed")
    
    # Cleanup
    os.remove("temp_input.txt")
    os.remove("temp_output.txt")
    
    # =============================================================================
    # Custom Context Manager - Function
    # =============================================================================
    print("\n3. CUSTOM CONTEXT MANAGER (function-based)")
    
    @contextmanager
    def timer_context(name):
        """Time a code block"""
        print(f"   ⏱️ Starting {name}...")
        start = time.time()
        try:
            yield
        finally:
            end = time.time()
            print(f"   ⏱️ {name} took {end - start:.4f}s")
    
    with timer_context("Model inference"):
        time.sleep(0.1)
        result = "Generated text"
    
    # =============================================================================
    # Custom Context Manager - Class
    # =============================================================================
    print("\n4. CUSTOM CONTEXT MANAGER (class-based)")
    
    class ModelLoader:
        """Load and unload model"""
        def __init__(self, model_name):
            self.model_name = model_name
            self.model = None
        
        def __enter__(self):
            print(f"   📥 Loading {self.model_name}...")
            self.model = {"name": self.model_name, "loaded": True}
            return self.model
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            print(f"   📤 Unloading {self.model_name}...")
            self.model = None
            return False  # Don't suppress exceptions
    
    with ModelLoader("gpt-4") as model:
        print(f"   🤖 Using model: {model['name']}")
        # Model automatically unloaded after this block
    
    # =============================================================================
    # Real AI Example: Training Context
    # =============================================================================
    print("\n5. REAL AI EXAMPLE: Training Context")
    
    @contextmanager
    def training_mode(model_name):
        """Set model to training mode"""
        print(f"   🎓 Entering training mode for {model_name}")
        print("   - Enabling gradients")
        print("   - Enabling dropout")
        
        try:
            yield
        finally:
            print(f"   🎓 Exiting training mode")
            print("   - Disabling gradients")
            print("   - Disabling dropout")
    
    with training_mode("my-model"):
        print("   📊 Training epoch 1...")
        print("   📊 Training epoch 2...")
    
    # =============================================================================
    # Exception Handling in Context Managers
    # =============================================================================
    print("\n6. EXCEPTION HANDLING")
    
    @contextmanager
    def safe_api_call(endpoint):
        """Safe API call with cleanup"""
        print(f"   🔌 Connecting to {endpoint}...")
        connection = {"endpoint": endpoint, "active": True}
        
        try:
            yield connection
        except Exception as e:
            print(f"   ⚠️ Error occurred: {e}")
            raise
        finally:
            print(f"   🔌 Closing connection to {endpoint}")
            connection["active"] = False
    
    try:
        with safe_api_call("/api/generate") as conn:
            print(f"   Making request to {conn['endpoint']}")
            # Simulate success
    except:
        pass


# Continue to next file due to length...
# (PYTHON_AI_INTERMEDIATE.py continues)

if __name__ == "__main__":
    print("Run the demonstrations...")
