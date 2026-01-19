#!/usr/bin/env python3
"""
FastAPI Server Startup Script
Run this to start the Smart Document Chat API server
"""

import uvicorn
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting Smart Document Chat API Server")
    print("="*60)
    print("📖 API Documentation: http://localhost:8000/api/docs")
    print("🔍 ReDoc: http://localhost:8000/api/redoc")
    print("🤖 Multi-Agent System: ACTIVE")
    print("="*60 + "\n")
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_includes=["api/*", "components/*", "config/*", "utils/*", "app.py"],
        log_level="info",
        access_log=True
    )
