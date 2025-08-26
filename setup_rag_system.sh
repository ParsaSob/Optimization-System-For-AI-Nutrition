#!/bin/bash

# RAG Meal Optimization System Setup Script
# This script sets up the complete RAG optimization system

echo "🚀 Setting up RAG Meal Optimization System..."
echo "=============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv rag_venv
source rag_venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if ingredients database exists
if [ ! -f "ingredients_database.json" ]; then
    echo "⚠️  Warning: ingredients_database.json not found. Creating sample database..."
    cat > ingredients_database.json << 'EOF'
[
    {
        "name": "Chicken Breast",
        "calories_per_100g": 165,
        "protein_per_100g": 31,
        "carbs_per_100g": 0,
        "fat_per_100g": 3.6,
        "category": "protein"
    },
    {
        "name": "Brown Rice",
        "calories_per_100g": 111,
        "protein_per_100g": 2.6,
        "carbs_per_100g": 23,
        "fat_per_100g": 0.9,
        "category": "grain"
    },
    {
        "name": "Salmon",
        "calories_per_100g": 208,
        "protein_per_100g": 25,
        "carbs_per_100g": 0,
        "fat_per_100g": 12,
        "category": "protein"
    },
    {
        "name": "Quinoa",
        "calories_per_100g": 120,
        "protein_per_100g": 4.4,
        "carbs_per_100g": 22,
        "fat_per_100g": 1.9,
        "category": "grain"
    },
    {
        "name": "Eggs",
        "calories_per_100g": 155,
        "protein_per_100g": 13,
        "carbs_per_100g": 1.1,
        "fat_per_100g": 11,
        "category": "protein"
    },
    {
        "name": "Sweet Potato",
        "calories_per_100g": 86,
        "protein_per_100g": 1.6,
        "carbs_per_100g": 20,
        "fat_per_100g": 0.1,
        "category": "vegetable"
    },
    {
        "name": "Avocado",
        "calories_per_100g": 160,
        "protein_per_100g": 2,
        "carbs_per_100g": 9,
        "fat_per_100g": 15,
        "category": "fat"
    },
    {
        "name": "Almonds",
        "calories_per_100g": 579,
        "protein_per_100g": 21,
        "carbs_per_100g": 22,
        "fat_per_100g": 50,
        "category": "nuts"
    },
    {
        "name": "Greek Yogurt",
        "calories_per_100g": 59,
        "protein_per_100g": 10,
        "carbs_per_100g": 3.6,
        "fat_per_100g": 0.4,
        "category": "dairy"
    },
    {
        "name": "Olive Oil",
        "calories_per_100g": 884,
        "protein_per_100g": 0,
        "carbs_per_100g": 0,
        "fat_per_100g": 100,
        "category": "fat"
    }
]
EOF
    echo "✅ Sample ingredients database created."
fi

# Create data directory
mkdir -p data

# Test the system
echo "🧪 Testing the system..."
python3 -c "
from rag_optimization_engine import RAGMealOptimizer
print('✅ RAG optimization engine imported successfully')
"

if [ $? -eq 0 ]; then
    echo "✅ System test passed!"
else
    echo "❌ System test failed. Please check the error messages above."
    exit 1
fi

# Create startup script
cat > start_rag_system.sh << 'EOF'
#!/bin/bash
# Startup script for RAG Meal Optimization System

echo "🚀 Starting RAG Meal Optimization System..."
echo "=========================================="

# Activate virtual environment
source rag_venv/bin/activate

# Start the backend server
echo "📍 Starting backend server on port 5000..."
python3 backend_server.py
EOF

chmod +x start_rag_system.sh

# Create test script
cat > test_rag_system.sh << 'EOF'
#!/bin/bash
# Test script for RAG Meal Optimization System

echo "🧪 Testing RAG Meal Optimization System..."
echo "========================================="

# Activate virtual environment
source rag_venv/bin/activate

# Run tests
python3 test_rag_optimization.py
EOF

chmod +x test_rag_system.sh

echo ""
echo "🎉 Setup completed successfully!"
echo "================================"
echo ""
echo "📋 Available commands:"
echo "   ./start_rag_system.sh    - Start the RAG optimization system"
echo "   ./test_rag_system.sh     - Test the system"
echo "   source rag_venv/bin/activate - Activate virtual environment"
echo ""
echo "🌐 The system will be available at: http://localhost:5000"
echo ""
echo "📚 Documentation: RAG_OPTIMIZATION_README.md"
echo "🐳 Docker support: docker-compose.rag.yml"
echo ""
echo "🚀 To start the system, run: ./start_rag_system.sh"
