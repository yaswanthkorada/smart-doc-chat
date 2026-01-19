# PowerShell script to run FastAPI server
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🚀 Starting Smart Document Chat API Server" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

# Activate virtual environment
Write-Host "`n📦 Activating virtual environment..." -ForegroundColor Yellow
& "$PSScriptRoot\venv\Scripts\Activate.ps1"

# Check if activation was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Start FastAPI server
Write-Host "`n🚀 Starting FastAPI server..." -ForegroundColor Yellow
Write-Host "📖 API Docs: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host "🔍 ReDoc: http://localhost:8000/api/redoc" -ForegroundColor Cyan
Write-Host "🤖 Multi-Agent System: ACTIVE`n" -ForegroundColor Green

python run_api.py
