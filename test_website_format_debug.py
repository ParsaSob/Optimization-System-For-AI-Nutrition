#!/usr/bin/env python3
"""
Debug script to understand why website ingredients are being skipped
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_website_format_debug():
    """Debug website ingredient format processing"""
    
    optimizer = RAGMealOptimizer()
    
    print("🧪 Debugging Website Ingredient Format")
    print("=" * 60)
    
    # Test ingredients exactly as the website sends them
    test_ingredients = [
        {
            "name": "Chicken",
            "protein_per_100g": 31.0,
            "carbs_per_100g": 0.0,
            "fat_per_100g": 3.6,
            "calories_per_100g": 165.0,
            "quantity_needed": 200
        },
        {
            "name": "Walnuts",
            "protein_per_100g": 15.0,
            "carbs_per_100g": 14.0,
            "fat_per_100g": 65.0,
            "calories_per_100g": 654.0,
            "quantity_needed": 50
        },
        {
            "name": "Basmati Rice",
            "protein_per_100g": 2.7,
            "carbs_per_100g": 28.0,
            "fat_per_100g": 0.3,
            "calories_per_100g": 130.0,
            "quantity_needed": 150
        },
        {
            "name": "Pomegranate Molasses",
            "protein_per_100g": 0.0,
            "carbs_per_100g": 65.0,
            "fat_per_100g": 0.0,
            "calories_per_100g": 260.0,
            "quantity_needed": 20
        },
        {
            "name": "Onion",
            "protein_per_100g": 1.1,
            "carbs_per_100g": 9.0,
            "fat_per_100g": 0.1,
            "calories_per_100g": 40.0,
            "quantity_needed": 100
        }
    ]
    
    print("📥 Test ingredients from website:")
    for ing in test_ingredients:
        print(f"   - {ing['name']}: P={ing['protein_per_100g']}, C={ing['carbs_per_100g']}, F={ing['fat_per_100g']}, Cal={ing['calories_per_100g']}")
    
    print("\n🔧 Testing nutrition detection logic...")
    
    # Test the nutrition detection logic manually
    for ing in test_ingredients:
        name = ing['name']
        has_nutrition = (
            'protein_per_100g' in ing and 
            'carbs_per_100g' in ing and 
            'fat_per_100g' in ing and 
            'calories_per_100g' in ing and
            any(ing.get(f'{macro}_per_100g', 0) != 0 for macro in ['protein', 'carbs', 'fat', 'calories'])
        )
        
        print(f"   - {name}: has_nutrition = {has_nutrition}")
        print(f"     protein_per_100g: {ing.get('protein_per_100g', 'MISSING')}")
        print(f"     carbs_per_100g: {ing.get('carbs_per_100g', 'MISSING')}")
        print(f"     fat_per_100g: {ing.get('fat_per_100g', 'MISSING')}")
        print(f"     calories_per_100g: {ing.get('calories_per_100g', 'MISSING')}")
        
        # Check the any() condition
        macro_values = [ing.get(f'{macro}_per_100g', 0) for macro in ['protein', 'carbs', 'fat', 'calories']]
        any_non_zero = any(val != 0 for val in macro_values)
        print(f"     any_non_zero: {any_non_zero} (values: {macro_values})")
        print()
    
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
    
    print("\n🔍 Analysis:")
    print(f"   - Original ingredients: {len(test_ingredients)}")
    print(f"   - Extracted ingredients: {len(extracted)}")
    print(f"   - Skipped ingredients: {len(test_ingredients) - len(extracted)}")
    
    if len(extracted) == 0:
        print("   ❌ ALL ingredients were skipped - this is the problem!")
    elif len(extracted) < len(test_ingredients):
        print("   ⚠️ Some ingredients were skipped")
    else:
        print("   ✅ All ingredients were processed")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_website_format_debug()
