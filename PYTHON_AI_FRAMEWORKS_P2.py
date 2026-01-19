"""
=============================================================================
PYTHON AI FRAMEWORKS PART 2 - Deep Learning & Deployment
=============================================================================

Continuation covering:
6. Transformers (Hugging Face)
7. PyTorch
8. TensorFlow/Keras
9. Streamlit
10. FastAPI
"""

# =============================================================================
# 6. Transformers (Hugging Face) - Pre-trained Models
# =============================================================================

def transformers_guide():
    """
    Transformers: Pre-trained model library
    
    WHAT: Library for using pre-trained models (BERT, GPT, etc.)
    WHEN: Need pre-trained models for NLP tasks
    WHY: 100,000+ models, easy to use, state-of-the-art
    """
    print("\n" + "="*80)
    print("6. Transformers (Hugging Face) - PRE-TRAINED MODELS")
    print("="*80)
    
    print("\n📦 Installation: pip install transformers torch")
    print("🎯 Use Case: Use pre-trained models for NLP")
    
    print("""
    6.1 PIPELINES (Easiest Way)
    
    from transformers import pipeline
    
    # Text Classification
    classifier = pipeline("sentiment-analysis")
    result = classifier("I love this!")
    # [{'label': 'POSITIVE', 'score': 0.99}]
    
    # Text Generation
    generator = pipeline("text-generation", model="gpt2")
    result = generator("Once upon a time", max_length=50)
    
    # Question Answering
    qa = pipeline("question-answering")
    result = qa(question="What is AI?", context="AI is...")
    
    # Fill Mask
    unmasker = pipeline("fill-mask", model="bert-base-uncased")
    result = unmasker("Paris is the [MASK] of France.")
    
    6.2 MODELS & TOKENIZERS
    
    from transformers import AutoTokenizer, AutoModel
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    model = AutoModel.from_pretrained("bert-base-uncased")
    
    # Tokenize
    inputs = tokenizer("Hello world", return_tensors="pt")
    # {'input_ids': tensor([[...]])}
    
    # Get embeddings
    outputs = model(**inputs)
    embeddings = outputs.last_hidden_state
    
    6.3 SPECIFIC MODELS
    
    # BERT for classification
    from transformers import BertForSequenceClassification
    model = BertForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        num_labels=2
    )
    
    # GPT-2 for generation
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    model = GPT2LMHeadModel.from_pretrained("gpt2")
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    
    input_ids = tokenizer.encode("Hello", return_tensors="pt")
    output = model.generate(input_ids, max_length=50)
    text = tokenizer.decode(output[0])
    
    6.4 FINE-TUNING
    
    from transformers import Trainer, TrainingArguments
    
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=16,
        learning_rate=2e-5,
        logging_dir="./logs"
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset
    )
    
    trainer.train()
    
    6.5 HUGGING FACE HUB
    
    from huggingface_hub import HfApi, login
    
    # Login
    login(token="your_token")
    
    # Upload model
    model.push_to_hub("my-model")
    
    # Download from hub
    model = AutoModel.from_pretrained("username/my-model")
    
    ✅ Transformers Use Cases:
    - Sentiment analysis
    - Named entity recognition
    - Text generation
    - Question answering
    - Translation
    - Summarization
    - Custom model fine-tuning
    """)


# =============================================================================
# 7. PyTorch - Deep Learning Framework
# =============================================================================

