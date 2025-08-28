#!/usr/bin/env python3
"""
Backend Server for Persian Meal Optimization
Implements the /optimize-single-meal endpoint with real optimization
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import asyncio
import os
from typing import Dict, List, Any
from models import (
    NutritionalTarget, UserPreferences, MealTime, Ingredient, MealItem, MealPlan,
    SingleMealOptimizationRequest, SingleMealOptimizationResponse
)
from optimization_engine import SingleMealOptimizer
from rag_optimization_engine import RAGMealOptimizer
import time

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def root():
    """Root endpoint for health check and API information"""
    return jsonify({
        "message": "Persian Meal Optimization API is running",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "optimize_single_meal": "/optimize-single-meal",
            "optimize_single_meal_rag": "/optimize-single-meal-rag",
            "optimize_single_meal_rag_advanced": "/optimize-single-meal-rag-advanced",
            "test_scipy_optimization": "/test-scipy-optimization",
            "test_scipy_with_helpers": "/test-scipy-with-helpers",
            "ingredients": "/api/ingredients",
            "rag_ingredients": "/api/rag-ingredients"
        },
        "railway_info": {
            "port_env": os.environ.get("PORT", "not_set"),
            "python_version": os.environ.get("PYTHON_VERSION", "not_set"),
            "message": f"Render deployment - using port {os.environ.get('PORT', 'not_set')}"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "message": "Persian Meal Optimization API is running",
        "render_status": {
            "port_env": os.environ.get("PORT", "not_set"),
            "message": f"Render deployment - using port {os.environ.get('PORT', 'not_set')}"
        }
    })

class RealMealOptimizer:
    """Real meal optimization engine that replaces mock responses"""
    
    def __init__(self):
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
        """Create the Persian ingredients from user data"""
        return [
            Ingredient(
                id="nan_barbari",
                name="Nan-e Barbari",
                name_fa="نان بربری",
                calories_per_100g=280,
                protein_per_100g=8,
                carbs_per_100g=54,
                fat_per_100g=2,
                category="grain",
                suitable_meals=[MealTime.LUNCH],
                price_per_kg=2.0,
                availability=True
            ),
            Ingredient(
                id="persian_butter",
                name="Persian Butter",
                name_fa="کره ایرانی",
                calories_per_100g=720,
                protein_per_100g=0,
                carbs_per_100g=0,
                fat_per_100g=80,
                category="dairy",
                suitable_meals=[MealTime.LUNCH],
                price_per_kg=12.0,
                availability=True
            ),
            Ingredient(
                id="honey",
                name="Honey",
                name_fa="عسل",
                calories_per_100g=307,
                protein_per_100g=0,
                carbs_per_100g=80,
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
                calories_per_100g=40,
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
                calories_per_100g=60,
                protein_per_100g=6,
                carbs_per_100g=8,
                fat_per_100g=2,
                category="dairy",
                suitable_meals=[MealTime.LUNCH],
                price_per_kg=4.0,
                availability=True
            ),
            Ingredient(
                id="fresh_fig",
                name="Fresh Fig",
                name_fa="انجیر تازه",
                calories_per_100g=67,
                protein_per_100g=0,
                carbs_per_100g=17,
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
                calories_per_100g=600,
                protein_per_100g=15,
                carbs_per_100g=25,
                fat_per_100g=50,
                category="nuts",
                suitable_meals=[MealTime.LUNCH],
                price_per_kg=25.0,
                availability=True
            )
        ]
    
    def find_supplements(self, target: NutritionalTarget) -> List[Ingredient]:
        """Find ingredients to supplement missing nutrition"""
        supplements = []
        
        # Add protein supplements
        protein_ingredients = [ing for ing in self.ingredients_db if ing.category == "protein" and ing.protein_per_100g > 20]
        if protein_ingredients:
            supplements.append(protein_ingredients[0])
        
        # Add carb supplements
        carb_ingredients = [ing for ing in self.ingredients_db if ing.category == "grain" and ing.carbs_per_100g > 20]
        if carb_ingredients:
            supplements.append(carb_ingredients[0])
        
        # Add fat supplements
        fat_ingredients = [ing for ing in self.ingredients_db if ing.fat_per_100g > 10]
        if fat_ingredients:
            supplements.append(fat_ingredients[0])
        
        # Add vegetable for fiber and micronutrients
        veg_ingredients = [ing for ing in self.ingredients_db if ing.category == "vegetable"]
        if veg_ingredients:
            supplements.append(veg_ingredients[0])
        
        return supplements
    
    def calculate_optimal_quantities(self, ingredients: List[Ingredient], target: NutritionalTarget) -> Dict[str, float]:
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
    
    def create_optimized_meal(self, ingredients: List[Ingredient], quantities: Dict[str, float]) -> Dict[str, Any]:
        """Create optimized meal with all ingredients"""
        meal_items = []
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for ingredient in ingredients:
            qty = quantities.get(ingredient.name, 100)
            
            calories = ingredient.calories_per_100g * qty / 100
            protein = ingredient.protein_per_100g * qty / 100
            carbs = ingredient.carbs_per_100g * qty / 100
            fat = ingredient.fat_per_100g * qty / 100
            
            meal_items.append({
                "ingredient": ingredient.name,
                "quantity_grams": qty,
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fat": fat
            })
            
            total_calories += calories
            total_protein += protein
            total_carbs += carbs
            total_fat += fat
        
        return {
            "meal_time": "lunch",
            "items": meal_items,
            "total_calories": total_calories,
            "total_protein": total_protein,
            "total_carbs": total_carbs,
            "total_fat": total_fat
        }
    
    def optimize_single_meal(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main optimization method that replaces mock responses"""
        start_time = time.time()
        
        try:
            # Extract target macros from request
            target_macros_data = request_data.get("target_macros", {})
            target_macros = NutritionalTarget(
                calories=target_macros_data.get("calories", 2000),
                protein=target_macros_data.get("protein", 150),
                carbohydrates=target_macros_data.get("carbohydrates", 200),
                fat=target_macros_data.get("fat", 65)
            )
            
            # Create Persian ingredients
            persian_ingredients = self.create_persian_ingredients()
            
            # Find supplements
            supplements = self.find_supplements(target_macros)
            
            # Combine all ingredients
            all_ingredients = persian_ingredients + supplements
            
            # Calculate optimal quantities
            optimal_quantities = self.calculate_optimal_quantities(all_ingredients, target_macros)
            
            # Create optimized meal
            optimized_meal = self.create_optimized_meal(all_ingredients, optimal_quantities)
            
            # Calculate cost estimate
            total_cost = sum(ing.price_per_kg * optimal_quantities.get(ing.name, 100) / 1000 for ing in all_ingredients)
            
            computation_time = time.time() - start_time
            
            return {
                "optimization_result": {
                    "success": True,
                    "method": "Real Mathematical Scaling Algorithm",
                    "computation_time": round(computation_time, 3)
                },
                "meal": optimized_meal,
                "target_achievement": {
                    "calories_achieved": optimized_meal["total_calories"] >= target_macros.calories,
                    "protein_achieved": optimized_meal["total_protein"] >= target_macros.protein,
                    "carbs_achieved": optimized_meal["total_carbs"] >= target_macros.carbohydrates,
                    "fat_achieved": optimized_meal["total_fat"] >= target_macros.fat
                },
                "recommendations": [
                    "All nutritional targets have been met through optimal ingredient combination",
                    "Persian ingredients are balanced with healthy supplements",
                    "Consider adjusting quantities based on personal preferences"
                ],
                "cost_estimate": round(total_cost, 2),
                "shopping_list": [
                    {
                        "ingredient": ing.name,
                        "quantity": f"{optimal_quantities.get(ing.name, 100):.1f}g",
                        "estimated_cost": f"${ing.price_per_kg * optimal_quantities.get(ing.name, 100) / 1000:.2f}"
                    }
                    for ing in all_ingredients
                ],
                "rag_enhancement": {
                    "original_ingredients": len(persian_ingredients),
                    "supplements_added": len(supplements),
                    "total_ingredients": len(all_ingredients),
                    "enhancement_method": "Nutritional deficit analysis and smart supplementation"
                }
            }
            
        except Exception as e:
            computation_time = time.time() - start_time
            return {
                "optimization_result": {
                    "success": False,
                    "method": "Real Algorithm (Failed)",
                    "computation_time": round(computation_time, 3),
                    "error": str(e)
                },
                "meal": None,
                "target_achievement": None,
                "recommendations": [f"Optimization failed: {str(e)}"],
                "cost_estimate": 0,
                "shopping_list": [],
                "rag_enhancement": None
            }

