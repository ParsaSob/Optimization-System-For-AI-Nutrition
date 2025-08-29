#!/usr/bin/env python3
"""
Simple test to check optimization data flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_simple_optimization():
    """Test simple optimization without complex balancing"""
    
    optimizer = RAGMealOptimizer()
    
    print("🧪 Testing Simple Optimization")
    print("=" * 50)
    
    # Simple test data
    test_data = {
        "rag_response": {
            "ingredients": [
                {
                    "name": "Low-fat Yogurt",
                    "protein_per_100g": 6,
                    "carbs_per_100g": 8,
                    "fat_per_100g": 2,
                    "calories_per_100g": 60,
                    "quantity_needed": 100
                }
            ]
        },
        "target_macros": {
            "calories": 100,
            "protein": 10,
            "carbs": 15,
            "fat": 5
        },
        "user_preferences": {
            "diet_type": "balanced",
            "allergies": [],
            "preferences": []
        },
        "meal_type": "breakfast"
    }
    
    print("📥 Test data:")
    print(f"   - Meal type: {test_data['meal_type']}")
    print(f"   - Target macros: {test_data['target_macros']}")
    
    try:
        result = optimizer.optimize_single_meal(
            rag_response=test_data,
            target_macros=test_data['target_macros'],
            user_preferences=test_data['user_preferences'],
            meal_type=test_data['meal_type'],
            request_data=test_data
        )
        
        print(f"\n✅ Optimization completed!")
        print(f"   - Success: {result.get('success', 'N/A')}")
        print(f"   - Meal ingredients: {len(result.get('meal', []))}")
        print(f"   - Helper ingredients: {len(result.get('helper_ingredients_added', []))}")
        print(f"   - Target achievement: {result.get('target_achievement', 'N/A')}")
        
        if result.get('meal'):
            print(f"\n🍽️ Meal ingredients:")
            for ing in result['meal']:
                print(f"   - {ing['name']}: {ing.get('quantity_needed', 0)}g")
        
        if result.get('nutritional_totals'):
            print(f"\n📊 Nutritional totals:")
            totals = result['nutritional_totals']
            print(f"   - Calories: {totals.get('calories', 0)}")
            print(f"   - Protein: {totals.get('protein', 0)}g")
            print(f"   - Carbs: {totals.get('carbs', 0)}g")
            print(f"   - Fat: {totals.get('fat', 0)}g")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_simple_optimization()
