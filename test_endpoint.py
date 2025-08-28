#!/usr/bin/env python3
"""
Test the simplified endpoint
"""

import requests
import json

def test_endpoints():
    """Test both endpoints"""
    
    base_url = "http://localhost:5000"
    
    # Test health endpoint
    print("🧪 Testing /health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health endpoint: {response.status_code}")
        print(f"📄 Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test optimize-meal endpoint
    print("🧪 Testing /optimize-meal endpoint...")
    
    test_data = {
        "rag_response": {
            "ingredients": [
                {
                    "name": "Ground Beef",
                    "protein_per_100g": 20.0,
                    "carbs_per_100g": 0,
                    "fat_per_100g": 15.0,
                    "calories_per_100g": 200,
                    "quantity_needed": 113.6,
                    "max_quantity": 500
                }
            ]
        },
        "target_macros": {
            "calories": 637.2,
            "protein": 45.4,
            "carbs": 88.5,
            "fat": 13.7
        },
        "user_preferences": {
            "diet_type": "balanced",
            "allergies": [],
            "preferences": ["low_sodium", "organic"]
        },
        "meal_type": "Lunch"
    }
    
    try:
        response = requests.post(
            f"{base_url}/optimize-meal",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Optimize endpoint: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 Success: {result.get('success', 'Unknown')}")
            print(f"🎯 Method: {result.get('optimization_result', {}).get('method', 'Unknown')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Optimize endpoint failed: {e}")

if __name__ == "__main__":
    test_endpoints()