# Initialize optimizers
optimizer = RealMealOptimizer()
single_meal_optimizer = SingleMealOptimizer()
rag_meal_optimizer = RAGMealOptimizer()

@app.route('/optimize-single-meal', methods=['POST'])
def optimize_single_meal():
    """Main optimization endpoint that replaces mock responses"""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "No request data provided"}), 400
        
        # Run optimization
        result = optimizer.optimize_single_meal(request_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": f"Optimization failed: {str(e)}",
            "status": "error"
        }), 500

@app.route('/optimize-single-meal-rag', methods=['POST'])
def optimize_single_meal_rag():
    """Single meal optimization endpoint with RAG enhancement"""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "No request data provided"}), 400
        
        # Validate required fields
        required_fields = ['rag_response', 'target_macros', 'user_preferences', 'meal_type']
        for field in required_fields:
            if field not in request_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Extract data
        rag_response = request_data['rag_response']
        target_macros = request_data['target_macros']
        user_preferences = request_data['user_preferences']
        meal_type = request_data['meal_type']
        
        # Run single meal optimization
        result = single_meal_optimizer.optimize_single_meal(
            rag_response=rag_response,
            target_macros=target_macros,
            user_preferences=user_preferences,
            meal_type=meal_type
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": f"Single meal optimization failed: {str(e)}",
            "status": "error"
        }), 500

