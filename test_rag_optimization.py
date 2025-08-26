#!/usr/bin/env python3
"""
Test script for RAG Meal Optimization System
Demonstrates the complete workflow from RAG response to optimized meal
"""

import requests
import json
import time

# Server configuration
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    print()

def test_rag_optimization():
    """Test the complete RAG optimization workflow"""
    print("🔍 Testing RAG meal optimization...")
    
    # Sample RAG response (as specified by user)
    rag_response = {
        "suggestions": [
            {
                "mealTitle": "Persian Chicken and Rice",
                "description": "A traditional Persian meal with chicken and aromatic rice",
                "ingredients": [
                    {
                        "name": "Chicken Breast",
                        "amount": 150,
                        "unit": "grams",
                        "calories": 247.5,
                        "protein": 46.5,
                        "carbs": 0,
                        "fat": 5.4
                    },
                    {
                        "name": "Basmati Rice",
                        "amount": 100,
                        "unit": "grams",
                        "calories": 130,
                        "protein": 2.7,
                        "carbs": 28,
                        "fat": 0.3
                    },
                    {
                        "name": "Olive Oil",
                        "amount": 15,
                        "unit": "grams",
                        "calories": 132.6,
                        "protein": 0,
                        "carbs": 0,
                        "fat": 15
                    },
                    {
                        "name": "Onion",
                        "amount": 50,
                        "unit": "grams",
                        "calories": 20,
                        "protein": 0.5,
                        "carbs": 4.7,
                        "fat": 0.1
                    }
                ],
                "totalCalories": 530.1,
                "totalProtein": 49.7,
                "totalCarbs": 32.7,
                "totalFat": 20.8
            }
        ],
        "success": True,
        "message": "Persian meal suggestion generated successfully"
    }
    
    # Target macros for optimization
    target_macros = {
        "calories": 800,
        "protein": 60,
        "carbohydrates": 80,
        "fat": 30
    }
    
    # User preferences
    user_preferences = {
        "dietary_restrictions": ["halal"],
        "allergies": [],
        "preferred_cuisines": ["persian", "mediterranean"],
        "calorie_preference": "moderate",
        "protein_preference": "high",
        "carb_preference": "moderate",
        "fat_preference": "low"
    }
    
    # Request payload
    request_data = {
        "rag_response": rag_response,
        "target_macros": target_macros,
        "user_preferences": user_preferences,
        "user_id": "user_123",
        "meal_type": "lunch"
    }
    
    try:
        print("📤 Sending optimization request...")
        print(f"   Target calories: {target_macros['calories']}")
        print(f"   Target protein: {target_macros['protein']}g")
        print(f"   Target carbs: {target_macros['carbohydrates']}g")
        print(f"   Target fat: {target_macros['fat']}g")
        print()
        
        # Test advanced RAG optimization
        response = requests.post(
            f"{BASE_URL}/optimize-single-meal-rag-advanced",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RAG optimization successful!")
            print()
            
            # Display optimization result
            print("📊 OPTIMIZATION RESULT:")
            print(f"   Method: {result['optimization_result']['method']}")
            print(f"   Success: {result['optimization_result']['success']}")
            print(f"   Target achieved: {result['optimization_result']['target_achieved']}")
            print(f"   Computation time: {result['optimization_result']['computation_time']}s")
            print()
            
            # Display meal details
            if result['meal']:
                meal = result['meal']
                print("🍽️  OPTIMIZED MEAL:")
                print(f"   Meal time: {meal['meal_time']}")
                print(f"   Total calories: {meal['total_calories']}")
                print(f"   Total protein: {meal['total_protein']}g")
                print(f"   Total carbs: {meal['total_carbs']}g")
                print(f"   Total fat: {meal['total_fat']}g")
                print()
                
                print("📝 MEAL ITEMS:")
                for item in meal['items']:
                    print(f"   • {item['ingredient']}: {item['quantity_grams']}g")
                    print(f"     Calories: {item['calories']}, Protein: {item['protein']}g, Carbs: {item['carbs']}g, Fat: {item['fat']}g")
                print()
            
            # Display target achievement
            if result['target_achievement']:
                achievement = result['target_achievement']
                print("🎯 TARGET ACHIEVEMENT:")
                print(f"   Calories achieved: {achievement['calories_achieved']}")
                print(f"   Protein achieved: {achievement['protein_achieved']}")
                print(f"   Carbs achieved: {achievement['carbs_achieved']}")
                print(f"   Fat achieved: {achievement['fat_achieved']}")
                print()
            
            # Display recommendations
            if result.get('recommendations'):
                print("💡 RECOMMENDATIONS:")
                for rec in result['recommendations']:
                    print(f"   • {rec}")
                print()
            
            # Display RAG enhancement details
            if result.get('rag_enhancement'):
                enhancement = result['rag_enhancement']
                print("🔧 RAG ENHANCEMENT:")
                print(f"   Method: {enhancement.get('enhancement_method', 'N/A')}")
                print(f"   Original ingredients: {enhancement.get('original_ingredients', 'N/A')}")
                print(f"   Supplements added: {enhancement.get('supplements_added', 'N/A')}")
                print(f"   Total ingredients: {enhancement.get('total_ingredients', 'N/A')}")
                print()
            
        else:
            print(f"❌ RAG optimization failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ RAG optimization error: {e}")
    
    print()

def test_ingredients_endpoints():
    """Test ingredients endpoints"""
    print("🔍 Testing ingredients endpoints...")
    
    try:
        # Test regular ingredients
        response = requests.get(f"{BASE_URL}/api/ingredients")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Regular ingredients loaded: {data['total_count']} ingredients")
        else:
            print(f"❌ Regular ingredients failed: {response.status_code}")
        
        # Test RAG ingredients
        response = requests.get(f"{BASE_URL}/api/rag-ingredients")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ RAG ingredients loaded: {data['total_count']} ingredients")
        else:
            print(f"❌ RAG ingredients failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ingredients test error: {e}")
    
    print()

def main():
    """Main test function"""
    print("🚀 RAG Meal Optimization System Test")
    print("=" * 50)
    print()
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    
    # Run tests
    test_health_check()
    test_ingredients_endpoints()
    test_rag_optimization()
    
    print("✨ Test completed!")

if __name__ == "__main__":
    main()
