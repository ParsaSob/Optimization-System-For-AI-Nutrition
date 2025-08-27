#!/usr/bin/env python3
"""
Test script to test ingredient optimization with real ingredients
"""

try:
    from rag_optimization_engine import RAGMealOptimizer
    print("✅ Successfully imported RAGMealOptimizer")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

def test_ingredient_optimization():
    """Test ingredient optimization with real ingredients"""
    
    print("\n🧪 Testing Ingredient Optimization")
    print("=" * 50)
    
    # Initialize the optimizer
    try:
        optimizer = RAGMealOptimizer()
        print("✅ RAG optimizer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize optimizer: {e}")
        return
    
    # Test Case 1: High Protein Meal
    print("\n📋 Test Case 1: High Protein Meal")
    print("-" * 40)
    
    high_protein_request = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "chicken_breast",
                            "protein_per_100g": 31,
                            "carbs_per_100g": 0,
                            "fat_per_100g": 3.6,
                            "calories_per_100g": 165,
                            "quantity_needed": 150
                        },
                        {
                            "name": "broccoli",
                            "protein_per_100g": 2.8,
                            "carbs_per_100g": 7,
                            "fat_per_100g": 0.4,
                            "calories_per_100g": 34,
                            "quantity_needed": 100
                        }
                    ]
                }
            ],
            "success": True,
            "message": "High protein meal suggestion"
        },
        "target_macros": {
            "calories": 800,
            "protein": 80,
            "carbs": 60,
            "fat": 25
        },
        "user_preferences": {
            "diet_type": "high_protein",
            "allergies": [],
            "preferences": ["low_fat", "high_fiber"]
        },
        "user_id": "protein_user",
        "meal_type": "dinner"
    }
    
    try:
        result = optimizer.optimize_single_meal(
            rag_response=high_protein_request['rag_response'],
            target_macros=high_protein_request['target_macros'],
            user_preferences=high_protein_request['user_preferences'],
            meal_type=high_protein_request['meal_type'],
            request_data=high_protein_request
        )
        
        print("✅ High Protein Optimization: Success")
        print(f"   Method: {result.get('optimization_result', {}).get('method', 'Unknown')}")
        print(f"   Computation Time: {result.get('optimization_result', {}).get('computation_time', 0)}s")
        
        # Show meal details
        meal = result.get('meal', [])
        print(f"\n🍽️ Final Meal ({len(meal)} ingredients):")
        for i, ingredient in enumerate(meal):
            print(f"   {i+1}. {ingredient['name']}: {ingredient['quantity_needed']}g")
            print(f"      Protein: {ingredient['protein_per_100g']}g, Carbs: {ingredient['carbs_per_100g']}g, Fat: {ingredient['fat_per_100g']}g")
        
        # Show nutritional totals
        totals = result.get('nutritional_totals', {})
        print(f"\n📊 Nutritional Totals:")
        print(f"   Calories: {totals.get('calories', 0):.1f}")
        print(f"   Protein: {totals.get('protein', 0):.1f}g")
        print(f"   Carbs: {totals.get('carbs', 0):.1f}g")
        print(f"   Fat: {totals.get('fat', 0):.1f}g")
        
        # Show target achievement
        achievement = result.get('target_achievement', {})
        print(f"\n🎯 Target Achievement:")
        print(f"   Calories: {'✅' if achievement.get('calories', False) else '❌'}")
        print(f"   Protein: {'✅' if achievement.get('protein', False) else '❌'}")
        print(f"   Carbs: {'✅' if achievement.get('carbs', False) else '❌'}")
        print(f"   Fat: {'✅' if achievement.get('fat', False) else '❌'}")
        print(f"   Overall: {'✅' if achievement.get('overall', False) else '❌'}")
        
    except Exception as e:
        print(f"❌ High Protein Optimization: Failed - {e}")
    
    # Test Case 2: Balanced Meal
    print("\n📋 Test Case 2: Balanced Meal")
    print("-" * 40)
    
    balanced_request = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "salmon",
                            "protein_per_100g": 25,
                            "carbs_per_100g": 0,
                            "fat_per_100g": 12,
                            "calories_per_100g": 208,
                            "quantity_needed": 120
                        },
                        {
                            "name": "quinoa",
                            "protein_per_100g": 4.4,
                            "carbs_per_100g": 22,
                            "fat_per_100g": 1.9,
                            "calories_per_100g": 120,
                            "quantity_needed": 80
                        },
                        {
                            "name": "spinach",
                            "protein_per_100g": 2.9,
                            "carbs_per_100g": 3.6,
                            "fat_per_100g": 0.4,
                            "calories_per_100g": 23,
                            "quantity_needed": 50
                        }
                    ]
                }
            ],
            "success": True,
            "message": "Balanced meal suggestion"
        },
        "target_macros": {
            "calories": 600,
            "protein": 45,
            "carbs": 70,
            "fat": 20
        },
        "user_preferences": {
            "diet_type": "balanced",
            "allergies": [],
            "preferences": ["organic", "gluten_free"]
        },
        "user_id": "balanced_user",
        "meal_type": "lunch"
    }
    
    try:
        result = optimizer.optimize_single_meal(
            rag_response=balanced_request['rag_response'],
            target_macros=balanced_request['target_macros'],
            user_preferences=balanced_request['user_preferences'],
            meal_type=balanced_request['meal_type'],
            request_data=balanced_request
        )
        
        print("✅ Balanced Meal Optimization: Success")
        print(f"   Method: {result.get('optimization_result', {}).get('method', 'Unknown')}")
        print(f"   Computation Time: {result.get('optimization_result', {}).get('computation_time', 0)}s")
        
        # Show meal details
        meal = result.get('meal', [])
        print(f"\n🍽️ Final Meal ({len(meal)} ingredients):")
        for i, ingredient in enumerate(meal):
            print(f"   {i+1}. {ingredient['name']}: {ingredient['quantity_needed']}g")
            print(f"      Protein: {ingredient['protein_per_100g']}g, Carbs: {ingredient['carbs_per_100g']}g, Fat: {ingredient['fat_per_100g']}g")
        
        # Show nutritional totals
        totals = result.get('nutritional_totals', {})
        print(f"\n📊 Nutritional Totals:")
        print(f"   Calories: {totals.get('calories', 0):.1f}")
        print(f"   Protein: {totals.get('protein', 0):.1f}g")
        print(f"   Carbs: {totals.get('carbs', 0):.1f}g")
        print(f"   Fat: {totals.get('fat', 0):.1f}g")
        
        # Show target achievement
        achievement = result.get('target_achievement', {})
        print(f"\n🎯 Target Achievement:")
        print(f"   Calories: {'✅' if achievement.get('calories', False) else '❌'}")
        print(f"   Protein: {'✅' if achievement.get('protein', False) else '❌'}")
        print(f"   Carbs: {'✅' if achievement.get('carbs', False) else '❌'}")
        print(f"   Fat: {'✅' if achievement.get('fat', False) else '❌'}")
        print(f"   Overall: {'✅' if achievement.get('overall', False) else '❌'}")
        
    except Exception as e:
        print(f"❌ Balanced Meal Optimization: Failed - {e}")
    
    # Test Case 3: Low Carb Meal
    print("\n📋 Test Case 3: Low Carb Meal")
    print("-" * 40)
    
    low_carb_request = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "eggs",
                            "protein_per_100g": 13,
                            "carbs_per_100g": 1.1,
                            "fat_per_100g": 11,
                            "calories_per_100g": 155,
                            "quantity_needed": 100
                        },
                        {
                            "name": "avocado",
                            "protein_per_100g": 2,
                            "carbs_per_100g": 9,
                            "fat_per_100g": 15,
                            "calories_per_100g": 160,
                            "quantity_needed": 80
                        },
                        {
                            "name": "almonds",
                            "protein_per_100g": 21,
                            "carbs_per_100g": 22,
                            "fat_per_100g": 49,
                            "calories_per_100g": 579,
                            "quantity_needed": 30
                        }
                    ]
                }
            ],
            "success": True,
            "message": "Low carb meal suggestion"
        },
        "target_macros": {
            "calories": 500,
            "protein": 35,
            "carbs": 25,
            "fat": 35
        },
        "user_preferences": {
            "diet_type": "keto",
            "allergies": [],
            "preferences": ["high_fat", "low_carb"]
        },
        "user_id": "keto_user",
        "meal_type": "breakfast"
    }
    
    try:
        result = optimizer.optimize_single_meal(
            rag_response=low_carb_request['rag_response'],
            target_macros=low_carb_request['target_macros'],
            user_preferences=low_carb_request['user_preferences'],
            meal_type=low_carb_request['meal_type'],
            request_data=low_carb_request
        )
        
        print("✅ Low Carb Optimization: Success")
        print(f"   Method: {result.get('optimization_result', {}).get('method', 'Unknown')}")
        print(f"   Computation Time: {result.get('optimization_result', {}).get('computation_time', 0)}s")
        
        # Show meal details
        meal = result.get('meal', [])
        print(f"\n🍽️ Final Meal ({len(meal)} ingredients):")
        for i, ingredient in enumerate(meal):
            print(f"   {i+1}. {ingredient['name']}: {ingredient['quantity_needed']}g")
            print(f"      Protein: {ingredient['protein_per_100g']}g, Carbs: {ingredient['carbs_per_100g']}g, Fat: {ingredient['fat_per_100g']}g")
        
        # Show nutritional totals
        totals = result.get('nutritional_totals', {})
        print(f"\n📊 Nutritional Totals:")
        print(f"   Calories: {totals.get('calories', 0):.1f}")
        print(f"   Protein: {totals.get('protein', 0):.1f}g")
        print(f"   Carbs: {totals.get('carbs', 0):.1f}g")
        print(f"   Fat: {totals.get('fat', 0):.1f}g")
        
        # Show target achievement
        achievement = result.get('target_achievement', {})
        print(f"\n🎯 Target Achievement:")
        print(f"   Calories: {'✅' if achievement.get('calories', False) else '❌'}")
        print(f"   Protein: {'✅' if achievement.get('protein', False) else '❌'}")
        print(f"   Carbs: {'✅' if achievement.get('carbs', False) else '❌'}")
        print(f"   Fat: {'✅' if achievement.get('fat', False) else '❌'}")
        print(f"   Overall: {'✅' if achievement.get('overall', False) else '❌'}")
        
    except Exception as e:
        print(f"❌ Low Carb Optimization: Failed - {e}")
    
    # Test Case 4: Vegetarian Meal
    print("\n📋 Test Case 4: Vegetarian Meal")
    print("-" * 40)
    
    vegetarian_request = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "lentils",
                            "protein_per_100g": 9,
                            "carbs_per_100g": 20,
                            "fat_per_100g": 0.4,
                            "calories_per_100g": 116,
                            "quantity_needed": 100
                        },
                        {
                            "name": "brown_rice",
                            "protein_per_100g": 2.7,
                            "carbs_per_100g": 23,
                            "fat_per_100g": 0.9,
                            "calories_per_100g": 111,
                            "quantity_needed": 80
                        },
                        {
                            "name": "tofu",
                            "protein_per_100g": 8,
                            "carbs_per_100g": 1.9,
                            "fat_per_100g": 4.8,
                            "calories_per_100g": 76,
                            "quantity_needed": 120
                        }
                    ]
                }
            ],
            "success": True,
            "message": "Vegetarian meal suggestion"
        },
        "target_macros": {
            "calories": 700,
            "protein": 40,
            "carbs": 100,
            "fat": 15
        },
        "user_preferences": {
            "diet_type": "vegetarian",
            "allergies": [],
            "preferences": ["plant_based", "high_fiber"]
        },
        "user_id": "veggie_user",
        "meal_type": "dinner"
    }
    
    try:
        result = optimizer.optimize_single_meal(
            rag_response=vegetarian_request['rag_response'],
            target_macros=vegetarian_request['target_macros'],
            user_preferences=vegetarian_request['user_preferences'],
            meal_type=vegetarian_request['meal_type'],
            request_data=vegetarian_request
        )
        
        print("✅ Vegetarian Optimization: Success")
        print(f"   Method: {result.get('optimization_result', {}).get('method', 'Unknown')}")
        print(f"   Computation Time: {result.get('optimization_result', {}).get('computation_time', 0)}s")
        
        # Show meal details
        meal = result.get('meal', [])
        print(f"\n🍽️ Final Meal ({len(meal)} ingredients):")
        for i, ingredient in enumerate(meal):
            print(f"   {i+1}. {ingredient['name']}: {ingredient['quantity_needed']}g")
            print(f"      Protein: {ingredient['protein_per_100g']}g, Carbs: {ingredient['carbs_per_100g']}g, Fat: {ingredient['fat_per_100g']}g")
        
        # Show nutritional totals
        totals = result.get('nutritional_totals', {})
        print(f"\n📊 Nutritional Totals:")
        print(f"   Calories: {totals.get('calories', 0):.1f}")
        print(f"   Protein: {totals.get('protein', 0):.1f}g")
        print(f"   Carbs: {totals.get('carbs', 0):.1f}g")
        print(f"   Fat: {totals.get('fat', 0):.1f}g")
        
        # Show target achievement
        achievement = result.get('target_achievement', {})
        print(f"\n🎯 Target Achievement:")
        print(f"   Calories: {'✅' if achievement.get('calories', False) else '❌'}")
        print(f"   Protein: {'✅' if achievement.get('protein', False) else '❌'}")
        print(f"   Carbs: {'✅' if achievement.get('carbs', False) else '❌'}")
        print(f"   Fat: {'✅' if achievement.get('fat', False) else '❌'}")
        print(f"   Overall: {'✅' if achievement.get('overall', False) else '❌'}")
        
    except Exception as e:
        print(f"❌ Vegetarian Optimization: Failed - {e}")

