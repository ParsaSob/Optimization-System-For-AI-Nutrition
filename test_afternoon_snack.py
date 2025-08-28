#!/usr/bin/env python3
"""
Test script to verify afternoon snack processing and input ingredient preservation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_afternoon_snack():
    """Test afternoon snack processing and input ingredient preservation"""
    
    optimizer = RAGMealOptimizer()
    
    # Test afternoon snack format
    print("🧪 Testing Afternoon Snack Processing")
    print("=" * 60)
    
    # Afternoon snack input with nutritional info
    afternoon_snack_input = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "Apple",
                            "protein_per_100g": 0.3,
                            "carbs_per_100g": 14.0,
                            "fat_per_100g": 0.2,
                            "calories_per_100g": 52.0,
                            "quantity_needed": 150
                        },
                        {
                            "name": "Almonds",
                            "protein_per_100g": 21.0,
                            "carbs_per_100g": 22.0,
                            "fat_per_100g": 50.0,
                            "calories_per_100g": 579.0,
                            "quantity_needed": 30
                        }
                    ]
                }
            ],
            "success": True,
            "message": "Ingredients extracted successfully"
        },
        "target_macros": {
            "calories": 300,
            "protein": 15,
            "carbs": 35,
            "fat": 15
        },
        "user_preferences": {
            "diet_type": "balanced",
            "allergies": [],
            "preferences": []
        },
        "user_id": "test_user",
        "meal_type": "afternoon_snack"
    }
    
    print("📥 Input format:")
    print("   - rag_response.suggestions[0].ingredients[]")
    print("   - Meal type: afternoon_snack")
    print("   - Target: 300 calories, 15g protein, 35g carbs, 15g fat")
    
    # Test ingredient extraction
    print("\n1️⃣ Testing ingredient extraction...")
    extracted = optimizer._extract_rag_ingredients(afternoon_snack_input)
    
    print(f"   Extracted {len(extracted)} ingredients:")
    for ing in extracted:
        print(f"   - {ing['name']}: protein={ing.get('protein_per_100g', 0)}, "
              f"carbs={ing.get('carbs_per_100g', 0)}, "
              f"fat={ing.get('fat_per_100g', 0)}, "
              f"calories={ing.get('calories_per_100g', 0)}, "
              f"quantity={ing.get('quantity', 0)}")
    
    # Test helper selection for afternoon snack
    print("\n2️⃣ Testing helper selection for afternoon snack...")
    existing_names = {ing['name'].lower() for ing in extracted}
    
    # Test protein helper
    protein_helper = optimizer._select_best_helper_candidate('afternoon_snack', 'protein', existing_names)
    if protein_helper:
        print(f"   ✅ Protein helper selected: {protein_helper['name']}")
    else:
        print("   ❌ No protein helper found")
    
    # Test carbs helper
    carbs_helper = optimizer._select_best_helper_candidate('afternoon_snack', 'carbs', existing_names)
    if carbs_helper:
        print(f"   ✅ Carbs helper selected: {carbs_helper['name']}")
    else:
        print("   ❌ No carbs helper found")
    
    # Test fat helper
    fat_helper = optimizer._select_best_helper_candidate('afternoon_snack', 'fat', existing_names)
    if fat_helper:
        print(f"   ✅ Fat helper selected: {fat_helper['name']}")
    else:
        print("   ❌ No fat helper found")
    
    # Test full optimization
    print("\n3️⃣ Testing full optimization...")
    try:
        result = optimizer.optimize_single_meal(
            rag_response=afternoon_snack_input,
            target_macros=afternoon_snack_input["target_macros"],
            user_preferences=afternoon_snack_input["user_preferences"],
            meal_type=afternoon_snack_input["meal_type"]
        )
        
        if result.get('success'):
            print("   ✅ Optimization successful!")
            print(f"   Method used: {result['optimization_result']['method']}")
            
            print("\n   📊 Final meal:")
            for item in result['meal']:
                print(f"   - {item['name']}: {item['quantity_needed']}g "
                      f"(P:{item['protein_per_100g']}, C:{item['carbs_per_100g']}, "
                      f"F:{item['fat_per_100g']}, Cal:{item['calories_per_100g']})")
            
            print(f"\n   🎯 Target achievement: {result['target_achievement']}")
            print(f"   📈 Nutritional totals: {result['nutritional_totals']}")
            
            # Check if input ingredients are still present with correct values
            print("\n4️⃣ Verifying input ingredients in final result...")
            original_ingredients = afternoon_snack_input["rag_response"]["suggestions"][0]["ingredients"]
            input_names = {ing['name'].lower() for ing in original_ingredients}
            
            for item in result['meal']:
                if item['name'].lower() in input_names:
                    # Find corresponding original ingredient
                    original = next((ing for ing in original_ingredients if ing['name'].lower() == item['name'].lower()), None)
                    if original:
                        if (item['protein_per_100g'] == original['protein_per_100g'] and
                            item['carbs_per_100g'] == original['carbs_per_100g'] and
                            item['fat_per_100g'] == original['fat_per_100g'] and
                            item['calories_per_100g'] == original['calories_per_100g']):
                            print(f"   ✅ {item['name']}: Values preserved correctly")
                        else:
                            print(f"   ❌ {item['name']}: Values changed!")
                            print(f"      Original: P={original['protein_per_100g']}, C={original['carbs_per_100g']}, F={original['fat_per_100g']}, Cal={original['calories_per_100g']}")
                            print(f"      Final: P={item['protein_per_100g']}, C={item['carbs_per_100g']}, F={item['fat_per_100g']}, Cal={item['calories_per_100g']}")
                
                # Check if it's a helper ingredient
                elif item['name'].lower() not in input_names:
                    print(f"   🔧 Helper ingredient: {item['name']}")
            
            if result.get('helper_ingredients_added'):
                print(f"\n   🔧 Helper ingredients added: {len(result['helper_ingredients_added'])}")
                for helper in result['helper_ingredients_added']:
                    print(f"      - {helper['name']}")
        else:
            print("   ❌ Optimization failed!")
            print(f"   Error: {result.get('optimization_result', {}).get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ❌ Exception during optimization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_afternoon_snack()
