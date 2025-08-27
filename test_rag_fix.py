#!/usr/bin/env python3
"""
Test script to verify RAG optimization engine fixes
"""

import json
from rag_optimization_engine import RAGMealOptimizer

def test_ingredient_enrichment():
    """Test that ingredients are properly enriched with nutritional data"""
    print("🧪 Testing ingredient enrichment...")
    
    # Initialize the optimizer
    optimizer = RAGMealOptimizer()
    
    # Test data similar to what the frontend sends
    test_rag_response = {
        "suggestions": [
            {
                "ingredients": [
                    {"name": "Ground Beef", "quantity_needed": 300},
                    {"name": "Onion", "quantity_needed": 100},
                    {"name": "Grilled Tomato", "quantity_needed": 100},
                    {"name": "Grilled Pepper", "quantity_needed": 50},
                    {"name": "Pita Bread", "quantity_needed": 100}
                ]
            }
        ]
    }
    
    test_target_macros = {
        "calories": 637.2,
        "protein": 45.4,
        "carbs": 88.5,
        "fat": 13.7
    }
    
    test_user_preferences = {
        "dietary_restrictions": [],
        "allergies": [],
        "preferred_cuisines": ["persian"]
    }
    
    try:
        # Test ingredient enrichment
        print("📊 Testing ingredient enrichment...")
        enriched_ingredients = optimizer._extract_rag_ingredients(test_rag_response)
        
        print(f"✅ Enriched {len(enriched_ingredients)} ingredients")
        
        for i, ingredient in enumerate(enriched_ingredients):
            print(f"  {i+1}. {ingredient['name']}")
            print(f"     Protein: {ingredient.get('protein_per_100g', 0)}g/100g")
            print(f"     Carbs: {ingredient.get('carbs_per_100g', 0)}g/100g")
            print(f"     Fat: {ingredient.get('fat_per_100g', 0)}g/100g")
            print(f"     Calories: {ingredient.get('calories_per_100g', 0)}cal/100g")
            print()
        
        # Test current totals calculation
        print("📊 Testing current totals calculation...")
        current_totals = optimizer._calculate_current_totals(enriched_ingredients)
        print(f"✅ Current totals: {current_totals}")
        
        # Test macro deficits calculation
        print("📊 Testing macro deficits calculation...")
        deficits = optimizer._calculate_macro_deficits(current_totals, test_target_macros)
        print(f"✅ Deficits: {deficits}")
        
        # Test full optimization
        print("🚀 Testing full optimization...")
        result = optimizer.optimize_single_meal(
            rag_response=test_rag_response,
            target_macros=test_target_macros,
            user_preferences=test_user_preferences,
            meal_type="lunch"
        )
        
        print("✅ Optimization completed successfully!")
        print(f"📊 Result: {json.dumps(result, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_specific_ingredients():
    """Test specific ingredient mappings"""
    print("\n🧪 Testing specific ingredient mappings...")
    
    optimizer = RAGMealOptimizer()
    
    test_ingredients = [
        {"name": "Ground Beef", "quantity_needed": 100},
        {"name": "Onion", "quantity_needed": 100},
        {"name": "Grilled Tomato", "quantity_needed": 100},
        {"name": "Grilled Pepper", "quantity_needed": 100},
        {"name": "Pita Bread", "quantity_needed": 100}
    ]
    
    for ingredient in test_ingredients:
        enriched = optimizer._enrich_ingredient_with_nutrition(ingredient)
        print(f"✅ {ingredient['name']} -> {enriched['name']}")
        print(f"   Protein: {enriched['protein_per_100g']}g, Carbs: {enriched['carbs_per_100g']}g, Fat: {enriched['fat_per_100g']}g, Calories: {enriched['calories_per_100g']}cal")
        print()

if __name__ == "__main__":
    print("🚀 Starting RAG optimization engine tests...")
    print("=" * 50)
    
    # Test specific ingredients first
    test_specific_ingredients()
    
    # Test full optimization
    success = test_ingredient_enrichment()
    
    if success:
        print("\n🎉 All tests passed! The RAG optimization engine is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
