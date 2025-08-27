#!/usr/bin/env python3
"""
Test script for the main optimization endpoint with automatic helper ingredients
This tests the complete algorithm: 1) optimize with 4 methods, 2) add helpers if needed, 3) re-optimize
"""

import requests
import json
import time

def test_main_optimization():
    """Test the main optimization endpoint with automatic helper ingredients"""
    
    # Test data with user's ingredients
    test_data = {
        "rag_response": "یک وعده غذایی سالم برای ناهار با گوشت، پیاز، گوجه و نان پیتا",
        "target_macros": {
            "calories": 637.2,
            "protein": 45.4,
            "carbs": 88.5,
            "fat": 13.7
        },
        "user_preferences": "گیاهی نیست، گوشت مجاز است",
        "meal_type": "lunch"
    }
    
    print("🚀 Testing Main Optimization Endpoint with Automatic Helper Ingredients...")
    print("=" * 70)
    
    # Print input data
    print("📊 Input Data:")
    print(f"  • RAG Response: {test_data['rag_response']}")
    print(f"  • User Preferences: {test_data['user_preferences']}")
    print(f"  • Meal Type: {test_data['meal_type']}")
    
    print(f"\n🎯 Target Macros:")
    print(f"  • Calories: {test_data['target_macros']['calories']} kcal")
    print(f"  • Protein: {test_data['target_macros']['protein']} g")
    print(f"  • Carbs: {test_data['target_macros']['carbs']} g")
    print(f"  • Fat: {test_data['target_macros']['fat']} g")
    
    print("\n" + "=" * 70)
    
    try:
        # Send request to the main optimization endpoint
        print("🌐 Sending request to /optimize-single-meal-rag-advanced...")
        
        response = requests.post(
            "http://localhost:5000/optimize-single-meal-rag-advanced",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Main optimization completed.")
            print("\n📈 Optimization Results:")
            print(f"  • Success: {result.get('success', False)}")
            
            # Print optimization steps
            optimization_steps = result.get('optimization_steps', {})
            if optimization_steps:
                print(f"\n🔄 Optimization Steps:")
                for step, description in optimization_steps.items():
                    print(f"  • {step}: {description}")
            
            # Print helper ingredients if added
            helper_ingredients = result.get('helper_ingredients_added', [])
            if helper_ingredients:
                print(f"\n🔧 Helper Ingredients Added:")
                for helper in helper_ingredients:
                    print(f"  • {helper['name']}: {helper['protein_per_100g']}g protein, {helper['carbs_per_100g']}g carbs, {helper['fat_per_100g']}g fat, {helper['calories_per_100g']} cal")
            else:
                print(f"\n🔧 No helper ingredients were added")
            
            # Print optimization details
            opt_result = result.get('optimization_result', {})
            if opt_result:
                print(f"\n📊 Optimization Details:")
                print(f"  • Method: {opt_result.get('method', 'Unknown')}")
                print(f"  • Success: {opt_result.get('success', False)}")
                
                if opt_result.get('success'):
                    quantities = opt_result.get('quantities', [])
                    if quantities:
                        print(f"\n🥗 Optimized Quantities:")
                        for i, qty in enumerate(quantities):
                            print(f"  • Ingredient {i+1}: {qty:.1f}g")
                    
                    # Show final nutrition
                    final_nutrition = opt_result.get('final_nutrition', {})
                    if final_nutrition:
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
                        
                        # Calculate differences
                        print(f"\n📈 Differences from Target:")
                        print(f"  • Calories: {final_nutrition['calories'] - targets['calories']:+.1f} kcal")
                        print(f"  • Protein: {final_nutrition['protein'] - targets['protein']:+.1f} g")
                        print(f"  • Carbs: {final_nutrition['carbs'] - targets['carbs']:+.1f} g")
                        print(f"  • Fat: {final_nutrition['fat'] - targets['fat']:+.1f} g")
                        
                        # Check if within 5% tolerance
                        tolerance = 0.05
                        within_tolerance = True
                        for macro in ['calories', 'protein', 'carbs', 'fat']:
                            target = targets[macro]
                            actual = final_nutrition[macro]
                            if abs(actual - target) > target * tolerance:
                                within_tolerance = False
                                break
                        
                        print(f"\n🎯 5% Tolerance Check:")
                        print(f"  • Within 5% tolerance: {'✅ YES' if within_tolerance else '❌ NO'}")
                        
                else:
                    print(f"❌ Optimization failed: {opt_result.get('error', 'Unknown error')}")
            
            # Print target achievement from result
            target_achievement = result.get('target_achievement', {})
            if target_achievement:
                print(f"\n🎯 Overall Target Achievement:")
                print(f"  • Overall: {'✅ Achieved' if target_achievement.get('overall', False) else '❌ Not Achieved'}")
                for macro in ['calories', 'protein', 'carbs', 'fat']:
                    if macro in target_achievement:
                        status = "✅" if target_achievement[macro] else "❌"
                        print(f"  • {macro.capitalize()}: {status}")
            
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
    print("🍽️  Main Optimization Test Script")
    print("=" * 70)
    
    # Wait a bit for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Run the test
    test_main_optimization()
    
    print("\n" + "=" * 70)
    print("�� Test completed!")
