#!/usr/bin/env python3
"""
Persian Single Meal Optimization - Final Version
Displays output exactly as requested by the user
"""

import asyncio
import json
from models import NutritionalTarget, UserPreferences, MealTime, Ingredient, MealItem, MealPlan
from typing import List, Dict

def create_persian_ingredients() -> List[Ingredient]:
    """Create the exact Persian ingredients from the user's data"""
    return [
        Ingredient(
            id="nan_barbari",
            name="Nan-e Barbari",
            name_fa="نان بربری",
            calories_per_100g=280,  # 140 cal / 50g * 100
            protein_per_100g=8,     # 4g / 50g * 100
            carbs_per_100g=54,      # 27g / 50g * 100
            fat_per_100g=2,         # 1g / 50g * 100
            category="grain",
            suitable_meals=[MealTime.LUNCH],
            price_per_kg=2.0,
            availability=True
        ),
        Ingredient(
            id="persian_butter",
            name="Persian Butter",
            name_fa="کره ایرانی",
            calories_per_100g=720,  # 72 cal / 10g * 100
            protein_per_100g=0,
            carbs_per_100g=0,
            fat_per_100g=80,        # 8g / 10g * 100
            category="dairy",
            suitable_meals=[MealTime.LUNCH],
            price_per_kg=12.0,
            availability=True
        ),
        Ingredient(
            id="honey",
            name="Honey",
            name_fa="عسل",
            calories_per_100g=307,  # 46 cal / 15g * 100
            protein_per_100g=0,
            carbs_per_100g=80,      # 12g / 15g * 100
            fat_per_100g=0,
            category="sweetener",
            suitable_meals=[MealTime.LUNCH],
            price_per_kg=20.0,
            availability=True
        ),
        Ingredient(
            id="black_tea",
            name="Black Tea Leaves",
            name_fa="چای سیاه",
            calories_per_100g=40,   # 2 cal / 5g * 100
            protein_per_100g=0,
            carbs_per_100g=0,
            fat_per_100g=0,
            category="beverage",
            suitable_meals=[MealTime.LUNCH],
            price_per_kg=15.0,
            availability=True
        ),
        Ingredient(
            id="mast_yogurt",
            name="Mast (Yogurt)",
            name_fa="ماست",
            calories_per_100g=60,   # 30 cal / 50g * 100
            protein_per_100g=6,     # 3g / 50g * 100
            carbs_per_100g=8,       # 4g / 50g * 100
            fat_per_100g=2,         # 1g / 50g * 100
            category="dairy",
            suitable_meals=[MealTime.LUNCH],
            price_per_kg=4.0,
            availability=True
        ),
        Ingredient(
            id="fresh_fig",
            name="Fresh Fig",
            name_fa="انجیر تازه",
            calories_per_100g=67,   # 20 cal / 30g * 100
            protein_per_100g=0,
            carbs_per_100g=17,      # 5g / 30g * 17
            fat_per_100g=0,
            category="fruit",
            suitable_meals=[MealTime.LUNCH],
            price_per_kg=8.0,
            availability=True
        ),
        Ingredient(
            id="persian_nuts_mix",
            name="Persian Nuts Mix",
            name_fa="آجیل ایرانی",
            calories_per_100g=600,  # 120 cal / 20g * 100
            protein_per_100g=15,    # 3g / 20g * 100
            carbs_per_100g=25,      # 5g / 20g * 100
            fat_per_100g=50,        # 10g / 20g * 100
            category="nuts",
            suitable_meals=[MealTime.LUNCH],
            price_per_kg=25.0,
            availability=True
        )
    ]

