@echo off
REM RAG Meal Optimization System Setup Script for Windows
REM This script sets up the complete RAG optimization system

echo 🚀 Setting up RAG Meal Optimization System...
echo ==============================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python version: %PYTHON_VERSION%

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv rag_venv
call rag_venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Check if ingredients database exists
if not exist "ingredients_database.json" (
    echo ⚠️  Warning: ingredients_database.json not found. Creating sample database...
    (
        echo [
        echo     {
        echo         "name": "Chicken Breast",
        echo         "calories_per_100g": 165,
        echo         "protein_per_100g": 31,
        echo         "carbs_per_100g": 0,
        echo         "fat_per_100g": 3.6,
        echo         "category": "protein"
        echo     },
        echo     {
        echo         "name": "Brown Rice",
        echo         "calories_per_100g": 111,
        echo         "protein_per_100g": 2.6,
        echo         "carbs_per_100g": 23,
        echo         "fat_per_100g": 0.9,
        echo         "category": "grain"
        echo     },
        echo     {
        echo         "name": "Salmon",
        echo         "calories_per_100g": 208,
        echo         "protein_per_100g": 25,
        echo         "carbs_per_100g": 0,
        echo         "fat_per_100g": 12,
        echo         "category": "protein"
        echo     },
        echo     {
        echo         "name": "Quinoa",
        echo         "calories_per_100g": 120,
        echo         "protein_per_100g": 4.4,
        echo         "carbs_per_100g": 22,
        echo         "fat_per_100g": 1.9,
        echo         "category": "grain"
        echo     },
        echo     {
        echo         "name": "Eggs",
        echo         "calories_per_100g": 155,
        echo         "protein_per_100g": 13,
        echo         "carbs_per_100g": 1.1,
        echo         "fat_per_100g": 11,
        echo         "category": "protein"
        echo     },
        echo     {
        echo         "name": "Sweet Potato",
        echo         "calories_per_100g": 86,
        echo         "protein_per_100g": 1.6,
        echo         "carbs_per_100g": 20,
        echo         "fat_per_100g": 0.1,
        echo         "category": "vegetable"
        echo     },
        echo     {
        echo         "name": "Avocado",
        echo         "calories_per_100g": 160,
        echo         "protein_per_100g": 2,
        echo         "carbs_per_100g": 9,
        echo         "fat_per_100g": 15,
        echo         "category": "fat"
        echo     },
        echo     {
        echo         "name": "Almonds",
        echo         "calories_per_100g": 579,
        echo         "protein_per_100g": 21,
        echo         "carbs_per_100g": 22,
        echo         "fat_per_100g": 50,
        echo         "category": "nuts"
        echo     },
        echo     {
        echo         "name": "Greek Yogurt",
        echo         "calories_per_100g": 59,
        echo         "protein_per_100g": 10,
        echo         "carbs_per_100g": 3.6,
        echo         "fat_per_100g": 0.4,
        echo         "category": "dairy"
        echo     },
        echo     {
        echo         "name": "Olive Oil",
        echo         "calories_per_100g": 884,
        echo         "protein_per_100g": 0,
        echo         "carbs_per_100g": 0,
        echo         "fat_per_100g": 100,
        echo         "category": "fat"
        echo     }
        echo ]
    ) > ingredients_database.json
    echo ✅ Sample ingredients database created.
)

REM Create data directory
if not exist "data" mkdir data

REM Test the system
echo 🧪 Testing the system...
python -c "from rag_optimization_engine import RAGMealOptimizer; print('✅ RAG optimization engine imported successfully')"

if errorlevel 1 (
    echo ❌ System test failed. Please check the error messages above.
    pause
    exit /b 1
) else (
    echo ✅ System test passed!
)

REM Create startup script
echo @echo off > start_rag_system.bat
echo REM Startup script for RAG Meal Optimization System >> start_rag_system.bat
echo. >> start_rag_system.bat
echo echo 🚀 Starting RAG Meal Optimization System... >> start_rag_system.bat
echo echo ========================================== >> start_rag_system.bat
echo. >> start_rag_system.bat
echo REM Activate virtual environment >> start_rag_system.bat
echo call rag_venv\Scripts\activate.bat >> start_rag_system.bat
echo. >> start_rag_system.bat
echo REM Start the backend server >> start_rag_system.bat
echo echo 📍 Starting backend server on port 5000... >> start_rag_system.bat
echo python backend_server.py >> start_rag_system.bat
echo pause >> start_rag_system.bat

REM Create test script
echo @echo off > test_rag_system.bat
echo REM Test script for RAG Meal Optimization System >> test_rag_system.bat
echo. >> test_rag_system.bat
echo echo 🧪 Testing RAG Meal Optimization System... >> test_rag_system.bat
echo echo ========================================= >> test_rag_system.bat
echo. >> test_rag_system.bat
echo REM Activate virtual environment >> test_rag_system.bat
echo call rag_venv\Scripts\activate.bat >> test_rag_system.bat
echo. >> test_rag_system.bat
echo REM Run tests >> test_rag_system.bat
echo python test_rag_optimization.py >> test_rag_system.bat
echo pause >> test_rag_system.bat

echo.
echo 🎉 Setup completed successfully!
echo ================================
echo.
echo 📋 Available commands:
echo    start_rag_system.bat    - Start the RAG optimization system
echo    test_rag_system.bat     - Test the system
echo    rag_venv\Scripts\activate.bat - Activate virtual environment
echo.
echo 🌐 The system will be available at: http://localhost:5000
echo.
echo 📚 Documentation: RAG_OPTIMIZATION_README.md
echo 🐳 Docker support: docker-compose.rag.yml
echo.
echo 🚀 To start the system, run: start_rag_system.bat
echo.
pause
