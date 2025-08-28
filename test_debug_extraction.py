#!/usr/bin/env python3
"""
Debug script to understand why input ingredients are getting zero values
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_debug_extraction():
    """Debug ingredient extraction process"""
    
    optimizer = RAGMealOptimizer()
    
    # Test the exact data that the website is sending
    print("🧪 Debugging Ingredient Extraction")
    print("=" * 60)
    
    # This is what the website is actually sending (based on user's output)
    website_input = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "Ground Beef",
                            "quantity_needed": 200
                            # Note: NO nutritional info!
                        },
                        {
                            "name": "Ground Lamb Fat", 
                            "quantity_needed": 100
                            # Note: NO nutritional info!
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
                            "name": "Pita Bread",
                            "quantity_needed": 100
                            # Note: NO nutritional info!
                        }
                    ]
                }
            ],
            "success": True,
            "message": "Ingredients extracted successfully"
        },
        "target_macros": {
            "calories": 600,
            "protein": 40,
            "carbs": 80,
            "fat": 20
        },
        "user_preferences": {
            "diet_type": "balanced",
            "allergies": [],
            "preferences": []
        },
        "user_id": "test_user",
        "meal_type": "lunch"
    }
    
    print("📥 Website input:")
    for ing in website_input["rag_response"]["suggestions"][0]["ingredients"]:
        has_nutrition = (
            'protein_per_100g' in ing and 
            'carbs_per_100g' in ing and 
            'fat_per_100g' in ing and 
            'calories_per_100g' in ing
        )
        print(f"   - {ing['name']}: has_nutrition={has_nutrition}")
        if has_nutrition:
            print(f"     P:{ing.get('protein_per_100g', 0)}, C:{ing.get('carbs_per_100g', 0)}, F:{ing.get('fat_per_100g', 0)}, Cal:{ing.get('calories_per_100g', 0)}")
    
    print("\n🔍 Step 1: Testing ingredient extraction...")
    extracted = optimizer._extract_rag_ingredients(website_input)
    
    print(f"\n📋 Extracted {len(extracted)} ingredients:")
    for ing in extracted:
        print(f"   - {ing['name']}:")
        print(f"     P:{ing.get('protein_per_100g', 0)}, C:{ing.get('carbs_per_100g', 0)}, F:{ing.get('fat_per_100g', 0)}, Cal:{ing.get('calories_per_100g', 0)}")
        print(f"     quantity:{ing.get('quantity', 0)}, max_quantity:{ing.get('max_quantity', 0)}")
    
    print("\n🔍 Step 2: Testing nutrition_db lookup...")
    for ing in extracted:
        name = ing['name'].lower()
        if name in optimizer.nutrition_db:
            print(f"   ✅ {ing['name']} found in nutrition_db: {optimizer.nutrition_db[name]}")
        else:
            print(f"   ❌ {ing['name']} NOT found in nutrition_db")
    
    print("\n🔍 Step 3: Testing _enrich_ingredient_with_nutrition...")
    for ing in website_input["rag_response"]["suggestions"][0]["ingredients"]:
        if not any(f'{macro}_per_100g' in ing for macro in ['protein', 'carbs', 'fat', 'calories']):
            print(f"\n   Testing enrichment for {ing['name']}...")
            enriched = optimizer._enrich_ingredient_with_nutrition(ing)
            print(f"     Before: {ing}")
            print(f"     After:  {enriched}")
    
    print("\n🔍 Step 4: Testing full optimization...")
    try:
        result = optimizer.optimize_single_meal(
            rag_response=website_input,
            target_macros=website_input["target_macros"],
            user_preferences=website_input["user_preferences"],
            meal_type=website_input["meal_type"]
        )
        
        if result.get('success'):
            print("   ✅ Optimization successful!")
            
            print("\n   📊 Final meal:")
            for item in result['meal']:
                print(f"   - {item['name']}: {item['quantity_needed']}g "
                      f"(P:{item['protein_per_100g']}, C:{item['carbs_per_100g']}, "
                      f"F:{item['fat_per_100g']}, Cal:{item['calories_per_100g']})")
            
            # Check which ingredients are zero
            print("\n🔍 Zero-value ingredients analysis:")
            for item in result['meal']:
                if (item['protein_per_100g'] == 0 and 
                    item['carbs_per_100g'] == 0 and 
                    item['fat_per_100g'] == 0 and 
                    item['calories_per_100g'] == 0):
                    print(f"   ❌ {item['name']}: ALL values are zero!")
                elif any(item.get(f'{macro}_per_100g', 0) == 0 for macro in ['protein', 'carbs', 'fat', 'calories']):
                    print(f"   ⚠️ {item['name']}: Some values are zero")
                else:
                    print(f"   ✅ {item['name']}: All values are non-zero")
        else:
            print("   ❌ Optimization failed!")
            
    except Exception as e:
        print(f"   ❌ Exception during optimization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_debug_extraction()
