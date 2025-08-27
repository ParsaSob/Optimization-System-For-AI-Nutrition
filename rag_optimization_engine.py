import logging
import time
from typing import Dict, List, Optional
import numpy as np
import random
from scipy.optimize import differential_evolution
import optuna

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGMealOptimizer:
    """Simplified meal optimizer that adds minimal supplements to reach targets"""
    
    def __init__(self):
        # Extended ingredient database with 100+ helper ingredients and realistic limits
        self.ingredients_db = [
            # High protein (25 ingredients)
            {'name': 'chicken_breast', 'protein_per_100g': 31, 'carbs_per_100g': 0, 'fat_per_100g': 3.6, 'calories_per_100g': 165, 'max_quantity': 300, 'category': 'protein'},
            {'name': 'salmon', 'protein_per_100g': 25, 'carbs_per_100g': 0, 'fat_per_100g': 12, 'calories_per_100g': 208, 'max_quantity': 250, 'category': 'protein'},
            {'name': 'tuna', 'protein_per_100g': 30, 'carbs_per_100g': 0, 'fat_per_100g': 1, 'calories_per_100g': 144, 'max_quantity': 200, 'category': 'protein'},
            {'name': 'cod', 'protein_per_100g': 23, 'carbs_per_100g': 0, 'fat_per_100g': 0.9, 'calories_per_100g': 105, 'max_quantity': 250, 'category': 'protein'},
            {'name': 'shrimp', 'protein_per_100g': 24, 'carbs_per_100g': 0.2, 'fat_per_100g': 0.3, 'calories_per_100g': 99, 'max_quantity': 200, 'category': 'protein'},
            {'name': 'eggs', 'protein_per_100g': 13, 'carbs_per_100g': 1.1, 'fat_per_100g': 11, 'calories_per_100g': 155, 'max_quantity': 150, 'category': 'protein'},
            {'name': 'egg_whites', 'protein_per_100g': 11, 'carbs_per_100g': 0.7, 'fat_per_100g': 0.2, 'calories_per_100g': 52, 'max_quantity': 200, 'category': 'protein'},
            {'name': 'beef', 'protein_per_100g': 26, 'carbs_per_100g': 0, 'fat_per_100g': 15, 'calories_per_100g': 250, 'max_quantity': 250, 'category': 'protein'},
            {'name': 'pork', 'protein_per_100g': 27, 'carbs_per_100g': 0, 'fat_per_100g': 14, 'calories_per_100g': 242, 'max_quantity': 250, 'category': 'protein'},
            {'name': 'turkey', 'protein_per_100g': 29, 'carbs_per_100g': 0, 'fat_per_100g': 3.6, 'calories_per_100g': 189, 'max_quantity': 250, 'category': 'protein'},
            {'name': 'lentils', 'protein_per_100g': 9, 'carbs_per_100g': 20, 'fat_per_100g': 0.4, 'calories_per_100g': 116, 'max_quantity': 200, 'category': 'protein'},
            {'name': 'black_beans', 'protein_per_100g': 8, 'carbs_per_100g': 23, 'fat_per_100g': 0.5, 'calories_per_100g': 132, 'max_quantity': 200, 'category': 'protein'},
            {'name': 'kidney_beans', 'protein_per_100g': 8, 'carbs_per_100g': 23, 'fat_per_100g': 0.5, 'calories_per_100g': 127, 'max_quantity': 200, 'category': 'protein'},
            {'name': 'chickpeas', 'protein_per_100g': 9, 'carbs_per_100g': 27, 'fat_per_100g': 3, 'calories_per_100g': 164, 'max_quantity': 200, 'category': 'protein'},
            {'name': 'pinto_beans', 'protein_per_100g': 9, 'carbs_per_100g': 26, 'fat_per_100g': 0.6, 'calories_per_100g': 143, 'max_quantity': 200, 'category': 'protein'},
            {'name': 'edamame', 'protein_per_100g': 11, 'carbs_per_100g': 10, 'fat_per_100g': 5, 'calories_per_100g': 121, 'max_quantity': 200, 'category': 'protein'},
            {'name': 'tofu', 'protein_per_100g': 8, 'carbs_per_100g': 1.9, 'fat_per_100g': 4.8, 'calories_per_100g': 76, 'max_quantity': 200, 'category': 'protein'},
            {'name': 'tempeh', 'protein_per_100g': 20, 'carbs_per_100g': 7.6, 'fat_per_100g': 11, 'calories_per_100g': 192, 'max_quantity': 200, 'category': 'protein'},
            {'name': 'seitan', 'protein_per_100g': 25, 'carbs_per_100g': 4, 'fat_per_100g': 1.2, 'calories_per_100g': 120, 'max_quantity': 200, 'category': 'protein'},
            {'name': 'greek_yogurt', 'protein_per_100g': 10, 'carbs_per_100g': 3.6, 'fat_per_100g': 0.4, 'calories_per_100g': 59, 'max_quantity': 300, 'category': 'protein'},
            {'name': 'cottage_cheese', 'protein_per_100g': 11, 'carbs_per_100g': 3.4, 'fat_per_100g': 4.3, 'calories_per_100g': 98, 'max_quantity': 250, 'category': 'protein'},
            {'name': 'protein_powder', 'protein_per_100g': 80, 'carbs_per_100g': 8, 'fat_per_100g': 2, 'calories_per_100g': 370, 'max_quantity': 100, 'category': 'protein'},
            {'name': 'whey_protein', 'protein_per_100g': 75, 'carbs_per_100g': 5, 'fat_per_100g': 2, 'calories_per_100g': 340, 'max_quantity': 100, 'category': 'protein'},
            {'name': 'casein_protein', 'protein_per_100g': 85, 'carbs_per_100g': 3, 'fat_per_100g': 1, 'calories_per_100g': 360, 'max_quantity': 100, 'category': 'protein'},
            
            # High carbs (25 ingredients)
            {'name': 'brown_rice', 'protein_per_100g': 2.7, 'carbs_per_100g': 23, 'fat_per_100g': 0.9, 'calories_per_100g': 111, 'max_quantity': 300, 'category': 'carbs'},
            {'name': 'white_rice', 'protein_per_100g': 2.7, 'carbs_per_100g': 28, 'fat_per_100g': 0.3, 'calories_per_100g': 130, 'max_quantity': 300, 'category': 'carbs'},
            {'name': 'quinoa', 'protein_per_100g': 4.4, 'carbs_per_100g': 22, 'fat_per_100g': 1.9, 'calories_per_100g': 120, 'max_quantity': 250, 'category': 'carbs'},
            {'name': 'oats', 'protein_per_100g': 6.9, 'carbs_per_100g': 58, 'fat_per_100g': 6.9, 'calories_per_100g': 389, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'oatmeal', 'protein_per_100g': 6.9, 'carbs_per_100g': 58, 'fat_per_100g': 6.9, 'calories_per_100g': 389, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'whole_wheat_bread', 'protein_per_100g': 13, 'carbs_per_100g': 41, 'fat_per_100g': 4.2, 'calories_per_100g': 247, 'max_quantity': 150, 'category': 'carbs'},
            {'name': 'whole_wheat_pasta', 'protein_per_100g': 13, 'carbs_per_100g': 71, 'fat_per_100g': 1.5, 'calories_per_100g': 352, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'sweet_potato', 'protein_per_100g': 1.6, 'carbs_per_100g': 20, 'fat_per_100g': 0.1, 'calories_per_100g': 86, 'max_quantity': 300, 'category': 'carbs'},
            {'name': 'potato', 'protein_per_100g': 2, 'carbs_per_100g': 17, 'fat_per_100g': 0.1, 'calories_per_100g': 77, 'max_quantity': 300, 'category': 'carbs'},
            {'name': 'banana', 'protein_per_100g': 1.1, 'carbs_per_100g': 23, 'fat_per_100g': 0.3, 'calories_per_100g': 89, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'apple', 'protein_per_100g': 0.3, 'carbs_per_100g': 14, 'fat_per_100g': 0.2, 'calories_per_100g': 52, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'orange', 'protein_per_100g': 0.9, 'carbs_per_100g': 12, 'fat_per_100g': 0.1, 'calories_per_100g': 47, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'grapes', 'protein_per_100g': 0.6, 'carbs_per_100g': 16, 'fat_per_100g': 0.2, 'calories_per_100g': 62, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'mango', 'protein_per_100g': 0.8, 'carbs_per_100g': 15, 'fat_per_100g': 0.4, 'calories_per_100g': 60, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'pineapple', 'protein_per_100g': 0.5, 'carbs_per_100g': 13, 'fat_per_100g': 0.1, 'calories_per_100g': 50, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'strawberries', 'protein_per_100g': 0.7, 'carbs_per_100g': 8, 'fat_per_100g': 0.3, 'calories_per_100g': 32, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'blueberries', 'protein_per_100g': 0.7, 'carbs_per_100g': 14, 'fat_per_100g': 0.3, 'calories_per_100g': 57, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'raspberries', 'protein_per_100g': 1.2, 'carbs_per_100g': 12, 'fat_per_100g': 0.7, 'calories_per_100g': 52, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'pear', 'protein_per_100g': 0.4, 'carbs_per_100g': 15, 'fat_per_100g': 0.1, 'calories_per_100g': 57, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'peach', 'protein_per_100g': 0.9, 'carbs_per_100g': 10, 'fat_per_100g': 0.3, 'calories_per_100g': 39, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'plum', 'protein_per_100g': 0.7, 'carbs_per_100g': 11, 'fat_per_100g': 0.3, 'calories_per_100g': 46, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'cherries', 'protein_per_100g': 1.1, 'carbs_per_100g': 16, 'fat_per_100g': 0.2, 'calories_per_100g': 63, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'kiwi', 'protein_per_100g': 1.1, 'carbs_per_100g': 15, 'fat_per_100g': 0.5, 'calories_per_100g': 61, 'max_quantity': 200, 'category': 'carbs'},
            {'name': 'papaya', 'protein_per_100g': 0.5, 'carbs_per_100g': 11, 'fat_per_100g': 0.3, 'calories_per_100g': 43, 'max_quantity': 200, 'category': 'carbs'},
            
            # High fat (25 ingredients) - with realistic limits
            {'name': 'olive_oil', 'protein_per_100g': 0, 'carbs_per_100g': 0, 'fat_per_100g': 100, 'calories_per_100g': 884, 'max_quantity': 30, 'category': 'fat'},
            {'name': 'coconut_oil', 'protein_per_100g': 0, 'carbs_per_100g': 0, 'fat_per_100g': 100, 'calories_per_100g': 862, 'max_quantity': 30, 'category': 'fat'},
            {'name': 'avocado', 'protein_per_100g': 2, 'carbs_per_100g': 9, 'fat_per_100g': 15, 'calories_per_100g': 160, 'max_quantity': 150, 'category': 'fat'},
            {'name': 'almonds', 'protein_per_100g': 21, 'carbs_per_100g': 22, 'fat_per_100g': 49, 'calories_per_100g': 579, 'max_quantity': 100, 'category': 'fat'},
            {'name': 'walnuts', 'protein_per_100g': 15, 'carbs_per_100g': 14, 'fat_per_100g': 65, 'calories_per_100g': 654, 'max_quantity': 100, 'category': 'fat'},
            {'name': 'cashews', 'protein_per_100g': 18, 'carbs_per_100g': 30, 'fat_per_100g': 44, 'calories_per_100g': 553, 'max_quantity': 100, 'category': 'fat'},
            {'name': 'peanuts', 'protein_per_100g': 26, 'carbs_per_100g': 16, 'fat_per_100g': 49, 'calories_per_100g': 567, 'max_quantity': 100, 'category': 'fat'},
            {'name': 'pecans', 'protein_per_100g': 9, 'carbs_per_100g': 14, 'fat_per_100g': 72, 'calories_per_100g': 691, 'max_quantity': 100, 'category': 'fat'},
            {'name': 'pistachios', 'protein_per_100g': 20, 'carbs_per_100g': 28, 'fat_per_100g': 45, 'calories_per_100g': 560, 'max_quantity': 100, 'category': 'fat'},
            {'name': 'macadamia_nuts', 'protein_per_100g': 8, 'carbs_per_100g': 14, 'fat_per_100g': 76, 'calories_per_100g': 718, 'max_quantity': 100, 'category': 'fat'},
            {'name': 'hazelnuts', 'protein_per_100g': 15, 'carbs_per_100g': 17, 'fat_per_100g': 61, 'calories_per_100g': 628, 'max_quantity': 100, 'category': 'fat'},
            {'name': 'brazil_nuts', 'protein_per_100g': 14, 'carbs_per_100g': 12, 'fat_per_100g': 66, 'calories_per_100g': 656, 'max_quantity': 100, 'category': 'fat'},
            {'name': 'pine_nuts', 'protein_per_100g': 14, 'carbs_per_100g': 13, 'fat_per_100g': 68, 'calories_per_100g': 673, 'max_quantity': 100, 'category': 'fat'},
            {'name': 'sunflower_seeds', 'protein_per_100g': 21, 'carbs_per_100g': 20, 'fat_per_100g': 51, 'calories_per_100g': 584, 'max_quantity': 100, 'category': 'fat'},
            {'name': 'pumpkin_seeds', 'protein_per_100g': 19, 'carbs_per_100g': 54, 'fat_per_100g': 19, 'calories_per_100g': 446, 'max_quantity': 100, 'category': 'fat'},
            {'name': 'chia_seeds', 'protein_per_100g': 17, 'carbs_per_100g': 42, 'fat_per_100g': 31, 'calories_per_100g': 486, 'max_quantity': 50, 'category': 'fat'},
            {'name': 'flaxseeds', 'protein_per_100g': 18, 'carbs_per_100g': 29, 'fat_per_100g': 42, 'calories_per_100g': 534, 'max_quantity': 50, 'category': 'fat'},
            {'name': 'hemp_seeds', 'protein_per_100g': 32, 'carbs_per_100g': 4, 'fat_per_100g': 49, 'calories_per_100g': 553, 'max_quantity': 50, 'category': 'fat'},
            {'name': 'sesame_seeds', 'protein_per_100g': 18, 'carbs_per_100g': 23, 'fat_per_100g': 50, 'calories_per_100g': 573, 'max_quantity': 50, 'category': 'fat'},
            {'name': 'peanut_butter', 'protein_per_100g': 25, 'carbs_per_100g': 20, 'fat_per_100g': 50, 'calories_per_100g': 588, 'max_quantity': 80, 'category': 'fat'},
            {'name': 'almond_butter', 'protein_per_100g': 21, 'carbs_per_100g': 20, 'fat_per_100g': 53, 'calories_per_100g': 614, 'max_quantity': 80, 'category': 'fat'},
            {'name': 'cashew_butter', 'protein_per_100g': 18, 'carbs_per_100g': 30, 'fat_per_100g': 44, 'calories_per_100g': 553, 'max_quantity': 80, 'category': 'fat'},
            {'name': 'tahini', 'protein_per_100g': 18, 'carbs_per_100g': 23, 'fat_per_100g': 50, 'calories_per_100g': 573, 'max_quantity': 80, 'category': 'fat'},
            {'name': 'coconut_milk', 'protein_per_100g': 2, 'carbs_per_100g': 3, 'fat_per_100g': 24, 'calories_per_100g': 230, 'max_quantity': 100, 'category': 'fat'},
            {'name': 'heavy_cream', 'protein_per_100g': 2, 'carbs_per_100g': 3, 'fat_per_100g': 37, 'calories_per_100g': 340, 'max_quantity': 100, 'category': 'fat'},
            
            # Vegetables (25 ingredients)
            {'name': 'broccoli', 'protein_per_100g': 2.8, 'carbs_per_100g': 7, 'fat_per_100g': 0.4, 'calories_per_100g': 34, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'spinach', 'protein_per_100g': 2.9, 'carbs_per_100g': 3.6, 'fat_per_100g': 0.4, 'calories_per_100g': 23, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'kale', 'protein_per_100g': 4.3, 'carbs_per_100g': 9, 'fat_per_100g': 0.9, 'calories_per_100g': 49, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'arugula', 'protein_per_100g': 2.6, 'carbs_per_100g': 3.7, 'fat_per_100g': 0.7, 'calories_per_100g': 25, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'romaine_lettuce', 'protein_per_100g': 1.2, 'carbs_per_100g': 2.9, 'fat_per_100g': 0.3, 'calories_per_100g': 17, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'carrots', 'protein_per_100g': 0.9, 'carbs_per_100g': 10, 'fat_per_100g': 0.2, 'calories_per_100g': 41, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'bell_peppers', 'protein_per_100g': 0.9, 'carbs_per_100g': 6, 'fat_per_100g': 0.2, 'calories_per_100g': 20, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'tomatoes', 'protein_per_100g': 0.9, 'carbs_per_100g': 3.9, 'fat_per_100g': 0.2, 'calories_per_100g': 18, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'cucumber', 'protein_per_100g': 0.7, 'carbs_per_100g': 3.6, 'fat_per_100g': 0.1, 'calories_per_100g': 16, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'zucchini', 'protein_per_100g': 1.2, 'carbs_per_100g': 3.1, 'fat_per_100g': 0.3, 'calories_per_100g': 17, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'cauliflower', 'protein_per_100g': 1.9, 'carbs_per_100g': 5, 'fat_per_100g': 0.3, 'calories_per_100g': 25, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'brussels_sprouts', 'protein_per_100g': 3.4, 'carbs_per_100g': 9, 'fat_per_100g': 0.3, 'calories_per_100g': 43, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'asparagus', 'protein_per_100g': 2.2, 'carbs_per_100g': 3.9, 'fat_per_100g': 0.1, 'calories_per_100g': 20, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'green_beans', 'protein_per_100g': 1.8, 'carbs_per_100g': 7, 'fat_per_100g': 0.2, 'calories_per_100g': 31, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'peas', 'protein_per_100g': 5.4, 'carbs_per_100g': 14, 'fat_per_100g': 0.4, 'calories_per_100g': 84, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'corn', 'protein_per_100g': 3.2, 'carbs_per_100g': 19, 'fat_per_100g': 1.2, 'calories_per_100g': 86, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'onion', 'protein_per_100g': 1.1, 'carbs_per_100g': 9, 'fat_per_100g': 0.1, 'calories_per_100g': 40, 'max_quantity': 200, 'category': 'vegetable'},
            {'name': 'garlic', 'protein_per_100g': 6.4, 'carbs_per_100g': 33, 'fat_per_100g': 0.5, 'calories_per_100g': 149, 'max_quantity': 50, 'category': 'vegetable'},
            {'name': 'ginger', 'protein_per_100g': 1.8, 'carbs_per_100g': 18, 'fat_per_100g': 0.8, 'calories_per_100g': 80, 'max_quantity': 50, 'category': 'vegetable'},
            {'name': 'mushrooms', 'protein_per_100g': 3.1, 'carbs_per_100g': 3.3, 'fat_per_100g': 0.3, 'calories_per_100g': 22, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'eggplant', 'protein_per_100g': 1, 'carbs_per_100g': 6, 'fat_per_100g': 0.2, 'calories_per_100g': 25, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'squash', 'protein_per_100g': 1.2, 'carbs_per_100g': 6, 'fat_per_100g': 0.2, 'calories_per_100g': 26, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'pumpkin', 'protein_per_100g': 1, 'carbs_per_100g': 6.5, 'fat_per_100g': 0.1, 'calories_per_100g': 26, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'beets', 'protein_per_100g': 1.6, 'carbs_per_100g': 10, 'fat_per_100g': 0.2, 'calories_per_100g': 43, 'max_quantity': 300, 'category': 'vegetable'},
            {'name': 'radishes', 'protein_per_100g': 0.9, 'carbs_per_100g': 3.4, 'fat_per_100g': 0.1, 'calories_per_100g': 16, 'max_quantity': 300, 'category': 'vegetable'},
        ]
        
        self.current_ingredients = []
    
    def _select_optimal_ingredients(self, target_macros: Dict, rag_ingredients: List[Dict]) -> List[Dict]:
        """Intelligently select optimal ingredients to add to RAG ingredients"""
        logger.info(f"🧠 Selecting optimal ingredients for targets: {target_macros}")
        
        # Calculate current totals from RAG ingredients
        current_totals = self._calculate_current_totals(rag_ingredients)
        deficits = self._calculate_macro_deficits(current_totals, target_macros)
        
        # Get existing ingredient categories to avoid duplicates
        existing_categories = set()
        existing_names = set()
        for ing in rag_ingredients:
            existing_names.add(ing.get('name', '').lower())
            # Check if it's a protein source
            if ing.get('protein_per_100g', 0) > 15:
                existing_categories.add('protein')
            # Check if it's a carb source  
            if ing.get('carbs_per_100g', 0) > 20:
                existing_categories.add('carbs')
            # Check if it's a fat source
            if ing.get('fat_per_100g', 0) > 10:
                existing_categories.add('fat')
        
        selected_ingredients = []
        
        # Select protein ingredients if needed
        if deficits['protein'] > 10 and 'protein' not in existing_categories:
            protein_ingredients = self._select_ingredients_by_macro('protein', deficits['protein'], existing_names)
            selected_ingredients.extend(protein_ingredients)
            logger.info(f"🥩 Selected {len(protein_ingredients)} protein ingredients")
        
        # Select carb ingredients if needed
        if deficits['carbs'] > 10 and 'carbs' not in existing_categories:
            carb_ingredients = self._select_ingredients_by_macro('carbs', deficits['carbs'], existing_names)
            selected_ingredients.extend(carb_ingredients)
            logger.info(f"🍞 Selected {len(carb_ingredients)} carb ingredients")
        
        # Select fat ingredients if needed
        if deficits['fat'] > 5 and 'fat' not in existing_categories:
            fat_ingredients = self._select_ingredients_by_macro('fat', deficits['fat'], existing_names)
            selected_ingredients.extend(fat_ingredients)
            logger.info(f"🥑 Selected {len(fat_ingredients)} fat ingredients")
        
        # If still have deficits, add more ingredients
        if len(selected_ingredients) < 3:
            additional_ingredients = self._select_additional_ingredients(deficits, existing_names, selected_ingredients)
            selected_ingredients.extend(additional_ingredients)
            logger.info(f"➕ Added {len(additional_ingredients)} additional ingredients")
        
        logger.info(f"🎯 Total selected ingredients: {len(selected_ingredients)}")
        return selected_ingredients
    
    def _select_ingredients_by_macro(self, macro: str, deficit: float, existing_names: set) -> List[Dict]:
        """Select ingredients for a specific macro deficiency"""
        try:
            logger.info(f"🔍 Selecting ingredients for macro: {macro}, deficit: {deficit:.1f}g")
            
            # Validate macro name
            valid_macros = ['protein', 'carbs', 'fat', 'calories']
            if macro not in valid_macros:
                logger.error(f"❌ Invalid macro name: {macro}. Valid macros: {valid_macros}")
                return []
            
            candidates = []
            
            for ingredient in self.ingredients_db:
                try:
                    if ingredient['name'].lower() not in existing_names:
                        # Safely get macro content with proper error handling
                        macro_field = f'{macro}_per_100g'
                        macro_content = ingredient.get(macro_field, 0)
                        
                        # Ensure macro_content is a number
                        if not isinstance(macro_content, (int, float)):
                            logger.warning(f"⚠️ Invalid macro content for {ingredient['name']}: {macro_content} (type: {type(macro_content)})")
                            macro_content = 0
                        
                        if macro_content > 0:
                            # Calculate efficiency (macro per calorie)
                            calories = ingredient.get('calories_per_100g', 1)
                            if not isinstance(calories, (int, float)) or calories <= 0:
                                calories = 1
                            
                            efficiency = macro_content / max(calories, 1)
                            
                            # Calculate quantity needed
                            max_qty = ingredient.get('max_quantity', 200)
                            if not isinstance(max_qty, (int, float)) or max_qty <= 0:
                                max_qty = 200
                            
                            quantity_needed = min((deficit / macro_content) * 100, max_qty)
                            
                            # Calculate score
                            score = efficiency * (1 - (quantity_needed / max_qty))
                            
                            candidates.append({
                                'ingredient': ingredient.copy(),
                                'efficiency': efficiency,
                                'quantity_needed': quantity_needed,
                                'score': score
                            })
                            
                except Exception as e:
                    logger.warning(f"⚠️ Error processing ingredient {ingredient.get('name', 'unknown')}: {e}")
                    continue
            
            logger.info(f"📊 Found {len(candidates)} candidate ingredients for {macro}")
            
            # Sort by score and select top candidates
            candidates.sort(key=lambda x: x['score'], reverse=True)
            
            selected = []
            remaining_deficit = deficit
            
            for candidate in candidates[:3]:  # Select up to 3 ingredients
                if remaining_deficit <= 0:
                    break
                    
                try:
                    ingredient = candidate['ingredient'].copy()
                    ingredient['quantity_needed'] = candidate['quantity_needed']
                    selected.append(ingredient)
                    
                    # Update remaining deficit
                    macro_content = ingredient.get(f'{macro}_per_100g', 0)
                    if isinstance(macro_content, (int, float)) and macro_content > 0:
                        remaining_deficit -= (candidate['quantity_needed'] / 100) * macro_content
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing candidate {candidate.get('ingredient', {}).get('name', 'unknown')}: {e}")
                    continue
            
            logger.info(f"✅ Selected {len(selected)} ingredients for {macro}")
            return selected
            
        except Exception as e:
            logger.error(f"❌ Error in _select_ingredients_by_macro for {macro}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def _select_additional_ingredients(self, deficits: Dict, existing_names: set, already_selected: List[Dict]) -> List[Dict]:
        """Select additional ingredients to fill remaining deficits"""
        additional = []
        
        # Find ingredients that can help with multiple macros
        for ingredient in self.ingredients_db:
            if ingredient['name'].lower() not in existing_names:
                # Check if this ingredient helps with multiple deficits
                helps_with = []
                if deficits['protein'] > 5 and ingredient.get('protein_per_100g', 0) > 5:
                    helps_with.append('protein')
                if deficits['carbs'] > 5 and ingredient.get('carbs_per_100g', 0) > 10:
                    helps_with.append('carbs')
                if deficits['fat'] > 3 and ingredient.get('fat_per_100g', 0) > 5:
                    helps_with.append('fat')
                
                if len(helps_with) >= 2:  # Helps with at least 2 macros
                    # Calculate balanced quantity
                    quantities = []
                    for macro in helps_with:
                        macro_content = ingredient.get(f'{macro}_per_100g', 0)
                        deficit = deficits[macro]
                        qty = min((deficit / macro_content) * 100, ingredient.get('max_quantity', 200))
                        quantities.append(qty)
                    
                    # Use the minimum quantity to avoid over-supplementing
                    balanced_quantity = min(quantities)
                    
                    selected_ingredient = ingredient.copy()
                    selected_ingredient['quantity_needed'] = balanced_quantity
                    additional.append(selected_ingredient)
                    
                    if len(additional) >= 2:  # Limit additional ingredients
                        break
        
        return additional
    
    def _fallback_ingredient_selection(self, deficits: Dict, rag_ingredients: List[Dict]) -> List[Dict]:
        """Fallback ingredient selection when intelligent selection fails"""
        logger.info("🔄 Using fallback ingredient selection")
        
        supplementary_ingredients = []
        existing_names = {ing.get('name', '').lower() for ing in rag_ingredients}
        
        try:
            # Simple protein supplement if needed
            if deficits['protein'] > 10:
                protein_ingredient = self._find_best_supplement('protein', deficits['protein'])
                if protein_ingredient and protein_ingredient['name'].lower() not in existing_names:
                    supplementary_ingredients.append(protein_ingredient)
                    existing_names.add(protein_ingredient['name'].lower())
                    logger.info(f"🥩 Fallback protein: {protein_ingredient['name']}")
            
            # Simple carb supplement if needed
            if deficits['carbs'] > 10:
                carb_ingredient = self._find_best_supplement('carbs', deficits['carbs'])
                if carb_ingredient and carb_ingredient['name'].lower() not in existing_names:
                    supplementary_ingredients.append(carb_ingredient)
                    existing_names.add(carb_ingredient['name'].lower())
                    logger.info(f"🍞 Fallback carbs: {carb_ingredient['name']}")
            
            # Simple fat supplement if needed
            if deficits['fat'] > 5:
                fat_ingredient = self._find_best_supplement('fat', deficits['fat'])
                if fat_ingredient and fat_ingredient['name'].lower() not in existing_names:
                    supplementary_ingredients.append(fat_ingredient)
                    existing_names.add(fat_ingredient['name'].lower())
                    logger.info(f"🥑 Fallback fat: {fat_ingredient['name']}")
            
        except Exception as e:
            logger.error(f"❌ Error in fallback ingredient selection: {e}")
        
        logger.info(f"🔄 Fallback selection complete: {len(supplementary_ingredients)} ingredients")
        return supplementary_ingredients
    
    def optimize_single_meal(self, rag_response: Dict, target_macros: Dict, user_preferences: Dict, meal_type: str, request_data: Dict = None) -> Dict:
        """Simple meal optimization: add minimal supplements to reach targets"""
        start_time = time.time()
        
        try:
            logger.info(f"🚀 Starting meal optimization for {meal_type}")
            logger.info(f"📊 Target macros: {target_macros}")
            
            # Initialize request_data if not provided
            if request_data is None:
                request_data = {}
            
            # Validate input data
            if not rag_response or not target_macros:
                raise ValueError("Missing required input data: rag_response or target_macros")
            
            # Validate target macros structure
            required_macros = ['calories', 'protein', 'carbs', 'fat']
            
            # Handle different possible macro key names
            macro_mapping = {
                'carbohydrates': 'carbs',
                'carb': 'carbs',
                'protein': 'protein',
                'proteins': 'protein',
                'fat': 'fat',
                'fats': 'fat',
                'calories': 'calories',
                'calorie': 'calories'
            }
            
            # Normalize target_macros keys
            normalized_macros = {}
            for key, value in target_macros.items():
                normalized_key = macro_mapping.get(key.lower(), key.lower())
                normalized_macros[normalized_key] = value
            
            # Check if we have all required macros
            missing_macros = []
            for macro in required_macros:
                if macro not in normalized_macros:
                    missing_macros.append(macro)
                elif not isinstance(normalized_macros[macro], (int, float)) or normalized_macros[macro] < 0:
                    logger.warning(f"⚠️ Invalid {macro} value: {normalized_macros[macro]}")
                    # Use default value for invalid macros
                    if macro in ['calories', 'protein', 'carbs', 'fat']:
                        default_values = {'calories': 500, 'protein': 30, 'carbs': 50, 'fat': 15}
                        normalized_macros[macro] = default_values[macro]
                        logger.info(f"🔄 Using default value for {macro}: {default_values[macro]}")
            
            if missing_macros:
                logger.warning(f"⚠️ Missing macros: {missing_macros}")
                logger.warning(f"⚠️ Available keys: {list(target_macros.keys())}")
                logger.warning(f"⚠️ Normalized keys: {list(normalized_macros.keys())}")
                
                # Try to provide default values for missing macros
                default_macros = {
                    'calories': 500,
                    'protein': 30,
                    'carbs': 50,
                    'fat': 15
                }
                
                for missing_macro in missing_macros:
                    if missing_macro in default_macros:
                        normalized_macros[missing_macro] = default_macros[missing_macro]
                        logger.info(f"🔄 Using default value for {missing_macro}: {default_macros[missing_macro]}")
                
                # Update target_macros with normalized values
                target_macros = normalized_macros.copy()
            else:
                # Update target_macros with normalized values
                target_macros = normalized_macros.copy()
            
            # Extract RAG ingredients
            rag_ingredients = self._extract_rag_ingredients(rag_response)
            logger.info(f"🍽️ RAG ingredients: {len(rag_ingredients)} items")
            
            # Calculate current totals
            current_totals = self._calculate_current_totals(rag_ingredients)
            deficits = self._calculate_macro_deficits(current_totals, target_macros)
            
            logger.info(f"📊 Deficits: protein={deficits['protein']:.1f}g, carbs={deficits['carbs']:.1f}g, fat={deficits['fat']:.1f}g")
            
            # Add minimal supplements to fill deficits
            supplementary_ingredients = []
            
            try:
                # Use intelligent ingredient selection instead of simple supplementation
                supplementary_ingredients = self._select_optimal_ingredients(target_macros, rag_ingredients)
                logger.info(f"✅ Successfully selected {len(supplementary_ingredients)} supplementary ingredients")
            except Exception as e:
                logger.error(f"❌ Error in ingredient selection: {e}")
                # Fallback to simple supplementation
                supplementary_ingredients = self._fallback_ingredient_selection(deficits, rag_ingredients)
                logger.info(f"🔄 Using fallback ingredient selection: {len(supplementary_ingredients)} ingredients")
            
            # Combine all ingredients
            all_ingredients = rag_ingredients + supplementary_ingredients
            logger.info(f"📊 Total: {len(rag_ingredients)} RAG + {len(supplementary_ingredients)} supplements = {len(all_ingredients)} total")
            
            # Run advanced optimization algorithms and pick the best result
            try:
                optimization_result = self._run_advanced_optimizations(all_ingredients, target_macros)
                logger.info(f"✅ Optimization completed: {optimization_result['method']}")
            except Exception as e:
                logger.error(f"❌ Error in advanced optimization: {e}")
                # Fallback to simple optimization
                optimization_result = self._fallback_optimize(all_ingredients, target_macros)
                logger.info(f"🔄 Using fallback optimization: {optimization_result['method']}")
            
            # Calculate final meal
            try:
                final_meal = self._calculate_final_meal(all_ingredients, optimization_result['quantities'])
                logger.info(f"✅ Final meal calculated successfully")
            except Exception as e:
                logger.error(f"❌ Error calculating final meal: {e}")
                # Use current totals as fallback
                final_meal = current_totals
                logger.info(f"🔄 Using current totals as fallback")
            
            # Check achievement
            try:
                target_achievement = self._check_target_achievement(final_meal, target_macros)
                logger.info(f"✅ Target achievement calculated")
            except Exception as e:
                logger.error(f"❌ Error calculating target achievement: {e}")
                # Create basic achievement info
                target_achievement = {
                    'calories': False, 'protein': False, 'carbs': False, 'fat': False, 'overall': False
                }
                logger.info(f"🔄 Using basic achievement info")
            
            computation_time = time.time() - start_time
            
            # Format meal ingredients for Next.js
            formatted_meal = []
            for i, ingredient in enumerate(all_ingredients):
                quantity = optimization_result['quantities'][i] if i < len(optimization_result['quantities']) else ingredient.get('quantity_needed', 100)
                formatted_meal.append({
                    "name": ingredient['name'].replace('_', ' ').title(),
                    "quantity_needed": round(quantity, 1),
                    "protein_per_100g": ingredient.get('protein_per_100g', 0),
                    "carbs_per_100g": ingredient.get('carbs_per_100g', 0),
                    "fat_per_100g": ingredient.get('fat_per_100g', 0),
                    "calories_per_100g": ingredient.get('calories_per_100g', 0)
                })
            
            return {
                "user_id": request_data.get('user_id', 'default_user'),
                "success": True,
                "optimization_result": {
                    "success": True,
                    "method": optimization_result['method'],
                    "computation_time": round(computation_time, 3)
                },
                "meal": formatted_meal,
                "nutritional_totals": final_meal,
                "target_achievement": target_achievement
            }
            
        except Exception as e:
            computation_time = time.time() - start_time
            logger.error(f"❌ Fatal error in meal optimization: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Return error response
            return {
                "optimization_result": {
                    "success": False,
                    "method": "Error",
                    "computation_time": round(computation_time, 3),
                    "error": str(e)
                },
                "meal": [],
                "nutritional_totals": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
                "target_achievement": {"overall": False}
            }
    
    def _extract_rag_ingredients(self, rag_response: Dict) -> List[Dict]:
        """Extract ingredients from RAG response with deduplication"""
        ingredients = []
        seen_ingredients = set()
        
        for suggestion in rag_response.get('suggestions', []):
            for ingredient in suggestion.get('ingredients', []):
                ingredient_name = ingredient.get('name', '').strip()
                
                if ingredient_name.lower() not in seen_ingredients:
                    ingredients.append(ingredient)
                    seen_ingredients.add(ingredient_name.lower())
                else:
                    logger.info(f"⚠️ Skipping duplicate: {ingredient_name}")
        
        return ingredients
    
    def _calculate_current_totals(self, ingredients: List[Dict]) -> Dict:
        """Calculate current nutritional totals"""
        totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
        
        for ingredient in ingredients:
            quantity = ingredient.get('quantity_needed', 100) / 100  # Convert to ratio
            totals['calories'] += ingredient.get('calories_per_100g', 0) * quantity
            totals['protein'] += ingredient.get('protein_per_100g', 0) * quantity
            totals['carbs'] += ingredient.get('carbs_per_100g', 0) * quantity
            totals['fat'] += ingredient.get('fat_per_100g', 0) * quantity
        
        return totals
    
    def _calculate_macro_deficits(self, current: Dict, target: Dict) -> Dict:
        """Calculate macro deficits"""
        return {
            'calories': max(0, target['calories'] - current['calories']),
            'protein': max(0, target['protein'] - current['protein']),
            'carbs': max(0, target['carbs'] - current['carbs']),
            'fat': max(0, target['fat'] - current['fat'])
        }
    
    def _find_best_supplement(self, macro: str, deficit: float) -> Optional[Dict]:
        """Find best supplement for a specific macro"""
        best_ingredient = None
        best_efficiency = 0
        
        for ingredient in self.ingredients_db:
            macro_content = ingredient.get(f'{macro}_per_100g', 0)
            if macro_content > 0:
                # Calculate efficiency (macro per calorie)
                calories = ingredient.get('calories_per_100g', 1)
                efficiency = macro_content / max(calories, 1)
                
                if efficiency > best_efficiency:
                    best_efficiency = efficiency
                    best_ingredient = ingredient.copy()
        
        if best_ingredient:
            # Calculate exact quantity needed to fill the deficit
            macro_content = best_ingredient.get(f'{macro}_per_100g', 0)
            exact_quantity = (deficit / macro_content) * 100
            
            # Use exact quantity needed (no bounds)
            best_ingredient['quantity_needed'] = exact_quantity
            
            logger.info(f"📏 {macro} supplement: {best_ingredient['name']} - {exact_quantity:.1f}g needed")
        
        return best_ingredient
    
    def _run_advanced_optimizations(self, ingredients: List[Dict], target_macros: Dict) -> Dict:
        """Run advanced optimization algorithms and return the best result"""
        logger.info(f"🚀 Running advanced optimization algorithms...")
        
        results = []
        
        # Algorithm 1: Linear Optimization with PuLP
        try:
            result1 = self._linear_optimize(ingredients, target_macros)
            results.append(result1)
            logger.info(f"✅ Algorithm 1 (Linear Optimization) completed")
        except Exception as e:
            logger.warning(f"❌ Linear optimization failed: {e}")
        
        # Algorithm 2: Differential Evolution
        try:
            result2 = self._differential_evolution_optimize(ingredients, target_macros)
            results.append(result2)
            logger.info(f"✅ Algorithm 2 (Differential Evolution) completed")
        except Exception as e:
            logger.warning(f"❌ Differential evolution failed: {e}")
        
        # Algorithm 3: Genetic Algorithm
        try:
            result3 = self._genetic_algorithm_optimize(ingredients, target_macros)
            results.append(result3)
            logger.info(f"✅ Algorithm 3 (Genetic Algorithm) completed")
        except Exception as e:
            logger.warning(f"❌ Genetic algorithm failed: {e}")
        
        # Algorithm 4: Optuna Optimization
        try:
            result4 = self._optuna_optimize(ingredients, target_macros)
            results.append(result4)
            logger.info(f"✅ Algorithm 4 (Optuna) completed")
        except Exception as e:
            logger.warning(f"❌ Optuna optimization failed: {e}")
        
        # Algorithm 5: Hybrid Optimization
        try:
            result5 = self._hybrid_optimize(ingredients, target_macros)
            results.append(result5)
            logger.info(f"✅ Algorithm 5 (Hybrid) completed")
        except Exception as e:
            logger.warning(f"❌ Hybrid optimization failed: {e}")
        
        # Evaluate all results and pick the best one
        if results:
            best_result = self._evaluate_optimization_results(results, ingredients, target_macros)
            logger.info(f"🏆 Best algorithm: {best_result['method']}")
            return best_result
        else:
            # Fallback to simple optimization if all algorithms fail
            logger.warning("⚠️ All optimization algorithms failed, using fallback")
            return self._fallback_optimize(ingredients, target_macros)
    
    def _linear_optimize(self, ingredients: List[Dict], target_macros: Dict) -> Dict:
        """Linear optimization using PuLP"""
        try:
            from pulp import LpMinimize, LpProblem, LpVariable, lpSum, value
            
            # Create optimization problem
            prob = LpProblem("Meal_Optimization", LpMinimize)
            
            # Variables: quantity of each ingredient (in grams)
            x = {}
            for i, ingredient in enumerate(ingredients):
                max_qty = ingredient.get('max_quantity', 200)
                x[i] = LpVariable(f"x_{i}", lowBound=0, upBound=max_qty)
            
            # Objective: minimize total calories
            prob += lpSum(x[i] * ingredients[i].get('calories_per_100g', 0) / 100 for i in range(len(ingredients)))
            
            # Constraints
            # Protein constraint
            prob += lpSum(x[i] * ingredients[i].get('protein_per_100g', 0) / 100 for i in range(len(ingredients))) >= target_macros['protein']
            
            # Carbs constraint
            prob += lpSum(x[i] * ingredients[i].get('carbs_per_100g', 0) / 100 for i in range(len(ingredients))) >= target_macros['carbs']
            
            # Fat constraint
            prob += lpSum(x[i] * ingredients[i].get('fat_per_100g', 0) / 100 for i in range(len(ingredients))) >= target_macros['fat']
            
            # Solve
            prob.solve()
            
            if prob.status == 1:  # Optimal solution found
                quantities = [value(x[i]) for i in range(len(ingredients))]
                return {
                    'success': True,
                    'method': 'Linear Optimization (PuLP)',
                    'quantities': quantities
                }
            else:
                raise Exception("No optimal solution found")
                
        except ImportError:
            raise Exception("PuLP not available")
        except Exception as e:
            raise Exception(f"Linear optimization error: {e}")
    
    def _differential_evolution_optimize(self, ingredients: List[Dict], target_macros: Dict) -> Dict:
        """Differential evolution optimization using SciPy"""
        try:
            # Prepare data for optimization
            ingredient_data = []
            bounds = []
            
            for ingredient in ingredients:
                max_qty = ingredient.get('max_quantity', 200)
                bounds.append((0, max_qty))
                ingredient_data.append({
                    'protein': ingredient.get('protein_per_100g', 0),
                    'carbs': ingredient.get('carbs_per_100g', 0),
                    'fat': ingredient.get('fat_per_100g', 0),
                    'calories': ingredient.get('calories_per_100g', 0)
                })
            
            # Objective function
            def objective(quantities):
                total_protein = sum(qty * data['protein'] / 100 for qty, data in zip(quantities, ingredient_data))
                total_carbs = sum(qty * data['carbs'] / 100 for qty, data in zip(quantities, ingredient_data))
                total_fat = sum(qty * data['fat'] / 100 for qty, data in zip(quantities, ingredient_data))
                total_calories = sum(qty * data['calories'] / 100 for qty, data in zip(quantities, ingredient_data))
                
                # Penalty for not meeting targets
                penalty = 0
                if total_protein < target_macros['protein']:
                    penalty += (target_macros['protein'] - total_protein) ** 2 * 100
                if total_carbs < target_macros['carbs']:
                    penalty += (target_macros['carbs'] - total_carbs) ** 2 * 100
                if total_fat < target_macros['fat']:
                    penalty += (target_macros['fat'] - total_fat) ** 2 * 100
                
                return total_calories + penalty
            
            # Run differential evolution
            result = differential_evolution(
                objective, 
                bounds, 
                popsize=15, 
                mutation=0.5, 
                recombination=0.7, 
                maxiter=100,
                seed=42
            )
            
            if result.success:
                return {
                    'success': True,
                    'method': 'Differential Evolution (SciPy)',
                    'quantities': result.x.tolist()
                }
            else:
                raise Exception("Differential evolution did not converge")
                
        except Exception as e:
            raise Exception(f"Differential evolution error: {e}")
    
    def _genetic_algorithm_optimize(self, ingredients: List[Dict], target_macros: Dict) -> Dict:
        """Genetic algorithm optimization"""
        try:
            # Prepare data
            ingredient_data = []
            bounds = []
            
            for ingredient in ingredients:
                max_qty = ingredient.get('max_quantity', 200)
                bounds.append((0, max_qty))
                ingredient_data.append({
                    'protein': ingredient.get('protein_per_100g', 0),
                    'carbs': ingredient.get('carbs_per_100g', 0),
                    'fat': ingredient.get('fat_per_100g', 0),
                    'calories': ingredient.get('calories_per_100g', 0)
                })
            
            # Population size and generations
            pop_size = 50
            generations = 30
            
            # Initialize population
            population = []
            for _ in range(pop_size):
                individual = [random.uniform(bounds[i][0], bounds[i][1]) for i in range(len(ingredients))]
                population.append(individual)
            
            # Fitness function
            def fitness(individual):
                total_protein = sum(qty * data['protein'] / 100 for qty, data in zip(individual, ingredient_data))
                total_carbs = sum(qty * data['carbs'] / 100 for qty, data in zip(individual, ingredient_data))
                total_fat = sum(qty * data['fat'] / 100 for qty, data in zip(individual, ingredient_data))
                total_calories = sum(qty * data['calories'] / 100 for qty, data in zip(individual, ingredient_data))
                
                # Penalty for not meeting targets
                penalty = 0
                if total_protein < target_macros['protein']:
                    penalty += (target_macros['protein'] - total_protein) ** 2 * 100
                if total_carbs < target_macros['carbs']:
                    penalty += (target_macros['carbs'] - total_carbs) ** 2 * 100
                if total_fat < target_macros['fat']:
                    penalty += (target_macros['fat'] - total_fat) ** 2 * 100
                
                return total_calories + penalty
            
            # Evolution loop
            best_individual = None
            best_fitness = float('inf')
            
            for generation in range(generations):
                # Evaluate fitness
                fitness_scores = [fitness(ind) for ind in population]
                
                # Find best individual
                min_idx = fitness_scores.index(min(fitness_scores))
                if fitness_scores[min_idx] < best_fitness:
                    best_fitness = fitness_scores[min_idx]
                    best_individual = population[min_idx].copy()
                
                # Selection (tournament)
                new_population = []
                for _ in range(pop_size):
                    # Tournament selection
                    tournament_size = 3
                    tournament = random.sample(range(pop_size), tournament_size)
                    winner_idx = min(tournament, key=lambda i: fitness_scores[i])
                    new_population.append(population[winner_idx].copy())
                
                # Crossover and mutation
                for i in range(0, pop_size, 2):
                    if i + 1 < pop_size:
                        # Crossover
                        if random.random() < 0.7:
                            crossover_point = random.randint(1, len(ingredients) - 1)
                            new_population[i][:crossover_point], new_population[i+1][:crossover_point] = \
                                new_population[i+1][:crossover_point], new_population[i][:crossover_point]
                        
                        # Mutation
                        for j in range(len(ingredients)):
                            if random.random() < 0.1:
                                new_population[i][j] = random.uniform(bounds[j][0], bounds[j][1])
                            if random.random() < 0.1:
                                new_population[i+1][j] = random.uniform(bounds[j][0], bounds[j][1])
                
                population = new_population
            
            if best_individual:
                return {
                    'success': True,
                    'method': 'Genetic Algorithm',
                    'quantities': best_individual
                }
            else:
                raise Exception("Genetic algorithm did not find solution")
                
        except Exception as e:
            raise Exception(f"Genetic algorithm error: {e}")
    
    def _optuna_optimize(self, ingredients: List[Dict], target_macros: Dict) -> Dict:
        """Optuna optimization"""
        try:
            # Prepare data
            ingredient_data = []
            bounds = []
            
            for ingredient in ingredients:
                max_qty = ingredient.get('max_quantity', 200)
                bounds.append((0, max_qty))
                ingredient_data.append({
                    'protein': ingredient.get('protein_per_100g', 0),
                    'carbs': ingredient.get('carbs_per_100g', 0),
                    'fat': ingredient.get('fat_per_100g', 0),
                    'calories': ingredient.get('calories_per_100g', 0)
                })
            
            # Objective function for Optuna
            def objective(trial):
                quantities = []
                for i in range(len(ingredients)):
                    qty = trial.suggest_float(f'qty_{i}', bounds[i][0], bounds[i][1])
                    quantities.append(qty)
                
                total_protein = sum(qty * data['protein'] / 100 for qty, data in zip(quantities, ingredient_data))
                total_carbs = sum(qty * data['carbs'] / 100 for qty, data in zip(quantities, ingredient_data))
                total_fat = sum(qty * data['fat'] / 100 for qty, data in zip(quantities, ingredient_data))
                total_calories = sum(qty * data['calories'] / 100 for qty, data in zip(quantities, ingredient_data))
                
                # Penalty for not meeting targets
                penalty = 0
                if total_protein < target_macros['protein']:
                    penalty += (target_macros['protein'] - total_protein) ** 2 * 100
                if total_carbs < target_macros['carbs']:
                    penalty += (target_macros['carbs'] - total_carbs) ** 2 * 100
                if total_fat < target_macros['fat']:
                    penalty += (target_macros['fat'] - total_fat) ** 2 * 100
                
                return total_calories + penalty
            
            # Create study and optimize
            study = optuna.create_study(direction='minimize')
            study.optimize(objective, n_trials=100)
            
            if study.best_params:
                # Extract quantities from best parameters
                quantities = []
                for i in range(len(ingredients)):
                    qty = study.best_params[f'qty_{i}']
                    quantities.append(qty)
                
                return {
                    'success': True,
                    'method': 'Optuna Optimization',
                    'quantities': quantities
                }
            else:
                raise Exception("Optuna did not find solution")
                
        except Exception as e:
            raise Exception(f"Optuna optimization error: {e}")
    
    def _hybrid_optimize(self, ingredients: List[Dict], target_macros: Dict) -> Dict:
        """Hybrid optimization combining multiple approaches"""
        try:
            # First, try differential evolution for initial solution
            de_result = self._differential_evolution_optimize(ingredients, target_macros)
            
            if de_result['success']:
                # Use DE result as starting point for genetic algorithm refinement
                initial_population = []
                pop_size = 20
                
                # Create population around the DE solution
                for _ in range(pop_size):
                    individual = de_result['quantities'].copy()
                    # Add some variation
                    for i in range(len(individual)):
                        variation = random.uniform(0.8, 1.2)
                        individual[i] = max(0, min(individual[i] * variation, ingredients[i].get('max_quantity', 200)))
                    initial_population.append(individual)
                
                # Run genetic algorithm with this initial population
                ga_result = self._genetic_algorithm_optimize_with_population(ingredients, target_macros, initial_population)
                
                if ga_result['success']:
                    return {
                        'success': True,
                        'method': 'Hybrid (DE + GA)',
                        'quantities': ga_result['quantities']
                    }
                else:
                    return de_result  # Fall back to DE result
            else:
                raise Exception("Differential evolution failed in hybrid approach")
                
        except Exception as e:
            raise Exception(f"Hybrid optimization error: {e}")
    
    def _genetic_algorithm_optimize_with_population(self, ingredients: List[Dict], target_macros: Dict, initial_population: List[List[float]]) -> Dict:
        """Genetic algorithm with custom initial population"""
        try:
            # Prepare data
            ingredient_data = []
            bounds = []
            
            for ingredient in ingredients:
                max_qty = ingredient.get('max_quantity', 200)
                bounds.append((0, max_qty))
                ingredient_data.append({
                    'protein': ingredient.get('protein_per_100g', 0),
                    'carbs': ingredient.get('carbs_per_100g', 0),
                    'fat': ingredient.get('fat_per_100g', 0),
                    'calories': ingredient.get('calories_per_100g', 0)
                })
            
            # Use initial population
            population = initial_population.copy()
            pop_size = len(population)
            generations = 20  # Fewer generations for refinement
            
            # Fitness function
            def fitness(individual):
                total_protein = sum(qty * data['protein'] / 100 for qty, data in zip(individual, ingredient_data))
                total_carbs = sum(qty * data['carbs'] / 100 for qty, data in zip(individual, ingredient_data))
                total_fat = sum(qty * data['fat'] / 100 for qty, data in zip(individual, ingredient_data))
                total_calories = sum(qty * data['calories'] / 100 for qty, data in zip(individual, ingredient_data))
                
                # Penalty for not meeting targets
                penalty = 0
                if total_protein < target_macros['protein']:
                    penalty += (target_macros['protein'] - total_protein) ** 2 * 100
                if total_carbs < target_macros['carbs']:
                    penalty += (target_macros['carbs'] - total_carbs) ** 2 * 100
                if total_fat < target_macros['fat']:
                    penalty += (target_macros['fat'] - total_fat) ** 2 * 100
                
                return total_calories + penalty
            
            # Evolution loop
            best_individual = None
            best_fitness = float('inf')
            
            for generation in range(generations):
                # Evaluate fitness
                fitness_scores = [fitness(ind) for ind in population]
                
                # Find best individual
                min_idx = fitness_scores.index(min(fitness_scores))
                if fitness_scores[min_idx] < best_fitness:
                    best_fitness = fitness_scores[min_idx]
                    best_individual = population[min_idx].copy()
                
                # Selection (tournament)
                new_population = []
                for _ in range(pop_size):
                    # Tournament selection
                    tournament_size = 3
                    tournament = random.sample(range(pop_size), tournament_size)
                    winner_idx = min(tournament, key=lambda i: fitness_scores[i])
                    new_population.append(population[winner_idx].copy())
                
                # Crossover and mutation (gentler for refinement)
                for i in range(0, pop_size, 2):
                    if i + 1 < pop_size:
                        # Crossover
                        if random.random() < 0.5:
                            crossover_point = random.randint(1, len(ingredients) - 1)
                            new_population[i][:crossover_point], new_population[i+1][:crossover_point] = \
                                new_population[i+1][:crossover_point], new_population[i][:crossover_point]
                        
                        # Mutation (gentler)
                        for j in range(len(ingredients)):
                            if random.random() < 0.05:  # Lower mutation rate
                                variation = random.uniform(0.9, 1.1)  # Smaller variation
                                new_population[i][j] = max(0, min(new_population[i][j] * variation, bounds[j][1]))
                            if random.random() < 0.05:
                                variation = random.uniform(0.9, 1.1)
                                new_population[i+1][j] = max(0, min(new_population[i+1][j] * variation, bounds[j][1]))
                
                population = new_population
            
            if best_individual:
                return {
                    'success': True,
                    'method': 'Genetic Algorithm (Refinement)',
                    'quantities': best_individual
                }
            else:
                raise Exception("Genetic algorithm refinement failed")
                
        except Exception as e:
            raise Exception(f"Genetic algorithm refinement error: {e}")
    
    def _fallback_optimize(self, ingredients: List[Dict], target_macros: Dict) -> Dict:
        """Fallback optimization method"""
        logger.info("🔄 Using fallback optimization method")
        
        quantities = [ingredient.get('quantity_needed', 100) for ingredient in ingredients]
        
        # Simple scaling approach
        for attempt in range(3):
            current_totals = self._calculate_current_totals(ingredients)
            
            if (current_totals['calories'] >= target_macros['calories'] * 0.95 and
                current_totals['protein'] >= target_macros['protein'] * 0.95 and
                current_totals['carbs'] >= target_macros['carbs'] * 0.95 and
                current_totals['fat'] >= target_macros['fat'] * 0.95):
                break
            
            # Scale up quantities
            for i in range(len(quantities)):
                max_qty = ingredients[i].get('max_quantity', 200)
                quantities[i] = min(quantities[i] * 1.1, max_qty)
        
        return {
            'success': True,
            'method': 'Fallback Scaling',
            'quantities': quantities
        }
    
    def _evaluate_optimization_results(self, results: List[Dict], ingredients: List[Dict], target_macros: Dict) -> Dict:
        """Evaluate all optimization results and return the best one"""
        best_result = None
        best_score = float('inf')
        
        for result in results:
            if result['success']:
                # Calculate final meal with these quantities
                final_meal = self._calculate_final_meal(ingredients, result['quantities'])
                score = self._calculate_optimization_score(final_meal, target_macros)
                
                if score < best_score:
                    best_score = score
                    best_result = result
        
        return best_result
    
    def _calculate_optimization_score(self, actual: Dict, target: Dict) -> float:
        """Calculate optimization score (lower is better)"""
        score = 0
        
        for macro in ['calories', 'protein', 'carbs', 'fat']:
            target_val = target[macro]
            actual_val = actual[macro]
            
            if target_val > 0:
                if actual_val > target_val:
                    # Penalize over-target
                    diff = (actual_val - target_val) / target_val
                    score += diff * diff * 5  # 5x penalty for over-target
                else:
                    # Penalize under-target
                    diff = (target_val - actual_val) / target_val
                    score += diff * diff
        
        return score
    
    def _calculate_final_meal(self, ingredients: List[Dict], quantities: List[float]) -> Dict:
        """Calculate final nutritional totals"""
        totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
        
        logger.info(f"🔍 Calculating final meal with {len(ingredients)} ingredients")
        
        for i, ingredient in enumerate(ingredients):
            quantity = quantities[i] / 100  # Convert to ratio
            calories = ingredient.get('calories_per_100g', 0) * quantity
            protein = ingredient.get('protein_per_100g', 0) * quantity
            carbs = ingredient.get('carbs_per_100g', 0) * quantity
            fat = ingredient.get('fat_per_100g', 0) * quantity
            
            totals['calories'] += calories
            totals['protein'] += protein
            totals['carbs'] += carbs
            totals['fat'] += fat
            
            logger.info(f"  {ingredient['name']}: {quantities[i]:.1f}g -> {calories:.1f}cal, {protein:.1f}g protein, {carbs:.1f}g carbs, {fat:.1f}g fat")
        
        logger.info(f"📊 FINAL TOTALS: {totals['calories']:.1f}cal, {totals['protein']:.1f}g protein, {totals['carbs']:.1f}g carbs, {totals['fat']:.1f}g fat")
        
        return totals
    
    def _check_target_achievement(self, final_meal: Dict, target_macros: Dict) -> Dict:
        """Check if targets are achieved"""
        achievement = {}
        
        for macro in ['calories', 'protein', 'carbs', 'fat']:
            target = target_macros[macro]
            actual = final_meal[macro]
            
            if actual >= target * 0.95:  # 95% of target is considered achieved
                achievement[macro] = True
            else:
                achievement[macro] = False
        
        # Overall achievement
        achievement['overall'] = all(achievement.values())
        
        return achievement
