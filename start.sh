#!/bin/bash

# Set Python version
export PYTHON_VERSION=3.11.9

# Install dependencies
pip install -r requirements.txt

# Start the application
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --log-level info
