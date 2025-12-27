# Quick test to verify Gemini API works on corporate network
Write-Host "Testing Gemini API connection..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Check .env file
Write-Host "✓ Checking .env configuration..." -ForegroundColor Yellow
$envContent = Get-Content .env -Raw
if ($envContent -match 'EMBEDDING_PROVIDER="gemini"') {
    Write-Host "  ✅ EMBEDDING_PROVIDER is set to gemini" -ForegroundColor Green
} else {
    Write-Host "  ❌ EMBEDDING_PROVIDER not set to gemini" -ForegroundColor Red
    Write-Host "  Please update .env: EMBEDDING_PROVIDER=`"gemini`"" -ForegroundColor Yellow
}

if ($envContent -match 'GEMINI_API_KEY="AIza') {
    Write-Host "  ✅ GEMINI_API_KEY is configured" -ForegroundColor Green
} else {
    Write-Host "  ❌ GEMINI_API_KEY not found" -ForegroundColor Red
}

Write-Host ""

# Test 2: Test Gemini API directly
Write-Host "✓ Testing Gemini API connection..." -ForegroundColor Yellow
python -c @"
import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content('Say hello')
    print('  ✅ Gemini API works! Response:', response.text[:50])
    print('  ✅ Your app will work on office laptop!')
except Exception as e:
    print('  ❌ Gemini API error:', str(e)[:100])
    print('  ℹ️  Check your API key or network connection')
"@

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "If you see ✅ marks above, run:" -ForegroundColor Green
Write-Host "  streamlit run app.py" -ForegroundColor White
Write-Host "================================" -ForegroundColor Cyan
