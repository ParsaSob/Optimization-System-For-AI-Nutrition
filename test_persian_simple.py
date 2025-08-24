#!/usr/bin/env python3
"""
Simple Persian Meal Optimization Test
Focuses on the specific Persian ingredients provided by the user
"""

import asyncio
import json
from optimization_engine import MealOptimizationEngine
from models import NutritionalTarget, UserPreferences, MealTime, Ingredient
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
            suitable_meals=[MealTime.BREAKFAST, MealTime.LUNCH, MealTime.DINNER],
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
            suitable_meals=[MealTime.BREAKFAST, MealTime.MORNING_SNACK],
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
            suitable_meals=[MealTime.BREAKFAST, MealTime.MORNING_SNACK],
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
            suitable_meals=[MealTime.BREAKFAST, MealTime.MORNING_SNACK, MealTime.AFTERNOON_SNACK],
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
            suitable_meals=[MealTime.BREAKFAST, MealTime.MORNING_SNACK, MealTime.AFTERNOON_SNACK],
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
            suitable_meals=[MealTime.BREAKFAST, MealTime.MORNING_SNACK, MealTime.AFTERNOON_SNACK],
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
            suitable_meals=[MealTime.MORNING_SNACK, MealTime.AFTERNOON_SNACK, MealTime.EVENING_SNACK],
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
        "carbs": total_carbs,
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

async def optimize_persian_meal():
    """Main optimization function"""
    print("🇮🇷 Persian Meal Optimization")
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
    
    # Create user preferences
    user_preferences = UserPreferences(
        dietary_restrictions=[],
        allergies=[],
        preferred_cuisines=["persian"],
        cooking_time_preference="medium"
    )
    
    # Initialize optimization engine
    engine = MealOptimizationEngine()
    
    print(f"\n🚀 Starting optimization with {len(all_ingredients)} ingredients...")
    print("   Using ML algorithms: Linear Programming, Genetic Algorithm, Differential Evolution")
    print("   Multi-objective optimization for nutrition balance and cost")
    
    try:
        # Run optimization
        result = await engine.optimize_meal_plan(
            ingredients=all_ingredients,
            target_macros=target_macros,
            user_preferences=user_preferences,
            meal_periods=list(MealTime)
        )
        
        if result and result.get('success', False):
            print("\n✅ OPTIMIZATION SUCCESSFUL!")
            print("=" * 60)
            
            # Display results
            print(f"📈 Optimization Method: {result.get('optimization_method', 'Unknown')}")
            print(f"🎯 Target Achieved: {result.get('target_achieved', 'Unknown')}")
            print(f"💰 Cost Estimate: ${result.get('cost_estimate', 0):.2f}")
            
            if 'meal_plans' in result:
                print(f"\n🍽️  Optimized Meal Plan:")
                for i, meal in enumerate(result['meal_plans']):
                    print(f"   {i+1}. {meal.meal_time.value}: {meal.total_calories:.1f} kcal")
                    if meal.items:
                        for item in meal.items:
                            print(f"      - {item.ingredient.name}: {item.quantity_grams:.1f}g")
            
            if 'daily_totals' in result:
                daily = result['daily_totals']
                print(f"\n📊 Daily Totals:")
                print(f"   Calories: {daily.calories:.1f}")
                print(f"   Protein: {daily.protein:.1f}g")
                print(f"   Carbs: {daily.carbohydrates:.1f}g")
                print(f"   Fat: {daily.fat:.1f}g")
            
            return result
            
        else:
            print("\n❌ OPTIMIZATION FAILED")
            print(f"   Error: {result.get('error', 'Unknown error') if result else 'No result returned'}")
            return None
            
    except Exception as e:
        print(f"\n❌ ERROR during optimization: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Main test function"""
    print("🇮🇷 Persian Meal Optimization Test")
    print("=" * 60)
    
    # Run optimization
    result = await optimize_persian_meal()
    
    if result:
        print("\n🎉 Persian meal optimization completed successfully!")
        print("The system has:")
        print("1. ✅ Analyzed your Persian ingredients")
        print("2. ✅ Calculated nutritional deficits")
        print("3. ✅ Added supplementary ingredients")
        print("4. ✅ Optimized using advanced ML algorithms")
        print("5. ✅ Generated a balanced meal plan")
    else:
        print("\n❌ Optimization failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
