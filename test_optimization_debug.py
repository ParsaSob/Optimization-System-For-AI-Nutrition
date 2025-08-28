#!/usr/bin/env python3
"""
Debug script to find where nutritional values are lost during optimization
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_optimization_debug():
    """Debug where nutritional values are lost during optimization"""
    
    optimizer = RAGMealOptimizer()
    
    print("🧪 Debugging Nutritional Values During Optimization")
    print("=" * 60)
    
    # Test data that matches the website format
    test_input = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "Ground Beef",
                            "protein_per_100g": 26.0,
                            "carbs_per_100g": 0.0,
                            "fat_per_100g": 15.0,
                            "calories_per_100g": 250.0,
                            "quantity_needed": 200
                        },
                        {
                            "name": "Ground Lamb Fat",
                            "protein_per_100g": 5.0,
                            "carbs_per_100g": 0.0,
                            "fat_per_100g": 90.0,
                            "calories_per_100g": 800.0,
                            "quantity_needed": 100
                        },
                        {
                            "name": "Onion",
                            "protein_per_100g": 1.1,
                            "carbs_per_100g": 9.0,
                            "fat_per_100g": 0.1,
                            "calories_per_100g": 40.0,
                            "quantity_needed": 100
                        },
                        {
                            "name": "Butter",
                            "protein_per_100g": 0.9,
                            "carbs_per_100g": 0.1,
                            "fat_per_100g": 81.0,
                            "calories_per_100g": 717.0,
                            "quantity_needed": 10
                        },
                        {
                            "name": "Pita Bread",
                            "protein_per_100g": 10.0,
                            "carbs_per_100g": 50.0,
                            "fat_per_100g": 2.0,
                            "calories_per_100g": 250.0,
                            "quantity_needed": 100
                        }
                    ]
                }
            ]
        },
        "target_macros": {
            "calories": 1000,
            "protein": 50,
            "carbs": 80,
            "fat": 40
        },
        "user_preferences": {
            "diet_type": "balanced",
            "allergies": [],
            "preferences": []
        },
        "user_id": "test_user",
        "meal_type": "lunch"
    }
    
    print("📥 Input data:")
    print(f"   - Target: {test_input['target_macros']}")
    print(f"   - Meal type: {test_input['meal_type']}")
    print(f"   - Ingredients: {len(test_input['rag_response']['suggestions'][0]['ingredients'])}")
    
    print("\n🚀 Running optimization...")
    
    try:
        # Extract the components from test_input
        rag_response = test_input["rag_response"]
        target_macros = test_input["target_macros"]
        user_preferences = test_input["user_preferences"]
        meal_type = test_input["meal_type"]
        
        result = optimizer.optimize_single_meal(
            rag_response=rag_response,
            target_macros=target_macros,
            user_preferences=user_preferences,
            meal_type=meal_type
        )
        
        print(f"\n✅ Optimization completed!")
        print(f"   - Method: {result.get('method', 'Unknown')}")
        print(f"   - Success: {result.get('success', False)}")
        
        if result.get('success'):
            meal = result.get('meal', [])
            print(f"\n📋 Final meal ({len(meal)} ingredients):")
            
            for i, ing in enumerate(meal):
                print(f"   {i+1}. {ing['name']}: {ing.get('quantity_needed', 0)}g")
                print(f"      P: {ing.get('protein_per_100g', 0)}, C: {ing.get('carbs_per_100g', 0)}, F: {ing.get('fat_per_100g', 0)}, Cal: {ing.get('calories_per_100g', 0)}")
                
            # Check if input ingredients preserved their values
            print(f"\n🔍 Checking input ingredient preservation:")
            for ing in meal:
                if ing['name'] in ['Ground Beef', 'Ground Lamb Fat', 'Onion', 'Butter', 'Pita Bread']:
                    has_nutrition = (
                        ing.get('protein_per_100g', 0) > 0 or
                        ing.get('carbs_per_100g', 0) > 0 or
                        ing.get('fat_per_100g', 0) > 0 or
                        ing.get('calories_per_100g', 0) > 0
                    )
                    status = "✅ PRESERVED" if has_nutrition else "❌ LOST"
                    print(f"   - {ing['name']}: {status}")
                    
                    # Show detailed comparison
                    if not has_nutrition:
                        print(f"      Original values were lost!")
                    
        else:
            print(f"❌ Optimization failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_optimization_debug()
