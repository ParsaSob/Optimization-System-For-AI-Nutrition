#!/usr/bin/env python3
"""
Debug test to find why website shows wrong nutritional totals
"""

import requests
import json

def test_debug_output():
    """Debug test to find output formatting issues"""
    
    print("🔍 Debug Test: Finding Output Formatting Issues")
    print("=" * 60)
    
    # Test data for Morning Snack
    test_data = {
        "rag_response": {
            "ingredients": [
                {
                    "name": "Low-fat Yogurt",
                    "protein_per_100g": 6,
                    "carbs_per_100g": 8,
                    "fat_per_100g": 2,
                    "calories_per_100g": 60,
                    "quantity_needed": 100
                },
                {
                    "name": "Almonds",
                    "protein_per_100g": 20,
                    "carbs_per_100g": 20,
                    "fat_per_100g": 46.67,
                    "calories_per_100g": 533.33,
                    "quantity_needed": 100
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
            
            print(f"\n🔍 FULL API RESPONSE:")
            print(json.dumps(result, indent=2))
            
            print(f"\n📊 Key Fields:")
            print(f"   - Success: {result.get('success', 'N/A')}")
            print(f"   - Meal ingredients: {len(result.get('meal', []))}")
            print(f"   - Helper ingredients: {len(result.get('helper_ingredients_added', []))}")
            print(f"   - Target achievement: {result.get('target_achievement', 'N/A')}")
            
            if result.get('meal'):
                print(f"\n🍽️ Meal ingredients (RAW):")
                for i, ing in enumerate(result['meal']):
                    print(f"   {i+1}. {ing}")
            
            if result.get('nutritional_totals'):
                print(f"\n📊 Nutritional totals (RAW):")
                totals = result['nutritional_totals']
                print(f"   - Raw totals: {totals}")
                print(f"   - Calories: {totals.get('calories', 0)} (target: {test_data['target_macros']['calories']})")
                print(f"   - Protein: {totals.get('protein', 0)}g (target: {test_data['target_macros']['protein']}g)")
                print(f"   - Carbs: {totals.get('carbs', 0)}g (target: {test_data['target_macros']['carbs']}g)")
                print(f"   - Fat: {totals.get('fat', 0)}g (target: {test_data['target_macros']['fat']}g)")
                
                # Calculate expected from meal ingredients
                expected_totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
                for ing in result.get('meal', []):
                    qty = ing.get('quantity_needed', 0) / 100.0
                    expected_totals['calories'] += ing.get('calories_per_100g', 0) * qty
                    expected_totals['protein'] += ing.get('protein_per_100g', 0) * qty
                    expected_totals['carbs'] += ing.get('carbs_per_100g', 0) * qty
                    expected_totals['fat'] += ing.get('fat_per_100g', 0) * qty
                
                print(f"\n🧮 Expected from ingredients:")
                print(f"   - Calories: {expected_totals['calories']:.1f}")
                print(f"   - Protein: {expected_totals['protein']:.1f}g")
                print(f"   - Carbs: {expected_totals['carbs']:.1f}g")
                print(f"   - Fat: {expected_totals['fat']:.1f}g")
                
                # Check for discrepancies
                print(f"\n⚠️ Discrepancies:")
                for macro in ['calories', 'protein', 'carbs', 'fat']:
                    api_value = totals.get(macro, 0)
                    expected_value = expected_totals[macro]
                    diff = abs(api_value - expected_value)
                    if diff > 1:
                        print(f"   - {macro}: API={api_value}, Expected={expected_value:.1f}, Diff={diff:.1f} ❌")
                    else:
                        print(f"   - {macro}: API={api_value}, Expected={expected_value:.1f}, Diff={diff:.1f} ✅")
                
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Debug test completed!")

if __name__ == "__main__":
    test_debug_output()
