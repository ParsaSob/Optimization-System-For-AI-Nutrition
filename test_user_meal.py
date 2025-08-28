#!/usr/bin/env python3
"""
Test the aggressive optimization with user's specific meal data.
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_user_meal():
    """Test the aggressive optimization with user's meal data."""
    
    # Initialize the engine
    engine = RAGMealOptimizer()
    
    # User's meal data
    user_meal_data = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "Ground Beef",
                            "protein_per_100g": 26.1,
                            "carbs_per_100g": 0,
                            "fat_per_100g": 15.4,
                            "calories_per_100g": 250,
                            "quantity_needed": 100
                        },
                        {
                            "name": "Basmati Rice",
                            "protein_per_100g": 7.1,
                            "carbs_per_100g": 78.0,
                            "fat_per_100g": 0.7,
                            "calories_per_100g": 345,
                            "quantity_needed": 100
                        }
                    ]
                }
            ],
            "success": True,
            "message": "Converted from AI suggestions"
        },
        "target_macros": {
            "calories": 600,
            "protein": 45,
            "carbs": 80,
            "fat": 15
        },
        "user_preferences": {
            "diet_type": "high_protein",
            "allergies": [],
            "preferences": ["low_sodium", "organic"]
        },
        "user_id": "user_123",
        "meal_type": "Lunch"
    }
    
    print("🧪 Testing User's Meal Optimization")
    print("=" * 50)
    
    # Extract ingredients from the suggestions format
    ingredients = user_meal_data["rag_response"]["suggestions"][0]["ingredients"]
    
    # Add max_quantity to ingredients (required by the optimizer)
    for ing in ingredients:
        ing['max_quantity'] = 500  # Reasonable max for testing
    
    print(f"🍽️ Original Ingredients:")
    for ing in ingredients:
        print(f"  - {ing['name']}: {ing['quantity_needed']}g")
        print(f"    Protein: {ing['protein_per_100g']}g/100g, Carbs: {ing['carbs_per_100g']}g/100g, Fat: {ing['fat_per_100g']}g/100g")
    
    print(f"\n🎯 Target Macros:")
    print(f"  - Calories: {user_meal_data['target_macros']['calories']}")
    print(f"  - Protein: {user_meal_data['target_macros']['protein']}g")
    print(f"  - Carbs: {user_meal_data['target_macros']['carbs']}g")
    print(f"  - Fat: {user_meal_data['target_macros']['fat']}g")
    
    # Calculate current nutrition
    current_nutrition = engine._calculate_final_meal(ingredients, [ing.get('quantity_needed', 0) for ing in ingredients])
    print(f"\n📊 Current Nutrition (before optimization):")
    print(f"  - Calories: {current_nutrition.get('calories', 0):.1f}")
    print(f"  - Protein: {current_nutrition.get('protein', 0):.1f}g")
    print(f"  - Carbs: {current_nutrition.get('carbs', 0):.1f}g")
    print(f"  - Fat: {current_nutrition.get('fat', 0):.1f}g")
    
    # Calculate gaps
    gaps = {}
    for macro in ['protein', 'carbs', 'fat']:
        current = current_nutrition.get(macro, 0)
        target = user_meal_data['target_macros'].get(macro, 0)
        gaps[macro] = target - current
    
    print(f"\n📈 Gaps to Targets:")
    for macro, gap in gaps.items():
        if gap > 0:
            print(f"  - {macro.capitalize()} deficit: {gap:.1f}g")
        elif gap < 0:
            print(f"  - {macro.capitalize()} excess: {abs(gap):.1f}g")
        else:
            print(f"  - {macro.capitalize()}: ✅ Target met")
    
    # Test the aggressive smart scaling method
    print(f"\n🎯 Testing Aggressive Smart Scaling...")
    try:
        result = engine._balance_by_smart_scaling(
            ingredients,
            user_meal_data["target_macros"],
            gaps
        )
        
        if result:
            print(f"✅ Method: {result['method']}")
            print(f"📊 Quantities: {result['quantities']}")
            
            # Calculate final nutrition
            final_nutrition = engine._calculate_final_meal(ingredients, result['quantities'])
            print(f"🍽️ Final Nutrition: {final_nutrition}")
            
            # Check target achievement
            achievement = engine._check_target_achievement(final_nutrition, user_meal_data["target_macros"])
            print(f"🎯 Target Achievement: {achievement}")
        else:
            print("❌ Method returned None")
            
    except Exception as e:
        print(f"❌ Error in smart scaling: {e}")
    
    # Test the ultra-aggressive method
    print(f"\n🚀🚀🚀 Testing Ultra-Aggressive Target Reach...")
    try:
        result = engine._balance_by_aggressive_target_reach(
            ingredients,
            user_meal_data["target_macros"],
            gaps
        )
        
        if result:
            print(f"✅ Method: {result['method']}")
            print(f"📊 Quantities: {result['quantities']}")
            
            # Calculate final nutrition
            final_nutrition = engine._calculate_final_meal(ingredients, result['quantities'])
            print(f"🍽️ Final Nutrition: {final_nutrition}")
            
            # Check target achievement
            achievement = engine._check_target_achievement(final_nutrition, user_meal_data["target_macros"])
            print(f"🎯 Target Achievement: {achievement}")
        else:
            print("❌ Method returned None")
            
    except Exception as e:
        print(f"❌ Error in ultra-aggressive method: {e}")
    
    # Test the full optimization pipeline
    print(f"\n🔄 Testing Full Optimization Pipeline...")
    try:
        # Prepare the data in the format expected by the optimizer
        rag_response = {
            "ingredients": ingredients
        }
        
        result = engine.optimize_single_meal(
            rag_response,
            user_meal_data["target_macros"],
            user_meal_data["user_preferences"],
            user_meal_data["meal_type"]
        )
        
        if result and result.get("success"):
            print(f"✅ Optimization successful!")
            print(f"📊 Method: {result['optimization_result']['method']}")
            print(f"🍽️ Final Nutrition: {result['nutritional_totals']}")
            print(f"🎯 Target Achievement: {result['target_achievement']}")
            
            # Show the meal
            print(f"\n🍽️ Final Meal:")
            for ing in result['meal']:
                print(f"  - {ing['name']}: {ing['quantity_needed']}g")
                
            # Show helper ingredients if any
            if result.get('helper_ingredients_added'):
                print(f"\n🔧 Helper Ingredients Added:")
                for helper in result['helper_ingredients_added']:
                    print(f"  - {helper['name']}")
        else:
            print(f"❌ Optimization failed: {result}")
            
    except Exception as e:
        print(f"❌ Error in full optimization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_meal()
