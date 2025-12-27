# Quick Start Script for RAG Assistant

Write-Host "================================" -ForegroundColor Cyan
Write-Host "RAG Assistant - Quick Start" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-Not (Test-Path ".env")) {
    Write-Host "[!] .env file not found!" -ForegroundColor Red
    Write-Host "[*] Copying .env.example to .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "[!] IMPORTANT: Edit .env file and add your OPENAI_API_KEY" -ForegroundColor Red
    Write-Host "    1. Open .env file in notepad" -ForegroundColor Yellow
    Write-Host "    2. Add: OPENAI_API_KEY=your-key-here" -ForegroundColor Yellow
    Write-Host "    3. Save and run this script again" -ForegroundColor Yellow
    Write-Host ""
    notepad .env
    exit
}

# Check if OpenAI API key is set
$envContent = Get-Content ".env" -Raw
if ($envContent -notmatch 'OPENAI_API_KEY=sk-') {
    Write-Host "[!] OpenAI API key not configured!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please add your OpenAI API key to .env file:" -ForegroundColor Yellow
    Write-Host "  OPENAI_API_KEY=sk-your-key-here" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Get your key from: https://platform.openai.com/api-keys" -ForegroundColor Cyan
    Write-Host ""
    notepad .env
    exit
}

Write-Host "[✓] Configuration file found" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "[*] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "[✓] Virtual environment created" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "[*] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "[✓] Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "[*] Installing dependencies..." -ForegroundColor Yellow
Write-Host "    This may take a few minutes on first run..." -ForegroundColor Gray
pip install -q -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "[✓] Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "[!] Error installing dependencies" -ForegroundColor Red
    exit
}
Write-Host ""

# Create necessary directories
Write-Host "[*] Creating data directories..." -ForegroundColor Yellow
$dirs = @("data", "data/user_files", "data/chroma_data", "logs", "temp")
foreach ($dir in $dirs) {
    if (-Not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
}
Write-Host "[✓] Directories created" -ForegroundColor Green
Write-Host ""

# Display configuration summary
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Configuration Summary" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$config = @{}
Get-Content ".env" | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        if ($value -and $key -notmatch '^#') {
            $config[$key] = $value
        }
    }
}

Write-Host "OpenAI API:      " -NoNewline
if ($config['OPENAI_API_KEY'] -match '^sk-') {
    Write-Host "✓ Configured" -ForegroundColor Green
} else {
    Write-Host "✗ Not configured" -ForegroundColor Red
}

Write-Host "Storage:         " -NoNewline
$storage = if ($config['STORAGE_TYPE']) { $config['STORAGE_TYPE'] } else { "local" }
Write-Host "$storage" -ForegroundColor Cyan

Write-Host "Vector DB:       " -NoNewline
$vectordb = if ($config['VECTOR_DB_TYPE']) { $config['VECTOR_DB_TYPE'] } else { "chromadb" }
Write-Host "$vectordb" -ForegroundColor Cyan

Write-Host "Database:        " -NoNewline
if ($config['DATABASE_URL'] -match 'sqlite') {
    Write-Host "SQLite (local)" -ForegroundColor Cyan
} elseif ($config['DATABASE_URL'] -match 'postgresql') {
    Write-Host "PostgreSQL" -ForegroundColor Cyan
} else {
    Write-Host "SQLite (default)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Start application
Write-Host "[*] Starting RAG Assistant..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Application will open in your browser at: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Demo Account:" -ForegroundColor Green
Write-Host "  Username: demo" -ForegroundColor Gray
Write-Host "  Password: Demo@123" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

streamlit run app.py
