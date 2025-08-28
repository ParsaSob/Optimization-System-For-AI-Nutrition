#!/usr/bin/env python3
"""
Test the conservative reduction method for over-target meals.
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_over_target_meal():
    """Test the conservative reduction with user's over-target meal."""
    
    # Initialize the engine
    engine = RAGMealOptimizer()
    
    # User's meal data (over targets)
    user_meal_data = {
        "rag_response": {
            "ingredients": [
                {
                    "name": "Ground Beef",
                    "protein_per_100g": 20.0,  # Approximate
                    "carbs_per_100g": 0,
                    "fat_per_100g": 15.0,  # Approximate
                    "calories_per_100g": 200,  # Approximate
                    "quantity_needed": 113.6,
                    "max_quantity": 500
                },
                {
                    "name": "Onion",
                    "protein_per_100g": 1.0,
                    "carbs_per_100g": 9.0,
                    "fat_per_100g": 0,
                    "calories_per_100g": 40,
                    "quantity_needed": 200.0,
                    "max_quantity": 500
                },
                {
                    "name": "Grilled Tomato",
                    "protein_per_100g": 1.0,
                    "carbs_per_100g": 5.0,
                    "fat_per_100g": 0,
                    "calories_per_100g": 20,
                    "quantity_needed": 200.0,
                    "max_quantity": 500
                },
                {
                    "name": "Grilled Pepper",
                    "protein_per_100g": 0,
                    "carbs_per_100g": 6.0,
                    "fat_per_100g": 0,
                    "calories_per_100g": 30,
                    "quantity_needed": 76.4,
                    "max_quantity": 500
                },
                {
                    "name": "Quinoa",
                    "protein_per_100g": 14.0,
                    "carbs_per_100g": 64.0,
                    "fat_per_100g": 6.0,
                    "calories_per_100g": 368,
                    "quantity_needed": 132.2,
                    "max_quantity": 500
                },
                {
                    "name": "Barley",
                    "protein_per_100g": 3.5,
                    "carbs_per_100g": 28.0,
                    "fat_per_100g": 0.4,
                    "calories_per_100g": 123,
                    "quantity_needed": 150.0,
                    "max_quantity": 500
                }
            ]
        },
        "target_macros": {
            "calories": 637.2,
            "protein": 45.4,
            "carbs": 88.5,
            "fat": 13.7
        },
        "user_preferences": {
            "diet_type": "balanced",
            "allergies": [],
            "preferences": []
        },
        "user_id": "user_123",
        "meal_type": "Lunch"
    }
    
    print("🧪 Testing Over-Target Meal Optimization")
    print("=" * 60)
    
    # Extract ingredients
    ingredients = user_meal_data["rag_response"]["ingredients"]
    
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
    
    # Test the conservative reduction method directly
    print(f"\n🎯🎯🎯 Testing Conservative Reduction Method...")
    try:
        result = engine._balance_by_conservative_reduction(
            ingredients,
            user_meal_data["target_macros"],
            gaps
        )
        
        if result:
            print(f"✅ Method: {result['method']}")
            
            # Calculate final nutrition
            final_nutrition = engine._calculate_final_meal(ingredients, result['quantities'])
            print(f"🍽️ Final Nutrition: {final_nutrition}")
            
            # Check target achievement
            achievement = engine._check_target_achievement(final_nutrition, user_meal_data["target_macros"])
            print(f"🎯 Target Achievement: {achievement}")
            
            # Show final quantities
            print(f"\n📊 Final Quantities:")
            for i, ing in enumerate(ingredients):
                print(f"  - {ing['name']}: {result['quantities'][i]:.1f}g")
                
            # Calculate improvement
            print(f"\n📈 Improvement Analysis:")
            for macro in ['calories', 'protein', 'carbs', 'fat']:
                current = current_nutrition.get(macro, 0)
                final = final_nutrition.get(macro, 0)
                target = user_meal_data['target_macros'].get(macro, 0)
                
                current_diff = abs(current - target)
                final_diff = abs(final - target)
                improvement = current_diff - final_diff
                
                print(f"  - {macro.capitalize()}: {current:.1f} → {final:.1f} (target: {target:.1f})")
                print(f"    Improvement: {improvement:.1f} closer to target")
                
        else:
            print("❌ Method returned None")
            
    except Exception as e:
        print(f"❌ Error in conservative reduction method: {e}")
        import traceback
        traceback.print_exc()
    
    # Test the full optimization pipeline
    print(f"\n🔄 Testing Full Optimization Pipeline...")
    try:
        result = engine.optimize_single_meal(
            user_meal_data["rag_response"],
            user_meal_data["target_macros"],
            user_meal_data["user_preferences"],
            user_meal_data["meal_type"]
        )
        
        if result and result.get("success"):
            print(f"✅ Optimization successful!")
            print(f"📊 Method: {result['optimization_result']['method']}")
            print(f"🍽️ Final Nutrition: {result['nutritional_totals']}")
            print(f"🎯 Target Achievement: {result['target_achievement']}")
            
            # Calculate precision
            final_nutrition = result['nutritional_totals']
            precision_scores = {}
            for macro in ['protein', 'carbs', 'fat']:
                current = final_nutrition.get(macro, 0)
                target = user_meal_data['target_macros'].get(macro, 0)
                if target > 0:
                    precision = abs(current - target) / target * 100
                    precision_scores[macro] = precision
            
            print(f"\n🎯 Precision Analysis:")
            for macro, precision in precision_scores.items():
                if precision <= 1:
                    print(f"  - {macro.capitalize()}: 🎯🎯🎯 EXCELLENT ({precision:.2f}% off)")
                elif precision <= 3:
                    print(f"  - {macro.capitalize()}: 🎯🎯 VERY GOOD ({precision:.2f}% off)")
                elif precision <= 5:
                    print(f"  - {macro.capitalize()}: 🎯 GOOD ({precision:.2f}% off)")
                else:
                    print(f"  - {macro.capitalize()}: ⚠️ NEEDS IMPROVEMENT ({precision:.2f}% off)")
                    
        else:
            print(f"❌ Optimization failed: {result}")
            
    except Exception as e:
        print(f"❌ Error in full optimization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_over_target_meal()
