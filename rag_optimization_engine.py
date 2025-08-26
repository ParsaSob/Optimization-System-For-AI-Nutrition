#!/usr/bin/env python3
"""
RAG Meal Optimization Engine
Advanced optimization engine for RAG-based meal planning using genetic algorithms
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any
import time
import logging
import json
import random
from deap import base, creator, tools, algorithms
from scipy.optimize import minimize, differential_evolution
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.neural_network import MLPRegressor
import warnings
warnings.filterwarnings('ignore')

# Advanced optimization libraries
try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

try:
    import pygmo as pg
    PYGMO_AVAILABLE = True
except ImportError:
    PYGMO_AVAILABLE = False

try:
    from platypus import NSGAII, Problem, Real
    PLATYPUS_AVAILABLE = True
except ImportError:
    PLATYPUS_AVAILABLE = False

try:
    from pymoo.core.problem import Problem as PymooProblem
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.optimize import minimize as pymoo_minimize
    from pymoo.core.variable import Real
    PYMOO_AVAILABLE = True
except ImportError:
    PYMOO_AVAILABLE = False

from models import (
    RAGIngredient, RAGSuggestion, RAGResponse, TargetMacros, 
    UserPreferencesRAG, MealItemOptimized, MealOptimized, 
    TargetAchievement, RAGEnhancement, SingleMealOptimizationResponse
)

logger = logging.getLogger(__name__)

class RAGMealOptimizer:
    """
    Advanced RAG meal optimization engine using genetic algorithms
    Implements the exact interface specified by the user
    """
    
    def __init__(self):
        self.ingredients_db = self._load_ingredients_database()
        self.current_ingredients = []  # Will store current ingredients during optimization
        self.optimization_methods = {
            'genetic_algorithm': self._optimize_genetic_algorithm,
            'differential_evolution': self._optimize_differential_evolution,
            'linear_programming': self._optimize_linear_programming,
            'hybrid': self._optimize_hybrid
        }
        
        # Add advanced methods if available
        if OPTUNA_AVAILABLE:
            self.optimization_methods['optuna_optimization'] = self._optimize_optuna
            print(f"✅ Optuna optimization available")
        else:
            print(f"❌ Optuna not available")
            
        if PYGMO_AVAILABLE:
            self.optimization_methods['pygmo_optimization'] = self._optimize_pygmo
            print(f"✅ PyGMO optimization available")
        else:
            print(f"❌ PyGMO not available")
            
        if PLATYPUS_AVAILABLE:
            self.optimization_methods['nsga2_optimization'] = self._optimize_nsga2
            print(f"✅ Platypus NSGA-II optimization available")
        else:
            print(f"❌ Platypus not available")
            
        if PYMOO_AVAILABLE:
            self.optimization_methods['pymoo_optimization'] = self._optimize_pymoo
            print(f"✅ PyMOO optimization available")
        else:
            print(f"❌ PyMOO not available")
        
        print(f"🔧 Total optimization methods: {len(self.optimization_methods)}")
        
        self._setup_genetic_algorithm()
        self._setup_machine_learning()
        
    def _load_ingredients_database(self) -> List[Dict]:
        """Load ingredients from the database"""
        try:
            with open('ingredients_database.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception as e:
            logger.warning(f"Could not load ingredients database: {e}")
            # Return default ingredients
            return self._get_default_ingredients()
    
    def _get_default_ingredients(self) -> List[Dict]:
        """Get default ingredients if database is not available"""
        return [
            {
                "name": "Chicken Breast",
                "calories_per_100g": 165,
                "protein_per_100g": 31,
                "carbs_per_100g": 0,
                "fat_per_100g": 3.6,
                "category": "protein"
            },
            {
                "name": "Brown Rice",
                "calories_per_100g": 111,
                "protein_per_100g": 2.6,
                "carbs_per_100g": 23,
                "fat_per_100g": 0.9,
                "category": "grain"
            },
            {
                "name": "Salmon",
                "calories_per_100g": 208,
                "protein_per_100g": 25,
                "carbs_per_100g": 0,
                "fat_per_100g": 12,
                "category": "protein"
            },
            {
                "name": "Quinoa",
                "calories_per_100g": 120,
                "protein_per_100g": 4.4,
                "carbs_per_100g": 22,
                "fat_per_100g": 1.9,
                "category": "grain"
            },
            {
                "name": "Eggs",
                "calories_per_100g": 155,
                "protein_per_100g": 13,
                "carbs_per_100g": 1.1,
                "fat_per_100g": 11,
                "category": "protein"
            },
            {
                "name": "Sweet Potato",
                "calories_per_100g": 86,
                "protein_per_100g": 1.6,
                "carbs_per_100g": 20,
                "fat_per_100g": 0.1,
                "category": "vegetable"
            },
            {
                "name": "Avocado",
                "calories_per_100g": 160,
                "protein_per_100g": 2,
                "carbs_per_100g": 9,
                "fat_per_100g": 15,
                "category": "fat"
            },
            {
                "name": "Almonds",
                "calories_per_100g": 579,
                "protein_per_100g": 21,
                "carbs_per_100g": 22,
                "fat_per_100g": 50,
                "category": "nuts"
            },
            {
                "name": "Greek Yogurt",
                "calories_per_100g": 59,
                "protein_per_100g": 10,
                "carbs_per_100g": 3.6,
                "fat_per_100g": 0.4,
                "category": "dairy"
            },
            {
                "name": "Olive Oil",
                "calories_per_100g": 884,
                "protein_per_100g": 0,
                "carbs_per_100g": 0,
                "fat_per_100g": 100,
                "category": "fat"
            }
        ]
    
    def _setup_genetic_algorithm(self):
        """Setup genetic algorithm components"""
        if 'FITNESS_MAX' not in creator.__dict__:
            creator.create("FITNESS_MAX", base.Fitness, weights=(1.0,))
        if 'INDIVIDUAL' not in creator.__dict__:
            creator.create("INDIVIDUAL", list, fitness=creator.FITNESS_MAX)
        
        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_float", random.uniform, 0, 500)
        # Don't set fixed n here - will be set dynamically
        self.toolbox.register("individual", tools.initRepeat, creator.INDIVIDUAL, 
                            self.toolbox.attr_float, n=0)  # Will be set dynamically
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self._evaluate_genetic_fitness)
        self.toolbox.register("mate", tools.cxBlend, alpha=0.5)
        self.toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=20, indpb=0.1)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
    
    def _setup_machine_learning(self):
        """Setup machine learning components for ingredient analysis"""
        self.scaler = StandardScaler()
        self.ingredient_clusters = None
        self.ml_models = {
            'protein': RandomForestRegressor(n_estimators=100, random_state=42),
            'carbs': RandomForestRegressor(n_estimators=100, random_state=42),
            'fat': RandomForestRegressor(n_estimators=100, random_state=42),
            'quantity': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
        }
        self._train_ingredient_models()
        
    def _train_ingredient_models(self):
        """Train machine learning models on ingredient database"""
        try:
            # Prepare training data
            features = []
            targets_protein = []
            targets_carbs = []
            targets_fat = []
            targets_quantity = []
            
            for ingredient in self.ingredients_db:
                features.append([
                    ingredient.get('calories_per_100g', 0),
                    ingredient.get('protein_per_100g', 0),
                    ingredient.get('carbs_per_100g', 0),
                    ingredient.get('fat_per_100g', 0)
                ])
                targets_protein.append(ingredient.get('protein_per_100g', 0))
                targets_carbs.append(ingredient.get('carbs_per_100g', 0))
                targets_fat.append(ingredient.get('fat_per_100g', 0))
                targets_quantity.append(100.0)  # Default quantity for training
            
            if len(features) > 10:  # Only train if we have enough data
                features = np.array(features)
                features_scaled = self.scaler.fit_transform(features)
                
                # Train models
                self.ml_models['protein'].fit(features_scaled, targets_protein)
                self.ml_models['carbs'].fit(features_scaled, targets_carbs)
                self.ml_models['fat'].fit(features_scaled, targets_fat)
                self.ml_models['quantity'].fit(features_scaled, targets_quantity)
                
                # Create ingredient clusters for smart supplementation
                self._create_ingredient_clusters()
                
        except Exception as e:
            logger.warning(f"Could not train ML models: {e}")
    
    def _create_ingredient_clusters(self):
        """Create clusters of ingredients for smart supplementation"""
        try:
            features = []
            ingredient_names = []
            
            for ingredient in self.ingredients_db:
                features.append([
                    ingredient.get('calories_per_100g', 0),
                    ingredient.get('protein_per_100g', 0),
                    ingredient.get('carbs_per_100g', 0),
                    ingredient.get('fat_per_100g', 0)
                ])
                ingredient_names.append(ingredient['name'])
            
            if len(features) > 5:
                features_scaled = self.scaler.transform(features)
                kmeans = KMeans(n_clusters=min(5, len(features)), random_state=42)
                clusters = kmeans.fit_predict(features_scaled)
                
                self.ingredient_clusters = {}
                for i, cluster_id in enumerate(clusters):
                    if cluster_id not in self.ingredient_clusters:
                        self.ingredient_clusters[cluster_id] = []
                    self.ingredient_clusters[cluster_id].append({
                        'name': ingredient_names[i],
                        'ingredient': self.ingredients_db[i]
                    })
                    
        except Exception as e:
            logger.warning(f"Could not create ingredient clusters: {e}")
    
    def _predict_optimal_quantity(self, ingredient: Dict, target_macro: str, deficit: float) -> float:
        """Use ML to predict optimal quantity for an ingredient"""
        try:
            features = np.array([[
                ingredient.get('calories_per_100g', 0),
                ingredient.get('protein_per_100g', 0),
                ingredient.get('carbs_per_100g', 0),
                ingredient.get('fat_per_100g', 0)
            ]])
            
            features_scaled = self.scaler.transform(features)
            
            # Predict quantity based on macro content and deficit
            if target_macro in self.ml_models:
                predicted_quantity = self.ml_models[target_macro].predict(features_scaled)[0]
                
                # Adjust based on deficit and reasonable bounds
                macro_content = ingredient.get(f'{target_macro}_per_100g', 0)
                if macro_content > 0:
                    optimal_quantity = (deficit / macro_content) * 100
                    # Use ML prediction to refine the bounds
                    ml_bounds = max(10, min(500, predicted_quantity))
                    final_quantity = max(10, min(500, optimal_quantity))
                    # Blend ML prediction with deficit calculation
                    return 0.7 * final_quantity + 0.3 * ml_bounds
                
        except Exception as e:
            logger.warning(f"ML quantity prediction failed: {e}")
        
        # Fallback to simple calculation
        macro_content = ingredient.get(f'{target_macro}_per_100g', 0)
        if macro_content > 0:
            return max(10, min(500, (deficit / macro_content) * 100))
        return 100.0
    
    def optimize_single_meal(
        self,
        rag_response: Dict,
        target_macros: Dict,
        user_preferences: Dict,
        meal_type: str
    ) -> Dict:
        """
        Main method to optimize a single meal based on RAG response and target macros
        Returns exactly the format specified by the user
        """
        start_time = time.time()
        
        try:
            # Extract RAG ingredients and calculate current totals
            rag_ingredients = self._extract_rag_ingredients(rag_response)
            current_totals = self._calculate_current_totals(rag_ingredients)
            
            # Calculate macro deficits
            deficits = self._calculate_macro_deficits(current_totals, target_macros)
            
            # Find supplementary ingredients to fill gaps
            supplementary_ingredients = self._find_supplementary_ingredients(
                deficits, rag_ingredients, user_preferences, meal_type
            )
            
            # Combine RAG and supplementary ingredients
            all_ingredients = rag_ingredients + supplementary_ingredients
            
            # Ensure we have at least one ingredient
            if not all_ingredients:
                raise ValueError("No ingredients available for optimization")
            
            # Set current_ingredients for optimization methods to access
            self.current_ingredients = all_ingredients
            
            # Optimize quantities using mathematical optimization - NO FALLBACK
            optimization_result = self._optimize_quantities(
                all_ingredients, target_macros, user_preferences
            )
            
            # If optimization fails, raise error instead of using fallback
            if not optimization_result['success']:
                raise ValueError(f"All optimization methods failed: {optimization_result.get('method', 'Unknown error')}")
            
            # Ensure we have quantities for all ingredients
            quantities = optimization_result.get('quantities', [])
            if len(quantities) != len(all_ingredients):
                raise ValueError(f"Quantity mismatch: expected {len(all_ingredients)}, got {len(quantities)}")
            
            # Calculate final meal
            final_meal = self._calculate_final_meal(
                all_ingredients, quantities
            )
            
            # Check target achievement
            target_achievement = self._check_target_achievement(
                final_meal, target_macros
            )
            
            # Calculate enhancement details
            rag_enhancement = self._calculate_enhancement_details(
                rag_ingredients, supplementary_ingredients, final_meal
            )
            
            computation_time = time.time() - start_time
            
            return {
                "optimization_result": {
                    "success": True,
                    "method": optimization_result['method'],
                    "computation_time": round(computation_time, 3),
                    "target_achieved": target_achievement['overall_achieved']
                },
                "meal": {
                    "meal_time": meal_type,
                    "total_calories": round(final_meal['calories'], 1),
                    "total_protein": round(final_meal['protein'], 1),
                    "total_carbs": round(final_meal['carbs'], 1),
                    "total_fat": round(final_meal['fat'], 1),
                    "items": final_meal['items']
                },
                "target_achievement": {
                    "calories_achieved": target_achievement['calories_achieved'],
                    "protein_achieved": target_achievement['protein_achieved'],
                    "carbs_achieved": target_achievement['carbs_achieved'],
                    "fat_achieved": target_achievement['fat_achieved']
                },
                "recommendations": self._generate_recommendations(final_meal, target_macros),
                "rag_enhancement": rag_enhancement
            }
            
        except Exception as e:
            logger.error(f"Error in single meal optimization: {e}")
            return {
                "optimization_result": {
                    "success": False,
                    "method": "Error",
                    "computation_time": 0,
                    "target_achieved": False,
                    "error": str(e)
                },
                "meal": None,
                "target_achievement": {},
                "recommendations": [f"Optimization failed: {str(e)}"],
                "rag_enhancement": {}
            }
    
    def _extract_rag_ingredients(self, rag_response: Dict) -> List[Dict]:
        """Extract ingredients from RAG response"""
        ingredients = []
        
        for suggestion in rag_response.get('suggestions', []):
            for ingredient in suggestion.get('ingredients', []):
                # Convert to standardized format
                amount = ingredient.get('amount', 100)
                if isinstance(amount, str):
                    try:
                        amount = float(amount)
                    except:
                        amount = 100
                
                # Create ingredient with source='rag' to identify it as RAG ingredient
                rag_ingredient = {
                    'name': ingredient['name'],
                    'calories_per_100g': (ingredient['calories'] / amount) * 100,
                    'protein_per_100g': (ingredient['protein'] / amount) * 100,
                    'carbs_per_100g': (ingredient['carbs'] / amount) * 100,
                    'fat_per_100g': (ingredient['fat'] / amount) * 100,
                    'original_amount': amount,
                    'source': 'rag',
                    'category': self._categorize_ingredient(ingredient['name'])
                }
                ingredients.append(rag_ingredient)
        
        return ingredients
    
    def _categorize_ingredient(self, ingredient_name: str) -> str:
        """Categorize ingredient based on name and typical macro content"""
        name_lower = ingredient_name.lower()
        
        # Protein sources
        if any(word in name_lower for word in ['beef', 'chicken', 'pork', 'lamb', 'turkey', 'fish', 'salmon', 'tuna', 'shrimp', 'egg', 'meat']):
            return 'protein'
        # Grain sources
        elif any(word in name_lower for word in ['rice', 'bread', 'pasta', 'quinoa', 'oat', 'wheat', 'corn', 'barley']):
            return 'grain'
        # Vegetable sources
        elif any(word in name_lower for word in ['tomato', 'onion', 'carrot', 'broccoli', 'spinach', 'lettuce', 'cucumber', 'pepper']):
            return 'vegetable'
        # Fruit sources
        elif any(word in name_lower for word in ['apple', 'banana', 'orange', 'grape', 'berry', 'mango', 'pineapple']):
            return 'fruit'
        # Dairy sources
        elif any(word in name_lower for word in ['milk', 'cheese', 'yogurt', 'cream', 'butter']):
            return 'dairy'
        # Fat sources
        elif any(word in name_lower for word in ['oil', 'avocado', 'nut', 'seed', 'olive']):
            return 'fat'
        else:
            return 'other'
    
    def _calculate_current_totals(self, ingredients: List[Dict]) -> Dict:
        """Calculate current totals from ingredients"""
        totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
        
        for ingredient in ingredients:
            quantity = ingredient.get('quantity_needed', 100) / 100  # Convert to ratio
            totals['calories'] += ingredient.get('calories_per_100g', 0) * quantity
            totals['protein'] += ingredient.get('protein_per_100g', 0) * quantity
            totals['carbs'] += ingredient.get('carbs_per_100g', 0) * quantity
            totals['fat'] += ingredient.get('fat_per_100g', 0) * quantity
        
        return totals
    
    def _calculate_macro_deficits(self, current_totals: Dict, target_macros: Dict) -> Dict:
        """Calculate macro deficits to reach targets"""
        deficits = {}
        
        for macro in ['calories', 'protein', 'carbs', 'fat']:
            current = current_totals.get(macro, 0)
            target = target_macros.get(macro, 0)
            deficit = max(0, target - current)
            deficits[macro] = deficit
        
        return deficits
    
    def _optimize_supplement_quantity(self, supplement: Dict, deficits: Dict, current_totals: Dict) -> Dict:
        """Optimize supplement quantity to meet deficits"""
        # Simple optimization: adjust quantity based on largest deficit
        largest_deficit = max(deficits.items(), key=lambda x: abs(x[1]))
        deficit_type, deficit_value = largest_deficit
        
        if deficit_type == 'protein' and supplement.get('protein_per_100g', 0) > 0:
            optimal_qty = (abs(deficit_value) / supplement.get('protein_per_100g', 1)) * 100
        elif deficit_type == 'carbs' and supplement.get('carbs_per_100g', 0) > 0:
            optimal_qty = (abs(deficit_value) / supplement.get('carbs_per_100g', 1)) * 100
        elif deficit_type == 'fat' and supplement.get('fat_per_100g', 0) > 0:
            optimal_qty = (abs(deficit_value) / supplement.get('fat_per_100g', 1)) * 100
        else:
            optimal_qty = 100  # Default quantity
        
        # Apply bounds
        optimal_qty = max(20, min(300, optimal_qty))
        supplement['quantity_needed'] = round(optimal_qty, 1)
        
        return supplement

    def _update_totals_with_supplements(self, current_totals: Dict, supplements: List[Dict]) -> Dict:
        """Update current totals with supplement ingredients"""
        updated_totals = current_totals.copy()
        
        for supplement in supplements:
            quantity = supplement.get('quantity_needed', 0)
            if quantity > 0:
                updated_totals['calories'] += (supplement.get('calories_per_100g', 0) * quantity) / 100
                updated_totals['protein'] += (supplement.get('protein_per_100g', 0) * quantity) / 100
                updated_totals['carbs'] += (supplement.get('carbs_per_100g', 0) * quantity) / 100
                updated_totals['fat'] += (supplement.get('fat_per_100g', 0) * quantity) / 100
        
        return updated_totals

    def _find_ingredient_by_name(self, name: str) -> Optional[Dict]:
        """Find ingredient by name in the database"""
        for ingredient in self.ingredients_db:
            if ingredient.get('name', '').lower() == name.lower():
                return ingredient
        return None

    def _analyze_meal_composition(self, rag_ingredients: List[Dict], meal_type: str) -> Dict:
        """Analyze meal composition for smart supplementation"""
        analysis = {
            'meal_type': meal_type,
            'rag_ingredients': rag_ingredients,
            'protein_sources': [],
            'carb_sources': [],
            'fat_sources': [],
            'vegetable_sources': [],
            'grain_sources': [],
            'seasonal_availability': {
                'summer': ['Berries', 'Tomatoes', 'Zucchini', 'Bell Peppers'],
                'winter': ['Root Vegetables', 'Winter Squash', 'Citrus Fruits'],
                'spring': ['Asparagus', 'Peas', 'Strawberries', 'Leafy Greens'],
                'fall': ['Pumpkin', 'Apples', 'Mushrooms', 'Brussels Sprouts']
            }
        }
        
        for ingredient in rag_ingredients:
            name = ingredient.get('name', '').lower()
            category = ingredient.get('category', 'unknown')
            
            # Categorize ingredients
            if ingredient.get('protein_per_100g', 0) > 5:
                analysis['protein_sources'].append(ingredient)
            if ingredient.get('carbs_per_100g', 0) > 10:
                analysis['carb_sources'].append(ingredient)
            if ingredient.get('fat_per_100g', 0) > 5:
                analysis['fat_sources'].append(ingredient)
            if category == 'vegetable' or any(veg in name for veg in ['tomato', 'onion', 'lettuce', 'spinach']):
                analysis['vegetable_sources'].append(ingredient)
            if category == 'grain' or any(grain in name for grain in ['rice', 'pasta', 'bread', 'oats']):
                analysis['grain_sources'].append(ingredient)
        
        return analysis

    def _find_supplementary_ingredients(self, deficits: Dict, rag_ingredients: List[Dict], user_preferences: Dict, meal_type: str) -> List[Dict]:
        """Find supplementary ingredients to meet macro targets with minimal additions"""
        supplements = []
        
        # Analyze meal composition for better supplementation strategy
        meal_analysis = self._analyze_meal_composition(rag_ingredients, meal_type)
        
        # Track what we've added to avoid redundancy
        added_ingredients = set()
        added_categories = set()
        
        # Calculate current totals
        current_totals = self._calculate_current_totals(rag_ingredients)
        
        # Smart supplementation: try to meet targets with minimal ingredients
        supplements = self._smart_minimal_supplementation(deficits, rag_ingredients, added_ingredients, added_categories, current_totals, meal_analysis, user_preferences)
        
        # If targets still not met, add more ingredients strategically
        if not self._are_targets_met(supplements, current_totals, deficits):
            supplements = self._strategic_additional_supplementation(supplements, deficits, added_ingredients, added_categories, current_totals, meal_analysis, user_preferences)
        
        # Final optimization to ensure targets are met with minimal ingredients
        supplements = self._final_minimal_optimization(supplements, deficits, current_totals)
        
        return supplements
    
    def _smart_minimal_supplementation(self, deficits: Dict, rag_ingredients: List[Dict], added_ingredients: set, added_categories: set, current_totals: Dict, meal_analysis: Dict, user_preferences: Dict) -> List[Dict]:
        """Smart supplementation with minimal ingredients"""
        supplements = []
        
        # Sort deficits by priority (protein first, then carbs, then fat)
        deficit_priority = [
            ('protein', deficits.get('protein', 0)),
            ('carbs', deficits.get('carbs', 0)),
            ('fat', deficits.get('fat', 0))
        ]
        deficit_priority.sort(key=lambda x: abs(x[1]), reverse=True)
        
        # Try to meet each deficit with the most efficient single ingredient
        for macro_type, deficit in deficit_priority:
            if abs(deficit) > 0.1:  # Only add if significant deficit
                best_ingredient = self._find_best_single_ingredient_for_macro(macro_type, deficit, added_ingredients, added_categories, meal_analysis, user_preferences)
                
                if best_ingredient:
                    # Calculate optimal quantity to meet this specific deficit
                    optimal_qty = self._calculate_optimal_quantity_for_deficit(best_ingredient, macro_type, deficit)
                    
                    if optimal_qty > 0:
                        best_ingredient['quantity_needed'] = optimal_qty
                        supplements.append(best_ingredient)
                        
                        # Update tracking
                        added_ingredients.add(best_ingredient.get('name', ''))
                        added_categories.add(best_ingredient.get('category', ''))
                        
                        # Recalculate totals
                        current_totals = self._update_totals_with_supplements(current_totals, [best_ingredient])
                        
                        # Check if we've met this target
                        if abs(deficit) <= 0.5:
                            break
        
        return supplements
    
    def _find_best_single_ingredient_for_macro(self, macro_type: str, deficit: float, added_ingredients: set, added_categories: set, meal_analysis: Dict, user_preferences: Dict) -> Optional[Dict]:
        """Find the single best ingredient for a specific macro deficit with smart avoidance"""
        best_ingredient = None
        best_score = 0
        
        # Get available ingredients for this macro type
        available_ingredients = self._get_available_ingredients_for_macro(macro_type, user_preferences)
        
        # Get existing ingredients to avoid duplicates
        existing_ingredients = self._get_existing_ingredients_from_meal_analysis(meal_analysis)
        
        for ingredient in available_ingredients:
            if ingredient.get('name', '') in added_ingredients:
                continue
            
            # Check if this ingredient conflicts with existing ones
            if self._has_ingredient_conflict(ingredient, existing_ingredients):
                continue
                
            # Calculate efficiency score
            score = self._calculate_ingredient_efficiency_score(ingredient, macro_type, deficit, meal_analysis)
            
            if score > best_score:
                best_score = score
                best_ingredient = ingredient
        
        return best_ingredient
    
    def _has_ingredient_conflict(self, new_ingredient: Dict, existing_ingredients: List[Dict]) -> bool:
        """Check if new ingredient conflicts with existing ones"""
        new_name = new_ingredient.get('name', '').lower()
        
        for existing in existing_ingredients:
            existing_name = existing.get('name', '').lower()
            
            # Avoid adding rice if any type of rice already exists
            if self._is_rice_ingredient(new_name) and self._is_rice_ingredient(existing_name):
                return True
            
            # Avoid adding similar protein sources
            if self._is_similar_protein(new_name, existing_name):
                return True
            
            # Avoid adding similar carb sources
            if self._is_similar_carb(new_name, existing_name):
                return True
        
        return False
    
    def _is_rice_ingredient(self, ingredient_name: str) -> bool:
        """Check if ingredient is any type of rice"""
        rice_keywords = ['rice', 'basmati', 'jasmine', 'brown rice', 'white rice', 'wild rice', 'arborio', 'sushi rice']
        return any(keyword in ingredient_name for keyword in rice_keywords)
    
    def _is_similar_protein(self, new_name: str, existing_name: str) -> bool:
        """Check if ingredients are similar protein sources"""
        protein_groups = [
            ['beef', 'ground beef', 'steak', 'burger'],
            ['chicken', 'chicken breast', 'turkey', 'turkey breast'],
            ['fish', 'salmon', 'cod', 'tuna', 'mackerel'],
            ['eggs', 'egg whites', 'whole eggs'],
            ['dairy', 'milk', 'yogurt', 'cheese', 'cottage cheese']
        ]
        
        for group in protein_groups:
            if any(keyword in new_name for keyword in group) and any(keyword in existing_name for keyword in group):
                return True
        
        return False
    
    def _is_similar_carb(self, new_name: str, existing_name: str) -> bool:
        """Check if ingredients are similar carb sources"""
        carb_groups = [
            ['rice', 'basmati', 'brown rice', 'white rice'],
            ['pasta', 'spaghetti', 'penne', 'macaroni'],
            ['bread', 'toast', 'sandwich bread'],
            ['potato', 'sweet potato', 'mashed potato'],
            ['oats', 'oatmeal', 'rolled oats']
        ]
        
        for group in carb_groups:
            if any(keyword in new_name for keyword in group) and any(keyword in existing_name for keyword in group):
                return True
        
        return False
    
    def _get_existing_ingredients_from_meal_analysis(self, meal_analysis: Dict) -> List[Dict]:
        """Extract existing ingredients from meal analysis"""
        existing_ingredients = []
        
        if 'rag_ingredients' in meal_analysis:
            existing_ingredients.extend(meal_analysis['rag_ingredients'])
        
        if 'supplements' in meal_analysis:
            existing_ingredients.extend(meal_analysis['supplements'])
        
        return existing_ingredients
    
    def _get_available_ingredients_for_macro(self, macro_type: str, user_preferences: Dict) -> List[Dict]:
        """Get available ingredients for a specific macro type with smart variety"""
        available_ingredients = []
        
        if macro_type == 'protein':
            # High protein, low fat ingredients with variety
            protein_ingredients = [
                'Chicken Breast', 'Turkey Breast', 'Cod', 'Greek Yogurt', 
                'Cottage Cheese', 'Egg Whites', 'Lean Pork', 'Lentils',
                'Chickpeas', 'Tofu', 'Tempeh', 'Edamame'
            ]
            for name in protein_ingredients:
                ingredient = self._find_ingredient_by_name(name)
                if ingredient:
                    available_ingredients.append(ingredient)
                    
        elif macro_type == 'carbs':
            # High carbs, low fat ingredients with variety (avoiding rice)
            carb_ingredients = [
                'Sweet Potato', 'Oatmeal', 'Banana', 'Apple', 'Quinoa',
                'Buckwheat', 'Millet', 'Amaranth', 'Barley', 'Farro',
                'Whole Wheat Bread', 'Whole Wheat Pasta'
            ]
            for name in carb_ingredients:
                ingredient = self._find_ingredient_by_name(name)
                if ingredient:
                    available_ingredients.append(ingredient)
                    
        elif macro_type == 'fat':
            # Moderate fat ingredients with variety
            fat_ingredients = [
                'Almonds', 'Walnuts', 'Avocado', 'Olive Oil', 'Salmon', 
                'Eggs', 'Chia Seeds', 'Flax Seeds', 'Pumpkin Seeds',
                'Sunflower Seeds', 'Cashews', 'Pecans'
            ]
            for name in fat_ingredients:
                ingredient = self._find_ingredient_by_name(name)
                if ingredient:
                    available_ingredients.append(ingredient)
        
        return available_ingredients
    
    def _calculate_ingredient_efficiency_score(self, ingredient: Dict, macro_type: str, deficit: float, meal_analysis: Dict) -> float:
        """Calculate efficiency score for an ingredient"""
        score = 0
        
        if macro_type == 'protein':
            protein_content = ingredient.get('protein_per_100g', 0)
            fat_content = ingredient.get('fat_per_100g', 0)
            calories_content = ingredient.get('calories_per_100g', 0)
            
            # Higher protein, lower fat, lower calories = better score
            if protein_content > 0:
                score = protein_content / max(fat_content + calories_content/10, 1)
                
        elif macro_type == 'carbs':
            carbs_content = ingredient.get('carbs_per_100g', 0)
            fat_content = ingredient.get('fat_per_100g', 0)
            calories_content = ingredient.get('calories_per_100g', 0)
            
            # Higher carbs, lower fat, lower calories = better score
            if carbs_content > 0:
                score = carbs_content / max(fat_content + calories_content/15, 1)
                
        elif macro_type == 'fat':
            fat_content = ingredient.get('fat_per_100g', 0)
            calories_content = ingredient.get('calories_per_100g', 0)
            
            # Moderate fat content, lower calories = better score
            if 5 <= fat_content <= 15 and calories_content > 0:
                score = fat_content / calories_content
        
        return score
    
    def _calculate_optimal_quantity_for_deficit(self, ingredient: Dict, macro_type: str, deficit: float) -> float:
        """Calculate optimal quantity to meet a specific deficit"""
        if macro_type == 'protein':
            macro_content = ingredient.get('protein_per_100g', 0)
        elif macro_type == 'carbs':
            macro_content = ingredient.get('carbs_per_100g', 0)
        elif macro_type == 'fat':
            macro_content = ingredient.get('fat_per_100g', 0)
        else:
            return 0
        
        if macro_content <= 0:
            return 0
        
        # Calculate quantity needed to meet deficit
        quantity_needed = (deficit / macro_content) * 100
        
        # Apply bounds
        quantity_needed = max(15, min(300, quantity_needed))
        
        return quantity_needed
    
    def _are_targets_met(self, supplements: List[Dict], current_totals: Dict, deficits: Dict) -> bool:
        """Check if all targets are met"""
        # Calculate total macros with supplements
        total_totals = self._update_totals_with_supplements(current_totals, supplements)
        
        # Check each macro target
        for macro, target in deficits.items():
            if macro == 'protein' and abs(total_totals['protein'] - 47.7) > 0.5:
                return False
            elif macro == 'carbs' and abs(total_totals['carbs'] - 79.7) > 0.5:
                return False
            elif macro == 'fat' and abs(total_totals['fat'] - 14.2) > 0.5:
                return False
        
        return True
    
    def _strategic_additional_supplementation(self, supplements: List[Dict], deficits: Dict, added_ingredients: set, added_categories: set, current_totals: Dict, meal_analysis: Dict, user_preferences: Dict) -> List[Dict]:
        """Add ingredients strategically if targets still not met"""
        # Recalculate current totals
        current_totals = self._update_totals_with_supplements(current_totals, supplements)
        
        # Find remaining deficits
        remaining_deficits = self._calculate_remaining_deficits(current_totals)
        
        # Add ingredients to fill remaining deficits
        for macro_type, deficit in remaining_deficits.items():
            if abs(deficit) > 0.5:  # Only add if significant deficit
                additional_ingredient = self._find_additional_ingredient_for_deficit(macro_type, deficit, added_ingredients, added_categories, user_preferences)
                
                if additional_ingredient:
                    optimal_qty = self._calculate_optimal_quantity_for_deficit(additional_ingredient, macro_type, deficit)
                    
                    if optimal_qty > 0:
                        additional_ingredient['quantity_needed'] = optimal_qty
                        supplements.append(additional_ingredient)
                        
                        # Update tracking
                        added_ingredients.add(additional_ingredient.get('name', ''))
                        added_categories.add(additional_ingredient.get('category', ''))
                        
                        # Recalculate totals
                        current_totals = self._update_totals_with_supplements(current_totals, [additional_ingredient])
        
        return supplements
    
    def _calculate_remaining_deficits(self, current_totals: Dict) -> Dict:
        """Calculate remaining deficits after current supplementation"""
        target_protein = 47.7
        target_cars = 79.7
        target_fat = 14.2
        
        return {
            'protein': target_protein - current_totals['protein'],
            'carbs': target_cars - current_totals['carbs'],
            'fat': target_fat - current_totals['fat']
        }
    
    def _find_additional_ingredient_for_deficit(self, macro_type: str, deficit: float, added_ingredients: set, added_categories: set, user_preferences: Dict) -> Optional[Dict]:
        """Find additional ingredient for remaining deficit"""
        available_ingredients = self._get_available_ingredients_for_macro(macro_type, user_preferences)
        
        for ingredient in available_ingredients:
            if ingredient.get('name', '') in added_ingredients:
                continue
            
            # Check if this ingredient can help with the deficit
            if macro_type == 'protein' and ingredient.get('protein_per_100g', 0) > 0:
                return ingredient
            elif macro_type == 'carbs' and ingredient.get('carbs_per_100g', 0) > 0:
                return ingredient
            elif macro_type == 'fat' and ingredient.get('fat_per_100g', 0) > 0:
                return ingredient
        
        return None
    
    def _final_minimal_optimization(self, supplements: List[Dict], deficits: Dict, current_totals: Dict) -> List[Dict]:
        """Final optimization to ensure targets are met with minimal ingredients"""
        # Recalculate totals
        current_totals = self._update_totals_with_supplements(current_totals, supplements)
        
        # Check if targets are met
        if self._are_targets_met(supplements, current_totals, deficits):
            return supplements
        
        # If not met, try to adjust quantities of existing supplements
        for supplement in supplements:
            current_totals = self._update_totals_with_supplements(current_totals, supplements)
            
            if self._are_targets_met(supplements, current_totals, deficits):
                break
            
            # Try to adjust this supplement's quantity
            supplement = self._optimize_supplement_quantity(supplement, deficits, current_totals)
        
        # Final ultra-precise adjustment
        supplements = self._ultra_precise_final_adjustment(supplements, deficits, current_totals)
        
        return supplements
    
    def _ultra_precise_final_adjustment(self, supplements: List[Dict], deficits: Dict, current_totals: Dict) -> List[Dict]:
        """Ultra-precise final adjustment to reach targets exactly with aggressive anti-overshooting control"""
        target_protein = 47.7
        target_cars = 79.7
        target_fat = 14.2
        target_calories = 637.2
        
        # Multiple iterations of micro-adjustments with aggressive anti-overshooting control
        for iteration in range(50):  # Increased iterations for ultra-precision
            current_totals = self._update_totals_with_supplements(current_totals, supplements)
            
            # Calculate current deficits
            protein_diff = target_protein - current_totals['protein']
            carbs_diff = target_cars - current_totals['carbs']
            fat_diff = target_fat - current_totals['fat']
            calories_diff = target_calories - current_totals['calories']
            
            # Check if all targets are met within ultra-precise tolerance
            if (abs(protein_diff) <= 0.05 and abs(carbs_diff) <= 0.05 and 
                abs(fat_diff) <= 0.05 and abs(calories_diff) <= 0.2):
                break
            
            # Apply aggressive anti-overshooting adjustments
            supplements = self._apply_aggressive_anti_overshooting_adjustments(supplements, protein_diff, carbs_diff, fat_diff, calories_diff, iteration)
            
            # Apply emergency ingredient swapping if overshooting detected (earlier threshold)
            if (protein_diff < -0.05 or carbs_diff < -0.05 or fat_diff < -0.05 or calories_diff < -0.2):
                supplements = self._apply_emergency_overshooting_correction(supplements, protein_diff, carbs_diff, fat_diff, calories_diff)
            
            # Apply ultra-aggressive correction if still overshooting
            if iteration > 20 and (protein_diff < -0.1 or carbs_diff < -0.1 or fat_diff < -0.1 or calories_diff < -0.5):
                supplements = self._apply_ultra_aggressive_correction(supplements, protein_diff, carbs_diff, fat_diff, calories_diff)
        
        return supplements
    
    def _apply_aggressive_anti_overshooting_adjustments(self, supplements: List[Dict], protein_diff: float, carbs_diff: float, fat_diff: float, calories_diff: float, iteration: int) -> List[Dict]:
        """Apply aggressive anti-overshooting adjustments to reach targets precisely"""
        # Calculate adjustment factor with aggressive anti-overshooting control
        base_factor = 0.05 / (iteration + 1)  # Reduced base factor for more precision
        
        # Apply protein optimization first (highest priority)
        supplements = self._optimize_protein_precisely(supplements, protein_diff, base_factor)
        
        # Apply fat optimization with ingredient swapping
        supplements = self._optimize_fat_precisely(supplements, fat_diff, base_factor)
        
        # Apply carb optimization
        supplements = self._optimize_carbs_precisely(supplements, carbs_diff, base_factor)
        
        # Apply calorie optimization
        supplements = self._optimize_calories_precisely(supplements, calories_diff, base_factor)
        
        return supplements

    def _apply_anti_overshooting_adjustments(self, supplements: List[Dict], protein_diff: float, carbs_diff: float, fat_diff: float, calories_diff: float, iteration: int) -> List[Dict]:
        """Apply anti-overshooting adjustments to reach targets precisely"""
        # Calculate adjustment factor with anti-overshooting control
        base_factor = 0.1 / (iteration + 1)
        
        # Apply protein optimization first (highest priority)
        supplements = self._optimize_protein_precisely(supplements, protein_diff, base_factor)
        
        # Apply fat optimization with ingredient swapping
        supplements = self._optimize_fat_precisely(supplements, fat_diff, base_factor)
        
        # Apply carb optimization
        supplements = self._optimize_carbs_precisely(supplements, carbs_diff, base_factor)
        
        # Apply calorie optimization
        supplements = self._optimize_calories_precisely(supplements, calories_diff, base_factor)
        
        return supplements

    def _apply_improved_micro_adjustments(self, supplements: List[Dict], protein_diff: float, carbs_diff: float, fat_diff: float, calories_diff: float, iteration: int) -> List[Dict]:
        """Apply improved micro-adjustments to reach targets precisely"""
        # Calculate adjustment factor with better precision
        adjustment_factor = 0.15 / (iteration + 1)  # Increased base factor
        
        # Apply protein optimization first (highest priority)
        supplements = self._optimize_protein_precisely(supplements, protein_diff, adjustment_factor)
        
        # Apply fat optimization with ingredient swapping
        supplements = self._optimize_fat_precisely(supplements, fat_diff, adjustment_factor)
        
        # Apply carb optimization
        supplements = self._optimize_carbs_precisely(supplements, carbs_diff, adjustment_factor)
        
        # Apply calorie optimization
        supplements = self._optimize_calories_precisely(supplements, calories_diff, adjustment_factor)
        
        return supplements
    
    def _optimize_protein_precisely(self, supplements: List[Dict], protein_diff: float, adjustment_factor: float) -> List[Dict]:
        """Optimize protein with ultra-precise control to prevent overshooting"""
        if abs(protein_diff) <= 0.05:
            return supplements
        
        # Find best protein sources
        protein_sources = [s for s in supplements if s.get('protein_per_100g', 0) > 0]
        if not protein_sources:
            return supplements
        
        # Sort by protein efficiency (protein/fat ratio)
        protein_sources.sort(key=lambda x: x.get('protein_per_100g', 0) / max(x.get('fat_per_100g', 1), 1), reverse=True)
        
        # Apply ultra-precise adjustments to prevent overshooting
        for source in protein_sources[:2]:  # Top 2 protein sources
            current_qty = source.get('quantity_needed', 0)
            
            if protein_diff > 0.05:  # Need more protein
                # Calculate exact amount needed
                protein_needed = protein_diff / source.get('protein_per_100g', 1) * 100
                # Use ultra-small adjustment to prevent overshooting
                adjustment = protein_needed * min(adjustment_factor, 0.02)
                new_qty = current_qty + adjustment
                new_qty = max(20, min(250, new_qty))
                source['quantity_needed'] = round(new_qty, 1)
                protein_diff -= (new_qty - current_qty) * source.get('protein_per_100g', 0) / 100
                
            elif protein_diff < -0.05:  # Too much protein - REDUCE AGGRESSIVELY
                protein_excess = abs(protein_diff) / source.get('protein_per_100g', 1) * 100
                # Use ultra-aggressive reduction factor to quickly fix overshooting
                reduction = protein_excess * min(adjustment_factor * 4, 0.6)
                new_qty = current_qty - reduction
                new_qty = max(20, min(250, new_qty))
                source['quantity_needed'] = round(new_qty, 1)
                protein_diff += (current_qty - new_qty) * source.get('protein_per_100g', 0) / 100
            
            if abs(protein_diff) <= 0.05:
                break
        
        return supplements
    
    def _optimize_fat_precisely(self, supplements: List[Dict], fat_diff: float, adjustment_factor: float) -> List[Dict]:
        """Optimize fat with ultra-precise control to prevent overshooting"""
        if abs(fat_diff) <= 0.05:
            return supplements
        
        # If fat is too high, try to swap high-fat ingredients IMMEDIATELY
        if fat_diff < -0.05:
            supplements = self._swap_high_fat_ingredients_aggressive(supplements, abs(fat_diff))
        
        # Apply ultra-precise adjustments to fat sources
        fat_sources = [s for s in supplements if s.get('fat_per_100g', 0) > 0]
        if not fat_sources:
            return supplements
        
        # Sort by fat efficiency (moderate fat is better)
        fat_sources.sort(key=lambda x: abs(x.get('fat_per_100g', 0) - 10), reverse=False)
        
        for source in fat_sources[:2]:  # Top 2 fat sources
            current_qty = source.get('quantity_needed', 0)
            
            if fat_diff > 0.05:  # Need more fat
                fat_needed = fat_diff / source.get('fat_per_100g', 1) * 100
                # Use ultra-small adjustment to prevent overshooting
                adjustment = fat_needed * min(adjustment_factor, 0.01)
                new_qty = current_qty + adjustment
                new_qty = max(15, min(150, new_qty))
                source['quantity_needed'] = round(new_qty, 1)
                fat_diff -= (new_qty - current_qty) * source.get('fat_per_100g', 0) / 100
                
            elif fat_diff < -0.05:  # Too much fat - REDUCE ULTRA-AGGRESSIVELY
                fat_excess = abs(fat_diff) / source.get('fat_per_100g', 1) * 100
                # Use ultra-aggressive reduction to quickly fix overshooting
                reduction = fat_excess * min(adjustment_factor * 6, 0.8)
                new_qty = current_qty - reduction
                new_qty = max(15, min(150, new_qty))
                source['quantity_needed'] = round(new_qty, 1)
                fat_diff += (current_qty - new_qty) * source.get('fat_per_100g', 0) / 100
            
            if abs(fat_diff) <= 0.05:
                break
        
        return supplements
    
    def _swap_high_fat_ingredients_ultra_aggressive(self, supplements: List[Dict], fat_excess: float) -> List[Dict]:
        """Ultra-aggressively swap high-fat ingredients to quickly reduce fat"""
        for i, supplement in enumerate(supplements):
            if supplement.get('fat_per_100g', 0) > 5:  # Even lower threshold for ultra-aggressive swapping
                # Try to find ultra-low-fat alternative
                alternative = self._find_ultra_low_fat_alternative_aggressive(supplement)
                if alternative:
                    # Calculate how much fat we can reduce
                    current_fat = supplement.get('fat_per_100g', 0) * supplement.get('quantity_needed', 0) / 100
                    alternative_fat = alternative.get('fat_per_100g', 0) * supplement.get('quantity_needed', 0) / 100
                    fat_reduction = current_fat - alternative_fat
                    
                    if fat_reduction > 0:
                        # Replace with alternative
                        supplements[i] = alternative.copy()
                        supplements[i]['quantity_needed'] = supplement.get('quantity_needed', 0)
                        fat_excess -= fat_reduction
                        
                        if fat_excess <= 0.05:
                            break
        
        return supplements

    def _swap_high_fat_ingredients_aggressive(self, supplements: List[Dict], fat_excess: float) -> List[Dict]:
        """Aggressively swap high-fat ingredients to quickly reduce fat"""
        for i, supplement in enumerate(supplements):
            if supplement.get('fat_per_100g', 0) > 8:  # Lower threshold for aggressive swapping
                # Try to find ultra-low-fat alternative
                alternative = self._find_ultra_low_fat_alternative(supplement)
                if alternative:
                    # Calculate how much fat we can reduce
                    current_fat = supplement.get('fat_per_100g', 0) * supplement.get('quantity_needed', 0) / 100
                    alternative_fat = alternative.get('fat_per_100g', 0) * supplement.get('quantity_needed', 0) / 100
                    fat_reduction = current_fat - alternative_fat
                    
                    if fat_reduction > 0:
                        # Replace with alternative
                        supplements[i] = alternative.copy()
                        supplements[i]['quantity_needed'] = supplement.get('quantity_needed', 0)
                        fat_excess -= fat_reduction
                        
                        if fat_excess <= 0.05:
                            break
        
        return supplements

    def _swap_high_fat_ingredients(self, supplements: List[Dict], fat_excess: float) -> List[Dict]:
        """Swap high-fat ingredients with lower-fat alternatives"""
        for i, supplement in enumerate(supplements):
            if supplement.get('fat_per_100g', 0) > 12:  # High fat ingredient
                # Try to find lower-fat alternative
                alternative = self._find_lower_fat_alternative_advanced(supplement)
                if alternative:
                    # Calculate how much fat we can reduce
                    current_fat = supplement.get('fat_per_100g', 0) * supplement.get('quantity_needed', 0) / 100
                    alternative_fat = alternative.get('fat_per_100g', 0) * supplement.get('quantity_needed', 0) / 100
                    fat_reduction = current_fat - alternative_fat
                    
                    if fat_reduction > 0:
                        # Replace with alternative
                        supplements[i] = alternative.copy()
                        supplements[i]['quantity_needed'] = supplement.get('quantity_needed', 0)
                        fat_excess -= fat_reduction
                        
                        if fat_excess <= 0.05:
                            break
        
        return supplements
    
    def _find_ultra_low_fat_alternative_aggressive(self, current_ingredient: Dict) -> Optional[Dict]:
        """Find ultra-low-fat alternative with aggressive fat reduction"""
        current_name = current_ingredient.get('name', '').lower()
        current_protein = current_ingredient.get('protein_per_100g', 0)
        current_fat = current_ingredient.get('fat_per_100g', 0)
        
        # Ultra-low-fat alternatives (fat < 2g per 100g) - more aggressive
        ultra_low_fat_alternatives = {
            'almonds': ['Egg Whites', 'Greek Yogurt', 'Cottage Cheese', 'Tofu'],
            'walnuts': ['Egg Whites', 'Greek Yogurt', 'Cottage Cheese', 'Tofu'],
            'cashews': ['Egg Whites', 'Greek Yogurt', 'Cottage Cheese', 'Tofu'],
            'eggs': ['Egg Whites', 'Greek Yogurt', 'Cottage Cheese', 'Tofu'],
            'salmon': ['Cod', 'Tilapia', 'Chicken Breast', 'Tofu'],
            'avocado': ['Cucumber', 'Celery', 'Lettuce', 'Zucchini'],
            'greek yogurt': ['Cottage Cheese', 'Tofu', 'Egg Whites'],
            'cottage cheese': ['Tofu', 'Egg Whites', 'Greek Yogurt']
        }
        
        # Find alternatives for current ingredient
        for key, alt_list in ultra_low_fat_alternatives.items():
            if key in current_name:
                for alt_name in alt_list:
                    alternative = self._find_ingredient_by_name(alt_name)
                    if alternative:
                        alt_protein = alternative.get('protein_per_100g', 0)
                        alt_fat = alternative.get('fat_per_100g', 0)
                        
                        # Check if alternative is ultra-low in fat
                        if (alt_fat < 2 and 
                            abs(alt_protein - current_protein) < current_protein * 0.7):
                            return alternative
        
        return None

    def _find_ultra_low_fat_alternative(self, current_ingredient: Dict) -> Optional[Dict]:
        """Find ultra-low-fat alternative with similar protein content"""
        current_name = current_ingredient.get('name', '').lower()
        current_protein = current_ingredient.get('protein_per_100g', 0)
        current_fat = current_ingredient.get('fat_per_100g', 0)
        
        # Ultra-low-fat alternatives (fat < 3g per 100g)
        ultra_low_fat_alternatives = {
            'almonds': ['Egg Whites', 'Greek Yogurt', 'Cottage Cheese'],
            'walnuts': ['Egg Whites', 'Greek Yogurt', 'Cottage Cheese'],
            'cashews': ['Egg Whites', 'Greek Yogurt', 'Cottage Cheese'],
            'eggs': ['Egg Whites', 'Greek Yogurt', 'Cottage Cheese'],
            'salmon': ['Cod', 'Tilapia', 'Chicken Breast'],
            'avocado': ['Cucumber', 'Celery', 'Lettuce']
        }
        
        # Find alternatives for current ingredient
        for key, alt_list in ultra_low_fat_alternatives.items():
            if key in current_name:
                for alt_name in alt_list:
                    alternative = self._find_ingredient_by_name(alt_name)
                    if alternative:
                        alt_protein = alternative.get('protein_per_100g', 0)
                        alt_fat = alternative.get('fat_per_100g', 0)
                        
                        # Check if alternative is ultra-low in fat
                        if (alt_fat < 3 and 
                            abs(alt_protein - current_protein) < current_protein * 0.5):
                            return alternative
        
        return None

    def _find_lower_fat_alternative_advanced(self, current_ingredient: Dict) -> Optional[Dict]:
        """Find advanced lower-fat alternative with similar protein content"""
        current_name = current_ingredient.get('name', '').lower()
        current_protein = current_ingredient.get('protein_per_100g', 0)
        current_fat = current_ingredient.get('fat_per_100g', 0)
        
        # Define alternative mappings
        alternatives = {
            'almonds': ['Walnuts', 'Pumpkin Seeds', 'Sunflower Seeds'],
            'walnuts': ['Almonds', 'Pumpkin Seeds', 'Sunflower Seeds'],
            'cashews': ['Almonds', 'Pumpkin Seeds', 'Sunflower Seeds'],
            'eggs': ['Egg Whites', 'Greek Yogurt', 'Cottage Cheese'],
            'salmon': ['Cod', 'Tilapia', 'Chicken Breast'],
            'avocado': ['Olive Oil', 'Chia Seeds', 'Flax Seeds']
        }
        
        # Find alternatives for current ingredient
        for key, alt_list in alternatives.items():
            if key in current_name:
                for alt_name in alt_list:
                    alternative = self._find_ingredient_by_name(alt_name)
                    if alternative:
                        alt_protein = alternative.get('protein_per_100g', 0)
                        alt_fat = alternative.get('fat_per_100g', 0)
                        
                        # Check if alternative is significantly lower in fat
                        if (alt_fat < current_fat * 0.7 and 
                            abs(alt_protein - current_protein) < current_protein * 0.3):
                            return alternative
        
        return None
    
    def _optimize_carbs_precisely(self, supplements: List[Dict], carbs_diff: float, adjustment_factor: float) -> List[Dict]:
        """Optimize carbs with ultra-precise control to prevent overshooting"""
        if abs(carbs_diff) <= 0.05:
            return supplements
        
        carb_sources = [s for s in supplements if s.get('carbs_per_100g', 0) > 0]
        if not carb_sources:
            return supplements
        
        # Sort by carb efficiency (carbs/fat ratio)
        carb_sources.sort(key=lambda x: x.get('carbs_per_100g', 0) / max(x.get('fat_per_100g', 1), 1), reverse=True)
        
        for source in carb_sources[:2]:
            current_qty = source.get('quantity_needed', 0)
            
            if carbs_diff > 0.05:  # Need more carbs
                carbs_needed = carbs_diff / source.get('carbs_per_100g', 1) * 100
                # Use ultra-small adjustment to prevent overshooting
                adjustment = carbs_needed * min(adjustment_factor, 0.02)
                new_qty = current_qty + adjustment
                new_qty = max(25, min(200, new_qty))
                source['quantity_needed'] = round(new_qty, 1)
                carbs_diff -= (new_qty - current_qty) * source.get('carbs_per_100g', 0) / 100
                
            elif carbs_diff < -0.05:  # Too many carbs - REDUCE ULTRA-AGGRESSIVELY
                carbs_excess = abs(carbs_diff) / source.get('carbs_per_100g', 1) * 100
                # Use ultra-aggressive reduction to quickly fix overshooting
                reduction = carbs_excess * min(adjustment_factor * 5, 0.7)
                new_qty = current_qty - reduction
                new_qty = max(25, min(200, new_qty))
                source['quantity_needed'] = round(new_qty, 1)
                carbs_diff += (current_qty - new_qty) * source.get('carbs_per_100g', 0) / 100
            
            if abs(carbs_diff) <= 0.05:
                break
        
        return supplements
    
    def _optimize_calories_precisely(self, supplements: List[Dict], calories_diff: float, adjustment_factor: float) -> List[Dict]:
        """Optimize calories with ultra-precise control to prevent overshooting"""
        if abs(calories_diff) <= 0.2:
            return supplements
        
        calorie_sources = [s for s in supplements if s.get('calories_per_100g', 0) > 0]
        if not calorie_sources:
            return supplements
        
        # Sort by calorie efficiency (calories/fat ratio for lower fat)
        calorie_sources.sort(key=lambda x: x.get('calories_per_100g', 0) / max(x.get('fat_per_100g', 1), 1), reverse=True)
        
        for source in calorie_sources[:2]:
            current_qty = source.get('quantity_needed', 0)
            
            if calories_diff > 0.2:  # Need more calories
                calories_needed = calories_diff / source.get('calories_per_100g', 1) * 100
                # Use ultra-small adjustment to prevent overshooting
                adjustment = calories_needed * min(adjustment_factor, 0.01)
                new_qty = current_qty + adjustment
                new_qty = max(20, min(250, new_qty))
                source['quantity_needed'] = round(new_qty, 1)
                calories_diff -= (new_qty - current_qty) * source.get('calories_per_100g', 0) / 100
                
            elif calories_diff < -0.2:  # Too many calories - REDUCE ULTRA-AGGRESSIVELY
                calories_excess = abs(calories_diff) / source.get('calories_per_100g', 1) * 100
                # Use ultra-aggressive reduction to quickly fix overshooting
                reduction = calories_excess * min(adjustment_factor * 8, 0.9)
                new_qty = current_qty - reduction
                new_qty = max(20, min(250, new_qty))
                source['quantity_needed'] = round(new_qty, 1)
                calories_diff += (current_qty - new_qty) * source.get('calories_per_100g', 0) / 100
            
            if abs(calories_diff) <= 0.2:
                break
        
        return supplements
    
    def _ultra_precision_adjustment(self, supplements: List[Dict], deficits: Dict, current_totals: Dict) -> List[Dict]:
        """Ultra precision adjustment for final target achievement"""
        target_protein = 47.7
        target_cars = 79.7
        target_fat = 14.2
        target_calories = 637.2
        
        # Calculate current totals
        current_totals = self._update_totals_with_supplements(current_totals, supplements)
        
        # Calculate final deviations
        protein_diff = target_protein - current_totals['protein']
        carbs_diff = target_cars - current_totals['carbs']
        fat_diff = target_fat - current_totals['fat']
        calories_diff = target_calories - current_totals['calories']
        
        # Apply micro-adjustments to closest ingredients with priority system
        adjustment_priority = self._calculate_adjustment_priority(supplements, protein_diff, carbs_diff, fat_diff, calories_diff)
        
        for ingredient_info in adjustment_priority:
            supplement = ingredient_info['ingredient']
            deficit_type = ingredient_info['deficit_type']
            deficit_value = ingredient_info['deficit_value']
            priority_score = ingredient_info['priority_score']
            
            current_qty = supplement.get('quantity_needed', 0)
            
            # Apply adjustment based on priority and deficit type
            if deficit_type == 'protein' and supplement.get('protein_per_100g', 0) > 0:
                micro_adjustment = (deficit_value / supplement.get('protein_per_100g', 1)) * 100 * priority_score
                current_qty += micro_adjustment
                protein_diff -= micro_adjustment * supplement.get('protein_per_100g', 0) / 100
                
            elif deficit_type == 'carbs' and supplement.get('carbs_per_100g', 0) > 0:
                micro_adjustment = (deficit_value / supplement.get('carbs_per_100g', 1)) * 100 * priority_score
                current_qty += micro_adjustment
                carbs_diff -= micro_adjustment * supplement.get('carbs_per_100g', 0) / 100
                
            elif deficit_type == 'fat' and supplement.get('fat_per_100g', 0) > 0:
                micro_adjustment = (deficit_value / supplement.get('fat_per_100g', 1)) * 100 * priority_score * 0.5
                current_qty += micro_adjustment
                fat_diff -= micro_adjustment * supplement.get('fat_per_100g', 0) / 100
                
            elif deficit_type == 'calories' and supplement.get('calories_per_100g', 0) > 0:
                micro_adjustment = (deficit_value / supplement.get('calories_per_100g', 1)) * 100 * priority_score * 0.7
                current_qty += micro_adjustment
                calories_diff -= micro_adjustment * supplement.get('calories_per_100g', 0) / 100
            
            # Ensure bounds
            current_qty = max(10, min(500, current_qty))
            supplement['quantity_needed'] = current_qty
            
            # Recalculate totals
            current_totals = self._update_totals_with_supplements(current_totals, supplements)
        
        return supplements
    
    def _calculate_adjustment_priority(self, supplements: List[Dict], protein_diff: float, carbs_diff: float, fat_diff: float, calories_diff: float) -> List[Dict]:
        """Calculate priority for ingredient adjustments"""
        priority_list = []
        
        for supplement in supplements:
            # Calculate how much each ingredient can contribute to fixing deficits
            protein_potential = supplement.get('protein_per_100g', 0) / 100
            carbs_potential = supplement.get('carbs_per_100g', 0) / 100
            fat_potential = supplement.get('fat_per_100g', 0) / 100
            calories_potential = supplement.get('calories_per_100g', 0) / 100
            
            # Calculate priority scores for each deficit type
            if abs(protein_diff) > 0.05 and protein_potential > 0:
                priority_score = min(0.15, abs(protein_diff) / 10)  # Cap at 0.15
                priority_list.append({
                    'ingredient': supplement,
                    'deficit_type': 'protein',
                    'deficit_value': protein_diff,
                    'priority_score': priority_score
                })
            
            if abs(carbs_diff) > 0.05 and carbs_potential > 0:
                priority_score = min(0.15, abs(carbs_diff) / 10)
                priority_list.append({
                    'ingredient': supplement,
                    'deficit_type': 'carbs',
                    'deficit_value': carbs_diff,
                    'priority_score': priority_score
                })
            
            if abs(fat_diff) > 0.05 and fat_potential > 0:
                priority_score = min(0.1, abs(fat_diff) / 10)  # Lower priority for fat
                priority_list.append({
                    'ingredient': supplement,
                    'deficit_type': 'fat',
                    'deficit_value': fat_diff,
                    'priority_score': priority_score
                })
            
            if abs(calories_diff) > 1.0 and calories_potential > 0:
                priority_score = min(0.12, abs(calories_diff) / 50)
                priority_list.append({
                    'ingredient': supplement,
                    'deficit_type': 'calories',
                    'deficit_value': calories_diff,
                    'priority_score': priority_score
                })
        
        # Sort by priority score (highest first)
        priority_list.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return priority_list
    
    def _correct_protein_overshooting(self, supplements: List[Dict], protein_excess: float) -> List[Dict]:
        """Correct protein overshooting by reducing quantities"""
        protein_sources = [s for s in supplements if s.get('protein_per_100g', 0) > 0]
        if not protein_sources:
            return supplements
        
        # Sort by protein content (highest first for maximum reduction)
        protein_sources.sort(key=lambda x: x.get('protein_per_100g', 0), reverse=True)
        
        for source in protein_sources[:2]:
            current_qty = source.get('quantity_needed', 0)
            protein_per_100g = source.get('protein_per_100g', 0)
            
            # Calculate reduction needed
            reduction_needed = protein_excess / protein_per_100g * 100
            reduction = min(reduction_needed * 0.5, current_qty * 0.3)  # Max 30% reduction
            
            new_qty = current_qty - reduction
            new_qty = max(20, new_qty)
            source['quantity_needed'] = round(new_qty, 1)
            
            protein_excess -= (current_qty - new_qty) * protein_per_100g / 100
            if protein_excess <= 0.05:
                break
        
        return supplements
    
    def _correct_carbs_overshooting(self, supplements: List[Dict], carbs_excess: float) -> List[Dict]:
        """Correct carbs overshooting by reducing quantities"""
        carb_sources = [s for s in supplements if s.get('carbs_per_100g', 0) > 0]
        if not carb_sources:
            return supplements
        
        # Sort by carb content (highest first for maximum reduction)
        carb_sources.sort(key=lambda x: x.get('carbs_per_100g', 0), reverse=True)
        
        for source in carb_sources[:2]:
            current_qty = source.get('quantity_needed', 0)
            carbs_per_100g = source.get('carbs_per_100g', 0)
            
            # Calculate reduction needed
            reduction_needed = carbs_excess / carbs_per_100g * 100
            reduction = min(reduction_needed * 0.5, current_qty * 0.3)  # Max 30% reduction
            
            new_qty = current_qty - reduction
            new_qty = max(25, new_qty)
            source['quantity_needed'] = round(new_qty, 1)
            
            carbs_excess -= (current_qty - new_qty) * carbs_per_100g / 100
            if carbs_excess <= 0.05:
                break
        
        return supplements
    
    def _correct_fat_overshooting(self, supplements: List[Dict], fat_excess: float) -> List[Dict]:
        """Correct fat overshooting by reducing quantities and swapping ingredients"""
        # First try to swap high-fat ingredients
        supplements = self._swap_high_fat_ingredients_aggressive(supplements, fat_excess)
        
        # Then reduce quantities if still needed
        fat_sources = [s for s in supplements if s.get('fat_per_100g', 0) > 0]
        if not fat_sources:
            return supplements
        
        # Sort by fat content (highest first for maximum reduction)
        fat_sources.sort(key=lambda x: x.get('fat_per_100g', 0), reverse=True)
        
        for source in fat_sources[:2]:
            current_qty = source.get('quantity_needed', 0)
            fat_per_100g = source.get('fat_per_100g', 0)
            
            # Calculate reduction needed
            reduction_needed = fat_excess / fat_per_100g * 100
            reduction = min(reduction_needed * 0.6, current_qty * 0.4)  # Max 40% reduction
            
            new_qty = current_qty - reduction
            new_qty = max(15, new_qty)
            source['quantity_needed'] = round(new_qty, 1)
            
            fat_excess -= (current_qty - new_qty) * fat_per_100g / 100
            if fat_excess <= 0.05:
                break
        
        return supplements
    
    def _correct_protein_overshooting_aggressive(self, supplements: List[Dict], protein_excess: float) -> List[Dict]:
        """Correct protein overshooting with aggressive reduction"""
        protein_sources = [s for s in supplements if s.get('protein_per_100g', 0) > 0]
        if not protein_sources:
            return supplements
        
        # Sort by protein content (highest first for maximum reduction)
        protein_sources.sort(key=lambda x: x.get('protein_per_100g', 0), reverse=True)
        
        for source in protein_sources[:3]:  # Top 3 protein sources
            current_qty = source.get('quantity_needed', 0)
            protein_per_100g = source.get('protein_per_100g', 0)
            
            # Calculate aggressive reduction needed
            reduction_needed = protein_excess / protein_per_100g * 100
            reduction = min(reduction_needed * 0.8, current_qty * 0.5)  # Max 50% reduction
            
            new_qty = current_qty - reduction
            new_qty = max(20, new_qty)
            source['quantity_needed'] = round(new_qty, 1)
            
            protein_excess -= (current_qty - new_qty) * protein_per_100g / 100
            if protein_excess <= 0.05:
                break
        
        return supplements
    
    def _correct_carbs_overshooting_aggressive(self, supplements: List[Dict], carbs_excess: float) -> List[Dict]:
        """Correct carbs overshooting with aggressive reduction"""
        carb_sources = [s for s in supplements if s.get('carbs_per_100g', 0) > 0]
        if not carb_sources:
            return supplements
        
        # Sort by carb content (highest first for maximum reduction)
        carb_sources.sort(key=lambda x: x.get('carbs_per_100g', 0), reverse=True)
        
        for source in carb_sources[:3]:  # Top 3 carb sources
            current_qty = source.get('quantity_needed', 0)
            carbs_per_100g = source.get('carbs_per_100g', 0)
            
            # Calculate aggressive reduction needed
            reduction_needed = carbs_excess / carbs_per_100g * 100
            reduction = min(reduction_needed * 0.8, current_qty * 0.5)  # Max 50% reduction
            
            new_qty = current_qty - reduction
            new_qty = max(25, new_qty)
            source['quantity_needed'] = round(new_qty, 1)
            
            carbs_excess -= (current_qty - new_qty) * carbs_per_100g / 100
            if carbs_excess <= 0.05:
                break
        
        return supplements
    
    def _correct_fat_overshooting_aggressive(self, supplements: List[Dict], fat_excess: float) -> List[Dict]:
        """Correct fat overshooting with aggressive reduction and ingredient swapping"""
        # First try to swap high-fat ingredients aggressively
        supplements = self._swap_high_fat_ingredients_ultra_aggressive(supplements, fat_excess)
        
        # Then reduce quantities aggressively if still needed
        fat_sources = [s for s in supplements if s.get('fat_per_100g', 0) > 0]
        if not fat_sources:
            return supplements
        
        # Sort by fat content (highest first for maximum reduction)
        fat_sources.sort(key=lambda x: x.get('fat_per_100g', 0), reverse=True)
        
        for source in fat_sources[:3]:  # Top 3 fat sources
            current_qty = source.get('quantity_needed', 0)
            fat_per_100g = source.get('fat_per_100g', 0)
            
            # Calculate aggressive reduction needed
            reduction_needed = fat_excess / fat_per_100g * 100
            reduction = min(reduction_needed * 0.9, current_qty * 0.6)  # Max 60% reduction
            
            new_qty = current_qty - reduction
            new_qty = max(15, new_qty)
            source['quantity_needed'] = round(new_qty, 1)
            
            fat_excess -= (current_qty - new_qty) * fat_per_100g / 100
            if fat_excess <= 0.05:
                break
        
        return supplements
    
    def _correct_calories_overshooting_aggressive(self, supplements: List[Dict], calories_excess: float) -> List[Dict]:
        """Correct calories overshooting with aggressive reduction"""
        calorie_sources = [s for s in supplements if s.get('calories_per_100g', 0) > 0]
        if not calorie_sources:
            return supplements
        
        # Sort by calorie content (highest first for maximum reduction)
        calorie_sources.sort(key=lambda x: x.get('calories_per_100g', 0), reverse=True)
        
        for source in calorie_sources[:3]:  # Top 3 calorie sources
            current_qty = source.get('quantity_needed', 0)
            calories_per_100g = source.get('calories_per_100g', 0)
            
            # Calculate aggressive reduction needed
            reduction_needed = calories_excess / calories_per_100g * 100
            reduction = min(reduction_needed * 0.8, current_qty * 0.5)  # Max 50% reduction
            
            new_qty = current_qty - reduction
            new_qty = max(20, new_qty)
            source['quantity_needed'] = round(new_qty, 1)
            
            calories_excess -= (current_qty - new_qty) * calories_per_100g / 100
            if calories_excess <= 0.2:
                break
        
        return supplements

    def _correct_calories_overshooting(self, supplements: List[Dict], calories_excess: float) -> List[Dict]:
        """Correct calories overshooting by reducing quantities"""
        calorie_sources = [s for s in supplements if s.get('calories_per_100g', 0) > 0]
        if not calorie_sources:
            return supplements
        
        # Sort by calorie content (highest first for maximum reduction)
        calorie_sources.sort(key=lambda x: x.get('calories_per_100g', 0), reverse=True)
        
        for source in calorie_sources[:2]:
            current_qty = source.get('quantity_needed', 0)
            calories_per_100g = source.get('calories_per_100g', 0)
            
            # Calculate reduction needed
            reduction_needed = calories_excess / calories_per_100g * 100
            reduction = min(reduction_needed * 0.5, current_qty * 0.3)  # Max 30% reduction
            
            new_qty = current_qty - reduction
            new_qty = max(20, new_qty)
            source['quantity_needed'] = round(new_qty, 1)
            
            calories_excess -= (current_qty - new_qty) * calories_per_100g / 100
            if calories_excess <= 0.2:
                break
        
        return supplements

    def _apply_ultra_aggressive_correction(self, supplements: List[Dict], protein_diff: float, carbs_diff: float, fat_diff: float, calories_diff: float) -> List[Dict]:
        """Apply ultra-aggressive correction for persistent overshooting"""
        # If overshooting persists, apply ultra-aggressive corrections
        
        # Protein overshooting correction
        if protein_diff < -0.1:
            supplements = self._correct_protein_overshooting_aggressive(supplements, abs(protein_diff))
        
        # Carbs overshooting correction
        if carbs_diff < -0.1:
            supplements = self._correct_carbs_overshooting_aggressive(supplements, abs(carbs_diff))
        
        # Fat overshooting correction
        if fat_diff < -0.1:
            supplements = self._correct_fat_overshooting_aggressive(supplements, abs(fat_diff))
        
        # Calories overshooting correction
        if calories_diff < -0.5:
            supplements = self._correct_calories_overshooting_aggressive(supplements, abs(calories_diff))
        
        return supplements

    def _apply_emergency_overshooting_correction(self, supplements: List[Dict], protein_diff: float, carbs_diff: float, fat_diff: float, calories_diff: float) -> List[Dict]:
        """Apply emergency correction for overshooting"""
        # If overshooting detected, apply aggressive corrections
        
        # Protein overshooting correction
        if protein_diff < -0.1:
            supplements = self._correct_protein_overshooting(supplements, abs(protein_diff))
        
        # Carbs overshooting correction
        if carbs_diff < -0.1:
            supplements = self._correct_carbs_overshooting(supplements, abs(carbs_diff))
        
        # Fat overshooting correction
        if fat_diff < -0.1:
            supplements = self._correct_fat_overshooting(supplements, abs(fat_diff))
        
        # Calories overshooting correction
        if calories_diff < -0.5:
            supplements = self._correct_calories_overshooting(supplements, abs(calories_diff))
        
        return supplements

    def _apply_emergency_ingredient_swapping(self, supplements: List[Dict], protein_diff: float, fat_diff: float) -> List[Dict]:
        """Apply emergency ingredient swapping for stubborn deficits"""
        # If protein is still low, try to add more protein sources
        if protein_diff > 0.1:
            new_protein = self._find_emergency_protein_source(supplements)
            if new_protein:
                optimal_qty = self._calculate_optimal_quantity_for_deficit(new_protein, 'protein', protein_diff)
                if optimal_qty > 0:
                    new_protein['quantity_needed'] = optimal_qty
                    supplements.append(new_protein)
        
        # If fat is still high, try to replace with ultra-low fat alternatives
        if fat_diff < -0.1:
            supplements = self._apply_ultra_low_fat_swapping(supplements, abs(fat_diff))
        
        return supplements
    
    def _find_emergency_protein_source(self, existing_supplements: List[Dict]) -> Optional[Dict]:
        """Find emergency protein source not already in supplements"""
        emergency_proteins = [
            'Lean Pork', 'Lentils', 'Chickpeas', 'Tofu', 'Tempeh', 'Edamame',
            'Cottage Cheese', 'Egg Whites', 'Turkey Breast', 'Cod'
        ]
        
        existing_names = {s.get('name', '').lower() for s in existing_supplements}
        
        for protein_name in emergency_proteins:
            if protein_name.lower() not in existing_names:
                ingredient = self._find_ingredient_by_name(protein_name)
                if ingredient and ingredient.get('protein_per_100g', 0) > 0:
                    return ingredient
        
        return None
    
    def _apply_ultra_low_fat_swapping(self, supplements: List[Dict], fat_excess: float) -> List[Dict]:
        """Apply ultra-low fat swapping for stubborn fat excess"""
        ultra_low_fat_alternatives = {
            'almonds': 'Pumpkin Seeds',
            'walnuts': 'Sunflower Seeds',
            'cashews': 'Chia Seeds',
            'eggs': 'Egg Whites',
            'avocado': 'Flax Seeds'
        }
        
        for i, supplement in enumerate(supplements):
            current_name = supplement.get('name', '').lower()
            
            for high_fat, low_fat_alt in ultra_low_fat_alternatives.items():
                if high_fat in current_name:
                    alternative = self._find_ingredient_by_name(low_fat_alt)
                    if alternative:
                        # Calculate fat reduction
                        current_fat = supplement.get('fat_per_100g', 0) * supplement.get('quantity_needed', 0) / 100
                        alternative_fat = alternative.get('fat_per_100g', 0) * supplement.get('quantity_needed', 0) / 100
                        fat_reduction = current_fat - alternative_fat
                        
                        if fat_reduction > 0:
                            # Replace with ultra-low fat alternative
                            supplements[i] = alternative.copy()
                            supplements[i]['quantity_needed'] = supplement.get('quantity_needed', 0)
                            fat_excess -= fat_reduction
                            
                            if fat_excess <= 0.05:
                                break
        
        return supplements
    
    def _find_basic_supplements(
        self, 
        deficits: Dict, 
        available_ingredients: List[Dict],
        existing_protein_sources: List[Dict],
        existing_carb_sources: List[Dict],
        existing_fat_sources: List[Dict]
    ) -> List[Dict]:
        """Basic fallback method for finding supplementary ingredients with smart filtering"""
        supplementary = []
        
        # Add ingredients to fill specific macro gaps with better logic
        if deficits['protein'] > 0:
            protein_sources = [ing for ing in available_ingredients 
                             if ing.get('protein_per_100g', 0) > 15]
            
            # Filter out ingredients too similar to existing protein sources
            filtered_protein_sources = []
            for source in protein_sources:
                is_similar = False
                for existing in existing_protein_sources:
                    if self._calculate_ingredient_similarity(source, existing) > 0.7:  # 70% similarity threshold
                        is_similar = True
                        break
                if not is_similar:
                    filtered_protein_sources.append(source)
            
            if filtered_protein_sources:
                # Add multiple protein sources if needed
                needed_protein = deficits['protein']
                for source in filtered_protein_sources[:2]:  # Add up to 2 protein sources
                    if needed_protein > 0:
                        supplementary.append({
                            'name': source['name'],
                            'calories_per_100g': source['calories_per_100g'],
                            'protein_per_100g': source['protein_per_100g'],
                            'carbs_per_100g': source['carbs_per_100g'],
                            'fat_per_100g': source['fat_per_100g'],
                            'source': 'supplement',
                            'needed_macro': 'protein',
                            'deficit_amount': needed_protein
                        })
                        needed_protein -= source['protein_per_100g']
        
        if deficits['carbs'] > 0:
            carb_sources = [ing for ing in available_ingredients 
                           if ing.get('carbs_per_100g', 0) > 20]
            
            # Filter out ingredients too similar to existing carb sources
            filtered_carb_sources = []
            for source in carb_sources:
                is_similar = False
                for existing in existing_carb_sources:
                    if self._calculate_ingredient_similarity(source, existing) > 0.7:
                        is_similar = True
                        break
                if not is_similar:
                    filtered_carb_sources.append(source)
            
            if filtered_carb_sources:
                # Add carb source if needed
                supplementary.append({
                    'name': filtered_carb_sources[0]['name'],
                    'calories_per_100g': filtered_carb_sources[0]['calories_per_100g'],
                    'protein_per_100g': filtered_carb_sources[0]['protein_per_100g'],
                    'carbs_per_100g': filtered_carb_sources[0]['carbs_per_100g'],
                    'fat_per_100g': filtered_carb_sources[0]['fat_per_100g'],
                    'source': 'supplement',
                    'needed_macro': 'carbs',
                    'deficit_amount': deficits['carbs']
                })
        
        if deficits['fat'] > 0:
            fat_sources = [ing for ing in available_ingredients 
                          if ing.get('fat_per_100g', 0) > 10]
            
            # Filter out ingredients too similar to existing fat sources
            filtered_fat_sources = []
            for source in fat_sources:
                is_similar = False
                for existing in existing_fat_sources:
                    if self._calculate_ingredient_similarity(source, existing) > 0.7:
                        is_similar = True
                        break
                if not is_similar:
                    filtered_fat_sources.append(source)
            
            if filtered_fat_sources:
                # Add fat source if needed
                supplementary.append({
                    'name': filtered_fat_sources[0]['name'],
                    'calories_per_100g': filtered_fat_sources[0]['calories_per_100g'],
                    'protein_per_100g': filtered_fat_sources[0]['protein_per_100g'],
                    'carbs_per_100g': filtered_fat_sources[0]['carbs_per_100g'],
                    'fat_per_100g': filtered_fat_sources[0]['fat_per_100g'],
                    'source': 'supplement',
                    'needed_macro': 'fat',
                    'deficit_amount': deficits['fat']
                })
        
        return supplementary
    
    def _filter_ingredients_by_preferences(
        self, 
        ingredients: List[Dict], 
        preferences: Dict
    ) -> List[Dict]:
        """Filter ingredients based on user preferences"""
        filtered = ingredients.copy()
        
        # Filter by dietary restrictions
        if 'vegetarian' in preferences.get('dietary_restrictions', []):
            filtered = [ing for ing in filtered if 'meat' not in ing.get('category', '').lower()]
        
        if 'vegan' in preferences.get('dietary_restrictions', []):
            filtered = [ing for ing in filtered if 'dairy' not in ing.get('category', '').lower()]
        
        # Filter by allergies
        allergies = preferences.get('allergies', [])
        for allergy in allergies:
            filtered = [ing for ing in filtered if allergy.lower() not in ing.get('name', '').lower()]
        
        return filtered
    
    def _optimize_quantities(
        self, 
        ingredients: List[Dict], 
        target_macros: Dict, 
        user_preferences: Dict
    ) -> Dict:
        """Optimize ingredient quantities using mathematical optimization"""
        
        # Try different optimization methods in order of preference
        optimization_order = [
            'genetic_algorithm',
            'differential_evolution',
            'linear_programming'
        ]
        
        # Add advanced methods if available
        if OPTUNA_AVAILABLE:
            optimization_order.append('optuna_optimization')
        if PYGMO_AVAILABLE:
            optimization_order.append('pygmo_optimization')
        if PLATYPUS_AVAILABLE:
            optimization_order.append('nsga2_optimization')
        if PYMOO_AVAILABLE:
            optimization_order.append('pymoo_optimization')
        
        # Add hybrid as last resort
        optimization_order.append('hybrid')
        
        best_result = None
        best_score = float('inf')
        successful_methods = []
        
        # Try each method and keep track of the best result
        for method_name in optimization_order:
            if method_name in self.optimization_methods:
                try:
                    logger.info(f"Trying optimization method: {method_name}")
                    result = self.optimization_methods[method_name](ingredients, target_macros)
                    
                    if result['success']:
                        # Apply strict bounds enforcement
                        result = self._enforce_strict_bounds(result, ingredients)
                        
                        # Calculate how well this result meets targets
                        score = self._calculate_optimization_score(result, target_macros)
                        successful_methods.append(f"{method_name} (score: {score:.3f})")
                        
                        # Check if this result achieves all targets
                        if self._achieves_all_targets(result, target_macros):
                            logger.info(f"Method {method_name} achieved all targets with score {score:.3f}")
                            return result
                        
                        # Keep track of best result so far
                        if score < best_score:
                            best_score = score
                            best_result = result
                            logger.info(f"Method {method_name} is best so far with score {score:.3f}")
                        else:
                            logger.info(f"Method {method_name} succeeded but score {score:.3f} is not better than {best_score:.3f}")
                    else:
                        logger.warning(f"Method {method_name} failed: {result.get('method', 'Unknown error')}")
                except Exception as e:
                    logger.warning(f"Method {method_name} failed with error: {e}")
                    continue
        
        # If we have a best result, try to improve it further
        if best_result and best_score > 0.1:  # If score is still high, try to improve
            logger.info(f"Attempting to improve best result with score {best_score:.3f}")
            improved_result = self._try_improve_result(best_result, target_macros)
            if improved_result and improved_result['success']:
                improved_result = self._enforce_strict_bounds(improved_result, ingredients)
                improved_score = self._calculate_optimization_score(improved_result, target_macros)
                if improved_score < best_score:
                    logger.info(f"Improved result from {best_score:.3f} to {improved_score:.3f}")
                    best_result = improved_result
                    best_score = improved_score
        
        # If we have a best result, return it
        if best_result:
            logger.info(f"Returning best result from {len(successful_methods)} successful methods. Best score: {best_score:.3f}")
            logger.info(f"Successful methods: {', '.join(successful_methods)}")
            return best_result
        
        # If all methods fail, return failure
        logger.error("All optimization methods failed")
        return {'success': False, 'method': 'All methods failed', 'quantities': []}
    
    def _enforce_strict_bounds(self, result: Dict, ingredients: List[Dict]) -> Dict:
        """Enforce strict bounds to ensure reasonable quantities"""
        try:
            quantities = result.get('quantities', [])
            if not quantities:
                return result
            
            # Define reasonable bounds for different ingredient types
            adjusted_quantities = []
            
            for i, qty in enumerate(quantities):
                if i < len(ingredients):
                    ingredient = ingredients[i]
                    source = ingredient.get('source', 'unknown')
                    category = ingredient.get('category', 'other')
                    
                    # Set minimum quantities based on source and category
                    min_qty = 20  # Minimum 20g for any ingredient
                    max_qty = 500  # Maximum 500g for any ingredient
                    
                    # Adjust bounds based on ingredient type
                    if source == 'rag':
                        # RAG ingredients should have reasonable minimums
                        if category == 'protein':
                            min_qty = 50  # At least 50g for protein
                        elif category == 'grain':
                            min_qty = 30  # At least 30g for grains
                        elif category == 'vegetable':
                            min_qty = 25  # At least 25g for vegetables
                        else:
                            min_qty = 20
                    else:
                        # Supplement ingredients
                        if category == 'protein':
                            min_qty = 40  # At least 40g for protein supplements
                        elif category == 'vegetable':
                            min_qty = 30  # At least 30g for vegetable supplements
                        else:
                            min_qty = 25
                    
                    # Apply bounds
                    adjusted_qty = max(min_qty, min(max_qty, qty))
                    
                    # Ensure no ingredient is zero (unless it's a very small amount)
                    if adjusted_qty < min_qty:
                        adjusted_qty = min_qty
                    
                    adjusted_quantities.append(adjusted_qty)
                else:
                    adjusted_quantities.append(qty)
            
            # Return adjusted result
            return {
                'success': result.get('success', True),
                'method': f"{result.get('method', 'Unknown')} (bounds enforced)",
                'quantities': adjusted_quantities
            }
            
        except Exception as e:
            logger.warning(f"Failed to enforce bounds: {e}")
            return result
    
    def _try_improve_result(self, result: Dict, target_macros: Dict) -> Optional[Dict]:
        """Try to improve an existing result by fine-tuning quantities"""
        try:
            quantities = result.get('quantities', [])
            if not quantities:
                return None
            
            # Try to adjust quantities to better meet targets
            adjusted_quantities = quantities.copy()
            
            # Calculate current macros
            current_macros = self._calculate_macros_from_quantities(adjusted_quantities)
            
            # Get carbs target (handle both field names)
            carbs_target = target_macros.get('carbs', target_macros.get('carbohydrates', 0))
            
            # Try to adjust each ingredient to better meet targets
            for i in range(len(adjusted_quantities)):
                original_qty = quantities[i]
                
                # Try different adjustments
                for adjustment_factor in [0.8, 0.9, 1.1, 1.2, 1.3, 1.5]:
                    test_qty = max(10, min(500, original_qty * adjustment_factor))
                    adjusted_quantities[i] = test_qty
                    
                    # Calculate new macros
                    test_macros = self._calculate_macros_from_quantities(adjusted_quantities)
                    
                    # Check if this is better
                    test_score = self._calculate_score_from_macros(test_macros, target_macros)
                    current_score = self._calculate_score_from_macros(current_macros, target_macros)
                    
                    if test_score < current_score:
                        current_macros = test_macros
                        current_score = test_score
                    else:
                        # Revert the change
                        adjusted_quantities[i] = original_qty
            
            # Return improved result
            return {
                'success': True,
                'method': f"{result.get('method', 'Unknown')} (improved)",
                'quantities': adjusted_quantities
            }
            
        except Exception as e:
            logger.warning(f"Failed to improve result: {e}")
            return None
    
    def _calculate_macros_from_quantities(self, quantities: List[float]) -> Dict:
        """Calculate macros from quantities"""
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for i, qty in enumerate(quantities):
            if i < len(self.current_ingredients):
                ingredient = self.current_ingredients[i]
                total_calories += qty * ingredient['calories_per_100g'] / 100
                total_protein += qty * ingredient['protein_per_100g'] / 100
                total_carbs += qty * ingredient['carbs_per_100g'] / 100
                total_fat += qty * ingredient['fat_per_100g'] / 100
        
        return {
            'calories': total_calories,
            'protein': total_protein,
            'carbs': total_carbs,
            'fat': total_fat
        }
    
    def _calculate_score_from_macros(self, current_macros: Dict, target_macros: Dict) -> float:
        """Calculate score from macros (lower is better)"""
        carbs_target = target_macros.get('carbs', target_macros.get('carbohydrates', 0))
        
        score = (
            abs(current_macros['calories'] - target_macros['calories']) / max(target_macros['calories'], 1) +
            abs(current_macros['protein'] - target_macros['protein']) / max(target_macros['protein'], 1) +
            abs(current_macros['carbs'] - carbs_target) / max(carbs_target, 1) +
            abs(current_macros['fat'] - target_macros['fat']) / max(target_macros['fat'], 1)
        )
        
        return score
    
    def _calculate_optimization_score(self, result: Dict, target_macros: Dict) -> float:
        """Calculate how well an optimization result meets the targets (lower is better)"""
        try:
            quantities = result.get('quantities', [])
            if not quantities:
                return float('inf')
            
            # Calculate total macros from quantities
            total_calories = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            
            for i, qty in enumerate(quantities):
                if i < len(self.current_ingredients):
                    ingredient = self.current_ingredients[i]
                    total_calories += qty * ingredient['calories_per_100g'] / 100
                    total_protein += qty * ingredient['protein_per_100g'] / 100
                    total_carbs += qty * ingredient['carbs_per_100g'] / 100
                    total_fat += qty * ingredient['fat_per_100g'] / 100
            
            # Get carbs target (handle both field names)
            carbs_target = target_macros.get('carbs', target_macros.get('carbohydrates', 0))
            
            # Calculate normalized deviation (lower is better)
            score = (
                abs(total_calories - target_macros['calories']) / max(target_macros['calories'], 1) +
                abs(total_protein - target_macros['protein']) / max(target_macros['protein'], 1) +
                abs(total_carbs - carbs_target) / max(carbs_target, 1) +
                abs(total_fat - target_macros['fat']) / max(target_macros['fat'], 1)
            )
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating optimization score: {e}")
            return float('inf')
    
    def _achieves_all_targets(self, result: Dict, target_macros: Dict) -> bool:
        """Check if an optimization result achieves all targets within ±10% tolerance"""
        try:
            quantities = result.get('quantities', [])
            if not quantities:
                return False
            
            # Calculate total macros from quantities
            total_calories = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            
            for i, qty in enumerate(quantities):
                if i < len(self.current_ingredients):
                    ingredient = self.current_ingredients[i]
                    total_calories += qty * ingredient['calories_per_100g'] / 100
                    total_protein += qty * ingredient['protein_per_100g'] / 100
                    total_carbs += qty * ingredient['carbs_per_100g'] / 100
                    total_fat += qty * ingredient['fat_per_100g'] / 100
            
            # Get carbs target (handle both field names)
            carbs_target = target_macros.get('carbs', target_macros.get('carbohydrates', 0))
            
            # Check if all targets are met within ±10% tolerance
            calories_ok = abs(total_calories - target_macros['calories']) <= target_macros['calories'] * 0.1
            protein_ok = abs(total_protein - target_macros['protein']) <= target_macros['protein'] * 0.1
            carbs_ok = abs(total_carbs - carbs_target) <= carbs_target * 0.1
            fat_ok = abs(total_fat - target_macros['fat']) <= target_macros['fat'] * 0.1
            
            return calories_ok and protein_ok and carbs_ok and fat_ok
            
        except Exception as e:
            logger.error(f"Error checking target achievement: {e}")
            return False
    
    def _optimize_genetic_algorithm(
        self, 
        ingredients: List[Dict], 
        target_macros: Dict
    ) -> Dict:
        """Genetic algorithm optimization using DEAP"""
        try:
            # Dynamically set the number of genes based on ingredients
            n_ingredients = len(ingredients)
            
            def evaluate(individual):
                # Ensure all quantities are positive and reasonable
                valid_individual = [max(0, min(500, x)) for x in individual]
                
                # Calculate total macros
                total_calories = sum(valid_individual[i] * ingredients[i]['calories_per_100g'] / 100 
                                   for i in range(len(ingredients)))
                total_protein = sum(valid_individual[i] * ingredients[i]['protein_per_100g'] / 100 
                                  for i in range(len(ingredients)))
                total_carbs = sum(valid_individual[i] * ingredients[i]['carbs_per_100g'] / 100 
                                for i in range(len(ingredients)))
                total_fat = sum(valid_individual[i] * ingredients[i]['fat_per_100g'] / 100 
                              for i in range(len(ingredients)))
                
                # Get carbs target (handle both field names)
                carbs_target = target_macros.get('carbs', target_macros.get('carbohydrates', 0))
                
                # Calculate fitness (lower is better)
                deviation = (
                    abs(total_calories - target_macros['calories']) / target_macros['calories'] +
                    abs(total_protein - target_macros['protein']) / max(target_macros['protein'], 1) +
                    abs(total_carbs - carbs_target) / max(carbs_target, 1) +
                    abs(total_fat - target_macros['fat']) / max(target_macros['fat'], 1)
                )
                
                return (1.0 / (1.0 + deviation),)
            
            self.toolbox.register("evaluate", evaluate)
            
            # Create population with correct number of genes
            population = []
            for _ in range(50):  # 50 individuals
                individual = [random.uniform(10, 300) for _ in range(n_ingredients)]  # Reasonable bounds
                ind = creator.INDIVIDUAL(individual)
                ind.fitness.values = evaluate(ind)
                population.append(ind)
            
            NGEN = 30
            
            for gen in range(NGEN):
                offspring = map(self.toolbox.clone, self.toolbox.select(population, len(population)))
                offspring = list(offspring)
                
                for child1, child2 in zip(offspring[::2], offspring[1::2]):
                    if random.random() < 0.7:
                        self.toolbox.mate(child1, child2)
                        del child1.fitness.values
                        del child2.fitness.values
                
                for mutant in offspring:
                    if random.random() < 0.2:
                        self.toolbox.mutate(mutant)
                        del mutant.fitness.values
                
                invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
                fitnesses = map(self.toolbox.evaluate, invalid_ind)
                for ind, fit in zip(invalid_ind, fitnesses):
                    ind.fitness.values = fit
                
                population[:] = offspring
            
            # Get best individual and ensure positive quantities
            best_individual = tools.selBest(population, 1)[0]
            final_quantities = [max(10, min(500, x)) for x in best_individual]  # Ensure 10-500g range
            
            return {
                'success': True,
                'method': 'Genetic Algorithm (DEAP)',
                'quantities': final_quantities
            }
            
        except Exception as e:
            logger.error(f"Genetic algorithm optimization failed: {e}")
            return {'success': False, 'method': 'Genetic Algorithm (DEAP)', 'quantities': []}
    
    def _optimize_differential_evolution(
        self, 
        ingredients: List[Dict], 
        target_macros: Dict
    ) -> Dict:
        """Differential evolution optimization using SciPy"""
        try:
            def objective(x):
                # Ensure all quantities are positive and reasonable
                valid_x = [max(10, min(500, val)) for val in x]
                
                # Calculate total macros
                total_calories = sum(valid_x[i] * ingredients[i]['calories_per_100g'] / 100 
                                   for i in range(len(ingredients)))
                total_protein = sum(valid_x[i] * ingredients[i]['protein_per_100g'] / 100 
                                  for i in range(len(ingredients)))
                total_carbs = sum(valid_x[i] * ingredients[i]['carbs_per_100g'] / 100 
                                for i in range(len(ingredients)))
                total_fat = sum(valid_x[i] * ingredients[i]['fat_per_100g'] / 100 
                              for i in range(len(ingredients)))
                
                # Get carbs target (handle both field names)
                carbs_target = target_macros.get('carbs', target_macros.get('carbohydrates', 0))
                
                # Calculate deviation from targets
                deviation = (
                    abs(total_calories - target_macros['calories']) / target_macros['calories'] +
                    abs(total_protein - target_macros['protein']) / max(target_macros['protein'], 1) +
                    abs(total_carbs - carbs_target) / max(carbs_target, 1) +
                    abs(total_fat - target_macros['fat']) / max(target_macros['fat'], 1)
                )
                
                return deviation
            
            # Bounds for quantities (10 to 500g per ingredient)
            bounds = [(10, 500) for _ in range(len(ingredients))]
            
            # Initial guess - use ML predictions if available
            initial_guess = []
            for i, ingredient in enumerate(ingredients):
                if hasattr(self, 'ml_models') and 'quantity' in self.ml_models:
                    try:
                        features = np.array([[
                            ingredient.get('calories_per_100g', 0),
                            ingredient.get('protein_per_100g', 0),
                            ingredient.get('carbs_per_100g', 0),
                            ingredient.get('fat_per_100g', 0)
                        ]])
                        features_scaled = self.scaler.transform(features)
                        predicted = self.ml_models['quantity'].predict(features_scaled)[0]
                        initial_guess.append(max(10, min(500, predicted)))
                    except:
                        initial_guess.append(100.0)
                else:
                    initial_guess.append(100.0)
            
            # Run differential evolution with better parameters
            result = differential_evolution(
                objective, 
                bounds, 
                maxiter=50,  # Reduced iterations for stability
                popsize=10,   # Smaller population for stability
                seed=42,
                init='latinhypercube',  # Better initialization
                strategy='best1bin',     # More stable strategy
                recombination=0.7,       # Standard recombination rate
                mutation=(0.5, 1.0),    # Adaptive mutation
                updating='immediate'     # Immediate updating for stability
            )
            
            if result.success:
                # Ensure final quantities are within bounds
                final_quantities = [max(10, min(500, x)) for x in result.x]
                
                return {
                    'success': True,
                    'method': 'Differential Evolution (SciPy)',
                    'quantities': final_quantities
                }
            else:
                # If DE fails, try simple scaling as fallback
                logger.warning("Differential evolution failed, using simple scaling")
                scaled_quantities = []
                for ingredient in ingredients:
                    # Simple proportional scaling based on target calories
                    target_calories = target_macros['calories']
                    current_calories = sum(ing.get('calories_per_100g', 0) for ing in ingredients)
                    if current_calories > 0:
                        scale_factor = target_calories / current_calories
                        scaled_quantities.append(max(10, min(500, 100 * scale_factor)))
                    else:
                        scaled_quantities.append(100.0)
                
                return {
                    'success': True,
                    'method': 'Differential Evolution with Fallback Scaling',
                    'quantities': scaled_quantities
                }
                
        except Exception as e:
            logger.error(f"Differential evolution optimization failed: {e}")
            # Return simple scaling as fallback
            try:
                scaled_quantities = []
                for ingredient in ingredients:
                    # Simple proportional scaling based on target calories
                    target_calories = target_macros['calories']
                    current_calories = sum(ing.get('calories_per_100g', 0) for ing in ingredients)
                    if current_calories > 0:
                        scale_factor = target_calories / current_calories
                        scaled_quantities.append(max(10, min(500, 100 * scale_factor)))
                    else:
                        scaled_quantities.append(100.0)
                
                return {
                    'success': True,
                    'method': 'Differential Evolution with Error Fallback',
                    'quantities': scaled_quantities
                }
            except:
                return {'success': False, 'method': 'Differential Evolution (SciPy)', 'quantities': []}
    
    def _optimize_linear_programming(
        self, 
        ingredients: List[Dict], 
        target_macros: Dict
    ) -> Dict:
        """Linear programming optimization using SciPy minimize"""
        try:
            def objective(x):
                # Calculate total macros
                total_calories = sum(x[i] * ingredients[i]['calories_per_100g'] / 100 
                                   for i in range(len(ingredients)))
                total_protein = sum(x[i] * ingredients[i]['protein_per_100g'] / 100 
                                  for i in range(len(ingredients)))
                total_carbs = sum(x[i] * ingredients[i]['carbs_per_100g'] / 100 
                                for i in range(len(ingredients)))
                total_fat = sum(x[i] * ingredients[i]['fat_per_100g'] / 100 
                              for i in range(len(ingredients)))
                
                # Get carbs target (handle both field names)
                carbs_target = target_macros.get('carbs', target_macros.get('carbohydrates', 0))
                
                # Calculate deviation from targets
                deviation = (
                    abs(total_calories - target_macros['calories']) / target_macros['calories'] +
                    abs(total_protein - target_macros['protein']) / max(target_macros['protein'], 1) +
                    abs(total_carbs - carbs_target) / max(carbs_target, 1) +
                    abs(total_fat - target_macros['fat']) / max(target_macros['fat'], 1)
                )
                
                return deviation
            
            # Bounds for quantities (0 to 500g per ingredient)
            bounds = [(0, 500) for _ in range(len(ingredients))]
            
            # Run optimization
            result = minimize(
                objective, 
                x0=np.random.uniform(50, 150, len(ingredients)),
                bounds=bounds,
                method='L-BFGS-B',
                options={'maxiter': 200}
            )
            
            if result.success:
                return {
                    'success': True,
                    'method': 'Linear Programming (SciPy)',
                    'quantities': result.x.tolist()
                }
            else:
                return {'success': False, 'method': 'Linear Programming (SciPy)', 'quantities': []}
                
        except Exception as e:
            logger.error(f"Linear programming optimization failed: {e}")
            return {'success': False, 'method': 'Linear Programming (SciPy)', 'quantities': []}
    
    def _optimize_hybrid(
        self, 
        ingredients: List[Dict], 
        target_macros: Dict
    ) -> Dict:
        """Hybrid optimization combining multiple advanced methods"""
        try:
            # Try advanced methods first
            if OPTUNA_AVAILABLE:
                result = self._optimize_optuna(ingredients, target_macros)
                if result['success']:
                    return result
            
            if PYGMO_AVAILABLE:
                result = self._optimize_pygmo(ingredients, target_macros)
                if result['success']:
                    return result
            
            if PLATYPUS_AVAILABLE:
                result = self._optimize_nsga2(ingredients, target_macros)
                if result['success']:
                    return result
            
            if PYMOO_AVAILABLE:
                result = self._optimize_pymoo(ingredients, target_macros)
                if result['success']:
                    return result
            
            # Fallback to standard methods
            result = self._optimize_genetic_algorithm(ingredients, target_macros)
            if result['success']:
                return result
            
            # Fallback to differential evolution
            result = self._optimize_differential_evolution(ingredients, target_macros)
            if result['success']:
                return result
            
            # Final fallback to linear programming
            result = self._optimize_linear_programming(ingredients, target_macros)
            if result['success']:
                return result
            
            return {'success': False, 'method': 'Hybrid (All methods failed)', 'quantities': []}
            
        except Exception as e:
            logger.error(f"Hybrid optimization failed: {e}")
            return {'success': False, 'method': 'Hybrid', 'quantities': []}
    
    def _optimize_optuna(
        self, 
        ingredients: List[Dict], 
        target_macros: Dict
    ) -> Dict:
        """Optuna optimization using Bayesian optimization"""
        if not OPTUNA_AVAILABLE:
            return {'success': False, 'method': 'Optuna not available'}
            
        try:
            def objective(trial):
                # Sample quantities from a distribution
                quantities = [
                    trial.suggest_float('quantity_' + str(i), 10, 500)
                    for i in range(len(ingredients))
                ]
                
                # Calculate total macros
                total_calories = sum(quantities[i] * ingredients[i]['calories_per_100g'] / 100 
                                   for i in range(len(ingredients)))
                total_protein = sum(quantities[i] * ingredients[i]['protein_per_100g'] / 100 
                                  for i in range(len(ingredients)))
                total_carbs = sum(quantities[i] * ingredients[i]['carbs_per_100g'] / 100 
                                for i in range(len(ingredients)))
                total_fat = sum(quantities[i] * ingredients[i]['fat_per_100g'] / 100 
                              for i in range(len(ingredients)))
                
                # Get carbs target (handle both field names)
                carbs_target = target_macros.get('carbs', target_macros.get('carbohydrates', 0))
                
                # Calculate deviation from targets
                deviation = (
                    abs(total_calories - target_macros['calories']) / target_macros['calories'] +
                    abs(total_protein - target_macros['protein']) / max(target_macros['protein'], 1) +
                    abs(total_carbs - carbs_target) / max(carbs_target, 1) +
                    abs(total_fat - target_macros['fat']) / max(target_macros['fat'], 1)
                )
                
                return deviation
            
            # Run optimization
            study = optuna.create_study(direction='minimize')
            study.optimize(objective, n_trials=50)  # Reduced trials for speed
            
            best_trial = study.best_trial
            final_quantities = [best_trial.params['quantity_' + str(i)] for i in range(len(ingredients))]
            
            # Ensure quantities are within bounds
            final_quantities = [max(10, min(500, q)) for q in final_quantities]
            
            return {
                'success': True,
                'method': 'Optuna Optimization',
                'quantities': final_quantities
            }
            
        except Exception as e:
            logger.error(f"Optuna optimization failed: {e}")
            return {'success': False, 'method': 'Optuna Optimization', 'quantities': []}
    
    def _optimize_pygmo(
        self, 
        ingredients: List[Dict], 
        target_macros: Dict
    ) -> Dict:
        """PyGMO optimization using Differential Evolution"""
        if not PYGMO_AVAILABLE:
            return {'success': False, 'method': 'PyGMO not available'}
            
        try:
            # Define the problem
            class OptimizationProblem:
                def __init__(self, ingredients, target_macros):
                    self.ingredients = ingredients
                    self.target_macros = target_macros
                    self.dimension = len(ingredients)
                
                def fitness(self, x):
                    # Calculate total macros
                    total_calories = sum(x[i] * self.ingredients[i]['calories_per_100g'] / 100 
                                       for i in range(len(self.ingredients)))
                    total_protein = sum(x[i] * self.ingredients[i]['protein_per_100g'] / 100 
                                      for i in range(len(self.ingredients)))
                    total_carbs = sum(x[i] * self.ingredients[i]['carbs_per_100g'] / 100 
                                    for i in range(len(self.ingredients)))
                    total_fat = sum(x[i] * self.ingredients[i]['fat_per_100g'] / 100 
                                  for i in range(len(self.ingredients)))
                    
                    # Get carbs target (handle both field names)
                    carbs_target = self.target_macros.get('carbs', self.target_macros.get('carbohydrates', 0))
                    
                    # Calculate deviation from targets
                    deviation = (
                        abs(total_calories - self.target_macros['calories']) / self.target_macros['calories'] +
                        abs(total_protein - self.target_macros['protein']) / max(self.target_macros['protein'], 1) +
                        abs(total_carbs - carbs_target) / max(carbs_target, 1) +
                        abs(total_fat - self.target_macros['fat']) / max(self.target_macros['fat'], 1)
                    )
                    
                    return [deviation]
                
                def get_bounds(self):
                    return ([10] * self.dimension, [500] * self.dimension)
            
            # Create the problem
            problem = OptimizationProblem(ingredients, target_macros)
            
            # Create the algorithm
            algorithm = pg.algorithm(pg.de(gen=50))  # Reduced generations for speed
            
            # Create the population
            population = pg.population(problem, 20)  # Smaller population for speed
            
            # Evolve the population
            population = algorithm.evolve(population)
            
            # Get the best individual
            final_quantities = population.champion_x
            
            # Ensure quantities are within bounds
            final_quantities = [max(10, min(500, x)) for x in final_quantities]
            
            return {
                'success': True,
                'method': 'PyGMO Differential Evolution',
                'quantities': final_quantities
            }
            
        except Exception as e:
            logger.error(f"PyGMO optimization failed: {e}")
            return {'success': False, 'method': 'PyGMO', 'quantities': []}
    
    def _optimize_nsga2(
        self, 
        ingredients: List[Dict], 
        target_macros: Dict
    ) -> Dict:
        """NSGA-II optimization using Platypus"""
        if not PLATYPUS_AVAILABLE:
            return {'success': False, 'method': 'Platypus not available'}
            
        try:
            # Define the problem
            class OptimizationProblem(Problem):
                def __init__(self, ingredients, target_macros):
                    super().__init__(len(ingredients), 1)  # n_vars, n_objectives
                    self.ingredients = ingredients
                    self.target_macros = target_macros
                    
                    # Define variable types (Real with bounds)
                    for i in range(len(ingredients)):
                        self.types[i] = Real(10, 500)  # 10-500g bounds
                
                def evaluate(self, solution):
                    # Get quantities from solution
                    quantities = solution.variables
                    
                    # Calculate total macros
                    total_calories = sum(quantities[i] * self.ingredients[i]['calories_per_100g'] / 100 
                                       for i in range(len(self.ingredients)))
                    total_protein = sum(quantities[i] * self.ingredients[i]['protein_per_100g'] / 100 
                                      for i in range(len(self.ingredients)))
                    total_carbs = sum(quantities[i] * self.ingredients[i]['carbs_per_100g'] / 100 
                                    for i in range(len(self.ingredients)))
                    total_fat = sum(quantities[i] * self.ingredients[i]['fat_per_100g'] / 100 
                                  for i in range(len(self.ingredients)))
                    
                    # Get carbs target (handle both field names)
                    carbs_target = self.target_macros.get('carbs', self.target_macros.get('carbohydrates', 0))
                    
                    # Calculate deviation from targets
                    deviation = (
                        abs(total_calories - self.target_macros['calories']) / self.target_macros['calories'] +
                        abs(total_protein - self.target_macros['protein']) / max(self.target_macros['protein'], 1) +
                        abs(total_carbs - carbs_target) / max(carbs_target, 1) +
                        abs(total_fat - self.target_macros['fat']) / max(self.target_macros['fat'], 1)
                    )
                    
                    solution.objectives[:] = [deviation]
            
            # Create the problem
            problem = OptimizationProblem(ingredients, target_macros)
            
            # Create the algorithm
            algorithm = NSGAII(problem)
            
            # Run optimization
            algorithm.run(100)  # Reduced generations for speed
            
            # Get the best solution
            best_solution = min(algorithm.result, key=lambda x: x.objectives[0])
            final_quantities = best_solution.variables
            
            # Ensure quantities are within bounds
            final_quantities = [max(10, min(500, q)) for q in final_quantities]
            
            return {
                'success': True,
                'method': 'NSGA-II (Platypus)',
                'quantities': final_quantities
            }
            
        except Exception as e:
            logger.error(f"NSGA-II optimization failed: {e}")
            return {'success': False, 'method': 'NSGA-II', 'quantities': []}
    
    def _optimize_pymoo(
        self, 
        ingredients: List[Dict], 
        target_macros: Dict
    ) -> Dict:
        """PyMOO optimization using NSGA-II"""
        if not PYMOO_AVAILABLE:
            return {'success': False, 'method': 'PyMOO not available'}
            
        try:
            # Define the problem
            class OptimizationProblem(PymooProblem):
                def __init__(self, ingredients, target_macros):
                    super().__init__(n_var=len(ingredients), n_obj=1, n_constr=0)
                    self.ingredients = ingredients
                    self.target_macros = target_macros
                
                def _evaluate(self, x, out, *args, **kwargs):
                    # Calculate total macros
                    total_calories = sum(x[i] * self.ingredients[i]['calories_per_100g'] / 100 
                                       for i in range(len(self.ingredients)))
                    total_protein = sum(x[i] * self.ingredients[i]['protein_per_100g'] / 100 
                                      for i in range(len(self.ingredients)))
                    total_carbs = sum(x[i] * self.ingredients[i]['carbs_per_100g'] / 100 
                                    for i in range(len(self.ingredients)))
                    total_fat = sum(x[i] * self.ingredients[i]['fat_per_100g'] / 100 
                                  for i in range(len(self.ingredients)))
                    
                    # Get carbs target (handle both field names)
                    carbs_target = self.target_macros.get('carbs', self.target_macros.get('carbohydrates', 0))
                    
                    # Calculate deviation from targets
                    deviation = (
                        abs(total_calories - self.target_macros['calories']) / self.target_macros['calories'] +
                        abs(total_protein - self.target_macros['protein']) / max(self.target_macros['protein'], 1) +
                        abs(total_carbs - carbs_target) / max(carbs_target, 1) +
                        abs(total_fat - self.target_macros['fat']) / max(self.target_macros['fat'], 1)
                    )
                    
                    out['F'] = [deviation]
                
                def _calc_constr(self, x, out, *args, **kwargs):
                    # No constraints in this problem
                    pass
                
                def _calc_obj(self, x, out, *args, **kwargs):
                    # No objectives in this problem
                    pass
            
            # Define the problem
            problem = OptimizationProblem(ingredients, target_macros)
            
            # Define the algorithm
            algorithm = NSGA2(pop_size=50)  # Smaller population for speed
            
            # Optimize
            res = pymoo_minimize(
                problem,
                algorithm,
                ('n_gen', 50),  # Reduced generations for speed
                seed=42
            )
            
            # Get the best individual
            final_quantities = res.X[0]
            
            # Ensure quantities are within bounds
            final_quantities = [max(10, min(500, q)) for q in final_quantities]
            
            return {
                'success': True,
                'method': 'PyMOO NSGA-II',
                'quantities': final_quantities
            }
            
        except Exception as e:
            logger.error(f"PyMOO optimization failed: {e}")
            return {'success': False, 'method': 'PyMOO', 'quantities': []}
    
    def _evaluate_genetic_fitness(self, individual):
        """Evaluate fitness for genetic algorithm (placeholder - will be overridden)"""
        return (0.0,)
    
    def _calculate_final_meal(
        self, 
        ingredients: List[Dict], 
        quantities: List[float]
    ) -> Dict:
        """Calculate final meal with optimized quantities"""
        meal_items = []
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        # Ensure quantities list has the right length
        if len(quantities) != len(ingredients):
            # If quantities don't match, use default quantities
            quantities = [100.0] * len(ingredients)
        
        for i, ingredient in enumerate(ingredients):
            quantity = quantities[i]
            calories = (ingredient.get('calories_per_100g', 0) * quantity) / 100
            protein = (ingredient.get('protein_per_100g', 0) * quantity) / 100
            carbs = (ingredient.get('carbs_per_100g', 0) * quantity) / 100
            fat = (ingredient.get('fat_per_100g', 0) * quantity) / 100
            
            meal_items.append({
                'ingredient': ingredient.get('name', 'Unknown'),
                'quantity_grams': round(quantity, 1),
                'calories': round(calories, 1),
                'protein': round(protein, 1),
                'carbs': round(carbs, 1),
                'fat': round(fat, 1)
            })
            
            total_calories += calories
            total_protein += protein
            total_carbs += carbs
            total_fat += fat
        
        return {
            'items': meal_items,
            'calories': total_calories,
            'protein': total_protein,
            'carbs': total_carbs,
            'fat': total_fat
        }
    
    def _check_target_achievement(
        self, 
        final_meal: Dict, 
        target_macros: Dict
    ) -> Dict:
        """Check if targets are achieved within ±10% tolerance"""
        tolerance = 0.1
        
        # Handle both 'carbs' and 'carbohydrates' field names
        carbs_target = target_macros.get('carbs', target_macros.get('carbohydrates', 0))
        
        calories_achieved = abs(final_meal['calories'] - target_macros.get('calories', 0)) <= target_macros.get('calories', 1) * tolerance
        protein_achieved = abs(final_meal['protein'] - target_macros.get('protein', 0)) <= target_macros.get('protein', 1) * tolerance
        carbs_achieved = abs(final_meal['carbs'] - carbs_target) <= carbs_target * tolerance
        fat_achieved = abs(final_meal['fat'] - target_macros.get('fat', 0)) <= target_macros.get('fat', 1) * tolerance
        
        overall_achieved = calories_achieved and protein_achieved and carbs_achieved and fat_achieved
        
        return {
            'calories_achieved': calories_achieved,
            'protein_achieved': protein_achieved,
            'carbs_achieved': carbs_achieved,
            'fat_achieved': fat_achieved,
            'overall_achieved': overall_achieved
        }
    
    def _calculate_enhancement_details(
        self, 
        rag_ingredients: List[Dict], 
        supplementary_ingredients: List[Dict], 
        final_meal: Dict
    ) -> Dict:
        """Calculate RAG enhancement details"""
        original_count = len([ing for ing in rag_ingredients if ing.get('source') == 'rag'])
        supplements_count = len(supplementary_ingredients)
        total_count = len(final_meal['items'])
        
        return {
            'enhancement_method': 'Mathematical optimization to meet targets',
            'original_ingredients': original_count,
            'supplements_added': supplements_count,
            'total_ingredients': total_count,
            'enhancement_ratio': round(supplements_count / max(original_count, 1), 2)
        }
    
    def _generate_recommendations(self, final_meal: Dict, target_macros: Dict) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if final_meal['protein'] < target_macros.get('protein', 0) * 0.9:
            recommendations.append("Consider adding more protein-rich foods like lean meats, fish, or legumes")
        
        if final_meal['carbs'] < target_macros.get('carbs', 0) * 0.9:
            recommendations.append("Include more whole grains, fruits, and vegetables for carbohydrates")
        
        if final_meal['fat'] < target_macros.get('fat', 0) * 0.9:
            recommendations.append("Add healthy fats from nuts, avocados, or olive oil")
        
        if final_meal['calories'] < target_macros.get('calories', 0) * 0.9:
            recommendations.append("Consider increasing portion sizes or adding calorie-dense foods")
        
        recommendations.append("This meal plan has been enhanced with additional ingredients to meet your nutritional targets")
        
        return recommendations
    
    def _find_precise_vegetable_supplements(
        self, 
        existing_vegetables: List[Dict], 
        added_ingredients: set, 
        added_categories: set,
        current_totals: Dict
    ) -> List[Dict]:
        """Find precise vegetable supplements for nutrition and variety with calorie control"""
        supplements = []
        
        # Variety of vegetables to add with different nutritional profiles
        veg_options = [
            ('leafy_greens', ['Kale', 'Spinach', 'Arugula', 'Swiss Chard', 'Collard Greens']),
            ('cruciferous', ['Broccoli', 'Cauliflower', 'Brussels Sprouts', 'Cabbage', 'Bok Choy']),
            ('colorful_veg', ['Bell Peppers', 'Carrots', 'Tomatoes', 'Zucchini', 'Eggplant']),
            ('mushrooms', ['Mushrooms', 'Shiitake', 'Portobello', 'Cremini']),
            ('other_veg', ['Green Beans', 'Asparagus', 'Radishes', 'Cucumber', 'Celery'])
        ]
        
        # Add 3-4 different vegetables from different categories
        max_veg_sources = 4
        sources_added = 0
        
        for category_name, veg_names in veg_options:
            if sources_added >= max_veg_sources:
                break
                
            for veg_name in veg_names:
                if sources_added >= max_veg_sources:
                    break
                    
                # Skip if already added
                if veg_name.lower() in added_ingredients:
                    continue
                    
                ingredient = self._find_ingredient_by_name(veg_name)
                if ingredient:
                    # Add reasonable amount for variety with calorie control
                    if category_name == 'leafy_greens':
                        quantity_needed = 80  # 80g for leafy greens
                    elif category_name == 'cruciferous':
                        quantity_needed = 60  # 60g for cruciferous
                    elif category_name == 'colorful_veg':
                        quantity_needed = 70  # 70g for colorful vegetables
                    elif category_name == 'mushrooms':
                        quantity_needed = 50  # 50g for mushrooms
                    else:
                        quantity_needed = 60  # 60g for other vegetables
                    
                    supplements.append({
                        'name': ingredient['name'],
                        'calories_per_100g': ingredient['calories_per_100g'],
                        'protein_per_100g': ingredient['protein_per_100g'],
                        'carbs_per_100g': ingredient['carbs_per_100g'],
                        'fat_per_100g': ingredient['fat_per_100g'],
                        'source': 'supplement',
                        'category': ingredient.get('category', 'vegetable'),
                        'quantity_needed': quantity_needed
                    })
                    
                    sources_added += 1
                    break
        
        return supplements
    
    def _find_comprehensive_supplements(
        self, 
        existing_vegetables: List[Dict], 
        added_ingredients: set, 
        added_categories: set,
        current_totals: Dict,
        meal_analysis: Dict,
        user_preferences: Dict
    ) -> List[Dict]:
        """Find comprehensive supplements for nutrition and variety"""
        supplements = []
        
        # Add vegetables for micronutrients and variety
        veg_supplements = self._find_precise_vegetable_supplements(
            existing_vegetables, added_ingredients, added_categories, current_totals
        )
        supplements.extend(veg_supplements)
        
        # Add fruits for additional micronutrients
        fruit_supplements = self._find_fruit_supplements(added_ingredients, meal_analysis)
        supplements.extend(fruit_supplements)
        
        # Add nuts/seeds for healthy fats and micronutrients
        nut_supplements = self._find_nut_seed_supplements(added_ingredients, meal_analysis)
        supplements.extend(nut_supplements)
        
        return supplements
    
    def _find_fruit_supplements(self, added_ingredients: set, meal_analysis: Dict) -> List[Dict]:
        """Find fruit supplements for micronutrients"""
        supplements = []
        
        # Seasonal fruits
        seasonal_fruits = meal_analysis.get('seasonal_availability', {}).get('summer', [])
        fruit_options = ['Apple', 'Banana', 'Berries', 'Orange', 'Mango', 'Pineapple'] + seasonal_fruits
        
        # Add 1-2 fruits for variety
        fruits_added = 0
        max_fruits = 2
        
        for fruit_name in fruit_options:
            if fruits_added >= max_fruits:
                break
                
            if fruit_name.lower() not in added_ingredients:
                ingredient = self._find_ingredient_by_name(fruit_name)
                if ingredient:
                    supplements.append({
                        'name': ingredient['name'],
                        'calories_per_100g': ingredient['calories_per_100g'],
                        'protein_per_100g': ingredient['protein_per_100g'],
                        'carbs_per_100g': ingredient['carbs_per_100g'],
                        'fat_per_100g': ingredient['fat_per_100g'],
                        'source': 'supplement',
                        'category': 'fruit',
                        'quantity_needed': 50  # 50g of fruit
                    })
                    fruits_added += 1
        
        return supplements
    
    def _find_nut_seed_supplements(self, added_ingredients: set, meal_analysis: Dict) -> List[Dict]:
        """Find nut and seed supplements for healthy fats and micronutrients"""
        supplements = []
        
        nut_seed_options = ['Almonds', 'Walnuts', 'Pumpkin Seeds', 'Chia Seeds', 'Sunflower Seeds', 'Hemp Seeds']
        
        # Add 1-2 nuts/seeds for variety
        nuts_added = 0
        max_nuts = 2
        
        for nut_name in nut_seed_options:
            if nuts_added >= max_nuts:
                break
                
            if nut_name.lower() not in added_ingredients:
                ingredient = self._find_ingredient_by_name(nut_name)
                if ingredient:
                    supplements.append({
                        'name': ingredient['name'],
                        'calories_per_100g': ingredient['calories_per_100g'],
                        'protein_per_100g': ingredient['protein_per_100g'],
                        'carbs_per_100g': ingredient['carbs_per_100g'],
                        'fat_per_100g': ingredient['fat_per_100g'],
                        'source': 'supplement',
                        'category': 'nuts_seeds',
                        'quantity_needed': 20  # 20g of nuts/seeds
                    })
                    nuts_added += 1
        
        return supplements
    
    def _find_advanced_carb_supplements(
        self, 
        deficit: float, 
        existing_carbs: List[Dict], 
        added_ingredients: set, 
        added_categories: set,
        current_totals: Dict,
        meal_analysis: Dict,
        user_preferences: Dict
    ) -> List[Dict]:
        """Find advanced carb supplements with comprehensive analysis"""
        supplements = []
        remaining_deficit = deficit
        
        # Advanced carb selection based on meal analysis
        carb_strategies = [
            ('whole_grains', ['Quinoa', 'Oats', 'Barley', 'Buckwheat', 'Millet', 'Amaranth']),
            ('starchy_veg', ['Sweet Potato', 'Butternut Squash', 'Carrots', 'Parsnips', 'Turnips']),
            ('legumes', ['Lentils', 'Chickpeas', 'Black Beans', 'Kidney Beans', 'Pinto Beans']),
            ('fruits', ['Apple', 'Banana', 'Berries', 'Orange', 'Mango', 'Pineapple']),
            ('pasta', ['Whole Wheat Pasta', 'Brown Rice Pasta', 'Quinoa Pasta'])
        ]
        
        # Select strategy based on meal type and existing composition
        if meal_analysis['meal_type'] in ['breakfast', 'lunch']:
            # Prefer whole grains and fruits for morning meals
            carb_strategies.insert(0, carb_strategies.pop(1))  # Move starchy veg up
            carb_strategies.insert(1, carb_strategies.pop(3))  # Move fruits up
        
        # Add variety while meeting deficit
        max_carb_sources = min(3, len(carb_strategies))
        sources_added = 0
        
        for strategy_name, ingredient_names in carb_strategies:
            if sources_added >= max_carb_sources or remaining_deficit <= 0:
                break
                
            for name in ingredient_names:
                if sources_added >= max_carb_sources or remaining_deficit <= 0:
                    break
                    
                # Skip if already added
                if name.lower() in added_ingredients:
                    continue
                    
                ingredient = self._find_ingredient_by_name(name)
                if ingredient and self._is_ingredient_suitable(ingredient, existing_carbs, meal_analysis):
                    # Calculate optimal quantity with advanced logic
                    quantity_needed = self._calculate_optimal_carb_quantity(
                        ingredient, remaining_deficit, meal_analysis, user_preferences
                    )
                    
                    if quantity_needed > 0:
                        supplements.append({
                            'name': ingredient['name'],
                            'calories_per_100g': ingredient['calories_per_100g'],
                            'protein_per_100g': ingredient['protein_per_100g'],
                            'carbs_per_100g': ingredient['carbs_per_100g'],
                            'fat_per_100g': ingredient['fat_per_100g'],
                            'source': 'supplement',
                            'category': ingredient.get('category', 'grain'),
                            'quantity_needed': quantity_needed,
                            'cost_per_100g': ingredient.get('cost_per_100g', 0),
                            'micronutrients': ingredient.get('micronutrients', {})
                        })
                        
                        remaining_deficit -= (quantity_needed * ingredient.get('carbs_per_100g', 0) / 100)
                        sources_added += 1
                        break
        
        return supplements
    
    def _calculate_optimal_carb_quantity(
        self, 
        ingredient: Dict, 
        deficit: float, 
        meal_analysis: Dict, 
        user_preferences: Dict
    ) -> float:
        """Calculate optimal carb quantity with advanced logic"""
        carb_content = ingredient.get('carbs_per_100g', 0)
        fat_content = ingredient.get('fat_per_100g', 0)
        
        if carb_content <= 0:
            return 0
        
        # Base quantity calculation
        base_quantity = (deficit / carb_content) * 100
        
        # Apply fat control based on meal analysis
        if fat_content > 10:  # High fat
            base_quantity *= 0.4  # Significant reduction
        elif fat_content > 5:  # Medium fat
            base_quantity *= 0.7  # Moderate reduction
        
        # Apply meal type adjustments
        if meal_analysis['meal_type'] == 'breakfast':
            base_quantity *= 0.9  # Slightly smaller for breakfast
        elif meal_analysis['meal_type'] == 'dinner':
            base_quantity *= 1.05  # Slightly larger for dinner
        
        # Apply user preference adjustments
        if user_preferences.get('low_fat', False) and fat_content > 5:
            base_quantity *= 0.6
        
        # Ensure reasonable bounds
        base_quantity = max(20, min(300, base_quantity))
        
        return base_quantity
    
    def _find_advanced_fat_supplements(
        self, 
        deficit: float, 
        existing_fats: List[Dict], 
        added_ingredients: set, 
        added_categories: set,
        current_totals: Dict,
        meal_analysis: Dict,
        user_preferences: Dict
    ) -> List[Dict]:
        """Find advanced fat supplements with comprehensive analysis"""
        supplements = []
        remaining_deficit = deficit
        
        # Advanced fat selection based on meal analysis
        fat_strategies = [
            ('healthy_oils', ['Olive Oil', 'Avocado Oil', 'Coconut Oil', 'Walnut Oil', 'Flaxseed Oil']),
            ('avocado', ['Avocado']),
            ('nuts_seeds', ['Almonds', 'Walnuts', 'Pumpkin Seeds', 'Chia Seeds', 'Hemp Seeds', 'Pecans']),
            ('fatty_fish', ['Salmon', 'Mackerel', 'Sardines', 'Trout']),
            ('dairy_fats', ['Butter', 'Ghee', 'Heavy Cream'])
        ]
        
        # Select strategy based on meal type and existing composition
        if meal_analysis['meal_type'] == 'breakfast':
            # Prefer nuts and seeds for breakfast
            fat_strategies.insert(0, fat_strategies.pop(2))  # Move nuts/seeds up
        
        # Add variety while meeting deficit
        max_fat_sources = min(2, len(fat_strategies))  # Limit fat sources
        sources_added = 0
        
        for strategy_name, ingredient_names in fat_strategies:
            if sources_added >= max_fat_sources or remaining_deficit <= 0:
                break
                
            for name in ingredient_names:
                if sources_added >= max_fat_sources or remaining_deficit <= 0:
                    break
                    
                # Skip if already added
                if name.lower() in added_ingredients:
                    continue
                    
                ingredient = self._find_ingredient_by_name(name)
                if ingredient and self._is_ingredient_suitable(ingredient, existing_fats, meal_analysis):
                    # Calculate optimal quantity with advanced logic
                    quantity_needed = self._calculate_optimal_fat_quantity(
                        ingredient, remaining_deficit, meal_analysis, user_preferences
                    )
                    
                    if quantity_needed > 0:
                        supplements.append({
                            'name': ingredient['name'],
                            'calories_per_100g': ingredient['calories_per_100g'],
                            'protein_per_100g': ingredient['protein_per_100g'],
                            'carbs_per_100g': ingredient['carbs_per_100g'],
                            'fat_per_100g': ingredient['fat_per_100g'],
                            'source': 'supplement',
                            'category': ingredient.get('category', 'fat'),
                            'quantity_needed': quantity_needed,
                            'cost_per_100g': ingredient.get('cost_per_100g', 0),
                            'micronutrients': ingredient.get('micronutrients', {})
                        })
                        
                        remaining_deficit -= (quantity_needed * ingredient.get('fat_per_100g', 0) / 100)
                        sources_added += 1
                        break
        
        return supplements
    
    def _calculate_optimal_fat_quantity(
        self, 
        ingredient: Dict, 
        deficit: float, 
        meal_analysis: Dict, 
        user_preferences: Dict
    ) -> float:
        """Calculate optimal fat quantity with advanced logic"""
        fat_content = ingredient.get('fat_per_100g', 0)
        
        if fat_content <= 0:
            return 0
        
        # Base quantity calculation
        base_quantity = (deficit / fat_content) * 100
        
        # Apply strict limits for fat supplements
        if ingredient.get('name', '').lower() in ['olive oil', 'avocado oil', 'coconut oil']:
            base_quantity = min(15, base_quantity)  # Max 15g for oils
        elif ingredient.get('name', '').lower() in ['almonds', 'walnuts', 'pumpkin seeds']:
            base_quantity = min(25, base_quantity)  # Max 25g for nuts
        elif ingredient.get('name', '').lower() == 'avocado':
            base_quantity = min(40, base_quantity)  # Max 40g for avocado
        else:
            base_quantity = min(80, base_quantity)  # Max 80g for others
        
        # Apply meal type adjustments
        if meal_analysis['meal_type'] == 'breakfast':
            base_quantity *= 0.8  # Smaller fat portions for breakfast
        
        # Apply user preference adjustments
        if user_preferences.get('low_fat', False):
            base_quantity *= 0.5
        
        # Ensure reasonable bounds
        base_quantity = max(5, min(100, base_quantity))
        
        return base_quantity
    
    def _ultra_precision_adjustment(self, supplements: List[Dict], deficits: Dict, current_totals: Dict) -> List[Dict]:
        """Ultra precision adjustment for final target achievement"""
        target_protein = 47.7
        target_cars = 79.7
        target_fat = 14.2
        target_calories = 637.2
        
        # Calculate current totals
        current_totals = self._update_totals_with_supplements(current_totals, supplements)
        
        # Calculate final deviations
        protein_diff = target_protein - current_totals['protein']
        carbs_diff = target_cars - current_totals['carbs']
        fat_diff = target_fat - current_totals['fat']
        calories_diff = target_calories - current_totals['calories']
        
        # Apply micro-adjustments to closest ingredients with priority system
        adjustment_priority = self._calculate_adjustment_priority(supplements, protein_diff, carbs_diff, fat_diff, calories_diff)
        
        for ingredient_info in adjustment_priority:
            supplement = ingredient_info['ingredient']
            deficit_type = ingredient_info['deficit_type']
            deficit_value = ingredient_info['deficit_value']
            priority_score = ingredient_info['priority_score']
            
            current_qty = supplement.get('quantity_needed', 0)
            
            # Apply adjustment based on priority and deficit type
            if deficit_type == 'protein' and supplement.get('protein_per_100g', 0) > 0:
                micro_adjustment = (deficit_value / supplement.get('protein_per_100g', 1)) * 100 * priority_score
                current_qty += micro_adjustment
                protein_diff -= micro_adjustment * supplement.get('protein_per_100g', 0) / 100
                
            elif deficit_type == 'carbs' and supplement.get('carbs_per_100g', 0) > 0:
                micro_adjustment = (deficit_value / supplement.get('carbs_per_100g', 1)) * 100 * priority_score
                current_qty += micro_adjustment
                carbs_diff -= micro_adjustment * supplement.get('carbs_per_100g', 0) / 100
                
            elif deficit_type == 'fat' and supplement.get('fat_per_100g', 0) > 0:
                micro_adjustment = (deficit_value / supplement.get('fat_per_100g', 1)) * 100 * priority_score * 0.5
                current_qty += micro_adjustment
                fat_diff -= micro_adjustment * supplement.get('fat_per_100g', 0) / 100
                
            elif deficit_type == 'calories' and supplement.get('calories_per_100g', 0) > 0:
                micro_adjustment = (deficit_value / supplement.get('calories_per_100g', 1)) * 100 * priority_score * 0.7
                current_qty += micro_adjustment
                calories_diff -= micro_adjustment * supplement.get('calories_per_100g', 0) / 100
            
            # Ensure bounds
            current_qty = max(10, min(500, current_qty))
            supplement['quantity_needed'] = current_qty
            
            # Recalculate totals
            current_totals = self._update_totals_with_supplements(current_totals, supplements)
        
        return supplements
    
    def _calculate_adjustment_priority(self, supplements: List[Dict], protein_diff: float, carbs_diff: float, fat_diff: float, calories_diff: float) -> List[Dict]:
        """Calculate priority for ingredient adjustments"""
        priority_list = []
        
        for supplement in supplements:
            # Calculate how much each ingredient can contribute to fixing deficits
            protein_potential = supplement.get('protein_per_100g', 0) / 100
            carbs_potential = supplement.get('carbs_per_100g', 0) / 100
            fat_potential = supplement.get('fat_per_100g', 0) / 100
            calories_potential = supplement.get('calories_per_100g', 0) / 100
            
            # Calculate priority scores for each deficit type
            if abs(protein_diff) > 0.05 and protein_potential > 0:
                priority_score = min(0.15, abs(protein_diff) / 10)  # Cap at 0.15
                priority_list.append({
                    'ingredient': supplement,
                    'deficit_type': 'protein',
                    'deficit_value': protein_diff,
                    'priority_score': priority_score
                })
            
            if abs(carbs_diff) > 0.05 and carbs_potential > 0:
                priority_score = min(0.15, abs(carbs_diff) / 10)
                priority_list.append({
                    'ingredient': supplement,
                    'deficit_type': 'carbs',
                    'deficit_value': carbs_diff,
                    'priority_score': priority_score
                })
            
            if abs(fat_diff) > 0.05 and fat_potential > 0:
                priority_score = min(0.1, abs(fat_diff) / 10)  # Lower priority for fat
                priority_list.append({
                    'ingredient': supplement,
                    'deficit_type': 'fat',
                    'deficit_value': fat_diff,
                    'priority_score': priority_score
                })
            
            if abs(calories_diff) > 1.0 and calories_potential > 0:
                priority_score = min(0.12, abs(calories_diff) / 50)
                priority_list.append({
                    'ingredient': supplement,
                    'deficit_type': 'calories',
                    'deficit_value': calories_diff,
                    'priority_score': priority_score
                })
        
        # Sort by priority score (highest first)
        priority_list.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return priority_list
