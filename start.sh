#!/bin/bash

# Quick Start Script for RAG Assistant (Linux/Mac)

echo "================================"
echo "RAG Assistant - Quick Start"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "[!] .env file not found!"
    echo "[*] Copying .env.example to .env..."
    cp .env.example .env
    echo ""
    echo "[!] IMPORTANT: Edit .env file and add your OPENAI_API_KEY"
    echo "    1. Open .env file: nano .env"
    echo "    2. Add: OPENAI_API_KEY=your-key-here"
    echo "    3. Save (Ctrl+X, Y, Enter) and run this script again"
    echo ""
    exit 1
fi

# Check if OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "[!] OpenAI API key not configured!"
    echo ""
    echo "Please add your OpenAI API key to .env file:"
    echo "  OPENAI_API_KEY=sk-your-key-here"
    echo ""
    echo "Get your key from: https://platform.openai.com/api-keys"
    echo ""
    exit 1
fi

echo "[✓] Configuration file found"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
    echo "[✓] Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "[*] Activating virtual environment..."
source venv/bin/activate
echo "[✓] Virtual environment activated"
echo ""

# Install dependencies
echo "[*] Installing dependencies..."
echo "    This may take a few minutes on first run..."
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "[✓] Dependencies installed"
else
    echo "[!] Error installing dependencies"
    exit 1
fi
echo ""

# Create necessary directories
echo "[*] Creating data directories..."
mkdir -p data/user_files data/chroma_data logs temp
echo "[✓] Directories created"
echo ""

# Display configuration summary
echo "================================"
echo "Configuration Summary"
echo "================================"

source .env

echo -n "OpenAI API:      "
if [[ $OPENAI_API_KEY == sk-* ]]; then
    echo "✓ Configured"
else
    echo "✗ Not configured"
fi

echo -n "Storage:         "
echo "${STORAGE_TYPE:-local}"

echo -n "Vector DB:       "
echo "${VECTOR_DB_TYPE:-chromadb}"

echo -n "Database:        "
if [[ $DATABASE_URL == *"sqlite"* ]]; then
    echo "SQLite (local)"
elif [[ $DATABASE_URL == *"postgresql"* ]]; then
    echo "PostgreSQL"
else
    echo "SQLite (default)"
fi

echo ""
echo "================================"
echo ""

# Start application
echo "[*] Starting RAG Assistant..."
echo ""
echo "Application will open in your browser at: http://localhost:8501"
echo ""
echo "Demo Account:"
echo "  Username: demo"
echo "  Password: Demo@123"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""
echo "================================"
echo ""

streamlit run app.py
