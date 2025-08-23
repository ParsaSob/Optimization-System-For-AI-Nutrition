#!/usr/bin/env python3
"""
Simple test for RAG optimization method
"""

import asyncio
from optimization_engine import MealOptimizationEngine
from models import NutritionalTarget, UserPreferences, Ingredient

async def test_rag_method():
    """Test the RAG optimization method directly"""
    try:
        print("Creating engine...")
        engine = MealOptimizationEngine()
        
        print("Creating test data...")
        rag_response = {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "Ground Beef",
                            "amount": 200,
                            "calories": 400,
                            "protein": 40,
                            "carbs": 0,
                            "fat": 30
                        }
                    ]
                }
            ]
        }
        
        target_macros = NutritionalTarget(
            calories=2000,
            protein=150,
            carbohydrates=200,
            fat=65
        )
        
        user_preferences = UserPreferences(
            dietary_restrictions=[],
            allergies=[],
            preferred_cuisines=["persian"],
            calorie_preference="moderate",
            protein_preference="high",
            carb_preference="moderate",
            fat_preference="moderate"
        )
        
        available_ingredients = [
            Ingredient(
                id="1",
                name="Chicken Breast",
                name_fa="سینه مرغ",
                calories_per_100g=165,
                protein_per_100g=31,
                carbs_per_100g=0,
                fat_per_100g=3.6,
                category="protein",
                suitable_meals=[],
                availability=True
            )
        ]
        
        print("Calling RAG optimization method...")
        result = await engine.optimize_rag_meal_plan(
            rag_response=rag_response,
            target_macros=target_macros,
            user_preferences=user_preferences,
            available_ingredients=available_ingredients
        )
        
        print("✅ RAG optimization successful!")
        print(f"Result type: {type(result)}")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
    except Exception as e:
        print(f"❌ RAG optimization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_rag_method())