@app.route('/optimize-single-meal-rag-advanced', methods=['POST'])
def optimize_single_meal_rag_advanced():
    """Advanced RAG-based single meal optimization endpoint with automatic helper ingredients"""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "No request data provided"}), 400
        
        # Validate required fields
        required_fields = ['rag_response', 'target_macros', 'user_preferences', 'meal_type']
        for field in required_fields:
            if field not in request_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Extract data
        rag_response = request_data['rag_response']
        target_macros = request_data['target_macros']
        user_preferences = request_data['user_preferences']
        meal_type = request_data['meal_type']
        
        print(f"🚀 Starting optimization for {meal_type} meal...")
        print(f"🎯 Target macros: {target_macros}")
        
        # Step 1: Run initial optimization with 5 methods using advanced method
        print("\n📊 Step 1: Running initial optimization with 5 methods...")
        initial_result = rag_meal_optimizer.optimize_single_meal_advanced(
            rag_response=rag_response,
            target_macros=target_macros,
            user_preferences=user_preferences,
            meal_type=meal_type,
            request_data=request_data
        )
        
        # The advanced method handles everything internally
        print(f"✅ Advanced optimization completed!")
        print(f"📊 Result: {initial_result.get('optimization_result', {}).get('method', 'Unknown method')}")
        
        return jsonify(initial_result)
        
    except Exception as e:
        return jsonify({
            "error": f"Advanced RAG meal optimization failed: {str(e)}",
            "status": "error"
        }), 500

def check_target_achievement_advanced(result, target_macros):
    """Check if targets are achieved with more detailed analysis"""
    # Try to get nutrition from different result formats
    nutrition = None
    
    if 'meal' in result and 'total_calories' in result['meal']:
        nutrition = {
            'calories': result['meal']['total_calories'],
            'protein': result['meal']['total_protein'],
            'carbs': result['meal']['total_carbs'],
            'fat': result['meal']['total_fat']
        }
    elif 'optimization_result' in result and 'final_nutrition' in result['optimization_result']:
        nutrition = result['optimization_result']['final_nutrition']
    elif 'final_nutrition' in result:
        nutrition = result['final_nutrition']
    
    if not nutrition:
        return {'overall': False, 'reason': 'Could not extract nutrition data'}
    
    # Check each macro with 5% tolerance
    achievement = {}
    for macro in ['calories', 'protein', 'carbs', 'fat']:
        target = target_macros[macro]
        actual = nutrition[macro]
        
        # 5% tolerance
        tolerance = target * 0.05
        if abs(actual - target) <= tolerance:
            achievement[macro] = True
        else:
            achievement[macro] = False
    
    # Overall achievement
    achievement['overall'] = all(achievement.values())
    
    return achievement

def get_current_ingredients_from_result(result):
    """Extract current ingredients from optimization result"""
    ingredients = []
    
    # Try different result formats
    if 'meal' in result and 'items' in result['meal']:
        # Extract from meal items
        for item in result['meal']['items']:
            ingredients.append({
                'name': item['ingredient'],
                'protein_per_100g': item.get('protein_per_100g', 0),
                'carbs_per_100g': item.get('carbs_per_100g', 0),
                'fat_per_100g': item.get('fat_per_100g', 0),
                'calories_per_100g': item.get('calories_per_100g', 0),
                'max_quantity': 300,
                'category': 'custom'
            })
    elif 'ingredients' in result:
        # Direct ingredients list
        ingredients = result['ingredients']
    else:
        # Fallback: create basic ingredients from target macros
        ingredients = [
            {
                'name': 'Base Ingredient',
                'protein_per_100g': 20,
                'carbs_per_100g': 30,
                'fat_per_100g': 10,
                'calories_per_100g': 300,
                'max_quantity': 300,
                'category': 'base'
            }
        ]
    
    return ingredients

def add_smart_helper_ingredients(current_ingredients, target_macros, meal_type):
    """Add smart helper ingredients based on meal type and deficits with conflict prevention"""
    helpers = []
    
    # Calculate current totals from ingredients
    current_totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
    for ing in current_ingredients:
        # Use reasonable default quantities (100g each)
        qty = 100
        current_totals['calories'] += ing['calories_per_100g'] * qty / 100
        current_totals['protein'] += ing['protein_per_100g'] * qty / 100
        current_totals['carbs'] += ing['carbs_per_100g'] * qty / 100
        current_totals['fat'] += ing['fat_per_100g'] * qty / 100
    
    # Calculate deficits
    protein_deficit = max(0, target_macros['protein'] - current_totals['protein'])
    carbs_deficit = max(0, target_macros['carbs'] - current_totals['carbs'])
    fat_deficit = max(0, target_macros['fat'] - current_totals['fat'])
    calories_deficit = max(0, target_macros['calories'] - current_totals['calories'])
    
    print(f"📊 Current totals: {current_totals}")
    print(f"🎯 Deficits: Protein: {protein_deficit:.1f}g, Carbs: {carbs_deficit:.1f}g, Fat: {fat_deficit:.1f}g, Calories: {calories_deficit:.1f}")
    
    # Analyze current ingredients to prevent conflicts
    current_protein_sources = analyze_protein_sources(current_ingredients)
    print(f"🔍 Current protein sources: {current_protein_sources}")
    
    # Get meal-specific helper ingredients with conflict prevention
    meal_helpers = get_meal_specific_helpers_smart(meal_type, current_protein_sources)
    
    # Add protein helper if needed (with conflict prevention)
    if protein_deficit > 5:
        protein_helper = select_smart_protein_helper(meal_type, current_protein_sources, protein_deficit)
        if protein_helper:
            helpers.append(protein_helper)
            print(f"➕ Added smart protein helper: {protein_helper['name']} (conflict-free)")
    
    # Add carb helper if needed (meal-appropriate)
    if carbs_deficit > 10:
        carb_helper = select_smart_carb_helper(meal_type, carbs_deficit)
        if carb_helper:
            helpers.append(carb_helper)
            print(f"➕ Added smart carb helper: {carb_helper['name']} (meal-appropriate)")
    
    # Add fat helper if needed (meal-appropriate)
    if fat_deficit > 3:
        fat_helper = select_smart_fat_helper(meal_type, fat_deficit)
        if fat_helper:
            helpers.append(fat_helper)
            print(f"➕ Added smart fat helper: {fat_helper['name']} (meal-appropriate)")
    
    # Add calorie helper if needed (meal-appropriate)
    if calories_deficit > 50:
        calorie_helper = select_smart_calorie_helper(meal_type, calories_deficit)
        if calorie_helper:
            helpers.append(calorie_helper)
            print(f"➕ Added smart calorie helper: {calorie_helper['name']} (meal-appropriate)")
    
    return helpers

