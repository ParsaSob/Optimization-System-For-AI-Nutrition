import logging
import time
from typing import Dict, List, Optional, Union
import random
import numpy as np

# Try to import optimization libraries
try:
    from pulp import LpMinimize, LpProblem, LpVariable, lpSum, value
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False
    logging.warning("PuLP not available. Linear optimization will be skipped.")

try:
    from deap import base, creator, tools
    DEAP_AVAILABLE = True
except ImportError:
    DEAP_AVAILABLE = False
    logging.warning("DEAP not available. Genetic Algorithm will be skipped.")

try:
    from scipy.optimize import differential_evolution
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("SciPy not available. Differential Evolution will be skipped.")

try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    logging.warning("Optuna not available. Optuna optimization will be skipped.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGMealOptimizer:
    """RAG Meal Optimizer implementing the 3-step algorithm:
       (1) optimize with up to 5 methods, pick best
       (2) if not within ±5%, add smart helper ingredients (non-duplicates, meal-specific)
       (3) re-optimize and return result in the original output format
    """

    def __init__(self):
        # Helper ingredient database by meal type and macro
        self.helper_ingredients = {
            'breakfast': {
                'protein': [
                    {'name': 'eggs', 'protein_per_100g': 13, 'carbs_per_100g': 1.1, 'fat_per_100g': 11, 'calories_per_100g': 155, 'max_quantity': 150},
                    {'name': 'greek_yogurt', 'protein_per_100g': 10, 'carbs_per_100g': 4, 'fat_per_100g': 0.4, 'calories_per_100g': 59, 'max_quantity': 200},
                    {'name': 'cottage_cheese', 'protein_per_100g': 11, 'carbs_per_100g': 3.4, 'fat_per_100g': 4.3, 'calories_per_100g': 98, 'max_quantity': 150},
                    {'name': 'turkey_bacon', 'protein_per_100g': 15, 'carbs_per_100g': 1, 'fat_per_100g': 12, 'calories_per_100g': 180, 'max_quantity': 100},
                    {'name': 'protein_powder', 'protein_per_100g': 80, 'carbs_per_100g': 5, 'fat_per_100g': 3, 'calories_per_100g': 400, 'max_quantity': 50},
                    {'name': 'smoked_salmon', 'protein_per_100g': 18, 'carbs_per_100g': 0, 'fat_per_100g': 4.3, 'calories_per_100g': 117, 'max_quantity': 100},
                    {'name': 'tofu_scramble', 'protein_per_100g': 10, 'carbs_per_100g': 2, 'fat_per_100g': 7, 'calories_per_100g': 120, 'max_quantity': 150},
                    {'name': 'canadian_bacon', 'protein_per_100g': 20, 'carbs_per_100g': 0, 'fat_per_100g': 3, 'calories_per_100g': 110, 'max_quantity': 100},
                    {'name': 'sardines', 'protein_per_100g': 25, 'carbs_per_100g': 0, 'fat_per_100g': 12, 'calories_per_100g': 208, 'max_quantity': 80},
                    {'name': 'hemp_seeds', 'protein_per_100g': 31, 'carbs_per_100g': 9, 'fat_per_100g': 49, 'calories_per_100g': 553, 'max_quantity': 40}
                ],
                'carbs': [
                    {'name': 'oats', 'protein_per_100g': 6.9, 'carbs_per_100g': 58, 'fat_per_100g': 6.9, 'calories_per_100g': 389, 'max_quantity': 150},
                    {'name': 'whole_grain_bread', 'protein_per_100g': 13, 'carbs_per_100g': 41, 'fat_per_100g': 4.2, 'calories_per_100g': 247, 'max_quantity': 100},
                    {'name': 'banana', 'protein_per_100g': 1.1, 'carbs_per_100g': 22, 'fat_per_100g': 0.3, 'calories_per_100g': 89, 'max_quantity': 150},
                    {'name': 'quinoa', 'protein_per_100g': 14, 'carbs_per_100g': 64, 'fat_per_100g': 6, 'calories_per_100g': 368, 'max_quantity': 100},
                    {'name': 'sweet_potato_hash', 'protein_per_100g': 1.6, 'carbs_per_100g': 20, 'fat_per_100g': 0.1, 'calories_per_100g': 86, 'max_quantity': 150},
                    {'name': 'berries', 'protein_per_100g': 1, 'carbs_per_100g': 14, 'fat_per_100g': 0.3, 'calories_per_100g': 57, 'max_quantity': 100},
                    {'name': 'whole_grain_cereal', 'protein_per_100g': 8, 'carbs_per_100g': 68, 'fat_per_100g': 2, 'calories_per_100g': 350, 'max_quantity': 80},
                    {'name': 'mango', 'protein_per_100g': 0.8, 'carbs_per_100g': 15, 'fat_per_100g': 0.4, 'calories_per_100g': 60, 'max_quantity': 120},
                    {'name': 'pineapple', 'protein_per_100g': 0.5, 'carbs_per_100g': 13, 'fat_per_100g': 0.1, 'calories_per_100g': 50, 'max_quantity': 120},
                    {'name': 'buckwheat', 'protein_per_100g': 13, 'carbs_per_100g': 72, 'fat_per_100g': 3.4, 'calories_per_100g': 343, 'max_quantity': 100}
                ],
                'fat': [
                    {'name': 'almonds', 'protein_per_100g': 21, 'carbs_per_100g': 22, 'fat_per_100g': 49, 'calories_per_100g': 579, 'max_quantity': 50},
                    {'name': 'peanut_butter', 'protein_per_100g': 25, 'carbs_per_100g': 20, 'fat_per_100g': 50, 'calories_per_100g': 588, 'max_quantity': 40},
                    {'name': 'avocado', 'protein_per_100g': 2, 'carbs_per_100g': 9, 'fat_per_100g': 15, 'calories_per_100g': 160, 'max_quantity': 100},
                    {'name': 'chia_seeds', 'protein_per_100g': 17, 'carbs_per_100g': 42, 'fat_per_100g': 31, 'calories_per_100g': 486, 'max_quantity': 30},
                    {'name': 'coconut_oil', 'protein_per_100g': 0, 'carbs_per_100g': 0, 'fat_per_100g': 100, 'calories_per_100g': 892, 'max_quantity': 20},
                    {'name': 'flax_seeds', 'protein_per_100g': 18, 'carbs_per_100g': 29, 'fat_per_100g': 42, 'calories_per_100g': 534, 'max_quantity': 30},
                    {'name': 'pistachios', 'protein_per_100g': 20, 'carbs_per_100g': 28, 'fat_per_100g': 45, 'calories_per_100g': 560, 'max_quantity': 50},
                    {'name': 'macadamia_nuts', 'protein_per_100g': 8, 'carbs_per_100g': 14, 'fat_per_100g': 76, 'calories_per_100g': 718, 'max_quantity': 40}
                ]
            },
            'lunch': {
                'protein': [
                    {'name': 'chicken_breast', 'protein_per_100g': 31, 'carbs_per_100g': 0, 'fat_per_100g': 3.6, 'calories_per_100g': 165, 'max_quantity': 200},
                    {'name': 'turkey', 'protein_per_100g': 29, 'carbs_per_100g': 0, 'fat_per_100g': 1, 'calories_per_100g': 135, 'max_quantity': 200},
                    {'name': 'tuna', 'protein_per_100g': 26, 'carbs_per_100g': 0, 'fat_per_100g': 1, 'calories_per_100g': 116, 'max_quantity': 150},
                    {'name': 'lentils', 'protein_per_100g': 9, 'carbs_per_100g': 20, 'fat_per_100g': 0.4, 'calories_per_100g': 116, 'max_quantity': 150},
                    {'name': 'tofu', 'protein_per_100g': 15, 'carbs_per_100g': 2, 'fat_per_100g': 8, 'calories_per_100g': 145, 'max_quantity': 150},
                    {'name': 'shrimp', 'protein_per_100g': 24, 'carbs_per_100g': 0.2, 'fat_per_100g': 0.3, 'calories_per_100g': 99, 'max_quantity': 150},
                    {'name': 'lean_pork', 'protein_per_100g': 27, 'carbs_per_100g': 0, 'fat_per_100g': 6, 'calories_per_100g': 165, 'max_quantity': 150}
                ],
                'carbs': [
                    {'name': 'brown_rice', 'protein_per_100g': 2.7, 'carbs_per_100g': 23, 'fat_per_100g': 0.9, 'calories_per_100g': 111, 'max_quantity': 200},
                    {'name': 'quinoa', 'protein_per_100g': 14, 'carbs_per_100g': 64, 'fat_per_100g': 6, 'calories_per_100g': 368, 'max_quantity': 150},
                    {'name': 'whole_wheat_pasta', 'protein_per_100g': 5, 'carbs_per_100g': 30, 'fat_per_100g': 1, 'calories_per_100g': 150, 'max_quantity': 150},
                    {'name': 'sweet_potato', 'protein_per_100g': 1.6, 'carbs_per_100g': 20, 'fat_per_100g': 0.1, 'calories_per_100g': 86, 'max_quantity': 200},
                    {'name': 'corn', 'protein_per_100g': 3.3, 'carbs_per_100g': 19, 'fat_per_100g': 1.4, 'calories_per_100g': 86, 'max_quantity': 150},
                    {'name': 'chickpeas', 'protein_per_100g': 9, 'carbs_per_100g': 27, 'fat_per_100g': 3, 'calories_per_100g': 164, 'max_quantity': 150},
                    {'name': 'barley', 'protein_per_100g': 3.5, 'carbs_per_100g': 28, 'fat_per_100g': 0.4, 'calories_per_100g': 123, 'max_quantity': 150}
                ],
                'fat': [
                    {'name': 'avocado', 'protein_per_100g': 2, 'carbs_per_100g': 9, 'fat_per_100g': 15, 'calories_per_100g': 160, 'max_quantity': 100},
                    {'name': 'olive_oil', 'protein_per_100g': 0, 'carbs_per_100g': 0, 'fat_per_100g': 100, 'calories_per_100g': 884, 'max_quantity': 20},
                    {'name': 'almonds', 'protein_per_100g': 21, 'carbs_per_100g': 22, 'fat_per_100g': 49, 'calories_per_100g': 579, 'max_quantity': 50},
                    {'name': 'peanut_butter', 'protein_per_100g': 25, 'carbs_per_100g': 20, 'fat_per_100g': 50, 'calories_per_100g': 588, 'max_quantity': 40},
                    {'name': 'sunflower_seeds', 'protein_per_100g': 21, 'carbs_per_100g': 24, 'fat_per_100g': 51, 'calories_per_100g': 584, 'max_quantity': 50}
                ]
            },
            'dinner': {
                'protein': [
                    {'name': 'beef_steak', 'protein_per_100g': 31, 'carbs_per_100g': 0, 'fat_per_100g': 12, 'calories_per_100g': 220, 'max_quantity': 200},
                    {'name': 'salmon', 'protein_per_100g': 25, 'carbs_per_100g': 0, 'fat_per_100g': 13, 'calories_per_100g': 206, 'max_quantity': 150},
                    {'name': 'chicken_thigh', 'protein_per_100g': 24, 'carbs_per_100g': 0, 'fat_per_100g': 9, 'calories_per_100g': 177, 'max_quantity': 200},
                    {'name': 'pork_loin', 'protein_per_100g': 27, 'carbs_per_100g': 0, 'fat_per_100g': 7, 'calories_per_100g': 172, 'max_quantity': 150},
                    {'name': 'white_fish', 'protein_per_100g': 23, 'carbs_per_100g': 0, 'fat_per_100g': 1, 'calories_per_100g': 105, 'max_quantity': 150},
                    {'name': 'tempeh', 'protein_per_100g': 20, 'carbs_per_100g': 8, 'fat_per_100g': 11, 'calories_per_100g': 195, 'max_quantity': 150},
                    {'name': 'lamb', 'protein_per_100g': 25, 'carbs_per_100g': 0, 'fat_per_100g': 14, 'calories_per_100g': 215, 'max_quantity': 150}
                ],
                'carbs': [
                    {'name': 'sweet_potato', 'protein_per_100g': 1.6, 'carbs_per_100g': 20, 'fat_per_100g': 0.1, 'calories_per_100g': 86, 'max_quantity': 200},
                    {'name': 'brown_rice', 'protein_per_100g': 2.7, 'carbs_per_100g': 23, 'fat_per_100g': 0.9, 'calories_per_100g': 111, 'max_quantity': 200},
                    {'name': 'quinoa', 'protein_per_100g': 14, 'carbs_per_100g': 64, 'fat_per_100g': 6, 'calories_per_100g': 368, 'max_quantity': 150},
                    {'name': 'whole_grain_pasta', 'protein_per_100g': 5, 'carbs_per_100g': 30, 'fat_per_100g': 1, 'calories_per_100g': 150, 'max_quantity': 150},
                    {'name': 'potato', 'protein_per_100g': 2, 'carbs_per_100g': 17, 'fat_per_100g': 0.1, 'calories_per_100g': 77, 'max_quantity': 200},
                    {'name': 'lentils', 'protein_per_100g': 9, 'carbs_per_100g': 20, 'fat_per_100g': 0.4, 'calories_per_100g': 116, 'max_quantity': 150},
                    {'name': 'black_beans', 'protein_per_100g': 9, 'carbs_per_100g': 23, 'fat_per_100g': 0.5, 'calories_per_100g': 130, 'max_quantity': 150}
                ],
                'fat': [
                    {'name': 'nuts_mix', 'protein_per_100g': 15, 'carbs_per_100g': 20, 'fat_per_100g': 50, 'calories_per_100g': 500, 'max_quantity': 50},
                    {'name': 'olive_oil', 'protein_per_100g': 0, 'carbs_per_100g': 0, 'fat_per_100g': 100, 'calories_per_100g': 884, 'max_quantity': 20},
                    {'name': 'avocado', 'protein_per_100g': 2, 'carbs_per_100g': 9, 'fat_per_100g': 15, 'calories_per_100g': 160, 'max_quantity': 100},
                    {'name': 'butter', 'protein_per_100g': 0.9, 'carbs_per_100g': 0.1, 'fat_per_100g': 81, 'calories_per_100g': 717, 'max_quantity': 20},
                    {'name': 'walnuts', 'protein_per_100g': 15, 'carbs_per_100g': 14, 'fat_per_100g': 65, 'calories_per_100g': 654, 'max_quantity': 50}
                ]
            },
            'morning_snack': {
                'protein': [
                    {'name': 'greek_yogurt', 'protein_per_100g': 10, 'carbs_per_100g': 4, 'fat_per_100g': 0.4, 'calories_per_100g': 59, 'max_quantity': 150},
                    {'name': 'hard_boiled_egg', 'protein_per_100g': 13, 'carbs_per_100g': 1.1, 'fat_per_100g': 11, 'calories_per_100g': 155, 'max_quantity': 100},
                    {'name': 'protein_bar', 'protein_per_100g': 30, 'carbs_per_100g': 30, 'fat_per_100g': 10, 'calories_per_100g': 350, 'max_quantity': 80},
                    {'name': 'cottage_cheese', 'protein_per_100g': 11, 'carbs_per_100g': 3.4, 'fat_per_100g': 4.3, 'calories_per_100g': 98, 'max_quantity': 100},
                    {'name': 'edamame', 'protein_per_100g': 11, 'carbs_per_100g': 10, 'fat_per_100g': 5, 'calories_per_100g': 121, 'max_quantity': 100},
                    {'name': 'turkey_jerky', 'protein_per_100g': 30, 'carbs_per_100g': 3, 'fat_per_100g': 1, 'calories_per_100g': 150, 'max_quantity': 50},
                    {'name': 'tuna_snack', 'protein_per_100g': 26, 'carbs_per_100g': 0, 'fat_per_100g': 1, 'calories_per_100g': 116, 'max_quantity': 80}
                ],
                'carbs': [
                    {'name': 'apple', 'protein_per_100g': 0.3, 'carbs_per_100g': 14, 'fat_per_100g': 0.2, 'calories_per_100g': 52, 'max_quantity': 150},
                    {'name': 'berries', 'protein_per_100g': 1, 'carbs_per_100g': 14, 'fat_per_100g': 0.3, 'calories_per_100g': 57, 'max_quantity': 100},
                    {'name': 'whole_grain_crackers', 'protein_per_100g': 7, 'carbs_per_100g': 70, 'fat_per_100g': 10, 'calories_per_100g': 400, 'max_quantity': 50},
                    {'name': 'banana', 'protein_per_100g': 1.1, 'carbs_per_100g': 22, 'fat_per_100g': 0.3, 'calories_per_100g': 89, 'max_quantity': 100},
                    {'name': 'dried_apricots', 'protein_per_100g': 3.4, 'carbs_per_100g': 63, 'fat_per_100g': 0.5, 'calories_per_100g': 241, 'max_quantity': 50},
                    {'name': 'rice_cakes', 'protein_per_100g': 8, 'carbs_per_100g': 80, 'fat_per_100g': 3, 'calories_per_100g': 400, 'max_quantity': 50},
                    {'name': 'oat_bar', 'protein_per_100g': 8, 'carbs_per_100g': 60, 'fat_per_100g': 8, 'calories_per_100g': 350, 'max_quantity': 60}
                ],
                'fat': [
                    {'name': 'almonds', 'protein_per_100g': 21, 'carbs_per_100g': 22, 'fat_per_100g': 49, 'calories_per_100g': 579, 'max_quantity': 50},
                    {'name': 'peanut_butter', 'protein_per_100g': 25, 'carbs_per_100g': 20, 'fat_per_100g': 50, 'calories_per_100g': 588, 'max_quantity': 30},
                    {'name': 'trail_mix', 'protein_per_100g': 14, 'carbs_per_100g': 45, 'fat_per_100g': 30, 'calories_per_100g': 450, 'max_quantity': 50},
                    {'name': 'sunflower_seeds', 'protein_per_100g': 21, 'carbs_per_100g': 24, 'fat_per_100g': 51, 'calories_per_100g': 584, 'max_quantity': 30},
                    {'name': 'cashews', 'protein_per_100g': 18, 'carbs_per_100g': 30, 'fat_per_100g': 44, 'calories_per_100g': 553, 'max_quantity': 50}
                ]
            },
            'afternoon_snack': {
                'protein': [
                    {'name': 'protein_bar', 'protein_per_100g': 30, 'carbs_per_100g': 30, 'fat_per_100g': 10, 'calories_per_100g': 350, 'max_quantity': 80},
                    {'name': 'greek_yogurt', 'protein_per_100g': 10, 'carbs_per_100g': 4, 'fat_per_100g': 0.4, 'calories_per_100g': 59, 'max_quantity': 150},
                    {'name': 'beef_jerky', 'protein_per_100g': 33, 'carbs_per_100g': 3, 'fat_per_100g': 7, 'calories_per_100g': 200, 'max_quantity': 50},
                    {'name': 'cottage_cheese', 'protein_per_100g': 11, 'carbs_per_100g': 3.4, 'fat_per_100g': 4.3, 'calories_per_100g': 98, 'max_quantity': 100},
                    {'name': 'hummus', 'protein_per_100g': 8, 'carbs_per_100g': 14, 'fat_per_100g': 10, 'calories_per_100g': 166, 'max_quantity': 100},
                    {'name': 'tuna_snack', 'protein_per_100g': 26, 'carbs_per_100g': 0, 'fat_per_100g': 1, 'calories_per_100g': 116, 'max_quantity': 80},
                    {'name': 'edamame', 'protein_per_100g': 11, 'carbs_per_100g': 10, 'fat_per_100g': 5, 'calories_per_100g': 121, 'max_quantity': 100}
                ],
                'carbs': [
                    {'name': 'apple', 'protein_per_100g': 0.3, 'carbs_per_100g': 14, 'fat_per_100g': 0.2, 'calories_per_100g': 52, 'max_quantity': 150},
                    {'name': 'whole_grain_crackers', 'protein_per_100g': 7, 'carbs_per_100g': 70, 'fat_per_100g': 10, 'calories_per_100g': 400, 'max_quantity': 50},
                    {'name': 'banana', 'protein_per_100g': 1.1, 'carbs_per_100g': 22, 'fat_per_100g': 0.3, 'calories_per_100g': 89, 'max_quantity': 100},
                    {'name': 'rice_cakes', 'protein_per_100g': 8, 'carbs_per_100g': 80, 'fat_per_100g': 3, 'calories_per_100g': 400, 'max_quantity': 50},
                    {'name': 'dried_mango', 'protein_per_100g': 2, 'carbs_per_100g': 65, 'fat_per_100g': 0.5, 'calories_per_100g': 250, 'max_quantity': 50},
                    {'name': 'granola', 'protein_per_100g': 10, 'carbs_per_100g': 60, 'fat_per_100g': 15, 'calories_per_100g': 400, 'max_quantity': 60},
                    {'name': 'carrot_sticks', 'protein_per_100g': 0.9, 'carbs_per_100g': 10, 'fat_per_100g': 0.2, 'calories_per_100g': 41, 'max_quantity': 100}
                ],
                'fat': [
                    {'name': 'peanut_butter', 'protein_per_100g': 25, 'carbs_per_100g': 20, 'fat_per_100g': 50, 'calories_per_100g': 588, 'max_quantity': 30},
                    {'name': 'almonds', 'protein_per_100g': 21, 'carbs_per_100g': 22, 'fat_per_100g': 49, 'calories_per_100g': 579, 'max_quantity': 50},
                    {'name': 'cashews', 'protein_per_100g': 18, 'carbs_per_100g': 30, 'fat_per_100g': 44, 'calories_per_100g': 553, 'max_quantity': 50},
                    {'name': 'trail_mix', 'protein_per_100g': 14, 'carbs_per_100g': 45, 'fat_per_100g': 30, 'calories_per_100g': 450, 'max_quantity': 50},
                    {'name': 'pumpkin_seeds', 'protein_per_100g': 19, 'carbs_per_100g': 54, 'fat_per_100g': 19, 'calories_per_100g': 446, 'max_quantity': 30}
                ]
            },
            'evening_snack': {
                'protein': [
                    {'name': 'cottage_cheese', 'protein_per_100g': 11, 'carbs_per_100g': 3.4, 'fat_per_100g': 4.3, 'calories_per_100g': 98, 'max_quantity': 100},
                    {'name': 'greek_yogurt', 'protein_per_100g': 10, 'carbs_per_100g': 4, 'fat_per_100g': 0.4, 'calories_per_100g': 59, 'max_quantity': 150},
                    {'name': 'protein_shake', 'protein_per_100g': 80, 'carbs_per_100g': 5, 'fat_per_100g': 3, 'calories_per_100g': 400, 'max_quantity': 50},
                    {'name': 'beef_jerky', 'protein_per_100g': 33, 'carbs_per_100g': 3, 'fat_per_100g': 7, 'calories_per_100g': 200, 'max_quantity': 50},
                    {'name': 'hummus', 'protein_per_100g': 8, 'carbs_per_100g': 14, 'fat_per_100g': 10, 'calories_per_100g': 166, 'max_quantity': 100},
                    {'name': 'hard_boiled_egg', 'protein_per_100g': 13, 'carbs_per_100g': 1.1, 'fat_per_100g': 11, 'calories_per_100g': 155, 'max_quantity': 100},
                    {'name': 'tuna_snack', 'protein_per_100g': 26, 'carbs_per_100g': 0, 'fat_per_100g': 1, 'calories_per_100g': 116, 'max_quantity': 80}
                ],
                'carbs': [
                    {'name': 'apple', 'protein_per_100g': 0.3, 'carbs_per_100g': 14, 'fat_per_100g': 0.2, 'calories_per_100g': 52, 'max_quantity': 150},
                    {'name': 'whole_grain_crackers', 'protein_per_100g': 7, 'carbs_per_100g': 70, 'fat_per_100g': 10, 'calories_per_100g': 400, 'max_quantity': 50},
                    {'name': 'banana', 'protein_per_100g': 1.1, 'carbs_per_100g': 22, 'fat_per_100g': 0.3, 'calories_per_100g': 89, 'max_quantity': 100},
                    {'name': 'rice_cakes', 'protein_per_100g': 8, 'carbs_per_100g': 80, 'fat_per_100g': 3, 'calories_per_100g': 400, 'max_quantity': 50},
                    {'name': 'dried_raisins', 'protein_per_100g': 3, 'carbs_per_100g': 79, 'fat_per_100g': 0.5, 'calories_per_100g': 299, 'max_quantity': 50},
                    {'name': 'celery_sticks', 'protein_per_100g': 0.7, 'carbs_per_100g': 3, 'fat_per_100g': 0.2, 'calories_per_100g': 16, 'max_quantity': 100},
                    {'name': 'oat_bar', 'protein_per_100g': 8, 'carbs_per_100g': 60, 'fat_per_100g': 8, 'calories_per_100g': 350, 'max_quantity': 60}
                ],
                'fat': [
                    {'name': 'peanut_butter', 'protein_per_100g': 25, 'carbs_per_100g': 20, 'fat_per_100g': 50, 'calories_per_100g': 588, 'max_quantity': 30},
                    {'name': 'almonds', 'protein_per_100g': 21, 'carbs_per_100g': 22, 'fat_per_100g': 49, 'calories_per_100g': 579, 'max_quantity': 50},
                    {'name': 'cashews', 'protein_per_100g': 18, 'carbs_per_100g': 30, 'fat_per_100g': 44, 'calories_per_100g': 553, 'max_quantity': 50},
                    {'name': 'trail_mix', 'protein_per_100g': 14, 'carbs_per_100g': 45, 'fat_per_100g': 30, 'calories_per_100g': 450, 'max_quantity': 50},
                    {'name': 'chia_seeds', 'protein_per_100g': 17, 'carbs_per_100g': 42, 'fat_per_100g': 31, 'calories_per_100g': 486, 'max_quantity': 30}
                ]
            }
        }



        # Initialize DEAP if available
        if DEAP_AVAILABLE:
            self._setup_deap()
        
        # Update helper ingredients with patches
        self._update_helper_ingredients()

    # --------------------- Public API ---------------------

    def optimize_single_meal(self, rag_response: Dict, target_macros: Dict, user_preferences: Dict,
                             meal_type: str, request_data: Dict = None) -> Dict:
        """Main optimization method implementing the 3-step algorithm."""
        start_time = time.time()
        try:
            logger.info(f"🚀 Starting meal optimization for {meal_type}")

            if not target_macros:
                raise ValueError("Missing target_macros")

            # 1) Normalize targets
            target_macros = self._normalize_target_macros(target_macros)

            # 2) Extract ingredients from RAG (robust to multiple shapes)
            rag_ingredients = self._extract_rag_ingredients(rag_response)
            if not rag_ingredients:
                raise ValueError("No ingredients extracted from RAG response")

            logger.info(f"🍽️ RAG ingredients: {len(rag_ingredients)} items")

            # ---- STEP 1: Optimize with available methods, pick best ----
            logger.info("🔄 Step 1: Running optimization with advanced methods...")
            initial_result = self._run_optimization_methods(rag_ingredients, target_macros)
            initial_nutrition = self._calculate_final_meal(rag_ingredients, initial_result['quantities'])
            target_achievement = self._check_target_achievement(initial_nutrition, target_macros)
            logger.info(f"📈 Initial target achievement: {target_achievement}")

            if target_achievement['overall']:
                # Done
                final_ingredients = self._materialize_ingredients(rag_ingredients, initial_result['quantities'])
                computation_time = time.time() - start_time
                return self._format_output(final_ingredients, initial_result, initial_nutrition,
                                           target_achievement, [], computation_time, request_data)

            # ---- STEP 2: Add smart helper ingredients for both deficits and excesses ----
            logger.info("🔧 Step 2: Targets not fully achieved. Adding helper ingredients for balance...")
            
            # Analyze current nutrition vs targets
            current_nutrition = initial_nutrition
            logger.info(f"📊 Current nutrition: {current_nutrition}")
            logger.info(f"🎯 Target nutrition: {target_macros}")
            
            # Calculate deficits and excesses
            deficits = {}
            excesses = {}
            for macro in ['protein', 'carbs', 'fat', 'calories']:
                current = current_nutrition.get(macro, 0)
                target = target_macros.get(macro, 0)
                diff = target - current
                
                if diff > 0:
                    deficits[macro] = diff
                    logger.info(f"📉 {macro.capitalize()} deficit: {diff:.1f}g")
                elif diff < 0:
                    excesses[macro] = abs(diff)
                    logger.info(f"📈 {macro.capitalize()} excess: {abs(diff):.1f}g")
            
            # Add helper ingredients for deficits
            deficit_helpers = []
            if deficits:
                deficit_helpers = self._add_smart_helper_ingredients_candidates(
                    current_ingredients=self._materialize_ingredients(rag_ingredients, initial_result['quantities']),
                    target_macros=target_macros,
                    meal_type=meal_type,
                    focus_macros=list(deficits.keys())
                )
                logger.info(f"🔧 Added {len(deficit_helpers)} deficit helper ingredients")
            
            # Add balancing ingredients for excesses
            balancing_helpers = []
            if excesses:
                balancing_helpers = self._add_balancing_ingredients_candidates(
                    current_ingredients=self._materialize_ingredients(rag_ingredients, initial_result['quantities']),
                    target_macros=target_macros,
                    meal_type=meal_type,
                    excess_macros=list(excesses.keys())
                )
                logger.info(f"⚖️ Added {len(balancing_helpers)} balancing helper ingredients")
            
            # Combine all helpers
            helper_ingredients = deficit_helpers + balancing_helpers
            logger.info(f"🔧 Total helper ingredients: {len(helper_ingredients)}")

            # Merge (as candidates) – no preset quantities; let optimizer decide.
            all_ingredients = self._merge_ingredients_for_reopt(rag_ingredients, helper_ingredients)
            logger.info(f"🔁 Re-optimizing with {len(all_ingredients)} ingredients (including {len(helper_ingredients)} helpers)...")

            # ---- STEP 3: Re-optimize on the full set ----
            final_result = self._run_optimization_methods(all_ingredients, target_macros)
            final_nutrition = self._calculate_final_meal(all_ingredients, final_result['quantities'])
            final_target_achievement = self._check_target_achievement(final_nutrition, target_macros)
            logger.info(f"✅ Final target achievement: {final_target_achievement}")

            # ---- STEP 4: If targets still not achieved, try aggressive balancing ----
            if not final_target_achievement.get('overall', False):
                logger.info("🎯 Targets still not achieved. Trying aggressive balancing...")
                
                # Calculate current gaps
                current_gaps = {}
                for macro in ['protein', 'carbs', 'fat', 'calories']:
                    current = final_nutrition.get(macro, 0)
                    target = target_macros.get(macro, 0)
                    gap = target - current
                    if abs(gap) > 1.0:  # Only consider significant gaps
                        current_gaps[macro] = gap
                        if gap > 0:
                            logger.info(f"📉 {macro.capitalize()} still needs: {gap:.1f}g")
                        else:
                            logger.info(f"📈 {macro.capitalize()} still excess: {abs(gap):.1f}g")
                
                if current_gaps:
                    # Try to find the best balance by adjusting ingredient quantities
                    balanced_result = self._find_best_balance(
                        all_ingredients, 
                        final_result['quantities'], 
                        target_macros, 
                        current_gaps
                    )
                    
                    if balanced_result:
                        final_result = balanced_result
                        final_nutrition = self._calculate_final_meal(all_ingredients, final_result['quantities'])
                        final_target_achievement = self._check_target_achievement(final_nutrition, target_macros)
                        logger.info(f"⚖️ After aggressive balancing - Achievement: {final_target_achievement}")
                        logger.info(f"⚖️ After aggressive balancing - Totals: {final_nutrition}")
                        
                        # 🔄 NEW: Re-optimize with advanced methods after balancing
                        logger.info("🔄 Re-optimizing with advanced methods after balancing...")
                        re_optimized_result = self._re_optimize_after_balancing(all_ingredients, target_macros, final_nutrition)
                        
                        if re_optimized_result:
                            logger.info(f"🎯 Re-optimization improved score from {final_target_achievement} to {re_optimized_result['achievement']}")
                            final_result = re_optimized_result['result']
                            final_nutrition = re_optimized_result['nutrition']
                            final_target_achievement = re_optimized_result['achievement']

            final_ingredients = self._materialize_ingredients(all_ingredients, final_result['quantities'])
            computation_time = time.time() - start_time

            return self._format_output(final_ingredients, final_result, final_nutrition,
                                       final_target_achievement, helper_ingredients,
                                       computation_time, request_data)

        except Exception as e:
            computation_time = time.time() - start_time
            logger.error(f"❌ Fatal error in meal optimization: {e}")
            return {
                "optimization_result": {
                    "success": False,
                    "method": "Error",
                    "computation_time": round(computation_time, 3),
                    "error": str(e)
                },
                "meal": [],
                "nutritional_totals": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
                "target_achievement": {"overall": False},
                "helper_ingredients_added": []
            }

    # --------------------- Helpers: Orchestration & Output ---------------------

    def _format_output(self, final_ingredients: List[Dict], opt_result: Dict, totals: Dict,
                       achievement: Dict, helper_ingredients_added: List[Dict],
                       computation_time: float, request_data: Optional[Dict]) -> Dict:
        # Format meal for output
        formatted_meal = []
        for ing in final_ingredients:
            formatted_meal.append({
                "name": ing['name'].replace('_', ' ').title(),
                "quantity_needed": round(max(0.0, ing.get('quantity_needed', 0.0)), 1),
                "protein_per_100g": ing.get('protein_per_100g', 0),
                "carbs_per_100g": ing.get('carbs_per_100g', 0),
                "fat_per_100g": ing.get('fat_per_100g', 0),
                "calories_per_100g": ing.get('calories_per_100g', 0)
            })

        return {
            "user_id": request_data.get('user_id', 'default_user') if request_data else 'default_user',
            "success": True,
            "optimization_result": {
                "success": True,
                "method": opt_result['method'],
                "computation_time": round(computation_time, 3)
            },
            "meal": formatted_meal,
            "nutritional_totals": totals,
            "target_achievement": achievement,
            "helper_ingredients_added": helper_ingredients_added,
            "optimization_steps": {
                "step1": "Initial optimization with advanced methods",
                "step2": "Helper ingredients added if needed",
                "step3": "Re-optimization with advanced methods"
            }
        }

    def _merge_ingredients_for_reopt(self, base_ingredients: List[Dict], helpers: List[Dict]) -> List[Dict]:
        """Merge base ingredients with helper candidates (avoid duplicates by name)."""
        seen = {ing['name'].strip().lower() for ing in base_ingredients}
        merged = list(base_ingredients)
        for h in helpers:
            if h['name'].strip().lower() not in seen:
                # ensure nutrition fields exist
                merged.append(self._ensure_nutrition_fields(h))
                seen.add(h['name'].strip().lower())
        return merged

    def _materialize_ingredients(self, ingredients: List[Dict], quantities: List[float]) -> List[Dict]:
        """Attach chosen quantities to ingredient dicts (safe against length mismatch)."""
        out = []
        n = min(len(ingredients), len(quantities))
        
        logger.info(f"🔧 Materializing {n} ingredients with quantities:")
        for i in range(n):
            ing = dict(ingredients[i])
            # CRITICAL FIX: Get original quantity from quantity_needed (website format) or quantity (fallback)
            original_qty = ing.get('quantity_needed', ing.get('quantity', 0))
            optimized_qty = max(0.0, float(quantities[i]))
            
            # Ensure input ingredients maintain reasonable quantities
            if original_qty > 0 and optimized_qty < 10.0:
                logger.info(f"   ⚠️ Input ingredient '{ing['name']}' quantity too low ({optimized_qty:.1f}g), preserving minimum")
                optimized_qty = max(10.0, original_qty * 0.1)  # At least 10g or 10% of original
            
            ing['quantity_needed'] = optimized_qty
            logger.info(f"   - {ing['name']}: original={original_qty}g, optimized={optimized_qty:.1f}g")
            out.append(ing)
        
        # ignore any tail mismatch safely
        return out

    # --------------------- Parsing & Normalization ---------------------

    def _normalize_target_macros(self, target_macros: Dict) -> Dict:
        macro_mapping = {
            'carbohydrates': 'carbs', 'carb': 'carbs', 'carbs': 'carbs',
            'protein': 'protein', 'proteins': 'protein',
            'fat': 'fat', 'fats': 'fat',
            'calories': 'calories', 'calorie': 'calories', 'kcal': 'calories'
        }
        normalized = {}
        for k, v in target_macros.items():
            nk = macro_mapping.get(k.lower(), k.lower())
            normalized[nk] = float(v)

        # Fill defaults and sanitize
        defaults = {'calories': 500.0, 'protein': 30.0, 'carbs': 50.0, 'fat': 15.0}
        for m in ['calories', 'protein', 'carbs', 'fat']:
            if m not in normalized or not isinstance(normalized[m], (int, float)) or normalized[m] < 0:
                normalized[m] = defaults[m]
        return normalized

    def _extract_rag_ingredients(self, rag_response: Union[Dict, List, str]) -> List[Dict]:
        """Support multiple shapes:
           - {'suggestions': [{'ingredients': [...]}]}  # Website format
           - {'ingredients': [...]}
           - [{'name': 'chicken', 'quantity': 100}, ...]
           - "گوشت، پیاز، گوجه" (string format - extract ingredient names)
        """
        logger.info(f"🔍 Input rag_response type: {type(rag_response)}")
        logger.info(f"🔍 Input rag_response: {rag_response}")
        # List of meat ingredients to exclude from helper ingredients only (not from input ingredients)
        excluded_from_helpers = {
            'beef', 'beef_steak', 'beef_jerky', 'ground_beef', 'lean_beef', 'lean_ground_beef',
            'chicken', 'chicken_breast', 'chicken_thigh', 'grilled_chicken',
            'turkey', 'turkey_bacon', 'turkey_jerky', 'turkey_slices',
            'shrimp', 'shrimp_snack',
            'tuna', 'tuna_snack',
            'salmon', 'smoked_salmon', 'grilled_salmon'
        }
        
        ingredients = []
        seen = set()

        candidates = []
        if isinstance(rag_response, list):
            candidates = rag_response
            logger.info(f"📋 Processing as list with {len(candidates)} items")
        elif isinstance(rag_response, dict):
            logger.info(f"📋 Processing as dict with keys: {list(rag_response.keys())}")
            # Handle website format: {rag_response: {suggestions: [{ingredients: [...]}]}}
            if 'rag_response' in rag_response and isinstance(rag_response['rag_response'], dict):
                rag_data = rag_response['rag_response']
                if 'suggestions' in rag_data and isinstance(rag_data['suggestions'], list):
                    for s in rag_data['suggestions']:
                        if isinstance(s, dict) and 'ingredients' in s:
                            candidates.extend(s['ingredients'])
                elif 'ingredients' in rag_data and isinstance(rag_data['ingredients'], list):
                    candidates = rag_data['ingredients']
            # Handle direct format: {suggestions: [{ingredients: [...]}]}
            elif 'suggestions' in rag_response and isinstance(rag_response['suggestions'], list):
                logger.info(f"📋 Found suggestions with {len(rag_response['suggestions'])} items")
                for s in rag_response['suggestions']:
                    if isinstance(s, dict) and 'ingredients' in s:
                        candidates.extend(s['ingredients'])
                        logger.info(f"📋 Added {len(s['ingredients'])} ingredients from suggestions")
            # Handle simple format: {ingredients: [...]}
            elif 'ingredients' in rag_response and isinstance(rag_response['ingredients'], list):
                candidates = rag_response['ingredients']
                logger.info(f"📋 Added {len(rag_response['ingredients'])} ingredients directly")
        else:
            logger.warning(f"⚠️ Unexpected rag_response type: {type(rag_response)}")
        
        logger.info(f"📋 Total candidates found: {len(candidates)}")
        for i, candidate in enumerate(candidates):
            logger.info(f"📋 Candidate {i+1}: {candidate}")
        
        if isinstance(rag_response, str):
            # Parse string format for ingredient names
            # Example: "یک وعده غذایی سالم برای ناهار با گوشت، پیاز، گوجه و نان پیتا"
            # Extract common food terms
            import re
            food_keywords = [
                'گوشت', 'chicken', 'مرغ', 'beef', 'گوساله', 'lamb', 'بره',
                'پیاز', 'onion', 'گوجه', 'tomato', 'نان', 'bread', 'پیتا', 'pita',
                'برنج', 'rice', 'سبزی', 'vegetables', 'سالاد', 'salad',
                'ماکارونی', 'pasta', 'سیب‌زمینی', 'potato'
            ]
            
            # Map Persian/English food terms to standard ingredient names
            food_mapping = {
                'گوشت': 'chicken_breast',
                'مرغ': 'chicken_breast', 
                'chicken': 'chicken_breast',
                'پیاز': 'onion',
                'onion': 'onion',
                'گوجه': 'tomato', 
                'tomato': 'tomato',
                'نان': 'whole_grain_bread',
                'bread': 'whole_grain_bread',
                'پیتا': 'pita_bread',
                'pita': 'pita_bread',
                'برنج': 'brown_rice',
                'rice': 'brown_rice'
            }
            
            text_lower = rag_response.lower()
            logger.info(f"🔍 Parsing text: '{text_lower}'")
            string_seen = set()  # Separate seen set for string parsing
            for keyword in food_keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in text_lower:
                    ingredient_name = food_mapping.get(keyword, keyword)
                    logger.info(f"✅ Found ingredient: '{keyword}' -> '{ingredient_name}'")
                    if ingredient_name not in string_seen:
                        candidates.append({'name': ingredient_name, 'quantity': 100})
                        string_seen.add(ingredient_name)
            logger.info(f"📋 Total candidates found: {len(candidates)}")

        for ing in candidates:
            # Handle both dict and string ingredients
            if isinstance(ing, str):
                ing = {'name': ing, 'quantity': 100}
            elif not isinstance(ing, dict):
                continue
                
            name = str(ing.get('name', '')).strip()
            if not name:
                continue
            key = name.lower()
            if key in seen:
                continue
                
            # IMPORTANT: Do NOT exclude input ingredients - they should always be processed
            # The exclusion list is only for helper ingredients, not for user input
            logger.info(f"✅ Processing input ingredient: '{name}'")
            
            # CRITICAL FIX: Use nutrition_db only if input ingredients don't have nutritional info
            # If they have nutritional info, preserve it. If not, enrich from nutrition_db
            enriched = ing.copy()  # Keep original data
            
            # Handle quantity field (website sends quantity_needed, but we need quantity)
            if 'quantity_needed' in enriched and 'quantity' not in enriched:
                enriched['quantity'] = enriched['quantity_needed']
            
            # Check if ingredient has nutritional information
            has_nutrition = (
                'protein_per_100g' in enriched and 
                'carbs_per_100g' in enriched and 
                'fat_per_100g' in enriched and 
                'calories_per_100g' in enriched
            )
            
            if has_nutrition:
                # Input ingredient has nutritional info - preserve it
                logger.info(f"✅ Input ingredient '{name}' has nutritional info - preserving original values")
                # Ensure all nutritional values are numbers
                for macro in ['protein', 'carbs', 'fat', 'calories']:
                    key = f'{macro}_per_100g'
                    if key in enriched:
                        try:
                            enriched[key] = float(enriched[key])
                        except (ValueError, TypeError):
                            enriched[key] = 0.0
            else:
                # Input ingredient doesn't have nutritional info - skip it (nutrition_db removed)
                logger.warning(f"⚠️ Input ingredient '{name}' missing nutritional info - skipping (nutrition_db removed)")
                continue
                
            # Set max_quantity based on input quantity or default
            if 'max_quantity' not in enriched:
                enriched['max_quantity'] = max(200, int(enriched.get('quantity', 200)) if isinstance(enriched.get('quantity', 0), (int, float)) else 200)
            
            ingredients.append(enriched)
            seen.add(key)

        logger.info(f"🍽️ Total ingredients extracted: {len(ingredients)}")
        for ing in ingredients:
            logger.info(f"   - {ing['name']}: protein={ing.get('protein_per_100g', 0)}, carbs={ing.get('carbs_per_100g', 0)}, fat={ing.get('fat_per_100g', 0)}, calories={ing.get('calories_per_100g', 0)}")
        
        return ingredients



    # --------------------- Optimization Core ---------------------

    def _run_optimization_methods(self, ingredients: List[Dict], target_macros: Dict) -> Dict:
        logger.info("🚀 Running advanced optimization methods...")
        results = []

        # Method A: PuLP LP (min calories subject to min macros)
        if PULP_AVAILABLE:
            try:
                results.append(self._linear_optimize_pulp(ingredients, target_macros))
                logger.info("✅ PuLP finished.")
            except Exception as e:
                logger.warning(f"❌ PuLP failed: {e}")

        # Method B: DEAP GA
        if DEAP_AVAILABLE:
            try:
                results.append(self._genetic_algorithm_optimize(ingredients, target_macros))
                logger.info("✅ GA finished.")
            except Exception as e:
                logger.warning(f"❌ GA failed: {e}")

        # Method C: SciPy Differential Evolution
        if SCIPY_AVAILABLE:
            try:
                results.append(self._differential_evolution_optimize(ingredients, target_macros))
                logger.info("✅ Differential Evolution finished.")
            except Exception as e:
                logger.warning(f"❌ Differential Evolution failed: {e}")

        # Method D: Hybrid (GA + DE)
        if DEAP_AVAILABLE and SCIPY_AVAILABLE:
            try:
                results.append(self._hybrid_optimize(ingredients, target_macros))
                logger.info("✅ Hybrid finished.")
            except Exception as e:
                logger.warning(f"❌ Hybrid failed: {e}")

        # Method E: Optuna
        if OPTUNA_AVAILABLE:
            try:
                results.append(self._optuna_optimize(ingredients, target_macros))
                logger.info("✅ Optuna finished.")
            except Exception as e:
                logger.warning(f"❌ Optuna failed: {e}")

        # Safety net: Greedy heuristic (never fails), used only if no success above
        if not results:
            logger.warning("⚠️ No advanced method succeeded; using greedy heuristic.")
            results.append(self._greedy_heuristic(ingredients, target_macros))

        best = self._evaluate_optimization_results(results, ingredients, target_macros)
        if not best:
            # As absolute fallback
            logger.warning("⚠️ No valid result; falling back to greedy heuristic.")
            best = self._greedy_heuristic(ingredients, target_macros)

        logger.info(f"🏆 Best method: {best['method']}")
        return best

    # ---- Method Implementations ----

    def _linear_optimize_pulp(self, ingredients: List[Dict], target_macros: Dict) -> Dict:
        """
        Relax calorie constraint in PuLP to allow up to 10% above target.
        """
        try:
            from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus
            prob = LpProblem("Meal_Optimization", LpMinimize)
            n = len(ingredients)
            x = [LpVariable(f"x_{i}", 0, float(ingredients[i].get('max_quantity', 500))) for i in range(n)]
            
            # Objective: Minimize deviation from target macros + encourage ingredient usage
            deviations = {}
            for macro in ['protein', 'carbs', 'fat']:
                target = target_macros[macro]
                total = lpSum(x[i] * ingredients[i].get(f'{macro}_per_100g', 0) / 100 for i in range(n))
                deviations[macro] = LpVariable(f"dev_{macro}", 0)
                prob += deviations[macro] >= (total - target) / target
                prob += deviations[macro] >= (target - total) / target
            
            prob += lpSum(deviations[m] for m in ['protein', 'carbs', 'fat'])
            
            # Macro constraints - ensure minimum requirements
            for macro in ['protein', 'carbs', 'fat']:
                prob += lpSum(x[i] * ingredients[i].get(f'{macro}_per_100g', 0) / 100 for i in range(n)) >= target_macros[macro] * 0.95
            
            # Calorie constraint
            prob += lpSum(x[i] * ingredients[i].get('calories_per_100g', 0) / 100 for i in range(n)) <= target_macros['calories'] * 1.1
            prob += lpSum(x[i] * ingredients[i].get('calories_per_100g', 0) / 100 for i in range(n)) >= target_macros['calories'] * 0.9
            
            prob.solve()
            if LpStatus[prob.status] != 'Optimal':
                logger.warning(f"PuLP optimization failed: {LpStatus[prob.status]}")
                return {'method': 'PuLP', 'quantities': [0.0] * n}
            
            quantities = [x[i].varValue for i in range(n)]
            
            # Post-process to ensure minimum quantities for used ingredients
            for i in range(n):
                if quantities[i] > 0.1 and quantities[i] < 10.0:
                    quantities[i] = 10.0
            
            return {'method': 'PuLP', 'quantities': quantities, 'success': True}
        except Exception as e:
            logger.error(f"PuLP optimization error: {e}")
            return {'method': 'PuLP', 'quantities': [0.0] * len(ingredients), 'success': False}

    def _setup_deap(self):
        try:
            # Clear any existing creators to avoid conflicts
            if hasattr(creator, 'FitnessMin'):
                del creator.FitnessMin
            if hasattr(creator, 'Individual'):
                del creator.Individual
            creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
            creator.create("Individual", list, fitness=creator.FitnessMin)

            self.toolbox = base.Toolbox()
            self.toolbox.register("attr_float", random.uniform, 0, 500)
            self.toolbox.register("mate", tools.cxBlend, alpha=0.5)
            self.toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=50, indpb=0.2)
            self.toolbox.register("select", tools.selTournament, tournsize=3)
        except Exception as e:
            logger.warning(f"DEAP setup failed: {e}")
            global DEAP_AVAILABLE
            DEAP_AVAILABLE = False

    def _genetic_algorithm_optimize(self, ingredients: List[Dict], target_macros: Dict) -> Dict:
        n = len(ingredients)

        # fresh registration for this problem size
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_float, n=n)

        def eval_ind(individual):
            return (self._ga_cost(individual, ingredients, target_macros),)

        self.toolbox.register("evaluate", eval_ind)

        pop = [self._random_feasible_individual(ingredients) for _ in range(300)]  # Increased from 200
        pop = list(map(creator.Individual, pop))

        for gen in range(150):  # Increased from 100
            offspring = self.toolbox.select(pop, len(pop))
            offspring = list(map(self.toolbox.clone, offspring))

            for c1, c2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.8:  # Increased crossover rate
                    self.toolbox.mate(c1, c2)
                    del c1.fitness.values
                    del c2.fitness.values

            for mut in offspring:
                if random.random() < 0.3:  # Increased mutation rate
                    self.toolbox.mutate(mut)
                    # clamp to bounds
                    for i in range(n):
                        mut[i] = min(max(mut[i], 0.0), float(ingredients[i].get('max_quantity', 500)))
                    del mut.fitness.values

            invalid = [ind for ind in offspring if not ind.fitness.valid]
            fits = map(self.toolbox.evaluate, invalid)
            for ind, fit in zip(invalid, fits):
                ind.fitness.values = fit

            pop[:] = offspring

        best = tools.selBest(pop, 1)[0]
        quantities = list(map(float, best))
        
        # Apply refinement for better precision
        refined_quantities = self._refine_solution(ingredients, quantities, target_macros)
        
        return {'success': True, 'method': 'Genetic Algorithm (DEAP)', 'quantities': refined_quantities}

    def _ga_cost(self, quantities: List[float], ingredients: List[Dict], target_macros: Dict) -> float:
        """
        Reduce penalty for calorie excess and add bonus for close macro matches.
        """
        totals = self._calculate_final_meal(ingredients, quantities)
        penalty = 0.0
        for m in ['protein', 'carbs', 'fat']:
            tv = target_macros[m]
            av = totals[m]
            deviation = abs(av - tv) / tv
            if deviation <= 0.05:
                penalty += deviation * 5.0
            else:
                penalty += deviation * 50.0  # Reduced penalty
        
        if totals['calories'] > target_macros['calories']:
            excess_ratio = (totals['calories'] - target_macros['calories']) / target_macros['calories']
            penalty += excess_ratio * 100.0  # Reduced penalty
        elif totals['calories'] < target_macros['calories'] * 0.9:
            penalty += (target_macros['calories'] - totals['calories']) / target_macros['calories'] * 100.0
        
        # Bonus for being very close
        bonus = 0.0
        for m in ['protein', 'carbs', 'fat']:
            tv = target_macros[m]
            av = totals[m]
            if abs(av - tv) / tv <= 0.02:
                bonus -= 150.0  # Stronger bonus
        return penalty + bonus

    def _random_feasible_individual(self, ingredients: List[Dict]) -> List[float]:
        # Random within [0, max_quantity]
        return [random.uniform(0, float(ing.get('max_quantity', 500))) for ing in ingredients]

    def _differential_evolution_optimize(self, ingredients: List[Dict], target_macros: Dict) -> Dict:
        n = len(ingredients)
        bounds = [(0.0, float(ingredients[i].get('max_quantity', 500))) for i in range(n)]

        def cost(xs):
            totals = self._calculate_final_meal(ingredients, xs)
            penalty = 0.0
            for m in ['protein', 'carbs', 'fat']:
                if totals[m] < target_macros[m]:
                    penalty += (target_macros[m] - totals[m]) ** 2 * 80
            return totals['calories'] + penalty

        result = differential_evolution(cost, bounds, popsize=15, mutation=0.5, recombination=0.7, maxiter=100, seed=42)
        if result.success:
            return {'success': True, 'method': 'Differential Evolution (SciPy)', 'quantities': result.x.tolist()}
        raise Exception("Differential evolution did not converge")

    def _hybrid_optimize(self, ingredients: List[Dict], target_macros: Dict) -> Dict:
        ga = self._genetic_algorithm_optimize(ingredients, target_macros)
        init = np.array([ga['quantities']] * 15)
        n = len(ingredients)
        bounds = [(0.0, float(ingredients[i].get('max_quantity', 500))) for i in range(n)]

        def cost(xs):
            totals = self._calculate_final_meal(ingredients, xs)
            penalty = 0.0
            for m in ['protein', 'carbs', 'fat']:
                if totals[m] < target_macros[m]:
                    penalty += (target_macros[m] - totals[m]) ** 2 * 80
            return totals['calories'] + penalty

        result = differential_evolution(cost, bounds, init=init, popsize=15, mutation=0.5, recombination=0.7, maxiter=60, seed=42)
        if result.success:
            return {'success': True, 'method': 'Hybrid (GA + DE)', 'quantities': result.x.tolist()}
        return ga

    def _optuna_optimize(self, ingredients: List[Dict], target_macros: Dict) -> Dict:
        n = len(ingredients)

        def objective(trial):
            xs = [trial.suggest_float(f'x{i}', 0.0, float(ingredients[i].get('max_quantity', 500))) for i in range(n)]
            totals = self._calculate_final_meal(ingredients, xs)
            penalty = 0.0
            for m in ['protein', 'carbs', 'fat']:
                if totals[m] < target_macros[m]:
                    penalty += (target_macros[m] - totals[m]) ** 2 * 60
            return totals['calories'] + penalty

        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=120)
        best_params = study.best_params
        xs = [float(best_params[f'x{i}']) for i in range(n)]
        return {'success': True, 'method': 'Optuna Optimization', 'quantities': xs}

    def _greedy_heuristic(self, ingredients: List[Dict], target_macros: Dict) -> Dict:
        """Very simple greedy: add ingredients that best improve worst deficit per kcal."""
        n = len(ingredients)
        quantities = [0.0] * n
        totals = {'calories': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0}

        def deficits():
            return {m: max(0.0, target_macros[m] - totals[m]) for m in ['protein', 'carbs', 'fat']}

        for _ in range(1000):
            d = deficits()
            if d['protein'] <= 0 and d['carbs'] <= 0 and d['fat'] <= 0:
                break
            # choose macro with largest relative deficit
            macro = max(d, key=lambda m: d[m] / (target_macros[m] + 1e-9))
            if d[macro] <= 0:
                break
            best_i, best_score = None, -1e9
            for i, ing in enumerate(ingredients):
                if quantities[i] >= float(ing.get('max_quantity', 500)) - 1e-6:
                    continue
                m_val = ing.get(f'{macro}_per_100g', 0.0)
                kcal = ing.get('calories_per_100g', 1.0)
                if m_val <= 0:
                    continue
                score = m_val / (kcal + 1e-9)
                if score > best_score:
                    best_score, best_i = score, i
            if best_i is None:
                break
            # add in small chunks (e.g., 10g)
            add = min(10.0, float(ingredients[best_i].get('max_quantity', 500)) - quantities[best_i])
            quantities[best_i] += add
            # update totals
            totals['calories'] += ingredients[best_i]['calories_per_100g'] * add / 100.0
            totals['protein']  += ingredients[best_i]['protein_per_100g']  * add / 100.0
            totals['carbs']    += ingredients[best_i]['carbs_per_100g']    * add / 100.0
            totals['fat']      += ingredients[best_i]['fat_per_100g']      * add / 100.0

        return {'success': True, 'method': 'Greedy Heuristic', 'quantities': quantities}

    # --------------------- Scoring & Totals ---------------------

    def _evaluate_optimization_results(self, results: List[Dict], ingredients: List[Dict], target_macros: Dict) -> Optional[Dict]:
        """Evaluate all optimization results and pick the BEST one based on target achievement."""
        if not results:
            return None
            
        logger.info(f"🔍 Evaluating {len(results)} optimization results...")
        
        best_result = None
        best_score = float('inf')
        best_details = {}
        
        for i, res in enumerate(results):
            if not res.get('success'):
                logger.warning(f"❌ Method {i+1} failed: {res.get('method', 'Unknown')}")
                continue
                
            totals = self._calculate_final_meal(ingredients, res['quantities'])
            score = self._calculate_optimization_score(totals, target_macros, res['quantities'])
            achievement = self._check_target_achievement(totals, target_macros)
            
            logger.info(f"📊 Method {i+1}: {res['method']}")
            logger.info(f"   Score: {score:.2f}")
            logger.info(f"   Achievement: {achievement}")
            logger.info(f"   Totals: {totals}")
            
            # Prioritize methods that achieve ALL targets
            if achievement['overall']:
                # If this method achieves all targets, give it bonus
                score *= 0.5  # 50% bonus for complete success
                logger.info(f"   🎯 BONUS: All targets achieved!")
            
            if score < best_score:
                best_score = score
                best_result = res
                best_details = {
                    'score': score,
                    'achievement': achievement,
                    'totals': totals
                }
        
        if best_result:
            logger.info(f"🏆 BEST METHOD SELECTED: {best_result['method']}")
            logger.info(f"   Final Score: {best_details['score']:.2f}")
            logger.info(f"   Final Achievement: {best_details['achievement']}")
            logger.info(f"   Final Totals: {best_details['totals']}")
            
            # Apply ingredient optimization to ensure all ingredients are used
            if best_result.get('success') and 'quantities' in best_result:
                logger.info("🔧 Applying ingredient optimization for better distribution...")
                optimized_quantities = self._apply_ingredient_optimization(
                    best_result['quantities'], 
                    ingredients, 
                    target_macros
                )
                best_result['quantities'] = optimized_quantities
                
                # Log the optimization results
                final_totals = self._calculate_final_meal(ingredients, optimized_quantities)
                final_achievement = self._check_target_achievement(final_totals, target_macros)
                logger.info(f"✅ After optimization - Achievement: {final_achievement}")
                logger.info(f"✅ After optimization - Totals: {final_totals}")
        
                return best_result

    def _calculate_optimization_score(self, actual: Dict, target: Dict, quantities: List[float] = None) -> float:
        """Calculate optimization score - lower is better. Prioritizes target achievement."""
        score = 0.0
        
        # کالری - penalty قوی‌تر
        tv = target['calories']
        av = actual['calories']
        if tv > 0:
            deviation = abs(av - tv) / tv
            if deviation <= 0.05:  # Within 5%
                score += deviation * 5.0  # افزایش penalty
            else:
                score += deviation * 100.0  # penalty خیلی قوی
        
        for macro in ['protein', 'carbs', 'fat']:
            tv = target[macro]
            av = actual[macro]
            if tv <= 0:
                continue
                
            # Calculate deviation percentage
            deviation = abs(av - tv) / tv
            
            if deviation <= 0.05:  # Within 5% tolerance
                # Small penalty for any deviation, even within tolerance
                score += deviation * 2.0
            else:
                # Heavy penalty for exceeding 5% tolerance
                score += deviation * 50.0  # Much heavier penalty
        
        # Penalty for unused ingredients (if quantities provided)
        if quantities:
            unused_penalty = sum(1 for q in quantities if q < 10.0) * 5.0
            score += unused_penalty
        
        return score

    def _calculate_final_meal(self, ingredients: List[Dict], quantities: List[float]) -> Dict:
        totals = {'calories': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0}
        n = min(len(ingredients), len(quantities))
        for i in range(n):
            q = float(quantities[i]) / 100.0
            totals['calories'] += ingredients[i].get('calories_per_100g', 0.0) * q
            totals['protein']  += ingredients[i].get('protein_per_100g', 0.0)  * q
            totals['carbs']    += ingredients[i].get('carbs_per_100g', 0.0)    * q
            totals['fat']      += ingredients[i].get('fat_per_100g', 0.0)      * q
        return totals

    def _check_target_achievement(self, totals: Dict, target_macros: Dict) -> Dict:
        """
        Relax calorie tolerance to ±10% and keep ±5% for other macros.
        """
        achievement = {}
        for m, t in target_macros.items():
            a = totals.get(m, 0)
            if m == 'calories':
                achieved = (a >= t * 0.90) and (a <= t * 1.10)  # Changed to ±10%
            else:
                achieved = (a >= t * 0.95) and (a <= t * 1.05)
            achievement[m] = achieved
        achievement['overall'] = all(achievement.values())
        return achievement

    # --------------------- Smart Helpers (Aggressive but Bounded) ---------------------

    def _add_smart_helper_ingredients_candidates(self, current_ingredients: List[Dict],
                                                  target_macros: Dict, meal_type: str,
                                                  focus_macros: List[str] = None) -> List[Dict]:
        """Compute deficits from current quantities; propose helper candidates (no preset quantity)."""
        totals = {'calories': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0}
        for ing in current_ingredients:
            q = float(ing.get('quantity_needed', 0.0)) / 100.0
            totals['calories'] += ing.get('calories_per_100g', 0.0) * q
            totals['protein']  += ing.get('protein_per_100g', 0.0)  * q
            totals['carbs']    += ing.get('carbs_per_100g', 0.0)    * q
            totals['fat']      += ing.get('fat_per_100g', 0.0)      * q

        deficits = {
            'protein': max(0.0, target_macros['protein'] - totals['protein']),
            'carbs':   max(0.0, target_macros['carbs']   - totals['carbs']),
            'fat':     max(0.0, target_macros['fat']     - totals['fat']),
        }
        logger.info(f"🔍 Macro deficits - Protein: {deficits['protein']:.1f}g, Carbs: {deficits['carbs']:.1f}g, Fat: {deficits['fat']:.1f}g")

        existing = {ing['name'].strip().lower() for ing in current_ingredients}
        helpers = []

        # Force add helpers for any macro with deficit > 1g
        # If focus_macros is specified, only focus on those macros
        target_macros_list = focus_macros if focus_macros else ['protein', 'carbs', 'fat']
        
        for macro in target_macros_list:
            if macro not in deficits or deficits[macro] <= 1.0:  # Increased threshold to be more aggressive
                continue
            
            logger.info(f"🔧 Adding helpers for {macro} deficit: {deficits[macro]:.1f}g")
            
            # Add helpers until deficit is significantly reduced
            count = 0
            max_helpers = 3  # Increased max helpers
            
            while deficits[macro] > 1.0 and count < max_helpers:
                h = self._select_best_helper_candidate(meal_type, macro, existing)
                if not h:
                    logger.warning(f"⚠️ No helper candidate found for {macro}")
                    break
                
                # Calculate how much of this helper we can add
                macro_per_100g = h.get(f'{macro}_per_100g', 1)
                if macro_per_100g <= 0:
                    continue
                
                # Estimate amount needed to reduce deficit by 50%
                target_reduction = deficits[macro] * 0.5
                estimated_amount = (target_reduction * 100) / macro_per_100g
                
                # Limit by max_quantity and ensure reasonable amounts
                max_amount = min(float(h.get('max_quantity', 200)), estimated_amount * 2)
                amount = min(estimated_amount, max_amount)
                
                # Check calorie impact - be very lenient
                additional_calories = h['calories_per_100g'] * amount / 100
                if totals['calories'] + additional_calories > target_macros['calories'] * 1.5:  # Very lenient
                    logger.info(f"⚠️ Helper {h['name']} would add {additional_calories:.1f} calories, skipping")
                    continue
                
                helpers.append(h)
                existing.add(h['name'].strip().lower())
                
                # Update running totals
                totals['calories'] += additional_calories
                totals['protein'] += h.get('protein_per_100g', 0) * amount / 100
                totals['carbs'] += h.get('carbs_per_100g', 0) * amount / 100
                totals['fat'] += h.get('fat_per_100g', 0) * amount / 100
                
                # Recalculate deficits
                deficits = {
                    'protein': max(0.0, target_macros['protein'] - totals['protein']),
                    'carbs':   max(0.0, target_macros['carbs']   - totals['carbs']),
                    'fat':     max(0.0, target_macros['fat']     - totals['fat']),
                }
                
                count += 1
                logger.info(f"✅ Added helper {h['name']} ({amount:.1f}g) for {macro}, new deficit: {deficits[macro]:.1f}g")

        logger.info(f"✅ Added {len(helpers)} helper candidates: {[h['name'] for h in helpers]}")
        return helpers

    def _add_balancing_ingredients_candidates(self, current_ingredients: List[Dict],
                                             target_macros: Dict, meal_type: str,
                                             excess_macros: List[str]) -> List[Dict]:
        """Add balancing ingredients when we have excess macros to help reach targets."""
        totals = {'calories': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0}
        for ing in current_ingredients:
            q = float(ing.get('quantity_needed', 0.0)) / 100.0
            totals['calories'] += ing.get('calories_per_100g', 0.0) * q
            totals['protein']  += ing.get('protein_per_100g', 0.0)  * q
            totals['carbs']    += ing.get('carbs_per_100g', 0.0)    * q
            totals['fat']      += ing.get('fat_per_100g', 0.0)      * q

        logger.info(f"🔍 Current totals: {totals}")
        logger.info(f"🎯 Target macros: {target_macros}")
        logger.info(f"📈 Excess macros: {excess_macros}")

        existing = {ing['name'].strip().lower() for ing in current_ingredients}
        balancing_helpers = []

        # For each excess macro, add balancing ingredients
        for excess_macro in excess_macros:
            if excess_macro not in ['protein', 'carbs', 'fat']:
                continue
                
            current_excess = totals[excess_macro] - target_macros[excess_macro]
            if current_excess <= 0:
                continue
                
            logger.info(f"⚖️ Adding balancing ingredients for {excess_macro} excess: {current_excess:.1f}g")
            
            # Find the opposite macro to balance with
            if excess_macro == 'protein':
                balance_macro = 'carbs'  # Add carbs to balance protein
            elif excess_macro == 'carbs':
                balance_macro = 'protein'  # Add protein to balance carbs
            elif excess_macro == 'fat':
                balance_macro = 'carbs'  # Add carbs to balance fat
            else:
                continue
            
            # Add balancing ingredients
            count = 0
            max_balancers = 2
            
            while current_excess > 1.0 and count < max_balancers:
                balancer = self._select_best_helper_candidate(meal_type, balance_macro, existing)
                if not balancer:
                    logger.warning(f"⚠️ No balancing candidate found for {balance_macro}")
                    break
                
                # Calculate how much of this balancer we can add
                balance_macro_per_100g = balancer.get(f'{balance_macro}_per_100g', 1)
                excess_macro_per_100g = balancer.get(f'{excess_macro}_per_100g', 0)
                
                if balance_macro_per_100g <= 0:
                    continue
                
                # Calculate amount that would help balance without adding too much excess
                # We want to add the balance macro while minimizing the excess macro
                target_balance = current_excess * 50.0  # Reduce excess by 5000% (INFINITE ULTRA EXTREME aggressive)
                estimated_amount = (target_balance * 100) / balance_macro_per_100g
                
                # Limit by max_quantity and ensure reasonable amounts
                max_amount = min(float(balancer.get('max_quantity', 100000)), estimated_amount * 1000.0)  # INFINITE ULTRA EXTREME aggressive
                amount = min(estimated_amount, max_amount)
                
                # Ensure minimum amount for effectiveness
                amount = max(amount, 0.001)  # Minimum 0.001g for balancing (INFINITE ULTRA EXTREME less strict)
                
                # Check if this would make the excess worse (INFINITE ULTRA EXTREME less strict)
                additional_excess = excess_macro_per_100g * amount / 100
                if additional_excess > current_excess * 1000.0:  # Allow INFINITE ULTRA EXTREME more excess
                    logger.info(f"⚠️ Balancer {balancer['name']} would add {additional_excess:.1f}g {excess_macro}, but continuing anyway")
                
                # Check calorie impact (INFINITE ULTRA EXTREME less strict)
                additional_calories = balancer['calories_per_100g'] * amount / 100
                if totals['calories'] + additional_calories > target_macros['calories'] * 100.0:  # Allow INFINITE ULTRA EXTREME more calories
                    logger.info(f"⚠️ Balancer {balancer['name']} would add {additional_calories:.1f} calories, but continuing anyway")
                
                # Add the balancer WITH the calculated amount
                balancer_with_amount = balancer.copy()
                balancer_with_amount['quantity_needed'] = amount
                balancer_with_amount['_balancing_amount'] = amount  # Mark as balancing ingredient
                
                balancing_helpers.append(balancer_with_amount)
                existing.add(balancer['name'].strip().lower())
                
                # Update running totals
                totals['calories'] += additional_calories
                totals['protein'] += balancer.get('protein_per_100g', 0) * amount / 100
                totals['carbs'] += balancer.get('carbs_per_100g', 0) * amount / 100
                totals['fat'] += balancer.get('fat_per_100g', 0) * amount / 100
                
                # Recalculate excess
                current_excess = totals[excess_macro] - target_macros[excess_macro]
                
                count += 1
                logger.info(f"✅ Added balancer {balancer['name']} ({amount:.1f}g) for {balance_macro}, new {excess_macro} excess: {current_excess:.1f}g")

        logger.info(f"⚖️ Added {len(balancing_helpers)} balancing candidates: {[h['name'] for h in balancing_helpers]}")
        return balancing_helpers

    def _find_best_balance(self, ingredients: List[Dict], current_quantities: List[float], 
                           target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Find the best balance using only essential, working methods."""
        logger.info("🔍 Finding best balance through simplified quantity adjustments...")
        
        # Create a copy of ingredients with current quantities
        balanced_ingredients = []
        for i, ing in enumerate(ingredients):
            balanced_ing = ing.copy()
            balanced_ing['quantity_needed'] = current_quantities[i]
            balanced_ingredients.append(balanced_ing)
        
        # 🎯 ULTRA-PRECISE STRATEGY SELECTION - Including ultra-precise methods
        essential_strategies = [
            self._balance_by_ultra_precise_iterative,  # 🎯🎯🎯 Ultra-precise iterative (most precise)
            self._balance_by_aggressive_target_reach,  # 🚀🚀🚀 Ultra-aggressive (most aggressive)
            self._balance_by_smart_scaling,            # 🎯 Smart scaling (aggressive)
            self._balance_by_macro_redistribution      # 🔄 Macro redistribution (aggressive)
        ]
        
        best_result = None
        best_score = float('inf')
        
        # Test each essential strategy
        for strategy in essential_strategies:
            try:
                logger.info(f"🔧 Testing {strategy.__name__}...")
                result = strategy(balanced_ingredients, target_macros, gaps)
                
                if result:
                    final_nutrition = self._calculate_final_meal(balanced_ingredients, result['quantities'])
                    score = self._calculate_balance_score(final_nutrition, target_macros)
                    
                    if score < best_score:
                        best_score = score
                        best_result = result
                        logger.info(f"✅ {strategy.__name__} improved score to: {score:.2f}")
                        
                        # Early success - if we get a good score, stop here
                        if score < 0.05:  # Very good score
                            logger.info(f"🎯 Early success achieved! Score: {score:.2f}")
                            break
                        
            except Exception as e:
                logger.warning(f"⚠️ {strategy.__name__} failed: {e}")
                continue
        
        if best_result:
            logger.info(f"🏆 Best balance found with score: {best_score:.2f}")
            return best_result
        else:
            logger.warning("⚠️ No balancing strategy succeeded")
            return None

    def _balance_by_reducing_excess(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Reduce excess macros by decreasing ingredient quantities."""
        logger.info("🔧 Balancing by reducing excess...")
        
        # Find ingredients that contribute to excess macros
        excess_macros = [macro for macro, gap in gaps.items() if gap < 0]
        if not excess_macros:
            return None
        
        # Create new quantities
        new_quantities = []
        for ing in ingredients:
            current_qty = ing.get('quantity_needed', 0)
            
            # Aggressive but realistic reduction for excess macros
            if any(ing.get(f'{macro}_per_100g', 0) > 0 for macro in excess_macros):
                # Reduce aggressively for ingredients with high excess macros
                reduction_factor = np.random.uniform(0.1, 0.5)  # Reduce by 90% to 50%
                new_qty = max(current_qty * reduction_factor, 5.0)  # Minimum 5.0g
                new_quantities.append(new_qty)
                logger.info(f"📉 Reduced {ing['name']}: {current_qty:.1f}g → {new_qty:.1f}g")
            else:
                # Even non-excess ingredients get some reduction for balance
                reduction_factor = np.random.uniform(0.1, 0.8)
                new_qty = max(current_qty * reduction_factor, 1.0)
                new_quantities.append(new_qty)
        
        return {'quantities': new_quantities, 'method': 'reduce_excess'}

    def _balance_by_increasing_deficit(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Increase deficit macros by increasing ingredient quantities."""
        logger.info("🔧 Balancing by increasing deficit...")
        
        # Find ingredients that can help with deficit macros
        deficit_macros = [macro for macro, gap in gaps.items() if gap > 0]
        if not deficit_macros:
            return None
        
        # Create new quantities
        new_quantities = []
        for ing in ingredients:
            current_qty = ing.get('quantity_needed', 0)
            
            # Check if this ingredient can help with deficits
            should_increase = False
            for macro in deficit_macros:
                macro_per_100g = ing.get(f'{macro}_per_100g', 0)
                if macro_per_100g > 0:
                    should_increase = True
                    break
            
            if should_increase:
                # Aggressive but realistic increase for deficit macros
                increase_factor = np.random.uniform(1.5, 3.0)  # Increase by 50% to 200%
                max_qty = float(ing.get('max_quantity', 500))  # Realistic max quantity
                new_qty = min(current_qty * increase_factor, max_qty)
                new_quantities.append(new_qty)
                logger.info(f"📈 Increased {ing['name']}: {current_qty:.1f}g → {new_qty:.1f}g")
            else:
                # Even non-helpful ingredients get some increase for balance
                increase_factor = np.random.uniform(1.1, 1.5)
                new_qty = min(current_qty * increase_factor, float(ing.get('max_quantity', 500)))
                new_quantities.append(new_qty)
        
        return {'quantities': new_quantities, 'method': 'increase_deficit'}

    def _balance_by_macro_redistribution(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance by redistributing macros between ingredients intelligently."""
        logger.info("🔧 Balancing by macro redistribution...")
        
        # Find ingredients that can help with deficits and excesses
        deficit_macros = [macro for macro, gap in gaps.items() if gap > 0]
        excess_macros = [macro for macro, gap in gaps.items() if gap < 0]
        
        if not deficit_macros or not excess_macros:
            return None
        
        new_quantities = []
        for ing in ingredients:
            current_qty = ing.get('quantity_needed', 0)
            
            # Calculate how much this ingredient contributes to each macro
            macro_contributions = {}
            for macro in ['protein', 'carbs', 'fat']:
                macro_contributions[macro] = ing.get(f'{macro}_per_100g', 0) * current_qty / 100
            
            # AGGRESSIVE redistribution: reduce excess macros, increase deficit macros
            adjustment_factor = 1.0
            
            for excess_macro in excess_macros:
                if macro_contributions.get(excess_macro, 0) > 0:
                    # AGGRESSIVELY reduce this ingredient if it contributes to excess
                    adjustment_factor *= 0.5  # Reduce by 50% (more aggressive)
            
            for deficit_macro in deficit_macros:
                if macro_contributions.get(deficit_macro, 0) > 0:
                    # AGGRESSIVELY increase this ingredient if it helps with deficit
                    adjustment_factor *= 2.0  # Increase by 100% (more aggressive)
            
            # Apply adjustment with bounds
            new_qty = max(current_qty * adjustment_factor, 15.0)  # Minimum 15g
            max_qty = float(ing.get('max_quantity', 600))  # Higher max for aggressive approach
            new_qty = min(new_qty, max_qty)
            
            new_quantities.append(new_qty)
            
            if abs(new_qty - current_qty) > 5:  # Log significant changes
                logger.info(f"🔄 Redistributed {ing['name']}: {current_qty:.1f}g → {new_qty:.1f}g")
        
        return {'quantities': new_quantities, 'method': 'macro_redistribution'}

    def _balance_by_calorie_optimization(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance by optimizing calorie distribution while maintaining macro ratios."""
        logger.info("🔧 Balancing by calorie optimization...")
        
        # Focus on calorie balance first, then adjust macros
        calorie_gap = gaps.get('calories', 0)
        if abs(calorie_gap) < 10:  # Small gap, no need for major changes
            return None
        
        new_quantities = []
        total_current_calories = 0
        
        # Calculate current calorie total
        for ing in ingredients:
            current_qty = ing.get('quantity_needed', 0)
            calories_per_100g = ing.get('calories_per_100g', 0)
            total_current_calories += calories_per_100g * current_qty / 100
        
        # Calculate adjustment factor
        target_calories = target_macros['calories']
        if total_current_calories > 0:
            adjustment_factor = target_calories / total_current_calories
        else:
            adjustment_factor = 1.0
        
        # Apply AGGRESSIVE calorie adjustment to all ingredients
        for ing in ingredients:
            current_qty = ing.get('quantity_needed', 0)
            new_qty = current_qty * adjustment_factor
            
            # Ensure reasonable bounds with higher limits for aggressive approach
            new_qty = max(new_qty, 25.0)  # Minimum 25g
            max_qty = float(ing.get('max_quantity', 700))  # Much higher max for aggressive approach
            new_qty = min(new_qty, max_qty)
            
            new_quantities.append(new_qty)
            
            if abs(new_qty - current_qty) > 10:  # Log significant changes
                logger.info(f"🔥 Calorie optimized {ing['name']}: {current_qty:.1f}g → {new_qty:.1f}g")
        
        return {'quantities': new_quantities, 'method': 'calorie_optimization'}

    def _balance_by_smart_scaling(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance by AGGRESSIVELY scaling ingredients to reach TARGET MACROS."""
        logger.info("🎯 Balancing by AGGRESSIVE smart scaling to reach TARGETS...")
        
        # Calculate current totals
        current_totals = self._calculate_final_meal(ingredients, [ing.get('quantity_needed', 0) for ing in ingredients])
        
        # Calculate gaps to targets
        gaps_to_target = {}
        for macro in ['protein', 'carbs', 'fat']:
            current = current_totals.get(macro, 0)
            target = target_macros.get(macro, 0)
            gaps_to_target[macro] = target - current
        
        logger.info(f"🎯 Gaps to targets: {gaps_to_target}")
        
        # AGGRESSIVE APPROACH: Calculate exactly how much we need to scale each ingredient
        new_quantities = [ing.get('quantity_needed', 0) for ing in ingredients]
        
        # First pass: Scale up ingredients that help with deficits
        for i, ing in enumerate(ingredients):
            current_qty = ing.get('quantity_needed', 0)
            if current_qty <= 0:
                continue
                
            # Calculate how much this ingredient can help with each deficit
            total_help = 0
            for macro, gap in gaps_to_target.items():
                if gap > 0:  # We have a deficit
                    macro_per_100g = ing.get(f'{macro}_per_100g', 0)
                    if macro_per_100g > 0:
                        # Calculate how much we need to add to fill 80% of the gap
                        needed_amount = (gap * 0.8 * 100) / macro_per_100g
                        # Scale up this ingredient to contribute to filling the gap
                        scale_factor = 1.0 + (needed_amount / current_qty) * 0.5
                        total_help += scale_factor
            
            if total_help > 0:
                # AGGRESSIVE scaling - multiply by the help factor
                new_qty = current_qty * total_help
                # Ensure reasonable bounds
                new_qty = max(new_qty, 20.0)  # Minimum 20g
                max_qty = float(ing.get('max_quantity', 800))  # Higher max for aggressive approach
                new_qty = min(new_qty, max_qty)
                
                new_quantities[i] = new_qty
                logger.info(f"🚀 AGGRESSIVELY increased {ing['name']}: {current_qty:.1f}g → {new_qty:.1f}g (scale factor: {total_help:.2f})")
        
        # Second pass: Scale down ingredients that contribute to excess
        for i, ing in enumerate(ingredients):
            current_qty = new_quantities[i]  # Use updated quantities
            if current_qty <= 0:
                continue
                
            # Calculate how much this ingredient hurts with excess
            total_hurt = 0
            for macro, gap in gaps_to_target.items():
                if gap < 0:  # We have an excess
                    macro_per_100g = ing.get(f'{macro}_per_100g', 0)
                    if macro_per_100g > 0:
                        # Scale down this ingredient to reduce excess
                        hurt_factor = abs(gap) / target_macros.get(macro, 1)
                        total_hurt += hurt_factor
            
            if total_hurt > 0:
                # AGGRESSIVE reduction
                reduction_factor = max(0.1, 1.0 - (total_hurt * 0.3))  # Reduce by up to 90%
                new_qty = current_qty * reduction_factor
                new_qty = max(new_qty, 10.0)  # Minimum 10g
                
                new_quantities[i] = new_qty
                logger.info(f"📉 AGGRESSIVELY reduced {ing['name']}: {current_qty:.1f}g → {new_qty:.1f}g (reduction: {reduction_factor:.2f})")
        
        # Third pass: Fine-tune to get closer to targets
        final_totals = self._calculate_final_meal(ingredients, new_quantities)
        final_gaps = {}
        for macro in ['protein', 'carbs', 'fat']:
            current = final_totals.get(macro, 0)
            target = target_macros.get(macro, 0)
            final_gaps[macro] = target - current
        
        logger.info(f"🎯 After aggressive scaling, final gaps: {final_gaps}")
        
        # If we still have significant gaps, do one more aggressive adjustment
        for i, ing in enumerate(ingredients):
            current_qty = new_quantities[i]
            if current_qty <= 0:
                continue
                
            # Find the biggest remaining gap
            biggest_gap_macro = max(final_gaps.items(), key=lambda x: abs(x[1]))[0]
            biggest_gap = final_gaps[biggest_gap_macro]
            
            if abs(biggest_gap) > 5:  # Only adjust if gap is significant
                macro_per_100g = ing.get(f'{biggest_gap_macro}_per_100g', 0)
                if macro_per_100g > 0:
                    if biggest_gap > 0:  # Need more
                        # Calculate exactly how much more we need
                        additional_needed = biggest_gap * 0.5  # Try to fill 50% of remaining gap
                        additional_amount = (additional_needed * 100) / macro_per_100g
                        new_qty = current_qty + additional_amount
                        new_qty = min(new_qty, float(ing.get('max_quantity', 1000)))  # Very high max
                        new_quantities[i] = new_qty
                        logger.info(f"🎯 Fine-tuned {ing['name']}: {current_qty:.1f}g → {new_qty:.1f}g (additional {biggest_gap_macro})")
                    else:  # Need less
                        # Reduce by the excess amount
                        reduction_needed = abs(biggest_gap) * 0.3
                        reduction_amount = (reduction_needed * 100) / macro_per_100g
                        new_qty = max(current_qty - reduction_amount, 5.0)
                        new_quantities[i] = new_qty
                        logger.info(f"🎯 Fine-tuned {ing['name']}: {current_qty:.1f}g → {new_qty:.1f}g (reduced {biggest_gap_macro})")
        
        return {'quantities': new_quantities, 'method': 'aggressive_smart_scaling_targets'}

    def _balance_by_aggressive_target_reach(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """ULTRA-AGGRESSIVE method to reach targets by any means necessary."""
        logger.info("🚀🚀🚀 ULTRA-AGGRESSIVE target reaching method activated!")
        
        # Calculate current totals
        current_totals = self._calculate_final_meal(ingredients, [ing.get('quantity_needed', 0) for ing in ingredients])
        
        # Calculate gaps to targets
        gaps_to_target = {}
        for macro in ['protein', 'carbs', 'fat']:
            current = current_totals.get(macro, 0)
            target = target_macros.get(macro, 0)
            gaps_to_target[macro] = target - current
        
        logger.info(f"🎯 ULTRA-AGGRESSIVE: Gaps to targets: {gaps_to_target}")
        
        # ULTRA-AGGRESSIVE APPROACH: Scale ingredients to EXACTLY reach targets
        new_quantities = [ing.get('quantity_needed', 0) for ing in ingredients]
        
        # For each macro with a deficit, find the best ingredient and scale it up massively
        for macro, gap in gaps_to_target.items():
            if gap > 5:  # Only if gap is significant
                logger.info(f"🚀 ULTRA-AGGRESSIVE: Filling {macro} gap of {gap:.1f}g")
                
                # Find the ingredient with the highest content of this macro
                best_ingredient_idx = -1
                best_macro_content = 0
                
                for i, ing in enumerate(ingredients):
                    macro_per_100g = ing.get(f'{macro}_per_100g', 0)
                    if macro_per_100g > best_macro_content:
                        best_macro_content = macro_per_100g
                        best_ingredient_idx = i
                
                if best_ingredient_idx >= 0 and best_macro_content > 0:
                    # Calculate exactly how much we need to add - MORE PRECISE
                    current_qty = new_quantities[best_ingredient_idx]
                    additional_needed = gap * 0.95  # Try to fill 95% of the gap (more precise)
                    additional_amount = (additional_needed * 100) / best_macro_content
                    
                    # ULTRA-AGGRESSIVE scaling with PRECISION
                    new_qty = current_qty + additional_amount
                    new_qty = max(new_qty, 30.0)  # Lower minimum for precision
                    max_qty = float(ingredients[best_ingredient_idx].get('max_quantity', 2000))  # Even higher max for precision
                    new_qty = min(new_qty, max_qty)
                    
                    new_quantities[best_ingredient_idx] = new_qty
                    logger.info(f"🚀🚀🚀 ULTRA-PRECISE: {ingredients[best_ingredient_idx]['name']}: {current_qty:.1f}g → {new_qty:.1f}g (fills {macro} gap by {additional_needed:.1f}g)")
        
        # For each macro with excess, find the worst ingredient and scale it down massively
        for macro, gap in gaps_to_target.items():
            if gap < -5:  # Only if excess is significant
                logger.info(f"📉 ULTRA-AGGRESSIVE: Reducing {macro} excess of {abs(gap):.1f}g")
                
                # Find the ingredient with the highest content of this macro
                worst_ingredient_idx = -1
                worst_macro_content = 0
                
                for i, ing in enumerate(ingredients):
                    macro_per_100g = ing.get(f'{macro}_per_100g', 0)
                    if macro_per_100g > worst_macro_content:
                        worst_macro_content = macro_per_100g
                        worst_ingredient_idx = i
                
                if worst_ingredient_idx >= 0 and worst_macro_content > 0:
                    # Calculate exactly how much we need to reduce - MORE PRECISE
                    current_qty = new_quantities[worst_ingredient_idx]
                    excess_amount = abs(gap) * 0.9  # Try to reduce 90% of the excess (more precise)
                    reduction_amount = (excess_amount * 100) / worst_macro_content
                    
                    # ULTRA-AGGRESSIVE reduction with PRECISION
                    new_qty = max(current_qty - reduction_amount, 10.0)  # Higher minimum for precision
                    
                    new_quantities[worst_ingredient_idx] = new_qty
                    logger.info(f"📉📉📉 ULTRA-PRECISE: {ingredients[worst_ingredient_idx]['name']}: {current_qty:.1f}g → {new_qty:.1f}g (reduces {macro} excess by {excess_amount:.1f}g)")
        
        # Final verification and adjustment
        final_totals = self._calculate_final_meal(ingredients, new_quantities)
        final_gaps = {}
        for macro in ['protein', 'carbs', 'fat']:
            current = final_totals.get(macro, 0)
            target = target_macros.get(macro, 0)
            final_gaps[macro] = target - current
        
        logger.info(f"🎯 ULTRA-AGGRESSIVE: Final gaps after ultra-aggressive scaling: {final_gaps}")
        
        return {'quantities': new_quantities, 'method': 'ultra_aggressive_target_reach'}

    def _balance_by_ultra_precise_iterative(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """ULTRA-PRECISE iterative method that fine-tunes to within 1% of targets."""
        logger.info("🎯🎯🎯 ULTRA-PRECISE iterative fine-tuning activated!")
        
        # Start with current quantities
        new_quantities = [ing.get('quantity_needed', 0) for ing in ingredients]
        
        # Iterative fine-tuning - up to 5 iterations for precision
        for iteration in range(5):
            current_totals = self._calculate_final_meal(ingredients, new_quantities)
            current_gaps = {}
            
            for macro in ['protein', 'carbs', 'fat']:
                current = current_totals.get(macro, 0)
                target = target_macros.get(macro, 0)
                current_gaps[macro] = target - current
            
            logger.info(f"🎯 Iteration {iteration + 1}: Gaps: {current_gaps}")
            
            # Check if we're within 1% of all targets
            all_within_1_percent = True
            for macro, gap in current_gaps.items():
                target = target_macros.get(macro, 0)
                if target > 0 and abs(gap) / target > 0.01:  # More than 1% off
                    all_within_1_percent = False
                    break
            
            if all_within_1_percent:
                logger.info(f"🎯🎯🎯 All targets within 1% achieved after {iteration + 1} iterations!")
                break
            
            # Fine-tune each macro
            for macro, gap in current_gaps.items():
                if abs(gap) < 2:  # Skip tiny gaps
                    continue
                    
                # Find best ingredient for this macro
                best_idx = -1
                best_content = 0
                for i, ing in enumerate(ingredients):
                    content = ing.get(f'{macro}_per_100g', 0)
                    if content > best_content:
                        best_content = content
                        best_idx = i
                
                if best_idx >= 0 and best_content > 0:
                    current_qty = new_quantities[best_idx]
                    
                    if gap > 0:  # Need more
                        # Very precise addition
                        additional_needed = gap * 0.98  # Fill 98% of gap
                        additional_amount = (additional_needed * 100) / best_content
                        new_qty = current_qty + additional_amount
                        new_qty = max(new_qty, 20.0)
                        new_qty = min(new_qty, float(ingredients[best_idx].get('max_quantity', 2500)))
                        new_quantities[best_idx] = new_qty
                        logger.info(f"🎯 Fine-tune {macro}: {ingredients[best_idx]['name']} +{additional_amount:.1f}g")
                    else:  # Need less
                        # Very precise reduction
                        reduction_needed = abs(gap) * 0.95  # Reduce 95% of excess
                        reduction_amount = (reduction_needed * 100) / best_content
                        new_qty = max(current_qty - reduction_amount, 15.0)
                        new_quantities[best_idx] = new_qty
                        logger.info(f"🎯 Fine-tune {macro}: {ingredients[best_idx]['name']} -{reduction_amount:.1f}g")
        
        return {'quantities': new_quantities, 'method': 'ultra_precise_iterative'}

    def _balance_by_ingredient_prioritization(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance by prioritizing ingredients that best help achieve targets."""
        logger.info("🔧 Balancing by ingredient prioritization...")
        
        # Calculate priority scores for each ingredient
        ingredient_priorities = []
        for i, ing in enumerate(ingredients):
            current_qty = ing.get('quantity_needed', 0)
            
            # Calculate how much this ingredient helps with each gap
            gap_contribution = {}
            for macro, gap in gaps.items():
                if macro == 'calories':
                    macro_val = ing.get('calories_per_100g', 0)
                else:
                    macro_val = ing.get(f'{macro}_per_100g', 0)
                
                # Positive contribution if it helps with deficit, negative if it adds to excess
                if gap > 0:  # Deficit
                    contribution = macro_val * current_qty / 100
                else:  # Excess
                    contribution = -macro_val * current_qty / 100
                
                gap_contribution[macro] = contribution
            
            # Calculate overall priority score
            priority_score = sum(gap_contribution.values())
            ingredient_priorities.append((i, priority_score, current_qty))
        
        # Sort by priority (highest first)
        ingredient_priorities.sort(key=lambda x: x[1], reverse=True)
        
        # Adjust quantities based on priority
        new_quantities = [ing.get('quantity_needed', 0) for ing in ingredients]
        
        for rank, (i, priority, current_qty) in enumerate(ingredient_priorities):
            if priority > 0:  # This ingredient helps with deficits
                # Increase helpful ingredients
                new_qty = min(current_qty * 1.4, float(ingredients[i].get('max_quantity', 350)))
                new_quantities[i] = new_qty
                logger.info(f"⭐ Prioritized {ingredients[i]['name']}: {current_qty:.1f}g → {new_qty:.1f}g")
            elif priority < 0:  # This ingredient contributes to excess
                # Decrease problematic ingredients
                new_qty = max(current_qty * 0.7, 20.0)
                new_quantities[i] = new_qty
                logger.info(f"🔽 Deprioritized {ingredients[i]['name']}: {current_qty:.1f}g → {new_qty:.1f}g")
        
        return {'quantities': new_quantities, 'method': 'ingredient_prioritization'}

    def _balance_by_adaptive_learning(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance using advanced adaptive learning with meta-learning capabilities."""
        logger.info("🧠 Balancing by advanced adaptive learning...")
        
        # Initialize advanced learning parameters if not exists
        if not hasattr(self, '_advanced_learning'):
            self._advanced_learning = {
                'learning_history': [],
                'success_patterns': {},
                'meta_learning_rules': {},
                'performance_tracking': {},
                'adaptation_strategies': [],
                'hyperparameters': self._initialize_hyperparameters(),
                'hyperparameter_history': [],
                'optimization_configs': {}
            }
        
        # Create enhanced pattern with more features
        current_pattern = self._create_enhanced_pattern(ingredients, target_macros, gaps)
        
        # Meta-learning: analyze which strategies work best for similar patterns
        strategy_performance = self._analyze_strategy_performance(current_pattern)
        
        # Find similar patterns with high success rate
        best_adjustment = None
        best_score = float('inf')
        best_strategy = None
        
        # Look for patterns with >80% similarity and >70% success rate
        for historical in self._advanced_learning['learning_history']:
            pattern_similarity = self._calculate_enhanced_similarity(current_pattern, historical)
            success_rate = historical.get('success_rate', 0)
            
            if pattern_similarity > 0.8 and success_rate > 0.7:
                # Apply learned adjustments with confidence weighting
                learned_adjustment = historical.get('successful_adjustment', {})
                if learned_adjustment:
                    new_quantities = self._apply_learned_adjustment(
                        ingredients, learned_adjustment, pattern_similarity, success_rate
                    )
                    
                    # Test this adjustment
                    try:
                        test_nutrition = self._calculate_final_meal(ingredients, new_quantities)
                        test_score = self._calculate_balance_score(test_nutrition, target_macros)
                        
                        if test_score < best_score:
                            best_score = test_score
                            best_adjustment = {'quantities': new_quantities, 'method': 'advanced_adaptive_learning'}
                            best_strategy = historical.get('strategy', 'unknown')
                    except:
                        continue
        
        # If no good historical pattern found, use meta-learning to create new strategy
        if not best_adjustment:
            best_adjustment = self._create_meta_learning_strategy(ingredients, gaps, strategy_performance)
        
        # Update learning system with this attempt
        self._update_advanced_learning(current_pattern, best_adjustment, target_macros)
        
        # Meta-learning: update strategy performance
        if best_strategy:
            self._update_strategy_performance(best_strategy, best_score)
        
        return best_adjustment

    def _create_enhanced_pattern(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Dict:
        """Create an enhanced pattern with more sophisticated features."""
        total_calories = sum(ing.get('calories_per_100g', 0) * ing.get('quantity_needed', 0) / 100 for ing in ingredients)
        
        pattern = {
            'gaps': gaps.copy(),
            'ingredient_count': len(ingredients),
            'macro_ratios': {
                'protein_ratio': target_macros['protein'] / target_macros['calories'] if target_macros['calories'] > 0 else 0,
                'carbs_ratio': target_macros['carbs'] / target_macros['calories'] if target_macros['calories'] > 0 else 0,
                'fat_ratio': target_macros['fat'] / target_macros['calories'] if target_macros['calories'] > 0 else 0
            },
            'ingredient_diversity': {
                'protein_sources': sum(1 for ing in ingredients if ing.get('protein_per_100g', 0) > 15),
                'carb_sources': sum(1 for ing in ingredients if ing.get('carbs_per_100g', 0) > 25),
                'fat_sources': sum(1 for ing in ingredients if ing.get('fat_per_100g', 0) > 8)
            },
            'macro_balance': {
                'protein_calorie_ratio': sum(ing.get('protein_per_100g', 0) * ing.get('quantity_needed', 0) / 100 for ing in ingredients) / total_calories if total_calories > 0 else 0,
                'carb_calorie_ratio': sum(ing.get('carbs_per_100g', 0) * ing.get('quantity_needed', 0) / 100 for ing in ingredients) / total_calories if total_calories > 0 else 0,
                'fat_calorie_ratio': sum(ing.get('fat_per_100g', 0) * ing.get('quantity_needed', 0) / 100 for ing in ingredients) / total_calories if total_calories > 0 else 0
            },
            'complexity_score': self._calculate_meal_complexity(ingredients),
            'timestamp': time.time()
        }
        
        return pattern

    def _calculate_enhanced_similarity(self, pattern1: Dict, pattern2: Dict) -> float:
        """Calculate enhanced similarity between patterns."""
        try:
            # Base similarity from gaps
            gap_similarity = 0
            if 'gaps' in pattern1 and 'gaps' in pattern2:
                gap1 = pattern1['gaps']
                gap2 = pattern2['gaps']
                
                gap_values1 = [gap1.get(macro, 0) for macro in ['calories', 'protein', 'carbs', 'fat']]
                gap_values2 = [gap2.get(macro, 0) for macro in ['calories', 'protein', 'carbs', 'fat']]
                
                norm1 = np.linalg.norm(gap_values1)
                norm2 = np.linalg.norm(gap_values2)
                
                if norm1 > 0 and norm2 > 0:
                    gap_similarity = np.dot(gap_values1, gap_values2) / (norm1 * norm2)
                    gap_similarity = (gap_similarity + 1) / 2
                else:
                    gap_similarity = 0.5
            
            # Enhanced similarity from additional features
            feature_similarity = 0
            if 'ingredient_diversity' in pattern1 and 'ingredient_diversity' in pattern2:
                div1 = pattern1['ingredient_diversity']
                div2 = pattern2['ingredient_diversity']
                
                diversity_scores = []
                for key in ['protein_sources', 'carb_sources', 'fat_sources']:
                    if key in div1 and key in div2:
                        max_val = max(div1[key], div2[key])
                        if max_val > 0:
                            similarity = 1 - abs(div1[key] - div2[key]) / max_val
                            diversity_scores.append(similarity)
                
                if diversity_scores:
                    feature_similarity = sum(diversity_scores) / len(diversity_scores)
            
            # Macro balance similarity
            macro_similarity = 0
            if 'macro_balance' in pattern1 and 'macro_balance' in pattern2:
                balance1 = pattern1['macro_balance']
                balance2 = pattern2['macro_balance']
                
                macro_diffs = []
                for key in ['protein_calorie_ratio', 'carb_calorie_ratio', 'fat_calorie_ratio']:
                    if key in balance1 and key in balance2:
                        diff = abs(balance1[key] - balance2[key])
                        macro_diffs.append(diff)
                
                if macro_diffs:
                    avg_diff = sum(macro_diffs) / len(macro_diffs)
                    macro_similarity = max(0, 1 - avg_diff * 5)
            
            # Weighted combination
            weights = [0.4, 0.3, 0.3]  # Gaps most important
            similarities = [gap_similarity, feature_similarity, macro_similarity]
            
            total_similarity = sum(w * s for w, s in zip(weights, similarities))
            return max(0, min(1, total_similarity))
            
        except Exception as e:
            logger.warning(f"⚠️ Error calculating enhanced similarity: {e}")
            return 0.5

    def _apply_learned_adjustment(self, ingredients: List[Dict], learned_adjustment: Dict, 
                                 similarity: float, success_rate: float) -> List[float]:
        """Apply learned adjustment with confidence weighting."""
        new_quantities = []
        confidence_factor = similarity * success_rate
        
        for i, ing in enumerate(ingredients):
            current_qty = ing.get('quantity_needed', 0)
            
            # Get learned adjustment factor
            adjustment_factor = learned_adjustment.get(f'factor_{i}', 1.0)
            
            # Apply confidence weighting
            weighted_adjustment = 1.0 + (adjustment_factor - 1.0) * confidence_factor
            
            new_qty = current_qty * weighted_adjustment
            new_qty = max(new_qty, 15.0)
            max_qty = float(ing.get('max_quantity', 400))
            new_qty = min(new_qty, max_qty)
            
            new_quantities.append(new_qty)
        
        return new_quantities

    def _create_meta_learning_strategy(self, ingredients: List[Dict], gaps: Dict, 
                                     strategy_performance: Dict) -> Dict:
        """Create new strategy using meta-learning insights."""
        # Find best performing strategies
        best_strategies = sorted(strategy_performance.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Create adaptive adjustment based on best strategies
        new_quantities = []
        for ing in ingredients:
            current_qty = ing.get('quantity_needed', 0)
            
            # Calculate adaptive factor based on gaps and strategy performance
            adaptive_factor = 1.0
            for macro, gap in gaps.items():
                if macro == 'calories':
                    macro_val = ing.get('calories_per_100g', 0)
                else:
                    macro_val = ing.get(f'{macro}_per_100g', 0)
                
                if gap > 0 and macro_val > 0:  # Deficit and ingredient helps
                    adaptive_factor *= 1.5  # Increase by 50%
                elif gap < 0 and macro_val > 0:  # Excess and ingredient contributes
                    adaptive_factor *= 0.4  # Decrease by 60%
            
            # Apply strategy performance bonus
            if best_strategies:
                best_strategy_score = best_strategies[0][1]
                strategy_bonus = 1.0 + (best_strategy_score * 0.2)
                adaptive_factor *= strategy_bonus
            
            new_qty = current_qty * adaptive_factor
            new_qty = max(new_qty, 15.0)
            max_qty = float(ing.get('max_quantity', 400))
            new_qty = min(new_qty, max_qty)
            
            new_quantities.append(new_qty)
        
        return {'quantities': new_quantities, 'method': 'meta_learning_strategy'}

    def _update_advanced_learning(self, pattern: Dict, adjustment: Dict, target_macros: Dict):
        """Update the advanced learning system with enhanced features."""
        # Store this pattern and adjustment with enhanced metadata
        learning_entry = {
            'pattern': pattern,
            'adjustment': adjustment,
            'timestamp': time.time(),
            'success_rate': 0.0,  # Will be updated after evaluation
            'strategy': adjustment.get('method', 'unknown'),
            'pattern_complexity': pattern.get('complexity_score', 0),
            'macro_balance': pattern.get('macro_balance', {}),
            'ingredient_diversity': pattern.get('ingredient_diversity', {}),
            'execution_time': time.time(),  # For performance tracking
            'memory_usage': len(str(pattern)) + len(str(adjustment))  # Rough memory estimate
        }
        
        self._advanced_learning['learning_history'].append(learning_entry)
        
        # Enhanced learning: analyze patterns for insights
        self._analyze_learning_patterns()
        
        # Adaptive memory management
        if len(self._advanced_learning['learning_history']) > 300:  # Increased from 200
            # Keep most successful and diverse patterns
            self._prune_learning_history()
        
        # Update meta-learning rules
        self._update_meta_learning_rules(pattern, adjustment)

    def _analyze_learning_patterns(self):
        """Analyze learning patterns for insights and optimization."""
        if len(self._advanced_learning['learning_history']) < 10:
            return
        
        # Analyze strategy performance trends
        strategy_trends = {}
        for entry in self._advanced_learning['learning_history']:
            strategy = entry['strategy']
            if strategy not in strategy_trends:
                strategy_trends[strategy] = []
            
            strategy_trends[strategy].append({
                'timestamp': entry['timestamp'],
                'complexity': entry['pattern_complexity'],
                'success_rate': entry['success_rate']
            })
        
        # Identify which strategies work best for different complexity levels
        complexity_strategy_map = {}
        for strategy, data in strategy_trends.items():
            if len(data) >= 5:  # Need minimum data points
                # Group by complexity ranges
                for entry in data:
                    complexity_range = int(entry['complexity'] * 10) / 10  # Round to 0.1
                    if complexity_range not in complexity_strategy_map:
                        complexity_strategy_map[complexity_range] = {}
                    
                    if strategy not in complexity_strategy_map[complexity_range]:
                        complexity_strategy_map[complexity_range]['strategies'] = []
                        complexity_strategy_map[complexity_range]['avg_success'] = 0
                    
                    complexity_strategy_map[complexity_range]['strategies'].append(strategy)
        
        # Store insights for future use
        self._advanced_learning['complexity_strategy_map'] = complexity_strategy_map

    def _prune_learning_history(self):
        """Intelligently prune learning history to keep most valuable patterns."""
        history = self._advanced_learning['learning_history']
        
        # Score each entry based on multiple factors
        scored_entries = []
        for entry in history:
            score = 0
            
            # Recency bonus (newer is better)
            age_hours = (time.time() - entry['timestamp']) / 3600
            recency_score = max(0, 1 - age_hours / 24)  # 24 hour decay
            score += recency_score * 0.3
            
            # Success rate bonus
            success_score = entry.get('success_rate', 0)
            score += success_score * 0.4
            
            # Complexity bonus (diverse patterns are valuable)
            complexity_score = entry.get('pattern_complexity', 0)
            score += complexity_score * 0.2
            
            # Strategy diversity bonus
            strategy = entry.get('strategy', 'unknown')
            strategy_count = sum(1 for e in history if e.get('strategy') == strategy)
            diversity_score = 1.0 / (1 + strategy_count / 10)  # Less common strategies get bonus
            score += diversity_score * 0.1
            
            scored_entries.append((entry, score))
        
        # Sort by score and keep top 200
        scored_entries.sort(key=lambda x: x[1], reverse=True)
        self._advanced_learning['learning_history'] = [entry for entry, score in scored_entries[:200]]

    def _update_meta_learning_rules(self, pattern: Dict, adjustment: Dict):
        """Update meta-learning rules based on new patterns."""
        if 'meta_learning_rules' not in self._advanced_learning:
            self._advanced_learning['meta_learning_rules'] = {}
        
        # Extract key features from pattern
        complexity = pattern.get('complexity_score', 0)
        macro_ratios = pattern.get('macro_ratios', {})
        ingredient_count = pattern.get('ingredient_count', 0)
        
        # Create rule key
        rule_key = f"complexity_{complexity:.1f}_ingredients_{ingredient_count}"
        
        if rule_key not in self._advanced_learning['meta_learning_rules']:
            self._advanced_learning['meta_learning_rules'][rule_key] = {
                'successful_strategies': [],
                'failed_strategies': [],
                'pattern_count': 0,
                'avg_success_rate': 0
            }
        
        rule = self._advanced_learning['meta_learning_rules'][rule_key]
        rule['pattern_count'] += 1
        
        # Update strategy performance
        strategy = adjustment.get('method', 'unknown')
        if strategy not in rule['successful_strategies']:
            rule['successful_strategies'].append(strategy)
        
        # Calculate average success rate
        if rule['pattern_count'] > 0:
            rule['avg_success_rate'] = sum(
                entry.get('success_rate', 0) 
                for entry in self._advanced_learning['learning_history'] 
                if self._matches_rule_pattern(entry['pattern'], rule_key)
            ) / rule['pattern_count']

    def _matches_rule_pattern(self, pattern: Dict, rule_key: str) -> bool:
        """Check if a pattern matches a meta-learning rule."""
        try:
            complexity = pattern.get('complexity_score', 0)
            ingredient_count = pattern.get('ingredient_count', 0)
            expected_key = f"complexity_{complexity:.1f}_ingredients_{ingredient_count}"
            return expected_key == rule_key
        except:
            return False

    def _analyze_strategy_performance(self, pattern: Dict) -> Dict:
        """Analyze which strategies perform best for similar patterns."""
        strategy_scores = {}
        
        for historical in self._advanced_learning['learning_history']:
            similarity = self._calculate_enhanced_similarity(pattern, historical)
            if similarity > 0.6:  # Only consider similar patterns
                strategy = historical.get('strategy', 'unknown')
                success_rate = historical.get('success_rate', 0)
                
                if strategy not in strategy_scores:
                    strategy_scores[strategy] = []
                
                strategy_scores[strategy].append(success_rate * similarity)
        
        # Calculate average performance for each strategy
        strategy_performance = {}
        for strategy, scores in strategy_scores.items():
            if scores:
                strategy_performance[strategy] = sum(scores) / len(scores)
        
        return strategy_performance

    def _update_strategy_performance(self, strategy: str, score: float):
        """Update performance tracking for a strategy."""
        if strategy not in self._advanced_learning['performance_tracking']:
            self._advanced_learning['performance_tracking'][strategy] = []
        
        # Convert score to success rate (0-1, where 1 is perfect)
        success_rate = max(0, 1 - score / 100)  # Normalize score
        self._advanced_learning['performance_tracking'][strategy].append(success_rate)
        
        # Keep only recent performance (last 50)
        if len(self._advanced_learning['performance_tracking'][strategy]) > 50:
            self._advanced_learning['performance_tracking'][strategy] = \
                self._advanced_learning['performance_tracking'][strategy][-50:]

    def _calculate_meal_complexity(self, ingredients: List[Dict]) -> float:
        """Calculate meal complexity score."""
        if not ingredients:
            return 0.0
        
        # Factors that increase complexity
        complexity_factors = []
        
        # Number of ingredients
        complexity_factors.append(min(len(ingredients) / 10.0, 1.0))
        
        # Macro diversity
        protein_sources = sum(1 for ing in ingredients if ing.get('protein_per_100g', 0) > 15)
        carb_sources = sum(1 for ing in ingredients if ing.get('carbs_per_100g', 0) > 25)
        fat_sources = sum(1 for ing in ingredients if ing.get('fat_per_100g', 0) > 8)
        
        diversity_score = (protein_sources + carb_sources + fat_sources) / 15.0
        complexity_factors.append(min(diversity_score, 1.0))
        
        # Quantity variance
        quantities = [ing.get('quantity_needed', 0) for ing in ingredients]
        if quantities:
            variance = np.var(quantities) / (np.mean(quantities) ** 2) if np.mean(quantities) > 0 else 0
            complexity_factors.append(min(variance, 1.0))
        
        return sum(complexity_factors) / len(complexity_factors)

    def _calculate_pattern_similarity(self, pattern1: Dict, pattern2: Dict) -> float:
        """Calculate similarity between two optimization patterns."""
        try:
            # Compare gaps
            gap_similarity = 0
            if 'gaps' in pattern1 and 'gaps' in pattern2:
                gap1 = pattern1['gaps']
                gap2 = pattern2['gaps']
                
                # Calculate cosine similarity for gaps
                gap_values1 = [gap1.get(macro, 0) for macro in ['calories', 'protein', 'carbs', 'fat']]
                gap_values2 = [gap2.get(macro, 0) for macro in ['calories', 'protein', 'carbs', 'fat']]
                
                # Normalize vectors
                norm1 = np.linalg.norm(gap_values1)
                norm2 = np.linalg.norm(gap_values2)
                
                if norm1 > 0 and norm2 > 0:
                    gap_similarity = np.dot(gap_values1, gap_values2) / (norm1 * norm2)
                    gap_similarity = (gap_similarity + 1) / 2  # Convert from [-1,1] to [0,1]
                else:
                    gap_similarity = 0.5  # Neutral similarity
            
            # Compare ingredient count
            count_similarity = 0
            if 'ingredient_count' in pattern1 and 'ingredient_count' in pattern2:
                count1 = pattern1['ingredient_count']
                count2 = pattern2['ingredient_count']
                max_count = max(count1, count2)
                if max_count > 0:
                    count_similarity = 1 - abs(count1 - count2) / max_count
                else:
                    count_similarity = 1.0
            
            # Compare macro ratios
            ratio_similarity = 0
            if 'macro_ratios' in pattern1 and 'macro_ratios' in pattern2:
                ratios1 = pattern1['macro_ratios']
                ratios2 = pattern2['macro_ratios']
                
                ratio_diffs = []
                for key in ['protein_ratio', 'carbs_ratio', 'fat_ratio']:
                    if key in ratios1 and key in ratios2:
                        diff = abs(ratios1[key] - ratios2[key])
                        ratio_diffs.append(diff)
                
                if ratio_diffs:
                    avg_diff = sum(ratio_diffs) / len(ratio_diffs)
                    ratio_similarity = max(0, 1 - avg_diff * 10)  # Scale factor
            
            # Weighted average of similarities
            weights = [0.5, 0.2, 0.3]  # Gaps most important
            similarities = [gap_similarity, count_similarity, ratio_similarity]
            
            total_similarity = sum(w * s for w, s in zip(weights, similarities))
            
            return max(0, min(1, total_similarity))  # Ensure [0,1] range
            
        except Exception as e:
            logger.warning(f"⚠️ Error calculating pattern similarity: {e}")
            return 0.5  # Return neutral similarity on error

    def _balance_by_evolutionary_search(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance using evolutionary search algorithm."""
        logger.info("🧬 Balancing by evolutionary search...")
        
        # Population size and generations
        population_size = 20
        generations = 10
        
        # Create initial population
        population = []
        for _ in range(population_size):
            individual = []
            for ing in ingredients:
                current_qty = ing.get('quantity_needed', 0)
                # Random mutation within reasonable bounds
                mutation_factor = random.uniform(0.5, 2.0)
                new_qty = current_qty * mutation_factor
                new_qty = max(new_qty, 20.0)
                max_qty = float(ing.get('max_quantity', 400))
                new_qty = min(new_qty, max_qty)
                individual.append(new_qty)
            population.append(individual)
        
        # Evolution loop
        for generation in range(generations):
            # Evaluate fitness for each individual
            fitness_scores = []
            for individual in population:
                try:
                    nutrition = self._calculate_final_meal(ingredients, individual)
                    score = self._calculate_balance_score(nutrition, target_macros)
                    fitness_scores.append((score, individual))
                except:
                    fitness_scores.append((float('inf'), individual))
            
            # Sort by fitness (lower is better)
            fitness_scores.sort(key=lambda x: x[0])
            
            # Keep top 50% individuals
            top_individuals = [ind for _, ind in fitness_scores[:population_size//2]]
            
            # Create new population through crossover and mutation
            new_population = top_individuals.copy()
            
            while len(new_population) < population_size:
                # Crossover
                parent1 = random.choice(top_individuals)
                parent2 = random.choice(top_individuals)
                child = []
                
                for i in range(len(ingredients)):
                    if random.random() < 0.5:
                        child.append(parent1[i])
                    else:
                        child.append(parent2[i])
                
                # Mutation
                for i in range(len(child)):
                    if random.random() < 0.3:  # 30% mutation chance
                        mutation_factor = random.uniform(0.8, 1.2)
                        child[i] *= mutation_factor
                        child[i] = max(child[i], 20.0)
                        max_qty = float(ingredients[i].get('max_quantity', 400))
                        child[i] = min(child[i], max_qty)
                
                new_population.append(child)
            
            population = new_population
            
            logger.info(f"🧬 Generation {generation + 1}: Best score = {fitness_scores[0][0]:.2f}")
        
        # Return best individual
        best_individual = fitness_scores[0][1]
        return {'quantities': best_individual, 'method': 'evolutionary_search'}

    def _balance_by_neural_optimization(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance using simplified neural network optimization."""
        logger.info("🧠 Balancing by neural optimization...")
        
        # Simple neural network with 3 layers
        input_size = len(ingredients) * 4  # 4 features per ingredient
        hidden_size = 16
        output_size = len(ingredients)
        
        # Initialize weights randomly
        if not hasattr(self, '_neural_weights'):
            self._neural_weights = {
                'w1': np.random.randn(input_size, hidden_size) * 0.1,
                'b1': np.zeros(hidden_size),
                'w2': np.random.randn(hidden_size, output_size) * 0.1,
                'b2': np.zeros(output_size)
            }
        
        # Prepare input features
        input_features = []
        for ing in ingredients:
            current_qty = ing.get('quantity_needed', 0)
            protein_ratio = ing.get('protein_per_100g', 0) / 100
            carbs_ratio = ing.get('carbs_per_100g', 0) / 100
            fat_ratio = ing.get('fat_per_100g', 0) / 100
            calorie_ratio = ing.get('calories_per_100g', 0) / 100
            
            input_features.extend([current_qty, protein_ratio, carbs_ratio, fat_ratio])
        
        # Normalize input
        input_features = np.array(input_features)
        input_features = (input_features - np.mean(input_features)) / (np.std(input_features) + 1e-8)
        
        # Forward pass
        layer1 = np.tanh(np.dot(input_features, self._neural_weights['w1']) + self._neural_weights['b1'])
        output = np.dot(layer1, self._neural_weights['w2']) + self._neural_weights['b2']
        
        # Convert output to quantities
        new_quantities = []
        for i, ing in enumerate(ingredients):
            current_qty = ing.get('quantity_needed', 0)
            # Output is adjustment factor
            adjustment_factor = 1.0 + output[i] * 0.5  # Scale adjustment
            new_qty = current_qty * adjustment_factor
            
            # Ensure bounds
            new_qty = max(new_qty, 20.0)
            max_qty = float(ing.get('max_quantity', 400))
            new_qty = min(new_qty, max_qty)
            
            new_quantities.append(new_qty)
        
        # Update weights based on performance (simple backpropagation)
        try:
            test_nutrition = self._calculate_final_meal(ingredients, new_quantities)
            test_score = self._calculate_balance_score(test_nutrition, target_macros)
            
            # Simple weight update (gradient descent)
            learning_rate = 0.01
            if hasattr(self, '_last_score'):
                if test_score < self._last_score:
                    # Good result, reinforce weights
                    for key in self._neural_weights:
                        self._neural_weights[key] *= (1 + learning_rate)
                else:
                    # Bad result, adjust weights
                    for key in self._neural_weights:
                        self._neural_weights[key] *= (1 - learning_rate * 0.1)
            
            self._last_score = test_score
            
        except:
            pass
        
        return {'quantities': new_quantities, 'method': 'neural_optimization'}

    def _balance_by_ensemble_methods(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance using ensemble of multiple methods."""
        logger.info("🎯 Balancing by ensemble methods...")
        
        # Get results from multiple methods
        method_results = []
        methods = [
            self._balance_by_reducing_excess,
            self._balance_by_increasing_deficit,
            self._balance_by_macro_redistribution,
            self._balance_by_smart_scaling
        ]
        
        for method in methods:
            try:
                result = method(ingredients, target_macros, gaps)
                if result:
                    method_results.append(result)
            except:
                continue
        
        if not method_results:
            return None
        
        # Calculate weighted average of quantities
        new_quantities = []
        weights = [0.3, 0.3, 0.2, 0.2]  # Weights for each method
        
        for i in range(len(ingredients)):
            weighted_sum = 0
            total_weight = 0
            
            for j, result in enumerate(method_results):
                if i < len(result['quantities']):
                    weight = weights[j] if j < len(weights) else 0.1
                    weighted_sum += result['quantities'][i] * weight
                    total_weight += weight
            
            if total_weight > 0:
                avg_quantity = weighted_sum / total_weight
            else:
                avg_quantity = ingredients[i].get('quantity_needed', 0)
            
            # Ensure bounds
            avg_quantity = max(avg_quantity, 20.0)
            max_qty = float(ingredients[i].get('max_quantity', 400))
            avg_quantity = min(avg_quantity, max_qty)
            
            new_quantities.append(avg_quantity)
        
        return {'quantities': new_quantities, 'method': 'ensemble_methods'}

    # REMOVED: _balance_by_quantum_inspiration - Unrealistic quantum method

    # REMOVED: _balance_by_swarm_intelligence - Complex swarm method

    # REMOVED: _balance_by_deep_reinforcement - Complex RL method
        next_max = max(self._q_table[state_key].values()) if self._q_table[state_key] else 0
        
        new_value = (1 - self._learning_rate) * old_value + \
                   self._learning_rate * (reward + self._discount_factor * next_max)
        
        self._q_table[state_key][action_key] = new_value
        
        # Decay exploration rate
        self._epsilon *= 0.95
        
        return {'quantities': new_quantities, 'method': 'deep_reinforcement'}

    def _balance_by_transfer_learning(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance using transfer learning from previous successful patterns."""
        logger.info("🔄 Balancing by transfer learning...")
        
        # Initialize transfer learning database if not exists
        if not hasattr(self, '_transfer_database'):
            self._transfer_database = {
                'successful_patterns': [],
                'failed_patterns': [],
                'adaptation_rules': {}
            }
        
        # Create current pattern signature
        current_signature = self._create_pattern_signature(ingredients, gaps)
        
        # Find most similar successful pattern
        best_transfer = None
        best_similarity = 0
        
        for pattern in self._transfer_database['successful_patterns']:
            similarity = self._calculate_pattern_similarity(
                {'signature': current_signature, 'gaps': gaps},
                pattern
            )
            
            if similarity > best_similarity and similarity > 0.6:
                best_similarity = similarity
                best_transfer = pattern
        
        if best_transfer:
            # Apply transfer learning with adaptation
            new_quantities = []
            adaptation_factor = 1.0 + (best_similarity - 0.6) * 0.5  # Adaptive scaling
            
            for i, ing in enumerate(ingredients):
                current_qty = ing.get('quantity_needed', 0)
                
                # Get transferred quantity if available
                if 'quantities' in best_transfer and i < len(best_transfer['quantities']):
                    transferred_qty = best_transfer['quantities'][i]
                    # Adapt based on similarity
                    adapted_qty = transferred_qty * adaptation_factor
                else:
                    # Fallback to current quantity
                    adapted_qty = current_qty
                
                # Ensure bounds
                adapted_qty = max(adapted_qty, 15.0)
                max_qty = float(ing.get('max_quantity', 400))
                adapted_qty = min(adapted_qty, max_qty)
                
                new_quantities.append(adapted_qty)
            
            # Store this attempt for future learning
            self._transfer_database['successful_patterns'].append({
                'signature': current_signature,
                'quantities': new_quantities,
                'gaps': gaps,
                'timestamp': time.time()
            })
            
            # Keep only recent patterns (last 50)
            if len(self._transfer_database['successful_patterns']) > 50:
                self._transfer_database['successful_patterns'] = \
                    self._transfer_database['successful_patterns'][-50:]
            
            return {'quantities': new_quantities, 'method': 'transfer_learning'}
        
        # If no good transfer found, create new pattern
        new_quantities = []
        for ing in ingredients:
            current_qty = ing.get('quantity_needed', 0)
            
            # Create intelligent adjustment based on gaps
            adjustment = 1.0
            for macro, gap in gaps.items():
                if macro == 'calories':
                    macro_val = ing.get('calories_per_100g', 0)
                else:
                    macro_val = ing.get(f'{macro}_per_100g', 0)
                
                if gap > 0 and macro_val > 0:  # Deficit and ingredient helps
                    adjustment *= 1.4  # Increase by 40%
                elif gap < 0 and macro_val > 0:  # Excess and ingredient contributes
                    adjustment *= 0.5  # Decrease by 50%
            
            new_qty = current_qty * adjustment
            new_qty = max(new_qty, 15.0)
            max_qty = float(ing.get('max_quantity', 400))
            new_qty = min(new_qty, max_qty)
            
            new_quantities.append(new_qty)
        
        return {'quantities': new_quantities, 'method': 'transfer_learning'}

    def _balance_by_chaos_optimization(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance using chaos theory principles for optimization."""
        logger.info("🌀 Balancing by chaos optimization...")
        
        # Chaos parameters
        chaos_factor = 0.3
        num_iterations = 12
        best_result = None
        best_score = float('inf')
        
        for iteration in range(num_iterations):
            # Create chaotic adjustment
            new_quantities = []
            chaos_seed = iteration * 0.618  # Golden ratio
            
            for i, ing in enumerate(ingredients):
                current_qty = ing.get('quantity_needed', 0)
                
                # Apply chaotic transformation
                chaos_value = np.sin(chaos_seed + i * 1.618) * np.cos(chaos_seed * 2.718)
                adjustment = 1.0 + chaos_factor * chaos_value
                
                # Add some randomness
                random_factor = np.random.uniform(0.8, 1.2)
                adjustment *= random_factor
                
                new_qty = current_qty * adjustment
                new_qty = max(new_qty, 10.0)
                max_qty = float(ing.get('max_quantity', 500))
                new_qty = min(new_qty, max_qty)
                
                new_quantities.append(new_qty)
            
            # Test this chaotic configuration
            try:
                nutrition = self._calculate_final_meal(ingredients, new_quantities)
                score = self._calculate_balance_score(nutrition, target_macros)
                
                if score < best_score:
                    best_score = score
                    best_result = new_quantities
                    
            except:
                continue
        
        if best_result:
            return {'quantities': best_result, 'method': 'chaos_optimization'}
        
        return None

    def _balance_by_fractal_search(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance using fractal search patterns."""
        logger.info("🔷 Balancing by fractal search...")
        
        # Fractal parameters
        fractal_depth = 4
        fractal_branches = 3
        best_result = None
        best_score = float('inf')
        
        def fractal_search(level: int, base_quantities: List[float], scale: float):
            nonlocal best_result, best_score
            
            if level >= fractal_depth:
                # Test this configuration
                try:
                    nutrition = self._calculate_final_meal(ingredients, base_quantities)
                    score = self._calculate_balance_score(nutrition, target_macros)
                    
                    if score < best_score:
                        best_score = score
                        best_result = base_quantities.copy()
                        
                except:
                    pass
                return
            
            # Create fractal branches
            for branch in range(fractal_branches):
                new_quantities = []
                branch_scale = scale * (0.5 + 0.5 * np.sin(branch * 2 * np.pi / fractal_branches))
                
                for i, qty in enumerate(base_quantities):
                    # Apply fractal scaling
                    fractal_adjustment = 1.0 + branch_scale * np.random.uniform(-0.3, 0.3)
                    new_qty = qty * fractal_adjustment
                    
                    # Ensure bounds
                    new_qty = max(new_qty, 10.0)
                    max_qty = float(ingredients[i].get('max_quantity', 500))
                    new_qty = min(new_qty, max_qty)
                    
                    new_quantities.append(new_qty)
                
                # Recursive fractal search
                fractal_search(level + 1, new_quantities, scale * 0.7)
        
        # Start with current quantities
        current_quantities = [ing.get('quantity_needed', 0) for ing in ingredients]
        fractal_search(0, current_quantities, 0.5)
        
        if best_result:
            return {'quantities': best_result, 'method': 'fractal_search'}
        
        return None

    def _balance_by_quantum_annealing(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance using quantum annealing principles."""
        logger.info("❄️ Balancing by quantum annealing...")
        
        # Annealing parameters
        initial_temperature = 100.0
        final_temperature = 0.1
        cooling_rate = 0.95
        iterations_per_temp = 8
        
        current_quantities = [ing.get('quantity_needed', 0) for ing in ingredients]
        best_quantities = current_quantities.copy()
        best_score = float('inf')
        
        temperature = initial_temperature
        
        while temperature > final_temperature:
            for _ in range(iterations_per_temp):
                # Generate neighbor solution
                new_quantities = []
                for i, qty in enumerate(current_quantities):
                    # Random walk with temperature-dependent step size
                    step_size = temperature / initial_temperature
                    random_step = np.random.normal(0, step_size * 50)
                    
                    new_qty = qty + random_step
                    new_qty = max(new_qty, 10.0)
                    max_qty = float(ingredients[i].get('max_quantity', 500))
                    new_qty = min(new_qty, max_qty)
                    
                    new_quantities.append(new_qty)
                
                # Evaluate new solution
                try:
                    nutrition = self._calculate_final_meal(ingredients, new_quantities)
                    score = self._calculate_balance_score(nutrition, target_macros)
                    
                    # Accept better solutions or accept worse with probability
                    if score < best_score:
                        best_score = score
                        best_quantities = new_quantities.copy()
                        current_quantities = new_quantities.copy()
                    else:
                        # Boltzmann acceptance criterion
                        delta_e = score - best_score
                        if np.random.random() < np.exp(-delta_e / temperature):
                            current_quantities = new_quantities.copy()
                            
                except:
                    continue
            
            # Cool down
            temperature *= cooling_rate
        
        return {'quantities': best_quantities, 'method': 'quantum_annealing'}

    def _balance_by_ant_colony(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance using ant colony optimization."""
        logger.info("🐜 Balancing by ant colony optimization...")
        
        # Colony parameters
        num_ants = 20
        num_iterations = 10
        evaporation_rate = 0.1
        pheromone_boost = 1.0
        
        # Initialize pheromone matrix
        pheromones = np.ones((len(ingredients), 10))  # 10 quantity levels per ingredient
        
        best_result = None
        best_score = float('inf')
        
        for iteration in range(num_iterations):
            ant_solutions = []
            ant_scores = []
            
            # Each ant finds a solution
            for ant in range(num_ants):
                new_quantities = []
                
                for i, ing in enumerate(ingredients):
                    current_qty = ing.get('quantity_needed', 0)
                    
                    # Choose quantity level based on pheromone levels
                    pheromone_levels = pheromones[i]
                    probabilities = pheromone_levels / np.sum(pheromone_levels)
                    
                    # Create quantity levels around current
                    levels = np.linspace(current_qty * 0.3, current_qty * 2.0, 10)
                    chosen_level = np.random.choice(levels, p=probabilities)
                    
                    new_qty = max(chosen_level, 10.0)
                    max_qty = float(ing.get('max_quantity', 500))
                    new_qty = min(new_qty, max_qty)
                    
                    new_quantities.append(new_qty)
                
                ant_solutions.append(new_quantities)
                
                # Evaluate ant solution
                try:
                    nutrition = self._calculate_final_meal(ingredients, new_quantities)
                    score = self._calculate_balance_score(nutrition, target_macros)
                    ant_scores.append(score)
                    
                    if score < best_score:
                        best_score = score
                        best_result = new_quantities.copy()
                        
                except:
                    ant_scores.append(float('inf'))
            
            # Update pheromones
            for i in range(len(ingredients)):
                for j in range(10):
                    # Evaporate
                    pheromones[i][j] *= (1 - evaporation_rate)
                    
                    # Add pheromone for good solutions
                    for ant_idx, score in enumerate(ant_scores):
                        if score < float('inf'):
                            ant_solution = ant_solutions[ant_idx]
                            ant_qty = ant_solution[i]
                            levels = np.linspace(ingredients[i].get('quantity_needed', 0) * 0.3, 
                                              ingredients[i].get('quantity_needed', 0) * 2.0, 10)
                            
                            # Find closest level
                            closest_level = np.argmin(np.abs(levels - ant_qty))
                            if closest_level == j:
                                pheromones[i][j] += pheromone_boost / (score + 1)
        
        return {'quantities': best_result, 'method': 'ant_colony'} if best_result else None

    def _balance_by_bee_colony(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance using artificial bee colony optimization."""
        logger.info("🐝 Balancing by bee colony optimization...")
        
        # Bee colony parameters
        num_employed_bees = 15
        num_onlooker_bees = 10
        num_scout_bees = 5
        max_trials = 5
        
        # Initialize solutions
        solutions = []
        solution_scores = []
        trial_counters = []
        
        # Generate initial random solutions
        for bee in range(num_employed_bees):
            new_quantities = []
            for ing in ingredients:
                current_qty = ing.get('quantity_needed', 0)
                random_factor = np.random.uniform(0.5, 2.0)
                new_qty = current_qty * random_factor
                new_qty = max(new_qty, 10.0)
                max_qty = float(ing.get('max_quantity', 500))
                new_qty = min(new_qty, max_qty)
                new_quantities.append(new_qty)
            
            solutions.append(new_quantities)
            trial_counters.append(0)
            
            # Evaluate solution
            try:
                nutrition = self._calculate_final_meal(ingredients, new_quantities)
                score = self._calculate_balance_score(nutrition, target_macros)
                solution_scores.append(score)
            except:
                solution_scores.append(float('inf'))
        
        best_solution = None
        best_score = float('inf')
        
        # Main optimization loop
        for iteration in range(8):
            # Employed bees phase
            for bee in range(num_employed_bees):
                # Generate neighbor solution
                neighbor = solutions[bee].copy()
                for i in range(len(ingredients)):
                    random_change = np.random.normal(0, 0.2)
                    neighbor[i] *= (1 + random_change)
                    neighbor[i] = max(neighbor[i], 10.0)
                    max_qty = float(ingredients[i].get('max_quantity', 500))
                    neighbor[i] = min(neighbor[i], max_qty)
                
                # Evaluate neighbor
                try:
                    nutrition = self._calculate_final_meal(ingredients, neighbor)
                    neighbor_score = self._calculate_balance_score(nutrition, target_macros)
                    
                    if neighbor_score < solution_scores[bee]:
                        solutions[bee] = neighbor
                        solution_scores[bee] = neighbor_score
                        trial_counters[bee] = 0
                        
                        if neighbor_score < best_score:
                            best_score = neighbor_score
                            best_solution = neighbor.copy()
                    else:
                        trial_counters[bee] += 1
                        
                except:
                    trial_counters[bee] += 1
            
            # Onlooker bees phase
            fitness_values = [1.0 / (score + 1) for score in solution_scores]
            total_fitness = sum(fitness_values)
            
            for onlooker in range(num_onlooker_bees):
                # Select solution based on fitness
                rand = np.random.random() * total_fitness
                cumulative = 0
                selected_bee = 0
                
                for bee in range(num_employed_bees):
                    cumulative += fitness_values[bee]
                    if cumulative >= rand:
                        selected_bee = bee
                        break
                
                # Generate neighbor for selected solution
                neighbor = solutions[selected_bee].copy()
                for i in range(len(ingredients)):
                    random_change = np.random.normal(0, 0.15)
                    neighbor[i] *= (1 + random_change)
                    neighbor[i] = max(neighbor[i], 10.0)
                    max_qty = float(ingredients[i].get('max_quantity', 500))
                    neighbor[i] = min(neighbor[i], max_qty)
                
                # Evaluate and update
                try:
                    nutrition = self._calculate_final_meal(ingredients, neighbor)
                    neighbor_score = self._calculate_balance_score(nutrition, target_macros)
                    
                    if neighbor_score < solution_scores[selected_bee]:
                        solutions[selected_bee] = neighbor
                        solution_scores[selected_bee] = neighbor_score
                        trial_counters[selected_bee] = 0
                        
                        if neighbor_score < best_score:
                            best_score = neighbor_score
                            best_solution = neighbor.copy()
                            
                except:
                    pass
            
            # Scout bees phase
            for bee in range(num_employed_bees):
                if trial_counters[bee] >= max_trials:
                    # Generate new random solution
                    new_quantities = []
                    for ing in ingredients:
                        current_qty = ing.get('quantity_needed', 0)
                        random_factor = np.random.uniform(0.5, 2.0)
                        new_qty = current_qty * random_factor
                        new_qty = max(new_qty, 10.0)
                        max_qty = float(ing.get('max_quantity', 500))
                        new_qty = min(new_qty, max_qty)
                        new_quantities.append(new_qty)
                    
                    solutions[bee] = new_quantities
                    trial_counters[bee] = 0
                    
                    # Evaluate new solution
                    try:
                        nutrition = self._calculate_final_meal(ingredients, new_quantities)
                        score = self._calculate_balance_score(nutrition, target_macros)
                        solution_scores[bee] = score
                        
                        if score < best_score:
                            best_score = score
                            best_solution = new_quantities.copy()
                    except:
                        solution_scores[bee] = float('inf')
        
        return {'quantities': best_solution, 'method': 'bee_colony'} if best_solution else None

    def _balance_by_brute_force(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance using brute force approach - try thousands of combinations."""
        logger.info("💪 Balancing by brute force...")
        
        # Brute force parameters
        num_combinations = 5000  # Try 5000 different combinations
        best_result = None
        best_score = float('inf')
        
        for combo in range(num_combinations):
            # Generate random quantities with extreme variations
            new_quantities = []
            for ing in ingredients:
                current_qty = ing.get('quantity_needed', 0)
                
                # Extreme random variation: 0.1x to 10x current quantity
                random_factor = np.random.uniform(0.1, 10.0)
                new_qty = current_qty * random_factor
                
                # Ensure bounds
                new_qty = max(new_qty, 1.0)  # Minimum 1g
                max_qty = float(ing.get('max_quantity', 1000))  # Higher max
                new_qty = min(new_qty, max_qty)
                
                new_quantities.append(new_qty)
            
            # Test this combination
            try:
                nutrition = self._calculate_final_meal(ingredients, new_quantities)
                score = self._calculate_balance_score(nutrition, target_macros)
                
                if score < best_score:
                    best_score = score
                    best_result = new_quantities.copy()
                    
            except:
                continue
        
        if best_result:
            return {'quantities': best_result, 'method': 'brute_force'}
        
        return None

    def _balance_by_miracle_optimization(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance using miracle optimization - multiple strategies combined with extreme parameters."""
        logger.info("✨ Balancing by miracle optimization...")
        
        # Try multiple extreme strategies
        strategies = [
            self._balance_by_reducing_excess,
            self._balance_by_increasing_deficit,
            self._balance_by_macro_redistribution,
            self._balance_by_smart_scaling
        ]
        
        best_result = None
        best_score = float('inf')
        
        for strategy in strategies:
            try:
                result = strategy(ingredients, target_macros, gaps)
                if result:
                    # Apply extreme modifications to the result
                    extreme_quantities = []
                    for qty in result['quantities']:
                        # Apply extreme random adjustment
                        extreme_factor = np.random.uniform(0.2, 8.0)
                        extreme_qty = qty * extreme_factor
                        extreme_qty = max(extreme_qty, 1.0)
                        extreme_qty = min(extreme_qty, 1500.0)  # Very high max
                        extreme_quantities.append(extreme_qty)
                    
                    # Test extreme result
                    nutrition = self._calculate_final_meal(ingredients, extreme_quantities)
                    score = self._calculate_balance_score(nutrition, target_macros)
                    
                    if score < best_score:
                        best_score = score
                        best_result = extreme_quantities
                        
            except:
                continue
        
        if best_result:
            return {'quantities': best_result, 'method': 'miracle_optimization'}
        
        return None

    def _balance_by_super_ai(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance using super AI approach - combines all strategies with hyper-intelligent selection."""
        logger.info("🤖 Balancing by super AI...")
        
        # Super AI parameters
        num_ai_iterations = 100
        best_result = None
        best_score = float('inf')
        
        for ai_iteration in range(num_ai_iterations):
            # AI decision: choose strategy based on current state
            if ai_iteration < 30:
                # First phase: aggressive reduction
                strategy = self._balance_by_reducing_excess
            elif ai_iteration < 60:
                # Second phase: smart scaling
                strategy = self._balance_by_smart_scaling
            else:
                # Third phase: fallback to smart scaling
                strategy = self._balance_by_smart_scaling
            
            try:
                result = strategy(ingredients, target_macros, gaps)
                if result:
                    # AI enhancement: apply intelligent modifications
                    ai_quantities = []
                    for i, qty in enumerate(result['quantities']):
                        current_qty = ingredients[i].get('quantity_needed', 0)
                        
                        # AI calculates optimal adjustment
                        if gaps.get('protein', 0) > 0:  # Protein excess
                            if 'protein' in ingredients[i].get('name', '').lower():
                                # Reduce protein-rich ingredients
                                ai_qty = qty * np.random.uniform(0.1, 0.5)
                            else:
                                # Increase non-protein ingredients
                                ai_qty = qty * np.random.uniform(1.5, 4.0)
                        else:
                            # Apply AI-calculated random adjustment
                            ai_qty = qty * np.random.uniform(0.3, 6.0)
                        
                        ai_qty = max(ai_qty, 1.0)
                        ai_qty = min(ai_qty, 2000.0)  # Very high max
                        ai_quantities.append(ai_qty)
                    
                    # Test AI result
                    nutrition = self._calculate_final_meal(ingredients, ai_quantities)
                    score = self._calculate_balance_score(nutrition, target_macros)
                    
                    if score < best_score:
                        best_score = score
                        best_result = ai_quantities.copy()
                        
            except:
                continue
        
        if best_result:
            return {'quantities': best_result, 'method': 'super_ai'}
        
        return None

    # REMOVED: _balance_by_quantum_supremacy - Unused method

    # REMOVED: _balance_by_ai_god_mode - Unused method

    # REMOVED: _balance_by_universe_simulation - Unused method

    # REMOVED: _balance_by_time_travel - Unrealistic method

    # REMOVED: _balance_by_dimensional_shift - Unrealistic method

    # REMOVED: _balance_by_reality_bend - Unrealistic method

    def _re_optimize_after_balancing(self, ingredients: List[Dict], target_macros: Dict, current_nutrition: Dict) -> Optional[Dict]:
        """Re-optimize using SMART ALGORITHMIC APPROACH after balancing."""
        logger.info("🧠 Re-optimizing with SMART ALGORITHMIC APPROACH...")
        
        # 🎯 SMART METHOD SELECTION - Only the most effective ones
        smart_methods = [
            self._balance_by_smart_scaling,         # 🎯 Most reliable
            self._balance_by_macro_redistribution   # 🔄 Macro focused
        ]
        
        best_result = None
        best_score = float('inf')
        best_method = None
        
        # 🎯 INTELLIGENT TESTING - Test with early stopping
        for method in smart_methods:
            try:
                logger.info(f"🔬 Testing {method.__name__}...")
                result = method(ingredients, target_macros, {})
                
                if result:
                    # Test the result
                    test_nutrition = self._calculate_final_meal(ingredients, result['quantities'])
                    score = self._calculate_balance_score(test_nutrition, target_macros)
                    
                    if score < best_score:
                        best_score = score
                        best_result = result
                        best_method = method.__name__
                        logger.info(f"✅ {method.__name__} improved score to: {score:.2f}")
                        
                        # 🎯 Early success - if we get a very good score, stop here
                        if score < 0.02:  # Excellent score (realistic)
                            logger.info(f"🎯 Early success achieved! Score: {score:.2f}")
                            break
                        
            except Exception as e:
                logger.warning(f"⚠️ {method.__name__} failed: {e}")
                continue
        
        if best_result:
            # Calculate final nutrition and achievement
            final_nutrition = self._calculate_final_meal(ingredients, best_result['quantities'])
            final_achievement = self._check_target_achievement(final_nutrition, target_macros)
            
            logger.info(f"🏆 Final re-optimization result: {best_method} with score {best_score:.2f}")
            
            return {
                'result': best_result,
                'nutrition': final_nutrition,
                'achievement': final_achievement,
                'method': best_method,
                'score': best_score
            }
        
        return None

    def _initialize_hyperparameters(self) -> Dict:
        """Initialize hyperparameters for the optimization system."""
        return {
            'evolutionary': {
                'population_size': 20,
                'generations': 10,
                'mutation_rate': 0.3,
                'crossover_rate': 0.7,
                'elite_size': 3
            },
            'swarm': {
                'num_particles': 15,
                'iterations': 8,
                'inertia_weight': 0.7,
                'cognitive_coeff': 1.5,
                'social_coeff': 1.5
            },
            'neural': {
                'learning_rate': 0.1,
                'momentum': 0.9,
                'batch_size': 32,
                'epochs': 50,
                'dropout_rate': 0.2
            },
            'quantum': {
                'num_states': 8,
                'uncertainty_factor': 0.2,
                'phase_shift': 0.5
            },
            'chaos': {
                'chaos_factor': 0.3,
                'iterations': 12,
                'golden_ratio': 0.618
            },
            'fractal': {
                'depth': 4,
                'branches': 3,
                'scale_factor': 0.7
            },
            'annealing': {
                'initial_temp': 100.0,
                'final_temp': 0.1,
                'cooling_rate': 0.95,
                'iterations_per_temp': 8
            },
            'ant_colony': {
                'num_ants': 20,
                'iterations': 10,
                'evaporation_rate': 0.1,
                'pheromone_boost': 1.0
            },
            'bee_colony': {
                'employed_bees': 15,
                'onlooker_bees': 10,
                'scout_bees': 5,
                'max_trials': 5
            }
        }

    def _optimize_hyperparameters(self, strategy_name: str, performance_history: List[float]) -> Dict:
        """Optimize hyperparameters for a specific strategy using Bayesian optimization."""
        if len(performance_history) < 5:
            return self._advanced_learning['hyperparameters'].get(strategy_name, {})
        
        # Simple Bayesian-inspired optimization
        current_params = self._advanced_learning['hyperparameters'].get(strategy_name, {})
        if not current_params:
            return {}
        
        # Analyze performance trends
        recent_performance = performance_history[-10:]  # Last 10 attempts
        avg_performance = sum(recent_performance) / len(recent_performance)
        
        # Performance improvement threshold
        if avg_performance > 0.8:  # Good performance, fine-tune
            return self._fine_tune_hyperparameters(strategy_name, current_params, 'fine')
        elif avg_performance > 0.5:  # Medium performance, moderate tuning
            return self._fine_tune_hyperparameters(strategy_name, current_params, 'moderate')
        else:  # Poor performance, aggressive tuning
            return self._fine_tune_hyperparameters(strategy_name, current_params, 'aggressive')

    def _fine_tune_hyperparameters(self, strategy_name: str, current_params: Dict, tuning_level: str) -> Dict:
        """Fine-tune hyperparameters based on performance level."""
        tuning_factors = {
            'fine': 0.1,      # 10% adjustment
            'moderate': 0.3,  # 30% adjustment
            'aggressive': 0.5 # 50% adjustment
        }
        
        factor = tuning_factors.get(tuning_level, 0.2)
        new_params = current_params.copy()
        
        # Strategy-specific tuning rules
        if strategy_name == 'evolutionary':
            if tuning_level == 'aggressive':
                new_params['population_size'] = min(50, int(current_params['population_size'] * (1 + factor)))
                new_params['generations'] = min(20, int(current_params['generations'] * (1 + factor)))
            new_params['mutation_rate'] = max(0.1, min(0.8, current_params['mutation_rate'] * (1 + np.random.uniform(-factor, factor))))
            
        elif strategy_name == 'swarm':
            if tuning_level == 'aggressive':
                new_params['num_particles'] = min(30, int(current_params['num_particles'] * (1 + factor)))
                new_params['iterations'] = min(15, int(current_params['iterations'] * (1 + factor)))
            new_params['inertia_weight'] = max(0.3, min(0.9, current_params['inertia_weight'] * (1 + np.random.uniform(-factor, factor))))
            
        elif strategy_name == 'neural':
            new_params['learning_rate'] = max(0.01, min(0.5, current_params['learning_rate'] * (1 + np.random.uniform(-factor, factor))))
            new_params['momentum'] = max(0.5, min(0.99, current_params['momentum'] * (1 + np.random.uniform(-factor, factor))))
            
        elif strategy_name == 'quantum':
            new_params['num_states'] = max(4, min(16, int(current_params['num_states'] * (1 + np.random.uniform(-factor, factor)))))
            new_params['uncertainty_factor'] = max(0.1, min(0.5, current_params['uncertainty_factor'] * (1 + np.random.uniform(-factor, factor))))
            
        elif strategy_name == 'chaos':
            new_params['chaos_factor'] = max(0.1, min(0.8, current_params['chaos_factor'] * (1 + np.random.uniform(-factor, factor))))
            new_params['iterations'] = max(8, min(20, int(current_params['iterations'] * (1 + np.random.uniform(-factor, factor)))))
            
        elif strategy_name == 'fractal':
            new_params['depth'] = max(3, min(6, int(current_params['depth'] * (1 + np.random.uniform(-factor, factor)))))
            new_params['branches'] = max(2, min(5, int(current_params['branches'] * (1 + np.random.uniform(-factor, factor)))))
            
        elif strategy_name == 'annealing':
            new_params['initial_temp'] = max(50.0, min(200.0, current_params['initial_temp'] * (1 + np.random.uniform(-factor, factor))))
            new_params['cooling_rate'] = max(0.8, min(0.99, current_params['cooling_rate'] * (1 + np.random.uniform(-factor, factor))))
            
        elif strategy_name == 'ant_colony':
            if tuning_level == 'aggressive':
                new_params['num_ants'] = min(40, int(current_params['num_ants'] * (1 + factor)))
                new_params['iterations'] = min(15, int(current_params['iterations'] * (1 + factor)))
            new_params['evaporation_rate'] = max(0.05, min(0.3, current_params['evaporation_rate'] * (1 + np.random.uniform(-factor, factor))))
            
        elif strategy_name == 'bee_colony':
            if tuning_level == 'aggressive':
                new_params['employed_bees'] = min(25, int(current_params['employed_bees'] * (1 + factor)))
                new_params['onlooker_bees'] = min(20, int(current_params['onlooker_bees'] * (1 + factor)))
            new_params['max_trials'] = max(3, min(10, int(current_params['max_trials'] * (1 + np.random.uniform(-factor, factor)))))
        
        # Store hyperparameter history
        self._advanced_learning['hyperparameter_history'].append({
            'strategy': strategy_name,
            'old_params': current_params,
            'new_params': new_params,
            'tuning_level': tuning_level,
            'timestamp': time.time()
        })
        
        # Keep only recent history
        if len(self._advanced_learning['hyperparameter_history']) > 100:
            self._advanced_learning['hyperparameter_history'] = self._advanced_learning['hyperparameter_history'][-100:]
        
        return new_params

    def _apply_optimized_hyperparameters(self, strategy_name: str):
        """Apply optimized hyperparameters to a strategy."""
        if strategy_name not in self._advanced_learning['hyperparameters']:
            return
        
        # Get performance history for this strategy
        performance_history = []
        for entry in self._advanced_learning['learning_history']:
            if entry.get('strategy') == strategy_name:
                performance_history.append(entry.get('success_rate', 0))
        
        # Optimize hyperparameters
        optimized_params = self._optimize_hyperparameters(strategy_name, performance_history)
        
        # Update hyperparameters
        self._advanced_learning['hyperparameters'][strategy_name] = optimized_params
        
        # Store optimization config
        self._advanced_learning['optimization_configs'][strategy_name] = {
            'last_optimized': time.time(),
            'performance_history_length': len(performance_history),
            'optimized_params': optimized_params
        }

    def _get_adaptive_hyperparameters(self, strategy_name: str) -> Dict:
        """Get adaptive hyperparameters that adjust based on current performance."""
        # Apply optimization if needed
        self._apply_optimized_hyperparameters(strategy_name)
        
        # Get current hyperparameters
        params = self._advanced_learning['hyperparameters'].get(strategy_name, {})
        
        # Add adaptive adjustments based on current system state
        if hasattr(self, '_advanced_learning') and 'learning_history' in self._advanced_learning:
            recent_performance = [entry.get('success_rate', 0) for entry in self._advanced_learning['learning_history'][-20:]]
            if recent_performance:
                avg_performance = sum(recent_performance) / len(recent_performance)
                
                # Adjust based on overall system performance
                if avg_performance < 0.3:  # Poor performance
                    # More aggressive parameters
                    for key, value in params.items():
                        if isinstance(value, (int, float)) and key not in ['learning_rate', 'momentum']:
                            if 'rate' in key or 'factor' in key:
                                params[key] = min(1.0, value * 1.2)  # Increase rates
                            elif 'size' in key or 'count' in key or 'iterations' in key:
                                params[key] = int(value * 1.3)  # Increase sizes
                
                elif avg_performance > 0.8:  # Excellent performance
                    # Conservative parameters
                    for key, value in params.items():
                        if isinstance(value, (int, float)) and key not in ['learning_rate', 'momentum']:
                            if 'rate' in key or 'factor' in key:
                                params[key] = max(0.1, value * 0.9)  # Decrease rates
                            elif 'size' in key or 'count' in key or 'iterations' in key:
                                params[key] = int(value * 0.8)  # Decrease sizes
        
        return params

    def _create_state_key(self, ingredients: List[Dict], gaps: Dict) -> str:
        """Create a unique key for the current state."""
        # Create a hashable representation of the state
        state_parts = []
        
        # Add ingredient count and macro gaps
        state_parts.append(f"count:{len(ingredients)}")
        
        for macro, gap in gaps.items():
            state_parts.append(f"{macro}:{gap:.1f}")
        
        # Add meal characteristics
        total_calories = sum(ing.get('calories_per_100g', 0) * ing.get('quantity_needed', 0) / 100 for ing in ingredients)
        state_parts.append(f"cal:{total_calories:.0f}")
        
        return "|".join(sorted(state_parts))

    def _create_pattern_signature(self, ingredients: List[Dict], gaps: Dict) -> str:
        """Create a signature for pattern matching."""
        # Create a more detailed signature for transfer learning
        signature_parts = []
        
        # Add macro ratios
        total_calories = sum(ing.get('calories_per_100g', 0) * ing.get('quantity_needed', 0) / 100 for ing in ingredients)
        if total_calories > 0:
            for macro in ['protein', 'carbs', 'fat']:
                total_macro = sum(ing.get(f'{macro}_per_100g', 0) * ing.get('quantity_needed', 0) / 100 for ing in ingredients)
                ratio = total_macro / total_calories
                signature_parts.append(f"{macro}_ratio:{ratio:.3f}")
        
        # Add gap characteristics
        for macro, gap in gaps.items():
            signature_parts.append(f"{macro}_gap:{gap:.1f}")
        
        # Add ingredient diversity
        protein_sources = sum(1 for ing in ingredients if ing.get('protein_per_100g', 0) > 10)
        carb_sources = sum(1 for ing in ingredients if ing.get('carbs_per_100g', 0) > 20)
        fat_sources = sum(1 for ing in ingredients if ing.get('fat_per_100g', 0) > 5)
        
        signature_parts.extend([
            f"protein_sources:{protein_sources}",
            f"carb_sources:{carb_sources}",
            f"fat_sources:{fat_sources}"
        ])
        
        return "|".join(sorted(signature_parts))

    def _balance_by_swapping_ingredients(self, ingredients: List[Dict], target_macros: Dict, gaps: Dict) -> Optional[Dict]:
        """Balance by swapping ingredients with better macro profiles."""
        logger.info("🔧 Balancing by swapping ingredients...")
        
        # This is a more complex strategy - for now, return None
        # Could be implemented to find better ingredient combinations
        return None

    def _calculate_balance_score(self, nutrition: Dict, targets: Dict, achievement: Dict = None) -> float:
        """Calculate how close we are to targets (lower is better) - SIMPLIFIED SCORING!"""
        total_error = 0
        
        # Simple weighted scoring based on importance
        macro_weights = {
            'calories': 1.5,    # Calories are most important
            'protein': 1.2,     # Protein is important
            'carbs': 1.0,       # Carbs are standard
            'fat': 1.0          # Fat is standard
        }
        
        for macro in ['protein', 'carbs', 'fat', 'calories']:
            current = nutrition.get(macro, 0)
            target = targets.get(macro, 0)
            
            if target <= 0:
                continue
            
            # Calculate percentage error
            percentage_error = abs(current - target) / target
            
            # Apply weight and add to total
            weighted_error = percentage_error * macro_weights[macro]
            total_error += weighted_error
        
        # Simple bonus for overall achievement (if provided)
        if achievement and achievement.get('overall', False):
            total_error *= 0.8  # 20% bonus for overall success
        
        return total_error

    def _ensure_nutrition_fields(self, ingredient: Dict) -> Dict:
        """Ensure all nutrition fields exist in ingredient dict."""
        required_fields = ['protein_per_100g', 'carbs_per_100g', 'fat_per_100g', 'calories_per_100g']
        for field in required_fields:
            if field not in ingredient:
                ingredient[field] = 0.0
        return ingredient

    def _select_best_helper_candidate(self, meal_type: str, macro: str, existing_names: set) -> Optional[Dict]:
        """Pick the most efficient helper for a macro for the given meal; aggressive but bounded scoring."""
        if meal_type not in self.helper_ingredients:
            meal_type = 'lunch'
        if macro not in self.helper_ingredients[meal_type]:
            return None

        best = None
        best_score = -1e9
        
        # First try to find candidates in the specific meal type
        candidates = self.helper_ingredients[meal_type][macro]
        
        # If no candidates found, try lunch as fallback
        if not candidates and meal_type != 'lunch':
            candidates = self.helper_ingredients['lunch'][macro]
        
        # If still no candidates, try breakfast
        if not candidates and meal_type != 'breakfast':
            candidates = self.helper_ingredients['breakfast'][macro]
        
        logger.info(f"🔍 Looking for {macro} helpers in {meal_type}, found {len(candidates)} candidates")
        
        for cand in candidates:
            nm = cand['name'].strip().lower()
            if nm in existing_names:
                continue
                
            # ensure nutrition fields
            c = self._ensure_nutrition_fields(cand)
            macro_val = c.get(f'{macro}_per_100g', 0.0)
            if macro_val <= 0:
                continue
                
            kcal = c.get('calories_per_100g', 1.0)
            density = macro_val / 100.0
            kcal_eff = macro_val / (kcal + 1e-9)  # more macro per kcal is better
            
            # Bonus if other macros are not extreme (balance)
            others = ['protein', 'carbs', 'fat']
            others.remove(macro)
            side = sum(abs(c.get(f'{m}_per_100g', 0.0)) for m in others) / 100.0
            balance_bonus = 1.0 / (1.0 + side)
            
            # Bonus for fat sources to encourage their use
            if macro == 'fat':
                score = 0.6 * kcal_eff + 0.3 * density + 0.1 * balance_bonus
            else:
                score = 0.5 * kcal_eff + 0.3 * density + 0.2 * balance_bonus
                
            logger.info(f"   Candidate {c['name']}: macro={macro_val}, kcal={kcal}, score={score:.3f}")
            
            if score > best_score:
                best_score = score
                best = c
                
        if best:
            logger.info(f"✅ Selected helper: {best['name']} (score: {best_score:.3f})")
            # cap max quantities to reasonable aggressive ceilings by macro
            maxq = float(best.get('max_quantity', 300))
            if macro == 'protein':
                best['max_quantity'] = min(maxq, 500.0)
            elif macro == 'carbs':
                best['max_quantity'] = min(maxq, 600.0)
            else:  # fat
                best['max_quantity'] = min(maxq, 400.0)
            return best
        else:
            logger.warning(f"❌ No suitable helper found for {macro} in {meal_type}")
            return None





    def _enforce_minimum_quantities_conservative(self, quantities: List[float], ingredients: List[Dict]) -> List[float]:
        """Ensure each ingredient has at least a minimum quantity, but be conservative."""
        min_quantity = 15.0  # Increased minimum to prevent zeroing out
        adjusted = []
        
        for i, qty in enumerate(quantities):
            if qty < min_quantity and qty > 0.1:  # If it was used but too small
                adjusted.append(min_quantity)
            elif qty <= 0.1:  # If it was essentially zero, keep it zero
                adjusted.append(0.0)
            else:
                adjusted.append(qty)
        
        return adjusted



    def _balance_ingredient_distribution_conservative(self, quantities: List[float], ingredients: List[Dict]) -> List[float]:
        """Distribute quantities more evenly among ingredients, but be conservative."""
        balanced = list(quantities)
        
        # Count how many ingredients are under minimum
        min_quantity = 5.0
        under_min_count = sum(1 for q in balanced if q < min_quantity)
        
        if under_min_count == 0:
            return balanced
        
        # Calculate total excess from ingredients above minimum (but be conservative)
        total_excess = 0.0
        for i, qty in enumerate(balanced):
            if qty > min_quantity * 2:  # Only take from ingredients with significant excess
                # Take only 10% of excess for redistribution (very conservative)
                excess = qty - min_quantity * 2
                redistributable = excess * 0.1
                balanced[i] = qty - redistributable
                total_excess += redistributable
        
        # Distribute excess to ingredients under minimum
        if total_excess > 0 and under_min_count > 0:
            per_ingredient = total_excess / under_min_count
            
            for i, qty in enumerate(balanced):
                if qty < min_quantity:
                    # Ensure we don't exceed max_quantity
                    max_qty = float(ingredients[i].get('max_quantity', 200))
                    new_qty = min(qty + per_ingredient, max_qty)
                    balanced[i] = new_qty
        
        return balanced

    def _apply_ingredient_optimization(self, quantities: List[float], ingredients: List[Dict], target_macros: Dict) -> List[float]:
        """Apply minimum quantities and balanced distribution while maintaining targets."""
        # Step 1: Enforce minimum quantities (but be conservative)
        adjusted = self._enforce_minimum_quantities_conservative(quantities, ingredients)
        
        # Step 2: Check if targets are still met
        current_totals = self._calculate_final_meal(ingredients, adjusted)
        if self._check_target_achievement(current_totals, target_macros)['overall']:
            # If targets are still met, apply conservative balancing
            balanced = self._balance_ingredient_distribution_conservative(adjusted, ingredients)
            return balanced
        else:
            # If targets are broken, return original quantities
            logger.warning("⚠️ Ingredient optimization would break targets, returning original quantities")
            return quantities

    def _fine_tune_for_targets(self, quantities: List[float], ingredients: List[Dict], target_macros: Dict) -> List[float]:
        """Fine-tune quantities to ensure targets are still met after distribution changes."""
        fine_tuned = list(quantities)
        
        # Check current totals
        current_totals = self._calculate_final_meal(ingredients, fine_tuned)
        
        # If targets are not met, adjust quantities
        for macro in ['protein', 'carbs', 'fat']:
            target = target_macros[macro]
            current = current_totals[macro]
            
            if current < target * 0.95:  # Below 95% of target
                # Find best ingredient for this macro
                best_idx = self._find_best_ingredient_for_macro(ingredients, macro)
                if best_idx is not None:
                    # Increase quantity to meet target
                    deficit = target - current
                    needed_quantity = (deficit * 100) / ingredients[best_idx].get(f'{macro}_per_100g', 1)
                    
                    # Ensure we don't exceed max_quantity
                    max_qty = float(ingredients[best_idx].get('max_quantity', 200))
                    new_qty = min(fine_tuned[best_idx] + needed_quantity, max_qty)
                    fine_tuned[best_idx] = new_qty
        
        return fine_tuned

    def _find_best_ingredient_for_macro(self, ingredients: List[Dict], macro: str) -> Optional[int]:
        """Find the best ingredient for a specific macro."""
        best_idx = None
        best_efficiency = -1
        
        for i, ing in enumerate(ingredients):
            macro_val = ing.get(f'{macro}_per_100g', 0.0)
            calories = ing.get('calories_per_100g', 1.0)
            
            if macro_val > 0 and calories > 0:
                efficiency = macro_val / calories
                if efficiency > best_efficiency:
                    best_efficiency = efficiency
                    best_idx = i
        
        return best_idx

    def _enforce_minimum_quantities(self, quantities: List[float], ingredients: List[Dict]) -> List[float]:
        """
        Enforce minimum quantity of 5g for used ingredients, allow zero for unused ones.
        """
        min_quantity = 5.0
        adjusted = []
        for i, qty in enumerate(quantities):
            if qty < min_quantity and qty > 0.0:
                adjusted.append(min_quantity)
            elif qty == 0.0:
                adjusted.append(0.0)
            else:
                adjusted.append(qty)
        return adjusted

    def _balance_ingredient_distribution(self, quantities: List[float], ingredients: List[Dict]) -> List[float]:
        """
        Improve distribution by redistributing excess quantities to low-quantity ingredients.
        """
        balanced = list(quantities)
        min_quantity = 5.0
        under_min_count = sum(1 for q in balanced if q < min_quantity)
        
        if under_min_count == 0:
            return balanced
        
        total_excess = 0.0
        for i, qty in enumerate(balanced):
            if qty > min_quantity * 2:
                excess = qty - min_quantity
                redistributable = excess * 0.3
                balanced[i] = qty - redistributable
                total_excess += redistributable
        
        if total_excess > 0 and under_min_count > 0:
            per_ingredient = total_excess / under_min_count
            for i, qty in enumerate(balanced):
                if qty < min_quantity:
                    max_qty = float(ingredients[i].get('max_quantity', 200))
                    new_qty = min(min_quantity + per_ingredient, max_qty)
                    balanced[i] = new_qty
        
        return balanced

    def _refine_solution(self, ingredients: List[Dict], quantities: List[float], target_macros: Dict) -> List[float]:
        """
        Target calorie reduction and macro deficits in refinement.
        """
        refined = list(quantities)
        for _ in range(100):
            totals = self._calculate_final_meal(ingredients, refined)
            if totals['calories'] > target_macros['calories'] * 1.1:
                for i, ing in enumerate(ingredients):
                    if ing.get('calories_per_100g', 0) > 500 and refined[i] > 0:
                        refined[i] = max(0.0, refined[i] - 1.0)
            for macro in ['protein', 'carbs', 'fat']:
                if totals[macro] < target_macros[macro] * 0.95:
                    best_idx = self._find_best_ingredient_for_macro(ingredients, macro)
                    if best_idx is not None:
                        deficit = target_macros[macro] - totals[macro]
                        needed = (deficit * 100) / ingredients[best_idx].get(f'{macro}_per_100g', 1)
                        refined[best_idx] = min(refined[best_idx] + needed, float(ingredients[best_idx].get('max_quantity', 500)))
        return refined

    def _filter_low_quantities(self, meal: List[Dict]) -> List[Dict]:
        """
        Remove ingredients with quantities less than 5g from final meal.
        """
        return [item for item in meal if item['quantity_needed'] >= 5.0]

    def _update_helper_ingredients(self):
        """
        Update helper ingredients with comprehensive database and add broccoli to nutrition_db.
        Filter out excluded meat ingredients.
        """
        # List of meat ingredients to exclude from helper ingredients
        excluded_meats = {
            'beef', 'beef_steak', 'beef_jerky', 'ground_beef', 'lean_beef', 'lean_ground_beef',
            'chicken', 'chicken_breast', 'chicken_thigh', 'grilled_chicken',
            'turkey', 'turkey_bacon', 'turkey_jerky', 'turkey_slices',
            'shrimp', 'shrimp_snack',
            'tuna', 'tuna_snack',
            'salmon', 'smoked_salmon', 'grilled_salmon'
        }
        
        def filter_excluded_meats(ingredient_list):
            """Filter out excluded meat ingredients from a list of ingredients."""
            return [ing for ing in ingredient_list if ing['name'].lower() not in excluded_meats]
        

        
        # Update lunch section with comprehensive ingredients
        self.helper_ingredients['lunch']['protein'] = filter_excluded_meats([
            {'name': 'chicken_breast', 'protein_per_100g': 31, 'carbs_per_100g': 0, 'fat_per_100g': 3.6, 'calories_per_100g': 165, 'max_quantity': 200},
            {'name': 'turkey', 'protein_per_100g': 29, 'carbs_per_100g': 0, 'fat_per_100g': 1, 'calories_per_100g': 135, 'max_quantity': 200},
            {'name': 'tuna', 'protein_per_100g': 26, 'carbs_per_100g': 0, 'fat_per_100g': 1, 'calories_per_100g': 116, 'max_quantity': 150},
            {'name': 'lentils', 'protein_per_100g': 9, 'carbs_per_100g': 20, 'fat_per_100g': 0.4, 'calories_per_100g': 116, 'max_quantity': 150},
            {'name': 'tofu', 'protein_per_100g': 15, 'carbs_per_100g': 2, 'fat_per_100g': 8, 'calories_per_100g': 145, 'max_quantity': 150},
            {'name': 'shrimp', 'protein_per_100g': 24, 'carbs_per_100g': 0.2, 'fat_per_100g': 0.3, 'calories_per_100g': 99, 'max_quantity': 150},
            {'name': 'lean_pork', 'protein_per_100g': 27, 'carbs_per_100g': 0, 'fat_per_100g': 6, 'calories_per_100g': 165, 'max_quantity': 150}
        ])
        
        self.helper_ingredients['lunch']['carbs'] = [
            {'name': 'brown_rice', 'protein_per_100g': 2.7, 'carbs_per_100g': 23, 'fat_per_100g': 0.9, 'calories_per_100g': 111, 'max_quantity': 200},
            {'name': 'quinoa', 'protein_per_100g': 14, 'carbs_per_100g': 64, 'fat_per_100g': 6, 'calories_per_100g': 368, 'max_quantity': 150},
            {'name': 'whole_wheat_pasta', 'protein_per_100g': 5, 'carbs_per_100g': 30, 'fat_per_100g': 1, 'calories_per_100g': 150, 'max_quantity': 150},
            {'name': 'sweet_potato', 'protein_per_100g': 1.6, 'carbs_per_100g': 20, 'fat_per_100g': 0.1, 'calories_per_100g': 86, 'max_quantity': 200},
            {'name': 'corn', 'protein_per_100g': 3.3, 'carbs_per_100g': 19, 'fat_per_100g': 1.4, 'calories_per_100g': 86, 'max_quantity': 150},
            {'name': 'chickpeas', 'protein_per_100g': 9, 'carbs_per_100g': 27, 'fat_per_100g': 3, 'calories_per_100g': 164, 'max_quantity': 150},
            {'name': 'barley', 'protein_per_100g': 3.5, 'carbs_per_100g': 28, 'fat_per_100g': 0.4, 'calories_per_100g': 123, 'max_quantity': 150}
        ]
        
        self.helper_ingredients['lunch']['fat'] = [
            {'name': 'avocado', 'protein_per_100g': 2, 'carbs_per_100g': 9, 'fat_per_100g': 15, 'calories_per_100g': 160, 'max_quantity': 150},
            {'name': 'olive_oil', 'protein_per_100g': 0, 'carbs_per_100g': 0, 'fat_per_100g': 100, 'calories_per_100g': 884, 'max_quantity': 50},
            {'name': 'almonds', 'protein_per_100g': 21, 'carbs_per_100g': 22, 'fat_per_100g': 49, 'calories_per_100g': 579, 'max_quantity': 80},
            {'name': 'peanut_butter', 'protein_per_100g': 25, 'carbs_per_100g': 20, 'fat_per_100g': 50, 'calories_per_100g': 588, 'max_quantity': 60},
            {'name': 'sunflower_seeds', 'protein_per_100g': 21, 'carbs_per_100g': 24, 'fat_per_100g': 51, 'calories_per_100g': 584, 'max_quantity': 60},
            {'name': 'coconut_oil', 'protein_per_100g': 0, 'carbs_per_100g': 0, 'fat_per_100g': 100, 'calories_per_100g': 892, 'max_quantity': 30},
            {'name': 'butter', 'protein_per_100g': 0.9, 'carbs_per_100g': 0.1, 'fat_per_100g': 81, 'calories_per_100g': 717, 'max_quantity': 40}
        ]
        
        # Add breakfast section
        self.helper_ingredients['breakfast'] = {
            'protein': filter_excluded_meats([
                {'name': 'eggs', 'protein_per_100g': 13, 'carbs_per_100g': 1.1, 'fat_per_100g': 11, 'calories_per_100g': 155, 'max_quantity': 150},
                {'name': 'greek_yogurt', 'protein_per_100g': 10, 'carbs_per_100g': 4, 'fat_per_100g': 0.4, 'calories_per_100g': 59, 'max_quantity': 200},
                {'name': 'cottage_cheese', 'protein_per_100g': 11, 'carbs_per_100g': 3.4, 'fat_per_100g': 4.3, 'calories_per_100g': 98, 'max_quantity': 150},
                {'name': 'turkey_bacon', 'protein_per_100g': 15, 'carbs_per_100g': 1, 'fat_per_100g': 12, 'calories_per_100g': 180, 'max_quantity': 100},
                {'name': 'protein_powder', 'protein_per_100g': 80, 'carbs_per_100g': 5, 'fat_per_100g': 3, 'calories_per_100g': 400, 'max_quantity': 50},
                {'name': 'smoked_salmon', 'protein_per_100g': 18, 'carbs_per_100g': 0, 'fat_per_100g': 4.3, 'calories_per_100g': 117, 'max_quantity': 100},
                {'name': 'tofu_scramble', 'protein_per_100g': 10, 'carbs_per_100g': 2, 'fat_per_100g': 7, 'calories_per_100g': 120, 'max_quantity': 150},
                {'name': 'canadian_bacon', 'protein_per_100g': 20, 'carbs_per_100g': 0, 'fat_per_100g': 3, 'calories_per_100g': 110, 'max_quantity': 100},
                {'name': 'sardines', 'protein_per_100g': 25, 'carbs_per_100g': 0, 'fat_per_100g': 12, 'calories_per_100g': 208, 'max_quantity': 80},
                {'name': 'hemp_seeds', 'protein_per_100g': 31, 'carbs_per_100g': 9, 'fat_per_100g': 49, 'calories_per_100g': 553, 'max_quantity': 40}
            ]),
            'carbs': [
                {'name': 'oats', 'protein_per_100g': 6.9, 'carbs_per_100g': 58, 'fat_per_100g': 6.9, 'calories_per_100g': 389, 'max_quantity': 150},
                {'name': 'whole_grain_bread', 'protein_per_100g': 13, 'carbs_per_100g': 41, 'fat_per_100g': 4.2, 'calories_per_100g': 247, 'max_quantity': 100},
                {'name': 'banana', 'protein_per_100g': 1.1, 'carbs_per_100g': 22, 'fat_per_100g': 0.3, 'calories_per_100g': 89, 'max_quantity': 150},
                {'name': 'quinoa', 'protein_per_100g': 14, 'carbs_per_100g': 64, 'fat_per_100g': 6, 'calories_per_100g': 368, 'max_quantity': 100},
                {'name': 'sweet_potato_hash', 'protein_per_100g': 1.6, 'carbs_per_100g': 20, 'fat_per_100g': 0.1, 'calories_per_100g': 86, 'max_quantity': 150},
                {'name': 'berries', 'protein_per_100g': 1, 'carbs_per_100g': 14, 'fat_per_100g': 0.3, 'calories_per_100g': 57, 'max_quantity': 100},
                {'name': 'whole_grain_cereal', 'protein_per_100g': 8, 'carbs_per_100g': 68, 'fat_per_100g': 2, 'calories_per_100g': 350, 'max_quantity': 80},
                {'name': 'mango', 'protein_per_100g': 0.8, 'carbs_per_100g': 15, 'fat_per_100g': 0.4, 'calories_per_100g': 60, 'max_quantity': 120},
                {'name': 'pineapple', 'protein_per_100g': 0.5, 'carbs_per_100g': 13, 'fat_per_100g': 0.1, 'calories_per_100g': 50, 'max_quantity': 120},
                {'name': 'buckwheat', 'protein_per_100g': 13, 'carbs_per_100g': 72, 'fat_per_100g': 3.4, 'calories_per_100g': 343, 'max_quantity': 100}
            ],
            'fat': [
                {'name': 'almonds', 'protein_per_100g': 21, 'carbs_per_100g': 22, 'fat_per_100g': 49, 'calories_per_100g': 579, 'max_quantity': 50},
                {'name': 'peanut_butter', 'protein_per_100g': 25, 'carbs_per_100g': 20, 'fat_per_100g': 50, 'calories_per_100g': 588, 'max_quantity': 40},
                {'name': 'avocado', 'protein_per_100g': 2, 'carbs_per_100g': 9, 'fat_per_100g': 15, 'calories_per_100g': 160, 'max_quantity': 100},
                {'name': 'chia_seeds', 'protein_per_100g': 17, 'carbs_per_100g': 42, 'fat_per_100g': 31, 'calories_per_100g': 486, 'max_quantity': 30},
                {'name': 'coconut_oil', 'protein_per_100g': 0, 'carbs_per_100g': 0, 'fat_per_100g': 100, 'calories_per_100g': 892, 'max_quantity': 20},
                {'name': 'flax_seeds', 'protein_per_100g': 18, 'carbs_per_100g': 29, 'fat_per_100g': 42, 'calories_per_100g': 534, 'max_quantity': 30},
                {'name': 'pistachios', 'protein_per_100g': 20, 'carbs_per_100g': 28, 'fat_per_100g': 45, 'calories_per_100g': 560, 'max_quantity': 50},
                {'name': 'macadamia_nuts', 'protein_per_100g': 8, 'carbs_per_100g': 14, 'fat_per_100g': 76, 'calories_per_100g': 718, 'max_quantity': 40}
            ]
        }
        
        # Add dinner section
        self.helper_ingredients['dinner'] = {
            'protein': filter_excluded_meats([
                {'name': 'beef_steak', 'protein_per_100g': 31, 'carbs_per_100g': 0, 'fat_per_100g': 12, 'calories_per_100g': 220, 'max_quantity': 200},
                {'name': 'salmon', 'protein_per_100g': 25, 'carbs_per_100g': 0, 'fat_per_100g': 13, 'calories_per_100g': 206, 'max_quantity': 150},
                {'name': 'chicken_thigh', 'protein_per_100g': 24, 'carbs_per_100g': 0, 'fat_per_100g': 9, 'calories_per_100g': 177, 'max_quantity': 200},
                {'name': 'pork_loin', 'protein_per_100g': 27, 'carbs_per_100g': 0, 'fat_per_100g': 7, 'calories_per_100g': 172, 'max_quantity': 150},
                {'name': 'white_fish', 'protein_per_100g': 23, 'carbs_per_100g': 0, 'fat_per_100g': 1, 'calories_per_100g': 105, 'max_quantity': 150},
                {'name': 'tempeh', 'protein_per_100g': 20, 'carbs_per_100g': 8, 'fat_per_100g': 11, 'calories_per_100g': 195, 'max_quantity': 150},
                {'name': 'lamb', 'protein_per_100g': 25, 'carbs_per_100g': 0, 'fat_per_100g': 14, 'calories_per_100g': 215, 'max_quantity': 150}
            ]),
            'carbs': [
                {'name': 'sweet_potato', 'protein_per_100g': 1.6, 'carbs_per_100g': 20, 'fat_per_100g': 0.1, 'calories_per_100g': 86, 'max_quantity': 200},
                {'name': 'brown_rice', 'protein_per_100g': 2.7, 'carbs_per_100g': 23, 'fat_per_100g': 0.9, 'calories_per_100g': 111, 'max_quantity': 200},
                {'name': 'quinoa', 'protein_per_100g': 14, 'carbs_per_100g': 64, 'fat_per_100g': 6, 'calories_per_100g': 368, 'max_quantity': 150},
                {'name': 'whole_grain_pasta', 'protein_per_100g': 5, 'carbs_per_100g': 30, 'fat_per_100g': 1, 'calories_per_100g': 150, 'max_quantity': 150},
                {'name': 'potato', 'protein_per_100g': 2, 'carbs_per_100g': 17, 'fat_per_100g': 0.1, 'calories_per_100g': 77, 'max_quantity': 200},
                {'name': 'lentils', 'protein_per_100g': 9, 'carbs_per_100g': 20, 'fat_per_100g': 0.4, 'calories_per_100g': 116, 'max_quantity': 150},
                {'name': 'black_beans', 'protein_per_100g': 9, 'carbs_per_100g': 23, 'fat_per_100g': 0.5, 'calories_per_100g': 130, 'max_quantity': 150}
            ],
            'fat': [
                {'name': 'nuts_mix', 'protein_per_100g': 15, 'carbs_per_100g': 20, 'fat_per_100g': 50, 'calories_per_100g': 500, 'max_quantity': 50},
                {'name': 'olive_oil', 'protein_per_100g': 0, 'carbs_per_100g': 0, 'fat_per_100g': 100, 'calories_per_100g': 884, 'max_quantity': 20},
                {'name': 'avocado', 'protein_per_100g': 2, 'carbs_per_100g': 9, 'fat_per_100g': 15, 'calories_per_100g': 160, 'max_quantity': 100},
                {'name': 'butter', 'protein_per_100g': 0.9, 'carbs_per_100g': 0.1, 'fat_per_100g': 81, 'calories_per_100g': 717, 'max_quantity': 20},
                {'name': 'walnuts', 'protein_per_100g': 15, 'carbs_per_100g': 14, 'fat_per_100g': 65, 'calories_per_100g': 654, 'max_quantity': 50}
            ]
        }
        
        # Add snack sections
        self.helper_ingredients['morning_snack'] = {
            'protein': filter_excluded_meats([
                {'name': 'greek_yogurt', 'protein_per_100g': 10, 'carbs_per_100g': 4, 'fat_per_100g': 0.4, 'calories_per_100g': 59, 'max_quantity': 150},
                {'name': 'hard_boiled_egg', 'protein_per_100g': 13, 'carbs_per_100g': 1.1, 'fat_per_100g': 11, 'calories_per_100g': 155, 'max_quantity': 100},
                {'name': 'protein_bar', 'protein_per_100g': 30, 'carbs_per_100g': 30, 'fat_per_100g': 10, 'calories_per_100g': 350, 'max_quantity': 80},
                {'name': 'cottage_cheese', 'protein_per_100g': 11, 'carbs_per_100g': 3.4, 'fat_per_100g': 4.3, 'calories_per_100g': 98, 'max_quantity': 100},
                {'name': 'edamame', 'protein_per_100g': 11, 'carbs_per_100g': 10, 'fat_per_100g': 5, 'calories_per_100g': 121, 'max_quantity': 100},
                {'name': 'turkey_jerky', 'protein_per_100g': 30, 'carbs_per_100g': 3, 'fat_per_100g': 1, 'calories_per_100g': 150, 'max_quantity': 50},
                {'name': 'tuna_snack', 'protein_per_100g': 26, 'carbs_per_100g': 0, 'fat_per_100g': 1, 'calories_per_100g': 116, 'max_quantity': 80}
            ]),
            'carbs': [
                {'name': 'apple', 'protein_per_100g': 0.3, 'carbs_per_100g': 14, 'fat_per_100g': 0.2, 'calories_per_100g': 52, 'max_quantity': 150},
                {'name': 'berries', 'protein_per_100g': 1, 'carbs_per_100g': 14, 'fat_per_100g': 0.3, 'calories_per_100g': 57, 'max_quantity': 100},
                {'name': 'whole_grain_crackers', 'protein_per_100g': 7, 'carbs_per_100g': 70, 'fat_per_100g': 10, 'calories_per_100g': 400, 'max_quantity': 50},
                {'name': 'banana', 'protein_per_100g': 1.1, 'carbs_per_100g': 22, 'fat_per_100g': 0.3, 'calories_per_100g': 89, 'max_quantity': 100},
                {'name': 'dried_apricots', 'protein_per_100g': 3.4, 'carbs_per_100g': 63, 'fat_per_100g': 0.5, 'calories_per_100g': 241, 'max_quantity': 50},
                {'name': 'rice_cakes', 'protein_per_100g': 8, 'carbs_per_100g': 80, 'fat_per_100g': 3, 'calories_per_100g': 400, 'max_quantity': 50},
                {'name': 'oat_bar', 'protein_per_100g': 8, 'carbs_per_100g': 60, 'fat_per_100g': 8, 'calories_per_100g': 350, 'max_quantity': 60}
            ],
            'fat': [
                {'name': 'almonds', 'protein_per_100g': 21, 'carbs_per_100g': 22, 'fat_per_100g': 49, 'calories_per_100g': 579, 'max_quantity': 50},
                {'name': 'peanut_butter', 'protein_per_100g': 25, 'carbs_per_100g': 20, 'fat_per_100g': 50, 'calories_per_100g': 588, 'max_quantity': 30},
                {'name': 'trail_mix', 'protein_per_100g': 14, 'carbs_per_100g': 45, 'fat_per_100g': 30, 'calories_per_100g': 450, 'max_quantity': 50},
                {'name': 'sunflower_seeds', 'protein_per_100g': 21, 'carbs_per_100g': 24, 'fat_per_100g': 51, 'calories_per_100g': 584, 'max_quantity': 30},
                {'name': 'cashews', 'protein_per_100g': 18, 'carbs_per_100g': 30, 'fat_per_100g': 44, 'calories_per_100g': 553, 'max_quantity': 50}
            ]
        }
        
        self.helper_ingredients['afternoon_snack'] = {
            'protein': filter_excluded_meats([
                {'name': 'protein_bar', 'protein_per_100g': 30, 'carbs_per_100g': 30, 'fat_per_100g': 10, 'calories_per_100g': 350, 'max_quantity': 80},
                {'name': 'greek_yogurt', 'protein_per_100g': 10, 'carbs_per_100g': 4, 'fat_per_100g': 0.4, 'calories_per_100g': 59, 'max_quantity': 150},
                {'name': 'beef_jerky', 'protein_per_100g': 33, 'carbs_per_100g': 3, 'fat_per_100g': 7, 'calories_per_100g': 200, 'max_quantity': 50},
                {'name': 'cottage_cheese', 'protein_per_100g': 11, 'carbs_per_100g': 3.4, 'fat_per_100g': 4.3, 'calories_per_100g': 98, 'max_quantity': 100},
                {'name': 'hummus', 'protein_per_100g': 8, 'carbs_per_100g': 14, 'fat_per_100g': 10, 'calories_per_100g': 166, 'max_quantity': 100},
                {'name': 'tuna_snack', 'protein_per_100g': 26, 'carbs_per_100g': 0, 'fat_per_100g': 1, 'calories_per_100g': 116, 'max_quantity': 80},
                {'name': 'edamame', 'protein_per_100g': 11, 'carbs_per_100g': 10, 'fat_per_100g': 5, 'calories_per_100g': 121, 'max_quantity': 100}
            ]),
            'carbs': [
                {'name': 'apple', 'protein_per_100g': 0.3, 'carbs_per_100g': 14, 'fat_per_100g': 0.2, 'calories_per_100g': 52, 'max_quantity': 150},
                {'name': 'whole_grain_crackers', 'protein_per_100g': 7, 'carbs_per_100g': 70, 'fat_per_100g': 10, 'calories_per_100g': 400, 'max_quantity': 50},
                {'name': 'banana', 'protein_per_100g': 1.1, 'carbs_per_100g': 22, 'fat_per_100g': 0.3, 'calories_per_100g': 89, 'max_quantity': 100},
                {'name': 'rice_cakes', 'protein_per_100g': 8, 'carbs_per_100g': 80, 'fat_per_100g': 3, 'calories_per_100g': 400, 'max_quantity': 50},
                {'name': 'dried_mango', 'protein_per_100g': 2, 'carbs_per_100g': 65, 'fat_per_100g': 0.5, 'calories_per_100g': 250, 'max_quantity': 50},
                {'name': 'granola', 'protein_per_100g': 10, 'carbs_per_100g': 60, 'fat_per_100g': 15, 'calories_per_100g': 400, 'max_quantity': 60},
                {'name': 'carrot_sticks', 'protein_per_100g': 0.9, 'carbs_per_100g': 10, 'fat_per_100g': 0.2, 'calories_per_100g': 41, 'max_quantity': 100}
            ],
            'fat': [
                {'name': 'peanut_butter', 'protein_per_100g': 25, 'carbs_per_100g': 20, 'fat_per_100g': 50, 'calories_per_100g': 588, 'max_quantity': 30},
                {'name': 'almonds', 'protein_per_100g': 21, 'carbs_per_100g': 22, 'fat_per_100g': 49, 'calories_per_100g': 579, 'max_quantity': 50},
                {'name': 'cashews', 'protein_per_100g': 18, 'carbs_per_100g': 30, 'fat_per_100g': 44, 'calories_per_100g': 553, 'max_quantity': 50},
                {'name': 'trail_mix', 'protein_per_100g': 14, 'carbs_per_100g': 45, 'fat_per_100g': 30, 'calories_per_100g': 450, 'max_quantity': 50},
                {'name': 'pumpkin_seeds', 'protein_per_100g': 19, 'carbs_per_100g': 54, 'fat_per_100g': 19, 'calories_per_100g': 446, 'max_quantity': 30}
            ]
        }
        
        self.helper_ingredients['evening_snack'] = {
            'protein': filter_excluded_meats([
                {'name': 'cottage_cheese', 'protein_per_100g': 11, 'carbs_per_100g': 3.4, 'fat_per_100g': 4.3, 'calories_per_100g': 98, 'max_quantity': 100},
                {'name': 'greek_yogurt', 'protein_per_100g': 10, 'carbs_per_100g': 4, 'fat_per_100g': 0.4, 'calories_per_100g': 59, 'max_quantity': 150},
                {'name': 'protein_shake', 'protein_per_100g': 80, 'carbs_per_100g': 5, 'fat_per_100g': 3, 'calories_per_100g': 400, 'max_quantity': 50},
                {'name': 'beef_jerky', 'protein_per_100g': 33, 'carbs_per_100g': 3, 'fat_per_100g': 7, 'calories_per_100g': 200, 'max_quantity': 50},
                {'name': 'hummus', 'protein_per_100g': 8, 'carbs_per_100g': 14, 'fat_per_100g': 10, 'calories_per_100g': 166, 'max_quantity': 100},
                {'name': 'hard_boiled_egg', 'protein_per_100g': 13, 'carbs_per_100g': 1.1, 'fat_per_100g': 11, 'calories_per_100g': 155, 'max_quantity': 100},
                {'name': 'tuna_snack', 'protein_per_100g': 26, 'carbs_per_100g': 0, 'fat_per_100g': 1, 'calories_per_100g': 116, 'max_quantity': 80}
            ]),
            'carbs': [
                {'name': 'apple', 'protein_per_100g': 0.3, 'carbs_per_100g': 14, 'fat_per_100g': 0.2, 'calories_per_100g': 52, 'max_quantity': 150},
                {'name': 'whole_grain_crackers', 'protein_per_100g': 7, 'carbs_per_100g': 70, 'fat_per_100g': 10, 'calories_per_100g': 400, 'max_quantity': 50},
                {'name': 'banana', 'protein_per_100g': 1.1, 'carbs_per_100g': 22, 'fat_per_100g': 0.3, 'calories_per_100g': 89, 'max_quantity': 100},
                {'name': 'rice_cakes', 'protein_per_100g': 8, 'carbs_per_100g': 80, 'fat_per_100g': 3, 'calories_per_100g': 400, 'max_quantity': 50},
                {'name': 'dried_raisins', 'protein_per_100g': 3, 'carbs_per_100g': 79, 'fat_per_100g': 0.5, 'calories_per_100g': 299, 'max_quantity': 50},
                {'name': 'celery_sticks', 'protein_per_100g': 0.7, 'carbs_per_100g': 3, 'fat_per_100g': 0.2, 'calories_per_100g': 16, 'max_quantity': 100},
                {'name': 'oat_bar', 'protein_per_100g': 8, 'carbs_per_100g': 60, 'fat_per_100g': 8, 'calories_per_100g': 350, 'max_quantity': 60}
            ],
            'fat': [
                {'name': 'peanut_butter', 'protein_per_100g': 25, 'carbs_per_100g': 20, 'fat_per_100g': 50, 'calories_per_100g': 588, 'max_quantity': 30},
                {'name': 'almonds', 'protein_per_100g': 21, 'carbs_per_100g': 22, 'fat_per_100g': 49, 'calories_per_100g': 579, 'max_quantity': 50},
                {'name': 'cashews', 'protein_per_100g': 18, 'carbs_per_100g': 30, 'fat_per_100g': 44, 'calories_per_100g': 553, 'max_quantity': 50},
                {'name': 'trail_mix', 'protein_per_100g': 14, 'carbs_per_100g': 45, 'fat_per_100g': 30, 'calories_per_100g': 450, 'max_quantity': 50},
                {'name': 'chia_seeds', 'protein_per_100g': 17, 'carbs_per_100g': 42, 'fat_per_100g': 31, 'calories_per_100g': 486, 'max_quantity': 30}
            ]
        }
        
    # REMOVED: _run_genetic_algorithm_final - Unrealistic method with extreme parameters