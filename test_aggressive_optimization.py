#!/usr/bin/env python3
"""
Test the aggressive optimization methods to ensure they reach target macros.
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_aggressive_optimization():
    """Test the aggressive optimization methods."""
    
    # Initialize the engine
    engine = RAGMealOptimizer()
    
    # Test data - Persian meal with target macros
    test_data = {
        "rag_response": {
            "ingredients": [
                {
                    "name": "برنج سفید",
                    "quantity_needed": 100,
                    "protein_per_100g": 2.7,
                    "carbs_per_100g": 28.0,
                    "fat_per_100g": 0.3,
                    "calories_per_100g": 130,
                    "max_quantity": 300
                },
                {
                    "name": "مرغ پخته",
                    "quantity_needed": 150,
                    "protein_per_100g": 31.0,
                    "carbs_per_100g": 0.0,
                    "fat_per_100g": 3.6,
                    "calories_per_100g": 165,
                    "max_quantity": 400
                },
                {
                    "name": "سبزیجات مخلوط",
                    "quantity_needed": 100,
                    "protein_per_100g": 2.0,
                    "carbs_per_100g": 4.0,
                    "fat_per_100g": 0.2,
                    "calories_per_100g": 25,
                    "max_quantity": 200
                }
            ]
        },
        "target_macros": {
            "calories": 800,
            "protein": 60,
            "carbs": 80,
            "fat": 25
        },
        "user_preferences": {
            "dietary_restrictions": [],
            "allergies": [],
            "cuisine_preference": "persian"
        },
        "meal_type": "lunch"
    }
    
    print("🧪 Testing Aggressive Optimization Methods")
    print("=" * 50)
    
    # Test the aggressive smart scaling method
    print("\n🎯 Testing Aggressive Smart Scaling...")
    try:
        result = engine._balance_by_smart_scaling(
            test_data["rag_response"]["ingredients"],
            test_data["target_macros"],
            {"protein": 20, "carbs": 30, "fat": 15}  # Simulated gaps
        )
        
        if result:
            print(f"✅ Method: {result['method']}")
            print(f"📊 Quantities: {result['quantities']}")
            
            # Calculate final nutrition
            final_nutrition = engine._calculate_final_meal(
                test_data["rag_response"]["ingredients"], 
                result['quantities']
            )
            print(f"🍽️ Final Nutrition: {final_nutrition}")
            
            # Check target achievement
            achievement = engine._check_target_achievement(final_nutrition, test_data["target_macros"])
            print(f"🎯 Target Achievement: {achievement}")
        else:
            print("❌ Method returned None")
            
    except Exception as e:
        print(f"❌ Error in smart scaling: {e}")
    
    # Test the ultra-aggressive method
    print("\n🚀🚀🚀 Testing Ultra-Aggressive Target Reach...")
    try:
        result = engine._balance_by_aggressive_target_reach(
            test_data["rag_response"]["ingredients"],
            test_data["target_macros"],
            {"protein": 20, "carbs": 30, "fat": 15}  # Simulated gaps
        )
        
        if result:
            print(f"✅ Method: {result['method']}")
            print(f"📊 Quantities: {result['quantities']}")
            
            # Calculate final nutrition
            final_nutrition = engine._calculate_final_meal(
                test_data["rag_response"]["ingredients"], 
                result['quantities']
            )
            print(f"🍽️ Final Nutrition: {final_nutrition}")
            
            # Check target achievement
            achievement = engine._check_target_achievement(final_nutrition, test_data["target_macros"])
            print(f"🎯 Target Achievement: {achievement}")
        else:
            print("❌ Method returned None")
            
    except Exception as e:
        print(f"❌ Error in ultra-aggressive method: {e}")
    
    # Test the full optimization pipeline
    print("\n🔄 Testing Full Optimization Pipeline...")
    try:
        result = engine.optimize_single_meal(
            test_data["rag_response"],
            test_data["target_macros"],
            test_data["user_preferences"],
            test_data["meal_type"]
        )
        
        if result and result.get("success"):
            print(f"✅ Optimization successful!")
            print(f"📊 Method: {result['optimization_result']['method']}")
            print(f"🍽️ Final Nutrition: {result['nutritional_totals']}")
            print(f"🎯 Target Achievement: {result['target_achievement']}")
            
            # Show the meal
            print(f"\n🍽️ Final Meal:")
            for ing in result['meal']:
                print(f"  - {ing['name']}: {ing['quantity_needed']}g")
        else:
            print(f"❌ Optimization failed: {result}")
            
    except Exception as e:
        print(f"❌ Error in full optimization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_aggressive_optimization()
