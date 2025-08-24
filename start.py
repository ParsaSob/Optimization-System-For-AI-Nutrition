#!/usr/bin/env python3
"""
Railway Startup Script
Handles PORT environment variable and starts uvicorn properly
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_port():
    """Get port from environment or use default"""
    port = os.environ.get('PORT')
    if port:
        try:
            return int(port)
        except ValueError:
            logger.warning(f"Invalid PORT value: {port}, using default 8000")
            return 8000
    return 8000

def main():
    """Main startup function"""
    port = get_port()
    host = "0.0.0.0"
    
    logger.info(f"🚀 Starting Meal Optimization API on {host}:{port}")
    logger.info(f"🔧 Environment: PORT={os.environ.get('PORT', 'not_set')}")
    logger.info(f"🌍 Using: host={host}, port={port}")
    
    # Build uvicorn command
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", host,
        "--port", str(port),
        "--workers", "1"
    ]
    
    logger.info(f"🚀 Command: {' '.join(cmd)}")
    
    try:
        # Start uvicorn
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to start uvicorn: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()
