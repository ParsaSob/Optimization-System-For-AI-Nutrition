#!/usr/bin/env python3
"""
Test Advanced RAG Optimization Algorithms
Testing all available optimization methods
"""

import json
import time
import numpy as np

def test_advanced_algorithms():
    """Test all available advanced optimization algorithms"""
    
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
    
    print("🧪 Testing Advanced RAG Optimization Algorithms")
    print("=" * 70)
    
    try:
        from rag_optimization_engine import RAGMealOptimizer
        
        print("📍 Testing local system...")
        optimizer = RAGMealOptimizer()
        
        # Test each optimization method individually
        test_methods = [
            'genetic_algorithm',
            'differential_evolution', 
            'linear_programming',
            'hybrid'
        ]
        
        # Add advanced methods if available
        if hasattr(optimizer, '_optimize_optuna'):
            test_methods.append('optuna_optimization')
        if hasattr(optimizer, '_optimize_pygmo'):
            test_methods.append('pygmo_optimization')
        if hasattr(optimizer, '_optimize_nsga2'):
            test_methods.append('nsga2_optimization')
        if hasattr(optimizer, '_optimize_pymoo'):
            test_methods.append('pymoo_optimization')
        
        print(f"🔧 Available optimization methods: {len(test_methods)}")
        print(f"📋 Methods: {', '.join(test_methods)}")
        print()
        
        # Test each method
        results = {}
        for method in test_methods:
            print(f"🧪 Testing {method}...")
            
            try:
                # Temporarily set only this method
                original_methods = optimizer.optimization_methods.copy()
                optimizer.optimization_methods = {method: original_methods[method]}
                
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
                
                if result.get('optimization_result', {}).get('success', False):
                    print(f"✅ {method}: SUCCESS in {computation_time:.3f}s")
                    results[method] = {
                        'success': True,
                        'time': computation_time,
                        'method_used': result['optimization_result']['method'],
                        'target_achieved': result['optimization_result']['target_achieved']
                    }
                else:
                    print(f"❌ {method}: FAILED")
                    results[method] = {
                        'success': False,
                        'time': computation_time,
                        'error': result.get('optimization_result', {}).get('error', 'Unknown error')
                    }
                    
            except Exception as e:
                print(f"❌ {method}: ERROR - {str(e)}")
                results[method] = {
                    'success': False,
                    'time': 0,
                    'error': str(e)
                }
            
            print()
        
        # Summary
        print("📊 OPTIMIZATION METHODS SUMMARY")
        print("-" * 50)
        
        successful_methods = [m for m, r in results.items() if r['success']]
        failed_methods = [m for m, r in results.items() if not r['success']]
        
        print(f"✅ Successful methods: {len(successful_methods)}")
        for method in successful_methods:
            result = results[method]
            print(f"   • {method}: {result['time']:.3f}s, Target: {'✅' if result['target_achieved'] else '❌'}")
        
        print(f"❌ Failed methods: {len(failed_methods)}")
        for method in failed_methods:
            result = results[method]
            print(f"   • {method}: {result.get('error', 'Unknown error')}")
        
        print()
        
        # Test ML-based supplementation
        print("🤖 Testing Machine Learning Features...")
        try:
            # Test ML quantity prediction
            test_ingredient = {
                'name': 'Chicken Breast',
                'calories_per_100g': 165,
                'protein_per_100g': 31,
                'carbs_per_100g': 0,
                'fat_per_100g': 3.6
            }
            
            predicted_quantity = optimizer._predict_optimal_quantity(test_ingredient, 'protein', 20)
            print(f"   • ML Quantity Prediction: {predicted_quantity:.1f}g")
            
            # Test ML compatibility score
            existing_profile = np.array([200, 20, 0, 15])  # Ground Beef profile
            compatibility_score = optimizer._calculate_ml_compatibility_score(
                test_ingredient, existing_profile, 'protein'
            )
            print(f"   • ML Compatibility Score: {compatibility_score:.3f}")
            
            print("✅ Machine Learning features working")
            
        except Exception as e:
            print(f"❌ Machine Learning features failed: {e}")
        
        print()
        
        # Final hybrid test
        print("🔄 Testing Hybrid Optimization...")
        try:
            start_time = time.time()
            final_result = optimizer.optimize_single_meal(
                rag_response=rag_response,
                target_macros=target_macros,
                user_preferences=user_preferences,
                meal_type="lunch"
            )
            computation_time = time.time() - start_time
            
            if final_result.get('optimization_result', {}).get('success', False):
                print(f"✅ Hybrid optimization successful in {computation_time:.3f}s")
                print(f"🔧 Method used: {final_result['optimization_result']['method']}")
                print(f"🎯 Target achieved: {final_result['optimization_result']['target_achieved']}")
                
                # Show final meal
                meal = final_result.get('meal', {})
                if meal:
                    print(f"🍽️ Final meal: {meal.get('total_calories', 0)} cal, {meal.get('total_protein', 0)}g protein")
                    
            else:
                print(f"❌ Hybrid optimization failed: {final_result.get('optimization_result', {}).get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Hybrid optimization error: {e}")
        
    except Exception as e:
        print(f"❌ System test failed: {e}")

if __name__ == "__main__":
    test_advanced_algorithms()
