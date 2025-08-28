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
                    {'name': 'berries', 'protein_per_100g': 1, 'carbs_per_100g': 14, 'fat_per_100g': 0.3, 'calories_per_100g': 57, 'max_quantity': 100},
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

        # Basic nutritional data for enrichment
        self.nutrition_db = {
            'chicken': {'protein_per_100g': 31, 'carbs_per_100g': 0, 'fat_per_100g': 3.6, 'calories_per_100g': 165},
            'chicken_breast': {'protein_per_100g': 31, 'carbs_per_100g': 0, 'fat_per_100g': 3.6, 'calories_per_100g': 165},
            'beef': {'protein_per_100g': 26, 'carbs_per_100g': 0, 'fat_per_100g': 15, 'calories_per_100g': 250},
            'beef_steak': {'protein_per_100g': 31, 'carbs_per_100g': 0, 'fat_per_100g': 12, 'calories_per_100g': 220},
            'rice': {'protein_per_100g': 2.7, 'carbs_per_100g': 28, 'fat_per_100g': 0.3, 'calories_per_100g': 130},
            'brown_rice': {'protein_per_100g': 2.7, 'carbs_per_100g': 23, 'fat_per_100g': 0.9, 'calories_per_100g': 111},
            'bread': {'protein_per_100g': 13, 'carbs_per_100g': 41, 'fat_per_100g': 4.2, 'calories_per_100g': 247},
            'tomato': {'protein_per_100g': 0.9, 'carbs_per_100g': 3.9, 'fat_per_100g': 0.2, 'calories_per_100g': 18},
            'onion': {'protein_per_100g': 1.1, 'carbs_per_100g': 9, 'fat_per_100g': 0.1, 'calories_per_100g': 40},
            'potato': {'protein_per_100g': 2, 'carbs_per_100g': 17, 'fat_per_100g': 0.1, 'calories_per_100g': 77},
            'eggs': {'protein_per_100g': 13, 'carbs_per_100g': 1.1, 'fat_per_100g': 11, 'calories_per_100g': 155},
            'oats': {'protein_per_100g': 6.9, 'carbs_per_100g': 58, 'fat_per_100g': 6.9, 'calories_per_100g': 389},
            'almonds': {'protein_per_100g': 21, 'carbs_per_100g': 22, 'fat_per_100g': 49, 'calories_per_100g': 579},
            'avocado': {'protein_per_100g': 2, 'carbs_per_100g': 9, 'fat_per_100g': 15, 'calories_per_100g': 160},
            'nuts_mix': {'protein_per_100g': 15, 'carbs_per_100g': 20, 'fat_per_100g': 50, 'calories_per_100g': 500},
            'sweet_potato': {'protein_per_100g': 1.6, 'carbs_per_100g': 20, 'fat_per_100g': 0.1, 'calories_per_100g': 86},
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

            # ---- STEP 2: Add smart helper ingredients (non-duplicates, meal-specific) ----
            logger.info("🔧 Step 2: Targets not fully achieved. Adding helper ingredients...")
            helper_ingredients = self._add_smart_helper_ingredients_candidates(
                current_ingredients=self._materialize_ingredients(rag_ingredients, initial_result['quantities']),
                target_macros=target_macros,
                meal_type=meal_type
            )

            # Merge (as candidates) – no preset quantities; let optimizer decide.
            all_ingredients = self._merge_ingredients_for_reopt(rag_ingredients, helper_ingredients)
            logger.info(f"🔁 Re-optimizing with {len(all_ingredients)} ingredients (including {len(helper_ingredients)} helpers)...")

            # ---- STEP 3: Re-optimize on the full set ----
            final_result = self._run_optimization_methods(all_ingredients, target_macros)
            final_nutrition = self._calculate_final_meal(all_ingredients, final_result['quantities'])
            final_target_achievement = self._check_target_achievement(final_nutrition, target_macros)
            logger.info(f"✅ Final target achievement: {final_target_achievement}")

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
        for i in range(n):
            ing = dict(ingredients[i])
            ing['quantity_needed'] = max(0.0, float(quantities[i]))
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
           - {'suggestions': [{'ingredients': [...]}]}
           - {'ingredients': [...]}
           - [{'name': 'chicken', 'quantity': 100}, ...]
           - "گوشت، پیاز، گوجه" (string format - extract ingredient names)
        """
        # List of meat ingredients to exclude from processing
        excluded_meats = {
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
        elif isinstance(rag_response, dict):
            if 'ingredients' in rag_response and isinstance(rag_response['ingredients'], list):
                candidates = rag_response['ingredients']
            elif 'suggestions' in rag_response and isinstance(rag_response['suggestions'], list):
                for s in rag_response['suggestions']:
                    candidates.extend(s.get('ingredients', []))
        elif isinstance(rag_response, str):
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
                    # Skip if this ingredient is in the excluded meats list
                    if ingredient_name.lower() in excluded_meats:
                        logger.info(f"🚫 Skipping excluded meat ingredient: '{keyword}' -> '{ingredient_name}'")
                        continue
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
                
            # Skip if this ingredient is in the excluded meats list
            if key in excluded_meats:
                logger.info(f"🚫 Skipping excluded meat ingredient: '{name}'")
                continue
                
            enriched = self._enrich_ingredient_with_nutrition(ing)
            # default max_quantity
            if 'max_quantity' not in enriched:
                enriched['max_quantity'] = max(200, int(ing.get('quantity', 200)) if isinstance(ing.get('quantity', 0), (int, float)) else 200)
            ingredients.append(enriched)
            seen.add(key)

        return ingredients

    def _ensure_nutrition_fields(self, ingredient: Dict) -> Dict:
        """Ensure nutrition fields exist for helper or custom items."""
        out = ingredient.copy()
        base = self.nutrition_db.get(out['name'].strip().lower())
        if base:
            out.update({k: base[k] for k in ['protein_per_100g', 'carbs_per_100g', 'fat_per_100g', 'calories_per_100g']})
        else:
            for k, dv in [('protein_per_100g', 5.0), ('carbs_per_100g', 10.0), ('fat_per_100g', 5.0), ('calories_per_100g', 100.0)]:
                out[k] = float(out.get(k, dv))
        if 'max_quantity' not in out:
            out['max_quantity'] = 200
        return out

    def _enrich_ingredient_with_nutrition(self, ingredient: Dict) -> Dict:
        name = ingredient.get('name', '').strip().lower()
        out = ingredient.copy()
        base = self.nutrition_db.get(name)
        if base:
            out.update(base)
        else:
            # fallback defaults
            out.setdefault('protein_per_100g', 5.0)
            out.setdefault('carbs_per_100g', 10.0)
            out.setdefault('fat_per_100g', 5.0)
            out.setdefault('calories_per_100g', 100.0)
        out.setdefault('max_quantity', 200)
        return out

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
                                                  target_macros: Dict, meal_type: str) -> List[Dict]:
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
        for macro in ['protein', 'carbs', 'fat']:
            if deficits[macro] <= 1.0:  # Increased threshold to be more aggressive
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
        
        self.nutrition_db['broccoli'] = {
            'protein_per_100g': 2.8,
            'carbs_per_100g': 7,
            'fat_per_100g': 0.4,
            'calories_per_100g': 35
        }
        
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
                {'name': 'berries', 'protein_per_100g': 1, 'carbs_per_100g': 14, 'fat_per_100g': 0.3, 'calories_per_100g': 57, 'max_quantity': 100},
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