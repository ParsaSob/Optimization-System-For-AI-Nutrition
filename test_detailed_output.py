#!/usr/bin/env python3
"""
Test Detailed RAG Optimization Output
Showing complete ingredient details with macros and quantities
"""

import json
import time
from rag_optimization_engine import RAGMealOptimizer

def test_detailed_output():
    """Test RAG optimization with detailed ingredient output"""
    
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
    
    print("🧪 Testing Detailed RAG Optimization Output")
    print("=" * 70)
    
    try:
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
        print()
        
        # Display optimization result
        print("📊 OPTIMIZATION RESULT")
        print("-" * 50)
        print(f"✅ Success: {result.get('optimization_result', {}).get('success', False)}")
        print(f"🔧 Method: {result.get('optimization_result', {}).get('method', 'Unknown')}")
        print(f"⏱️  Time: {computation_time:.3f}s")
        print(f"🎯 Target Achieved: {result.get('optimization_result', {}).get('target_achieved', False)}")
        print()
        
        # Display meal summary
        meal = result.get('meal', {})
        print("🍽️  MEAL SUMMARY")
        print("-" * 50)
        print(f"🍽️  Meal Type: {meal.get('meal_time', 'Unknown')}")  # Changed from 'meal_type' to 'meal_time'
        print(f"🔥 Total Calories: {meal.get('total_calories', 0):.1f} kcal")
        print(f"🥩 Total Protein: {meal.get('total_protein', 0):.1f}g")
        print(f"🍞 Total Carbs: {meal.get('total_carbs', 0):.1f}g")
        print(f"🥑 Total Fat: {meal.get('total_fat', 0):.1f}g")
        print()
        
        # Display detailed ingredients
        print("📝 DETAILED INGREDIENTS")
        print("-" * 50)
        
        ingredients = meal.get('items', [])  # Changed from 'ingredients' to 'items'
        if ingredients:
            for i, ingredient in enumerate(ingredients, 1):
                print(f"{i:2d}. {ingredient.get('ingredient', 'Unknown Name')}")
                print(f"    📏 Quantity: {ingredient.get('quantity_grams', 0):.1f}g")
                print(f"    🔥 Calories: {ingredient.get('calories', 0):.1f} cal")
                print(f"    🥩 Protein: {ingredient.get('protein', 0):.1f}g")
                print(f"    🍞 Carbs: {ingredient.get('carbs', 0):.1f}g")
                print(f"    🥑 Fat: {ingredient.get('fat', 0):.1f}g")
                print(f"    📊 Source: {'RAG' if i <= 4 else 'Supplement'}")
                print()
        else:
            print("❌ No ingredients found in meal data")
            print()
        
        # Display target achievement
        print("🎯 TARGET ACHIEVEMENT DETAILS")
        print("-" * 50)
        
        total_calories = meal.get('total_calories', 0)
        total_protein = meal.get('total_protein', 0)
        total_carbs = meal.get('total_carbs', 0)
        total_fat = meal.get('total_fat', 0)
        
        # Calculate percentages
        cal_percent = (total_calories / target_macros['calories']) * 100
        protein_percent = (total_protein / target_macros['protein']) * 100
        carbs_percent = (total_carbs / target_macros['carbohydrates']) * 100
        fat_percent = (total_fat / target_macros['fat']) * 100
        
        print(f"🔥 Calories: {total_calories:.1f} kcal vs {target_macros['calories']:.1f} kcal ({cal_percent:.1f}%)")
        if abs(cal_percent - 100) <= 10:
            print("   ✅ Target Met (±10%)")
        else:
            print("   ❌ Target Not Met")
        
        print(f"🥩 Protein: {total_protein:.1f}g vs {target_macros['protein']:.1f}g ({protein_percent:.1f}%)")
        if abs(protein_percent - 100) <= 10:
            print("   ✅ Target Met (±10%)")
        else:
            print("   ❌ Target Not Met")
        
        print(f"🍞 Carbs: {total_carbs:.1f}g vs {target_macros['carbohydrates']:.1f}g ({carbs_percent:.1f}%)")
        if abs(carbs_percent - 100) <= 10:
            print("   ✅ Target Met (±10%)")
        else:
            print("   ❌ Target Not Met")
        
        print(f"🥑 Fat: {total_fat:.1f}g vs {target_macros['fat']:.1f}g ({fat_percent:.1f}%)")
        if abs(fat_percent - 100) <= 10:
            print("   ✅ Target Met (±10%)")
        else:
            print("   ❌ Target Not Met")
        print()
        
        # Display RAG enhancement details
        print("🔧 RAG ENHANCEMENT DETAILS")
        print("-" * 50)
        enhancement = result.get('rag_enhancement', {})
        print(f"🔧 Method: {enhancement.get('method', 'Unknown')}")
        print(f"📊 Original ingredients: {enhancement.get('original_ingredients', 0)}")
        print(f"➕ Supplements added: {enhancement.get('supplements_added', 0)}")
        print(f"📋 Total ingredients: {enhancement.get('total_ingredients', 0)}")
        print()
        
        # Display recommendations
        print("💡 RECOMMENDATIONS")
        print("-" * 50)
        recommendations = result.get('recommendations', [])
        if recommendations:
            for rec in recommendations:
                print(f"• {rec}")
        else:
            print("• No specific recommendations provided")
        print()
        
        # Display nutritional analysis
        print("📊 NUTRITIONAL ANALYSIS")
        print("-" * 50)
        
        # Calculate macro ratios
        if total_calories > 0:
            protein_ratio = (total_protein * 4 / total_calories) * 100
            carbs_ratio = (total_carbs * 4 / total_calories) * 100
            fat_ratio = (total_fat * 9 / total_calories) * 100
            
            print(f"🥩 Protein: {protein_ratio:.1f}% of total calories")
            print(f"🍞 Carbs: {carbs_ratio:.1f}% of total calories")
            print(f"🥑 Fat: {fat_ratio:.1f}% of total calories")
            print()
            
            # Check if ratios are balanced
            if 10 <= protein_ratio <= 35:
                print("✅ Protein ratio is within healthy range (10-35%)")
            else:
                print(f"⚠️  Protein ratio ({protein_ratio:.1f}%) is outside healthy range (10-35%)")
            
            if 45 <= carbs_ratio <= 65:
                print("✅ Carb ratio is within healthy range (45-65%)")
            else:
                print(f"⚠️  Carb ratio ({carbs_ratio:.1f}%) is outside healthy range (45-65%)")
            
            if 20 <= fat_ratio <= 35:
                print("✅ Fat ratio is within healthy range (20-35%)")
            else:
                print(f"⚠️  Fat ratio ({fat_ratio:.1f}%) is outside healthy range (20-35%)")
        
        print()
        print("🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_detailed_output()
