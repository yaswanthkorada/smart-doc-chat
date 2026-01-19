"""
=============================================================================
PYTHON AI/ML FRAMEWORKS & LIBRARIES - COMPLETE REFERENCE
=============================================================================

Purpose: Master all major Python AI/ML libraries
Coverage: From data processing to model deployment

Libraries Covered:
1. NumPy - Numerical computing
2. Pandas - Data manipulation
3. Scikit-learn - Traditional ML
4. OpenAI - GenAI API
5. LangChain - LLM applications
6. Transformers (Hugging Face) - Pre-trained models
7. PyTorch - Deep learning
8. TensorFlow/Keras - Deep learning
9. Streamlit - AI web apps
10. FastAPI - AI APIs

For each library: What, When, Why, How, Examples
"""

print("""
=============================================================================
PYTHON AI FRAMEWORKS & LIBRARIES GUIDE
=============================================================================

This comprehensive guide covers ALL major Python libraries for AI/GenAI.
Each section explains:
- WHAT: What is the library?
- WHEN: When to use it?
- WHY: Why choose it?
- HOW: How to use it?
- EXAMPLES: Working code examples

📚 Navigate to specific sections below...
""")

# =============================================================================
# 1. NumPy - Numerical Computing Foundation
# =============================================================================

def numpy_guide():
    """
    NumPy: Numerical Python
    
    WHAT: Array computing library (foundation for AI)
    WHEN: Need fast numerical operations, arrays, linear algebra
    WHY: 10-100x faster than Python lists, used by all AI libs
    """
    print("\n" + "="*80)
    print("1. NumPy - NUMERICAL COMPUTING")
    print("="*80)
    
    import numpy as np
    
    print("\n📦 Installation: pip install numpy")
    print("🎯 Use Case: Numerical operations, vectors, matrices")
    
    # Arrays
    print("\n1.1 ARRAYS (Core Data Structure)")
    arr = np.array([1, 2, 3, 4, 5])
    print(f"   Array: {arr}")
    print(f"   Type: {type(arr)}")
    print(f"   Shape: {arr.shape}")
    print(f"   Dtype: {arr.dtype}")
    
    # 2D Arrays (Matrices)
    print("\n1.2 MATRICES (2D Arrays)")
    matrix = np.array([[1, 2, 3], [4, 5, 6]])
    print(f"   Matrix:\n{matrix}")
    print(f"   Shape: {matrix.shape}")  # (rows, cols)
    
    # Array Operations
    print("\n1.3 ARRAY OPERATIONS")
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    print(f"   a = {a}")
    print(f"   b = {b}")
    print(f"   a + b = {a + b}")
    print(f"   a * b = {a * b}")  # Element-wise
    print(f"   a @ b = {a @ b}")  # Dot product
    
    # Common Functions
    print("\n1.4 COMMON FUNCTIONS")
    data = np.array([1, 2, 3, 4, 5])
    print(f"   Data: {data}")
    print(f"   Mean: {np.mean(data)}")
    print(f"   Std: {np.std(data):.2f}")
    print(f"   Sum: {np.sum(data)}")
    print(f"   Max: {np.max(data)}")
    
    # Broadcasting
    print("\n1.5 BROADCASTING (Important!)")
    matrix = np.array([[1, 2, 3], [4, 5, 6]])
    vector = np.array([10, 20, 30])
    result = matrix + vector  # Broadcasts vector to each row
    print(f"   Matrix:\n{matrix}")
    print(f"   Vector: {vector}")
    print(f"   Matrix + Vector:\n{result}")
    
    # Indexing & Slicing
    print("\n1.6 INDEXING & SLICING")
    arr = np.array([10, 20, 30, 40, 50])
    print(f"   arr = {arr}")
    print(f"   arr[0] = {arr[0]}")
    print(f"   arr[1:4] = {arr[1:4]}")
    print(f"   arr[arr > 25] = {arr[arr > 25]}")  # Boolean indexing
    
    # Random Numbers (AI data simulation)
    print("\n1.7 RANDOM NUMBERS")
    np.random.seed(42)
    random_data = np.random.randn(5)  # Normal distribution
    print(f"   Random (normal): {random_data}")
    random_uniform = np.random.random(5)  # Uniform [0, 1)
    print(f"   Random (uniform): {random_uniform}")
    
    print("""
    ✅ NumPy Use Cases in AI:
    - Feature vectors and matrices
    - Numerical computations
    - Linear algebra operations
    - Random data generation
    - Foundation for Pandas, PyTorch, TensorFlow
    """)


