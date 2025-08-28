#!/usr/bin/env python3
"""
Debug script to find exactly where nutritional values are getting zeroed out
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_zero_values_debug():
    """Debug where nutritional values are getting zeroed out"""
    
    optimizer = RAGMealOptimizer()
    
    print("🧪 Debugging Zero Nutritional Values")
    print("=" * 60)
    
    # Test ingredients that the website sends (with nutritional info)
    test_ingredients = [
        {
            "name": "Ground Beef",
            "protein_per_100g": 26.0,
            "carbs_per_100g": 0.0,
            "fat_per_100g": 15.0,
            "calories_per_100g": 250.0,
            "quantity_needed": 200
        },
        {
            "name": "Ground Lamb Fat",
            "protein_per_100g": 5.0,
            "carbs_per_100g": 0.0,
            "fat_per_100g": 90.0,
            "calories_per_100g": 800.0,
            "quantity_needed": 100
        },
        {
            "name": "Onion",
            "protein_per_100g": 1.1,
            "carbs_per_100g": 9.0,
            "fat_per_100g": 0.1,
            "calories_per_100g": 40.0,
            "quantity_needed": 100
        },
        {
            "name": "Butter",
            "protein_per_100g": 0.9,
            "carbs_per_100g": 0.1,
            "fat_per_100g": 81.0,
            "calories_per_100g": 717.0,
            "quantity_needed": 10
        },
        {
            "name": "Pita Bread",
            "protein_per_100g": 10.0,
            "carbs_per_100g": 50.0,
            "fat_per_100g": 2.0,
            "calories_per_100g": 250.0,
            "quantity_needed": 100
        }
    ]
    
    print("📥 Test ingredients:")
    for ing in test_ingredients:
        print(f"   - {ing['name']}: P={ing['protein_per_100g']}, C={ing['carbs_per_100g']}, F={ing['fat_per_100g']}, Cal={ing['calories_per_100g']}")
    
    print("\n🔧 Testing _extract_rag_ingredients...")
    
    # Simulate the extraction process
    rag_response = {
        "suggestions": [
            {
                "ingredients": test_ingredients
            }
        ]
    }
    
    extracted = optimizer._extract_rag_ingredients(rag_response)
    
    print(f"\n📋 Extracted {len(extracted)} ingredients:")
    for ing in extracted:
        print(f"   - {ing['name']}: P={ing.get('protein_per_100g', 0)}, C={ing.get('carbs_per_100g', 0)}, F={ing.get('fat_per_100g', 0)}, Cal={ing.get('calories_per_100g', 0)}")
    
    print("\n🔍 Checking if any values became zero:")
    for i, ing in enumerate(test_ingredients):
        extracted_ing = extracted[i]
        if (ing['protein_per_100g'] != extracted_ing.get('protein_per_100g', 0) or
            ing['carbs_per_100g'] != extracted_ing.get('carbs_per_100g', 0) or
            ing['fat_per_100g'] != extracted_ing.get('fat_per_100g', 0) or
            ing['calories_per_100g'] != extracted_ing.get('calories_per_100g', 0)):
            print(f"   ❌ {ing['name']}: Values changed!")
            print(f"      Original: P={ing['protein_per_100g']}, C={ing['carbs_per_100g']}, F={ing['fat_per_100g']}, Cal={ing['calories_per_100g']}")
            print(f"      Extracted: P={extracted_ing.get('protein_per_100g', 0)}, C={extracted_ing.get('carbs_per_100g', 0)}, F={extracted_ing.get('fat_per_100g', 0)}, Cal={extracted_ing.get('calories_per_100g', 0)}")
        else:
            print(f"   ✅ {ing['name']}: Values preserved")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_zero_values_debug()
