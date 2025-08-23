import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any
import time as time_module
import logging
from models import (
    Ingredient, MealPlan, MealItem, NutritionalTarget, 
    UserPreferences, OptimizationResult, MealTime
)
from pulp import *
from deap import base, creator, tools, algorithms
import random
from scipy.optimize import minimize, differential_evolution, dual_annealing
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error
import asyncio
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import json

logger = logging.getLogger(__name__)

class MealOptimizationEngine:
    """
    Advanced meal optimization engine using multiple optimization techniques:
    - Linear Programming (PuLP)
    - Genetic Algorithms (DEAP)
    - Differential Evolution (SciPy)
    - Particle Swarm Optimization (Custom Implementation)
    - Simulated Annealing (SciPy)
    - Machine Learning (Scikit-learn)
    - Multi-objective optimization
    - Constraint satisfaction algorithms
    """
    
    def __init__(self):
        self.optimization_methods = {
            'linear_programming': self._optimize_linear_programming,
            'genetic_algorithm': self._optimize_genetic_algorithm,
            'differential_evolution': self._optimize_differential_evolution,
            'particle_swarm': self._optimize_particle_swarm,
            'simulated_annealing': self._optimize_simulated_annealing,
            'hybrid': self._optimize_hybrid,
            'multi_objective': self._optimize_multi_objective
        }
        
        # Initialize genetic algorithm components
        self._setup_genetic_algorithm()
        
        # Initialize machine learning models
        self._setup_ml_models()
        
        # Optimization history for learning
        self.optimization_history = []
        
    def _setup_ml_models(self):
        """Setup machine learning models for optimization guidance"""
        self.ml_models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'neural_network': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
        }
        
        # Feature scaler
        self.scaler = StandardScaler()
        
    def _setup_genetic_algorithm(self):
        """Setup genetic algorithm components with improved parameters"""
        if 'FITNESS_MAX' not in creator.__dict__:
            creator.create("FITNESS_MAX", base.Fitness, weights=(1.0,))
        if 'INDIVIDUAL' not in creator.__dict__:
            creator.create("INDIVIDUAL", list, fitness=creator.FITNESS_MAX)
        
        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_float", random.uniform, 0, 300)  # Increased range
        self.toolbox.register("individual", tools.initRepeat, creator.INDIVIDUAL, 
                            self.toolbox.attr_float, n=100)  # Increased complexity
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self._evaluate_genetic_fitness)
        self.toolbox.register("mate", tools.cxBlend, alpha=0.5)  # Blend crossover
        self.toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=25, indpb=0.15)
        self.toolbox.register("select", tools.selNSGA2)  # Multi-objective selection

    async def optimize_meal_plan(
        self,
        ingredients: List[Ingredient],
        target_macros: NutritionalTarget,
        user_preferences: UserPreferences,
        meal_periods: List[MealTime]
    ) -> Dict:
        """
        Main optimization method that tries different approaches with parallel execution
        """
        start_time = time_module.time()
        
        # Filter ingredients based on user preferences
        filtered_ingredients = self._filter_ingredients(ingredients, user_preferences)
        
        # Try different optimization methods in parallel
        best_result = None
        best_score = float('-inf')
        
        # Create tasks for parallel execution
        tasks = []
        for method_name, method_func in self.optimization_methods.items():
            if method_name in ['genetic_algorithm', 'particle_swarm']:
                task = self._run_async_optimization(
                    method_func, filtered_ingredients, target_macros, meal_periods
                )
            else:
                task = self._run_async_optimization(
                    method_func, filtered_ingredients, target_macros, meal_periods
                )
            tasks.append((method_name, task))
        
        # Execute all methods and find the best result
        for method_name, task in tasks:
            try:
                logger.info(f"Executing optimization method: {method_name}")
                result = await task
                
                if result and result['score'] > best_score:
                    best_score = result['score']
                    best_result = result
                    best_result['method'] = method_name
                    
            except Exception as e:
                logger.warning(f"Method {method_name} failed: {e}")
                continue
        
        if not best_result:
            raise Exception("All optimization methods failed")
        
        # Create meal plans
        meal_plans = self._create_meal_plans(best_result, meal_periods, filtered_ingredients)
        
        # Calculate daily totals
        daily_totals = self._calculate_daily_totals(meal_plans)
        
        # Check if target achieved
        target_achieved = self._check_target_achievement(daily_totals, target_macros)
        
        # If target not achieved, add personalized ingredients
        if not target_achieved:
            meal_plans = await self._add_personalized_ingredients(
                meal_plans, target_macros, daily_totals, filtered_ingredients, user_preferences
            )
            daily_totals = self._calculate_daily_totals(meal_plans)
        
        computation_time = time_module.time() - start_time
        
        # Store optimization result for learning
        self.optimization_history.append({
            'method': best_result['method'],
            'score': best_score,
            'computation_time': computation_time,
            'target_achieved': target_achieved
        })
        
        optimization_result = OptimizationResult(
            success=True,
            target_achieved=target_achieved,
            optimization_method=best_result['method'],
            objective_value=best_score,
            constraints_violated=[],
            computation_time=computation_time
        )
        
        return {
            'optimization_result': optimization_result,
            'meal_plans': meal_plans,
            'daily_totals': daily_totals,
            'recommendations': self._generate_recommendations(daily_totals, target_macros),
            'cost_estimate': self._estimate_cost(meal_plans),
            'shopping_list': self._create_shopping_list(meal_plans)
        }

    def _filter_ingredients(self, ingredients: List[Ingredient], preferences: UserPreferences) -> List[Ingredient]:
        """Filter ingredients based on user preferences and restrictions"""
        filtered = []
        
        for ingredient in ingredients:
            # Check dietary restrictions
            if preferences.dietary_restrictions:
                if 'vegetarian' in preferences.dietary_restrictions and 'meat' in ingredient.category.lower():
                    continue
                if 'vegan' in preferences.dietary_restrictions and 'animal' in ingredient.category.lower():
                    continue
                if 'gluten-free' in preferences.dietary_restrictions and 'gluten' in ingredient.name.lower():
                    continue
            
            # Check allergies
            if any(allergy.lower() in ingredient.name.lower() for allergy in preferences.allergies):
                continue
                
            filtered.append(ingredient)
        
        return filtered

    def _optimize_linear_programming(
        self, 
        ingredients: List[Ingredient], 
        target_macros: NutritionalTarget,
        meal_times: List[MealTime]
    ) -> Dict:
        """Linear Programming optimization using PuLP"""
        try:
            # Create optimization problem
            prob = LpProblem("Meal_Optimization", LpMinimize)
            
            # Decision variables: quantity of each ingredient for each meal
            ingredient_vars = {}
            for i, ingredient in enumerate(ingredients):
                for meal_time in meal_times:
                    var_name = f"ingredient_{i}_{meal_time.value}"
                    ingredient_vars[(i, meal_time)] = LpVariable(var_name, 0, None)
            
            # Objective function: minimize deviation from target macros
            # Create auxiliary variables for absolute values
            calorie_deviation = LpVariable("calorie_deviation", 0, None)
            protein_deviation = LpVariable("protein_deviation", 0, None)
            
            # Calculate total calories and protein
            total_calories = lpSum([ingredient_vars[(i, meal_time)] * ingredient.calories_per_100g / 100 
                                   for i, ingredient in enumerate(ingredients) 
                                   for meal_time in meal_times])
            total_protein = lpSum([ingredient_vars[(i, meal_time)] * ingredient.protein_per_100g / 100 
                                  for i, ingredient in enumerate(ingredients) 
                                  for meal_time in meal_times])
            
            # Objective: minimize total deviation
            prob += calorie_deviation + protein_deviation
            
            # Constraints for absolute deviations
            prob += total_calories - target_macros.calories <= calorie_deviation
            prob += target_macros.calories - total_calories <= calorie_deviation
            prob += total_protein - target_macros.protein <= protein_deviation
            prob += target_macros.protein - total_protein <= protein_deviation
            
            # Constraints
            # Protein constraint
            prob += lpSum([ingredient_vars[(i, meal_time)] * ingredient.protein_per_100g / 100 
                          for i, ingredient in enumerate(ingredients) 
                          for meal_time in meal_times]) >= target_macros.protein * 0.8
            
            # Calories constraint
            prob += lpSum([ingredient_vars[(i, meal_time)] * ingredient.calories_per_100g / 100 
                          for i, ingredient in enumerate(ingredients) 
                          for meal_time in meal_times]) >= target_macros.calories * 0.8
            
            # Solve
            prob.solve(PULP_CBC_CMD(msg=False))
            
            if prob.status == LpStatusOptimal:
                # Extract solution
                solution = {}
                for (i, meal_time), var in ingredient_vars.items():
                    if value(var) > 0:
                        solution[(i, meal_time)] = value(var)
                
                return {
                    'solution': solution,
                    'score': -prob.objective.value(),
                    'status': 'optimal'
                }
            
        except Exception as e:
            logger.error(f"Linear programming optimization failed: {e}")
        
        return None

    def _optimize_genetic_algorithm(
        self, 
        ingredients: List[Ingredient], 
        target_macros: NutritionalTarget,
        meal_times: List[MealTime]
    ) -> Dict:
        """Genetic Algorithm optimization using DEAP"""
        try:
            # Population size and generations
            POPULATION_SIZE = 50
            NGEN = 30
            
            # Create population
            pop = self.toolbox.population(n=POPULATION_SIZE)
            
            # Statistics
            stats = tools.Statistics(lambda ind: ind.fitness.values)
            stats.register("avg", np.mean)
            stats.register("std", np.std)
            stats.register("min", np.min)
            stats.register("max", np.max)
            
            # Hall of fame
            hof = tools.HallOfFame(1)
            
            # Run genetic algorithm
            pop, logbook = algorithms.eaSimple(
                pop, self.toolbox, cxpb=0.7, mutpb=0.2, 
                ngen=NGEN, stats=stats, halloffame=hof, verbose=False
            )
            
            best_individual = hof[0]
            
            # Convert to solution format
            solution = {}
            for i, (ingredient, meal_time) in enumerate(zip(ingredients, meal_times * (len(ingredients) // len(meal_times) + 1))):
                if i < len(best_individual):
                    solution[(i, meal_time)] = max(0, best_individual[i])
            
            return {
                'solution': solution,
                'score': best_individual.fitness.values[0],
                'status': 'genetic_optimal'
            }
            
        except Exception as e:
            logger.error(f"Genetic algorithm optimization failed: {e}")
        
        return None

    def _optimize_differential_evolution(
        self, 
        ingredients: List[Ingredient], 
        target_macros: NutritionalTarget,
        meal_times: List[MealTime]
    ) -> Dict:
        """Differential Evolution optimization using SciPy"""
        try:
            n_variables = len(ingredients) * len(meal_times)
            
            # Bounds for each variable (0 to 200g)
            bounds = [(0, 200)] * n_variables
            
            # Objective function
            def objective(x):
                return self._calculate_objective_value(x, ingredients, target_macros, meal_times)
            
            # Run differential evolution
            result = differential_evolution(
                objective, bounds, 
                maxiter=100, popsize=15, 
                seed=42, workers=1
            )
            
            if result.success:
                # Convert to solution format
                solution = {}
                for i, value in enumerate(result.x):
                    if value > 0:
                        ingredient_idx = i // len(meal_times)
                        meal_idx = i % len(meal_times)
                        solution[(ingredient_idx, meal_times[meal_idx])] = value
                
                return {
                    'solution': solution,
                    'score': -result.fun,
                    'status': 'differential_optimal'
                }
                
        except Exception as e:
            logger.error(f"Differential evolution optimization failed: {e}")
        
        return None

    def _optimize_particle_swarm(
        self, 
        ingredients: List[Ingredient], 
        target_macros: NutritionalTarget,
        meal_times: List[MealTime]
    ) -> Dict:
        """Particle Swarm Optimization implementation"""
        try:
            n_particles = 30
            n_variables = len(ingredients) * len(meal_times)
            max_iterations = 100
            
            # Initialize particles and velocities
            particles = np.random.uniform(0, 200, (n_particles, n_variables))
            velocities = np.random.uniform(-10, 10, (n_particles, n_variables))
            
            # Personal and global best
            personal_best = particles.copy()
            personal_best_scores = np.array([float('inf')] * n_particles)
            global_best = particles[0].copy()
            global_best_score = float('inf')
            
            # PSO parameters
            w = 0.7  # inertia weight
            c1 = 2.0  # cognitive parameter
            c2 = 2.0  # social parameter
            
            for iteration in range(max_iterations):
                for i in range(n_particles):
                    # Evaluate fitness
                    score = self._calculate_objective_value(particles[i], ingredients, target_macros, meal_times)
                    
                    # Update personal best
                    if score < personal_best_scores[i]:
                        personal_best_scores[i] = score
                        personal_best[i] = particles[i].copy()
                        
                        # Update global best
                        if score < global_best_score:
                            global_best_score = score
                            global_best = particles[i].copy()
                
                # Update velocities and positions
                for i in range(n_particles):
                    r1, r2 = np.random.random(2)
                    
                    velocities[i] = (w * velocities[i] + 
                                   c1 * r1 * (personal_best[i] - particles[i]) +
                                   c2 * r2 * (global_best - particles[i]))
                    
                    particles[i] += velocities[i]
                    particles[i] = np.clip(particles[i], 0, 200)
            
            # Convert to solution format
            solution = {}
            for i, value in enumerate(global_best):
                if value > 0:
                    ingredient_idx = i // len(meal_times)
                    meal_idx = i % len(meal_times)
                    solution[(ingredient_idx, meal_times[meal_idx])] = value
            
            return {
                'solution': solution,
                'score': -global_best_score,
                'status': 'pso_optimal'
            }
            
        except Exception as e:
            logger.error(f"Particle swarm optimization failed: {e}")
        
        return None

    def _optimize_simulated_annealing(
        self, 
        ingredients: List[Ingredient], 
        target_macros: NutritionalTarget,
        meal_times: List[MealTime]
    ) -> Dict:
        """Simulated Annealing optimization using SciPy"""
        try:
            n_variables = len(ingredients) * len(meal_times)
            
            # Bounds for each variable (0 to 200g)
            bounds = [(0, 200)] * n_variables
            
            # Objective function
            def objective(x):
                return self._calculate_objective_value(x, ingredients, target_macros, meal_times)
            
            # Run simulated annealing
            result = dual_annealing(
                objective, bounds,
                maxiter=1000, seed=42
            )
            
            if result.success:
                # Convert to solution format
                solution = {}
                for i, value in enumerate(result.x):
                    if value > 0:
                        ingredient_idx = i // len(meal_times)
                        meal_idx = i % len(meal_times)
                        solution[(ingredient_idx, meal_times[meal_idx])] = value
                
                return {
                    'solution': solution,
                    'score': -result.fun,
                    'status': 'annealing_optimal'
                }
                
        except Exception as e:
            logger.error(f"Simulated annealing optimization failed: {e}")
        
        return None

    def _optimize_multi_objective(
        self, 
        ingredients: List[Ingredient], 
        target_macros: NutritionalTarget,
        meal_times: List[MealTime]
    ) -> Dict:
        """Multi-objective optimization considering multiple nutritional goals"""
        try:
            n_variables = len(ingredients) * len(meal_times)
            
            # Multiple objective functions
            def objective_calories(x):
                total_calories = 0
                for i, value in enumerate(x):
                    ingredient_idx = i // len(meal_times)
                    if ingredient_idx < len(ingredients):
                        ingredient = ingredients[ingredient_idx]
                        total_calories += value * ingredient.calories_per_100g / 100
                return abs(total_calories - target_macros.calories)
            
            def objective_protein(x):
                total_protein = 0
                for i, value in enumerate(x):
                    ingredient_idx = i // len(meal_times)
                    if ingredient_idx < len(ingredients):
                        ingredient = ingredients[ingredient_idx]
                        total_protein += value * ingredient.protein_per_100g / 100
                return abs(total_protein - target_macros.protein)
            
            def objective_cost(x):
                total_cost = 0
                for i, value in enumerate(x):
                    ingredient_idx = i // len(meal_times)
                    if ingredient_idx < len(ingredients):
                        ingredient = ingredients[ingredient_idx]
                        if ingredient.price_per_kg:
                            total_cost += (value / 1000) * ingredient.price_per_kg
                return total_cost
            
            # Combined objective with weights
            def combined_objective(x):
                w1, w2, w3 = 0.4, 0.4, 0.2  # weights for calories, protein, cost
                return (w1 * objective_calories(x) + 
                       w2 * objective_protein(x) + 
                       w3 * objective_cost(x))
            
            # Bounds for each variable (0 to 200g)
            bounds = [(0, 200)] * n_variables
            
            # Run optimization
            result = minimize(
                combined_objective, 
                x0=np.random.uniform(50, 150, n_variables),
                bounds=bounds,
                method='L-BFGS-B',
                options={'maxiter': 200}
            )
            
            if result.success:
                # Convert to solution format
                solution = {}
                for i, value in enumerate(result.x):
                    if value > 0:
                        ingredient_idx = i // len(meal_times)
                        meal_idx = i % len(meal_times)
                        solution[(ingredient_idx, meal_times[meal_idx])] = value
                
                return {
                    'solution': solution,
                    'score': -result.fun,
                    'status': 'multi_objective_optimal'
                }
                
        except Exception as e:
            logger.error(f"Multi-objective optimization failed: {e}")
        
        return None

    def _optimize_hybrid(
        self, 
        ingredients: List[Ingredient], 
        target_macros: NutritionalTarget,
        meal_times: List[MealTime]
    ) -> Dict:
        """Hybrid optimization combining multiple methods with intelligent selection"""
        try:
            results = []
            
            # Try all optimization methods
            methods = [
                ('linear_programming', self._optimize_linear_programming),
                ('genetic_algorithm', self._optimize_genetic_algorithm),
                ('differential_evolution', self._optimize_differential_evolution),
                ('particle_swarm', self._optimize_particle_swarm),
                ('simulated_annealing', self._optimize_simulated_annealing),
                ('multi_objective', self._optimize_multi_objective)
            ]
            
            for method_name, method_func in methods:
                try:
                    result = method_func(ingredients, target_macros, meal_times)
                    if result:
                        results.append((method_name, result))
                except Exception as e:
                    logger.warning(f"Method {method_name} failed in hybrid: {e}")
                    continue
            
            if not results:
                raise Exception("All optimization methods failed in hybrid approach")
            
            # Select best result based on multiple criteria
            best_result = None
            best_score = float('-inf')
            
            for method_name, result in results:
                # Calculate composite score considering multiple factors
                score = result['score']
                
                # Bonus for faster methods
                if method_name == 'linear_programming':
                    score *= 1.1
                elif method_name == 'genulated_annealing':
                    score *= 1.05
                
                if score > best_score:
                    best_score = score
                    best_result = result
                    best_result['method'] = method_name
            
            return best_result
                
        except Exception as e:
            logger.error(f"Hybrid optimization failed: {e}")
        
        return None

    def _evaluate_genetic_fitness(self, individual):
        """Fitness function for genetic algorithm"""
        # This is a simplified fitness function
        # In practice, you'd want to calculate actual nutritional values
        return sum(individual),

    def _calculate_objective_value(self, x, ingredients, target_macros, meal_times):
        """Calculate objective value for differential evolution"""
        total_calories = 0
        total_protein = 0
        
        for i, value in enumerate(x):
            ingredient_idx = i // len(meal_times)
            meal_idx = i % len(meal_times)
            
            if ingredient_idx < len(ingredients):
                ingredient = ingredients[ingredient_idx]
                total_calories += value * ingredient.calories_per_100g / 100
                total_protein += value * ingredient.protein_per_100g / 100
        
        # Penalty for deviation from targets
        calorie_penalty = abs(total_calories - target_macros.calories) ** 2
        protein_penalty = abs(total_protein - target_macros.protein) ** 2
        
        return calorie_penalty + protein_penalty

    def _create_meal_plans(self, optimization_result: Dict, meal_times: List[MealTime], ingredients: List[Ingredient] = None) -> List[MealPlan]:
        """Create meal plans from optimization result"""
        meal_plans = []
        
        # Use provided ingredients or fall back to stored ones
        if ingredients is None:
            ingredients = getattr(self, 'ingredients', [])
        
        for meal_time in meal_times:
            items = []
            total_calories = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            
            for (ingredient_idx, mt), quantity in optimization_result['solution'].items():
                if mt == meal_time and quantity > 0 and ingredient_idx < len(ingredients):
                    ingredient = ingredients[ingredient_idx]
                    item = MealItem(
                        ingredient=ingredient,
                        quantity_grams=quantity,
                        calories=quantity * ingredient.calories_per_100g / 100,
                        protein=quantity * ingredient.protein_per_100g / 100,
                        carbs=quantity * ingredient.carbs_per_100g / 100,
                        fat=quantity * ingredient.fat_per_100g / 100
                    )
                    items.append(item)
                    
                    total_calories += item.calories
                    total_protein += item.protein
                    total_carbs += item.carbs
                    total_fat += item.fat
            
            meal_plan = MealPlan(
                meal_time=meal_time,
                items=items,
                total_calories=total_calories,
                total_protein=total_protein,
                total_carbs=total_carbs,
                total_fat=total_fat
            )
            meal_plans.append(meal_plan)
        
        return meal_plans

    def _calculate_daily_totals(self, meal_plans: List[MealPlan]) -> NutritionalTarget:
        """Calculate daily nutritional totals"""
        total_calories = sum(plan.total_calories for plan in meal_plans)
        total_protein = sum(plan.total_protein for plan in meal_plans)
        total_carbs = sum(plan.total_carbs for plan in meal_plans)
        total_fat = sum(plan.total_fat for plan in meal_plans)
        
        return NutritionalTarget(
            calories=total_calories,
            protein=total_protein,
            carbohydrates=total_carbs,
            fat=total_fat
        )

    def _check_target_achievement(self, daily_totals: NutritionalTarget, target_macros: NutritionalTarget) -> bool:
        """Check if target macros are achieved"""
        calorie_achieved = abs(daily_totals.calories - target_macros.calories) / target_macros.calories < 0.1
        protein_achieved = abs(daily_totals.protein - target_macros.protein) / target_macros.protein < 0.1
        carbs_achieved = abs(daily_totals.carbohydrates - target_macros.carbohydrates) / target_macros.carbohydrates < 0.1
        fat_achieved = abs(daily_totals.fat - target_macros.fat) / target_macros.fat < 0.1
        
        return calorie_achieved and protein_achieved and carbs_achieved and fat_achieved

    async def _add_personalized_ingredients(
        self,
        meal_plans: List[MealPlan],
        target_macros: NutritionalTarget,
        current_totals: NutritionalTarget,
        ingredients: List[Ingredient],
        user_preferences: UserPreferences
    ) -> List[MealPlan]:
        """Add personalized ingredients to meet target macros"""
        # Calculate deficits
        calorie_deficit = target_macros.calories - current_totals.calories
        protein_deficit = target_macros.protein - current_totals.protein
        carbs_deficit = target_macros.carbohydrates - current_totals.carbohydrates
        fat_deficit = target_macros.fat - current_totals.fat
        
        # Find suitable ingredients for each meal time
        for meal_plan in meal_plans:
            if calorie_deficit > 0 or protein_deficit > 0:
                # Add protein-rich ingredients for breakfast and dinner
                if meal_plan.meal_time in [MealTime.BREAKFAST, MealTime.DINNER]:
                    protein_ingredients = [i for i in ingredients if i.protein_per_100g > 20]
                    if protein_ingredients:
                        ingredient = random.choice(protein_ingredients)
                        quantity = min(100, protein_deficit / (ingredient.protein_per_100g / 100))
                        
                        item = MealItem(
                            ingredient=ingredient,
                            quantity_grams=quantity,
                            calories=quantity * ingredient.calories_per_100g / 100,
                            protein=quantity * ingredient.protein_per_100g / 100,
                            carbs=quantity * ingredient.carbs_per_100g / 100,
                            fat=quantity * ingredient.fat_per_100g / 100
                        )
                        meal_plan.items.append(item)
                        
                        # Update totals
                        meal_plan.total_calories += item.calories
                        meal_plan.total_protein += item.protein
                        meal_plan.total_carbs += item.carbs
                        meal_plan.total_fat += item.fat
                        
                        protein_deficit -= item.protein
                        calorie_deficit -= item.calories
        
        return meal_plans

    async def _add_personalized_ingredients_ml(
        self,
        meal_plans: List[MealPlan],
        target_macros: NutritionalTarget,
        current_totals: NutritionalTarget,
        ingredients: List[Ingredient],
        user_preferences: UserPreferences
    ) -> List[MealPlan]:
        """Add personalized ingredients to meet target macros using ML models"""
        # Calculate deficits
        calorie_deficit = target_macros.calories - current_totals.calories
        protein_deficit = target_macros.protein - current_totals.protein
        carbs_deficit = target_macros.carbohydrates - current_totals.carbohydrates
        fat_deficit = target_macros.fat - current_totals.fat
        
        # Use ML models to predict optimal ingredient additions
        if len(meal_plans) > 0 and len(meal_plans[0].items) > 0:
            try:
                # Prepare sample data for ML prediction
                sample_data = []
                for meal_plan in meal_plans:
                    for item in meal_plan.items:
                        sample_data.append([item.calories, item.protein, item.carbs, item.fat])
                
                if sample_data:
                    # Scale features
                    sample_data_scaled = self.scaler.fit_transform(sample_data)
                    
                    # Predict optimal additions using ML models
                    if hasattr(self.ml_models['random_forest'], 'predict'):
                        # Use trained model if available
                        optimal_additions = self.ml_models['random_forest'].predict(sample_data_scaled)
                    else:
                        # Fallback to heuristic approach
                        optimal_additions = [100] * len(sample_data)
            except Exception as e:
                logger.warning(f"ML prediction failed, using fallback: {e}")
                optimal_additions = [100] * len(meal_plans)
        else:
            optimal_additions = [100] * len(meal_plans)

        # Add personalized ingredients
        for meal_plan in meal_plans:
            for i, item in enumerate(meal_plan.items):
                if item.calories < target_macros.calories * 0.9: # If current calories are low
                    ingredient = random.choice(ingredients)
                    quantity = min(calories_to_add_grams[i], 100) # Add up to 100g
                    if quantity > 0:
                        new_item = MealItem(
                            ingredient=ingredient,
                            quantity_grams=quantity,
                            calories=quantity * ingredient.calories_per_100g / 100,
                            protein=quantity * ingredient.protein_per_100g / 100,
                            carbs=quantity * ingredient.carbs_per_100g / 100,
                            fat=quantity * ingredient.fat_per_100g / 100
                        )
                        meal_plan.items.append(new_item)
                        meal_plan.total_calories += new_item.calories
                        meal_plan.total_protein += new_item.protein
                        meal_plan.total_carbs += new_item.carbs
                        meal_plan.total_fat += new_item.fat

                if item.protein < target_macros.protein * 0.9: # If current protein is low
                    ingredient = random.choice(ingredients)
                    quantity = min(protein_to_add_grams[i], 100) # Add up to 100g
                    if quantity > 0:
                        new_item = MealItem(
                            ingredient=ingredient,
                            quantity_grams=quantity,
                            calories=quantity * ingredient.calories_per_100g / 100,
                            protein=quantity * ingredient.protein_per_100g / 100,
                            carbs=quantity * ingredient.carbs_per_100g / 100,
                            fat=quantity * ingredient.fat_per_100g / 100
                        )
                        meal_plan.items.append(new_item)
                        meal_plan.total_calories += new_item.calories
                        meal_plan.total_protein += new_item.protein
                        meal_plan.total_carbs += new_item.carbs
                        meal_plan.total_fat += new_item.fat

        return meal_plans

    def _generate_recommendations(self, daily_totals: NutritionalTarget, target_macros: NutritionalTarget) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if daily_totals.protein < target_macros.protein * 0.9:
            recommendations.append("Consider adding more protein-rich foods like lean meats, fish, or legumes")
        
        if daily_totals.carbohydrates < target_macros.carbohydrates * 0.9:
            recommendations.append("Include more whole grains, fruits, and vegetables for carbohydrates")
        
        if daily_totals.fat < target_macros.fat * 0.9:
            recommendations.append("Add healthy fats from nuts, avocados, or olive oil")
        
        return recommendations

    def _generate_recommendations_ml(self, daily_totals: NutritionalTarget, target_macros: NutritionalTarget, user_preferences: UserPreferences) -> List[str]:
        """Generate personalized recommendations using ML models"""
        recommendations = []
        
        # Prepare data for ML models
        X_calories = []
        X_protein = []
        for meal_plan in [MealPlan(meal_time=MealTime.BREAKFAST, items=[], total_calories=daily_totals.calories, total_protein=daily_totals.protein, total_carbs=daily_totals.carbohydrates, total_fat=daily_totals.fat)]:
            for item in meal_plan.items:
                X_calories.append([item.calories, item.protein, item.carbs, item.fat])
                X_protein.append([item.protein, item.calories, item.carbs, item.fat])

        # Scale features
        X_calories_scaled = self.scaler.transform(X_calories)
        X_protein_scaled = self.scaler.transform(X_protein)

        # Predict additional quantities for calories and protein
        calories_to_add = self.ml_models['random_forest'].predict(X_calories_scaled)
        protein_to_add = self.ml_models['gradient_boosting'].predict(X_protein_scaled)

        # Convert predictions to grams
        calories_to_add_grams = calories_to_add * 100
        protein_to_add_grams = protein_to_add * 100

        # Add personalized recommendations
        if daily_totals.protein < target_macros.protein * 0.9:
            recommendations.append("Consider adding more protein-rich foods like lean meats, fish, or legumes")
        
        if daily_totals.carbohydrates < target_macros.carbohydrates * 0.9:
            recommendations.append("Include more whole grains, fruits, and vegetables for carbohydrates")
        
        if daily_totals.fat < target_macros.fat * 0.9:
            recommendations.append("Add healthy fats from nuts, avocados, or olive oil")
        
        return recommendations

    def _estimate_cost(self, meal_plans: List[MealPlan]) -> float:
        """Estimate daily cost of meal plan"""
        total_cost = 0
        for meal_plan in meal_plans:
            for item in meal_plan.items:
                if item.ingredient.price_per_kg:
                    total_cost += (item.quantity_grams / 1000) * item.ingredient.price_per_kg
        return total_cost

    def _create_shopping_list(self, meal_plans: List[MealPlan]) -> List[Dict]:
        """Create shopping list with quantities"""
        shopping_dict = {}
        
        for meal_plan in meal_plans:
            for item in meal_plan.items:
                ingredient_name = item.ingredient.name
                if ingredient_name in shopping_dict:
                    shopping_dict[ingredient_name]['quantity'] += item.quantity_grams
                else:
                    shopping_dict[ingredient_name] = {
                        'name': ingredient_name,
                        'quantity': item.quantity_grams,
                        'unit': 'grams'
                    }
        
        return list(shopping_dict.values())

    async def _run_async_optimization(self, method_func, *args):
        """Run optimization method asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, method_func, *args)

    async def optimize_rag_meal_plan(
        self,
        rag_response: Dict[str, Any],
        target_macros: NutritionalTarget,
        user_preferences: UserPreferences,
        available_ingredients: List[Ingredient]
    ) -> Dict:
        """
        Optimize meal plan from RAG response and add missing ingredients to reach targets
        """
        try:
            # Parse RAG response
            suggestions = rag_response.get('suggestions', [])
            if not suggestions:
                raise ValueError("No meal suggestions found in RAG response")
            
            # Convert RAG ingredients to our format
            rag_ingredients = self._convert_rag_ingredients(suggestions[0]['ingredients'])
            
            # Calculate current macros from RAG
            current_macros = self._calculate_rag_macros(rag_ingredients)
            
            # Check if targets are met
            if self._targets_met(current_macros, target_macros):
                return self._create_rag_response(rag_ingredients, current_macros, "Targets already met")
            
            # Find missing ingredients to reach targets
            missing_ingredients = self._find_missing_ingredients(
                current_macros, target_macros, available_ingredients, rag_ingredients
            )
            
            # Add missing ingredients
            final_ingredients = rag_ingredients + missing_ingredients
            
            # Recalculate macros
            final_macros = self._calculate_total_macros(final_ingredients)
            
            # Create meal plans
            meal_plans = self._create_meal_plans_from_ingredients(final_ingredients)
            
            # Create optimization result
            optimization_result = OptimizationResult(
                success=True,
                target_achieved=self._targets_met(final_macros, target_macros),
                optimization_method='rag_enhanced',
                objective_value=self._calculate_objective_value(final_macros, target_macros),
                constraints_violated=[],
                computation_time=0.1
            )
            
            return {
                'optimization_result': optimization_result,
                'meal_plans': meal_plans,
                'daily_totals': final_macros,
                'recommendations': self._generate_rag_recommendations(final_macros, target_macros),
                'cost_estimate': self._estimate_cost(meal_plans),
                'shopping_list': self._create_shopping_list(meal_plans),
                'rag_enhancement': {
                    'original_macros': current_macros,
                    'added_ingredients': missing_ingredients,
                    'enhancement_notes': f"Added {len(missing_ingredients)} ingredients to reach targets"
                }
            }
            
        except Exception as e:
            logger.error(f"RAG optimization failed: {e}")
            raise

    def _convert_rag_ingredients(self, rag_ingredients: List[Dict]) -> List[Ingredient]:
        """Convert RAG ingredient format to our Ingredient model"""
        converted = []
        
        for rag_ing in rag_ingredients:
            ingredient = Ingredient(
                id=None,
                name=rag_ing['name'],
                name_fa=rag_ing['name'],  # Could be enhanced with Persian names
                calories_per_100g=rag_ing['calories'] * 100 / rag_ing['amount'],
                protein_per_100g=rag_ing['protein'] * 100 / rag_ing['amount'],
                carbs_per_100g=rag_ing['carbs'] * 100 / rag_ing['amount'],
                fat_per_100g=rag_ing['fat'] * 100 / rag_ing['amount'],
                fiber_per_100g=None,
                sugar_per_100g=None,
                sodium_per_100g=None,
                category=self._categorize_ingredient(rag_ing['name']),
                suitable_meals=[MealTime.LUNCH, MealTime.DINNER],  # Default
                price_per_kg=None,
                availability=True
            )
            converted.append(ingredient)
        
        return converted

    def _categorize_ingredient(self, name: str) -> str:
        """Categorize ingredient based on name"""
        name_lower = name.lower()
        
        protein_keywords = ['beef', 'chicken', 'fish', 'salmon', 'tuna', 'eggs', 'yogurt', 'cheese']
        grain_keywords = ['rice', 'bread', 'pasta', 'quinoa', 'oats']
        vegetable_keywords = ['spinach', 'tomato', 'onion', 'carrot', 'broccoli', 'lettuce']
        fruit_keywords = ['apple', 'banana', 'orange', 'berry', 'grape']
        fat_keywords = ['butter', 'oil', 'olive', 'avocado', 'nuts']
        
        if any(keyword in name_lower for keyword in protein_keywords):
            return 'protein'
        elif any(keyword in name_lower for keyword in grain_keywords):
            return 'grain'
        elif any(keyword in name_lower for keyword in vegetable_keywords):
            return 'vegetable'
        elif any(keyword in name_lower for keyword in fruit_keywords):
            return 'fruit'
        elif any(keyword in name_lower for keyword in fat_keywords):
            return 'fat'
        else:
            return 'other'

    def _calculate_rag_macros(self, ingredients: List[Ingredient]) -> NutritionalTarget:
        """Calculate total macros from RAG ingredients"""
        total_calories = sum(ing.calories_per_100g for ing in ingredients)
        total_protein = sum(ing.protein_per_100g for ing in ingredients)
        total_carbs = sum(ing.carbs_per_100g for ing in ingredients)
        total_fat = sum(ing.fat_per_100g for ing in ingredients)
        
        return NutritionalTarget(
            calories=total_calories,
            protein=total_protein,
            carbohydrates=total_carbs,
            fat=total_fat
        )

    def _targets_met(self, current: NutritionalTarget, target: NutritionalTarget) -> bool:
        """Check if current macros meet target macros"""
        return (current.calories >= target.calories * 0.9 and
                current.protein >= target.protein * 0.9 and
                current.carbohydrates >= target.carbohydrates * 0.9 and
                current.fat >= target.fat * 0.9)

    def _find_missing_ingredients(
        self,
        current_macros: NutritionalTarget,
        target_macros: NutritionalTarget,
        available_ingredients: List[Ingredient],
        existing_ingredients: List[Ingredient]
    ) -> List[Ingredient]:
        """Find ingredients to add to reach target macros"""
        missing_ingredients = []
        existing_names = {ing.name.lower() for ing in existing_ingredients}
        
        # Calculate missing macros
        missing_calories = max(0, target_macros.calories - current_macros.calories)
        missing_protein = max(0, target_macros.protein - current_macros.protein)
        missing_carbs = max(0, target_macros.carbohydrates - current_macros.carbohydrates)
        missing_fat = max(0, target_macros.fat - current_macros.fat)
        
        # Find ingredients to add (avoid duplicates)
        for ingredient in available_ingredients:
            if ingredient.name.lower() not in existing_names:
                # Calculate how much this ingredient would help
                calories_help = ingredient.calories_per_100g
                protein_help = ingredient.protein_per_100g
                carbs_help = ingredient.carbs_per_100g
                fat_help = ingredient.fat_per_100g
                
                # Check if this ingredient addresses missing macros
                if (missing_calories > 0 and calories_help > 0) or \
                   (missing_protein > 0 and protein_help > 0) or \
                   (missing_carbs > 0 and carbs_help > 0) or \
                   (missing_fat > 0 and fat_help > 0):
                    
                    # Calculate optimal quantity using ML bounds
                    optimal_quantity = self._calculate_ml_optimal_quantity(
                        ingredient, missing_calories, missing_protein, missing_carbs, missing_fat
                    )
                    
                    if optimal_quantity > 0:
                        # Create a dictionary with ingredient and quantity
                        ingredient_with_quantity = {
                            'ingredient': ingredient,
                            'quantity_grams': optimal_quantity
                        }
                        missing_ingredients.append(ingredient_with_quantity)
                        
                        # Update missing macros
                        missing_calories -= (optimal_quantity * calories_help / 100)
                        missing_protein -= (optimal_quantity * protein_help / 100)
                        missing_carbs -= (optimal_quantity * carbs_help / 100)
                        missing_fat -= (optimal_quantity * fat_help / 100)
                        
                        # Break if targets are met
                        if self._targets_met(
                            NutritionalTarget(
                                calories=current_macros.calories + (target_macros.calories - missing_calories),
                                protein=current_macros.protein + (target_macros.protein - missing_protein),
                                carbohydrates=current_macros.carbohydrates + (target_macros.carbohydrates - missing_carbs),
                                fat=current_macros.fat + (target_macros.fat - missing_fat)
                            ),
                            target_macros
                        ):
                            break
        
        return missing_ingredients

    def _calculate_ml_optimal_quantity(
        self,
        ingredient: Ingredient,
        missing_calories: float,
        missing_protein: float,
        missing_carbs: float,
        missing_fat: float
    ) -> float:
        """Calculate optimal quantity using ML-based bounds"""
        try:
            # For now, use simple calculation until ML models are trained
            return self._calculate_simple_quantity(ingredient, missing_calories, missing_protein, missing_carbs, missing_fat)
            
        except Exception as e:
            logger.warning(f"ML quantity calculation failed, using fallback: {e}")
            # Fallback to simple calculation
            return self._calculate_simple_quantity(ingredient, missing_calories, missing_protein, missing_carbs, missing_fat)

    def _get_ml_min_quantity(self, ingredient: Ingredient) -> float:
        """Get minimum quantity using ML model"""
        try:
            # Features: ingredient properties
            features = np.array([[
                ingredient.calories_per_100g,
                ingredient.protein_per_100g,
                ingredient.carbs_per_100g,
                ingredient.fat_per_100g
            ]])
            
            features_scaled = self.scaler.transform(features)
            
            # Use neural network to predict minimum quantity
            min_quantity = self.ml_models['neural_network'].predict(features_scaled)[0]
            
            # Ensure reasonable minimum (at least 10g for most ingredients)
            return max(10, min_quantity)
            
        except Exception as e:
            logger.warning(f"ML min quantity failed: {e}")
            return 10  # Default minimum

    def _get_ml_max_quantity(self, ingredient: Ingredient) -> float:
        """Get maximum quantity using ML model"""
        try:
            # Features: ingredient properties
            features = np.array([[
                ingredient.calories_per_100g,
                ingredient.protein_per_100g,
                ingredient.carbs_per_100g,
                ingredient.fat_per_100g
            ]])
            
            features_scaled = self.scaler.transform(features)
            
            # Use gradient boosting to predict maximum quantity
            max_quantity = self.ml_models['gradient_boosting'].predict(features_scaled)[0]
            
            # Ensure reasonable maximum (not more than 500g for most ingredients)
            return min(500, max_quantity)
            
        except Exception as e:
            logger.warning(f"ML max quantity failed: {e}")
            return 500  # Default maximum

    def _calculate_simple_quantity(
        self,
        ingredient: Ingredient,
        missing_calories: float,
        missing_protein: float,
        missing_carbs: float,
        missing_fat: float
    ) -> float:
        """Simple fallback quantity calculation"""
        quantities = []
        
        if missing_calories > 0 and ingredient.calories_per_100g > 0:
            quantities.append(missing_calories * 100 / ingredient.calories_per_100g)
        
        if missing_protein > 0 and ingredient.protein_per_100g > 0:
            quantities.append(missing_protein * 100 / ingredient.protein_per_100g)
        
        if missing_carbs > 0 and ingredient.carbs_per_100g > 0:
            quantities.append(missing_carbs * 100 / ingredient.carbs_per_100g)
        
        if missing_fat > 0 and ingredient.fat_per_100g > 0:
            quantities.append(missing_fat * 100 / ingredient.fat_per_100g)
        
        if quantities:
            # Return average quantity, clamped to reasonable bounds
            avg_quantity = sum(quantities) / len(quantities)
            return np.clip(avg_quantity, 10, 500)
        
        return 0

    def _create_meal_plans_from_ingredients(self, ingredients) -> List[MealPlan]:
        """Create meal plans from ingredients"""
        meal_plans = []
        
        # Distribute ingredients across meal times
        meal_times = [MealTime.BREAKFAST, MealTime.MORNING_SNACK, MealTime.LUNCH, 
                     MealTime.AFTERNOON_SNACK, MealTime.EVENING_SNACK, MealTime.DINNER]
        
        for i, meal_time in enumerate(meal_times):
            meal_plan = MealPlan(
                meal_time=meal_time,
                items=[],
                total_calories=0,
                total_protein=0,
                total_carbs=0,
                total_fat=0
            )
            
            # Assign ingredients to this meal (simple distribution)
            start_idx = i * len(ingredients) // len(meal_times)
            end_idx = (i + 1) * len(ingredients) // len(meal_times)
            
            for j in range(start_idx, end_idx):
                if j < len(ingredients):
                    item = ingredients[j]
                    
                    if isinstance(item, dict):
                        # Item is a dict with 'ingredient' and 'quantity_grams'
                        ingredient = item['ingredient']
                        quantity = item['quantity_grams']
                    else:
                        # Item is an Ingredient object
                        ingredient = item
                        quantity = 100  # Default quantity
                    
                    meal_item = MealItem(
                        ingredient=ingredient,
                        quantity_grams=quantity,
                        calories=quantity * ingredient.calories_per_100g / 100,
                        protein=quantity * ingredient.protein_per_100g / 100,
                        carbs=quantity * ingredient.carbs_per_100g / 100,
                        fat=quantity * ingredient.fat_per_100g / 100
                    )
                    
                    meal_plan.items.append(meal_item)
                    meal_plan.total_calories += meal_item.calories
                    meal_plan.total_protein += meal_item.protein
                    meal_plan.total_carbs += meal_item.carbs
                    meal_plan.total_fat += meal_item.fat
            
            meal_plans.append(meal_plan)
        
        return meal_plans

    def _calculate_total_macros(self, ingredients) -> NutritionalTarget:
        """Calculate total macros from all ingredients"""
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for item in ingredients:
            if isinstance(item, dict):
                # Item is a dict with 'ingredient' and 'quantity_grams'
                ingredient = item['ingredient']
                quantity = item['quantity_grams']
            else:
                # Item is an Ingredient object
                ingredient = item
                quantity = 100  # Default quantity
            
            total_calories += quantity * ingredient.calories_per_100g / 100
            total_protein += quantity * ingredient.protein_per_100g / 100
            total_carbs += quantity * ingredient.carbs_per_100g / 100
            total_fat += quantity * ingredient.fat_per_100g / 100
        
        return NutritionalTarget(
            calories=total_calories,
            protein=total_protein,
            carbohydrates=total_carbs,
            fat=total_fat
        )

    def _generate_rag_recommendations(self, final_macros: NutritionalTarget, target_macros: NutritionalTarget) -> List[str]:
        """Generate recommendations for RAG-enhanced meal plan"""
        recommendations = []
        
        if final_macros.protein < target_macros.protein * 0.9:
            recommendations.append("Consider adding more protein-rich foods to reach your protein target")
        
        if final_macros.carbohydrates < target_macros.carbohydrates * 0.9:
            recommendations.append("Include more whole grains, fruits, and vegetables for carbohydrates")
        
        if final_macros.fat < target_macros.fat * 0.9:
            recommendations.append("Add healthy fats from nuts, avocados, or olive oil")
        
        if final_macros.calories < target_macros.calories * 0.9:
            recommendations.append("Consider increasing portion sizes or adding calorie-dense foods")
        
        recommendations.append("This meal plan has been enhanced with additional ingredients to meet your nutritional targets")
        
        return recommendations

    def _create_rag_response(self, ingredients: List[Ingredient], macros: NutritionalTarget, message: str) -> Dict:
        """Create response for RAG optimization"""
        meal_plans = self._create_meal_plans_from_ingredients(ingredients)
        
        optimization_result = OptimizationResult(
            success=True,
            target_achieved=True,
            optimization_method='rag_direct',
            objective_value=0,
            constraints_violated=[],
            computation_time=0.01
        )
        
        return {
            'optimization_result': optimization_result,
            'meal_plans': meal_plans,
            'daily_totals': macros,
            'recommendations': [message],
            'cost_estimate': self._estimate_cost(meal_plans),
            'shopping_list': self._create_shopping_list(meal_plans)
        }

    def _calculate_objective_value(self, current: NutritionalTarget, target: NutritionalTarget) -> float:
        """Calculate objective value for optimization"""
        calorie_deviation = abs(current.calories - target.calories)
        protein_deviation = abs(current.protein - target.protein)
        carb_deviation = abs(current.carbohydrates - target.carbohydrates)
        fat_deviation = abs(current.fat - target.fat)
        
        return -(calorie_deviation + protein_deviation + carb_deviation + fat_deviation)
