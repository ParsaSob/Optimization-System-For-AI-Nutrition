#!/usr/bin/env python3
"""
Test script to verify the /optimize-meal endpoint works correctly
"""

import requests
import json

def test_optimize_meal_endpoint():
    """Test the /optimize-meal endpoint with Morning Snack"""
    
    print("🧪 Testing /optimize-meal Endpoint")
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
                },
                {
                    "name": "Walnuts",
                    "protein_per_100g": 16.67,
                    "carbs_per_100g": 13.33,
                    "fat_per_100g": 66.67,
                    "calories_per_100g": 666.67,
                    "quantity_needed": 100,
                    "max_quantity": 500
                },
                {
                    "name": "Pistachios",
                    "protein_per_100g": 20,
                    "carbs_per_100g": 23.33,
                    "fat_per_100g": 43.33,
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
    
    print("\n🚀 Sending request to /optimize-meal...")
    
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
            
            # Check if meal was optimized
            if 'meal' in result:
                meal = result['meal']
                print(f"   - Meal items: {len(meal)}")
                
                # Check if ingredients have nutrition data
                total_calories = 0
                total_protein = 0
                total_carbs = 0
                total_fat = 0
                
                for item in meal:
                    name = item['name']
                    qty = item.get('quantity_needed', 0)
                    calories = item.get('calories_per_100g', 0) * qty / 100
                    protein = item.get('protein_per_100g', 0) * qty / 100
                    carbs = item.get('carbs_per_100g', 0) * qty / 100
                    fat = item.get('fat_per_100g', 0) * qty / 100
                    
                    total_calories += calories
                    total_protein += protein
                    total_carbs += carbs
                    total_fat += fat
                    
                    print(f"     - {name}: {qty:.1f}g, Cal: {calories:.1f}, P: {protein:.1f}, C: {carbs:.1f}, F: {fat:.1f}")
                
                print(f"\n📊 Calculated totals:")
                print(f"   - Calories: {total_calories:.1f}")
                print(f"   - Protein: {total_protein:.1f}g")
                print(f"   - Carbs: {total_carbs:.1f}g")
                print(f"   - Fat: {total_fat:.1f}g")
                
                # Check target achievement
                target = test_data['target_macros']
                print(f"\n🎯 Target achievement:")
                print(f"   - Calories: {total_calories:.1f}/{target['calories']} ({total_calories/target['calories']*100:.1f}%)")
                print(f"   - Protein: {total_protein:.1f}/{target['protein']} ({total_protein/target['protein']*100:.1f}%)")
                print(f"   - Carbs: {total_carbs:.1f}/{target['carbs']} ({total_carbs/target['carbs']*100:.1f}%)")
                print(f"   - Fat: {total_fat:.1f}/{target['fat']} ({total_fat/target['fat']*100:.1f}%)")
                
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
    test_optimize_meal_endpoint()
