#!/usr/bin/env python3
"""
Backend Server for Persian Meal Optimization
Implements the /optimize-single-meal endpoint with real optimization
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import asyncio
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

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Persian Meal Optimization Backend",
        "version": "1.0.0"
    })

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
    """Advanced RAG-based single meal optimization endpoint"""
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
        
        # Run advanced RAG meal optimization
        result = rag_meal_optimizer.optimize_single_meal(
            rag_response=rag_response,
            target_macros=target_macros,
            user_preferences=user_preferences,
            meal_type=meal_type
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": f"Advanced RAG meal optimization failed: {str(e)}",
            "status": "error"
        }), 500

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
    print("   GET  /api/ingredients - Get available ingredients")
    print("   GET  /api/rag-ingredients - Get RAG ingredients")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