def pytorch_guide():
    """
    PyTorch: Deep learning framework
    
    WHAT: Dynamic deep learning framework
    WHEN: Building neural networks, research
    WHY: Pythonic, flexible, great for research
    """
    print("\n" + "="*80)
    print("7. PyTorch - DEEP LEARNING")
    print("="*80)
    
    print("\n📦 Installation: pip install torch torchvision")
    print("🎯 Use Case: Build/train neural networks")
    
    print("""
    7.1 TENSORS (Like NumPy but GPU)
    
    import torch
    
    # Create tensors
    x = torch.tensor([1, 2, 3])
    y = torch.randn(3, 4)  # Random 3x4
    z = torch.zeros(2, 3)
    
    # Operations
    a = torch.tensor([1.0, 2.0, 3.0])
    b = torch.tensor([4.0, 5.0, 6.0])
    c = a + b
    d = a * b
    
    # GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    x = x.to(device)
    
    7.2 AUTOGRAD (Automatic Differentiation)
    
    x = torch.tensor(2.0, requires_grad=True)
    y = x ** 2
    y.backward()  # Compute gradients
    print(x.grad)  # dy/dx = 2x = 4
    
    7.3 NEURAL NETWORK
    
    import torch.nn as nn
    
    class SimpleNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc1 = nn.Linear(10, 50)
            self.fc2 = nn.Linear(50, 1)
            self.relu = nn.ReLU()
        
        def forward(self, x):
            x = self.relu(self.fc1(x))
            x = self.fc2(x)
            return x
    
    model = SimpleNN()
    
    7.4 TRAINING LOOP
    
    import torch.optim as optim
    
    # Setup
    model = SimpleNN()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training
    for epoch in range(100):
        # Forward
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        
        # Backward
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item():.4f}")
    
    7.5 SAVE/LOAD MODEL
    
    # Save
    torch.save(model.state_dict(), "model.pth")
    
    # Load
    model = SimpleNN()
    model.load_state_dict(torch.load("model.pth"))
    model.eval()
    
    7.6 DATA LOADING
    
    from torch.utils.data import Dataset, DataLoader
    
    class CustomDataset(Dataset):
        def __init__(self, X, y):
            self.X = X
            self.y = y
        
        def __len__(self):
            return len(self.X)
        
        def __getitem__(self, idx):
            return self.X[idx], self.y[idx]
    
    dataset = CustomDataset(X, y)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    for batch_X, batch_y in dataloader:
        # Train on batch
        pass
    
    ✅ PyTorch Use Cases:
    - Custom neural networks
    - Computer vision (with torchvision)
    - NLP models
    - Reinforcement learning
    - Research and prototyping
    """)


# =============================================================================
# 8. TensorFlow/Keras - Deep Learning Framework
# =============================================================================

def tensorflow_guide():
    """
    TensorFlow/Keras: Deep learning framework
    
    WHAT: Production-ready deep learning
    WHEN: Need deployment, TPUs, TensorFlow ecosystem
    WHY: Production-ready, scalable, TensorFlow Lite/JS
    """
    print("\n" + "="*80)
    print("8. TensorFlow/Keras - DEEP LEARNING")
    print("="*80)
    
    print("\n📦 Installation: pip install tensorflow")
    print("🎯 Use Case: Production ML, deployment")
    
    print("""
    8.1 KERAS API (High-level)
    
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    
    # Sequential model
    model = keras.Sequential([
        layers.Dense(64, activation='relu', input_shape=(10,)),
        layers.Dense(32, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])
    
    # Compile
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    # Train
    history = model.fit(
        X_train, y_train,
        epochs=10,
        batch_size=32,
        validation_split=0.2
    )
    
    # Predict
    predictions = model.predict(X_test)
    
    8.2 FUNCTIONAL API (More flexible)
    
    inputs = keras.Input(shape=(10,))
    x = layers.Dense(64, activation='relu')(inputs)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(1, activation='sigmoid')(x)
    
    model = keras.Model(inputs=inputs, outputs=outputs)
    
    8.3 CUSTOM TRAINING
    
    @tf.function
    def train_step(x, y):
        with tf.GradientTape() as tape:
            predictions = model(x, training=True)
            loss = loss_fn(y, predictions)
        
        gradients = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(zip(gradients, model.trainable_variables))
        return loss
    
    8.4 SAVE/LOAD
    
    # Save full model
    model.save('my_model.keras')
    
    # Load
    model = keras.models.load_model('my_model.keras')
    
    # Save weights only
    model.save_weights('weights.h5')
    model.load_weights('weights.h5')
    
    8.5 CALLBACKS
    
    callbacks = [
        keras.callbacks.EarlyStopping(patience=3),
        keras.callbacks.ModelCheckpoint('best_model.keras'),
        keras.callbacks.TensorBoard(log_dir='./logs')
    ]
    
    model.fit(X_train, y_train, callbacks=callbacks)
    
    8.6 DATA PIPELINE
    
    # tf.data for efficient data loading
    dataset = tf.data.Dataset.from_tensor_slices((X, y))
    dataset = dataset.shuffle(1000).batch(32).prefetch(tf.data.AUTOTUNE)
    
    model.fit(dataset, epochs=10)
    
    ✅ TensorFlow Use Cases:
    - Production deployment
    - Mobile (TensorFlow Lite)
    - Web (TensorFlow.js)
    - Large-scale training
    - Serving models (TensorFlow Serving)
    """)


# =============================================================================
# 9. Streamlit - AI Web Apps
# =============================================================================

