#!/usr/bin/env python3
"""
Test file for the advanced RAG optimization algorithm
Tests the 5 advanced optimization methods: PuLP, DEAP, SciPy, Hybrid, and Optuna
"""

from rag_optimization_engine import RAGMealOptimizer
import json

def test_rag_optimization():
    """Test the RAG optimization algorithm with advanced methods"""
    
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
    
    print("🚀 Testing Advanced RAG Optimization Algorithm")
    print("=" * 60)
    print(f"Target macros: {target_macros}")
    print(f"Meal type: {meal_type}")
    print()
    
    # Check which optimization libraries are available
    print("📚 Available Optimization Libraries:")
    print(f"  PuLP (Linear Optimization): {'✅' if hasattr(optimizer, '_linear_optimize_pulp') else '❌'}")
    print(f"  DEAP (Genetic Algorithm): {'✅' if hasattr(optimizer, '_genetic_algorithm_optimize') else '❌'}")
    print(f"  SciPy (Differential Evolution): {'✅' if hasattr(optimizer, '_differential_evolution_optimize') else '❌'}")
    print(f"  Hybrid (GA + DE): {'✅' if hasattr(optimizer, '_hybrid_optimize') else '❌'}")
    print(f"  Optuna: {'✅' if hasattr(optimizer, '_optuna_optimize') else '❌'}")
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
            
        else:
            print("❌ Optimization failed!")
            print(f"Error: {result['optimization_result'].get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        
        # Provide helpful installation instructions
        print("\n🔧 Installation Instructions:")
        print("To use all optimization methods, install the required libraries:")
        print("pip install -r requirements_advanced.txt")
        print("\nOr install individually:")
        print("pip install pulp deap scipy optuna numpy")

def test_individual_methods():
    """Test individual optimization methods to see which ones work"""
    print("\n🧪 Testing Individual Optimization Methods")
    print("=" * 50)
    
    optimizer = RAGMealOptimizer()
    
    # Simple test data
    ingredients = [
        {"name": "chicken", "protein_per_100g": 31, "carbs_per_100g": 0, "fat_per_100g": 3.6, "calories_per_100g": 165, "max_quantity": 200},
        {"name": "rice", "protein_per_100g": 2.7, "carbs_per_100g": 28, "fat_per_100g": 0.3, "calories_per_100g": 130, "max_quantity": 200}
    ]
    
    target_macros = {"calories": 400, "protein": 30, "carbs": 40, "fat": 10}
    
    methods_to_test = [
        ("Linear Optimization (PuLP)", optimizer._linear_optimize_pulp),
        ("Genetic Algorithm (DEAP)", optimizer._genetic_algorithm_optimize),
        ("Differential Evolution (SciPy)", optimizer._differential_evolution_optimize),
        ("Hybrid (GA + DE)", optimizer._hybrid_optimize),
        ("Optuna", optimizer._optuna_optimize)
    ]
    
    for method_name, method_func in methods_to_test:
        try:
            print(f"Testing {method_name}...", end=" ")
            result = method_func(ingredients, target_macros)
            if result['success']:
                print("✅ Success")
                print(f"    Method: {result['method']}")
                print(f"    Quantities: {[f'{q:.1f}g' for q in result['quantities']]}")
            else:
                print("❌ Failed")
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}...")
        print()

if __name__ == "__main__":
    test_rag_optimization()
    test_individual_methods()