# =============================================================================
# 2. Pandas - Data Manipulation
# =============================================================================

def pandas_guide():
    """
    Pandas: Data Analysis Library
    
    WHAT: DataFrame library for data manipulation
    WHEN: Need to load, clean, transform tabular data
    WHY: Excel-like operations in Python, handles missing data
    """
    print("\n" + "="*80)
    print("2. Pandas - DATA MANIPULATION")
    print("="*80)
    
    import pandas as pd
    import numpy as np
    
    print("\n📦 Installation: pip install pandas")
    print("🎯 Use Case: Load/clean/transform datasets")
    
    # Create DataFrame
    print("\n2.1 DATAFRAME (Core Data Structure)")
    data = {
        'text': ['I love this', 'Terrible', 'Amazing', 'Bad'],
        'label': ['positive', 'negative', 'positive', 'negative'],
        'score': [0.9, 0.1, 0.95, 0.15]
    }
    df = pd.DataFrame(data)
    print(f"   DataFrame:\n{df}")
    print(f"\n   Shape: {df.shape}")
    print(f"   Columns: {df.columns.tolist()}")
    
    # Reading Data
    print("\n2.2 READING DATA")
    # df = pd.read_csv('data.csv')
    # df = pd.read_json('data.json')
    # df = pd.read_excel('data.xlsx')
    print("   pd.read_csv('data.csv')")
    print("   pd.read_json('data.json')")
    print("   pd.read_excel('data.xlsx')")
    
    # Selecting Data
    print("\n2.3 SELECTING DATA")
    print(f"   df['text']:\n{df['text']}")
    print(f"\n   df[['text', 'label']]:\n{df[['text', 'label']]}")
    print(f"\n   df[df['score'] > 0.5]:\n{df[df['score'] > 0.5]}")
    
    # Statistics
    print("\n2.4 STATISTICS")
    print(f"   describe():\n{df['score'].describe()}")
    print(f"\n   mean: {df['score'].mean():.3f}")
    print(f"   value_counts():\n{df['label'].value_counts()}")
    
    # Transformations
    print("\n2.5 TRANSFORMATIONS")
    df['text_length'] = df['text'].apply(len)
    print(f"   Added text_length:\n{df}")
    
    # Group By
    print("\n2.6 GROUP BY")
    grouped = df.groupby('label')['score'].mean()
    print(f"   Average score by label:\n{grouped}")
    
    # Handling Missing Data
    print("\n2.7 MISSING DATA")
    df_missing = pd.DataFrame({
        'A': [1, 2, np.nan, 4],
        'B': [5, np.nan, 7, 8]
    })
    print(f"   With NaN:\n{df_missing}")
    print(f"\n   Filled:\n{df_missing.fillna(0)}")
    print(f"\n   Dropped:\n{df_missing.dropna()}")
    
    print("""
    ✅ Pandas Use Cases in AI:
    - Load training datasets (CSV, JSON, Excel)
    - Data cleaning and preprocessing
    - Feature engineering
    - Exploratory data analysis (EDA)
    - Split data into train/test sets
    """)


# =============================================================================
# 3. Scikit-learn - Traditional Machine Learning
# =============================================================================

def sklearn_guide():
    """
    Scikit-learn: Machine Learning Library
    
    WHAT: Traditional ML algorithms
    WHEN: Classification, regression, clustering before deep learning
    WHY: Easy API, well-documented, fast, good baselines
    """
    print("\n" + "="*80)
    print("3. Scikit-learn - MACHINE LEARNING")
    print("="*80)
    
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, classification_report
    import numpy as np
    
    print("\n📦 Installation: pip install scikit-learn")
    print("🎯 Use Case: Classification, regression, clustering")
    
    # Sample data
    print("\n3.1 SAMPLE DATASET")
    from sklearn.datasets import make_classification
    X, y = make_classification(n_samples=100, n_features=4, n_classes=2, random_state=42)
    print(f"   Features shape: {X.shape}")
    print(f"   Labels shape: {y.shape}")
    print(f"   First sample: {X[0]}")
    print(f"   First label: {y[0]}")
    
    # Train/Test Split
    print("\n3.2 TRAIN/TEST SPLIT")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"   Train: {X_train.shape}, Test: {X_test.shape}")
    
    # Preprocessing
    print("\n3.3 PREPROCESSING")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print(f"   Original mean: {X_train.mean():.3f}")
    print(f"   Scaled mean: {X_train_scaled.mean():.3f}")
    
    # Training
    print("\n3.4 TRAINING MODEL")
    model = LogisticRegression()
    model.fit(X_train_scaled, y_train)
    print("   ✅ Model trained")
    
    # Prediction
    print("\n3.5 PREDICTION")
    y_pred = model.predict(X_test_scaled)
    print(f"   Predictions: {y_pred[:5]}")
    print(f"   Actual: {y_test[:5]}")
    
    # Evaluation
    print("\n3.6 EVALUATION")
    accuracy = accuracy_score(y_test, y_pred)
    print(f"   Accuracy: {accuracy:.2%}")
    
    print("""
    ✅ Scikit-learn Use Cases:
    - Quick ML baselines
    - Text classification (with TF-IDF)
    - Feature preprocessing
    - Model evaluation metrics
    - Cross-validation
    """)


