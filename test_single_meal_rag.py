#!/usr/bin/env python3
"""
Test script for Single Meal RAG Optimization API
Tests the /optimize-single-meal-rag endpoint with mathematical optimization
"""

import requests
import json
import time

def test_single_meal_rag_optimization():
    """Test the single meal RAG optimization endpoint"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Single Meal RAG Optimization API...")
    print("=" * 60)
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return
    
    print()
    
    # Test 2: Single Meal RAG Optimization
    print("2. Testing Single Meal RAG Optimization...")
    
    # Sample request data matching the expected structure
    request_data = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "Ground Beef",
                            "amount": 200,
                            "unit": "g",
                            "calories": 250,
                            "protein": 25,
                            "carbs": 0,
                            "fat": 15
                        },
                        {
                            "name": "Brown Rice",
                            "amount": 150,
                            "unit": "g",
                            "calories": 150,
                            "protein": 3,
                            "carbs": 30,
                            "fat": 1
                        },
                        {
                            "name": "Broccoli",
                            "amount": 100,
                            "unit": "g",
                            "calories": 34,
                            "protein": 2.8,
                            "carbs": 7,
                            "fat": 0.4
                        }
                    ]
                }
            ]
        },
        "target_macros": {
            "calories": 825,
            "protein": 46.5,
            "carbohydrates": 41.0,
            "fat": 56.0
        },
        "user_preferences": {
            "dietary_restrictions": [],
            "allergies": [],
            "preferred_cuisines": ["persian", "mediterranean"],
            "cooking_time_preference": "medium",
            "budget_constraint": 15.0
        },
        "meal_type": "lunch"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/optimize-single-meal-rag",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Single meal RAG optimization successful!")
            print(f"   Method: {data['optimization_result']['method']}")
            print(f"   Computation Time: {data['optimization_result']['computation_time']}s")
            print(f"   API Response Time: {(end_time - start_time):.3f}s")
            print(f"   Target Achieved: {data['optimization_result']['target_achieved']}")
            
            if data['meal']:
                meal = data['meal']
                print(f"   Meal Time: {meal['meal_time']}")
                print(f"   Total Calories: {meal['total_calories']:.1f}")
                print(f"   Total Protein: {meal['total_protein']:.1f}g")
                print(f"   Total Carbs: {meal['total_carbs']:.1f}g")
                print(f"   Total Fat: {meal['total_fat']:.1f}g")
                
                print(f"   Ingredients ({len(meal['items'])} items):")
                for item in meal['items']:
                    print(f"     - {item['ingredient']}: {item['quantity_grams']:.1f}g")
                    print(f"       Calories: {item['calories']:.1f}, Protein: {item['protein']:.1f}g, Carbs: {item['carbs']:.1f}g, Fat: {item['fat']:.1f}g")
            
            print(f"   Target Achievement:")
            for target, achieved in data['target_achievement'].items():
                status = "✅" if achieved else "❌"
                print(f"     {target}: {status}")
            
            if data['rag_enhancement']:
                enhancement = data['rag_enhancement']
                print(f"   RAG Enhancement:")
                print(f"     Method: {enhancement['enhancement_method']}")
                print(f"     Original Ingredients: {enhancement['original_ingredients']}")
                print(f"     Supplements Added: {enhancement['supplements_added']}")
                print(f"     Total Ingredients: {enhancement['total_ingredients']}")
                print(f"     Enhancement Ratio: {enhancement['enhancement_ratio']}")
                
        else:
            print(f"   ❌ Single meal RAG optimization failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Single meal RAG optimization error: {e}")
    
    print()
    
    # Test 3: Edge Case - Very High Protein Target
    print("3. Testing Edge Case - High Protein Target...")
    
    high_protein_request = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "Chicken Breast",
                            "amount": 150,
                            "unit": "g",
                            "calories": 165,
                            "protein": 31,
                            "carbs": 0,
                            "fat": 3.6
                        }
                    ]
                }
            ]
        },
        "target_macros": {
            "calories": 600,
            "protein": 80,
            "carbohydrates": 50,
            "fat": 20
        },
        "user_preferences": {
            "dietary_restrictions": [],
            "allergies": [],
            "preferred_cuisines": ["persian"]
        },
        "meal_type": "dinner"
    }
    
    try:
        response = requests.post(
            f"{base_url}/optimize-single-meal-rag",
            json=high_protein_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ High protein optimization successful!")
            print(f"   Method: {data['optimization_result']['method']}")
            print(f"   Target Achieved: {data['optimization_result']['target_achieved']}")
            
            if data['meal']:
                print(f"   Final Protein: {data['meal']['total_protein']:.1f}g (Target: 80g)")
        else:
            print(f"   ❌ High protein optimization failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ High protein optimization error: {e}")
    
    print()
    
    # Test 4: Edge Case - Low Calorie Target
    print("4. Testing Edge Case - Low Calorie Target...")
    
    low_calorie_request = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "Salad Greens",
                            "amount": 50,
                            "unit": "g",
                            "calories": 10,
                            "protein": 1,
                            "carbs": 2,
                            "fat": 0.1
                        }
                    ]
                }
            ]
        },
        "target_macros": {
            "calories": 200,
            "protein": 15,
            "carbohydrates": 25,
            "fat": 8
        },
        "user_preferences": {
            "dietary_restrictions": ["vegetarian"],
            "allergies": [],
            "preferred_cuisines": ["persian"]
        },
        "meal_type": "breakfast"
    }
    
    try:
        response = requests.post(
            f"{base_url}/optimize-single-meal-rag",
            json=low_calorie_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Low calorie optimization successful!")
            print(f"   Method: {data['optimization_result']['method']}")
            print(f"   Target Achieved: {data['optimization_result']['target_achieved']}")
            
            if data['meal']:
                print(f"   Final Calories: {data['meal']['total_calories']:.1f} (Target: 200)")
        else:
            print(f"   ❌ Low calorie optimization failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Low calorie optimization error: {e}")
    
    print()
    print("🎯 Single Meal RAG Optimization Test Complete!")

if __name__ == "__main__":
    # Wait a bit for server to start
    print("⏳ Waiting 3 seconds for server to start...")
    time.sleep(3)
    
    test_single_meal_rag_optimization()
