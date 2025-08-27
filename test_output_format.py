#!/usr/bin/env python3
"""
Test script to show the complete output format
"""

try:
    from rag_optimization_engine import RAGMealOptimizer
    print("✅ Successfully imported RAGMealOptimizer")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

def test_output_format():
    """Test to show the complete output format"""
    
    print("\n🧪 Testing Output Format")
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
                        }
                    ]
                }
            ],
            "success": True,
            "message": "Format test"
        },
        "target_macros": {
            "calories": 600,
            "protein": 50,
            "carbs": 60,
            "fat": 20
        },
        "user_preferences": {
            "diet_type": "balanced",
            "allergies": [],
            "preferences": []
        },
        "user_id": "format_test_user",
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
        
        print("✅ Format Test: Success")
        print("\n📋 COMPLETE OUTPUT FORMAT:")
        print("=" * 60)
        
        # Pretty print the result
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("\n🔍 STRUCTURE ANALYSIS:")
        print("=" * 40)
        
        # Analyze the structure
        print(f"✅ Success: {result.get('success', False)}")
        print(f"👤 User ID: {result.get('user_id', 'N/A')}")
        
        # Optimization result
        opt_result = result.get('optimization_result', {})
        print(f"🏆 Method: {opt_result.get('method', 'N/A')}")
        print(f"⏱️ Computation Time: {opt_result.get('computation_time', 0)}s")
        
        # Meal ingredients
        meal = result.get('meal', [])
        print(f"🍽️ Total Ingredients: {len(meal)}")
        for i, ingredient in enumerate(meal):
            print(f"   {i+1}. {ingredient['name']}: {ingredient['quantity_needed']}g")
        
        # Nutritional totals
        totals = result.get('nutritional_totals', {})
        print(f"\n📊 Nutritional Totals:")
        print(f"   Calories: {totals.get('calories', 0):.1f}")
        print(f"   Protein: {totals.get('protein', 0):.1f}g")
        print(f"   Carbs: {totals.get('carbs', 0):.1f}g")
        print(f"   Fat: {totals.get('fat', 0):.1f}g")
        
        # Target achievement
        achievement = result.get('target_achievement', {})
        print(f"\n🎯 Target Achievement:")
        print(f"   Calories: {'✅' if achievement.get('calories', False) else '❌'}")
        print(f"   Protein: {'✅' if achievement.get('protein', False) else '❌'}")
        print(f"   Carbs: {'✅' if achievement.get('carbs', False) else '❌'}")
        print(f"   Fat: {'✅' if achievement.get('fat', False) else '❌'}")
        print(f"   Overall: {'✅' if achievement.get('overall', False) else '❌'}")
        
    except Exception as e:
        print(f"❌ Format Test: Failed - {e}")

if __name__ == "__main__":
    print("🧪 Output Format Test Suite")
    print("=" * 60)
    
    test_output_format()
    
    print("\n🎉 Test completed!")
    print("\n💡 Use this format in your main site.")
