#!/usr/bin/env python3
"""
Test script to see the actual response structure from /optimize-meal
"""

import requests
import json

def test_response_structure():
    """Test and see the response structure"""
    
    print("🧪 Testing Response Structure from /optimize-meal")
    print("=" * 60)
    
    # Test data exactly as the website sends for Morning Snack
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
    
    print("🚀 Sending request to /optimize-meal...")
    
    try:
        response = requests.post(
            "http://localhost:5000/optimize-meal",
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
    test_response_structure()