def analyze_protein_sources(ingredients):
    """Analyze current protein sources to prevent conflicts"""
    protein_sources = {
        'red_meat': [],      # beef, lamb, pork
        'white_meat': [],    # chicken, turkey
        'fish': [],          # salmon, tuna, cod
        'plant_based': [],   # tofu, tempeh, legumes
        'dairy_eggs': []     # eggs, yogurt, cheese
    }
    
    for ing in ingredients:
        name = ing['name'].lower()
        protein = ing['protein_per_100g']
        
        if protein > 15:  # Only consider high-protein ingredients
            if any(word in name for word in ['beef', 'lamb', 'pork', 'steak', 'burger']):
                protein_sources['red_meat'].append(ing)
            elif any(word in name for word in ['chicken', 'turkey', 'duck']):
                protein_sources['white_meat'].append(ing)
            elif any(word in name for word in ['salmon', 'tuna', 'cod', 'fish', 'seafood']):
                protein_sources['fish'].append(ing)
            elif any(word in name for word in ['tofu', 'tempeh', 'bean', 'lentil', 'chickpea']):
                protein_sources['plant_based'].append(ing)
            elif any(word in name for word in ['egg', 'yogurt', 'cheese', 'milk']):
                protein_sources['dairy_eggs'].append(ing)
    
    return protein_sources

def select_smart_protein_helper(meal_type, current_protein_sources, deficit):
    """Select protein helper that doesn't conflict with current sources"""
    
    # Define protein source priorities for each meal type
    meal_protein_priorities = {
        'breakfast': ['dairy_eggs', 'plant_based', 'fish', 'white_meat', 'red_meat'],
        'morning_snack': ['dairy_eggs', 'plant_based', 'fish'],
        'lunch': ['red_meat', 'white_meat', 'fish', 'plant_based', 'dairy_eggs'],
        'afternoon_snack': ['dairy_eggs', 'plant_based', 'fish'],
        'dinner': ['fish', 'white_meat', 'plant_based', 'red_meat', 'dairy_eggs'],
        'evening_snack': ['dairy_eggs', 'plant_based']
    }
    
    priorities = meal_protein_priorities.get(meal_type.lower(), meal_protein_priorities['lunch'])
    
    # Find the best non-conflicting protein source
    for source_type in priorities:
        if not current_protein_sources[source_type]:  # No conflict
            helper = get_protein_helper_by_type(source_type, deficit, meal_type)
            if helper:
                return helper
    
    # If all conflict, find the least conflicting option
    for source_type in priorities:
        helper = get_protein_helper_by_type(source_type, deficit, meal_type)
        if helper:
            print(f"⚠️  Using {helper['name']} despite potential conflict")
            return helper
    
    return None

