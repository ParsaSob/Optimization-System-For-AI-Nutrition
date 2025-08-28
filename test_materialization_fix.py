#!/usr/bin/env python3
"""
Test script to verify that _materialize_ingredients now correctly shows original quantities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_materialization_fix():
    """Test that _materialize_ingredients correctly shows original quantities"""
    
    optimizer = RAGMealOptimizer()
    
    print("🧪 Testing Materialization Fix")
    print("=" * 60)
    
    # Test ingredients with quantity_needed (website format)
    test_ingredients = [
        {
            "name": "Ground Beef",
            "protein_per_100g": 26.0,
            "carbs_per_100g": 0.0,
            "fat_per_100g": 15.0,
            "calories_per_100g": 250.0,
            "quantity_needed": 200  # Website sends this
        },
        {
            "name": "Onion",
            "protein_per_100g": 1.1,
            "carbs_per_100g": 9.0,
            "fat_per_100g": 0.1,
            "calories_per_100g": 40.0,
            "quantity_needed": 100  # Website sends this
        },
        {
            "name": "Grilled Tomato",
            "protein_per_100g": 0.9,
            "carbs_per_100g": 3.9,
            "fat_per_100g": 0.2,
            "calories_per_100g": 18.0,
            "quantity_needed": 150  # Website sends this
        }
    ]
    
    # Test quantities from optimization
    test_quantities = [150.0, 80.0, 120.0]
    
    print("📥 Test ingredients:")
    for ing in test_ingredients:
        print(f"   - {ing['name']}: quantity_needed={ing['quantity_needed']}g")
    
    print(f"\n📊 Test quantities: {test_quantities}")
    
    print("\n🔧 Testing _materialize_ingredients...")
    materialized = optimizer._materialize_ingredients(test_ingredients, test_quantities)
    
    print(f"\n📋 Materialized {len(materialized)} ingredients:")
    for ing in materialized:
        print(f"   - {ing['name']}: {ing['quantity_needed']}g")
    
    print("\n✅ Test completed! Check the logs above to see if original quantities are now displayed correctly.")

if __name__ == "__main__":
    test_materialization_fix()
