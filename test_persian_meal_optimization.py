#!/usr/bin/env python3
"""
Persian Meal Optimization Test
Takes Persian ingredients, optimizes them, and adds more if needed to meet nutritional targets
"""

import asyncio
import json
from optimization_engine import MealOptimizationEngine
from models import NutritionalTarget, UserPreferences, MealTime, Ingredient, MealItem, MealPlan
from typing import List, Dict, Tuple

class PersianMealOptimizer:
    """Persian meal optimizer that handles ingredient optimization and supplementation"""
    
    def __init__(self):
        self.engine = MealOptimizationEngine()
        self.ingredients_db = self._load_ingredients_database()
        
    def _load_ingredients_database(self) -> List[Ingredient]:
        """Load ingredients from the database"""
        try:
            with open('ingredients_database.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Ingredient(**item) for item in data]
        except Exception as e:
            print(f"Warning: Could not load ingredients database: {e}")
            return []
    
    def create_persian_ingredients(self) -> List[Ingredient]:
        """Create the Persian ingredients provided by the user"""
        persian_ingredients = [
            Ingredient(
                id="nan_barbari",
                name="Nan-e Barbari",
                name_fa="نان بربری",
                calories_per_100g=280,  # 140 calories for 50g = 280 per 100g
                protein_per_100g=8,     # 4g for 50g = 8 per 100g
                carbs_per_100g=54,      # 27g for 50g = 54 per 100g
                fat_per_100g=2,         # 1g for 50g = 2 per 100g
                category="grain",
                suitable_meals=[MealTime.BREAKFAST, MealTime.LUNCH, MealTime.DINNER],
                price_per_kg=2.0,
                availability=True
            ),
            Ingredient(
                id="persian_butter",
                name="Persian Butter",
                name_fa="کره ایرانی",
                calories_per_100g=720,  # 72 calories for 10g = 720 per 100g
                protein_per_100g=0,
                carbs_per_100g=0,
                fat_per_100g=80,        # 8g for 10g = 80 per 100g
                category="dairy",
                suitable_meals=[MealTime.BREAKFAST, MealTime.MORNING_SNACK],
                price_per_kg=12.0,
                availability=True
            ),
            Ingredient(
                id="honey",
                name="Honey",
                name_fa="عسل",
                calories_per_100g=307,  # 46 calories for 15g = 307 per 100g
                protein_per_100g=0,
                carbs_per_100g=80,      # 12g for 15g = 80 per 100g
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
                calories_per_100g=40,   # 2 calories for 5g = 40 per 100g
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
                calories_per_100g=60,   # 30 calories for 50g = 60 per 100g
                protein_per_100g=6,     # 3g for 50g = 6 per 100g
                carbs_per_100g=8,       # 4g for 50g = 8 per 100g
                fat_per_100g=2,         # 1g for 50g = 2 per 100g
                category="dairy",
                suitable_meals=[MealTime.BREAKFAST, MealTime.MORNING_SNACK, MealTime.AFTERNOON_SNACK],
                price_per_kg=4.0,
                availability=True
            ),
            Ingredient(
                id="fresh_fig",
                name="Fresh Fig",
                name_fa="انجیر تازه",
                calories_per_100g=67,   # 20 calories for 30g = 67 per 100g
                protein_per_100g=0,
                carbs_per_100g=17,      # 5g for 30g = 17 per 100g
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
                calories_per_100g=600,  # 120 calories for 20g = 600 per 100g
                protein_per_100g=15,    # 3g for 20g = 15 per 100g
                carbs_per_100g=25,      # 5g for 20g = 25 per 100g
                fat_per_100g=50,        # 10g for 20g = 50 per 100g
                category="nuts",
                suitable_meals=[MealTime.MORNING_SNACK, MealTime.AFTERNOON_SNACK, MealTime.EVENING_SNACK],
                price_per_kg=25.0,
                availability=True
            )
        ]
        return persian_ingredients
    
    def analyze_current_nutrition(self, ingredients: List[Ingredient]) -> Dict[str, float]:
        """Analyze current nutritional content of ingredients"""
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for ingredient in ingredients:
            # Calculate based on typical serving sizes
            if ingredient.name == "Nan-e Barbari":
                serving = 50
            elif ingredient.name == "Persian Butter":
                serving = 10
            elif ingredient.name == "Honey":
                serving = 15
            elif ingredient.name == "Black Tea Leaves":
                serving = 5
            elif ingredient.name == "Mast (Yogurt)":
                serving = 50
            elif ingredient.name == "Fresh Fig":
                serving = 30
            elif ingredient.name == "Persian Nuts Mix":
                serving = 20
            else:
                serving = 100
            
            ratio = serving / 100
            total_calories += ingredient.calories_per_100g * ratio
            total_protein += ingredient.protein_per_100g * ratio
            total_carbs += ingredient.carbs_per_100g * ratio
            total_fat += ingredient.fat_per_100g * ratio
        
        return {
            "calories": total_calories,
            "protein": total_protein,
            "carbs": total_carbs,
            "fat": total_fat
        }
    
    def find_supplementary_ingredients(self, current_nutrition: Dict[str, float], target: NutritionalTarget) -> List[Ingredient]:
        """Find ingredients to supplement missing nutrition"""
        supplements = []
        
        # Calculate deficits
        protein_deficit = max(0, target.protein - current_nutrition["protein"])
        carbs_deficit = max(0, target.carbohydrates - current_nutrition["carbs"])
        fat_deficit = max(0, target.fat - current_nutrition["fat"])
        calories_deficit = max(0, target.calories - current_nutrition["calories"])
        
        print(f"📊 Nutritional Analysis:")
        print(f"   Current: {current_nutrition['calories']:.1f} cal, {current_nutrition['protein']:.1f}g protein, {current_nutrition['carbs']:.1f}g carbs, {current_nutrition['fat']:.1f}g fat")
        print(f"   Target: {target.calories:.1f} cal, {target.protein:.1f}g protein, {target.carbohydrates:.1f}g carbs, {target.fat:.1f}g fat")
        print(f"   Deficits: {calories_deficit:.1f} cal, {protein_deficit:.1f}g protein, {carbs_deficit:.1f}g carbs, {fat_deficit:.1f}g fat")
        
        # Add protein supplements if needed
        if protein_deficit > 0:
            protein_ingredients = [ing for ing in self.ingredients_db if ing.category == "protein" and ing.protein_per_100g > 20]
            if protein_ingredients:
                supplements.append(protein_ingredients[0])
                print(f"   ➕ Adding protein: {protein_ingredients[0].name}")
        
        # Add carb supplements if needed
        if carbs_deficit > 0:
            carb_ingredients = [ing for ing in self.ingredients_db if ing.category == "grain" and ing.carbs_per_100g > 20]
            if carb_ingredients:
                supplements.append(carb_ingredients[0])
                print(f"   ➕ Adding carbs: {carb_ingredients[0].name}")
        
        # Add fat supplements if needed
        if fat_deficit > 0:
            fat_ingredients = [ing for ing in self.ingredients_db if ing.fat_per_100g > 10]
            if fat_ingredients:
                supplements.append(fat_ingredients[0])
                print(f"   ➕ Adding fat: {fat_ingredients[0].name}")
        
        # Add vegetable supplements for fiber and micronutrients
        veg_ingredients = [ing for ing in self.ingredients_db if ing.category == "vegetable"]
        if veg_ingredients:
            supplements.append(veg_ingredients[0])
            print(f"   ➕ Adding vegetable: {veg_ingredients[0].name}")
        
        return supplements
    
    async def optimize_persian_meal(self, target_macros: NutritionalTarget) -> Dict:
        """Main optimization method for Persian meal"""
        print("🍽️  Persian Meal Optimization Starting...")
        print("=" * 50)
        
        # Get Persian ingredients
        persian_ingredients = self.create_persian_ingredients()
        print(f"📋 Original Persian Ingredients ({len(persian_ingredients)} items):")
        for ing in persian_ingredients:
            print(f"   • {ing.name_fa} ({ing.name})")
        
        # Analyze current nutrition
        current_nutrition = self.analyze_current_nutrition(persian_ingredients)
        
        # Find supplements
        supplements = self.find_supplementary_ingredients(current_nutrition, target_macros)
        
        # Combine all ingredients
        all_ingredients = persian_ingredients + supplements
        print(f"\n🔧 Total ingredients after supplementation: {len(all_ingredients)}")
        
        # Create user preferences for Persian cuisine
        user_preferences = UserPreferences(
            dietary_restrictions=[],
            allergies=[],
            preferred_cuisines=["persian"],
            cooking_time_preference="medium"
        )
        
        # Try to optimize with current ingredients first
        print("\n🚀 Attempting optimization with current ingredients...")
        try:
            result = await self.engine.optimize_meal_plan(
                ingredients=all_ingredients,
                target_macros=target_macros,
                user_preferences=user_preferences,
                meal_periods=list(MealTime)
            )
            
            if result and result.get('success', False):
                print("✅ Optimization successful with current ingredients!")
                return self._format_optimization_result(result, persian_ingredients, supplements)
            else:
                print("⚠️  Optimization failed with current ingredients, trying with more supplements...")
                
        except Exception as e:
            print(f"❌ Error in first optimization attempt: {e}")
        
        # If first attempt fails, add more supplements and try again
        additional_supplements = self._get_additional_supplements(target_macros, all_ingredients)
        all_ingredients.extend(additional_supplements)
        
        print(f"\n🔄 Retrying with {len(additional_supplements)} additional supplements...")
        try:
            result = await self.engine.optimize_meal_plan(
                ingredients=all_ingredients,
                target_macros=target_macros,
                user_preferences=user_preferences,
                meal_periods=list(MealTime)
            )
            
            if result and result.get('success', False):
                print("✅ Optimization successful with additional supplements!")
                return self._format_optimization_result(result, persian_ingredients, supplements + additional_supplements)
            else:
                print("❌ Optimization still failed")
                return {"success": False, "error": "Could not optimize meal plan"}
                
        except Exception as e:
            print(f"❌ Error in second optimization attempt: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_additional_supplements(self, target: NutritionalTarget, current_ingredients: List[Ingredient]) -> List[Ingredient]:
        """Get additional supplements if needed"""
        supplements = []
        
        # Add more variety
        categories_needed = ["protein", "grain", "vegetable", "fruit"]
        for category in categories_needed:
            category_ingredients = [ing for ing in self.ingredients_db if ing.category == category]
            if category_ingredients:
                # Find one not already in current ingredients
                for ing in category_ingredients:
                    if ing not in current_ingredients:
                        supplements.append(ing)
                        print(f"   ➕ Additional {category}: {ing.name}")
                        break
        
        return supplements
    
    def _format_optimization_result(self, result: Dict, persian_ingredients: List[Ingredient], supplements: List[Ingredient]) -> Dict:
        """Format the optimization result for display"""
        return {
            "success": True,
            "persian_ingredients": [ing.name for ing in persian_ingredients],
            "supplements_added": [ing.name for ing in supplements],
            "optimization_result": result,
            "total_ingredients": len(persian_ingredients) + len(supplements)
        }

async def main():
    """Main test function"""
    print("🇮🇷 Persian Meal Optimization Test")
    print("=" * 50)
    
    # Create optimizer
    optimizer = PersianMealOptimizer()
    
    # Define target macros (typical daily requirements)
    target_macros = NutritionalTarget(
        calories=2000,
        protein=150,
        carbohydrates=200,
        fat=65
    )
    
    print(f"🎯 Target Nutrition:")
    print(f"   Calories: {target_macros.calories}")
    print(f"   Protein: {target_macros.protein}g")
    print(f"   Carbs: {target_macros.carbohydrates}g")
    print(f"   Fat: {target_macros.fat}g")
    print()
    
    # Run optimization
    result = await optimizer.optimize_persian_meal(target_macros)
    
    if result.get('success'):
        print("\n🎉 OPTIMIZATION COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"📋 Persian Ingredients Used: {', '.join(result['persian_ingredients'])}")
        print(f"🔧 Supplements Added: {', '.join(result['supplements_added'])}")
        print(f"📊 Total Ingredients: {result['total_ingredients']}")
        
        # Display detailed results if available
        if 'optimization_result' in result:
            opt_result = result['optimization_result']
            print(f"\n📈 Optimization Details:")
            print(f"   Method: {opt_result.get('optimization_method', 'Unknown')}")
            print(f"   Success: {opt_result.get('success', 'Unknown')}")
            print(f"   Target Achieved: {opt_result.get('target_achieved', 'Unknown')}")
            
            if 'meal_plans' in opt_result:
                print(f"\n🍽️  Meal Plans:")
                for i, meal in enumerate(opt_result['meal_plans']):
                    print(f"   {i+1}. {meal.meal_time.value}: {meal.total_calories:.1f} kcal")
    else:
        print(f"\n❌ OPTIMIZATION FAILED: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())