# =============================================================================
# 4. OpenAI - GenAI API
# =============================================================================

def openai_guide():
    """
    OpenAI: GenAI API Client
    
    WHAT: API for GPT models
    WHEN: Need state-of-the-art LLMs
    WHY: Best-in-class models, simple API
    """
    print("\n" + "="*80)
    print("4. OpenAI - GenAI API")
    print("="*80)
    
    print("\n📦 Installation: pip install openai")
    print("🎯 Use Case: GPT chat, completions, embeddings")
    
    print("""
    4.1 CHAT COMPLETIONS
    
    from openai import OpenAI
    
    client = OpenAI(api_key="your-key")
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "What is AI?"}
        ],
        temperature=0.7,
        max_tokens=100
    )
    
    print(response.choices[0].message.content)
    
    4.2 STREAMING
    
    stream = client.chat.completions.create(
        model="gpt-4",
        messages=[...],
        stream=True
    )
    
    for chunk in stream:
        print(chunk.choices[0].delta.content, end="")
    
    4.3 EMBEDDINGS
    
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input="Your text here"
    )
    
    embedding = response.data[0].embedding  # 1536 dimensions
    
    4.4 FUNCTION CALLING
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    }
                }
            }
        }
    ]
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[...],
        tools=tools
    )
    
    ✅ OpenAI Use Cases:
    - Chatbots and virtual assistants
    - Content generation
    - Code generation
    - Text embeddings for search
    - Function calling for tools
    """)


# =============================================================================
# 5. LangChain - LLM Applications
# =============================================================================

def langchain_guide():
    """
    LangChain: Framework for LLM apps
    
    WHAT: Framework for building LLM applications
    WHEN: Building chains, agents, RAG systems
    WHY: Simplifies LLM app development
    """
    print("\n" + "="*80)
    print("5. LangChain - LLM APPLICATIONS")
    print("="*80)
    
    print("\n📦 Installation: pip install langchain langchain-openai")
    print("🎯 Use Case: Chains, agents, RAG, memory")
    
    print("""
    5.1 BASIC CHAIN
    
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    prompt = ChatPromptTemplate.from_template("Tell me about {topic}")
    chain = prompt | llm
    
    response = chain.invoke({"topic": "AI"})
    
    5.2 RAG (Retrieval Augmented Generation)
    
    from langchain.vectorstores import Chroma
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    
    # Create vector store
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings()
    )
    
    # Retrieve and generate
    retriever = vectorstore.as_retriever()
    docs = retriever.get_relevant_documents("query")
    
    5.3 AGENTS
    
    from langchain.agents import create_openai_functions_agent
    from langchain.tools import Tool
    
    tools = [
        Tool(
            name="Calculator",
            func=lambda x: eval(x),
            description="For math"
        )
    ]
    
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    5.4 MEMORY
    
    from langchain.memory import ConversationBufferMemory
    
    memory = ConversationBufferMemory()
    memory.save_context(
        {"input": "Hi, I'm Bob"},
        {"output": "Hello Bob!"}
    )
    
    ✅ LangChain Use Cases:
    - RAG systems (chat with documents)
    - AI agents with tools
    - Conversational memory
    - Prompt templates
    - Document loading and splitting
    """)


# Continue in next file due to length...

if __name__ == "__main__":
    print("Run individual functions to see each library guide")
    print("Example: numpy_guide(), pandas_guide(), sklearn_guide(), etc.")
