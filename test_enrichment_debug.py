#!/usr/bin/env python3
"""
Test script to verify ingredient enrichment works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_enrichment_debug():
    """Test ingredient enrichment functionality"""
    
    optimizer = RAGMealOptimizer()
    
    print("🧪 Testing Ingredient Enrichment")
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
            "name": "Chicken Breast",  # This should be enriched from nutrition_db
            "quantity_needed": 150
        },
        {
            "name": "Rice",  # This should be enriched from nutrition_db
            "quantity_needed": 100
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
            print(f"   🔧 {ing['name']}: Needs enrichment")
    
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
    
    print("\n🔍 Checking enrichment results:")
    for i, ing in enumerate(test_ingredients):
        extracted_ing = extracted[i]
        
        if 'protein_per_100g' in ing:
            # Original ingredient with nutrition - should be preserved
            if (ing['protein_per_100g'] == extracted_ing.get('protein_per_100g', 0) and
                ing['carbs_per_100g'] == extracted_ing.get('carbs_per_100g', 0) and
                ing['fat_per_100g'] == extracted_ing.get('fat_per_100g', 0) and
                ing['calories_per_100g'] == extracted_ing.get('calories_per_100g', 0)):
                print(f"   ✅ {ing['name']}: Original values preserved")
            else:
                print(f"   ❌ {ing['name']}: Values changed unexpectedly")
        else:
            # Ingredient without nutrition - should be enriched
            has_nutrition = (
                extracted_ing.get('protein_per_100g', 0) > 0 or
                extracted_ing.get('carbs_per_100g', 0) > 0 or
                extracted_ing.get('fat_per_100g', 0) > 0 or
                extracted_ing.get('calories_per_100g', 0) > 0
            )
            if has_nutrition:
                print(f"   ✅ {ing['name']}: Successfully enriched from nutrition_db")
            else:
                print(f"   ❌ {ing['name']}: Failed to enrich (still has zero values)")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_enrichment_debug()
