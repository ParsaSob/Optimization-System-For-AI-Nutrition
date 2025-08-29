#!/usr/bin/env python3
"""
Test direct target adjustment functionality
"""

import requests
import json

def test_direct_adjustment():
    """Test direct target adjustment with Morning Snack"""
    
    print("🧪 Testing Direct Target Adjustment")
    print("=" * 50)
    
    # Test data for Morning Snack with targets that need direct adjustment
    test_data = {
        "rag_response": {
            "ingredients": [
                {
                    "name": "Low-fat Yogurt",
                    "protein_per_100g": 6,
                    "carbs_per_100g": 8,
                    "fat_per_100g": 2,
                    "calories_per_100g": 60,
                    "quantity_needed": 200
                },
                {
                    "name": "Almonds",
                    "protein_per_100g": 20,
                    "carbs_per_100g": 20,
                    "fat_per_100g": 46.67,
                    "calories_per_100g": 533.33,
                    "quantity_needed": 20
                }
            ]
        },
        "target_macros": {
            "calories": 283.2,
            "protein": 22.7,
            "carbs": 35.4,
            "fat": 6.7
        },
        "user_preferences": {
            "diet_type": "balanced",
            "allergies": [],
            "preferences": []
        },
        "meal_type": "Morning Snack"
    }
    
    print("📥 Test data:")
    print(f"   - Meal type: {test_data['meal_type']}")
    print(f"   - Target macros: {test_data['target_macros']}")
    print("   - Input ingredients: Low-fat Yogurt (200g), Almonds (20g)")
    
    # Calculate expected from input ingredients
    yogurt_nutrition = {
        'calories': 60 * 2,  # 200g
        'protein': 6 * 2,
        'carbs': 8 * 2,
        'fat': 2 * 2
    }
    
    almonds_nutrition = {
        'calories': 533.33 * 0.2,  # 20g
        'protein': 20 * 0.2,
        'carbs': 20 * 0.2,
        'fat': 46.67 * 0.2
    }
    
    input_totals = {
        'calories': yogurt_nutrition['calories'] + almonds_nutrition['calories'],
        'protein': yogurt_nutrition['protein'] + almonds_nutrition['protein'],
        'carbs': yogurt_nutrition['carbs'] + almonds_nutrition['carbs'],
        'fat': yogurt_nutrition['fat'] + almonds_nutrition['fat']
    }
    
    print(f"   - Expected from inputs: {input_totals}")
    
    # Calculate gaps
    gaps = {}
    for macro in ['calories', 'protein', 'carbs', 'fat']:
        gap = test_data['target_macros'][macro] - input_totals[macro]
        gaps[macro] = gap
    
    print(f"   - Expected gaps: {gaps}")
    
    try:
        # Send request to API
        response = requests.post(
            "http://localhost:5000/optimize-meal",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📡 API Response:")
        print(f"   - Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   - Success: {result.get('success', 'N/A')}")
            print(f"   - Meal ingredients: {len(result.get('meal', []))}")
            print(f"   - Helper ingredients: {len(result.get('helper_ingredients_added', []))}")
            print(f"   - Target achievement: {result.get('target_achievement', 'N/A')}")
            
            if result.get('meal'):
                print(f"\n🍽️ Meal ingredients:")
                for ing in result['meal']:
                    print(f"   - {ing['name']}: {ing.get('quantity_needed', 0)}g")
            
            if result.get('nutritional_totals'):
                print(f"\n📊 Nutritional totals:")
                totals = result['nutritional_totals']
                print(f"   - Calories: {totals.get('calories', 0):.1f} (target: {test_data['target_macros']['calories']})")
                print(f"   - Protein: {totals.get('protein', 0):.1f}g (target: {test_data['target_macros']['protein']}g)")
                print(f"   - Carbs: {totals.get('carbs', 0):.1f}g (target: {test_data['target_macros']['carbs']}g)")
                print(f"   - Fat: {totals.get('fat', 0):.1f}g (target: {test_data['target_macros']['fat']}g)")
                
                # Calculate final gaps
                final_gaps = {}
                for macro in ['calories', 'protein', 'carbs', 'fat']:
                    final_gap = test_data['target_macros'][macro] - totals.get(macro, 0)
                    final_gaps[macro] = final_gap
                
                print(f"\n🎯 Final gaps:")
                for macro, gap in final_gaps.items():
                    status = "✅" if abs(gap) < 2 else "❌"
                    print(f"   - {macro}: {gap:+.1f} {status}")
                
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_direct_adjustment()
