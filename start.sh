#!/bin/bash
# Start script for RAG Meal Optimization System on Render

echo "🚀 Starting RAG Meal Optimization System..."
echo "🔧 Environment: $FLASK_ENV"
echo "🌐 Port: $PORT"
echo "📁 Working directory: $(pwd)"
echo "📋 Available files:"
ls -la

echo ""
echo "🔍 Checking Python version..."
python --version

echo ""
echo "🔍 Checking dependencies..."
pip list | grep -E "(flask|fastapi|uvicorn)"

echo ""
echo "🚀 Starting Flask server..."
python start.py
