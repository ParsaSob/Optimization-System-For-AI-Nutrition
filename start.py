#!/usr/bin/env python3
"""
Simple startup script for Railway deployment
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Get port from Railway environment or .env file
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Meal Optimization API on {host}:{port}")
    print(f"🔧 Railway PORT: {os.environ.get('PORT', 'not_set')}")
    print(f"🔧 Environment HOST: {host}")
    print(f"🔧 Environment PORT: {port}")
    
    # Start the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        workers=1,
        log_level="info"
    )

