#!/usr/bin/env python3
"""
Simple test for optimization engine
"""

import asyncio
from models import Ingredient, NutritionalTarget, UserPreferences, MealTime
from optimization_engine import MealOptimizationEngine

async def test_optimization():
    """Test the optimization engine step by step"""
    
    print("🔧 Testing Optimization Engine Step by Step")
    print("=" * 50)
    
    # Create test ingredients
    ingredients = [
        Ingredient(
            name="Chicken Breast",
            name_fa="سینه مرغ",
            calories_per_100g=165,
            protein_per_100g=31,
            carbs_per_100g=0,
            fat_per_100g=3.6,
            category="protein",
            suitable_meals=[MealTime.BREAKFAST, MealTime.LUNCH, MealTime.DINNER]
        ),
        Ingredient(
            name="Brown Rice",
            name_fa="برنج قهوه‌ای",
            calories_per_100g=111,
            protein_per_100g=2.6,
            carbs_per_100g=23,
            fat_per_100g=0.9,
            category="grain",
            suitable_meals=[MealTime.LUNCH, MealTime.DINNER]
        )
    ]
    
    # Create target macros
    target_macros = NutritionalTarget(
        calories=2000,
        protein=150,
        carbohydrates=200,
        fat=65
    )
    
    # Create user preferences
    user_preferences = UserPreferences(
        dietary_restrictions=[],
        allergies=[],
        preferred_cuisines=["persian"],
        cooking_time_preference="medium"
    )
    
    # Create meal times
    meal_times = [MealTime.BREAKFAST, MealTime.LUNCH, MealTime.DINNER]
    
    print("✅ Test data created successfully")
    print(f"   Ingredients: {len(ingredients)}")
    print(f"   Target calories: {target_macros.calories}")
    print(f"   Meal times: {len(meal_times)}")
    print()
    
    try:
        # Create optimization engine
        print("🔧 Creating optimization engine...")
        engine = MealOptimizationEngine()
        print("✅ Optimization engine created")
        
        # Test filtering
        print("🔧 Testing ingredient filtering...")
        filtered = engine._filter_ingredients(ingredients, user_preferences)
        print(f"✅ Filtered ingredients: {len(filtered)}")
        
        # Test optimization
        print("🔧 Testing optimization...")
        result = await engine.optimize_meal_plan(
            ingredients=ingredients,
            target_macros=target_macros,
            user_preferences=user_preferences,
            meal_periods=meal_times
        )
        
        print("✅ Optimization completed successfully!")
        print(f"   Method used: {result['optimization_result'].optimization_method}")
        print(f"   Target achieved: {result['optimization_result'].target_achieved}")
        print(f"   Computation time: {result['optimization_result'].computation_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_optimization())
