#!/usr/bin/env python3
"""
Test script to verify ingredient enrichment and optimization
"""

try:
    from rag_optimization_engine import RAGMealOptimizer
    print("✅ Successfully imported RAGMealOptimizer")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

def test_ingredient_enrichment():
    """Test ingredient enrichment functionality"""
    
    print("\n🧪 Testing Ingredient Enrichment")
    print("=" * 50)
    
    # Initialize the optimizer
    try:
        optimizer = RAGMealOptimizer()
        print("✅ RAG optimizer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize optimizer: {e}")
        return
    
    # Test RAG response with ingredients that need enrichment
    test_rag_response = {
        "suggestions": [
            {
                "ingredients": [
                    {
                        "name": "ground_beef",
                        "quantity_needed": 300
                    },
                    {
                        "name": "onion",
                        "quantity_needed": 100
                    },
                    {
                        "name": "grilled_tomato",
                        "quantity_needed": 100
                    },
                    {
                        "name": "grilled_pepper",
                        "quantity_needed": 50
                    },
                    {
                        "name": "pita_bread",
                        "quantity_needed": 100
                    }
                ]
            }
        ],
        "success": True,
        "message": "Test ingredients"
    }
    
    # Test ingredient extraction and enrichment
    try:
        enriched_ingredients = optimizer._extract_rag_ingredients(test_rag_response)
        print(f"✅ Extracted and enriched {len(enriched_ingredients)} ingredients")
        
        print("\n📋 Enriched Ingredients:")
        print("-" * 40)
        for i, ingredient in enumerate(enriched_ingredients):
            print(f"{i+1}. {ingredient['name']}:")
            print(f"   Quantity: {ingredient['quantity_needed']}g")
            print(f"   Protein: {ingredient['protein_per_100g']}g/100g")
            print(f"   Carbs: {ingredient['carbs_per_100g']}g/100g")
            print(f"   Fat: {ingredient['fat_per_100g']}g/100g")
            print(f"   Calories: {ingredient['calories_per_100g']}kcal/100g")
            print()
        
        # Test current totals calculation
        current_totals = optimizer._calculate_current_totals(enriched_ingredients)
        print(f"📊 Current Totals:")
        print(f"   Calories: {current_totals['calories']:.1f}")
        print(f"   Protein: {current_totals['protein']:.1f}g")
        print(f"   Carbs: {current_totals['carbs']:.1f}g")
        print(f"   Fat: {current_totals['fat']:.1f}g")
        
    except Exception as e:
        print(f"❌ Error in ingredient enrichment: {e}")
        import traceback
        traceback.print_exc()

def test_meal_optimization():
    """Test complete meal optimization"""
    
    print("\n🧪 Testing Complete Meal Optimization")
    print("=" * 50)
    
    # Initialize the optimizer
    try:
        optimizer = RAGMealOptimizer()
        print("✅ RAG optimizer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize optimizer: {e}")
        return
    
    # Test request
    test_request = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "ground_beef",
                            "quantity_needed": 300
                        },
                        {
                            "name": "onion",
                            "quantity_needed": 100
                        },
                        {
                            "name": "grilled_tomato",
                            "quantity_needed": 100
                        },
                        {
                            "name": "grilled_pepper",
                            "quantity_needed": 50
                        },
                        {
                            "name": "pita_bread",
                            "quantity_needed": 100
                        }
                    ]
                }
            ],
            "success": True,
            "message": "Test meal"
        },
        "target_macros": {
            "calories": 637,
            "protein": 45.4,
            "carbs": 88.5,
            "fat": 13.7
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
        
        print("✅ Meal optimization completed successfully!")
        print(f"🏆 Method: {result['optimization_result']['method']}")
        print(f"⏱️ Computation Time: {result['optimization_result']['computation_time']}s")
        
        print("\n🍽️ Final Meal:")
        print("-" * 30)
        for ingredient in result['meal']:
            print(f"• {ingredient['name']}: {ingredient['quantity_needed']}g")
            print(f"  Calories: {ingredient['calories_per_100g']}kcal/100g")
            print(f"  Protein: {ingredient['protein_per_100g']}g/100g")
            print(f"  Carbs: {ingredient['carbs_per_100g']}g/100g")
            print(f"  Fat: {ingredient['fat_per_100g']}g/100g")
            print()
        
        print(f"📊 Nutritional Totals:")
        print(f"   Calories: {result['nutritional_totals']['calories']:.1f}")
        print(f"   Protein: {result['nutritional_totals']['protein']:.1f}g")
        print(f"   Carbs: {result['nutritional_totals']['carbs']:.1f}g")
        print(f"   Fat: {result['nutritional_totals']['fat']:.1f}g")
        
        print(f"\n🎯 Target Achievement:")
        achievement = result['target_achievement']
        print(f"   Calories: {'✅' if achievement.get('calories', False) else '❌'}")
        print(f"   Protein: {'✅' if achievement.get('protein', False) else '❌'}")
        print(f"   Carbs: {'✅' if achievement.get('carbs', False) else '❌'}")
        print(f"   Fat: {'✅' if achievement.get('fat', False) else '❌'}")
        print(f"   Overall: {'✅' if achievement.get('overall', False) else '❌'}")
        
    except Exception as e:
        print(f"❌ Error in meal optimization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Ingredient Optimization Test Suite")
    print("=" * 60)
    
    test_ingredient_enrichment()
    test_meal_optimization()
    
    print("\n🎉 All tests completed!")
