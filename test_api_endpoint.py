#!/usr/bin/env python3
"""
Test script to verify the API endpoint works correctly
"""

import requests
import json

def test_api_endpoint():
    """Test the optimize-single-meal-rag-advanced endpoint"""
    
    print("🧪 Testing API Endpoint")
    print("=" * 60)
    
    # Test data exactly as the website sends
    test_data = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "Chicken",
                            "protein_per_100g": 31.0,
                            "carbs_per_100g": 0.0,
                            "fat_per_100g": 3.6,
                            "calories_per_100g": 165.0,
                            "quantity_needed": 200
                        },
                        {
                            "name": "Walnuts",
                            "protein_per_100g": 15.0,
                            "carbs_per_100g": 14.0,
                            "fat_per_100g": 65.0,
                            "calories_per_100g": 654.0,
                            "quantity_needed": 50
                        },
                        {
                            "name": "Basmati Rice",
                            "protein_per_100g": 2.7,
                            "carbs_per_100g": 28.0,
                            "fat_per_100g": 0.3,
                            "calories_per_100g": 130.0,
                            "quantity_needed": 150
                        }
                    ]
                }
            ],
            "success": True,
            "message": "Test ingredients"
        },
        "target_macros": {
            "calories": 800,
            "protein": 40,
            "carbs": 60,
            "fat": 30
        },
        "user_preferences": {
            "diet_type": "balanced",
            "allergies": [],
            "preferences": []
        },
        "user_id": "test_user",
        "meal_type": "lunch"
    }
    
    print("📥 Test data:")
    print(f"   - Ingredients: {len(test_data['rag_response']['suggestions'][0]['ingredients'])}")
    print(f"   - Target macros: {test_data['target_macros']}")
    print(f"   - Meal type: {test_data['meal_type']}")
    
    print("\n🚀 Sending request to API...")
    
    try:
        response = requests.post(
            "http://localhost:5000/optimize-single-meal-rag-advanced",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API request successful!")
            
            # Check if ingredients were processed
            if 'meal' in result:
                meal = result['meal']
                print(f"   - Meal items: {len(meal.get('items', []))}")
                print(f"   - Total calories: {meal.get('total_calories', 0)}")
                print(f"   - Total protein: {meal.get('total_protein', 0)}")
                print(f"   - Total carbs: {meal.get('total_carbs', 0)}")
                print(f"   - Total fat: {meal.get('total_fat', 0)}")
            else:
                print("   - No meal data in response")
                print(f"   - Response keys: {list(result.keys())}")
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_api_endpoint()
