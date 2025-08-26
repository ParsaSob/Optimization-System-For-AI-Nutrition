#!/usr/bin/env python3
"""
Simple test for hybrid optimization target achievement
"""

import json
import time

def test_hybrid_simple():
    """Test hybrid optimization specifically"""
    
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
    
    print("🧪 Testing Hybrid Optimization Target Achievement")
    print("=" * 60)
    
    try:
        from rag_optimization_engine import RAGMealOptimizer
        
        optimizer = RAGMealOptimizer()
        
        # Test hybrid optimization specifically
        print("🔧 Testing hybrid optimization...")
        
        # Temporarily set only hybrid method
        original_methods = optimizer.optimization_methods.copy()
        optimizer.optimization_methods = {'hybrid': original_methods['hybrid']}
        
        start_time = time.time()
        result = optimizer.optimize_single_meal(
            rag_response=rag_response,
            target_macros=target_macros,
            user_preferences=user_preferences,
            meal_type="lunch"
        )
        computation_time = time.time() - start_time
        
        # Restore original methods
        optimizer.optimization_methods = original_methods
        
        print(f"⏱️  Computation time: {computation_time:.3f}s")
        print(f"✅ Success: {result.get('optimization_result', {}).get('success', False)}")
        print(f"🔧 Method used: {result.get('optimization_result', {}).get('method', 'Unknown')}")
        print(f"🎯 Target achieved: {result.get('optimization_result', {}).get('target_achieved', False)}")
        
        # Show meal details
        meal = result.get('meal', {})
        if meal:
            print(f"\n🍽️  Final meal:")
            print(f"   Calories: {meal.get('total_calories', 0):.1f} kcal")
            print(f"   Protein: {meal.get('total_protein', 0):.1f}g")
            print(f"   Carbs: {meal.get('total_carbs', 0):.1f}g")
            print(f"   Fat: {meal.get('total_fat', 0):.1f}g")
            
            # Show target achievement details
            target_achievement = result.get('target_achievement', {})
            if target_achievement:
                print(f"\n🎯 Target Achievement Details:")
                print(f"   Overall: {target_achievement.get('overall_achieved', False)}")
                print(f"   Calories: {target_achievement.get('calories_achieved', False)}")
                print(f"   Protein: {target_achievement.get('protein_achieved', False)}")
                print(f"   Carbs: {target_achievement.get('carbs_achieved', False)}")
                print(f"   Fat: {target_achievement.get('fat_achieved', False)}")
                
                # Show deviations if available
                deviations = target_achievement.get('deviations', {})
                if deviations:
                    print(f"\n📊 Deviations:")
                    print(f"   Calories: ±{deviations.get('calories', 0):.1f}")
                    print(f"   Protein: ±{deviations.get('protein', 0):.1f}")
                    print(f"   Carbs: ±{deviations.get('carbs', 0):.1f}")
                    print(f"   Fat: ±{deviations.get('fat', 0):.1f}")
        
        # Show raw result for debugging
        print(f"\n🔍 Raw result keys: {list(result.keys())}")
        if 'optimization_result' in result:
            print(f"🔍 Optimization result keys: {list(result['optimization_result'].keys())}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hybrid_simple()
