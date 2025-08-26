#!/usr/bin/env python3
"""
Test Improved RAG Optimization System
Testing with user's specific meal data
"""

import json
import requests
import time

def test_improved_rag_optimization():
    """Test the improved RAG optimization system"""
    
    # User's meal data
    rag_response = {
        "suggestions": [
            {
                "mealTitle": "Lunch",
                "ingredients": [
                    {
                        "name": "Ground Beef",
                        "amount": 100.0,
                        "unit": "g",
                        "calories": 200,
                        "protein": 20,
                        "carbs": 0,
                        "fat": 15
                    },
                    {
                        "name": "Basmati Rice",
                        "amount": 100.0,
                        "unit": "g",
                        "calories": 360,
                        "protein": 6.7,
                        "carbs": 80,
                        "fat": 1.3
                    },
                    {
                        "name": "Grilled Tomato",
                        "amount": 100.0,
                        "unit": "g",
                        "calories": 20,
                        "protein": 1,
                        "carbs": 5,
                        "fat": 0
                    },
                    {
                        "name": "Onion",
                        "amount": 100.0,
                        "unit": "g",
                        "calories": 40,
                        "protein": 2,
                        "carbs": 10,
                        "fat": 0
                    }
                ]
            }
        ],
        "success": True
    }
    
    # Target macros
    target_macros = {
        "calories": 637.2,
        "protein": 47.7,
        "carbohydrates": 79.7,
        "fat": 14.2
    }
    
    # User preferences
    user_preferences = {
        "dietary_restrictions": [],
        "allergies": [],
        "preferred_cuisines": ["persian"],
        "calorie_preference": "moderate",
        "protein_preference": "high",
        "carb_preference": "moderate",
        "fat_preference": "low"
    }
    
    # Test data
    test_data = {
        "rag_response": rag_response,
        "target_macros": target_macros,
        "user_preferences": user_preferences,
        "user_id": "test_user_123",
        "meal_type": "lunch"
    }
    
    print("🧪 Testing Improved RAG Optimization System")
    print("=" * 60)
    
    # Test local system first
    try:
        from rag_optimization_engine import RAGMealOptimizer
        
        print("📍 Testing local system...")
        optimizer = RAGMealOptimizer()
        
        start_time = time.time()
        result = optimizer.optimize_single_meal(
            rag_response=rag_response,
            target_macros=target_macros,
            user_preferences=user_preferences,
            meal_type="lunch"
        )
        computation_time = time.time() - start_time
        
        print(f"✅ Local test completed in {computation_time:.3f}s")
        print_result(result)
        
    except Exception as e:
        print(f"❌ Local test failed: {e}")
    
    # Test backend server if available
    print("\n🌐 Testing backend server...")
    try:
        response = requests.post(
            "http://localhost:5000/optimize-single-meal-rag-advanced",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Backend test successful")
            print_result(result)
        else:
            print(f"❌ Backend test failed: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Backend server not running. Start with: python backend_server.py")
    except Exception as e:
        print(f"❌ Backend test error: {e}")

def print_result(result):
    """Print optimization result in a readable format"""
    
    print("\n📊 OPTIMIZATION RESULT")
    print("-" * 40)
    
    # Optimization details
    opt_result = result.get('optimization_result', {})
    print(f"✅ Success: {opt_result.get('success', False)}")
    print(f"🔧 Method: {opt_result.get('method', 'Unknown')}")
    print(f"⏱️  Time: {opt_result.get('computation_time', 0)}s")
    print(f"🎯 Target Achieved: {opt_result.get('target_achieved', False)}")
    
    # Meal details
    meal = result.get('meal', {})
    if meal:
        print(f"\n🍽️  MEAL: {meal.get('meal_time', 'Unknown')}")
        print(f"🔥 Total Calories: {meal.get('total_calories', 0)} kcal")
        print(f"🥩 Total Protein: {meal.get('total_protein', 0)}g")
        print(f"🍞 Total Carbs: {meal.get('total_carbs', 0)}g")
        print(f"🥑 Total Fat: {meal.get('total_fat', 0)}g")
        
        print(f"\n📝 INGREDIENTS:")
        for item in meal.get('items', []):
            print(f"   • {item['ingredient']}: {item['quantity_grams']}g")
            print(f"     {item['calories']} cal, {item['protein']}g protein, {item['carbs']}g carbs, {item['fat']}g fat")
    
    # Target achievement
    target_achievement = result.get('target_achievement', {})
    if target_achievement:
        print(f"\n🎯 TARGET ACHIEVEMENT:")
        print(f"   • Calories: {'✅' if target_achievement.get('calories_achieved') else '❌'}")
        print(f"   • Protein: {'✅' if target_achievement.get('protein_achieved') else '❌'}")
        print(f"   • Carbs: {'✅' if target_achievement.get('carbs_achieved') else '❌'}")
        print(f"   • Fat: {'✅' if target_achievement.get('fat_achieved') else '❌'}")
    
    # RAG enhancement
    rag_enhancement = result.get('rag_enhancement', {})
    if rag_enhancement:
        print(f"\n🔧 RAG ENHANCEMENT:")
        print(f"   • Method: {rag_enhancement.get('enhancement_method', 'Unknown')}")
        print(f"   • Original ingredients: {rag_enhancement.get('original_ingredients', 0)}")
        print(f"   • Supplements added: {rag_enhancement.get('supplements_added', 0)}")
        print(f"   • Total ingredients: {rag_enhancement.get('total_ingredients', 0)}")
    
    # Recommendations
    recommendations = result.get('recommendations', [])
    if recommendations:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"   • {rec}")

if __name__ == "__main__":
    test_improved_rag_optimization()
