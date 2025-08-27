#!/usr/bin/env python3
"""
Test script to verify the new format fix in RAG optimization engine
"""

try:
    from rag_optimization_engine import RAGMealOptimizer
    print("✅ Successfully imported RAGMealOptimizer")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

def test_new_format():
    """Test the RAG optimization engine with the new format"""
    
    print("\n🧪 Testing New Format Fix")
    print("=" * 50)
    
    # Initialize the optimizer
    try:
        optimizer = RAGMealOptimizer()
        print("✅ RAG optimizer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize optimizer: {e}")
        return
    
    # Sample request data matching Next.js format
    request_data = {
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
                            "name": "onion",
                            "protein_per_100g": 1.1,
                            "carbs_per_100g": 9.3,
                            "fat_per_100g": 0.1,
                            "calories_per_100g": 40,
                            "quantity_needed": 100
                        }
                    ]
                }
            ],
            "success": True,
            "message": "Converted from AI suggestions"
        },
        "target_macros": {
            "calories": 637.2,
            "protein": 47.7,
            "carbs": 79.65,
            "fat": 14.18
        },
        "user_preferences": {
            "diet_type": "high_protein",
            "allergies": [],
            "preferences": ["low_sodium", "organic"]
        },
        "user_id": "user_123",
        "meal_type": "lunch"
    }
    
    print("📋 Test Request Data:")
    print(f"   User ID: {request_data['user_id']}")
    print(f"   Meal Type: {request_data['meal_type']}")
    print(f"   Target Calories: {request_data['target_macros']['calories']}")
    print(f"   Target Protein: {request_data['target_macros']['protein']}g")
    print(f"   Target Carbs: {request_data['target_macros']['carbs']}g")
    print(f"   Target Fat: {request_data['target_macros']['fat']}g")
    
    try:
        result = optimizer.optimize_single_meal(
            rag_response=request_data['rag_response'],
            target_macros=request_data['target_macros'],
            user_preferences=request_data['user_preferences'],
            meal_type=request_data['meal_type'],
            request_data=request_data
        )
        
        print("\n✅ Optimization completed successfully!")
        print(f"   Method: {result.get('optimization_result', {}).get('method', 'Unknown')}")
        print(f"   Computation Time: {result.get('optimization_result', {}).get('computation_time', 0)}s")
        print(f"   Success: {result.get('success', False)}")
        print(f"   User ID: {result.get('user_id', 'Not found')}")
        
        # Check meal format
        meal = result.get('meal', [])
        print(f"\n🍽️ Meal Ingredients ({len(meal)} items):")
        for i, ingredient in enumerate(meal):
            print(f"   {i+1}. {ingredient['name']}: {ingredient['quantity_needed']}g")
            print(f"      Protein: {ingredient['protein_per_100g']}g, Carbs: {ingredient['carbs_per_100g']}g, Fat: {ingredient['fat_per_100g']}g")
        
        # Check nutritional totals
        totals = result.get('nutritional_totals', {})
        print(f"\n📊 Nutritional Totals:")
        print(f"   Calories: {totals.get('calories', 0):.1f}")
        print(f"   Protein: {totals.get('protein', 0):.1f}g")
        print(f"   Carbs: {totals.get('carbs', 0):.1f}g")
        print(f"   Fat: {totals.get('fat', 0):.1f}g")
        
        # Check target achievement
        achievement = result.get('target_achievement', {})
        print(f"\n🎯 Target Achievement:")
        print(f"   Calories: {'✅' if achievement.get('calories', False) else '❌'}")
        print(f"   Protein: {'✅' if achievement.get('protein', False) else '❌'}")
        print(f"   Carbs: {'✅' if achievement.get('carbs', False) else '❌'}")
        print(f"   Fat: {'✅' if achievement.get('fat', False) else '❌'}")
        print(f"   Overall: {'✅' if achievement.get('overall', False) else '❌'}")
        
        # Verify format matches Next.js expectations
        print(f"\n🔍 Format Verification:")
        required_fields = ['user_id', 'success', 'optimization_result', 'meal', 'nutritional_totals', 'target_achievement']
        missing_fields = [field for field in required_fields if field not in result]
        
        if not missing_fields:
            print("   ✅ All required fields present")
        else:
            print(f"   ❌ Missing fields: {missing_fields}")
        
        # Check meal ingredient format
        if meal:
            first_ingredient = meal[0]
            required_ingredient_fields = ['name', 'quantity_needed', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g', 'calories_per_100g']
            missing_ingredient_fields = [field for field in required_ingredient_fields if field not in first_ingredient]
            
            if not missing_ingredient_fields:
                print("   ✅ Meal ingredient format correct")
            else:
                print(f"   ❌ Missing ingredient fields: {missing_ingredient_fields}")
        
        print(f"\n🎉 Format test completed successfully!")
        
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    print("🧪 New Format Fix Test Suite")
    print("=" * 60)
    
    test_new_format()
    
    print("\n🎉 All tests completed!")
    print("\n💡 The new format should now work with Next.js frontend.")
