"""
=============================================================================
PYTHON FOR AI/GenAI - BEGINNER LEVEL (COMPLETE GUIDE)
=============================================================================

Purpose: Learn Python fundamentals needed for AI/GenAI development
Target: Absolute beginners to confident basics
Time: 2-3 hours to complete all examples

What You'll Learn:
1. Python Syntax & Data Types (for AI data handling)
2. Control Flow (for AI logic)
3. Functions (for AI model components)
4. Data Structures (for AI datasets)
5. File I/O (for AI data loading)
6. Error Handling (for robust AI systems)
7. Basic OOP (for AI model classes)

AI Context: Why each concept matters for AI development
"""

# =============================================================================
# PART 1: VARIABLES & DATA TYPES
# =============================================================================
# AI Context: Understanding data types is crucial for handling:
# - Model inputs (tensors, arrays)
# - Text data (strings)
# - Numerical computations (int, float)
# - Boolean flags (True/False)
# =============================================================================

def demonstrate_data_types():
    """
    Basic Python Data Types for AI
    
    When to use in AI:
    - str: Text data, prompts, responses
    - int: Counts, indices, epochs
    - float: Probabilities, losses, learning rates
    - bool: Flags, conditions, masks
    """
    print("\n" + "="*80)
    print("PART 1: DATA TYPES FOR AI")
    print("="*80)
    
    # Strings - for text/prompts
    prompt = "Explain quantum computing"
    model_name = "gpt-4"
    print(f"\n1. STRING (text data):")
    print(f"   prompt = '{prompt}'")
    print(f"   model = '{model_name}'")
    print(f"   Type: {type(prompt)}")
    
    # Integers - for counting
    num_epochs = 100
    batch_size = 32
    max_tokens = 1024
    print(f"\n2. INTEGER (counts, indices):")
    print(f"   epochs = {num_epochs}")
    print(f"   batch_size = {batch_size}")
    print(f"   Type: {type(num_epochs)}")
    
    # Floats - for numerical values
    learning_rate = 0.001
    temperature = 0.7
    accuracy = 0.95
    print(f"\n3. FLOAT (decimals, probabilities):")
    print(f"   learning_rate = {learning_rate}")
    print(f"   temperature = {temperature}")
    print(f"   accuracy = {accuracy}")
    print(f"   Type: {type(learning_rate)}")
    
    # Booleans - for flags
    is_training = True
    use_gpu = False
    print(f"\n4. BOOLEAN (flags, conditions):")
    print(f"   is_training = {is_training}")
    print(f"   use_gpu = {use_gpu}")
    print(f"   Type: {type(is_training)}")
    
    # Type conversion (important for AI)
    print(f"\n5. TYPE CONVERSION:")
    str_num = "100"
    int_num = int(str_num)  # String to int
    float_num = float(int_num)  # Int to float
    print(f"   '{str_num}' (str) → {int_num} (int) → {float_num} (float)")
    
    # String operations for AI prompts
    print(f"\n6. STRING OPERATIONS (for prompts):")
    base_prompt = "You are a helpful AI assistant."
    user_query = "What is Python?"
    full_prompt = base_prompt + "\n\nUser: " + user_query
    print(f"   Combined prompt:\n{full_prompt}")
    
    # F-strings (modern, best for AI logging)
    model = "GPT-4"
    tokens = 1500
    cost = 0.03
    log = f"Model: {model}, Tokens: {tokens}, Cost: ${cost:.2f}"
    print(f"\n7. F-STRINGS (for logging):")
    print(f"   {log}")


# =============================================================================
# PART 2: DATA STRUCTURES
# =============================================================================
# AI Context: Essential for managing:
# - Lists: Sequences of data (prompts, responses)
# - Tuples: Fixed data (model config)
# - Dictionaries: Key-value pairs (API responses, configs)
# - Sets: Unique items (vocabulary, seen examples)
# =============================================================================

