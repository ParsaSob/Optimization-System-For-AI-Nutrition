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
        self.optimization_methods = {
            'genetic_algorithm': self._optimize_genetic_algorithm,
            'differential_evolution': self._optimize_differential_evolution,
            'linear_programming': self._optimize_linear_programming,
            'hybrid': self._optimize_hybrid
        }
        self._setup_genetic_algorithm()
        
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
        self.toolbox.register("individual", tools.initRepeat, creator.INDIVIDUAL, 
                            self.toolbox.attr_float, n=50)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self._evaluate_genetic_fitness)
        self.toolbox.register("mate", tools.cxBlend, alpha=0.5)
        self.toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=20, indpb=0.1)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
    
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
                deficits, user_preferences, meal_type
            )
            
            # Combine RAG and supplementary ingredients
            all_ingredients = rag_ingredients + supplementary_ingredients
            
            # Ensure we have at least one ingredient
            if not all_ingredients:
                raise ValueError("No ingredients available for optimization")
            
            # Optimize quantities using mathematical optimization
            optimization_result = self._optimize_quantities(
                all_ingredients, target_macros, user_preferences
            )
            
            if not optimization_result['success']:
                # Fallback to simpler scaling
                optimization_result = self._fallback_scaling(
                    all_ingredients, target_macros
                )
            
            # Ensure we have quantities for all ingredients
            quantities = optimization_result.get('quantities', [])
            if len(quantities) != len(all_ingredients):
                # If quantities don't match, use fallback scaling
                optimization_result = self._fallback_scaling(
                    all_ingredients, target_macros
                )
                quantities = optimization_result.get('quantities', [])
            
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
                
                ingredients.append({
                    'name': ingredient['name'],
                    'calories_per_100g': (ingredient['calories'] / amount) * 100,
                    'protein_per_100g': (ingredient['protein'] / amount) * 100,
                    'carbs_per_100g': (ingredient['carbs'] / amount) * 100,
                    'fat_per_100g': (ingredient['fat'] / amount) * 100,
                    'original_amount': amount,
                    'source': 'rag'
                })
        
        return ingredients
    
    def _calculate_current_totals(self, ingredients: List[Dict]) -> Dict:
        """Calculate current nutritional totals from RAG ingredients"""
        totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
        
        for ingredient in ingredients:
            amount = ingredient.get('original_amount', 100)
            totals['calories'] += (ingredient.get('calories_per_100g', 0) * amount) / 100
            totals['protein'] += (ingredient.get('protein_per_100g', 0) * amount) / 100
            totals['carbs'] += (ingredient.get('carbs_per_100g', 0) * amount) / 100
            totals['fat'] += (ingredient.get('fat_per_100g', 0) * amount) / 100
        
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
    
    def _find_supplementary_ingredients(
        self, 
        deficits: Dict, 
        user_preferences: Dict, 
        meal_type: str
    ) -> List[Dict]:
        """Find supplementary ingredients to fill macro gaps"""
        supplementary = []
        
        # Filter database ingredients based on preferences
        available_ingredients = self._filter_ingredients_by_preferences(
            self.ingredients_db, user_preferences
        )
        
        # Add ingredients to fill specific macro gaps
        if deficits['protein'] > 0:
            protein_sources = [ing for ing in available_ingredients 
                             if ing.get('protein_per_100g', 0) > 15]
            if protein_sources:
                supplementary.append({
                    'name': protein_sources[0]['name'],
                    'calories_per_100g': protein_sources[0]['calories_per_100g'],
                    'protein_per_100g': protein_sources[0]['protein_per_100g'],
                    'carbs_per_100g': protein_sources[0]['carbs_per_100g'],
                    'fat_per_100g': protein_sources[0]['fat_per_100g'],
                    'source': 'supplement'
                })
        
        if deficits['carbs'] > 0:
            carb_sources = [ing for ing in available_ingredients 
                           if ing.get('carbs_per_100g', 0) > 20]
            if carb_sources:
                supplementary.append({
                    'name': carb_sources[0]['name'],
                    'calories_per_100g': carb_sources[0]['calories_per_100g'],
                    'protein_per_100g': carb_sources[0]['protein_per_100g'],
                    'carbs_per_100g': carb_sources[0]['carbs_per_100g'],
                    'fat_per_100g': carb_sources[0]['fat_per_100g'],
                    'source': 'supplement'
                })
        
        if deficits['fat'] > 0:
            fat_sources = [ing for ing in available_ingredients 
                          if ing.get('fat_per_100g', 0) > 10]
            if fat_sources:
                supplementary.append({
                    'name': fat_sources[0]['name'],
                    'calories_per_100g': fat_sources[0]['calories_per_100g'],
                    'protein_per_100g': fat_sources[0]['protein_per_100g'],
                    'carbs_per_100g': fat_sources[0]['carbs_per_100g'],
                    'fat_per_100g': fat_sources[0]['fat_per_100g'],
                    'source': 'supplement'
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
        
        # Try different optimization methods
        for method_name, method_func in self.optimization_methods.items():
            try:
                result = method_func(ingredients, target_macros)
                if result['success']:
                    return result
            except Exception as e:
                logger.warning(f"Method {method_name} failed: {e}")
                continue
        
        # If all methods fail, return failure
        return {'success': False, 'method': 'All methods failed', 'quantities': []}
    
    def _optimize_genetic_algorithm(
        self, 
        ingredients: List[Dict], 
        target_macros: Dict
    ) -> Dict:
        """Genetic algorithm optimization using DEAP"""
        try:
            def evaluate(individual):
                # Calculate total macros
                total_calories = sum(individual[i] * ingredients[i]['calories_per_100g'] / 100 
                                   for i in range(len(ingredients)))
                total_protein = sum(individual[i] * ingredients[i]['protein_per_100g'] / 100 
                                  for i in range(len(ingredients)))
                total_carbs = sum(individual[i] * ingredients[i]['carbs_per_100g'] / 100 
                                for i in range(len(ingredients)))
                total_fat = sum(individual[i] * ingredients[i]['fat_per_100g'] / 100 
                              for i in range(len(ingredients)))
                
                # Calculate fitness (lower is better)
                deviation = (
                    abs(total_calories - target_macros['calories']) / target_macros['calories'] +
                    abs(total_protein - target_macros['protein']) / max(target_macros['protein'], 1) +
                    abs(total_carbs - target_macros['carbs']) / max(target_macros['carbs'], 1) +
                    abs(total_fat - target_macros['fat']) / max(target_macros['fat'], 1)
                )
                
                return (1.0 / (1.0 + deviation),)
            
            self.toolbox.register("evaluate", evaluate)
            
            # Create population and evolve
            population = self.toolbox.population(n=50)
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
            
            # Get best individual
            best_individual = tools.selBest(population, 1)[0]
            
            return {
                'success': True,
                'method': 'Genetic Algorithm (DEAP)',
                'quantities': best_individual
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
                # Calculate total macros
                total_calories = sum(x[i] * ingredients[i]['calories_per_100g'] / 100 
                                   for i in range(len(ingredients)))
                total_protein = sum(x[i] * ingredients[i]['protein_per_100g'] / 100 
                                  for i in range(len(ingredients)))
                total_carbs = sum(x[i] * ingredients[i]['carbs_per_100g'] / 100 
                                for i in range(len(ingredients)))
                total_fat = sum(x[i] * ingredients[i]['fat_per_100g'] / 100 
                              for i in range(len(ingredients)))
                
                # Calculate deviation from targets
                deviation = (
                    abs(total_calories - target_macros['calories']) / target_macros['calories'] +
                    abs(total_protein - target_macros['protein']) / max(target_macros['protein'], 1) +
                    abs(total_carbs - target_macros['carbs']) / max(target_macros['carbs'], 1) +
                    abs(total_fat - target_macros['fat']) / max(target_macros['fat'], 1)
                )
                
                return deviation
            
            # Bounds for quantities (0 to 500g per ingredient)
            bounds = [(0, 500) for _ in range(len(ingredients))]
            
            # Run differential evolution
            result = differential_evolution(
                objective, 
                bounds, 
                maxiter=100, 
                popsize=15, 
                seed=42
            )
            
            if result.success:
                return {
                    'success': True,
                    'method': 'Differential Evolution (SciPy)',
                    'quantities': result.x.tolist()
                }
            else:
                return {'success': False, 'method': 'Differential Evolution (SciPy)', 'quantities': []}
                
        except Exception as e:
            logger.error(f"Differential evolution optimization failed: {e}")
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
                
                # Calculate deviation from targets
                deviation = (
                    abs(total_calories - target_macros['calories']) / target_macros['calories'] +
                    abs(total_protein - target_macros['protein']) / max(target_macros['protein'], 1) +
                    abs(total_carbs - target_macros['carbs']) / max(target_macros['carbs'], 1) +
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
        """Hybrid optimization combining multiple methods"""
        try:
            # Try genetic algorithm first
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
    
    def _evaluate_genetic_fitness(self, individual):
        """Evaluate fitness for genetic algorithm (placeholder - will be overridden)"""
        return (0.0,)
    
    def _fallback_scaling(
        self, 
        ingredients: List[Dict], 
        target_macros: Dict
    ) -> Dict:
        """Fallback method using simple scaling"""
        try:
            # Calculate current totals
            current_totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
            for ingredient in ingredients:
                if ingredient.get('source') == 'rag':
                    amount = ingredient.get('original_amount', 100)
                    current_totals['calories'] += (ingredient.get('calories_per_100g', 0) * amount) / 100
                    current_totals['protein'] += (ingredient.get('protein_per_100g', 0) * amount) / 100
                    current_totals['carbs'] += (ingredient.get('carbs_per_100g', 0) * amount) / 100
                    current_totals['fat'] += (ingredient.get('fat_per_100g', 0) * amount) / 100
            
            # Calculate scaling factors
            scale_factors = {}
            for macro in ['calories', 'protein', 'carbs', 'fat']:
                if current_totals[macro] > 0:
                    scale_factors[macro] = target_macros[macro] / current_totals[macro]
                else:
                    scale_factors[macro] = 1.0
            
            # Use average scaling factor
            avg_scale = sum(scale_factors.values()) / len(scale_factors)
            
            # Apply scaling
            quantities = []
            for ingredient in ingredients:
                if ingredient.get('source') == 'rag':
                    quantities.append(ingredient.get('original_amount', 100) * avg_scale)
                else:
                    # For supplementary ingredients, add reasonable amounts
                    quantities.append(100.0)  # Default 100g
            
            return {
                'success': True,
                'method': 'Fallback Scaling',
                'quantities': quantities
            }
            
        except Exception as e:
            logger.error(f"Fallback scaling failed: {e}")
            return {'success': False, 'method': 'Fallback Scaling', 'quantities': []}
    
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
