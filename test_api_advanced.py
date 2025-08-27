#!/usr/bin/env python3
"""
Test script for the new Advanced RAG Optimization API endpoint
"""

import requests
import json
import time

def test_advanced_rag_api():
    """Test the new advanced RAG optimization API endpoint"""
    
    # API endpoint
    base_url = "http://localhost:8000"
    endpoint = "/optimize-advanced-rag-meal"
    
    print("🧪 Testing Advanced RAG Optimization API")
    print("=" * 50)
    print(f"Endpoint: {base_url}{endpoint}")
    print()
    
    # Sample request data
    request_data = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "chicken_breast",
                            "protein_per_100g": 31,
                            "carbs_per_100g": 0,
                            "fat_per_100g": 3.6,
                            "calories_per_100g": 165,
                            "quantity_needed": 150
                        },
                        {
                            "name": "brown_rice",
                            "protein_per_100g": 2.7,
                            "carbs_per_100g": 23,
                            "fat_per_100g": 0.9,
                            "calories_per_100g": 111,
                            "quantity_needed": 100
                        },
                        {
                            "name": "broccoli",
                            "protein_per_100g": 2.8,
                            "carbs_per_100g": 7,
                            "fat_per_100g": 0.4,
                            "calories_per_100g": 34,
                            "quantity_needed": 100
                        }
                    ]
                }
            ]
        },
        "target_macros": {
            "calories": 800,
            "protein": 60,
            "carbs": 80,
            "fat": 25
        },
        "user_preferences": {
            "diet_type": "high_protein",
            "allergies": [],
            "preferences": ["low_sodium", "organic"]
        },
        "user_id": "test_user_123",
        "meal_type": "lunch"
    }
    
    print("📤 Request Data:")
    print(f"  • RAG Ingredients: {len(request_data['rag_response']['suggestions'][0]['ingredients'])}")
    print(f"  • Target Calories: {request_data['target_macros']['calories']}")
    print(f"  • Target Protein: {request_data['target_macros']['protein']}g")
    print(f"  • Target Carbs: {request_data['target_macros']['carbs']}g")
    print(f"  • Target Fat: {request_data['target_macros']['fat']}g")
    print(f"  • User ID: {request_data['user_id']}")
    print(f"  • Meal Type: {request_data['meal_type']}")
    print()
    
    try:
        # Make API request
        print("🚀 Sending request to API...")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}{endpoint}",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        end_time = time.time()
        request_time = end_time - start_time
        
        print(f"⏱️  Request completed in {request_time:.2f} seconds")
        print(f"📊 Response Status: {response.status_code}")
        print()
        
        if response.status_code == 200:
            # Success response
            result = response.json()
            print("✅ API Request Successful!")
            print()
            
            print("📊 Response Data:")
            print(f"  • User ID: {result.get('user_id', 'N/A')}")
            print(f"  • Success: {result.get('success', 'N/A')}")
            print(f"  • Ingredients Count: {len(result.get('meal', []))}")
            print()
            
            # Optimization result details
            optimization_result = result.get('optimization_result', {})
            print("🔧 Optimization Result:")
            print(f"  • Method: {optimization_result.get('method', 'N/A')}")
            print(f"  • Success: {optimization_result.get('success', 'N/A')}")
            print(f"  • Computation Time: {optimization_result.get('computation_time', 'N/A')}s")
            print()
            
            # Nutritional totals
            nutritional_totals = result.get('nutritional_totals', {})
            print("📈 Nutritional Totals:")
            print(f"  • Calories: {nutritional_totals.get('calories', 0):.1f}")
            print(f"  • Protein: {nutritional_totals.get('protein', 0):.1f}g")
            print(f"  • Carbs: {nutritional_totals.get('carbs', 0):.1f}g")
            print(f"  • Fat: {nutritional_totals.get('fat', 0):.1f}g")
            print()
            
            # Target achievement
            target_achievement = result.get('target_achievement', {})
            print("🎯 Target Achievement:")
            for macro, achieved in target_achievement.items():
                if macro != 'overall':
                    status = "✅" if achieved else "❌"
                    print(f"  {status} {macro.capitalize()}: {'Achieved' if achieved else 'Not Achieved'}")
            
            overall_achievement = target_achievement.get('overall', False)
            print(f"  🎯 Overall: {'✅ All Targets Achieved' if overall_achievement else '❌ Some Targets Not Met'}")
            print()
            
            # Meal details
            meal = result.get('meal', [])
            print("🍽️ Meal Composition:")
            print("  🥘 RAG Ingredients:")
            rag_count = len(request_data['rag_response']['suggestions'][0]['ingredients'])
            for i, ingredient in enumerate(meal[:rag_count]):
                qty = ingredient.get('quantity_needed', 100)
                print(f"    • {ingredient['name']}: {qty:.1f}g")
            
            if len(meal) > rag_count:
                print("  ➕ Supplementary Ingredients:")
                for ingredient in meal[rag_count:]:
                    qty = ingredient.get('quantity_needed', 100)
                    print(f"    • {ingredient['name']}: {qty:.1f}g")
            
            print()
            print("🎉 Test completed successfully!")
            
        else:
            # Error response
            print(f"❌ API Request Failed with status {response.status_code}")
            print(f"Error Response: {response.text}")
            
            try:
                error_data = response.json()
                print(f"Error Detail: {error_data.get('detail', 'Unknown error')}")
            except:
                print("Could not parse error response")
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to the API server")
        print("Make sure the server is running on http://localhost:8000")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long to complete")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()

def test_health_endpoint():
    """Test the health endpoint to check if server is running"""
    
    base_url = "http://localhost:8000"
    endpoint = "/health"
    
    print(f"\n🏥 Testing Health Endpoint: {base_url}{endpoint}")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}{endpoint}", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Server is healthy!")
            print(f"  • Status: {health_data.get('status', 'N/A')}")
            print(f"  • Database Ready: {health_data.get('database_ready', 'N/A')}")
            print(f"  • Engine Ready: {health_data.get('engine_ready', 'N/A')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        print("Start the server with: python main.py")
        
    except Exception as e:
        print(f"❌ Health check error: {e}")

if __name__ == "__main__":
    print("🧪 Advanced RAG Optimization API Test Suite")
    print("=" * 60)
    
    # Test health endpoint first
    test_health_endpoint()
    
    # Test the main endpoint
    test_advanced_rag_api()
    
    print("\n🎉 All tests completed!")
    print("\n💡 To use this API from your Next.js app:")
    print("   POST /optimize-advanced-rag-meal")
    print("   With the request structure shown above")
