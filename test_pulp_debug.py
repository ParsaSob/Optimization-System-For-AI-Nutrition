#!/usr/bin/env python3
"""
Test script to debug PuLP optimization specifically
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_pulp_debug():
    """Test PuLP optimization specifically"""
    
    optimizer = RAGMealOptimizer()
    
    print("🧪 Testing PuLP Optimization Debug")
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
    
    print("📥 Test data:")
    print(f"   - Ingredients: {len(ingredients)}")
    print(f"   - Target macros: {target_macros}")
    
    print("\n🔧 Testing PuLP optimization...")
    
    try:
        # Test PuLP directly
        result = optimizer._linear_optimize_pulp(ingredients, target_macros)
        print(f"✅ PuLP result: {result}")
        
        if result.get('success'):
            quantities = result['quantities']
            print(f"   - Quantities: {quantities}")
            
            # Calculate nutrition
            totals = optimizer._calculate_final_meal(ingredients, quantities)
            print(f"   - Nutrition totals: {totals}")
            
            # Check achievement
            achievement = optimizer._check_target_achievement(totals, target_macros)
            print(f"   - Target achievement: {achievement}")
        else:
            print(f"   ❌ PuLP failed: {result.get('method')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_pulp_debug()
