#!/usr/bin/env python3
"""
Test script to verify that meal optimization returns single day meal plans
"""

import asyncio
import json
from optimization_engine import MealOptimizationEngine
from models import NutritionalTarget, UserPreferences, MealTime, Ingredient

async def test_single_day_meal():
    """Test that meal optimization returns single day meal plans"""
    
    # Initialize the optimization engine
    engine = MealOptimizationEngine()
    
    # Create sample target macros
    target_macros = NutritionalTarget(
        calories=2000,
        protein=150,
        carbohydrates=200,
        fat=65
    )
    
    # Create sample user preferences
    user_preferences = UserPreferences(
        dietary_restrictions=[],
        allergies=[],
        preferred_cuisines=["persian"],
        cooking_time_preference="medium"
    )
    
    # Create sample RAG response (simulating the Persian lunch scenario)
    rag_response = {
        "suggestions": [
            {
                "name": "Persian Lunch Fesenjan",
                "calories": 1445.0,
                "protein": 64.0,
                "carbs": 148.0,
                "fat": 62.0,
                "ingredients": [
                    {
                        "name": "Chicken",
                        "amount": 300,
                        "calories": 495,
                        "protein": 93,
                        "carbs": 0,
                        "fat": 10.8
                    },
                    {
                        "name": "Walnuts",
                        "amount": 50,
                        "calories": 330,
                        "protein": 8,
                        "carbs": 8,
                        "fat": 30
                    },
                    {
                        "name": "Pomegranate Molasses",
                        "amount": 30,
                        "calories": 60,
                        "protein": 0,
                        "carbs": 15,
                        "fat": 0
                    },
                    {
                        "name": "Onion",
                        "amount": 50,
                        "calories": 20,
                        "protein": 1,
                        "carbs": 5,
                        "fat": 0
                    },
                    {
                        "name": "Basmati Rice",
                        "amount": 150,
                        "calories": 540,
                        "protein": 10,
                        "carbs": 120,
                        "fat": 2
                    }
                ]
            }
        ]
    }
    
    # Create sample available ingredients from database
    available_ingredients = [
        Ingredient(
            id="chicken_breast",
            name="Chicken Breast",
            name_fa="سینه مرغ",
            calories_per_100g=165,
            protein_per_100g=31,
            carbs_per_100g=0,
            fat_per_100g=3.6,
            category="protein",
            suitable_meals=[MealTime.BREAKFAST, MealTime.LUNCH, MealTime.DINNER],
            price_per_kg=15.0,
            availability=True
        )
    ]
    
    try:
        # Test the RAG meal optimization
        result = await engine.optimize_rag_meal_plan(
            rag_response=rag_response,
            target_macros=target_macros,
            user_preferences=user_preferences,
            available_ingredients=available_ingredients
        )
        
        print("✅ Meal optimization completed successfully!")
        print(f"Plan type: {result.get('plan_type', 'Not specified')}")
        print(f"Total meals: {result.get('total_meals', 'Not specified')}")
        print(f"Number of meal plans: {len(result['meal_plans'])}")
        
        print("\n📋 Meal Plans (Single Day):")
        for i, meal_plan in enumerate(result['meal_plans']):
            print(f"  {i+1}. {meal_plan.meal_time.value}: {meal_plan.total_calories:.1f} kcal")
            if meal_plan.items:
                for item in meal_plan.items:
                    print(f"     - {item.ingredient.name}: {item.quantity_grams:.1f}g")
        
        print(f"\n📊 Daily Totals:")
        print(f"  Calories: {result['daily_totals'].calories:.1f}")
        print(f"  Protein: {result['daily_totals'].protein:.1f}g")
        print(f"  Carbs: {result['daily_totals'].carbohydrates:.1f}g")
        print(f"  Fat: {result['daily_totals'].fat:.1f}g")
        
        print(f"\n💰 Cost Estimate: ${result.get('cost_estimate', 0):.2f}")
        
        # Verify this is a single day plan
        if result.get('plan_type') == 'single_day' and result.get('total_meals') == 6:
            print("\n✅ SUCCESS: This is correctly a single day meal plan with 6 meal times!")
        else:
            print("\n❌ WARNING: Plan type or meal count not as expected!")
            
    except Exception as e:
        print(f"❌ Error during meal optimization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_single_day_meal())
