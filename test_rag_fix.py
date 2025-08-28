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
    
    # Test data similar to what the user provided
    test_ingredients = [
        {'name': 'Ground Beef', 'quantity': 200},
        {'name': 'Basmati Rice', 'quantity': 150},
        {'name': 'Butter', 'quantity': 10},
        {'name': 'Grilled Tomato', 'quantity': 100}
    ]
    
    # Test target macros
    target_macros = {
        'calories': 800,
        'protein': 40,
        'carbs': 80,
        'fat': 30
    }
    
    print("🧪 Testing RAG Engine with Input Ingredients")
    print("=" * 50)
    
    # Test ingredient extraction
    print("\n1️⃣ Testing ingredient extraction...")
    extracted = optimizer._extract_rag_ingredients(test_ingredients)
    
    print(f"   Extracted {len(extracted)} ingredients:")
    for ing in extracted:
        print(f"   - {ing['name']}: protein={ing.get('protein_per_100g', 0)}, "
              f"carbs={ing.get('carbs_per_100g', 0)}, "
              f"fat={ing.get('fat_per_100g', 0)}, "
              f"calories={ing.get('calories_per_100g', 0)}")
    
    # Test optimization
    print("\n2️⃣ Testing optimization...")
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
        else:
            print("   ❌ Optimization failed!")
            print(f"   Error: {result.get('optimization_result', {}).get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ❌ Exception during optimization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_input_ingredients()
