#!/usr/bin/env python3
"""
Test script to debug optimize_single_meal method directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_optimize_single_meal():
    """Test optimize_single_meal method directly"""
    
    optimizer = RAGMealOptimizer()
    
    print("🧪 Testing optimize_single_meal Method")
    print("=" * 60)
    
    # Test data exactly as the website sends
    test_data = {
        "rag_response": {
            "ingredients": [
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
        },
        "target_macros": {
            "calories": 283.2,
            "protein": 22.7,
            "carbs": 35.4,
            "fat": 6.7
        },
        "user_preferences": {
            "diet_type": "balanced",
            "allergies": [],
            "preferences": []
        },
        "meal_type": "Morning Snack"
    }
    
    print("📥 Test data:")
    print(f"   - Meal type: {test_data['meal_type']}")
    print(f"   - Ingredients: {len(test_data['rag_response']['ingredients'])}")
    print(f"   - Target macros: {test_data['target_macros']}")
    
    print("\n🔧 Testing optimize_single_meal...")
    
    try:
        # Test the method directly
        result = optimizer.optimize_single_meal(
            rag_response=test_data,
            target_macros=test_data['target_macros'],
            user_preferences=test_data['user_preferences'],
            meal_type=test_data['meal_type'],
            request_data=test_data
        )
        print(f"✅ Result: {result}")
        
        if result:
            print(f"   - Result type: {type(result)}")
            print(f"   - Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            if isinstance(result, dict):
                for key, value in result.items():
                    print(f"   - {key}: {type(value)} = {value}")
        else:
            print("   ❌ Result is None!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_optimize_single_meal()
