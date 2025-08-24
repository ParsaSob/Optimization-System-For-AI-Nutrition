#!/usr/bin/env python3
"""
Railway startup script for Meal Optimization API
This script ensures proper dependency installation and application startup
"""

import os
import subprocess
import sys

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def start_application():
    """Start the FastAPI application"""
    print("🚀 Starting Meal Optimization API...")
    
    # Get port from Railway environment
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"🌐 Binding to {host}:{port}")
    
    # Start uvicorn
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            workers=1,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Railway Startup Script for Meal Optimization API")
    print("=" * 60)
    
    # Install dependencies first
    install_dependencies()
    
    # Start application
    start_application()
