from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union, Any
from enum import Enum

class MealTime(str, Enum):
    """Meal time enumeration"""
    BREAKFAST = "breakfast"
    MORNING_SNACK = "morning_snack"
    LUNCH = "lunch"
    AFTERNOON_SNACK = "afternoon_snack"
    EVENING_SNACK = "evening_snack"
    DINNER = "dinner"

class NutritionalTarget(BaseModel):
    """Nutritional target macros"""
    calories: float = Field(..., description="Target calories per day")
    protein: float = Field(..., description="Target protein in grams")
    carbohydrates: float = Field(..., description="Target carbohydrates in grams")
    fat: float = Field(..., description="Target fat in grams")
    fiber: Optional[float] = Field(None, description="Target fiber in grams")
    sugar: Optional[float] = Field(None, description="Target sugar in grams")
    sodium: Optional[float] = Field(None, description="Target sodium in mg")

class Ingredient(BaseModel):
    """Ingredient with nutritional information"""
    id: Optional[str] = Field(None, description="Unique ingredient ID")
    name: str = Field(..., description="Ingredient name")
    name_fa: Optional[str] = Field(None, description="Persian name")
    calories_per_100g: float = Field(..., description="Calories per 100g")
    protein_per_100g: float = Field(..., description="Protein per 100g")
    carbs_per_100g: float = Field(..., description="Carbohydrates per 100g")
    fat_per_100g: float = Field(..., description="Fat per 100g")
    fiber_per_100g: Optional[float] = Field(None, description="Fiber per 100g")
    sugar_per_100g: Optional[float] = Field(None, description="Sugar per 100g")
    sodium_per_100g: Optional[float] = Field(None, description="Sodium per 100g")
    category: str = Field(..., description="Food category (e.g., protein, vegetable, grain)")
    suitable_meals: List[MealTime] = Field(..., description="Suitable meal times")
    price_per_kg: Optional[float] = Field(None, description="Price per kilogram")
    availability: bool = Field(True, description="Ingredient availability")

class MealItem(BaseModel):
    """Individual meal item with quantity"""
    ingredient: Ingredient
    quantity_grams: float = Field(..., description="Quantity in grams")
    calories: float = Field(..., description="Calculated calories")
    protein: float = Field(..., description="Calculated protein")
    carbs: float = Field(..., description="Calculated carbohydrates")
    fat: float = Field(..., description="Calculated fat")

class MealPlan(BaseModel):
    """Complete meal plan for a specific meal time"""
    meal_time: MealTime
    items: List[MealItem]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    total_fiber: Optional[float] = None
    total_sugar: Optional[float] = None
    total_sodium: Optional[float] = None

class UserPreferences(BaseModel):
    """User dietary preferences and restrictions"""
    dietary_restrictions: List[str] = Field(default_factory=list, description="e.g., vegetarian, vegan, gluten-free")
    allergies: List[str] = Field(default_factory=list, description="Food allergies")
    preferred_cuisines: List[str] = Field(default_factory=list, description="Preferred cuisines")
    cooking_time_preference: str = Field("medium", description="quick, medium, elaborate")
    budget_constraint: Optional[float] = Field(None, description="Daily budget in currency")
    taste_preferences: Dict[str, float] = Field(default_factory=dict, description="Taste preference scores")

class MealRequest(BaseModel):
    """Request for meal optimization"""
    user_id: str = Field(..., description="Unique user identifier")
    ingredients: List[Ingredient] = Field(..., description="Available ingredients")
    target_macros: NutritionalTarget = Field(..., description="Target nutritional values")
    user_preferences: UserPreferences = Field(..., description="User preferences")
    meal_times: List[MealTime] = Field(default_factory=lambda: list(MealTime), description="Meal times to optimize")
    optimization_priority: str = Field("balanced", description="calories, protein, carbs, fat, balanced, cost")

class OptimizationResult(BaseModel):
    """Result of optimization process"""
    success: bool = Field(..., description="Whether optimization was successful")
    target_achieved: bool = Field(..., description="Whether target macros were achieved")
    optimization_method: str = Field(..., description="Method used for optimization")
    objective_value: float = Field(..., description="Objective function value")
    constraints_violated: List[str] = Field(default_factory=list, description="Violated constraints")
    computation_time: float = Field(..., description="Time taken for optimization")

class MealResponse(BaseModel):
    """Response containing optimized meal plan"""
    user_id: str
    optimization_result: OptimizationResult
    meal_plans: List[MealPlan]
    daily_totals: NutritionalTarget
    recommendations: List[str] = Field(..., description="Additional recommendations")
    cost_estimate: Optional[float] = Field(None, description="Estimated daily cost")
    shopping_list: List[Dict[str, Union[str, float]]] = Field(..., description="Shopping list with quantities")

class IngredientDatabase(BaseModel):
    """Database of available ingredients"""
    ingredients: List[Ingredient]
    last_updated: str
    version: str = "1.0.0"

class RAGIngredient(BaseModel):
    """Ingredient from RAG response with nutritional data"""
    name: str = Field(..., description="Ingredient name")
    amount: float = Field(..., description="Amount in grams")
    unit: str = Field(..., description="Unit of measurement")
    calories: float = Field(..., description="Calories for the amount")
    protein: float = Field(..., description="Protein in grams for the amount")
    carbs: float = Field(..., description="Carbohydrates in grams for the amount")
    fat: float = Field(..., description="Fat in grams for the amount")

class RAGSuggestion(BaseModel):
    """Suggestion from RAG response"""
    ingredients: List[RAGIngredient] = Field(..., description="List of ingredients")

class RAGResponse(BaseModel):
    """RAG response containing meal suggestions"""
    suggestions: List[RAGSuggestion] = Field(..., description="List of meal suggestions")

class SingleMealRequest(BaseModel):
    """Request for single meal optimization"""
    rag_response: RAGResponse = Field(..., description="RAG response with ingredients")
    target_macros: NutritionalTarget = Field(..., description="Target macros for the meal")
    user_preferences: UserPreferences = Field(..., description="User preferences")
    meal_type: str = Field(..., description="Type of meal (breakfast, lunch, dinner, etc.)")

class SingleMealItem(BaseModel):
    """Individual meal item with quantity and nutritional info"""
    ingredient: str = Field(..., description="Ingredient name")
    quantity_grams: float = Field(..., description="Quantity in grams")
    calories: float = Field(..., description="Calculated calories")
    protein: float = Field(..., description="Calculated protein")
    carbs: float = Field(..., description="Calculated carbohydrates")
    fat: float = Field(..., description="Calculated fat")

class SingleMealResponse(BaseModel):
    """Response for single meal optimization"""
    optimization_result: Dict[str, Any] = Field(..., description="Optimization result details")
    meal: Dict[str, Any] = Field(..., description="Optimized meal details")
    target_achievement: Dict[str, bool] = Field(..., description="Target achievement status")
    rag_enhancement: Dict[str, Any] = Field(..., description="RAG enhancement details")