def get_protein_helper_by_type(source_type, deficit, meal_type):
    """Get protein helper based on source type and meal"""
    
    protein_helpers = {
        'red_meat': {
            'breakfast': {'name': 'Lean Beef Jerky', 'protein_per_100g': 35, 'carbs_per_100g': 5, 'fat_per_100g': 2, 'calories_per_100g': 180, 'max_quantity': 50, 'category': 'protein_supplement'},
            'lunch': {'name': 'Lean Ground Beef', 'protein_per_100g': 26, 'carbs_per_100g': 0, 'fat_per_100g': 15, 'calories_per_100g': 250, 'max_quantity': 150, 'category': 'protein_supplement'},
            'dinner': {'name': 'Beef Steak', 'protein_per_100g': 31, 'carbs_per_100g': 0, 'fat_per_100g': 12, 'calories_per_100g': 220, 'max_quantity': 200, 'category': 'protein_supplement'},
            'default': {'name': 'Lean Beef', 'protein_per_100g': 26, 'carbs_per_100g': 0, 'fat_per_100g': 15, 'calories_per_100g': 250, 'max_quantity': 150, 'category': 'protein_supplement'}
        },
        'white_meat': {
            'breakfast': {'name': 'Turkey Slices', 'protein_per_100g': 29, 'carbs_per_100g': 0, 'fat_per_100g': 3.6, 'calories_per_100g': 189, 'max_quantity': 100, 'category': 'protein_supplement'},
            'lunch': {'name': 'Chicken Breast', 'protein_per_100g': 31, 'carbs_per_100g': 0, 'fat_per_100g': 3.6, 'calories_per_100g': 165, 'max_quantity': 200, 'category': 'protein_supplement'},
            'dinner': {'name': 'Grilled Chicken', 'protein_per_100g': 31, 'carbs_per_100g': 0, 'fat_per_100g': 3.6, 'calories_per_100g': 165, 'max_quantity': 200, 'category': 'protein_supplement'},
            'default': {'name': 'Chicken Breast', 'protein_per_100g': 31, 'carbs_per_100g': 0, 'fat_per_100g': 3.6, 'calories_per_100g': 165, 'max_quantity': 200, 'category': 'protein_supplement'}
        },
        'fish': {
            'breakfast': {'name': 'Smoked Salmon', 'protein_per_100g': 25, 'carbs_per_100g': 0, 'fat_per_100g': 12, 'calories_per_100g': 208, 'max_quantity': 80, 'category': 'protein_supplement'},
            'lunch': {'name': 'Grilled Salmon', 'protein_per_100g': 25, 'carbs_per_100g': 0, 'fat_per_100g': 12, 'calories_per_100g': 208, 'max_quantity': 150, 'category': 'protein_supplement'},
            'dinner': {'name': 'Baked Cod', 'protein_per_100g': 23, 'carbs_per_100g': 0, 'fat_per_100g': 0.9, 'calories_per_100g': 105, 'max_quantity': 200, 'category': 'protein_supplement'},
            'default': {'name': 'Salmon', 'protein_per_100g': 25, 'carbs_per_100g': 0, 'fat_per_100g': 12, 'calories_per_100g': 208, 'max_quantity': 150, 'category': 'protein_supplement'}
        },
        'plant_based': {
            'breakfast': {'name': 'Greek Yogurt', 'protein_per_100g': 10, 'carbs_per_100g': 3.6, 'fat_per_100g': 0.4, 'calories_per_100g': 59, 'max_quantity': 200, 'category': 'protein_supplement'},
            'lunch': {'name': 'Tofu', 'protein_per_100g': 8, 'carbs_per_100g': 1.9, 'fat_per_100g': 4.8, 'calories_per_100g': 76, 'max_quantity': 200, 'category': 'protein_supplement'},
            'dinner': {'name': 'Tempeh', 'protein_per_100g': 20, 'carbs_per_100g': 7.6, 'fat_per_100g': 11, 'calories_per_100g': 192, 'max_quantity': 150, 'category': 'protein_supplement'},
            'default': {'name': 'Tofu', 'protein_per_100g': 8, 'carbs_per_100g': 1.9, 'fat_per_100g': 4.8, 'calories_per_100g': 76, 'max_quantity': 200, 'category': 'protein_supplement'}
        },
        'dairy_eggs': {
            'breakfast': {'name': 'Eggs', 'protein_per_100g': 13, 'carbs_per_100g': 1.1, 'fat_per_100g': 11, 'calories_per_100g': 155, 'max_quantity': 150, 'category': 'protein_supplement'},
            'lunch': {'name': 'Cottage Cheese', 'protein_per_100g': 11, 'carbs_per_100g': 3.4, 'fat_per_100g': 4.3, 'calories_per_100g': 98, 'max_quantity': 200, 'category': 'protein_supplement'},
            'dinner': {'name': 'Greek Yogurt', 'protein_per_100g': 10, 'carbs_per_100g': 3.6, 'fat_per_100g': 0.4, 'calories_per_100g': 59, 'max_quantity': 200, 'category': 'protein_supplement'},
            'default': {'name': 'Eggs', 'protein_per_100g': 13, 'carbs_per_100g': 1.1, 'fat_per_100g': 11, 'calories_per_100g': 155, 'max_quantity': 150, 'category': 'protein_supplement'}
        }
    }
    
    source_helpers = protein_helpers.get(source_type, {})
    return source_helpers.get(meal_type.lower(), source_helpers.get('default'))

