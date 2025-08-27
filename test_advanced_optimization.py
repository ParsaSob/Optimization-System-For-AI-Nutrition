#!/usr/bin/env python3
"""
Test script for the advanced optimization algorithms in RAG Meal Optimizer
"""

import json
import time
from rag_optimization_engine import RAGMealOptimizer

def test_advanced_optimization():
    """Test the advanced optimization algorithms"""
    
    # Initialize the optimizer
    optimizer = RAGMealOptimizer()
    
    # Sample RAG response (simulating what would come from RAG system)
    rag_response = {
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
                        "name": "brown_rice",
                        "protein_per_100g": 2.7,
                        "carbs_per_100g": 23,
                        "fat_per_100g": 0.9,
                        "calories_per_100g": 111,
                        "quantity_needed": 100
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
        ]
    }
    
    # Target macros (example: high protein, moderate carbs, low fat)
    target_macros = {
        "calories": 800,
        "protein": 60,
        "carbs": 80,
        "fat": 25
    }
    
    # User preferences
    user_preferences = {
        "diet_type": "high_protein",
        "allergies": [],
        "preferences": ["low_sodium", "organic"]
    }
    
    print("🚀 Testing Advanced Optimization Algorithms")
    print("=" * 50)
    print(f"Target Macros: {target_macros}")
    print(f"RAG Ingredients: {len(rag_response['suggestions'][0]['ingredients'])}")
    print()
    
    try:
        # Run optimization
        start_time = time.time()
        result = optimizer.optimize_single_meal(
            rag_response, 
            target_macros, 
            user_preferences, 
            "lunch"
        )
        end_time = time.time()
        
        # Display results
        print("✅ Optimization Completed Successfully!")
        print(f"⏱️  Computation Time: {result['optimization_result']['computation_time']}s")
        print(f"🏆 Best Algorithm: {result['optimization_result']['method']}")
        print()
        
        print("📊 Final Meal Composition:")
        print("-" * 40)
        
        # Display RAG ingredients
        print("🥘 RAG Ingredients:")
        for ingredient in result['meal'][:len(rag_response['suggestions'][0]['ingredients'])]:
            print(f"  • {ingredient['name']}: {ingredient.get('quantity_needed', 100):.1f}g")
        
        # Display supplementary ingredients
        if len(result['meal']) > len(rag_response['suggestions'][0]['ingredients']):
            print("\n➕ Supplementary Ingredients:")
            for ingredient in result['meal'][len(rag_response['suggestions'][0]['ingredients']):]:
                print(f"  • {ingredient['name']}: {ingredient.get('quantity_needed', 100):.1f}g")
        
        print()
        print("📈 Nutritional Totals:")
        print("-" * 40)
        totals = result['nutritional_totals']
        print(f"🔥 Calories: {totals['calories']:.1f} / {target_macros['calories']}")
        print(f"🥩 Protein: {totals['protein']:.1f}g / {target_macros['protein']}g")
        print(f"🍞 Carbs: {totals['carbs']:.1f}g / {target_macros['carbs']}g")
        print(f"🥑 Fat: {totals['fat']:.1f}g / {target_macros['fat']}g")
        
        print()
        print("🎯 Target Achievement:")
        print("-" * 40)
        achievement = result['target_achievement']
        for macro, achieved in achievement.items():
            if macro != 'overall':
                status = "✅" if achieved else "❌"
                print(f"{status} {macro.capitalize()}: {'Achieved' if achieved else 'Not Achieved'}")
        
        print(f"\n🎯 Overall: {'✅ All Targets Achieved' if achievement['overall'] else '❌ Some Targets Not Met'}")
        
        # Performance analysis
        print()
        print("⚡ Performance Analysis:")
        print("-" * 40)
        print(f"• Total Ingredients: {len(result['meal'])}")
        print(f"• RAG Ingredients: {len(rag_response['suggestions'][0]['ingredients'])}")
        print(f"• Supplementary Ingredients: {len(result['meal']) - len(rag_response['suggestions'][0]['ingredients'])}")
        print(f"• Optimization Time: {result['optimization_result']['computation_time']}s")
        
        # Check if realistic quantities were used
        print()
        print("🔍 Quantity Validation:")
        print("-" * 40)
        realistic = True
        for ingredient in result['meal']:
            qty = ingredient.get('quantity_needed', 100)
            max_qty = ingredient.get('max_quantity', 200)
            if qty > max_qty:
                print(f"⚠️  {ingredient['name']}: {qty:.1f}g exceeds max {max_qty}g")
                realistic = False
            else:
                print(f"✅ {ingredient['name']}: {qty:.1f}g (max: {max_qty}g)")
        
        if realistic:
            print("\n🎉 All quantities are within realistic limits!")
        else:
            print("\n⚠️  Some quantities exceed realistic limits!")
        
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        import traceback
        traceback.print_exc()

def test_different_targets():
    """Test with different target macro combinations"""
    
    print("\n" + "="*60)
    print("🧪 Testing Different Target Combinations")
    print("="*60)
    
    optimizer = RAGMealOptimizer()
    
    # Test cases
    test_cases = [
        {
            "name": "High Protein, Low Carb",
            "targets": {"calories": 600, "protein": 80, "carbs": 30, "fat": 20}
        },
        {
            "name": "Balanced Macros",
            "targets": {"calories": 700, "protein": 50, "carbs": 70, "fat": 30}
        },
        {
            "name": "High Carb, Low Fat",
            "targets": {"calories": 800, "protein": 40, "carbs": 100, "fat": 15}
        }
    ]
    
    # Simple RAG response for testing
    rag_response = {
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
                    }
                ]
            }
        ]
    }
    
    user_preferences = {"diet_type": "balanced", "allergies": [], "preferences": []}
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        print(f"Targets: {test_case['targets']}")
        
        try:
            start_time = time.time()
            result = optimizer.optimize_single_meal(
                rag_response, 
                test_case['targets'], 
                user_preferences, 
                "test"
            )
            end_time = time.time()
            
            print(f"✅ Success: {result['optimization_result']['method']}")
            print(f"⏱️  Time: {result['optimization_result']['computation_time']}s")
            print(f"🎯 Achievement: {result['target_achievement']['overall']}")
            
            # Show key results
            totals = result['nutritional_totals']
            print(f"📊 Results: {totals['calories']:.0f}cal, {totals['protein']:.0f}g protein, {totals['carbs']:.0f}g carbs, {totals['fat']:.0f}g fat")
            
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    print("🧪 Advanced Optimization Algorithm Test Suite")
    print("=" * 60)
    
    # Test main optimization
    test_advanced_optimization()
    
    # Test different target combinations
    test_different_targets()
    
    print("\n🎉 Testing completed!")
    print("\n💡 The system now uses advanced optimization algorithms:")
    print("   • Linear Optimization (PuLP)")
    print("   • Differential Evolution (SciPy)")
    print("   • Genetic Algorithm")
    print("   • Optuna Optimization")
    print("   • Hybrid Optimization (DE + GA)")
    print("   • Intelligent ingredient selection with realistic limits")
