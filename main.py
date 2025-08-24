from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uvicorn
from optimization_engine import MealOptimizationEngine
from models import (
    MealRequest, MealResponse, Ingredient, NutritionalTarget, 
    UserPreferences, MealTime
)
from database import DatabaseManager
import logging
import asyncio
import os
import traceback

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Railway-specific configuration
PORT = int(os.environ.get("PORT", 8000))
HOST = "0.0.0.0"

app = FastAPI(
    title="Meal Optimization API",
    description="Advanced meal optimization system using mathematical optimization",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure with your main website domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components with error handling
db_manager = None
optimization_engine = None

@app.on_event("startup")
async def startup_event():
    """Initialize database and optimization engine on startup"""
    global db_manager, optimization_engine
    
    try:
        logger.info(f"Starting Meal Optimization API on {HOST}:{PORT}")
        
        # Initialize database
        db_manager = DatabaseManager()
        await db_manager.initialize()
        logger.info("Database initialized successfully")
        
        # Initialize optimization engine
        optimization_engine = MealOptimizationEngine()
        logger.info("Optimization engine ready")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Don't crash the app, continue with limited functionality
        logger.warning("Continuing with limited functionality")

@app.get("/")
async def root():
    """Root endpoint for Railway health check"""
    return {
        "message": "Meal Optimization API is running",
        "status": "healthy",
        "port": PORT,
        "host": HOST,
        "components_ready": db_manager is not None and optimization_engine is not None
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "Meal Optimization API is running",
        "database_ready": db_manager is not None,
        "engine_ready": optimization_engine is not None
    }

@app.post("/optimize-meal", response_model=MealResponse)
async def optimize_meal(request: MealRequest):
    """
    Optimize meal plan based on given ingredients and target macros
    بهینه‌سازی برنامه غذایی بر اساس مواد غذایی داده شده و ماکروهای هدف
    """
    try:
        logger.info(f"Received optimization request for user: {request.user_id}")
        
        # Run optimization
        optimized_meal = await optimization_engine.optimize_meal_plan(
            ingredients=request.ingredients,
            target_macros=request.target_macros,
            user_preferences=request.user_preferences,
            meal_periods=request.meal_times
        )
        
        # Add user_id to response
        optimized_meal['user_id'] = request.user_id
        
        return optimized_meal
        
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.post("/test-rag")
async def test_rag():
    """Simple test endpoint for RAG"""
    return {"message": "RAG endpoint working", "status": "success"}

# RAGRequest model removed for debugging

@app.post("/rag-test")
async def rag_test():
    """Test RAG endpoint"""
    return {"message": "RAG test endpoint working", "status": "success"}

@app.get("/rag-get")
async def rag_get():
    """Test RAG GET endpoint"""
    return {"message": "RAG GET endpoint working", "status": "success"}

@app.post("/rag-post")
async def rag_post():
    """Test RAG POST endpoint"""
    return {"message": "RAG POST endpoint working", "status": "success"}

@app.post("/rag-optimize")
async def rag_optimize():
    """Test RAG optimize endpoint"""
    return {"message": "RAG optimize endpoint working", "status": "success"}

@app.post("/test-rag-connection")
async def test_rag_connection():
    """
    تست اتصال RAG - این endpoint برای تست کردن اتصال سایت اصلی به این API استفاده می‌شه
    
    سایت اصلی باید:
    1. ابتدا به RAG system وصل بشه
    2. داده‌های RAG رو دریافت کنه  
    3. اون داده‌ها رو به این endpoint ارسال کنه
    4. نتیجه بهینه‌سازی رو دریافت کنه
    """
    return {
        "message": "RAG Connection Test Successful",
        "status": "ready",
        "endpoint": "/optimize-rag-meal",
        "method": "POST",
        "description": "این endpoint داده‌های RAG رو از سایت اصلی دریافت کرده و بهینه‌سازی می‌کنه",
        "workflow": [
            "سایت اصلی → RAG System → دریافت داده‌ها",
            "سایت اصلی → این API → ارسال داده‌های RAG",
            "این API → بهینه‌سازی → برنامه غذایی کامل",
            "این API → سایت اصلی → نتیجه نهایی"
        ]
    }

class RAGRequest(BaseModel):
    rag_response: Dict[str, Any]
    target_macros: NutritionalTarget
    user_preferences: UserPreferences
    user_id: str = "default_user"

@app.post("/optimize-rag-meal")
async def optimize_rag_meal(request: RAGRequest):
    """
    بهینه‌سازی برنامه غذایی بر اساس داده‌های RAG که از سایت اصلی دریافت شده
    
    این endpoint:
    1. داده‌های RAG رو از سایت اصلی دریافت می‌کنه
    2. ماکروهای فعلی رو محاسبه می‌کنه
    3. اگر به target نرسیده، ingredient های اضافی اضافه می‌کنه
    4. برنامه غذایی کامل 6 وعده‌ای تولید می‌کنه
    5. لیست خرید و توصیه‌ها رو برمی‌گردونه
    """
    try:
        # Check if components are ready
        if db_manager is None or optimization_engine is None:
            logger.error("Components not initialized")
            raise HTTPException(
                status_code=503, 
                detail="Service temporarily unavailable - components not initialized"
            )
        
        logger.info(f"Received RAG optimization request for user: {request.user_id}")
        logger.info(f"RAG response contains {len(request.rag_response.get('suggestions', []))} meal suggestions")
        
        # Get available ingredients from database
        available_ingredients = await db_manager.get_all_ingredients()
        logger.info(f"Found {len(available_ingredients)} available ingredients in database")
        
        # Run RAG optimization
        optimized_meal = await optimization_engine.optimize_rag_meal_plan(
            rag_response=request.rag_response,
            target_macros=request.target_macros,
            user_preferences=request.user_preferences,
            available_ingredients=available_ingredients
        )
        
        # Add user_id to response
        optimized_meal['user_id'] = request.user_id
        
        logger.info(f"RAG optimization completed successfully for user: {request.user_id}")
        logger.info(f"Generated {len(optimized_meal.get('meal_plans', []))} meal plans")
        
        return optimized_meal
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RAG optimization failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"RAG optimization failed: {str(e)}")

@app.post("/add-ingredients")
async def add_ingredients(ingredients: List[Ingredient]):
    """Add new ingredients to the database"""
    try:
        if db_manager is None:
            raise HTTPException(
                status_code=503, 
                detail="Service temporarily unavailable - database not initialized"
            )
        
        await db_manager.add_ingredients(ingredients)
        return {"message": f"Added {len(ingredients)} ingredients successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add ingredients: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add ingredients: {str(e)}")

@app.get("/ingredients")
async def get_ingredients():
    """Get all available ingredients"""
    try:
        if db_manager is None:
            raise HTTPException(
                status_code=503, 
                detail="Service temporarily unavailable - database not initialized"
            )
        
        ingredients = await db_manager.get_all_ingredients()
        return {"ingredients": ingredients}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get ingredients: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get ingredients: {str(e)}")

@app.get("/meal-times")
async def get_meal_times():
    """Get available meal times"""
    return {
        "meal_times": [
            "breakfast",
            "morning_snack", 
            "lunch",
            "afternoon_snack",
            "evening_snack",
            "dinner"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,  # Disable reload in production
        log_level="info"
    )

