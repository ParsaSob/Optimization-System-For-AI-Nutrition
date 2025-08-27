#!/usr/bin/env python3
"""
Test to verify that the system reaches targets precisely without exceeding them
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_precise_targets():
    """Test that the system reaches targets precisely"""
    print("🧪 TESTING: Precise target achievement without exceeding")
    print("=" * 60)
    
    # Mock RAG response with low protein
    rag_response = {
        "suggestions": [
            {
                "ingredients": [
                    {"name": "Rice", "amount": 100, "calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
                    {"name": "Tomato", "amount": 50, "calories": 9, "protein": 0.9, "carbs": 2.1, "fat": 0.1}
                ]
            }
        ]
    }
    
    # Target macros
    target_macros = {
        "calories": 600,
        "protein": 60,
        "carbs": 70,
        "fat": 20
    }
    
    user_preferences = {
        "cuisine_preference": "persian",
        "dietary_restrictions": [],
        "protein_priority": ["chicken", "fish", "beef", "lentils"],
        "carb_priority": ["rice", "bread", "potatoes"],
        "fat_priority": ["olive_oil", "nuts", "avocado"]
    }
    
    try:
        engine = RAGMealOptimizer()
        
        # Run optimization
        print("🚀 Running optimization...")
        result = engine.optimize_single_meal(rag_response, target_macros, user_preferences, "dinner")
        
        print("✅ Optimization completed!")
        
        if 'meal' in result:
            meal_data = result['meal']
            
            if isinstance(meal_data, dict) and 'items' in meal_data:
                meal_items = meal_data['items']
                print(f"🍽️ Final meal has {len(meal_items)} ingredients")
                
                # Show all ingredients
                for i, item in enumerate(meal_items):
                    print(f"  {i+1}. {item.get('ingredient', 'Unknown')} - {item.get('quantity_grams', 0):.1f}g")
                    print(f"     Calories: {item.get('calories', 0):.1f}, Protein: {item.get('protein', 0):.1f}g, Carbs: {item.get('carbs', 0):.1f}g, Fat: {item.get('fat', 0):.1f}g")
                
                # Show totals
                if 'total_calories' in meal_data:
                    total_cal = meal_data['total_calories']
                    total_protein = meal_data['total_protein']
                    total_carbs = meal_data['total_carbs']
                    total_fat = meal_data['total_fat']
                    
                    print(f"\n📊 TOTALS vs TARGETS:")
                    print(f"  Calories: {total_cal:.1f} / {target_macros['calories']} {'✅' if abs(total_cal - target_macros['calories']) <= 50 else '❌'}")
                    print(f"  Protein:  {total_protein:.1f}g / {target_macros['protein']}g {'✅' if abs(total_protein - target_macros['protein']) <= 5 else '❌'}")
                    print(f"  Carbs:    {total_carbs:.1f}g / {target_macros['carbs']}g {'✅' if abs(total_carbs - target_macros['carbs']) <= 5 else '❌'}")
                    print(f"  Fat:      {total_fat:.1f}g / {target_macros['fat']}g {'✅' if abs(total_fat - target_macros['fat']) <= 3 else '❌'}")
                    
                    # Check if targets are met precisely
                    calories_ok = abs(total_cal - target_macros['calories']) <= 50
                    protein_ok = abs(total_protein - target_macros['protein']) <= 5
                    carbs_ok = abs(total_carbs - target_macros['carbs']) <= 5
                    fat_ok = abs(total_fat - target_macros['fat']) <= 3
                    
                    if calories_ok and protein_ok and carbs_ok and fat_ok:
                        print(f"\n🎉 SUCCESS: All targets met precisely!")
                        return True
                    else:
                        print(f"\n❌ FAILURE: Some targets not met precisely")
                        return False
        
        if 'target_achievement' in result:
            achievement = result['target_achievement']
            print(f"\n🎯 Target Achievement:")
            print(f"  Overall: {'✅' if achievement.get('overall_achieved', False) else '❌'}")
            print(f"  Calories: {'✅' if achievement.get('calories_achieved', False) else '❌'}")
            print(f"  Protein: {'✅' if achievement.get('protein_achieved', False) else '❌'}")
            print(f"  Carbs: {'✅' if achievement.get('carbs_achieved', False) else '❌'}")
            print(f"  Fat: {'✅' if achievement.get('fat_achieved', False) else '❌'}")
        
        return False
        
    except Exception as e:
        print(f"❌ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_precise_targets()
    if success:
        print("\n🎉 TEST PASSED: Targets met precisely!")
    else:
        print("\n💥 TEST FAILED: Targets not met precisely!")
