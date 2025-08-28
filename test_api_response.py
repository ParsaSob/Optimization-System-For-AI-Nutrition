#!/usr/bin/env python3
"""
Test script to see the actual API response structure
"""

import requests
import json

def test_api_response():
    """Test the API and see the response structure"""
    
    print("🧪 Testing API Response Structure")
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
    
    print("🚀 Sending request to API...")
    
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
            
            # Print the full response structure
            print("\n📋 Full Response Structure:")
            print(json.dumps(result, indent=2, default=str))
            
            # Analyze the response
            print(f"\n🔍 Response Analysis:")
            print(f"   - Response type: {type(result)}")
            print(f"   - Top-level keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            if isinstance(result, dict):
                for key, value in result.items():
                    print(f"   - {key}: {type(value)} = {value}")
            
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_api_response()