def streamlit_guide():
    """
    Streamlit: Web app framework
    
    WHAT: Framework for data/ML web apps
    WHEN: Need quick UI for AI models
    WHY: Pure Python, no HTML/CSS/JS needed
    """
    print("\n" + "="*80)
    print("9. Streamlit - AI WEB APPS")
    print("="*80)
    
    print("\n📦 Installation: pip install streamlit")
    print("🎯 Use Case: Build ML/AI demos quickly")
    
    print("""
    9.1 BASIC APP (app.py)
    
    import streamlit as st
    
    st.title("My AI App")
    st.write("Welcome!")
    
    # Run: streamlit run app.py
    
    9.2 INPUT WIDGETS
    
    # Text input
    user_text = st.text_input("Enter text:")
    
    # Slider
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    
    # Selectbox
    model = st.selectbox("Model", ["GPT-4", "GPT-3.5"])
    
    # Button
    if st.button("Generate"):
        st.write("Generating...")
    
    # File uploader
    file = st.file_uploader("Upload CSV")
    
    9.3 DISPLAY
    
    # Text
    st.write("Hello")
    st.markdown("**Bold**")
    st.code("print('hello')")
    
    # Data
    import pandas as pd
    df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    st.dataframe(df)
    st.table(df)
    
    # Charts
    st.line_chart(df)
    st.bar_chart(df)
    
    # JSON
    st.json({"key": "value"})
    
    9.4 LAYOUT
    
    # Columns
    col1, col2 = st.columns(2)
    with col1:
        st.write("Left")
    with col2:
        st.write("Right")
    
    # Sidebar
    with st.sidebar:
        st.write("Settings")
        option = st.selectbox("Choose", [1, 2, 3])
    
    # Tabs
    tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])
    with tab1:
        st.write("Content 1")
    
    9.5 CACHING (Important!)
    
    @st.cache_data
    def load_model():
        # Expensive operation
        return model
    
    @st.cache_resource
    def load_llm():
        # Shared resource
        return ChatOpenAI()
    
    9.6 CHATBOT EXAMPLE
    
    import streamlit as st
    
    st.title("Chatbot")
    
    # Initialize history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("Say something"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get response (mock)
        response = f"Echo: {prompt}"
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    ✅ Streamlit Use Cases:
    - ML model demos
    - Data dashboards
    - Chatbot interfaces
    - Internal tools
    - Prototyping AI apps
    """)


# =============================================================================
# 10. FastAPI - AI APIs
# =============================================================================

def fastapi_guide():
    """
    FastAPI: Modern API framework
    
    WHAT: High-performance API framework
    WHEN: Build production APIs for AI models
    WHY: Fast, auto docs, type hints, async
    """
    print("\n" + "="*80)
    print("10. FastAPI - AI APIs")
    print("="*80)
    
    print("\n📦 Installation: pip install fastapi uvicorn")
    print("🎯 Use Case: Production APIs for ML models")
    
    print("""
    10.1 BASIC API (main.py)
    
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.get("/")
    def read_root():
        return {"message": "Hello World"}
    
    # Run: uvicorn main:app --reload
    # Docs: http://localhost:8000/docs
    
    10.2 PATH & QUERY PARAMETERS
    
    @app.get("/items/{item_id}")
    def read_item(item_id: int, q: str = None):
        return {"item_id": item_id, "q": q}
    
    # /items/5?q=test
    
    10.3 REQUEST BODY
    
    from pydantic import BaseModel
    
    class ChatRequest(BaseModel):
        message: str
        temperature: float = 0.7
    
    @app.post("/chat")
    def chat(request: ChatRequest):
        return {"response": f"You said: {request.message}"}
    
    10.4 AI MODEL ENDPOINT
    
    from transformers import pipeline
    
    # Load once at startup
    classifier = pipeline("sentiment-analysis")
    
    class TextRequest(BaseModel):
        text: str
    
    @app.post("/predict")
    def predict(request: TextRequest):
        result = classifier(request.text)[0]
        return {
            "text": request.text,
            "label": result["label"],
            "score": result["score"]
        }
    
    10.5 ASYNC ENDPOINTS
    
    @app.post("/generate")
    async def generate(prompt: str):
        # Async LLM call
        response = await llm.agenerate([prompt])
        return {"text": response.text}
    
    10.6 MIDDLEWARE & CORS
    
    from fastapi.middleware.cors import CORSMiddleware
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    10.7 BACKGROUND TASKS
    
    from fastapi import BackgroundTasks
    
    def train_model(data):
        # Long-running task
        pass
    
    @app.post("/train")
    def start_training(background_tasks: BackgroundTasks, data: dict):
        background_tasks.add_task(train_model, data)
        return {"status": "Training started"}
    
    10.8 FILE UPLOAD
    
    from fastapi import File, UploadFile
    
    @app.post("/upload")
    async def upload(file: UploadFile = File(...)):
        contents = await file.read()
        return {"filename": file.filename, "size": len(contents)}
    
    10.9 AUTHENTICATION
    
    from fastapi import Depends, HTTPException
    from fastapi.security import HTTPBearer
    
    security = HTTPBearer()
    
    def verify_token(credentials = Depends(security)):
        if credentials.credentials != "secret":
            raise HTTPException(status_code=401)
        return credentials
    
    @app.get("/protected", dependencies=[Depends(verify_token)])
    def protected():
        return {"data": "secret"}
    
    ✅ FastAPI Use Cases:
    - ML model serving
    - Chatbot backends
    - Data processing APIs
    - Microservices
    - Real-time inference
    """)


