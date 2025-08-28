from rag_optimization_engine import RAGMealOptimizer
import json

def test_full_optimization():
    """Test the full optimization workflow with all new balancing strategies."""
    print("🧪 Testing Full Optimization with Learning Algorithms...")
    
    optimizer = RAGMealOptimizer()
    
    # Test input with the format you specified
    test_input = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "Ground Beef",
                            "protein_per_100g": 26,
                            "carbs_per_100g": 0,
                            "fat_per_100g": 15,
                            "calories_per_100g": 250,
                            "quantity_needed": 150,
                            "max_quantity": 200
                        },
                        {
                            "name": "Onion",
                            "protein_per_100g": 1.1,
                            "carbs_per_100g": 9,
                            "fat_per_100g": 0.1,
                            "calories_per_100g": 40,
                            "quantity_needed": 50,
                            "max_quantity": 100
                        },
                        {
                            "name": "Pita Bread",
                            "protein_per_100g": 9,
                            "carbs_per_100g": 55,
                            "fat_per_100g": 1.2,
                            "calories_per_100g": 275,
                            "quantity_needed": 80,
                            "max_quantity": 120
                        }
                    ]
                }
            ],
            "success": True,
            "message": "Test meal suggestion"
        },
        "target_macros": {
            "calories": 800,
            "protein": 40,
            "carbs": 60,
            "fat": 30
        },
        "user_preferences": {
            "diet_type": "balanced",
            "allergies": [],
            "preferences": []
        },
        "user_id": "test_user",
        "meal_type": "lunch"
    }
    
    print("\n📊 Input Data:")
    print(f"Target Macros: {test_input['target_macros']}")
    print(f"Meal Type: {test_input['meal_type']}")
    print(f"Ingredients: {len(test_input['rag_response']['suggestions'][0]['ingredients'])}")
    
    try:
        # Run the full optimization
        result = optimizer.optimize_single_meal(
            rag_response=test_input['rag_response'],
            target_macros=test_input['target_macros'],
            user_preferences=test_input['user_preferences'],
            meal_type=test_input['meal_type'],
            request_data=test_input
        )
        
        print("\n✅ Optimization Result:")
        print(f"Success: {result.get('success', False)}")
        print(f"Message: {result.get('message', 'No message')}")
        
        if 'optimized_meal' in result:
            meal = result['optimized_meal']
            print(f"\n🍽️ Final Meal:")
            print(f"Total Calories: {meal.get('total_calories', 0):.1f}")
            print(f"Total Protein: {meal.get('total_protein', 0):.1f}g")
            print(f"Total Carbs: {meal.get('total_carbs', 0):.1f}g")
            print(f"Total Fat: {meal.get('total_fat', 0):.1f}g")
            
            print(f"\n📋 Ingredients:")
            for i, ing in enumerate(meal.get('ingredients', [])):
                print(f"  {i+1}. {ing['name']}: {ing.get('quantity_needed', 0):.1f}g")
        
        if 'target_achievement' in result:
            achievement = result['target_achievement']
            print(f"\n🎯 Target Achievement:")
            print(f"Calories: {'✅' if achievement.get('calories') else '❌'}")
            print(f"Protein: {'✅' if achievement.get('protein') else '❌'}")
            print(f"Carbs: {'✅' if achievement.get('carbs') else '❌'}")
            print(f"Fat: {'✅' if achievement.get('fat') else '❌'}")
            print(f"Overall: {'✅' if achievement.get('overall') else '❌'}")
        
        if 'optimization_details' in result:
            details = result['optimization_details']
            print(f"\n🔧 Optimization Details:")
            print(f"Initial Method: {details.get('initial_method', 'Unknown')}")
            print(f"Helper Method: {details.get('helper_method', 'Unknown')}")
            print(f"Balancing Method: {details.get('balancing_method', 'Unknown')}")
            print(f"Final Balancing Method: {details.get('final_balancing_method', 'Unknown')}")
        
        # Test learning capabilities
        print(f"\n🧠 Learning System Test:")
        if hasattr(optimizer, '_learning_history'):
            print(f"Learning History: {len(optimizer._learning_history)} patterns stored")
        if hasattr(optimizer, '_neural_weights'):
            print(f"Neural Network: Weights initialized")
        if hasattr(optimizer, '_success_patterns'):
            print(f"Success Patterns: {len(optimizer._success_patterns)} patterns learned")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_full_optimization()
    
    if result:
        print(f"\n🎉 Test completed successfully!")
        print(f"Final result keys: {list(result.keys())}")
    else:
        print(f"\n💥 Test failed!")
