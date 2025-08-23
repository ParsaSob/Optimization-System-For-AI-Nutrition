import asyncio
import json
import os
from typing import List, Optional
from models import Ingredient, MealTime
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for ingredient storage and retrieval"""
    
    def __init__(self):
        self.ingredients_file = "ingredients_database.json"
        self.ingredients: List[Ingredient] = []
        self.initialized = False
        
    async def initialize(self):
        """Initialize database and load default ingredients"""
        if not self.initialized:
            await self._load_ingredients()
            if not self.ingredients:
                await self._create_default_ingredients()
            self.initialized = True
            logger.info(f"Database initialized with {len(self.ingredients)} ingredients")
    
    async def _load_ingredients(self):
        """Load ingredients from JSON file"""
        try:
            if os.path.exists(self.ingredients_file):
                with open(self.ingredients_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.ingredients = [Ingredient(**item) for item in data]
                    logger.info(f"Loaded {len(self.ingredients)} ingredients from database")
            else:
                logger.info("No existing ingredients database found, will create default")
        except Exception as e:
            logger.error(f"Failed to load ingredients: {e}")
            self.ingredients = []
    
    async def _save_ingredients(self):
        """Save ingredients to JSON file"""
        try:
            with open(self.ingredients_file, 'w', encoding='utf-8') as f:
                json.dump([ingredient.dict() for ingredient in self.ingredients], f, 
                         ensure_ascii=False, indent=2)
            logger.info("Ingredients saved to database")
        except Exception as e:
            logger.error(f"Failed to save ingredients: {e}")
    
    async def _create_default_ingredients(self):
        """Create default ingredient database with common foods"""
        default_ingredients = [
            # Proteins
            Ingredient(
                name="Chicken Breast",
                name_fa="سینه مرغ",
                calories_per_100g=165,
                protein_per_100g=31,
                carbs_per_100g=0,
                fat_per_100g=3.6,
                fiber_per_100g=0,
                sugar_per_100g=0,
                sodium_per_100g=74,
                category="protein",
                suitable_meals=[MealTime.BREAKFAST, MealTime.LUNCH, MealTime.DINNER],
                price_per_kg=15.0
            ),
            Ingredient(
                name="Salmon",
                name_fa="ماهی سالمون",
                calories_per_100g=208,
                protein_per_100g=25,
                carbs_per_100g=0,
                fat_per_100g=12,
                fiber_per_100g=0,
                sugar_per_100g=0,
                sodium_per_100g=59,
                category="protein",
                suitable_meals=[MealTime.LUNCH, MealTime.DINNER],
                price_per_kg=25.0
            ),
            Ingredient(
                name="Eggs",
                name_fa="تخم مرغ",
                calories_per_100g=155,
                protein_per_100g=13,
                carbs_per_100g=1.1,
                fat_per_100g=11,
                fiber_per_100g=0,
                sugar_per_100g=1.1,
                sodium_per_100g=124,
                category="protein",
                suitable_meals=[MealTime.BREAKFAST, MealTime.LUNCH, MealTime.DINNER],
                price_per_kg=8.0
            ),
            Ingredient(
                name="Greek Yogurt",
                name_fa="ماست یونانی",
                calories_per_100g=59,
                protein_per_100g=10,
                carbs_per_100g=3.6,
                fat_per_100g=0.4,
                fiber_per_100g=0,
                sugar_per_100g=3.2,
                sodium_per_100g=36,
                category="protein",
                suitable_meals=[MealTime.BREAKFAST, MealTime.MORNING_SNACK, MealTime.AFTERNOON_SNACK],
                price_per_kg=6.0
            ),
            
            # Carbohydrates
            Ingredient(
                name="Brown Rice",
                name_fa="برنج قهوه‌ای",
                calories_per_100g=111,
                protein_per_100g=2.6,
                carbs_per_100g=23,
                fat_per_100g=0.9,
                fiber_per_100g=1.8,
                sugar_per_100g=0.4,
                sodium_per_100g=5,
                category="grain",
                suitable_meals=[MealTime.LUNCH, MealTime.DINNER],
                price_per_kg=3.0
            ),
            Ingredient(
                name="Quinoa",
                name_fa="کینوا",
                calories_per_100g=120,
                protein_per_100g=4.4,
                carbs_per_100g=22,
                fat_per_100g=1.9,
                fiber_per_100g=2.8,
                sugar_per_100g=0.9,
                sodium_per_100g=7,
                category="grain",
                suitable_meals=[MealTime.BREAKFAST, MealTime.LUNCH, MealTime.DINNER],
                price_per_kg=12.0
            ),
            Ingredient(
                name="Sweet Potato",
                name_fa="سیب زمینی شیرین",
                calories_per_100g=86,
                protein_per_100g=1.6,
                carbs_per_100g=20,
                fat_per_100g=0.1,
                fiber_per_100g=3.0,
                sugar_per_100g=4.2,
                sodium_per_100g=55,
                category="vegetable",
                suitable_meals=[MealTime.LUNCH, MealTime.DINNER],
                price_per_kg=2.5
            ),
            Ingredient(
                name="Banana",
                name_fa="موز",
                calories_per_100g=89,
                protein_per_100g=1.1,
                carbs_per_100g=23,
                fat_per_100g=0.3,
                fiber_per_100g=2.6,
                sugar_per_100g=12,
                sodium_per_100g=1,
                category="fruit",
                suitable_meals=[MealTime.BREAKFAST, MealTime.MORNING_SNACK, MealTime.AFTERNOON_SNACK],
                price_per_kg=3.5
            ),
            
            # Fats
            Ingredient(
                name="Avocado",
                name_fa="آووکادو",
                calories_per_100g=160,
                protein_per_100g=2.0,
                carbs_per_100g=9,
                fat_per_100g=15,
                fiber_per_100g=6.7,
                sugar_per_100g=0.7,
                sodium_per_100g=7,
                category="fat",
                suitable_meals=[MealTime.BREAKFAST, MealTime.LUNCH, MealTime.DINNER],
                price_per_kg=18.0
            ),
            Ingredient(
                name="Almonds",
                name_fa="بادام",
                calories_per_100g=579,
                protein_per_100g=21,
                carbs_per_100g=22,
                fat_per_100g=50,
                fiber_per_100g=12.5,
                sugar_per_100g=4.8,
                sodium_per_100g=1,
                category="nut",
                suitable_meals=[MealTime.MORNING_SNACK, MealTime.AFTERNOON_SNACK, MealTime.EVENING_SNACK],
                price_per_kg=25.0
            ),
            Ingredient(
                name="Olive Oil",
                name_fa="روغن زیتون",
                calories_per_100g=884,
                protein_per_100g=0,
                carbs_per_100g=0,
                fat_per_100g=100,
                fiber_per_100g=0,
                sugar_per_100g=0,
                sodium_per_100g=2,
                category="fat",
                suitable_meals=[MealTime.BREAKFAST, MealTime.LUNCH, MealTime.DINNER],
                price_per_kg=15.0
            ),
            
            # Vegetables
            Ingredient(
                name="Spinach",
                name_fa="اسفناج",
                calories_per_100g=23,
                protein_per_100g=2.9,
                carbs_per_100g=3.6,
                fat_per_100g=0.4,
                fiber_per_100g=2.2,
                sugar_per_100g=0.4,
                sodium_per_100g=79,
                category="vegetable",
                suitable_meals=[MealTime.LUNCH, MealTime.DINNER],
                price_per_kg=4.0
            ),
            Ingredient(
                name="Broccoli",
                name_fa="کلم بروکلی",
                calories_per_100g=34,
                protein_per_100g=2.8,
                carbs_per_100g=7,
                fat_per_100g=0.4,
                fiber_per_100g=2.6,
                sugar_per_100g=1.5,
                sodium_per_100g=33,
                category="vegetable",
                suitable_meals=[MealTime.LUNCH, MealTime.DINNER],
                price_per_kg=3.5
            ),
            Ingredient(
                name="Carrots",
                name_fa="هویج",
                calories_per_100g=41,
                protein_per_100g=0.9,
                carbs_per_100g=10,
                fat_per_100g=0.2,
                fiber_per_100g=2.8,
                sugar_per_100g=4.7,
                sodium_per_100g=69,
                category="vegetable",
                suitable_meals=[MealTime.MORNING_SNACK, MealTime.AFTERNOON_SNACK, MealTime.LUNCH, MealTime.DINNER],
                price_per_kg=2.0
            ),
            
            # Dairy
            Ingredient(
                name="Milk",
                name_fa="شیر",
                calories_per_100g=42,
                protein_per_100g=3.4,
                carbs_per_100g=5.0,
                fat_per_100g=1.0,
                fiber_per_100g=0,
                sugar_per_100g=5.0,
                sodium_per_100g=44,
                category="dairy",
                suitable_meals=[MealTime.BREAKFAST, MealTime.MORNING_SNACK, MealTime.EVENING_SNACK],
                price_per_kg=2.5
            ),
            Ingredient(
                name="Cottage Cheese",
                name_fa="پنیر کوتاژ",
                calories_per_100g=98,
                protein_per_100g=11,
                carbs_per_100g=3.4,
                fat_per_100g=4.3,
                fiber_per_100g=0,
                sugar_per_100g=2.7,
                sodium_per_100g=364,
                category="dairy",
                suitable_meals=[MealTime.BREAKFAST, MealTime.MORNING_SNACK, MealTime.AFTERNOON_SNACK],
                price_per_kg=8.0
            )
        ]
        
        self.ingredients = default_ingredients
        await self._save_ingredients()
        logger.info(f"Created default database with {len(self.ingredients)} ingredients")
    
    async def add_ingredients(self, ingredients: List[Ingredient]):
        """Add new ingredients to database"""
        for ingredient in ingredients:
            # Check if ingredient already exists
            existing = next((i for i in self.ingredients if i.name.lower() == ingredient.name.lower()), None)
            if existing:
                # Update existing ingredient
                for key, value in ingredient.dict().items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                logger.info(f"Updated ingredient: {ingredient.name}")
            else:
                # Add new ingredient
                ingredient.id = f"ing_{len(self.ingredients) + 1}"
                self.ingredients.append(ingredient)
                logger.info(f"Added new ingredient: {ingredient.name}")
        
        await self._save_ingredients()
    
    async def get_all_ingredients(self) -> List[Ingredient]:
        """Get all ingredients from database"""
        return self.ingredients
    
    async def get_ingredients_by_category(self, category: str) -> List[Ingredient]:
        """Get ingredients by category"""
        return [i for i in self.ingredients if i.category.lower() == category.lower()]
    
    async def get_ingredients_by_meal_time(self, meal_time: MealTime) -> List[Ingredient]:
        """Get ingredients suitable for specific meal time"""
        return [i for i in self.ingredients if meal_time in i.suitable_meals]
    
    async def search_ingredients(self, query: str) -> List[Ingredient]:
        """Search ingredients by name (English or Persian)"""
        query_lower = query.lower()
        results = []
        
        for ingredient in self.ingredients:
            if (query_lower in ingredient.name.lower() or 
                (ingredient.name_fa and query_lower in ingredient.name_fa.lower())):
                results.append(ingredient)
        
        return results
    
    async def get_ingredient_by_id(self, ingredient_id: str) -> Optional[Ingredient]:
        """Get ingredient by ID"""
        return next((i for i in self.ingredients if i.id == ingredient_id), None)
    
    async def delete_ingredient(self, ingredient_id: str) -> bool:
        """Delete ingredient by ID"""
        ingredient = await self.get_ingredient_by_id(ingredient_id)
        if ingredient:
            self.ingredients.remove(ingredient)
            await self._save_ingredients()
            logger.info(f"Deleted ingredient: {ingredient.name}")
            return True
        return False
    
    async def update_ingredient(self, ingredient_id: str, updates: dict) -> bool:
        """Update ingredient by ID"""
        ingredient = await self.get_ingredient_by_id(ingredient_id)
        if ingredient:
            for key, value in updates.items():
                if hasattr(ingredient, key):
                    setattr(ingredient, key, value)
            await self._save_ingredients()
            logger.info(f"Updated ingredient: {ingredient.name}")
            return True
        return False

