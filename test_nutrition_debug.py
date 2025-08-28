#!/usr/bin/env python3
"""
Debug script to understand why input ingredients get zero nutritional values
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_nutrition_debug():
    """Debug nutritional value processing"""
    
    optimizer = RAGMealOptimizer()
    
    print("🧪 Debugging Nutritional Values")
    print("=" * 60)
    
    # Test ingredients that the website sends
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
            "name": "Pita Bread",
            "protein_per_100g": 10.0,
            "carbs_per_100g": 50.0,
            "fat_per_100g": 2.0,
            "calories_per_100g": 250.0,
            "quantity_needed": 150
        },
        {
            "name": "Grilled Tomato",
            "protein_per_100g": 0.9,
            "carbs_per_100g": 3.9,
            "fat_per_100g": 0.2,
            "calories_per_100g": 18.0,
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
    
    print("\n🔍 Checking nutrition_db for these ingredients:")
    for ing in test_ingredients:
        name = ing['name'].lower()
        if name in optimizer.nutrition_db:
            print(f"   ✅ {ing['name']} found in nutrition_db")
        else:
            print(f"   ❌ {ing['name']} NOT found in nutrition_db")
    
    print("\n✅ Test completed! Check if nutritional values are preserved.")

if __name__ == "__main__":
    test_nutrition_debug()