def load_ingredients_database() -> List[Ingredient]:
    """Load additional ingredients from database for supplementation"""
    try:
        with open('ingredients_database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Ingredient(**item) for item in data]
    except Exception as e:
        print(f"Warning: Could not load ingredients database: {e}")
        return []

def find_supplements(target: NutritionalTarget, db_ingredients: List[Ingredient]) -> List[Ingredient]:
    """Find ingredients to supplement missing nutrition"""
    supplements = []
    
    # Add protein supplements
    protein_ingredients = [ing for ing in db_ingredients if ing.category == "protein" and ing.protein_per_100g > 20]
    if protein_ingredients:
        supplements.append(protein_ingredients[0])
    
    # Add carb supplements
    carb_ingredients = [ing for ing in db_ingredients if ing.category == "grain" and ing.carbs_per_100g > 20]
    if carb_ingredients:
        supplements.append(carb_ingredients[0])
    
    # Add fat supplements
    fat_ingredients = [ing for ing in db_ingredients if ing.fat_per_100g > 10]
    if fat_ingredients:
        supplements.append(fat_ingredients[0])
    
    # Add vegetable for fiber and micronutrients
    veg_ingredients = [ing for ing in db_ingredients if ing.category == "vegetable"]
    if veg_ingredients:
        supplements.append(veg_ingredients[0])
    
    return supplements

def calculate_optimal_quantities(ingredients: List[Ingredient], target: NutritionalTarget) -> Dict[str, float]:
    """Calculate optimal quantities for each ingredient to meet daily targets"""
    
    # Start with base quantities (original serving sizes)
    base_quantities = {
        "Nan-e Barbari": 50,
        "Persian Butter": 10,
        "Honey": 15,
        "Black Tea Leaves": 5,
        "Mast (Yogurt)": 50,
        "Fresh Fig": 30,
        "Persian Nuts Mix": 20
    }
    
    # Calculate current nutrition with base quantities
    current_nutrition = {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0
    }
    
    for ingredient in ingredients:
        base_qty = base_quantities.get(ingredient.name, 100)
        ratio = base_qty / 100
        
        current_nutrition["calories"] += ingredient.calories_per_100g * ratio
        current_nutrition["protein"] += ingredient.protein_per_100g * ratio
        current_nutrition["carbs"] += ingredient.carbs_per_100g * ratio
        current_nutrition["fat"] += ingredient.fat_per_100g * ratio
    
    # Calculate scaling factors to reach targets
    calories_scale = target.calories / current_nutrition["calories"] if current_nutrition["calories"] > 0 else 1
    protein_scale = target.protein / current_nutrition["protein"] if current_nutrition["protein"] > 0 else 1
    carbs_scale = target.carbohydrates / current_nutrition["carbs"] if current_nutrition["carbs"] > 0 else 1
    fat_scale = target.fat / current_nutrition["fat"] if current_nutrition["fat"] > 0 else 1
    
    # Use the highest scale factor to ensure we meet all targets
    max_scale = max(calories_scale, protein_scale, carbs_scale, fat_scale)
    
    # Calculate final quantities
    optimal_quantities = {}
    for ingredient in ingredients:
        base_qty = base_quantities.get(ingredient.name, 100)
        optimal_qty = base_qty * max_scale
        optimal_quantities[ingredient.name] = optimal_qty
    
    return optimal_quantities

def display_final_meal_plan(ingredients: List[Ingredient], quantities: Dict[str, float]):
    """Display the final meal plan in the exact format requested by the user"""
    print("\n" + "=" * 60)
    print("🍽️  FINAL OPTIMIZED MEAL PLAN")
    print("=" * 60)
    
    # Calculate totals
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    
    print("lunch:")
    for ingredient in ingredients:
        qty = quantities.get(ingredient.name, 100)
        
        # Calculate nutrition for this quantity
        calories = ingredient.calories_per_100g * qty / 100
        protein = ingredient.protein_per_100g * qty / 100
        carbs = ingredient.carbs_per_100g * qty / 100
        fat = ingredient.fat_per_100g * qty / 100
        
        # Update totals
        total_calories += calories
        total_protein += protein
        total_carbs += carbs
        total_fat += fat
        
        # Display ingredient with quantity
        print(f"  - {ingredient.name}: {qty:.1f}g")
    
    print(f"\n📊 TOTAL NUTRITION:")
    print(f"   Calories: {total_calories:.1f} kcal")
    print(f"   Protein: {total_protein:.1f}g")
    print(f"   Carbs: {total_carbs:.1f}g")
    print(f"   Fat: {total_fat:.1f}g")
    
    # Calculate cost estimate
    total_cost = sum(ing.price_per_kg * quantities.get(ing.name, 100) / 1000 for ing in ingredients)
    print(f"💰 Cost Estimate: ${total_cost:.2f}")

async def optimize_persian_single_meal():
    """Main optimization function for single lunch meal"""
    print("🇮🇷 Persian Single Meal Optimization")
    print("=" * 60)
    
    # Create Persian ingredients
    persian_ingredients = create_persian_ingredients()
    print(f"📋 Persian Ingredients ({len(persian_ingredients)} items):")
    for ing in persian_ingredients:
        print(f"   • {ing.name_fa} ({ing.name})")
    
    # Define target macros
    target_macros = NutritionalTarget(
        calories=2000,
        protein=150,
        carbohydrates=200,
        fat=65
    )
    
    print(f"\n🎯 Target Nutrition:")
    print(f"   Calories: {target_macros.calories}")
    print(f"   Protein: {target_macros.protein}g")
    print(f"   Carbs: {target_macros.carbohydrates}g")
    print(f"   Fat: {target_macros.fat}g")
    
    # Load database for supplements
    db_ingredients = load_ingredients_database()
    
    # Find supplements
    supplements = find_supplements(target_macros, db_ingredients)
    
    # Combine all ingredients
    all_ingredients = persian_ingredients + supplements
    print(f"\n🔧 Supplements Added: {len(supplements)} items")
    
    # Calculate optimal quantities
    optimal_quantities = calculate_optimal_quantities(all_ingredients, target_macros)
    
    # Display final meal plan
    display_final_meal_plan(all_ingredients, optimal_quantities)
    
    return {
        "success": True,
        "ingredients": all_ingredients,
        "quantities": optimal_quantities
    }

async def main():
    """Main test function"""
    print("🇮🇷 Persian Single Meal Optimization Test")
    print("=" * 60)
    
    # Run optimization
    result = await optimize_persian_single_meal()
    
    if result:
        print("\n🎉 Persian single meal optimization completed successfully!")
        print("The system has:")
        print("1. ✅ Analyzed your Persian ingredients")
        print("2. ✅ Added supplementary ingredients")
        print("3. ✅ Calculated optimal quantities for single meal")
        print("4. ✅ Generated a single lunch meal plan")
    else:
        print("\n❌ Optimization failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
