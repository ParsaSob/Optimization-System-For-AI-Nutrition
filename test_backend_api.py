#!/usr/bin/env python3
"""
Test script for Backend API
Tests the /optimize-single-meal endpoint
"""

import requests
import json
import time

def test_backend_api():
    """Test the backend API endpoints"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Backend API...")
    print("=" * 50)
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    print()
    
    # Test 2: Get Ingredients
    print("2. Testing Get Ingredients...")
    try:
        response = requests.get(f"{base_url}/api/ingredients")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Ingredients loaded: {data['total_count']} items")
        else:
            print(f"   ❌ Get ingredients failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Get ingredients error: {e}")
    
    print()
    
    # Test 3: Main Optimization Endpoint
    print("3. Testing Main Optimization Endpoint...")
    
    # Sample request data
    request_data = {
        "rag_response": {
            "meal_suggestions": ["Persian breakfast with traditional ingredients"]
        },
        "target_macros": {
            "calories": 2000,
            "protein": 150,
            "carbohydrates": 200,
            "fat": 65
        },
        "user_preferences": {
            "dietary_restrictions": [],
            "allergies": [],
            "preferred_cuisines": ["persian"]
        },
        "user_id": "user_123",
        "meal_type": "lunch"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/optimize-single-meal",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Optimization successful!")
            print(f"   Method: {data['optimization_result']['method']}")
            print(f"   Computation Time: {data['optimization_result']['computation_time']}s")
            print(f"   API Response Time: {(end_time - start_time):.3f}s")
            
            if data['meal']:
                meal = data['meal']
                print(f"   Meal Time: {meal['meal_time']}")
                print(f"   Total Calories: {meal['total_calories']:.1f}")
                print(f"   Total Protein: {meal['total_protein']:.1f}g")
                print(f"   Total Carbs: {meal['total_carbs']:.1f}g")
                print(f"   Total Fat: {meal['total_fat']:.1f}g")
                print(f"   Cost Estimate: ${data['cost_estimate']}")
                
                print(f"   Ingredients ({len(meal['items'])} items):")
                for item in meal['items']:
                    print(f"     - {item['ingredient']}: {item['quantity_grams']:.1f}g")
            
            print(f"   Target Achievement:")
            for target, achieved in data['target_achievement'].items():
                status = "✅" if achieved else "❌"
                print(f"     {target}: {status}")
                
        else:
            print(f"   ❌ Optimization failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Optimization error: {e}")
    
    print()
    print("🎯 API Test Complete!")

if __name__ == "__main__":
    # Wait a bit for server to start
    print("⏳ Waiting 3 seconds for server to start...")
    time.sleep(3)
    
    test_backend_api()
