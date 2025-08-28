#!/usr/bin/env python3
"""
Test script for the new _cleanup_excess_ingredients method
"""

from rag_optimization_engine import RAGMealOptimizer
import json

def test_cleanup_method():
    """Test the cleanup method with sample data"""
    
    # Initialize the optimizer
    optimizer = RAGMealOptimizer()
    
    # Sample ingredients with many helpers
    sample_ingredients = [
        # Input ingredients
        {
            'name': 'Low-fat Yogurt',
            'protein_per_100g': 6.0,
            'carbs_per_100g': 8.0,
            'fat_per_100g': 2.0,
            'calories_per_100g': 60.0,
            'quantity_needed': 100.0
        },
        {
            'name': 'Almonds',
            'protein_per_100g': 20.0,
            'carbs_per_100g': 20.0,
            'fat_per_100g': 46.67,
            'calories_per_100g': 533.33,
            'quantity_needed': 100.0
        },
        # Helper ingredients (many of them)
        {
            'name': 'rice_cakes',
            'protein_per_100g': 8,
            'carbs_per_100g': 80,
            'fat_per_100g': 3,
            'calories_per_100g': 400,
            'quantity_needed': 50.0,
            '_balancing_amount': 50.0
        },
        {
            'name': 'dried_apricots',
            'protein_per_100g': 3.4,
            'carbs_per_100g': 63,
            'fat_per_100g': 0.5,
            'calories_per_100g': 241,
            'quantity_needed': 50.0,
            '_balancing_amount': 50.0
        },
        {
            'name': 'whole_grain_crackers',
            'protein_per_100g': 7,
            'carbs_per_100g': 70,
            'fat_per_100g': 10,
            'calories_per_100g': 400,
            'quantity_needed': 50.0,
            '_balancing_amount': 50.0
        },
        {
            'name': 'quinoa',
            'protein_per_100g': 14,
            'carbs_per_100g': 64,
            'fat_per_100g': 6,
            'calories_per_100g': 368,
            'quantity_needed': 100.0,
            '_balancing_amount': 100.0
        },
        {
            'name': 'protein_shake',
            'protein_per_100g': 80,
            'carbs_per_100g': 5,
            'fat_per_100g': 3,
            'calories_per_100g': 400,
            'quantity_needed': 50.0,
            '_balancing_amount': 50.0
        },
        {
            'name': 'greek_yogurt',
            'protein_per_100g': 10,
            'carbs_per_100g': 4,
            'fat_per_100g': 0.5,
            'calories_per_100g': 60,
            'quantity_needed': 50.0,
            '_balancing_amount': 50.0
        }
    ]
    
    target_macros = {
        'calories': 283.2,
        'protein': 22.7,
        'carbs': 35.4,
        'fat': 6.7
    }
    
    meal_type = 'Morning Snack'
    
    print("🧪 Testing _cleanup_excess_ingredients Method")
    print("=" * 60)
    print(f"📥 Input ingredients: {len(sample_ingredients)}")
    print(f"📥 Helper ingredients: {len([i for i in sample_ingredients if '_balancing_amount' in i])}")
    
    # Test the cleanup method
    cleaned_ingredients = optimizer._cleanup_excess_ingredients(
        sample_ingredients, 
        target_macros, 
        meal_type
    )
    
    print(f"✅ Output ingredients: {len(cleaned_ingredients)}")
    print(f"✅ Helper ingredients after cleanup: {len([i for i in cleaned_ingredients if '_balancing_amount' in i])}")
    
    # Show the cleaned ingredients
    print("\n🧹 Cleaned ingredients:")
    for i, ing in enumerate(cleaned_ingredients):
        helper_mark = " (HELPER)" if '_balancing_amount' in ing else " (INPUT)"
        print(f"  {i+1}. {ing['name']}{helper_mark}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_cleanup_method()
