#!/usr/bin/env python3
"""
Test script for the new advanced algorithm with the exact data from the user's website
Tests the multi-step optimization with 5 methods and smart helper ingredients
"""

import requests
import json
import time

def test_advanced_algorithm():
    """Test the advanced algorithm with real website data"""
    
    # Test with the exact data from the user's website
    test_data = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "Ground Beef",
                            "protein_per_100g": 26.0,
                            "carbs_per_100g": 0,
                            "fat_per_100g": 15.0,
                            "calories_per_100g": 250,
                            "max_quantity": 300,
                            "category": "protein"
                        },
                        {
                            "name": "Onion",
                            "protein_per_100g": 1.1,
                            "carbs_per_100g": 9.0,
                            "fat_per_100g": 0.1,
                            "calories_per_100g": 40,
                            "max_quantity": 300,
                            "category": "vegetable"
                        },
                        {
                            "name": "Pita Bread",
                            "protein_per_100g": 13.0,
                            "carbs_per_100g": 41.0,
                            "fat_per_100g": 4.2,
                            "calories_per_100g": 247,
                            "max_quantity": 300,
                            "category": "grain"
                        },
                        {
                            "name": "Grilled Tomato",
                            "protein_per_100g": 1.0,
                            "carbs_per_100g": 5.0,
                            "fat_per_100g": 0,
                            "calories_per_100g": 25,
                            "max_quantity": 300,
                            "category": "vegetable"
                        },
                        {
                            "name": "Grilled Pepper",
                            "protein_per_100g": 1.0,
                            "carbs_per_100g": 5.0,
                            "fat_per_100g": 0,
                            "calories_per_100g": 25,
                            "max_quantity": 300,
                            "category": "vegetable"
                        }
                    ]
                }
            ]
        },
        "target_macros": {
            "calories": 637.2,
            "protein": 45.4,
            "carbs": 88.5,
            "fat": 13.7
        },
        "user_preferences": "گوشت مجاز است",
        "meal_type": "lunch"
    }
    
    print("🧠 Testing Advanced Algorithm with Real Website Data...")
    print("=" * 80)
    print(f"🎯 Target Macros:")
    print(f"  • Calories: {test_data['target_macros']['calories']} kcal")
    print(f"  • Protein: {test_data['target_macros']['protein']} g")
    print(f"  • Carbs: {test_data['target_macros']['carbs']} g")
    print(f"  • Fat: {test_data['target_macros']['fat']} g")
    print(f"🍽️ Meal Type: {test_data['meal_type']}")
    print(f"🔧 User Preferences: {test_data['user_preferences']}")
    print("=" * 80)
    
    try:
        # Send request to the advanced optimization endpoint
        print(f"🌐 Testing advanced optimization endpoint...")
        
        response = requests.post(
            "http://localhost:5000/optimize-single-meal-rag-advanced",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Advanced optimization completed.")
            
            # Print optimization result
            optimization_result = result.get('optimization_result', {})
            print(f"\n📊 Optimization Result:")
            print(f"  • Method: {optimization_result.get('method', 'Unknown')}")
            print(f"  • Success: {optimization_result.get('success', False)}")
            print(f"  • Computation Time: {optimization_result.get('computation_time', 0)}s")
            
            # Print helper ingredients added
            helper_ingredients = result.get('helper_ingredients_added', [])
            if helper_ingredients:
                print(f"\n🔧 Helper Ingredients Added:")
                for helper in helper_ingredients:
                    print(f"  • {helper['name']}: {helper['protein_per_100g']}g protein, {helper['carbs_per_100g']}g carbs, {helper['fat_per_100g']}g fat")
            else:
                print(f"\n🔧 No helper ingredients were added")
            
            # Print optimization steps
            optimization_steps = result.get('optimization_steps', {})
            if optimization_steps:
                print(f"\n🔄 Optimization Steps:")
                for step, description in optimization_steps.items():
                    print(f"  • {step}: {description}")
            
            # Print final meal
            meal = result.get('meal', [])
            if meal:
                print(f"\n🍽️ Final Meal:")
                total_calories = 0
                total_protein = 0
                total_carbs = 0
                total_fat = 0
                
                for ingredient in meal:
                    qty = ingredient.get('quantity_needed', 0)
                    calories = ingredient.get('calories_per_100g', 0) * qty / 100
                    protein = ingredient.get('protein_per_100g', 0) * qty / 100
                    carbs = ingredient.get('carbs_per_100g', 0) * qty / 100
                    fat = ingredient.get('fat_per_100g', 0) * qty / 100
                    
                    total_calories += calories
                    total_protein += protein
                    total_carbs += carbs
                    total_fat += fat
                    
                    print(f"  • {ingredient['name']}: {qty:.1f}g - {calories:.1f} cal, {protein:.1f}g protein, {carbs:.1f}g carbs, {fat:.1f}g fat")
                
                print(f"\n📊 Calculated Totals:")
                print(f"  • Calories: {total_calories:.1f} kcal")
                print(f"  • Protein: {total_protein:.1f} g")
                print(f"  • Carbs: {total_carbs:.1f} g")
                print(f"  • Fat: {total_fat:.1f} g")
                
                # Check target achievement
                target_achievement = result.get('target_achievement', {})
                if target_achievement:
                    print(f"\n🎯 Target Achievement:")
                    for macro, achieved in target_achievement.items():
                        if macro != 'overall':
                            status = "✅ Met" if achieved else "❌ Not Met"
                            print(f"  • {macro.title()}: {status}")
                    
                    overall = target_achievement.get('overall', False)
                    print(f"  • Overall: {'✅ All Targets Met' if overall else '❌ Some Targets Not Met'}")
            
            # Print nutritional totals from result
            nutritional_totals = result.get('nutritional_totals', {})
            if nutritional_totals:
                print(f"\n📊 Nutritional Totals from Result:")
                print(f"  • Calories: {nutritional_totals.get('calories', 0):.1f} kcal")
                print(f"  • Protein: {nutritional_totals.get('protein', 0):.1f} g")
                print(f"  • Carbs: {nutritional_totals.get('carbs', 0):.1f} g")
                print(f"  • Fat: {nutritional_totals.get('fat', 0):.1f} g")
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    print("\n" + "=" * 80)
    print("🏁 Test completed!")

if __name__ == "__main__":
    print("🧠 Advanced Algorithm Test Script")
    print("=" * 80)
    
    # Wait a bit for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    # Run the test
    test_advanced_algorithm()
    
    print("\n" + "=" * 80)
    print("�� Test completed!")
