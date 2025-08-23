import os
from typing import Dict, Any

class Config:
    """Application configuration"""
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"
    
    # Database Configuration
    DATABASE_FILE = os.getenv("DATABASE_FILE", "ingredients_database.json")
    
    # Optimization Configuration
    OPTIMIZATION_TIMEOUT = int(os.getenv("OPTIMIZATION_TIMEOUT", 300))  # 5 minutes
    MAX_INGREDIENTS_PER_MEAL = int(os.getenv("MAX_INGREDIENTS_PER_MEAL", 10))
    MIN_INGREDIENT_QUANTITY = float(os.getenv("MIN_INGREDIENT_QUANTITY", 10.0))  # grams
    MAX_INGREDIENT_QUANTITY = float(os.getenv("MAX_INGREDIENT_QUANTITY", 500.0))  # grams
    
    # Genetic Algorithm Parameters
    GA_POPULATION_SIZE = int(os.getenv("GA_POPULATION_SIZE", 50))
    GA_GENERATIONS = int(os.getenv("GA_GENERATIONS", 30))
    GA_CROSSOVER_RATE = float(os.getenv("GA_CROSSOVER_RATE", 0.7))
    GA_MUTATION_RATE = float(os.getenv("GA_MUTATION_RATE", 0.2))
    
    # Differential Evolution Parameters
    DE_POPULATION_SIZE = int(os.getenv("DE_POPULATION_SIZE", 15))
    DE_MAX_ITERATIONS = int(os.getenv("DE_MAX_ITERATIONS", 100))
    
    # Nutritional Constraints
    MIN_PROTEIN_RATIO = float(os.getenv("MIN_PROTEIN_RATIO", 0.8))  # 80% of target
    MIN_CALORIE_RATIO = float(os.getenv("MIN_CALORIE_RATIO", 0.8))  # 80% of target
    MAX_SODIUM_PER_DAY = float(os.getenv("MAX_SODIUM_PER_DAY", 2300))  # mg
    MIN_FIBER_PER_DAY = float(os.getenv("MIN_FIBER_PER_DAY", 25))  # grams
    
    # Meal Distribution
    MEAL_DISTRIBUTION = {
        "breakfast": 0.25,      # 25% of daily calories
        "morning_snack": 0.15,  # 15% of daily calories
        "lunch": 0.30,          # 30% of daily calories
        "afternoon_snack": 0.10, # 10% of daily calories
        "evening_snack": 0.05,  # 5% of daily calories
        "dinner": 0.15          # 15% of daily calories
    }
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def get_meal_distribution(cls, meal_time: str) -> float:
        """Get calorie distribution for a specific meal time"""
        return cls.MEAL_DISTRIBUTION.get(meal_time, 0.0)
    
    @classmethod
    def get_optimization_weights(cls) -> Dict[str, float]:
        """Get weights for different optimization objectives"""
        return {
            "calories": 1.0,
            "protein": 1.2,      # Higher weight for protein
            "carbohydrates": 0.8,
            "fat": 0.9,
            "fiber": 0.7,
            "cost": 0.5
        }
    
    @classmethod
    def get_ingredient_categories(cls) -> Dict[str, str]:
        """Get ingredient categories with Persian translations"""
        return {
            "protein": "پروتئین",
            "carbohydrate": "کربوهیدرات",
            "fat": "چربی",
            "vegetable": "سبزیجات",
            "fruit": "میوه",
            "grain": "غلات",
            "dairy": "لبنیات",
            "nut": "آجیل",
            "spice": "ادویه",
            "herb": "گیاهان دارویی"
        }
    
    @classmethod
    def get_meal_time_translations(cls) -> Dict[str, str]:
        """Get meal time translations"""
        return {
            "breakfast": "صبحانه",
            "morning_snack": "میان‌وعده صبح",
            "lunch": "ناهار",
            "afternoon_snack": "میان‌وعده عصر",
            "evening_snack": "میان‌وعده شب",
            "dinner": "شام"
        }

