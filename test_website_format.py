#!/usr/bin/env python3
"""
Test script to verify website input format processing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_website_format():
    """Test the exact format that the website sends"""
    
    optimizer = RAGMealOptimizer()
    
    # Test the exact format from the website
    print("🧪 Testing Website Input Format")
    print("=" * 60)
    
    # Website format with nutritional info
    website_input = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "Ground Beef",
                            "protein_per_100g": 26.0,
                            "carbs_per_100g": 0.0,
                            "fat_per_100g": 15.0,
                            "calories_per_100g": 250.0,
                            "quantity_needed": 200
                        },
                        {
                            "name": "Onion",
                            "protein_per_100g": 1.1,
                            "carbs_per_100g": 9.0,
                            "fat_per_100g": 0.1,
                            "calories_per_100g": 40.0,
                            "quantity_needed": 100
                        },
                        {
                            "name": "Butter",
                            "protein_per_100g": 0.9,
                            "carbs_per_100g": 0.1,
                            "fat_per_100g": 81.0,
                            "calories_per_100g": 717.0,
                            "quantity_needed": 10
                        },
                        {
                            "name": "Pita Bread",
                            "protein_per_100g": 10.0,
                            "carbs_per_100g": 50.0,
                            "fat_per_100g": 2.0,
                            "calories_per_100g": 250.0,
                            "quantity_needed": 100
                        },
                        {
                            "name": "Grilled Tomato",
                            "protein_per_100g": 0.9,
                            "carbs_per_100g": 3.9,
                            "fat_per_100g": 0.2,
                            "calories_per_100g": 18.0,
                            "quantity_needed": 100
                        }
                    ]
                }
            ],
            "success": True,
            "message": "Ingredients extracted successfully"
        },
        "target_macros": {
            "calories": 800,
            "protein": 40,
            "carbs": 80,
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
    
    print("📥 Input format:")
    print("   - rag_response.suggestions[0].ingredients[]")
    print("   - Each ingredient has: name, protein_per_100g, carbs_per_100g, fat_per_100g, calories_per_100g, quantity_needed")
    
    # Test ingredient extraction
    print("\n1️⃣ Testing ingredient extraction...")
    extracted = optimizer._extract_rag_ingredients(website_input)
    
    print(f"   Extracted {len(extracted)} ingredients:")
    for ing in extracted:
        print(f"   - {ing['name']}: protein={ing.get('protein_per_100g', 0)}, "
              f"carbs={ing.get('carbs_per_100g', 0)}, "
              f"fat={ing.get('fat_per_100g', 0)}, "
              f"calories={ing.get('calories_per_100g', 0)}, "
              f"quantity={ing.get('quantity', 0)}")
    
    # Verify that nutritional values are preserved
    print("\n2️⃣ Verifying nutritional values preservation...")
    original_ingredients = website_input["rag_response"]["suggestions"][0]["ingredients"]
    for i, original in enumerate(original_ingredients):
        if i < len(extracted):
            extracted_ing = extracted[i]
            print(f"   {original['name']}:")
            print(f"     Original: P={original['protein_per_100g']}, C={original['carbs_per_100g']}, F={original['fat_per_100g']}, Cal={original['calories_per_100g']}")
            print(f"     Extracted: P={extracted_ing['protein_per_100g']}, C={extracted_ing['carbs_per_100g']}, F={extracted_ing['fat_per_100g']}, Cal={extracted_ing['calories_per_100g']}")
            
            # Check if values are preserved
            if (extracted_ing['protein_per_100g'] == original['protein_per_100g'] and
                extracted_ing['carbs_per_100g'] == original['carbs_per_100g'] and
                extracted_ing['fat_per_100g'] == original['fat_per_100g'] and
                extracted_ing['calories_per_100g'] == original['calories_per_100g']):
                print("     ✅ Values preserved correctly")
            else:
                print("     ❌ Values were changed!")
    
    # Test full optimization
    print("\n3️⃣ Testing full optimization...")
    try:
        result = optimizer.optimize_single_meal(
            rag_response=website_input,
            target_macros=website_input["target_macros"],
            user_preferences=website_input["user_preferences"],
            meal_type=website_input["meal_type"]
        )
        
        if result.get('success'):
            print("   ✅ Optimization successful!")
            print(f"   Method used: {result['optimization_result']['method']}")
            
            print("\n   📊 Final meal:")
            for item in result['meal']:
                print(f"   - {item['name']}: {item['quantity_needed']}g "
                      f"(P:{item['protein_per_100g']}, C:{item['carbs_per_100g']}, "
                      f"F:{item['fat_per_100g']}, Cal:{item['calories_per_100g']})")
            
            print(f"\n   🎯 Target achievement: {result['target_achievement']}")
            print(f"   📈 Nutritional totals: {result['nutritional_totals']}")
            
            # Check if input ingredients are still present with correct values
            print("\n4️⃣ Verifying input ingredients in final result...")
            input_names = {ing['name'].lower() for ing in original_ingredients}
            for item in result['meal']:
                if item['name'].lower() in input_names:
                    # Find corresponding original ingredient
                    original = next((ing for ing in original_ingredients if ing['name'].lower() == item['name'].lower()), None)
                    if original:
                        if (item['protein_per_100g'] == original['protein_per_100g'] and
                            item['carbs_per_100g'] == original['carbs_per_100g'] and
                            item['fat_per_100g'] == original['fat_per_100g'] and
                            item['calories_per_100g'] == original['calories_per_100g']):
                            print(f"   ✅ {item['name']}: Values preserved correctly")
                        else:
                            print(f"   ❌ {item['name']}: Values changed!")
                            print(f"      Original: P={original['protein_per_100g']}, C={original['carbs_per_100g']}, F={original['fat_per_100g']}, Cal={original['calories_per_100g']}")
                            print(f"      Final: P={item['protein_per_100g']}, C={item['carbs_per_100g']}, F={item['fat_per_100g']}, Cal={item['calories_per_100g']}")
        else:
            print("   ❌ Optimization failed!")
            print(f"   Error: {result.get('optimization_result', {}).get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ❌ Exception during optimization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_website_format()
