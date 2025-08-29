#!/usr/bin/env python3
"""
Test to verify that helpers and balancing are now added even when overall is True
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_final_fix():
    """Test that helpers and balancing are added even when overall is True."""
    
    print("🧪 Testing Final Fix - Helpers + Balancing Always Added...")
    print("=" * 50)
    
    optimizer = RAGMealOptimizer()
    
    # Same scenario
    target_macros = {
        'calories': 637.2,
        'protein': 45.4,
        'carbs': 88.5,
        'fat': 13.7
    }
    
    ingredients = [
        {
            'name': 'Ground Beef',
            'protein_per_100g': 20,
            'carbs_per_100g': 0,
            'fat_per_100g': 15,
            'calories_per_100g': 200,
            'quantity_needed': 100,
            'max_quantity': 500
        },
        {
            'name': 'Onion',
            'protein_per_100g': 1,
            'carbs_per_100g': 9,
            'fat_per_100g': 0,
            'calories_per_100g': 40,
            'quantity_needed': 100,
            'max_quantity': 500
        },
        {
            'name': 'Pita Bread',
            'protein_per_100g': 8,
            'carbs_per_100g': 54,
            'fat_per_100g': 2,
            'calories_per_100g': 280,
            'quantity_needed': 100,
            'max_quantity': 500
        },
        {
            'name': 'Grilled Tomato',
            'protein_per_100g': 1,
            'carbs_per_100g': 5,
            'fat_per_100g': 0,
            'calories_per_100g': 20,
            'quantity_needed': 100,
            'max_quantity': 500
        }
    ]
    
    print("🚀 Starting optimization...")
    print("-" * 30)
    
    try:
        result = optimizer.optimize_single_meal(
            rag_response={'ingredients': ingredients},
            target_macros=target_macros,
            meal_type='lunch',
            user_preferences={}
        )
        
        print("\n✅ Optimization completed!")
        print("=" * 50)
        
        # Show results
        if 'meal' in result:
            print("🍽️ Final Meal:")
            for ing in result['meal']:
                print(f"   {ing['name']}: {ing['quantity_needed']}g")
        
        if 'helper_ingredients_added' in result and result['helper_ingredients_added']:
            print(f"\n🔧 Helper Ingredients Added ({len(result['helper_ingredients_added'])}):")
            for helper in result['helper_ingredients_added']:
                print(f"   {helper['name']}: {helper['quantity_needed']}g")
        else:
            print("\n❌ No helper ingredients were added!")
        
        if 'balancing_ingredients_added' in result and result['balancing_ingredients_added']:
            print(f"\n⚖️ Balancing Ingredients Added ({len(result['balancing_ingredients_added'])}):")
            for balancer in result['balancing_ingredients_added']:
                print(f"   {balancer['name']}: {balancer['quantity_needed']}g")
        else:
            print("\n❌ No balancing ingredients were added!")
        
        # Show final totals
        if 'final_totals' in result:
            print(f"\n📊 Final Totals:")
            for macro, value in result['final_totals'].items():
                target = target_macros.get(macro, 0)
                diff = value - target
                status = "✅" if abs(diff) <= target * 0.1 else "❌"
                print(f"   {macro}: {value:.1f} (target: {target:.1f}, diff: {diff:+.1f}) {status}")
        
        # Show target achievement
        if 'target_achievement' in result:
            print(f"\n🎯 Target Achievement:")
            for macro, achieved in result['target_achievement'].items():
                status = "✅" if achieved else "❌"
                print(f"   {macro}: {status}")
        
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_fix()