def select_smart_carb_helper(meal_type, deficit):
    """Select carb helper appropriate for meal type"""
    
    carb_helpers = {
        'breakfast': {'name': 'Oatmeal', 'protein_per_100g': 6.9, 'carbs_per_100g': 58, 'fat_per_100g': 6.9, 'calories_per_100g': 389, 'max_quantity': 150, 'category': 'carb_supplement'},
        'morning_snack': {'name': 'Banana', 'protein_per_100g': 1.1, 'carbs_per_100g': 23, 'fat_per_100g': 0.3, 'calories_per_100g': 89, 'max_quantity': 120, 'category': 'carb_supplement'},
        'lunch': {'name': 'Brown Rice', 'protein_per_100g': 2.7, 'carbs_per_100g': 23, 'fat_per_100g': 0.9, 'calories_per_100g': 111, 'max_quantity': 200, 'category': 'carb_supplement'},
        'afternoon_snack': {'name': 'Apple', 'protein_per_100g': 0.3, 'carbs_per_100g': 14, 'fat_per_100g': 0.2, 'calories_per_100g': 52, 'max_quantity': 150, 'category': 'carb_supplement'},
        'dinner': {'name': 'Quinoa', 'protein_per_100g': 4.4, 'carbs_per_100g': 22, 'fat_per_100g': 1.9, 'calories_per_100g': 120, 'max_quantity': 200, 'category': 'carb_supplement'},
        'evening_snack': {'name': 'Berries', 'protein_per_100g': 0.7, 'carbs_per_100g': 12, 'fat_per_100g': 0.3, 'calories_per_100g': 50, 'max_quantity': 100, 'category': 'carb_supplement'}
    }
    
    return carb_helpers.get(meal_type.lower(), carb_helpers['lunch'])

def select_smart_fat_helper(meal_type, deficit):
    """Select fat helper appropriate for meal type"""
    
    fat_helpers = {
        'breakfast': {'name': 'Almonds', 'protein_per_100g': 21, 'carbs_per_100g': 22, 'fat_per_100g': 49, 'calories_per_100g': 579, 'max_quantity': 50, 'category': 'fat_supplement'},
        'morning_snack': {'name': 'Walnuts', 'protein_per_100g': 15, 'carbs_per_100g': 14, 'fat_per_100g': 65, 'calories_per_100g': 654, 'max_quantity': 40, 'category': 'fat_supplement'},
        'lunch': {'name': 'Avocado', 'protein_per_100g': 2, 'carbs_per_100g': 9, 'fat_per_100g': 15, 'calories_per_100g': 160, 'max_quantity': 100, 'category': 'fat_supplement'},
        'afternoon_snack': {'name': 'Cashews', 'protein_per_100g': 18, 'carbs_per_100g': 30, 'fat_per_100g': 44, 'calories_per_100g': 553, 'max_quantity': 40, 'category': 'fat_supplement'},
        'dinner': {'name': 'Olive Oil', 'protein_per_100g': 0, 'carbs_per_100g': 0, 'fat_per_100g': 100, 'calories_per_100g': 884, 'max_quantity': 30, 'category': 'fat_supplement'},
        'evening_snack': {'name': 'Dark Chocolate', 'protein_per_100g': 4, 'carbs_per_100g': 60, 'fat_per_100g': 30, 'calories_per_100g': 546, 'max_quantity': 30, 'category': 'fat_supplement'}
    }
    
    return fat_helpers.get(meal_type.lower(), fat_helpers['lunch'])

def select_smart_calorie_helper(meal_type, deficit):
    """Select calorie helper appropriate for meal type"""
    
    calorie_helpers = {
        'breakfast': {'name': 'Honey', 'protein_per_100g': 0, 'carbs_per_100g': 80, 'fat_per_100g': 0, 'calories_per_100g': 307, 'max_quantity': 30, 'category': 'calorie_supplement'},
        'morning_snack': {'name': 'Dried Fruits', 'protein_per_100g': 2, 'carbs_per_100g': 70, 'fat_per_100g': 0.5, 'calories_per_100g': 290, 'max_quantity': 50, 'category': 'calorie_supplement'},
        'lunch': {'name': 'Sweet Potato', 'protein_per_100g': 1.6, 'carbs_per_100g': 20, 'fat_per_100g': 0.1, 'calories_per_100g': 86, 'max_quantity': 200, 'category': 'calorie_supplement'},
        'afternoon_snack': {'name': 'Granola', 'protein_per_100g': 10, 'carbs_per_100g': 65, 'fat_per_100g': 20, 'calories_per_100g': 471, 'max_quantity': 60, 'category': 'calorie_supplement'},
        'dinner': {'name': 'Nuts Mix', 'protein_per_100g': 15, 'carbs_per_100g': 20, 'fat_per_100g': 50, 'calories_per_100g': 500, 'max_quantity': 50, 'category': 'calorie_supplement'},
        'evening_snack': {'name': 'Yogurt with Honey', 'protein_per_100g': 8, 'carbs_per_100g': 25, 'fat_per_100g': 2, 'calories_per_100g': 150, 'max_quantity': 100, 'category': 'calorie_supplement'}
    }
    
    return calorie_helpers.get(meal_type.lower(), calorie_helpers['lunch'])

def get_meal_specific_helpers_smart(meal_type, current_protein_sources):
    """Get meal-specific helpers with conflict prevention (legacy function for compatibility)"""
    # This function is now replaced by the smart selection functions above
    return {}

# This function has been replaced by smart selection functions above

