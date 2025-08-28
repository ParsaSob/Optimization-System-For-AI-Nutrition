#!/usr/bin/env python3
"""
Test script to verify the code works without nutrition_db
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_no_nutrition_db():
    """Test that the code works without nutrition_db"""
    
    optimizer = RAGMealOptimizer()
    
    print("🧪 Testing Without Nutrition DB")
    print("=" * 60)
    
    # Test ingredients: some with nutrition, some without
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
            "name": "Chicken Breast",  # This should be skipped (no nutrition data)
            "quantity_needed": 150
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
    
    print("📥 Test ingredients:")
    for ing in test_ingredients:
        if 'protein_per_100g' in ing:
            print(f"   ✅ {ing['name']}: Has nutrition data")
        else:
            print(f"   ⚠️ {ing['name']}: No nutrition data (will be skipped)")
    
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
    
    print("\n🔍 Checking results:")
    print(f"   - Original ingredients: {len(test_ingredients)}")
    print(f"   - Extracted ingredients: {len(extracted)}")
    print(f"   - Skipped ingredients: {len(test_ingredients) - len(extracted)}")
    
    # Check if ingredients without nutrition were skipped
    skipped_names = []
    for ing in test_ingredients:
        if 'protein_per_100g' not in ing:
            if not any(e['name'] == ing['name'] for e in extracted):
                skipped_names.append(ing['name'])
    
    if skipped_names:
        print(f"   ✅ Correctly skipped: {', '.join(skipped_names)}")
    else:
        print("   ❌ No ingredients were skipped")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_no_nutrition_db()
