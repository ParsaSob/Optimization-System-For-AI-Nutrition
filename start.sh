#!/bin/bash

# Railway Startup Script
# Handles PORT environment variable and starts uvicorn properly

echo "🚀 Starting Meal Optimization API"
echo "🔧 Environment: PORT=$PORT"

# Set default port if not provided
if [ -z "$PORT" ]; then
    PORT=8000
    echo "⚠️ No PORT set, using default: $PORT"
fi

# Validate PORT is a number
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "❌ Invalid PORT value: $PORT, using default 8000"
    PORT=8000
fi

echo "🌍 Using port: $PORT"

# Start uvicorn with proper port
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