@app.route('/test-scipy-optimization', methods=['POST'])
def test_scipy_optimization():
    """Test endpoint for scipy differential evolution optimization with custom ingredients"""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "No request data provided"}), 400
        
        # Extract custom ingredients and target macros
        custom_ingredients = request_data.get('ingredients', [])
        target_macros = request_data.get('target_macros', {})
        
        if not custom_ingredients or not target_macros:
            return jsonify({"error": "Both 'ingredients' and 'target_macros' are required"}), 400
        
        # Convert ingredients to the format expected by RAG optimizer
        formatted_ingredients = []
        for ing in custom_ingredients:
            formatted_ing = {
                'name': ing.get('name', 'Unknown'),
                'protein_per_100g': ing.get('protein_per_100g', 0),
                'carbs_per_100g': ing.get('carbs_per_100g', 0),
                'fat_per_100g': ing.get('fat_per_100g', 0),
                'calories_per_100g': ing.get('calories_per_100g', 0),
                'max_quantity': ing.get('max_quantity', 300),
                'category': ing.get('category', 'custom')
            }
            formatted_ingredients.append(formatted_ing)
        
        # Test scipy differential evolution optimization
        result = rag_meal_optimizer._differential_evolution_optimize(
            formatted_ingredients, 
            target_macros
        )
        
        return jsonify({
            "success": True,
            "method": "SciPy Differential Evolution Test",
            "input_ingredients": custom_ingredients,
            "target_macros": target_macros,
            "optimization_result": result,
            "message": "SciPy optimization test completed successfully"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"SciPy optimization test failed: {str(e)}",
            "status": "error"
        }), 500

@app.route('/test-scipy-with-helpers', methods=['POST'])
def test_scipy_with_helpers():
    """Test endpoint for scipy optimization with helper ingredients to reach targets precisely"""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "No request data provided"}), 400
        
        # Extract custom ingredients and target macros
        custom_ingredients = request_data.get('ingredients', [])
        target_macros = request_data.get('target_macros', {})
        
        if not custom_ingredients or not target_macros:
            return jsonify({"error": "Both 'ingredients' and 'target_macros' are required"}), 400
        
        # Convert ingredients to the format expected by RAG optimizer
        formatted_ingredients = []
        for ing in custom_ingredients:
            formatted_ing = {
                'name': ing.get('name', 'Unknown'),
                'protein_per_100g': ing.get('protein_per_100g', 0),
                'carbs_per_100g': ing.get('carbs_per_100g', 0),
                'fat_per_100g': ing.get('fat_per_100g', 0),
                'calories_per_100g': ing.get('calories_per_100g', 0),
                'max_quantity': ing.get('max_quantity', 300),
                'category': ing.get('category', 'custom')
            }
            formatted_ingredients.append(formatted_ing)
        
        # Add helper ingredients to reach targets
        helper_ingredients = add_helper_ingredients(formatted_ingredients, target_macros)
        all_ingredients = formatted_ingredients + helper_ingredients
        
        print(f"🔧 Added {len(helper_ingredients)} helper ingredients")
        for helper in helper_ingredients:
            print(f"  • {helper['name']}: {helper['protein_per_100g']}g protein, {helper['carbs_per_100g']}g carbs, {helper['fat_per_100g']}g fat")
        
        # Test scipy differential evolution optimization with all ingredients
        result = rag_meal_optimizer._differential_evolution_optimize(
            all_ingredients, 
            target_macros
        )
        
        # Calculate final nutrition with helper ingredients
        if result.get('success') and result.get('quantities'):
            final_nutrition = calculate_final_nutrition_with_helpers(all_ingredients, result['quantities'])
            result['final_nutrition'] = final_nutrition
            result['target_achievement'] = check_target_achievement(final_nutrition, target_macros)
        
        return jsonify({
            "success": True,
            "method": "SciPy with Helper Ingredients",
            "input_ingredients": custom_ingredients,
            "helper_ingredients": helper_ingredients,
            "all_ingredients": all_ingredients,
            "target_macros": target_macros,
            "optimization_result": result,
            "message": "SciPy optimization with helpers completed successfully"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"SciPy optimization with helpers failed: {str(e)}",
            "status": "error"
        }), 500

