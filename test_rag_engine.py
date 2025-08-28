#!/usr/bin/env python3
"""
Test script for RAG Meal Optimizer
"""

from rag_optimization_engine import RAGMealOptimizer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_rag_optimizer():
    optimizer = RAGMealOptimizer()
    print("✅ Optimizer initialized successfully")
    
    rag_response = [
        {'name': 'chicken_breast', 'quantity': 100},
        {'name': 'brown_rice', 'quantity': 80},
        {'name': 'broccoli', 'quantity': 50}
    ]
    
    target_macros = {
        'protein': 35.0,
        'carbs': 45.0,
        'fat': 15.0,
        'calories': 400.0
    }
    
    user_preferences = {}
    meal_type = 'lunch'
    
    print(f"🍽️ Testing with {len(rag_response)} ingredients")
    print(f"🎯 Target macros: {target_macros}")
    
    try:
        result = optimizer.optimize_single_meal(
            rag_response=rag_response,
            target_macros=target_macros,
            user_preferences=user_preferences,
            meal_type=meal_type
        )
        
        print("\n✅ Optimization completed successfully!")
        print(f"📊 Method used: {result['optimization_result']['method']}")
        print(f"⏱️ Computation time: {result['optimization_result']['computation_time']}s")
        
        print("\n🍽️ Final Meal:")
        for ingredient in result['meal']:
            print(f"  - {ingredient['name']}: {ingredient['quantity_needed']}g")
        
        print(f"\n📈 Nutritional Totals:")
        totals = result['nutritional_totals']
        for macro, value in totals.items():
            print(f"  - {macro}: {value:.1f}")
        
        print(f"\n🎯 Target Achievement:")
        achievement = result['target_achievement']
        for macro, achieved in achievement.items():
            if macro != 'overall':
                status = "✅" if achieved else "❌"
                print(f"  - {macro}: {status}")
        
        print(f"\n🔧 Helper ingredients added: {result['helper_ingredients_added']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rag_optimizer()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Tests failed!")
