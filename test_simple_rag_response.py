#!/usr/bin/env python3
"""
Test with only rag_response to see if that works
"""

import requests
import json

def test_simple_rag_response():
    """Test with only rag_response"""
    
    print("🧪 Testing Simple RAG Response")
    print("=" * 50)
    
    # Test data with only rag_response
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
            "calories": 60,
            "protein": 6,
            "carbs": 8,
            "fat": 2
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
        # Send request to API
        response = requests.post(
            "http://localhost:5000/optimize-meal",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📡 API Response:")
        print(f"   - Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
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
                
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_simple_rag_response()
