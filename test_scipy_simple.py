#!/usr/bin/env python3
"""
Simple test script for SciPy optimization with custom ingredients
"""

import requests
import json
import time

def test_scipy_optimization():
    """Test the scipy optimization endpoint"""
    
    # Test data with user's ingredients
    test_data = {
        "ingredients": [
            {
                "name": "Ground Beef",
                "protein_per_100g": 26.0,
                "carbs_per_100g": 0,
                "fat_per_100g": 15.0,
                "calories_per_100g": 250,
                "max_quantity": 300,
                "category": "protein"
            },
            {
                "name": "Onion",
                "protein_per_100g": 1.1,
                "carbs_per_100g": 9.0,
                "fat_per_100g": 0.1,
                "calories_per_100g": 40,
                "max_quantity": 300,
                "category": "vegetable"
            },
            {
                "name": "Grilled Tomato",
                "protein_per_100g": 1.0,
                "carbs_per_100g": 5.0,
                "fat_per_100g": 0,
                "calories_per_100g": 25,
                "max_quantity": 300,
                "category": "vegetable"
            },
            {
                "name": "Pita Bread",
                "protein_per_100g": 13.0,
                "carbs_per_100g": 41.0,
                "fat_per_100g": 4.2,
                "calories_per_100g": 247,
                "max_quantity": 300,
                "category": "grain"
            }
        ],
        "target_macros": {
            "calories": 637.2,
            "protein": 45.4,
            "carbs": 88.5,
            "fat": 13.7
        }
    }
    
    print("🚀 Testing SciPy Optimization...")
    print("=" * 50)
    
    # Print input data
    print("📊 Input Ingredients:")
    for ing in test_data["ingredients"]:
        print(f"  • {ing['name']}: {ing['protein_per_100g']}g protein, {ing['carbs_per_100g']}g carbs, {ing['fat_per_100g']}g fat, {ing['calories_per_100g']} cal")
    
    print(f"\n🎯 Target Macros:")
    print(f"  • Calories: {test_data['target_macros']['calories']} kcal")
    print(f"  • Protein: {test_data['target_macros']['protein']} g")
    print(f"  • Carbs: {test_data['target_macros']['carbs']} g")
    print(f"  • Fat: {test_data['target_macros']['fat']} g")
    
    print("\n" + "=" * 50)
    
    try:
        # Send request to the endpoint
        print("🌐 Sending request to /test-scipy-optimization...")
        
        response = requests.post(
            "http://localhost:5000/test-scipy-optimization",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Optimization completed.")
            print("\n📈 Optimization Results:")
            print(f"  • Method: {result.get('method', 'Unknown')}")
            print(f"  • Success: {result.get('success', False)}")
            
            # Print optimization details
            opt_result = result.get('optimization_result', {})
            if opt_result:
                print(f"  • Optimization Method: {opt_result.get('method', 'Unknown')}")
                print(f"  • Success: {opt_result.get('success', False)}")
                
                if opt_result.get('success'):
                    quantities = opt_result.get('quantities', [])
                    if quantities:
                        print(f"\n🥗 Optimized Quantities:")
                        for i, qty in enumerate(quantities):
                            ing_name = test_data["ingredients"][i]["name"]
                            print(f"  • {ing_name}: {qty:.1f}g")
                    
                    # Calculate final nutrition
                    final_nutrition = calculate_final_nutrition(test_data["ingredients"], quantities)
                    print(f"\n📊 Final Nutrition:")
                    print(f"  • Calories: {final_nutrition['calories']:.1f} kcal")
                    print(f"  • Protein: {final_nutrition['protein']:.1f} g")
                    print(f"  • Carbs: {final_nutrition['carbs']:.1f} g")
                    print(f"  • Fat: {final_nutrition['fat']:.1f} g")
                    
                    # Check target achievement
                    print(f"\n🎯 Target Achievement:")
                    targets = test_data["target_macros"]
                    print(f"  • Calories: {'✅' if final_nutrition['calories'] >= targets['calories'] * 0.95 else '❌'} ({final_nutrition['calories']:.1f}/{targets['calories']})")
                    print(f"  • Protein: {'✅' if final_nutrition['protein'] >= targets['protein'] * 0.95 else '❌'} ({final_nutrition['protein']:.1f}/{targets['protein']})")
                    print(f"  • Carbs: {'✅' if final_nutrition['carbs'] >= targets['carbs'] * 0.95 else '❌'} ({final_nutrition['carbs']:.1f}/{targets['carbs']})")
                    print(f"  • Fat: {'✅' if final_nutrition['fat'] >= targets['fat'] * 0.95 else '❌'} ({final_nutrition['fat']:.1f}/{targets['fat']})")
                else:
                    print(f"❌ Optimization failed: {opt_result.get('error', 'Unknown error')}")
            
            print(f"\n📝 Full Response:")
            print(json.dumps(result, indent=2))
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to server")
        print("💡 Make sure the backend server is running on port 5000")
        print("   Run: python backend_server.py")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")

def calculate_final_nutrition(ingredients, quantities):
    """Calculate final nutrition based on optimized quantities"""
    totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
    
    for i, ingredient in enumerate(ingredients):
        if i < len(quantities):
            quantity = quantities[i] / 100  # Convert grams to ratio
            totals['calories'] += ingredient['calories_per_100g'] * quantity
            totals['protein'] += ingredient['protein_per_100g'] * quantity
            totals['carbs'] += ingredient['carbs_per_100g'] * quantity
            totals['fat'] += ingredient['fat_per_100g'] * quantity
    
    return totals

if __name__ == "__main__":
    print("🍽️  SciPy Optimization Test Script")
    print("=" * 50)
    
    # Wait a bit for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Run the test
    test_scipy_optimization()
    
    print("\n" + "=" * 50)
    print("�� Test completed!")
