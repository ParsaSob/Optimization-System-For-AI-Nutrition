#!/usr/bin/env python3
"""
Startup script for Meal Optimization API
"""

import uvicorn
import logging
from config import Config

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Meal Optimization API...")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=Config.API_RELOAD,
        log_level=Config.LOG_LEVEL.lower()
    )