def demonstrate_data_structures():
    """
    Data Structures for AI Development
    
    When to use:
    - List: Ordered, mutable sequences (training data)
    - Tuple: Immutable sequences (model shape, config)
    - Dict: Key-value pairs (JSON responses, configs)
    - Set: Unique items (vocabulary, deduplication)
    """
    print("\n" + "="*80)
    print("PART 2: DATA STRUCTURES FOR AI")
    print("="*80)
    
    # =============================================================================
    # LISTS - Most common for AI data
    # =============================================================================
    print("\n1. LISTS (ordered, mutable)")
    print("   Use: Training data, batch processing, sequences")
    
    # List of prompts
    prompts = [
        "Explain AI",
        "What is machine learning?",
        "Define neural networks"
    ]
    print(f"\n   prompts = {prompts}")
    print(f"   Length: {len(prompts)}")
    print(f"   First prompt: {prompts[0]}")
    print(f"   Last prompt: {prompts[-1]}")
    
    # Adding to lists
    prompts.append("What is deep learning?")
    print(f"\n   After append: {len(prompts)} prompts")
    
    # List slicing (important for batching)
    batch = prompts[0:2]  # First 2 items
    print(f"   Batch (first 2): {batch}")
    
    # List comprehension (efficient, Pythonic)
    lengths = [len(p) for p in prompts]
    print(f"   Prompt lengths: {lengths}")
    
    # Common list operations for AI
    print("\n   Common List Operations:")
    scores = [0.9, 0.85, 0.92, 0.88]
    print(f"   scores = {scores}")
    print(f"   max = {max(scores)}")
    print(f"   min = {min(scores)}")
    print(f"   avg = {sum(scores)/len(scores):.3f}")
    print(f"   sorted = {sorted(scores, reverse=True)}")
    
    # =============================================================================
    # TUPLES - Immutable, for fixed configs
    # =============================================================================
    print("\n2. TUPLES (immutable)")
    print("   Use: Fixed configs, model shapes, coordinates")
    
    # Model configuration
    model_config = ("gpt-3.5-turbo", 4096, 0.7)  # (name, max_tokens, temp)
    print(f"\n   model_config = {model_config}")
    print(f"   Model: {model_config[0]}")
    print(f"   Max tokens: {model_config[1]}")
    print(f"   Temperature: {model_config[2]}")
    
    # Tuple unpacking (very useful!)
    model_name, max_tokens, temperature = model_config
    print(f"\n   Unpacked: {model_name}, {max_tokens}, {temperature}")
    
    # Image shape tuple
    image_shape = (224, 224, 3)  # (height, width, channels)
    print(f"   image_shape = {image_shape}")
    
    # =============================================================================
    # DICTIONARIES - Most important for AI APIs
    # =============================================================================
    print("\n3. DICTIONARIES (key-value pairs)")
    print("   Use: API requests/responses, configurations, JSON data")
    
    # API request
    api_request = {
        "model": "gpt-4",
        "prompt": "Explain Python",
        "max_tokens": 100,
        "temperature": 0.7
    }
    print(f"\n   api_request = {api_request}")
    print(f"   Model: {api_request['model']}")
    print(f"   Prompt: {api_request['prompt']}")
    
    # Safe access with .get()
    api_key = api_request.get("api_key", "not_provided")
    print(f"   API Key: {api_key}")
    
    # Adding/updating
    api_request["stream"] = True
    print(f"\n   After adding 'stream': {api_request.keys()}")
    
    # Iterating dictionaries
    print("\n   All config items:")
    for key, value in api_request.items():
        print(f"   - {key}: {value}")
    
    # Nested dictionaries (common in AI responses)
    response = {
        "id": "chatcmpl-123",
        "model": "gpt-4",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Python is a programming language."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }
    
    print("\n   Nested dictionary (API response):")
    print(f"   Model: {response['model']}")
    print(f"   Content: {response['choices'][0]['message']['content']}")
    print(f"   Total tokens: {response['usage']['total_tokens']}")
    
    # =============================================================================
    # SETS - For unique items
    # =============================================================================
    print("\n4. SETS (unique items)")
    print("   Use: Vocabulary, deduplication, membership testing")
    
    # Vocabulary building
    words = ["AI", "ML", "AI", "DL", "ML", "NLP"]
    vocabulary = set(words)
    print(f"\n   words = {words}")
    print(f"   vocabulary = {vocabulary}")
    print(f"   Unique words: {len(vocabulary)}")
    
    # Membership testing (fast!)
    print(f"   'AI' in vocabulary: {'AI' in vocabulary}")
    print(f"   'CV' in vocabulary: {'CV' in vocabulary}")
    
    # Set operations
    set1 = {"AI", "ML", "DL"}
    set2 = {"ML", "NLP", "CV"}
    print(f"\n   set1 = {set1}")
    print(f"   set2 = {set2}")
    print(f"   Union: {set1 | set2}")
    print(f"   Intersection: {set1 & set2}")
    print(f"   Difference: {set1 - set2}")


# =============================================================================
# PART 3: CONTROL FLOW
# =============================================================================
# AI Context: Essential for:
# - Conditional logic (model selection, validation)
# - Loops (training epochs, batch processing)
# - Iteration (dataset processing)
# =============================================================================

def demonstrate_control_flow():
    """
    Control Flow for AI Logic
    
    When to use:
    - if/elif/else: Model selection, validation
    - for loops: Batch processing, epochs
    - while loops: Training until convergence
    - break/continue: Early stopping
    """
    print("\n" + "="*80)
    print("PART 3: CONTROL FLOW FOR AI")
    print("="*80)
    
    # =============================================================================
    # IF/ELIF/ELSE - Conditional logic
    # =============================================================================
    print("\n1. IF/ELIF/ELSE (conditional logic)")
    print("   Use: Model selection, validation, error handling")
    
    # Example: Select model based on task
    task = "text_generation"
    
    if task == "text_generation":
        model = "gpt-4"
        print(f"\n   Task: {task} → Model: {model}")
    elif task == "classification":
        model = "bert-base"
        print(f"\n   Task: {task} → Model: {model}")
    else:
        model = "default"
        print(f"\n   Task: {task} → Model: {model}")
    
    # Example: Validate input
    max_tokens = 150000
    
    if max_tokens > 128000:
        print(f"\n   ⚠️ Warning: {max_tokens} exceeds limit (128000)")
        max_tokens = 128000
        print(f"   Adjusted to: {max_tokens}")
    else:
        print(f"\n   ✅ Valid: {max_tokens} tokens")
    
    # Example: Model selection by accuracy
    accuracy = 0.92
    
    if accuracy >= 0.95:
        status = "Excellent"
    elif accuracy >= 0.90:
        status = "Good"
    elif accuracy >= 0.80:
        status = "Acceptable"
    else:
        status = "Needs improvement"
    
    print(f"\n   Accuracy: {accuracy} → Status: {status}")
    
    # Ternary operator (one-line if-else)
    is_training = True
    mode = "train" if is_training else "eval"
    print(f"\n   Ternary: mode = '{mode}' (is_training={is_training})")
    
    # =============================================================================
    # FOR LOOPS - Most common in AI
    # =============================================================================
    print("\n2. FOR LOOPS (iteration)")
    print("   Use: Batch processing, epochs, dataset iteration")
    
    # Example: Training epochs
    print("\n   Training simulation:")
    for epoch in range(1, 6):  # 5 epochs
        loss = 1.0 / epoch  # Simulated decreasing loss
        print(f"   Epoch {epoch}/5: loss = {loss:.4f}")
    
    # Example: Batch processing
    prompts = ["What is AI?", "Explain ML", "Define DL"]
    print("\n   Batch processing:")
    for i, prompt in enumerate(prompts):
        response = f"Response to: {prompt}"
        print(f"   [{i+1}] {response}")
    
    # Example: List comprehension (Pythonic!)
    scores = [0.85, 0.90, 0.88, 0.92, 0.87]
    high_scores = [s for s in scores if s >= 0.90]
    print(f"\n   All scores: {scores}")
    print(f"   High scores (≥0.90): {high_scores}")
    
    # Example: Dictionary iteration
    config = {"model": "gpt-4", "temp": 0.7, "max_tokens": 1000}
    print("\n   Config iteration:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    # =============================================================================
    # WHILE LOOPS - For convergence
    # =============================================================================
    print("\n3. WHILE LOOPS (until condition)")
    print("   Use: Training until convergence, retry logic")
    
    # Example: Train until convergence
    print("\n   Training until loss < 0.01:")
    loss = 1.0
    iteration = 0
    while loss > 0.01 and iteration < 10:
        loss *= 0.7  # Simulated decrease
        iteration += 1
        print(f"   Iteration {iteration}: loss = {loss:.4f}")
    print(f"   Converged after {iteration} iterations!")
    
    # =============================================================================
    # BREAK & CONTINUE - Early stopping
    # =============================================================================
    print("\n4. BREAK & CONTINUE (control loop)")
    print("   Use: Early stopping, skip bad data")
    
    # Example: Early stopping
    print("\n   Early stopping when accuracy > 0.95:")
    for epoch in range(1, 11):
        accuracy = 0.85 + (epoch * 0.02)
        print(f"   Epoch {epoch}: accuracy = {accuracy:.2f}")
        if accuracy > 0.95:
            print(f"   ✅ Target reached! Stopping early.")
            break
    
    # Example: Skip invalid data
    print("\n   Skip invalid responses:")
    responses = ["Good", "", "Excellent", None, "Perfect"]
    for i, response in enumerate(responses):
        if not response:  # Skip empty/None
            print(f"   [{i}] Skipped (invalid)")
            continue
        print(f"   [{i}] Processing: {response}")
    
    # =============================================================================
    # RANGE - Essential for AI loops
    # =============================================================================
    print("\n5. RANGE (generate sequences)")
    print("   Use: Epochs, batches, indices")
    
    print("\n   range(5):        ", list(range(5)))         # 0 to 4
    print("   range(1, 6):     ", list(range(1, 6)))       # 1 to 5
    print("   range(0, 10, 2): ", list(range(0, 10, 2)))   # 0, 2, 4, 6, 8


# =============================================================================
# PART 4: FUNCTIONS
# =============================================================================
# AI Context: Building blocks of AI systems:
# - Model initialization
# - Data preprocessing
# - Prediction functions
# - Utility functions
# =============================================================================

def demonstrate_functions():
    """
    Functions for AI Development
    
    When to use:
    - Code reusability
    - Modularity
    - Testing
    - Clean architecture
    """
    print("\n" + "="*80)
    print("PART 4: FUNCTIONS FOR AI")
    print("="*80)
    
    # =============================================================================
    # Basic functions
    # =============================================================================
    print("\n1. BASIC FUNCTIONS")
    
    def preprocess_text(text):
        """Clean and prepare text for AI model"""
        # Remove extra whitespace
        cleaned = " ".join(text.split())
        # Lowercase
        cleaned = cleaned.lower()
        return cleaned
    
    raw_text = "  Hello   WORLD!  "
    clean_text = preprocess_text(raw_text)
    print(f"   Raw: '{raw_text}'")
    print(f"   Cleaned: '{clean_text}'")
    
    # =============================================================================
    # Functions with multiple parameters
    # =============================================================================
    print("\n2. MULTIPLE PARAMETERS")
    
    def call_llm(prompt, model="gpt-3.5-turbo", temperature=0.7, max_tokens=100):
        """Simulate LLM API call"""
        result = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response": f"Mock response to: {prompt[:30]}..."
        }
        return result
    
    # Call with defaults
    result1 = call_llm("What is AI?")
    print(f"   Result 1: {result1['model']}, temp={result1['temperature']}")
    
    # Call with custom params
    result2 = call_llm("Explain ML", model="gpt-4", temperature=0.9)
    print(f"   Result 2: {result2['model']}, temp={result2['temperature']}")
    
    # =============================================================================
    # Return multiple values
    # =============================================================================
    print("\n3. MULTIPLE RETURN VALUES")
    
    def evaluate_model(predictions, labels):
        """Calculate accuracy and loss"""
        correct = sum(p == l for p, l in zip(predictions, labels))
        accuracy = correct / len(labels)
        loss = 1 - accuracy  # Simplified
        return accuracy, loss
    
    preds = [1, 0, 1, 1, 0]
    labels = [1, 0, 1, 0, 0]
    acc, loss = evaluate_model(preds, labels)
    print(f"   Accuracy: {acc:.2f}, Loss: {loss:.2f}")
    
    # =============================================================================
    # *args and **kwargs
    # =============================================================================
    print("\n4. *ARGS & **KWARGS (flexible arguments)")
    
    def create_prompt(*parts, **options):
        """Build prompt from multiple parts with options"""
        prompt = "\n".join(parts)
        
        if options.get("add_context"):
            prompt = "Context: AI assistant\n\n" + prompt
        
        if options.get("add_instruction"):
            prompt += "\n\nPlease respond clearly."
        
        return prompt
    
    prompt = create_prompt(
        "You are helpful.",
        "User: What is Python?",
        add_context=True,
        add_instruction=True
    )
    print(f"   Generated prompt:\n{prompt}")
    
    # =============================================================================
    # Lambda functions (inline functions)
    # =============================================================================
    print("\n5. LAMBDA FUNCTIONS (one-liners)")
    
    # Simple transformation
    normalize = lambda x: (x - 0.5) * 2  # Scale to [-1, 1]
    print(f"   normalize(0.5) = {normalize(0.5)}")
    print(f"   normalize(0.75) = {normalize(0.75)}")
    
    # Use with map/filter
    scores = [0.85, 0.92, 0.78, 0.95, 0.88]
    high_scores = list(filter(lambda x: x >= 0.90, scores))
    print(f"   All scores: {scores}")
    print(f"   High scores: {high_scores}")
    
    # =============================================================================
    # Docstrings (essential for AI code)
    # =============================================================================
    print("\n6. DOCSTRINGS (documentation)")
    
    def train_model(data, epochs, learning_rate):
        """
        Train AI model on data.
        
        Args:
            data: Training dataset
            epochs: Number of training iterations
            learning_rate: Learning rate for optimizer
            
        Returns:
            Trained model
            
        Example:
            >>> model = train_model(data, epochs=10, learning_rate=0.001)
        """
        return f"Model trained for {epochs} epochs with lr={learning_rate}"
    
    print(f"   Docstring:\n{train_model.__doc__}")


# =============================================================================
# PART 5: FILE I/O
# =============================================================================
# AI Context: Critical for:
# - Loading datasets
# - Saving models
# - Reading configs
# - Writing logs
# =============================================================================

def demonstrate_file_io():
    """
    File I/O for AI Data Management
    
    When to use:
    - Read: Load data, configs, models
    - Write: Save results, logs, models
    - JSON: API configs, responses
    - CSV: Datasets, results
    """
    print("\n" + "="*80)
    print("PART 5: FILE I/O FOR AI")
    print("="*80)
    
    import json
    import csv
    from pathlib import Path
    
    # =============================================================================
    # Text files - Basic I/O
    # =============================================================================
    print("\n1. TEXT FILES")
    
    # Write prompts to file
    prompts = [
        "What is machine learning?",
        "Explain neural networks",
        "Define deep learning"
    ]
    
    with open("temp_prompts.txt", "w") as f:
        for prompt in prompts:
            f.write(prompt + "\n")
    print("   ✅ Wrote prompts to temp_prompts.txt")
    
    # Read prompts from file
    with open("temp_prompts.txt", "r") as f:
        loaded_prompts = [line.strip() for line in f]
    print(f"   ✅ Loaded {len(loaded_prompts)} prompts")
    
    # =============================================================================
    # JSON files - Most common for AI configs
    # =============================================================================
    print("\n2. JSON FILES (configs, API responses)")
    
    # AI model configuration
    config = {
        "model": "gpt-4",
        "parameters": {
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 0.9
        },
        "system_prompt": "You are a helpful AI assistant.",
        "settings": {
            "stream": False,
            "log_level": "INFO"
        }
    }
    
    # Save config
    with open("temp_config.json", "w") as f:
        json.dump(config, f, indent=2)
    print("   ✅ Saved config to temp_config.json")
    
    # Load config
    with open("temp_config.json", "r") as f:
        loaded_config = json.load(f)
    print(f"   ✅ Loaded config: {loaded_config['model']}")
    print(f"   Temperature: {loaded_config['parameters']['temperature']}")
    
    # =============================================================================
    # CSV files - For datasets
    # =============================================================================
    print("\n3. CSV FILES (datasets, results)")
    
    # Sample training data
    training_data = [
        ["text", "label"],
        ["I love this!", "positive"],
        ["This is terrible", "negative"],
        ["Amazing product", "positive"]
    ]
    
    # Write CSV
    with open("temp_data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(training_data)
    print("   ✅ Saved dataset to temp_data.csv")
    
    # Read CSV
    with open("temp_data.csv", "r") as f:
        reader = csv.reader(f)
        data = list(reader)
    print(f"   ✅ Loaded {len(data)-1} samples (excluding header)")
    
    # Read CSV as dictionary
    with open("temp_data.csv", "r") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i < 2:  # Show first 2
                print(f"   Sample {i+1}: {row['text']} → {row['label']}")
    
    # =============================================================================
    # Path handling - Modern approach
    # =============================================================================
    print("\n4. PATH HANDLING (pathlib)")
    
    # Create directory
    data_dir = Path("temp_ai_data")
    data_dir.mkdir(exist_ok=True)
    print(f"   ✅ Created directory: {data_dir}")
    
    # Save file in directory
    model_path = data_dir / "model.txt"
    model_path.write_text("Model weights here")
    print(f"   ✅ Saved to: {model_path}")
    
    # Check if file exists
    print(f"   File exists: {model_path.exists()}")
    
    # Get file info
    if model_path.exists():
        print(f"   File size: {model_path.stat().st_size} bytes")
    
    # Clean up
    import shutil
    shutil.rmtree(data_dir)
    for temp_file in ["temp_prompts.txt", "temp_config.json", "temp_data.csv"]:
        Path(temp_file).unlink(missing_ok=True)
    print("\n   🧹 Cleaned up temp files")


# =============================================================================
# PART 6: ERROR HANDLING
# =============================================================================
# AI Context: Robust AI systems need:
# - API error handling
# - Data validation
# - Graceful degradation
# - Logging
# =============================================================================

def demonstrate_error_handling():
    """
    Error Handling for Robust AI Systems
    
    When to use:
    - try/except: API calls, file I/O
    - raise: Input validation
    - finally: Cleanup resources
    - custom exceptions: Specific errors
    """
    print("\n" + "="*80)
    print("PART 6: ERROR HANDLING FOR AI")
    print("="*80)
    
    # =============================================================================
    # Basic try/except
    # =============================================================================
    print("\n1. BASIC TRY/EXCEPT")
    
    def divide_loss(loss, batch_size):
        """Calculate per-sample loss"""
        try:
            return loss / batch_size
        except ZeroDivisionError:
            print("   ⚠️ Error: batch_size cannot be 0")
            return None
    
    print(f"   divide_loss(1.0, 32) = {divide_loss(1.0, 32)}")
    print(f"   divide_loss(1.0, 0) = {divide_loss(1.0, 0)}")
    
    # =============================================================================
    # Multiple exception types
    # =============================================================================
    print("\n2. MULTIPLE EXCEPTION TYPES")
    
    def parse_response(response_json):
        """Parse AI model response"""
        try:
            data = response_json
            content = data["choices"][0]["message"]["content"]
            tokens = data["usage"]["total_tokens"]
            return content, tokens
        except KeyError as e:
            print(f"   ⚠️ Missing key: {e}")
            return None, 0
        except IndexError:
            print("   ⚠️ No choices in response")
            return None, 0
        except Exception as e:
            print(f"   ⚠️ Unexpected error: {e}")
            return None, 0
    
    # Valid response
    valid = {
        "choices": [{"message": {"content": "Hello"}}],
        "usage": {"total_tokens": 10}
    }
    content, tokens = parse_response(valid)
    print(f"   Valid: content='{content}', tokens={tokens}")
    
    # Invalid response
    invalid = {"data": "incomplete"}
    content, tokens = parse_response(invalid)
    print(f"   Invalid: content={content}, tokens={tokens}")
    
    # =============================================================================
    # try/except/else/finally
    # =============================================================================
    print("\n3. TRY/EXCEPT/ELSE/FINALLY")
    
    def load_model(model_path):
        """Load model with proper resource management"""
        file_handle = None
        try:
            print(f"   Attempting to load: {model_path}")
            # Simulate loading
            if "invalid" in model_path:
                raise FileNotFoundError(f"Model not found: {model_path}")
            file_handle = "model_data"
            print("   ✅ Model loaded successfully")
        except FileNotFoundError as e:
            print(f"   ⚠️ Error: {e}")
            return None
        else:
            print("   📊 Model validation passed")
            return file_handle
        finally:
            print("   🧹 Cleanup completed")
    
    load_model("valid_model.pt")
    print()
    load_model("invalid_model.pt")
    
    # =============================================================================
    # Raising exceptions
    # =============================================================================
    print("\n4. RAISING EXCEPTIONS (validation)")
    
    def validate_temperature(temp):
        """Validate LLM temperature parameter"""
        if not isinstance(temp, (int, float)):
            raise TypeError(f"Temperature must be numeric, got {type(temp)}")
        if temp < 0 or temp > 2:
            raise ValueError(f"Temperature must be 0-2, got {temp}")
        return True
    
    try:
        validate_temperature(0.7)
        print("   ✅ Valid temperature: 0.7")
    except (TypeError, ValueError) as e:
        print(f"   ⚠️ {e}")
    
    try:
        validate_temperature(3.0)
        print("   ✅ Valid temperature: 3.0")
    except (TypeError, ValueError) as e:
        print(f"   ⚠️ {e}")
    
    # =============================================================================
    # Custom exceptions
    # =============================================================================
    print("\n5. CUSTOM EXCEPTIONS")
    
    class ModelError(Exception):
        """Custom exception for model errors"""
        pass
    
    class TokenLimitError(ModelError):
        """Raised when token limit exceeded"""
        pass
    
    def generate_text(prompt, max_tokens):
        """Generate text with token limit check"""
        estimated_tokens = len(prompt.split()) * 1.3
        if estimated_tokens > max_tokens:
            raise TokenLimitError(
                f"Estimated {estimated_tokens:.0f} tokens exceeds limit of {max_tokens}"
            )
        return f"Generated text for: {prompt[:30]}..."
    
    try:
        result = generate_text("Short prompt", max_tokens=100)
        print(f"   ✅ {result}")
    except TokenLimitError as e:
        print(f"   ⚠️ {e}")
    
    try:
        long_prompt = " ".join(["word"] * 1000)
        result = generate_text(long_prompt, max_tokens=100)
        print(f"   ✅ {result}")
    except TokenLimitError as e:
        print(f"   ⚠️ {e}")


# =============================================================================
# PART 7: BASIC OOP FOR AI
# =============================================================================
# AI Context: Classes are essential for:
# - Model wrappers
# - Data loaders
# - Agent systems
# - API clients
# =============================================================================

def demonstrate_basic_oop():
    """
    Object-Oriented Programming for AI
    
    When to use:
    - Classes: Model wrappers, data structures
    - __init__: Setup/configuration
    - Methods: Model operations
    - Attributes: Model state
    """
    print("\n" + "="*80)
    print("PART 7: BASIC OOP FOR AI")
    print("="*80)
    
    # =============================================================================
    # Basic class - AI Model wrapper
    # =============================================================================
    print("\n1. BASIC CLASS (Model Wrapper)")
    
    class SimpleModel:
        """Simple AI model wrapper"""
        
        def __init__(self, model_name, temperature=0.7):
            """Initialize model"""
            self.model_name = model_name
            self.temperature = temperature
            self.call_count = 0
            print(f"   ✅ Initialized {model_name}")
        
        def generate(self, prompt):
            """Generate response"""
            self.call_count += 1
            response = f"Response from {self.model_name}: {prompt[:30]}..."
            return response
        
        def get_stats(self):
            """Get usage statistics"""
            return {
                "model": self.model_name,
                "temperature": self.temperature,
                "calls": self.call_count
            }
    
    # Create instance
    model = SimpleModel("gpt-3.5-turbo", temperature=0.8)
    
    # Use model
    response1 = model.generate("What is AI?")
    response2 = model.generate("Explain ML")
    print(f"\n   Response 1: {response1}")
    print(f"   Response 2: {response2}")
    
    # Get stats
    stats = model.get_stats()
    print(f"\n   Stats: {stats}")
    
    # =============================================================================
    # Class with properties
    # =============================================================================
    print("\n2. CLASS WITH PROPERTIES")
    
    class DataLoader:
        """Data loader with validation"""
        
        def __init__(self, batch_size):
            self._batch_size = batch_size
            self._data = []
        
        @property
        def batch_size(self):
            """Get batch size"""
            return self._batch_size
        
        @batch_size.setter
        def batch_size(self, value):
            """Set batch size with validation"""
            if value <= 0:
                raise ValueError("Batch size must be positive")
            self._batch_size = value
        
        def load_data(self, data):
            """Load data"""
            self._data = data
            print(f"   ✅ Loaded {len(data)} samples")
        
        def get_batches(self):
            """Get number of batches"""
            if not self._data:
                return 0
            return (len(self._data) + self._batch_size - 1) // self._batch_size
    
    loader = DataLoader(batch_size=32)
    print(f"   Batch size: {loader.batch_size}")
    
    # Change batch size
    loader.batch_size = 64
    print(f"   Updated batch size: {loader.batch_size}")
    
    # Load data
    loader.load_data(list(range(100)))
    print(f"   Number of batches: {loader.get_batches()}")
    
    # =============================================================================
    # Class inheritance
    # =============================================================================
    print("\n3. CLASS INHERITANCE")
    
    class BaseModel:
        """Base model class"""
        
        def __init__(self, name):
            self.name = name
        
        def predict(self, input_data):
            """Base prediction method"""
            return f"Prediction from {self.name}"
    
    class GPTModel(BaseModel):
        """GPT-specific model"""
        
        def __init__(self, name, max_tokens=1000):
            super().__init__(name)
            self.max_tokens = max_tokens
        
        def predict(self, input_data):
            """Override with GPT-specific logic"""
            base = super().predict(input_data)
            return f"{base} (max_tokens={self.max_tokens})"
    
    base_model = BaseModel("base-model")
    gpt_model = GPTModel("gpt-4", max_tokens=2000)
    
    print(f"   Base: {base_model.predict('test')}")
    print(f"   GPT:  {gpt_model.predict('test')}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Run all demonstrations"""
    
    print("="*80)
    print("PYTHON FOR AI/GenAI - BEGINNER LEVEL")
    print("="*80)
    print("\nThis guide covers Python basics essential for AI development.")
    print("Each section shows: WHAT, WHY, WHEN, and HOW to use each concept.\n")
    
    input("Press Enter to start...")
    
    # Part 1: Data Types
    demonstrate_data_types()
    input("\nPress Enter to continue to Part 2...")
    
    # Part 2: Data Structures
    demonstrate_data_structures()
    input("\nPress Enter to continue to Part 3...")
    
    # Part 3: Control Flow
    demonstrate_control_flow()
    input("\nPress Enter to continue to Part 4...")
    
    # Part 4: Functions
    demonstrate_functions()
    input("\nPress Enter to continue to Part 5...")
    
    # Part 5: File I/O
    demonstrate_file_io()
    input("\nPress Enter to continue to Part 6...")
    
    # Part 6: Error Handling
    demonstrate_error_handling()
    input("\nPress Enter to continue to Part 7...")
    
    # Part 7: Basic OOP
    demonstrate_basic_oop()
    
    # Summary
    print("\n" + "="*80)
    print("✅ BEGINNER LEVEL COMPLETE!")
    print("="*80)
    print("""
📚 What You Learned:
1. ✅ Data Types - Variables for AI (strings, numbers, booleans)
2. ✅ Data Structures - Lists, tuples, dicts, sets for AI data
3. ✅ Control Flow - if/else, loops, iteration for AI logic
4. ✅ Functions - Reusable AI components
5. ✅ File I/O - Load/save data, configs, models
6. ✅ Error Handling - Robust AI systems
7. ✅ Basic OOP - Model wrappers and classes

🎯 Next Steps:
- Run: python PYTHON_AI_INTERMEDIATE.py
- Learn: List comprehensions, generators, decorators
- Practice: Build a simple text classifier
- Study: NumPy, Pandas for data manipulation

💡 Key Takeaways:
- Python basics are essential for AI development
- Understanding data structures is crucial for handling AI data
- Functions and classes make code reusable and maintainable
- Error handling is critical for production AI systems

Ready for intermediate level? 🚀
""")


if __name__ == "__main__":
    main()
