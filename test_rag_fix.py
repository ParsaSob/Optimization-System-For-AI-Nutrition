#!/usr/bin/env python3
"""
Test script to verify that RAG engine properly processes input ingredients
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_input_ingredients():
    """Test that input ingredients are properly processed and not excluded"""
    
    # Initialize the optimizer
    optimizer = RAGMealOptimizer()
    
    # Test data with EXACT format from user's test case
    # These ingredients already have their nutritional values and should NOT be enriched
    test_ingredients = [
        {
            'name': 'Ground Beef',
            'quantity': 200,
            'protein_per_100g': 26.0,
            'carbs_per_100g': 0.0,
            'fat_per_100g': 15.0,
            'calories_per_100g': 250.0
        },
        {
            'name': 'Onion',
            'quantity': 100,
            'protein_per_100g': 1.1,
            'carbs_per_100g': 9.0,
            'fat_per_100g': 0.1,
            'calories_per_100g': 40.0
        },
        {
            'name': 'Pita Bread',
            'quantity': 100,
            'protein_per_100g': 10.0,
            'carbs_per_100g': 50.0,
            'fat_per_100g': 2.0,
            'calories_per_100g': 250.0
        },
        {
            'name': 'Grilled Tomato',
            'quantity': 100,
            'protein_per_100g': 0.9,
            'carbs_per_100g': 3.9,
            'fat_per_100g': 0.2,
            'calories_per_100g': 18.0
        },
        {
            'name': 'Grilled Pepper',
            'quantity': 50,
            'protein_per_100g': 1.0,
            'carbs_per_100g': 6.0,
            'fat_per_100g': 0.3,
            'calories_per_100g': 30.0
        }
    ]
    
    # Test target macros
    target_macros = {
        'calories': 800,
        'protein': 40,
        'carbs': 80,
        'fat': 30
    }
    
    print("🧪 Testing RAG Engine with Input Ingredients (User's Test Case)")
    print("=" * 60)
    
    # Test ingredient extraction
    print("\n1️⃣ Testing ingredient extraction...")
    extracted = optimizer._extract_rag_ingredients(test_ingredients)
    
    print(f"   Extracted {len(extracted)} ingredients:")
    for ing in extracted:
        print(f"   - {ing['name']}: protein={ing.get('protein_per_100g', 0)}, "
              f"carbs={ing.get('carbs_per_100g', 0)}, "
              f"fat={ing.get('fat_per_100g', 0)}, "
              f"calories={ing.get('calories_per_100g', 0)}")
    
    # Verify that original nutritional values are preserved
    print("\n2️⃣ Verifying nutritional values preservation...")
    for i, original in enumerate(test_ingredients):
        extracted_ing = extracted[i]
        print(f"   {original['name']}:")
        print(f"     Original: P={original['protein_per_100g']}, C={original['carbs_per_100g']}, F={original['fat_per_100g']}, Cal={original['calories_per_100g']}")
        print(f"     Extracted: P={extracted_ing['protein_per_100g']}, C={extracted_ing['carbs_per_100g']}, F={extracted_ing['fat_per_100g']}, Cal={extracted_ing['calories_per_100g']}")
        
        # Check if values are preserved
        if (extracted_ing['protein_per_100g'] == original['protein_per_100g'] and
            extracted_ing['carbs_per_100g'] == original['carbs_per_100g'] and
            extracted_ing['fat_per_100g'] == original['fat_per_100g'] and
            extracted_ing['calories_per_100g'] == original['calories_per_100g']):
            print("     ✅ Values preserved correctly")
        else:
            print("     ❌ Values were changed!")
    
    # Test optimization
    print("\n3️⃣ Testing optimization...")
    try:
        result = optimizer.optimize_single_meal(
            rag_response=test_ingredients,
            target_macros=target_macros,
            user_preferences={},
            meal_type='lunch'
        )
        
        if result.get('success'):
            print("   ✅ Optimization successful!")
            print(f"   Method used: {result['optimization_result']['method']}")
            print(f"   Computation time: {result['optimization_result']['computation_time']}s")
            
            print("\n   📊 Final meal:")
            for item in result['meal']:
                print(f"   - {item['name']}: {item['quantity_needed']}g "
                      f"(P:{item['protein_per_100g']}, C:{item['carbs_per_100g']}, "
                      f"F:{item['fat_per_100g']}, Cal:{item['calories_per_100g']})")
            
            print(f"\n   🎯 Target achievement: {result['target_achievement']}")
            print(f"   📈 Nutritional totals: {result['nutritional_totals']}")
            
            if result.get('helper_ingredients_added'):
                print(f"\n   🔧 Helper ingredients added: {len(result['helper_ingredients_added'])}")
                for helper in result['helper_ingredients_added']:
                    print(f"      - {helper['name']}")
            
            # Check if input ingredients are still present with correct values
            print("\n4️⃣ Verifying input ingredients in final result...")
            input_names = {ing['name'].lower() for ing in test_ingredients}
            for item in result['meal']:
                if item['name'].lower() in input_names:
                    # Find corresponding original ingredient
                    original = next((ing for ing in test_ingredients if ing['name'].lower() == item['name'].lower()), None)
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
        else:
            print("   ❌ Optimization failed!")
            print(f"   Error: {result.get('optimization_result', {}).get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ❌ Exception during optimization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_input_ingredients()
