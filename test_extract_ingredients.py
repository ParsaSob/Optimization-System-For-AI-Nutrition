#!/usr/bin/env python3
"""
Test script to debug _extract_rag_ingredients method
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_extract_ingredients():
    """Test _extract_rag_ingredients method directly"""
    
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
    
    print("📥 Test data structure:")
    print(f"   - Top level keys: {list(test_data.keys())}")
    print(f"   - rag_response keys: {list(test_data['rag_response'].keys())}")
    print(f"   - ingredients count: {len(test_data['rag_response']['ingredients'])}")
    
    print("\n🔧 Testing _extract_rag_ingredients...")
    
    try:
        # Test with full request_data
        extracted = optimizer._extract_rag_ingredients(test_data)
        print(f"✅ Extracted {len(extracted)} ingredients")
        
        for i, ing in enumerate(extracted):
            print(f"   {i+1}. {ing['name']}: P={ing.get('protein_per_100g', 0)}, C={ing.get('carbs_per_100g', 0)}, F={ing.get('fat_per_100g', 0)}, Cal={ing.get('calories_per_100g', 0)}")
        
        # Test with just rag_response
        print(f"\n🔧 Testing with just rag_response...")
        extracted2 = optimizer._extract_rag_ingredients(test_data['rag_response'])
        print(f"✅ Extracted {len(extracted2)} ingredients from rag_response")
        
        for i, ing in enumerate(extracted2):
            print(f"   {i+1}. {ing['name']}: P={ing.get('protein_per_100g', 0)}, C={ing.get('carbs_per_100g', 0)}, F={ing.get('fat_per_100g', 0)}, Cal={ing.get('calories_per_100g', 0)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_extract_ingredients()