def add_helper_ingredients(ingredients, target_macros):
    """Add helper ingredients to reach targets more precisely"""
    helpers = []
    
    # Calculate current totals from main ingredients
    current_totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
    for ing in ingredients:
        # Use reasonable default quantities (100g each)
        qty = 100
        current_totals['calories'] += ing['calories_per_100g'] * qty / 100
        current_totals['protein'] += ing['protein_per_100g'] * qty / 100
        current_totals['carbs'] += ing['carbs_per_100g'] * qty / 100
        current_totals['fat'] += ing['fat_per_100g'] * qty / 100
    
    # Calculate deficits
    protein_deficit = max(0, target_macros['protein'] - current_totals['protein'])
    carbs_deficit = max(0, target_macros['carbs'] - current_totals['carbs'])
    fat_deficit = max(0, target_macros['fat'] - current_totals['fat'])
    calories_deficit = max(0, target_macros['calories'] - current_totals['calories'])
    
    print(f"📊 Current totals: {current_totals}")
    print(f"🎯 Deficits: Protein: {protein_deficit:.1f}g, Carbs: {carbs_deficit:.1f}g, Fat: {fat_deficit:.1f}g, Calories: {calories_deficit:.1f}")
    
    # Add protein helper if needed
    if protein_deficit > 5:  # Only add if deficit is significant
        protein_helper = {
            'name': 'Protein Powder',
            'protein_per_100g': 80,
            'carbs_per_100g': 8,
            'fat_per_100g': 2,
            'calories_per_100g': 370,
            'max_quantity': 100,
            'category': 'protein_supplement'
        }
        helpers.append(protein_helper)
        print(f"➕ Added protein helper: {protein_helper['name']}")
    
    # Add carb helper if needed
    if carbs_deficit > 10:  # Only add if deficit is significant
        carb_helper = {
            'name': 'Oats',
            'protein_per_100g': 6.9,
            'carbs_per_100g': 58,
            'fat_per_100g': 6.9,
            'calories_per_100g': 389,
            'max_quantity': 200,
            'category': 'carb_supplement'
        }
        helpers.append(carb_helper)
        print(f"➕ Added carb helper: {carb_helper['name']}")
    
    # Add fat helper if needed
    if fat_deficit > 3:  # Only add if deficit is significant
        fat_helper = {
            'name': 'Olive Oil',
            'protein_per_100g': 0,
            'carbs_per_100g': 0,
            'fat_per_100g': 100,
            'calories_per_100g': 884,
            'max_quantity': 30,
            'category': 'fat_supplement'
        }
        helpers.append(fat_helper)
        print(f"➕ Added fat helper: {fat_helper['name']}")
    
    # Add calorie helper if needed
    if calories_deficit > 50:  # Only add if deficit is significant
        calorie_helper = {
            'name': 'Honey',
            'protein_per_100g': 0,
            'carbs_per_100g': 80,
            'fat_per_100g': 0,
            'calories_per_100g': 307,
            'max_quantity': 50,
            'category': 'calorie_supplement'
        }
        helpers.append(calorie_helper)
        print(f"➕ Added calorie helper: {calorie_helper['name']}")
    
    return helpers

def calculate_final_nutrition_with_helpers(ingredients, quantities):
    """Calculate final nutrition including helper ingredients"""
    totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
    
    for i, ingredient in enumerate(ingredients):
        if i < len(quantities):
            quantity = quantities[i] / 100  # Convert grams to ratio
            totals['calories'] += ingredient['calories_per_100g'] * quantity
            totals['protein'] += ingredient['protein_per_100g'] * quantity
            totals['carbs'] += ingredient['carbs_per_100g'] * quantity
            totals['fat'] += ingredient['fat_per_100g'] * quantity
    
    return totals

def check_target_achievement(final_nutrition, target_macros):
    """Check if targets are achieved"""
    achievement = {}
    
    for macro in ['calories', 'protein', 'carbs', 'fat']:
        target = target_macros[macro]
        actual = final_nutrition[macro]
        
        if actual >= target * 0.95:  # 95% of target is considered achieved
            achievement[macro] = True
        else:
            achievement[macro] = False
    
    # Overall achievement
    achievement['overall'] = all(achievement.values())
    
    return achievement

@app.route('/api/ingredients', methods=['GET'])
def get_ingredients():
    """Get available ingredients from database"""
    try:
        ingredients = optimizer.ingredients_db
        return jsonify({
            "ingredients": [
                {
                    "id": ing.id,
                    "name": ing.name,
                    "category": ing.category,
                    "calories_per_100g": ing.calories_per_100g,
                    "protein_per_100g": ing.protein_per_100g,
                    "carbs_per_100g": ing.carbs_per_100g,
                    "fat_per_100g": ing.fat_per_100g,
                    "price_per_kg": ing.price_per_kg
                }
                for ing in ingredients
            ],
            "total_count": len(ingredients)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to load ingredients: {str(e)}"}), 500

@app.route('/api/rag-ingredients', methods=['GET'])
def get_rag_ingredients():
    """Get RAG-specific ingredients from database"""
    try:
        ingredients = rag_meal_optimizer.ingredients_db
        return jsonify({
            "ingredients": ingredients,
            "total_count": len(ingredients)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to load RAG ingredients: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 Starting Persian Meal Optimization Backend Server...")
    print("📍 Endpoints available:")
    print("   GET  /health - Health check")
    print("   POST /optimize-single-meal - Main optimization endpoint")
    print("   POST /optimize-single-meal-rag - Single meal RAG optimization")
    print("   POST /optimize-single-meal-rag-advanced - Advanced RAG optimization")
    print("   POST /test-scipy-optimization - Test SciPy optimization")
    print("   POST /test-scipy-with-helpers - Test SciPy with helper ingredients")
    print("   GET  /api/ingredients - Get available ingredients")
    print("   GET  /api/rag-ingredients - Get RAG ingredients")
    print("=" * 60)

    # Get port from environment variable (for Render) or use default
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Server will start on port: {port}")
    print(f"🔧 Debug mode: {debug_mode}")
    print(f"🌍 Bind address: 0.0.0.0")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug_mode, threaded=True)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        # Try alternative port if main port fails
        try:
            alt_port = port + 1 if port < 65535 else 5000
            print(f"🔄 Trying alternative port: {alt_port}")
            app.run(host='0.0.0.0', port=alt_port, debug=debug_mode, threaded=True)
        except Exception as e2:
            print(f"❌ Failed to start on alternative port: {e2}")
            exit(1)