# =============================================================================
# BONUS: Other Important Libraries
# =============================================================================

def bonus_libraries():
    """Other useful AI libraries"""
    print("\n" + "="*80)
    print("BONUS: OTHER AI LIBRARIES")
    print("="*80)
    
    print("""
    📦 Vector Databases
    
    # ChromaDB
    pip install chromadb
    import chromadb
    client = chromadb.Client()
    collection = client.create_collection("docs")
    collection.add(documents=["text"], ids=["1"])
    
    # FAISS
    pip install faiss-cpu
    import faiss
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)
    
    📦 Web Scraping
    
    # BeautifulSoup
    pip install beautifulsoup4
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Selenium
    pip install selenium
    from selenium import webdriver
    driver = webdriver.Chrome()
    
    📦 Computer Vision
    
    # OpenCV
    pip install opencv-python
    import cv2
    img = cv2.imread('image.jpg')
    
    # Pillow
    pip install pillow
    from PIL import Image
    img = Image.open('image.jpg')
    
    📦 Visualization
    
    # Matplotlib
    pip install matplotlib
    import matplotlib.pyplot as plt
    plt.plot(x, y)
    plt.show()
    
    # Plotly
    pip install plotly
    import plotly.express as px
    fig = px.line(df, x='x', y='y')
    
    📦 API Clients
    
    # Requests
    pip install requests
    import requests
    response = requests.get('https://api.example.com')
    
    # HTTPx (async)
    pip install httpx
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    """)


# =============================================================================
# MAIN GUIDE
# =============================================================================

def main():
    """Run all guides"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                PYTHON AI FRAMEWORKS & LIBRARIES GUIDE                      ║
║                           Part 2 of 2                                      ║
╚═══════════════════════════════════════════════════════════════════════════╝

This guide covers major Python frameworks for AI/ML development.

LIBRARIES COVERED (Part 2):
6. Transformers (Hugging Face) - Pre-trained models
7. PyTorch - Deep learning
8. TensorFlow/Keras - Deep learning
9. Streamlit - AI web apps
10. FastAPI - AI APIs
+ Bonus libraries

Press Enter to continue through each section...
    """)
    
    input("Press Enter to start...")
    
    transformers_guide()
    input("\n\nPress Enter for next section...")
    
    pytorch_guide()
    input("\n\nPress Enter for next section...")
    
    tensorflow_guide()
    input("\n\nPress Enter for next section...")
    
    streamlit_guide()
    input("\n\nPress Enter for next section...")
    
    fastapi_guide()
    input("\n\nPress Enter for bonus libraries...")
    
    bonus_libraries()
    
    print("""
    
╔═══════════════════════════════════════════════════════════════════════════╗
║                        CONGRATULATIONS! 🎉                                 ║
╚═══════════════════════════════════════════════════════════════════════════╝

You've completed the Python AI Frameworks guide!

📚 WHAT YOU'VE LEARNED:
✅ Transformers (Hugging Face) - Using pre-trained models
✅ PyTorch - Building neural networks
✅ TensorFlow/Keras - Production ML
✅ Streamlit - Quick AI demos
✅ FastAPI - Production APIs

🎯 NEXT STEPS:
1. Build a small project with each framework
2. Combine libraries (e.g., FastAPI + Transformers)
3. Deploy to production (Streamlit Cloud, Railway, etc.)
4. Explore advanced features

💡 PROJECT IDEAS:
- Sentiment analysis API (FastAPI + Transformers)
- Chatbot with memory (LangChain + Streamlit)
- Image classifier (PyTorch + FastAPI)
- Document QA system (RAG + Streamlit)

Keep coding and building! 🚀
    """)


if __name__ == "__main__":
    main()
