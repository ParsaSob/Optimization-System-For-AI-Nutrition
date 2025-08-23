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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Initialize components
db_manager = DatabaseManager()
optimization_engine = MealOptimizationEngine()

@app.on_event("startup")
async def startup_event():
    """Initialize database and optimization engine on startup"""
    try:
        await db_manager.initialize()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Meal Optimization API is running"}

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
        
    except Exception as e:
        logger.error(f"RAG optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG optimization failed: {str(e)}")

@app.post("/add-ingredients")
async def add_ingredients(ingredients: List[Ingredient]):
    """Add new ingredients to the database"""
    try:
        await db_manager.add_ingredients(ingredients)
        return {"message": f"Added {len(ingredients)} ingredients successfully"}
    except Exception as e:
        logger.error(f"Failed to add ingredients: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add ingredients: {str(e)}")

@app.get("/ingredients")
async def get_ingredients():
    """Get all available ingredients"""
    try:
        ingredients = await db_manager.get_all_ingredients()
        return {"ingredients": ingredients}
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
    import os
    
    # Get port from Railway environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )

