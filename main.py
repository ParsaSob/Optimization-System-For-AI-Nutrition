from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration - using Railway PORT
logger.info(f"🚀 Starting Meal Optimization API")
logger.info(f"🌍 Environment: Railway deployment")
logger.info(f"🔧 Railway PORT env: {os.environ.get('PORT', 'not_set')}")

app = FastAPI(
    title="Meal Optimization API",
    description="Advanced meal optimization system using mathematical optimization",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        logger.info(f"🚀 Starting Meal Optimization API")
        
        # Initialize database
        db_manager = DatabaseManager()
        await db_manager.initialize()
        logger.info("✅ Database initialized successfully")
        
        # Initialize optimization engine
        optimization_engine = MealOptimizationEngine()
        logger.info("✅ Optimization engine ready")
        
        logger.info("🎉 All components initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize components: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Don't crash the app, continue with limited functionality
        logger.warning("⚠️ Continuing with limited functionality")

@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {
        "message": "Meal Optimization API is running",
        "status": "healthy",
        "components_ready": db_manager is not None and optimization_engine is not None,
        "railway_info": {
            "port_env": os.environ.get("PORT", "not_set"),
            "python_version": os.environ.get("PYTHON_VERSION", "not_set"),
            "message": f"Railway deployment - using port {os.environ.get('PORT', 'not_set')}"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "Meal Optimization API is running",
        "database_ready": db_manager is not None,
        "engine_ready": optimization_engine is not None,
        "railway_status": {
            "port_env": os.environ.get("PORT", "not_set"),
            "message": f"Railway deployment - using port {os.environ.get('PORT', 'not_set')}"
        }
    }

@app.post("/optimize-meal", response_model=MealResponse)
async def optimize_meal(request: MealRequest):
    """
    Optimize meal plan based on given ingredients and target macros
    بهینه‌سازی برنامه غذایی بر اساس مواد غذایی داده شده و ماکروهای هدف
    
    Note: Returns one day's worth of meals (multiple meal times), not multiple days
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

class AdvancedRAGRequest(BaseModel):
    """Advanced RAG optimization request with enhanced structure"""
    rag_response: Dict[str, Any] = Field(..., description="RAG response from main site")
    target_macros: Dict[str, float] = Field(..., description="Target macros: calories, protein, carbs, fat")
    user_preferences: Dict[str, Any] = Field(..., description="User preferences and restrictions")
    user_id: str = Field("default_user", description="Unique user identifier")
    meal_type: str = Field("lunch", description="Type of meal to optimize")

class AdvancedRAGResponse(BaseModel):
    """Advanced RAG optimization response"""
    user_id: str
    optimization_result: Dict[str, Any]
    meal: List[Dict[str, Any]]
    nutritional_totals: Dict[str, float]
    target_achievement: Dict[str, Any]
    success: bool = True
    error_message: Optional[str] = None

@app.post("/optimize-rag-meal")
async def optimize_rag_meal(request: RAGRequest):
    """
    بهینه‌سازی برنامه غذایی بر اساس داده‌های RAG که از سایت اصلی دریافت شده
    
    این endpoint:
    1. داده‌های RAG رو از سایت اصلی دریافت می‌کنه
    2. ماکروهای فعلی رو محاسبه می‌کنه
    3. اگر به target نرسیده، ingredient های اضافی اضافه می‌کنه
    4. برنامه غذایی کامل یک روز (6 وعده) تولید می‌کنه
    5. لیست خرید و توصیه‌ها رو برمی‌گردونه
    
    Note: Returns one day's worth of meals (6 meal times), not multiple days
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

@app.post("/optimize-advanced-rag-meal", response_model=AdvancedRAGResponse)
async def optimize_advanced_rag_meal(request: AdvancedRAGRequest):
    """
    بهینه‌سازی پیشرفته برنامه غذایی با استفاده از الگوریتم‌های بهینه‌سازی پیشرفته
    
    این endpoint از سیستم جدید RAG optimization engine استفاده می‌کند که شامل:
    1. انتخاب هوشمند ingredient ها
    2. 5 الگوریتم بهینه‌سازی پیشرفته (Linear, DE, GA, Optuna, Hybrid)
    3. محدودیت‌های واقع‌گرایانه برای مقدار ingredient ها
    4. سیستم fallback برای اطمینان از موفقیت
    
    ورودی:
    - rag_response: پاسخ RAG از سایت اصلی
    - target_macros: ماکروهای هدف (calories, protein, carbs, fat)
    - user_preferences: ترجیحات کاربر
    - meal_type: نوع وعده غذایی
    
    خروجی:
    - برنامه غذایی بهینه شده
    - نتایج بهینه‌سازی
    - دستیابی به اهداف
    """
    try:
        logger.info(f"🚀 Advanced RAG optimization request for user: {request.user_id}")
        logger.info(f"📊 Target macros: {request.target_macros}")
        logger.info(f"🍽️ Meal type: {request.meal_type}")
        
        # Import the advanced RAG optimization engine
        try:
            from rag_optimization_engine import RAGMealOptimizer
            logger.info("✅ Successfully imported advanced RAG optimization engine")
        except ImportError as e:
            logger.error(f"❌ Failed to import advanced RAG optimization engine: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Advanced optimization engine not available"
            )
        
        # Initialize the advanced optimizer
        try:
            advanced_optimizer = RAGMealOptimizer()
            logger.info("✅ Advanced RAG optimizer initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize advanced RAG optimizer: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to initialize advanced optimization engine"
            )
        
        # Run advanced optimization
        try:
            logger.info("🔍 Starting advanced meal optimization...")
            result = advanced_optimizer.optimize_single_meal(
                rag_response=request.rag_response,
                target_macros=request.target_macros,
                user_preferences=request.user_preferences,
                meal_type=request.meal_type
            )
            logger.info("✅ Advanced meal optimization completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Advanced optimization failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, 
                detail=f"Advanced optimization failed: {str(e)}"
            )
        
        # Check if optimization was successful
        if not result.get('optimization_result', {}).get('success', False):
            logger.warning("⚠️ Optimization returned unsuccessful result")
            return AdvancedRAGResponse(
                user_id=request.user_id,
                optimization_result=result.get('optimization_result', {}),
                meal=result.get('meal', []),
                nutritional_totals=result.get('nutritional_totals', {}),
                target_achievement=result.get('target_achievement', {}),
                success=False,
                error_message="Optimization did not complete successfully"
            )
        
        # Prepare response
        response = AdvancedRAGResponse(
            user_id=request.user_id,
            optimization_result=result.get('optimization_result', {}),
            meal=result.get('meal', []),
            nutritional_totals=result.get('nutritional_totals', {}),
            target_achievement=result.get('target_achievement', {}),
            success=True
        )
        
        logger.info(f"🎉 Advanced RAG optimization completed successfully for user: {request.user_id}")
        logger.info(f"📊 Generated meal with {len(response.meal)} ingredients")
        logger.info(f"🏆 Best algorithm: {response.optimization_result.get('method', 'Unknown')}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fatal error in advanced RAG optimization: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Advanced RAG optimization failed: {str(e)}"
        )

@app.post("/test-advanced-rag")
async def test_advanced_rag():
    """Simple test endpoint for advanced RAG"""
    return {"message": "Advanced RAG endpoint working", "status": "success"}

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
    # For local development only
    host = "127.0.0.1"  # Local development
    port = 8000
    
    logger.info(f"🚀 Starting locally on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )

