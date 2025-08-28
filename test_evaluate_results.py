#!/usr/bin/env python3
"""
Test script to debug _evaluate_optimization_results method
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_evaluate_results():
    """Test _evaluate_optimization_results method"""
    
    optimizer = RAGMealOptimizer()
    
    print("🧪 Testing _evaluate_optimization_results Method")
    print("=" * 60)
    
    # Test ingredients
    ingredients = [
        {
            "name": "Low-fat Yogurt",
            "protein_per_100g": 6,
            "carbs_per_100g": 8,
            "fat_per_100g": 2,
            "calories_per_100g": 60,
            "quantity_needed": 100,
            "max_quantity": 500
        },
        {
            "name": "Almonds",
            "protein_per_100g": 20,
            "carbs_per_100g": 20,
            "fat_per_100g": 46.67,
            "calories_per_100g": 533.33,
            "quantity_needed": 100,
            "max_quantity": 500
        }
    ]
    
    target_macros = {
        "calories": 283.2,
        "protein": 22.7,
        "carbs": 35.4,
        "fat": 6.7
    }
    
    # Test results from optimization methods
    results = [
        {
            'method': 'PuLP',
            'quantities': [424.8, 0.0],
            'success': True
        },
        {
            'method': 'GA',
            'quantities': [400.0, 50.0],
            'success': True
        }
    ]
    
    print("📥 Test data:")
    print(f"   - Ingredients: {len(ingredients)}")
    print(f"   - Results: {len(results)}")
    print(f"   - Target macros: {target_macros}")
    
    print("\n🔧 Testing _evaluate_optimization_results...")
    
    try:
        # Test the method directly
        result = optimizer._evaluate_optimization_results(results, ingredients, target_macros)
        print(f"✅ Result: {result}")
        
        if result:
            print(f"   - Method: {result.get('method')}")
            print(f"   - Success: {result.get('success')}")
            print(f"   - Quantities: {result.get('quantities')}")
            
            # Calculate nutrition
            totals = optimizer._calculate_final_meal(ingredients, result['quantities'])
            print(f"   - Nutrition totals: {totals}")
            
            # Check achievement
            achievement = optimizer._check_target_achievement(totals, target_macros)
            print(f"   - Target achievement: {achievement}")
        else:
            print("   ❌ Result is None!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_evaluate_results()