def test_optimization_algorithms():
    """Test different optimization algorithms"""
    
    print("\n🧪 Testing Optimization Algorithms")
    print("=" * 50)
    
    # Initialize the optimizer
    try:
        optimizer = RAGMealOptimizer()
        print("✅ RAG optimizer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize optimizer: {e}")
        return
    
    # Simple test case
    test_request = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "chicken_breast",
                            "protein_per_100g": 31,
                            "carbs_per_100g": 0,
                            "fat_per_100g": 3.6,
                            "calories_per_100g": 165,
                            "quantity_needed": 100
                        },
                        {
                            "name": "sweet_potato",
                            "protein_per_100g": 1.6,
                            "carbs_per_100g": 20,
                            "fat_per_100g": 0.1,
                            "calories_per_100g": 86,
                            "quantity_needed": 100
                        }
                    ]
                }
            ],
            "success": True,
            "message": "Algorithm test"
        },
        "target_macros": {
            "calories": 400,
            "protein": 35,
            "carbs": 45,
            "fat": 8
        },
        "user_preferences": {
            "diet_type": "balanced",
            "allergies": [],
            "preferences": []
        },
        "user_id": "test_user",
        "meal_type": "lunch"
    }
    
    try:
        result = optimizer.optimize_single_meal(
            rag_response=test_request['rag_response'],
            target_macros=test_request['target_macros'],
            user_preferences=test_request['user_preferences'],
            meal_type=test_request['meal_type'],
            request_data=test_request
        )
        
        print("✅ Algorithm Test: Success")
        print(f"   Method: {result.get('optimization_result', {}).get('method', 'Unknown')}")
        print(f"   Computation Time: {result.get('optimization_result', {}).get('computation_time', 0)}s")
        
        # Show which algorithm was selected
        method = result.get('optimization_result', {}).get('method', 'Unknown')
        print(f"\n🏆 Selected Algorithm: {method}")
        
        if 'Linear' in method:
            print("   📊 Linear Optimization (PuLP) - Fast and reliable for simple constraints")
        elif 'Differential Evolution' in method:
            print("   🧬 Differential Evolution - Good for complex, non-linear problems")
        elif 'Genetic Algorithm' in method:
            print("   🧬 Genetic Algorithm - Evolutionary approach for complex optimization")
        elif 'Optuna' in method:
            print("   🔍 Optuna - Hyperparameter optimization framework")
        elif 'Hybrid' in method:
            print("   🔄 Hybrid - Combination of multiple algorithms")
        else:
            print("   🔄 Fallback - Simple scaling method")
        
    except Exception as e:
        print(f"❌ Algorithm Test: Failed - {e}")

if __name__ == "__main__":
    print("🧪 Ingredient Optimization Test Suite")
    print("=" * 60)
    
    # Test ingredient optimization
    test_ingredient_optimization()
    
    # Test optimization algorithms
    test_optimization_algorithms()
    
    print("\n🎉 All tests completed!")
    print("\n💡 The optimizer should handle different meal types and dietary preferences.")
    print("💡 Different optimization algorithms will be selected based on the problem complexity.")
