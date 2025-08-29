#!/usr/bin/env python3
"""
Test _extract_rag_ingredients method
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_extract_ingredients():
    """Test _extract_rag_ingredients method"""
    
    optimizer = RAGMealOptimizer()
    
    print("🧪 Testing _extract_rag_ingredients Method")
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
    print(f"   - Target macros: {test_data['target_macros']}")
    
    try:
        # Test _extract_rag_ingredients directly
        ingredients = optimizer._extract_rag_ingredients(test_data)
        
        print(f"\n✅ _extract_rag_ingredients completed!")
        print(f"   - Extracted ingredients: {len(ingredients)}")
        
        if ingredients:
            print(f"\n🍽️ Extracted ingredients:")
            for ing in ingredients:
                print(f"   - {ing['name']}: {ing.get('quantity_needed', 0)}g")
                print(f"     Protein: {ing.get('protein_per_100g', 0)}g")
                print(f"     Carbs: {ing.get('carbs_per_100g', 0)}g")
                print(f"     Fat: {ing.get('fat_per_100g', 0)}g")
                print(f"     Calories: {ing.get('calories_per_100g', 0)}")
        else:
            print("   ❌ No ingredients extracted!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_extract_ingredients()
