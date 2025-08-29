#!/usr/bin/env python3
"""
Test script to verify the fix for the 'list' object has no attribute 'get' error
"""

from rag_optimization_engine import RAGMealOptimizer

def test_optimization():
    """Test the optimization without the fatal error"""
    print("🧪 Testing optimization fix...")
    
    try:
        # Create optimizer
        optimizer = RAGMealOptimizer()
        
        # Test data (similar to the error case)
        test_data = {
            'rag_response': {
                'ingredients': [
                    {
                        'name': 'Almonds',
                        'protein_per_100g': 20,
                        'carbs_per_100g': 20,
                        'fat_per_100g': 46.67,
                        'calories_per_100g': 533.33,
                        'quantity_needed': 100,
                        'max_quantity': 500
                    },
                    {
                        'name': 'Walnuts',
                        'protein_per_100g': 16.67,
                        'carbs_per_100g': 13.33,
                        'fat_per_100g': 66.67,
                        'calories_per_100g': 666.67,
                        'quantity_needed': 100,
                        'max_quantity': 500
                    }
                ]
            },
            'target_macros': {
                'calories': 283.2,
                'protein': 22.68,
                'carbs': 35.4,
                'fat': 6.68
            },
            'user_preferences': {
                'diet_type': 'high_protein',
                'allergies': [],
                'preferences': ['low_sodium', 'organic']
            },
            'meal_type': 'Morning Snack'
        }
        
        print("✅ Test data created successfully")
        
        # Test the optimization
        result = optimizer.optimize_single_meal(
            rag_response=test_data['rag_response'],
            target_macros=test_data['target_macros'],
            user_preferences=test_data['user_preferences'],
            meal_type=test_data['meal_type'],
            request_data=test_data
        )
        
        print("✅ Optimization completed successfully!")
        print(f"📊 Result type: {type(result)}")
        
        if isinstance(result, dict):
            print(f"📋 Result keys: {list(result.keys())}")
            if 'ingredients' in result:
                print(f"🍽️ Number of ingredients: {len(result['ingredients'])}")
            if 'achievement' in result:
                print(f"🎯 Achievement: {result['achievement']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing optimization fix...\n")
    
    success = test_optimization()
    
    print("\n" + "="*50)
    if success:
        print("🎉 Test passed! The fix is working.")
    else:
        print("❌ Test failed. There are still issues.")
    print("="*50)
