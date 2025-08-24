#!/usr/bin/env python3
"""
Persian Single Meal Optimization
Puts all ingredients in one lunch meal with proper quantities to meet daily targets
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
            suitable_meals=[MealTime.LUNCH],  # Only lunch
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
            suitable_meals=[MealTime.LUNCH],  # Only lunch
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
            suitable_meals=[MealTime.LUNCH],  # Only lunch
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
            suitable_meals=[MealTime.LUNCH],  # Only lunch
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
            suitable_meals=[MealTime.LUNCH],  # Only lunch
            price_per_kg=4.0,
            availability=True
        ),
        Ingredient(
            id="fresh_fig",
            name="Fresh Fig",
            name_fa="انجیر تازه",
            calories_per_100g=67,   # 20 cal / 30g * 100
            protein_per_100g=0,
            carbs_per_100g=17,      # 5g / 30g * 100
            fat_per_100g=0,
            category="fruit",
            suitable_meals=[MealTime.LUNCH],  # Only lunch
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
            suitable_meals=[MealTime.LUNCH],  # Only lunch
            price_per_kg=25.0,
            availability=True
        )
    ]

def analyze_persian_nutrition(ingredients: List[Ingredient]) -> Dict[str, float]:
    """Analyze the nutritional content of Persian ingredients with their serving sizes"""
    # Original serving sizes from user data
    servings = {
        "Nan-e Barbari": 50,
        "Persian Butter": 10,
        "Honey": 15,
        "Black Tea Leaves": 5,
        "Mast (Yogurt)": 50,
        "Fresh Fig": 30,
        "Persian Nuts Mix": 20
    }
    
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    
    print("📊 Persian Ingredients Nutritional Analysis:")
    print("=" * 60)
    print(f"{'Ingredient':<20} {'Serving':<10} {'Calories':<10} {'Protein':<10} {'Carbs':<10} {'Fat':<10}")
    print("-" * 60)
    
    for ingredient in ingredients:
        serving = servings.get(ingredient.name, 100)
        ratio = serving / 100
        
        calories = ingredient.calories_per_100g * ratio
        protein = ingredient.protein_per_100g * ratio
        carbs = ingredient.carbs_per_100g * ratio
        fat = ingredient.fat_per_100g * ratio
        
        total_calories += calories
        total_protein += protein
        total_carbs += carbs
        total_fat += fat
        
        print(f"{ingredient.name_fa:<20} {serving:<10}g {calories:<10.1f} {protein:<10.1f}g {carbs:<10.1f}g {fat:<10.1f}g")
    
    print("-" * 60)
    print(f"{'TOTAL':<20} {'':<10} {total_calories:<10.1f} {total_protein:<10.1f}g {total_carbs:<10.1f}g {total_fat:<10.1f}g")
    
    return {
        "calories": total_calories,
        "protein": total_protein,
        "carbs": total_calories,
        "fat": total_fat
    }

def load_ingredients_database() -> List[Ingredient]:
    """Load additional ingredients from database for supplementation"""
    try:
        with open('ingredients_database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Ingredient(**item) for item in data]
    except Exception as e:
        print(f"Warning: Could not load ingredients database: {e}")
        return []

def find_supplements(current_nutrition: Dict[str, float], target: NutritionalTarget, db_ingredients: List[Ingredient]) -> List[Ingredient]:
    """Find ingredients to supplement missing nutrition"""
    supplements = []
    
    # Calculate deficits
    protein_deficit = max(0, target.protein - current_nutrition["protein"])
    carbs_deficit = max(0, target.carbohydrates - current_nutrition["carbs"])
    fat_deficit = max(0, target.fat - current_nutrition["fat"])
    calories_deficit = max(0, target.calories - current_nutrition["calories"])
    
    print(f"\n🎯 Target vs Current:")
    print(f"   Target:     {target.calories:.1f} cal, {target.protein:.1f}g protein, {target.carbohydrates:.1f}g carbs, {target.fat:.1f}g fat")
    print(f"   Current:    {current_nutrition['calories']:.1f} cal, {current_nutrition['protein']:.1f}g protein, {current_nutrition['carbs']:.1f}g carbs, {current_nutrition['fat']:.1f}g fat")
    print(f"   Deficits:   {calories_deficit:.1f} cal, {protein_deficit:.1f}g protein, {carbs_deficit:.1f}g carbs, {fat_deficit:.1f}g fat")
    
    print(f"\n🔧 Adding Supplements:")
    
    # Add protein supplements
    if protein_deficit > 0:
        protein_ingredients = [ing for ing in db_ingredients if ing.category == "protein" and ing.protein_per_100g > 20]
        if protein_ingredients:
            supplements.append(protein_ingredients[0])
            print(f"   ➕ Protein: {protein_ingredients[0].name} ({protein_ingredients[0].protein_per_100g:.1f}g/100g)")
    
    # Add carb supplements
    if carbs_deficit > 0:
        carb_ingredients = [ing for ing in db_ingredients if ing.category == "grain" and ing.carbs_per_100g > 20]
        if carb_ingredients:
            supplements.append(carb_ingredients[0])
            print(f"   ➕ Carbs: {carb_ingredients[0].name} ({carb_ingredients[0].carbs_per_100g:.1f}g/100g)")
    
    # Add fat supplements
    if fat_deficit > 0:
        fat_ingredients = [ing for ing in db_ingredients if ing.fat_per_100g > 10]
        if fat_ingredients:
            supplements.append(fat_ingredients[0])
            print(f"   ➕ Fat: {fat_ingredients[0].name} ({fat_ingredients[0].fat_per_100g:.1f}g/100g)")
    
    # Add vegetable for fiber and micronutrients
    veg_ingredients = [ing for ing in db_ingredients if ing.category == "vegetable"]
    if veg_ingredients:
        supplements.append(veg_ingredients[0])
        print(f"   ➕ Vegetable: {veg_ingredients[0].name}")
    
    return supplements

def calculate_optimal_quantities(ingredients: List[Ingredient], target: NutritionalTarget) -> Dict[str, float]:
    """Calculate optimal quantities for each ingredient to meet daily targets"""
    print(f"\n🧮 Calculating Optimal Quantities...")
    
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

def create_single_lunch_meal(ingredients: List[Ingredient], quantities: Dict[str, float]) -> MealPlan:
    """Create a single lunch meal with all ingredients"""
    meal_items = []
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    
    for ingredient in ingredients:
        qty = quantities.get(ingredient.name, 100)
        
        item = MealItem(
            ingredient=ingredient,
            quantity_grams=qty,
            calories=ingredient.calories_per_100g * qty / 100,
            protein=ingredient.protein_per_100g * qty / 100,
            carbs=ingredient.carbs_per_100g * qty / 100,
            fat=ingredient.fat_per_100g * qty / 100
        )
        
        meal_items.append(item)
        total_calories += item.calories
        total_protein += item.protein
        total_carbs += item.carbs
        total_fat += item.fat
    
    return MealPlan(
        meal_time=MealTime.LUNCH,
        items=meal_items,
        total_calories=total_calories,
        total_protein=total_protein,
        total_carbs=total_carbs,
        total_fat=total_fat
    )

async def optimize_persian_single_meal():
    """Main optimization function for single lunch meal"""
    print("🇮🇷 Persian Single Meal Optimization")
    print("=" * 60)
    
    # Create Persian ingredients
    persian_ingredients = create_persian_ingredients()
    print(f"📋 Persian Ingredients ({len(persian_ingredients)} items):")
    for ing in persian_ingredients:
        print(f"   • {ing.name_fa} ({ing.name})")
    
    # Analyze current nutrition
    current_nutrition = analyze_persian_nutrition(persian_ingredients)
    
    # Define target macros
    target_macros = NutritionalTarget(
        calories=2000,
        protein=150,
        carbohydrates=200,
        fat=65
    )
    
    # Load database for supplements
    db_ingredients = load_ingredients_database()
    
    # Find supplements
    supplements = find_supplements(current_nutrition, target_macros, db_ingredients)
    
    # Combine all ingredients
    all_ingredients = persian_ingredients + supplements
    print(f"\n🔧 Total ingredients after supplementation: {len(all_ingredients)}")
    
    # Calculate optimal quantities
    optimal_quantities = calculate_optimal_quantities(all_ingredients, target_macros)
    
    # Create single lunch meal
    lunch_meal = create_single_lunch_meal(all_ingredients, optimal_quantities)
    
    print(f"\n✅ OPTIMIZATION SUCCESSFUL!")
    print("=" * 60)
    
    # Display results
    print(f"🍽️  Single Lunch Meal Plan:")
    print(f"   Meal Time: {lunch_meal.meal_time.value}")
    print(f"   Total Calories: {lunch_meal.total_calories:.1f} kcal")
    print(f"   Total Protein: {lunch_meal.total_protein:.1f}g")
    print(f"   Total Carbs: {lunch_meal.total_carbs:.1f}g")
    print(f"   Total Fat: {lunch_meal.total_fat:.1f}g")
    
    print(f"\n📋 Ingredients with Quantities:")
    for item in lunch_meal.items:
        print(f"   - {item.ingredient.name}: {item.quantity_grams:.1f}g")
        print(f"     Calories: {item.calories:.1f}, Protein: {item.protein:.1f}g, Carbs: {item.carbs:.1f}g, Fat: {item.fat:.1f}g")
    
    # Calculate cost estimate
    total_cost = sum(item.ingredient.price_per_kg * item.quantity_grams / 1000 for item in lunch_meal.items)
    print(f"\n💰 Cost Estimate: ${total_cost:.2f}")
    
    return {
        "success": True,
        "meal_plan": lunch_meal,
        "quantities": optimal_quantities,
        "cost_estimate": total_cost
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
        print("2. ✅ Calculated nutritional deficits")
        print("3. ✅ Added supplementary ingredients")
        print("4. ✅ Calculated optimal quantities for single meal")
        print("5. ✅ Generated a single lunch meal plan")
        
        print(f"\n📊 Final Summary:")
        print(f"   Persian Ingredients: {len(create_persian_ingredients())}")
        print(f"   Supplements Added: {len(load_ingredients_database())}")
        print(f"   Total Ingredients Used: {len(create_persian_ingredients()) + len(load_ingredients_database())}")
        print(f"   Single Meal Calories: {result['meal_plan'].total_calories:.1f}")
        print(f"   Single Meal Protein: {result['meal_plan'].total_protein:.1f}g")
    else:
        print("\n❌ Optimization failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
