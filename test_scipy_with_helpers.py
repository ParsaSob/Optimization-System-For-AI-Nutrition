#!/usr/bin/env python3
"""
Test script for SciPy optimization with helper ingredients
This will add helper ingredients to reach targets more precisely
"""

import requests
import json
import time

def test_scipy_with_helpers():
    """Test the scipy optimization with helpers endpoint"""
    
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
    
    print("🚀 Testing SciPy Optimization WITH Helper Ingredients...")
    print("=" * 60)
    
    # Print input data
    print("📊 Input Ingredients:")
    for ing in test_data["ingredients"]:
        print(f"  • {ing['name']}: {ing['protein_per_100g']}g protein, {ing['carbs_per_100g']}g carbs, {ing['fat_per_100g']}g fat, {ing['calories_per_100g']} cal")
    
    print(f"\n🎯 Target Macros:")
    print(f"  • Calories: {test_data['target_macros']['calories']} kcal")
    print(f"  • Protein: {test_data['target_macros']['protein']} g")
    print(f"  • Carbs: {test_data['target_macros']['carbs']} g")
    print(f"  • Fat: {test_data['target_macros']['fat']} g")
    
    print("\n" + "=" * 60)
    
    try:
        # Send request to the new endpoint
        print("🌐 Sending request to /test-scipy-with-helpers...")
        
        response = requests.post(
            "http://localhost:5000/test-scipy-with-helpers",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Optimization with helpers completed.")
            print("\n📈 Optimization Results:")
            print(f"  • Method: {result.get('method', 'Unknown')}")
            print(f"  • Success: {result.get('success', False)}")
            
            # Print helper ingredients added
            helper_ingredients = result.get('helper_ingredients', [])
            if helper_ingredients:
                print(f"\n🔧 Helper Ingredients Added:")
                for helper in helper_ingredients:
                    print(f"  • {helper['name']}: {helper['protein_per_100g']}g protein, {helper['carbs_per_100g']}g carbs, {helper['fat_per_100g']}g fat, {helper['calories_per_100g']} cal")
            else:
                print(f"\n🔧 No helper ingredients were needed")
            
            # Print optimization details
            opt_result = result.get('optimization_result', {})
            if opt_result:
                print(f"\n📊 Optimization Details:")
                print(f"  • Method: {opt_result.get('method', 'Unknown')}")
                print(f"  • Success: {opt_result.get('success', False)}")
                
                if opt_result.get('success'):
                    quantities = opt_result.get('quantities', [])
                    if quantities:
                        all_ingredients = result.get('all_ingredients', [])
                        print(f"\n🥗 Optimized Quantities (including helpers):")
                        for i, qty in enumerate(quantities):
                            if i < len(all_ingredients):
                                ing_name = all_ingredients[i]['name']
                                ing_type = "🆘" if i >= len(test_data["ingredients"]) else "📝"
                                print(f"  {ing_type} {ing_name}: {qty:.1f}g")
                    
                    # Show final nutrition
                    final_nutrition = opt_result.get('final_nutrition', {})
                    if final_nutrition:
                        print(f"\n📊 Final Nutrition (with helpers):")
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
                        
                        # Calculate differences
                        print(f"\n📈 Differences from Target:")
                        print(f"  • Calories: {final_nutrition['calories'] - targets['calories']:+.1f} kcal")
                        print(f"  • Protein: {final_nutrition['protein'] - targets['protein']:+.1f} g")
                        print(f"  • Carbs: {final_nutrition['carbs'] - targets['carbs']:+.1f} g")
                        print(f"  • Fat: {final_nutrition['fat'] - targets['fat']:+.1f} g")
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

if __name__ == "__main__":
    print("🍽️  SciPy Optimization WITH Helpers Test Script")
    print("=" * 60)
    
    # Wait a bit for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Run the test
    test_scipy_with_helpers()
    
    print("\n" + "=" * 60)
    print("�� Test completed!")
