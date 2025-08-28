#!/usr/bin/env python3
"""
Test file for specific ingredients optimization
Tests optimization of: Chicken, Rice, Tomato
"""

from rag_optimization_engine import RAGMealOptimizer
import json

def test_specific_ingredients():
    """Test optimization with specific ingredients: Chicken, Rice, Tomato"""
    
    # Initialize the optimizer
    optimizer = RAGMealOptimizer()
    
    # Test data with specific ingredients
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
    
    # Target macros for a balanced meal - MORE REALISTIC
    target_macros = {
        "calories": 500,
        "protein": 25,  # Reduced from 35g to 25g (5% instead of 7%)
        "carbs": 45,
        "fat": 15
    }
    
    user_preferences = {}
    meal_type = "lunch"
    
    print("🍽️ Testing Specific Ingredients Optimization")
    print("=" * 60)
    print("Ingredients: Chicken, Rice, Tomato")
    print(f"Target macros: {target_macros}")
    print(f"Meal type: {meal_type}")
    print()
    
    try:
        # Run optimization
        print("🔄 Running optimization...")
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
                if macro != 'overall':
                    status = "✅" if achieved else "❌"
                    print(f"  {macro}: {status}")
            print(f"  Overall: {'✅' if result['target_achievement']['overall'] else '❌'}")
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
            
            # Calculate total weight
            total_weight = sum(ingredient['quantity_needed'] for ingredient in result["meal"])
            print(f"\n⚖️ Total meal weight: {total_weight:.1f}g")
            
        else:
            print("❌ Optimization failed!")
            print(f"Error: {result['optimization_result'].get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

def test_different_targets():
    """Test with different target macro combinations"""
    print("\n🧪 Testing Different Target Combinations")
    print("=" * 50)
    
    optimizer = RAGMealOptimizer()
    
    # Same ingredients, different targets
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
    
    test_targets = [
        {"name": "High Protein", "macros": {"calories": 600, "protein": 40, "carbs": 40, "fat": 20}},
        {"name": "Low Carb", "macros": {"calories": 400, "protein": 35, "carbs": 25, "fat": 25}},
        {"name": "Balanced", "macros": {"calories": 500, "protein": 25, "carbs": 45, "fat": 15}},
        {"name": "High Energy", "macros": {"calories": 700, "protein": 25, "carbs": 70, "fat": 25}}
    ]
    
    for test_case in test_targets:
        print(f"\n🎯 Testing: {test_case['name']}")
        print(f"Targets: {test_case['macros']}")
        
        try:
            result = optimizer.optimize_single_meal(
                rag_response=rag_response,
                target_macros=test_case['macros'],
                user_preferences={},
                meal_type="lunch"
            )
            
            if result["success"]:
                print(f"✅ Success - Method: {result['optimization_result']['method']}")
                print(f"   Final weight: {sum(ing['quantity_needed'] for ing in result['meal']):.1f}g")
                
                # Check if targets achieved
                overall_achieved = result["target_achievement"]["overall"]
                status = "✅" if overall_achieved else "❌"
                print(f"   Targets achieved: {status}")
            else:
                print(f"❌ Failed: {result['optimization_result'].get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}...")

if __name__ == "__main__":
    test_specific_ingredients()
    test_different_targets()
