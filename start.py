#!/usr/bin/env python3
"""
Start script for RAG Meal Optimization System
Automatically detects and runs the appropriate server
"""

import os
import sys

def start_flask_server():
    """Start Flask backend server"""
    print("🚀 Starting Flask Backend Server...")
    from backend_server import app
    
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Flask server starting on port: {port}")
    print(f"🔧 Debug mode: {debug_mode}")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug_mode, threaded=True)
    except Exception as e:
        print(f"❌ Error starting Flask server: {e}")
        sys.exit(1)

def start_fastapi_server():
    """Start FastAPI server"""
    print("🚀 Starting FastAPI Server...")
    import uvicorn
    from main import app
    
    port = int(os.environ.get('PORT', 8000))
    
    print(f"🌐 FastAPI server starting on port: {port}")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"❌ Error starting FastAPI server: {e}")
        sys.exit(1)

def main():
    """Main function to determine which server to start"""
    print("🔍 Detecting server type...")
    
    # Check environment variables
    server_type = os.environ.get('SERVER_TYPE', 'auto')
    
    if server_type == 'flask':
        print("📋 Using Flask server (explicitly set)")
        start_flask_server()
    elif server_type == 'fastapi':
        print("📋 Using FastAPI server (explicitly set)")
        start_fastapi_server()
    else:
        # Auto-detect based on available files
        if os.path.exists('backend_server.py'):
            print("📋 Auto-detected: Flask backend server available")
            start_flask_server()
        elif os.path.exists('main.py'):
            print("📋 Auto-detected: FastAPI main server available")
            start_fastapi_server()
        else:
            print("❌ No server files found!")
            print("Available files:")
            for file in os.listdir('.'):
                if file.endswith('.py'):
                    print(f"  - {file}")
            sys.exit(1)

if __name__ == "__main__":
    main()
