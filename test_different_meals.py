#!/usr/bin/env python3
"""
Test the tuned aggressive optimization with different meal types.
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_meal_optimization(meal_name, meal_data, target_macros):
    """Test optimization for a specific meal."""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {meal_name}")
    print(f"{'='*60}")
    
    # Initialize the engine
    engine = RAGMealOptimizer()
    
    # Extract ingredients
    ingredients = meal_data["ingredients"]
    
    # Add max_quantity to ingredients
    for ing in ingredients:
        ing['max_quantity'] = 800  # Higher max for aggressive testing
    
    print(f"🍽️ Original Ingredients:")
    for ing in ingredients:
        print(f"  - {ing['name']}: {ing['quantity_needed']}g")
        print(f"    Protein: {ing['protein_per_100g']}g/100g, Carbs: {ing['carbs_per_100g']}g/100g, Fat: {ing['fat_per_100g']}g/100g")
    
    print(f"\n🎯 Target Macros:")
    print(f"  - Calories: {target_macros['calories']}")
    print(f"  - Protein: {target_macros['protein']}g")
    print(f"  - Carbs: {target_macros['carbs']}g")
    print(f"  - Fat: {target_macros['fat']}g")
    
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
        target = target_macros.get(macro, 0)
        gaps[macro] = target - current
    
    print(f"\n📈 Gaps to Targets:")
    for macro, gap in gaps.items():
        if gap > 0:
            print(f"  - {macro.capitalize()} deficit: {gap:.1f}g")
        elif gap < 0:
            print(f"  - {macro.capitalize()} excess: {abs(gap):.1f}g")
        else:
            print(f"  - {macro.capitalize()}: ✅ Target met")
    
    # Test the ultra-precise iterative method
    print(f"\n🎯🎯🎯 Testing Ultra-Precise Iterative Method...")
    try:
        result = engine._balance_by_ultra_precise_iterative(
            ingredients,
            target_macros,
            gaps
        )
        
        if result:
            print(f"✅ Method: {result['method']}")
            
            # Calculate final nutrition
            final_nutrition = engine._calculate_final_meal(ingredients, result['quantities'])
            print(f"🍽️ Final Nutrition: {final_nutrition}")
            
            # Check target achievement
            achievement = engine._check_target_achievement(final_nutrition, target_macros)
            print(f"🎯 Target Achievement: {achievement}")
            
            # Show final quantities
            print(f"\n📊 Final Quantities:")
            for i, ing in enumerate(ingredients):
                print(f"  - {ing['name']}: {result['quantities'][i]:.1f}g")
                
        else:
            print("❌ Method returned None")
            
    except Exception as e:
        print(f"❌ Error in ultra-precise method: {e}")
    
    # Test the full optimization pipeline
    print(f"\n🔄 Testing Full Optimization Pipeline...")
    try:
        rag_response = {"ingredients": ingredients}
        
        result = engine.optimize_single_meal(
            rag_response,
            target_macros,
            {"diet_type": "balanced", "allergies": [], "preferences": []},
            "Lunch"
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
                target = target_macros.get(macro, 0)
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

def main():
    """Test multiple meal types with different targets."""
    
    # Test 1: High Protein Meal
    high_protein_meal = {
        "ingredients": [
            {
                "name": "Chicken Breast",
                "protein_per_100g": 31.0,
                "carbs_per_100g": 0,
                "fat_per_100g": 3.6,
                "calories_per_100g": 165,
                "quantity_needed": 150
            },
            {
                "name": "Sweet Potato",
                "protein_per_100g": 1.6,
                "carbs_per_100g": 20.1,
                "fat_per_100g": 0.1,
                "calories_per_100g": 86,
                "quantity_needed": 200
            },
            {
                "name": "Broccoli",
                "protein_per_100g": 2.8,
                "carbs_per_100g": 6.6,
                "fat_per_100g": 0.4,
                "calories_per_100g": 34,
                "quantity_needed": 100
            }
        ]
    }
    
    high_protein_targets = {
        "calories": 500,
        "protein": 50,
        "carbs": 45,
        "fat": 15
    }
    
    # Test 2: Low Carb Meal
    low_carb_meal = {
        "ingredients": [
            {
                "name": "Salmon",
                "protein_per_100g": 20.4,
                "carbs_per_100g": 0,
                "fat_per_100g": 13.4,
                "calories_per_100g": 208,
                "quantity_needed": 200
            },
            {
                "name": "Spinach",
                "protein_per_100g": 2.9,
                "carbs_per_100g": 3.6,
                "fat_per_100g": 0.4,
                "calories_per_100g": 23,
                "quantity_needed": 150
            },
            {
                "name": "Avocado",
                "protein_per_100g": 2.0,
                "carbs_per_100g": 8.5,
                "fat_per_100g": 14.7,
                "calories_per_100g": 160,
                "quantity_needed": 100
            }
        ]
    }
    
    low_carb_targets = {
        "calories": 600,
        "protein": 45,
        "carbs": 20,
        "fat": 40
    }
    
    # Test 3: Balanced Vegetarian Meal
    vegetarian_meal = {
        "ingredients": [
            {
                "name": "Quinoa",
                "protein_per_100g": 4.4,
                "carbs_per_100g": 21.3,
                "fat_per_100g": 1.9,
                "calories_per_100g": 120,
                "quantity_needed": 150
            },
            {
                "name": "Chickpeas",
                "protein_per_100g": 8.9,
                "carbs_per_100g": 27.4,
                "fat_per_100g": 2.6,
                "calories_per_100g": 164,
                "quantity_needed": 200
            },
            {
                "name": "Olive Oil",
                "protein_per_100g": 0,
                "carbs_per_100g": 0,
                "fat_per_100g": 100,
                "calories_per_100g": 884,
                "quantity_needed": 15
            }
        ]
    }
    
    vegetarian_targets = {
        "calories": 400,
        "protein": 25,
        "carbs": 60,
        "fat": 12
    }
    
    # Run all tests
    test_meal_optimization("High Protein Meal", high_protein_meal, high_protein_targets)
    test_meal_optimization("Low Carb Meal", low_carb_meal, low_carb_targets)
    test_meal_optimization("Balanced Vegetarian Meal", vegetarian_meal, vegetarian_targets)

if __name__ == "__main__":
    main()
