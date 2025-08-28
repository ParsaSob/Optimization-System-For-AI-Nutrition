#!/usr/bin/env python3
"""
Test file for the RAG optimization algorithm
"""

from rag_optimization_engine import RAGMealOptimizer
import json

def test_rag_optimization():
    """Test the RAG optimization algorithm"""
    
    # Initialize the optimizer
    optimizer = RAGMealOptimizer()
    
    # Test data
    rag_response = {
        "suggestions": [
            {
                "ingredients": [
                    {"name": "chicken", "quantity": 100},
                    {"name": "rice", "quantity": 150},
                    {"name": "tomato", "quantity": 50}
                ]
            }
        ]
    }
    
    target_macros = {
        "calories": 600,
        "protein": 40,
        "carbs": 60,
        "fat": 20
    }
    
    user_preferences = {}
    meal_type = "lunch"
    
    print("🚀 Testing RAG Optimization Algorithm")
    print("=" * 50)
    print(f"Target macros: {target_macros}")
    print(f"Meal type: {meal_type}")
    print()
    
    try:
        # Run optimization
        result = optimizer.optimize_single_meal(
            rag_response=rag_response,
            target_macros=target_macros,
            user_preferences=user_preferences,
            meal_type=meal_type
        )
        
        if result["success"]:
            print("✅ Optimization successful!")
            print(f"Method used: {result['optimization_result']['method']}")
            print(f"Computation time: {result['optimization_result']['computation_time']}s")
            print()
            
            print("📊 Nutritional totals:")
            for macro, value in result["nutritional_totals"].items():
                target = target_macros.get(macro, 0)
                diff_percent = abs(value - target) / target * 100 if target > 0 else 0
                print(f"  {macro}: {value:.1f} (target: {target:.1f}, diff: {diff_percent:.1f}%)")
            print()
            
            print("🎯 Target achievement:")
            for macro, achieved in result["target_achievement"].items():
                status = "✅" if achieved else "❌"
                print(f"  {macro}: {status}")
            print()
            
            print("🍽️ Final meal:")
            for i, ingredient in enumerate(result["meal"]):
                print(f"  {i+1}. {ingredient['name']}: {ingredient['quantity_needed']:.1f}g")
            print()
            
            if result["helper_ingredients_added"]:
                print("➕ Helper ingredients added:")
                for ingredient in result["helper_ingredients_added"]:
                    print(f"  - {ingredient['name']}: {ingredient['quantity_needed']:.1f}g")
                print()
            
            print("📋 Optimization steps:")
            for step_name, step_desc in result["optimization_steps"].items():
                print(f"  {step_name}: {step_desc}")
            
        else:
            print("❌ Optimization failed!")
            print(f"Error: {result['optimization_result'].get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_optimization()
