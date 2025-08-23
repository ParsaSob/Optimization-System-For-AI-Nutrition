#!/usr/bin/env python3
"""
Test script for RAG-based meal optimization
"""

import asyncio
import json
import httpx
from models import NutritionalTarget, UserPreferences

# Sample RAG response
SAMPLE_RAG_RESPONSE = {
    "suggestions": [
        {
            "mealTitle": "Persian Lunch Kabab Koobideh",
            "description": "High in protein and calories, suitable for muscle gain goals for a moderately active individual. Includes a balance of meat for protein and rice for energy, with vegetables for micronutrients.",
            "ingredients": [
                {
                    "name": "Ground Beef",
                    "amount": 200,
                    "unit": "g",
                    "calories": 400,
                    "protein": 40,
                    "carbs": 0,
                    "fat": 30,
                    "macrosString": "400 cal, 40g protein, 0g carbs, 30g fat"
                },
                {
                    "name": "Onion",
                    "amount": 50,
                    "unit": "g",
                    "calories": 20,
                    "protein": 1,
                    "carbs": 5,
                    "fat": 0,
                    "macrosString": "20 cal, 1g protein, 5g carbs, 0g fat"
                },
                {
                    "name": "Saffron",
                    "amount": 2,
                    "unit": "g",
                    "calories": 1,
                    "protein": 0,
                    "carbs": 0,
                    "fat": 0,
                    "macrosString": "1 cal, 0g protein, 0g carbs, 0g fat"
                },
                {
                    "name": "Butter",
                    "amount": 25,
                    "unit": "g",
                    "calories": 180,
                    "protein": 0,
                    "carbs": 0,
                    "fat": 20,
                    "macrosString": "180 cal, 0g protein, 0g carbs, 20g fat"
                },
                {
                    "name": "Basmati Rice",
                    "amount": 200,
                    "unit": "g",
                    "calories": 720,
                    "protein": 13.3,
                    "carbs": 160,
                    "fat": 2.7,
                    "macrosString": "720 cal, 13.3g protein, 160g carbs, 2.7g fat"
                },
                {
                    "name": "Grilled Tomato",
                    "amount": 50,
                    "unit": "g",
                    "calories": 10,
                    "protein": 0.5,
                    "carbs": 2.5,
                    "fat": 0,
                    "macrosString": "10 cal, 0.5g protein, 2.5g carbs, 0g fat"
                }
            ],
            "totalCalories": 1331,
            "totalProtein": 54.8,
            "totalCarbs": 167.5,
            "totalFat": 52.7,
            "nutritionalNotes": "High protein content supports muscle synthesis, with sufficient carbs for energy during workouts. Fat content aids in hormone regulation crucial for muscle growth.",
            "instructions": "Cook ingredients according to preference. Season to taste and serve."
        }
    ],
    "success": True,
    "message": None
}

# Target macros (higher than RAG provides)
TARGET_MACROS = NutritionalTarget(
    calories=2000,
    protein=150,
    carbohydrates=200,
    fat=65
)

# User preferences
USER_PREFERENCES = UserPreferences(
    dietary_restrictions=[],
    allergies=[],
    preferred_cuisines=["persian", "mediterranean"],
    calorie_preference="moderate",
    protein_preference="high",
    carb_preference="moderate",
    fat_preference="moderate"
)

async def test_rag_optimization():
    """Test the RAG optimization endpoint"""
    print("🚀 Testing RAG-based Meal Optimization")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test RAG optimization endpoint
            print("📝 Testing RAG meal optimization...")
            
            response = await client.post(
                "http://localhost:8000/optimize-rag-meal",
                json={
                    "rag_response": SAMPLE_RAG_RESPONSE,
                    "target_macros": TARGET_MACROS.model_dump(),
                    "user_preferences": USER_PREFERENCES.model_dump(),
                    "user_id": "test_user_rag"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ RAG optimization successful!")
                
                # Display results
                optimization_result = result['optimization_result']
                print(f"Optimization method: {optimization_result['optimization_method']}")
                print(f"Target achieved: {optimization_result['target_achieved']}")
                
                # Show meal plans
                meal_plans = result['meal_plans']
                print(f"\n📋 Generated {len(meal_plans)} meal plans:")
                
                for meal_plan in meal_plans:
                    meal_time = meal_plan['meal_time']
                    total_calories = meal_plan['total_calories']
                    total_protein = meal_plan['total_protein']
                    total_carbs = meal_plan['total_carbs']
                    total_fat = meal_plan['total_fat']
                    
                    print(f"\n🍽️ {meal_time.title()}:")
                    print(f"   Calories: {total_calories:.1f}")
                    print(f"   Protein: {total_protein:.1f}g")
                    print(f"   Carbs: {total_carbs:.1f}g")
                    print(f"   Fat: {total_fat:.1f}g")
                    
                    if meal_plan['items']:
                        print("   Ingredients:")
                        for item in meal_plan['items']:
                            ingredient_name = item['ingredient']['name']
                            quantity = item['quantity_grams']
                            print(f"     • {ingredient_name}: {quantity:.1f}g")
                
                # Show daily totals
                daily_totals = result['daily_totals']
                print(f"\n📊 Daily Totals:")
                print(f"   Calories: {daily_totals['calories']:.1f} / {TARGET_MACROS.calories}")
                print(f"   Protein: {daily_totals['protein']:.1f}g / {TARGET_MACROS.protein}g")
                print(f"   Carbs: {daily_totals['carbohydrates']:.1f}g / {TARGET_MACROS.carbohydrates}g")
                print(f"   Fat: {daily_totals['fat']:.1f}g / {TARGET_MACROS.fat}g")
                
                # Show RAG enhancement info
                if 'rag_enhancement' in result:
                    enhancement = result['rag_enhancement']
                    print(f"\n🔧 RAG Enhancement:")
                    print(f"   Original macros: {enhancement['original_macros']}")
                    print(f"   Added ingredients: {len(enhancement['added_ingredients'])}")
                    print(f"   Notes: {enhancement['enhancement_notes']}")
                
                # Show recommendations
                recommendations = result['recommendations']
                print(f"\n💡 Recommendations:")
                for rec in recommendations:
                    print(f"   • {rec}")
                
                # Show shopping list
                shopping_list = result['shopping_list']
                print(f"\n🛒 Shopping List:")
                for item in shopping_list:
                    print(f"   • {item['name']}: {item['quantity']:.1f} {item['unit']}")
                
            else:
                print(f"❌ RAG optimization failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    print("Starting RAG optimization test...")
    asyncio.run(test_rag_optimization())
