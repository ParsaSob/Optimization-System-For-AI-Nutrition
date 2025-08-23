# Meal Optimization API Documentation

## Overview
The Meal Optimization API is a sophisticated system that uses advanced mathematical optimization techniques to create personalized meal plans. It supports 6 meal times and uses multiple optimization algorithms to achieve target nutritional goals.

## Features
- **6 Meal Times**: Breakfast, Morning Snack, Lunch, Afternoon Snack, Evening Snack, Dinner
- **Advanced Optimization**: Linear Programming, Genetic Algorithms, Differential Evolution
- **Personalization**: Dietary restrictions, allergies, preferences
- **Bilingual Support**: English and Persian ingredient names
- **Cost Optimization**: Budget constraints and shopping lists

## API Endpoints

### 1. Health Check
```
GET /health
```
Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "message": "Meal Optimization API is running"
}
```

### 2. Meal Optimization
```
POST /optimize-meal
```
Main endpoint for meal optimization.

**Request Body:**
```json
{
  "user_id": "user_123",
  "ingredients": [
    {
      "name": "Chicken Breast",
      "name_fa": "سینه مرغ",
      "calories_per_100g": 165,
      "protein_per_100g": 31,
      "carbs_per_100g": 0,
      "fat_per_100g": 3.6,
      "category": "protein",
      "suitable_meals": ["breakfast", "lunch", "dinner"]
    }
  ],
  "target_macros": {
    "calories": 2000,
    "protein": 150,
    "carbohydrates": 200,
    "fat": 65
  },
  "user_preferences": {
    "dietary_restrictions": ["vegetarian"],
    "allergies": ["nuts"],
    "preferred_cuisines": ["mediterranean"],
    "cooking_time_preference": "medium",
    "budget_constraint": 50.0
  },
  "meal_times": ["breakfast", "lunch", "dinner"],
  "optimization_priority": "balanced"
}
```

**Response:**
```json
{
  "user_id": "user_123",
  "optimization_result": {
    "success": true,
    "target_achieved": true,
    "optimization_method": "linear_programming",
    "objective_value": 0.95,
    "constraints_violated": [],
    "computation_time": 2.34
  },
  "meal_plans": [
    {
      "meal_time": "breakfast",
      "items": [
        {
          "ingredient": {
            "name": "Eggs",
            "name_fa": "تخم مرغ"
          },
          "quantity_grams": 100,
          "calories": 155,
          "protein": 13,
          "carbs": 1.1,
          "fat": 11
        }
      ],
      "total_calories": 155,
      "total_protein": 13,
      "total_carbs": 1.1,
      "total_fat": 11
    }
  ],
  "daily_totals": {
    "calories": 2000,
    "protein": 150,
    "carbohydrates": 200,
    "fat": 65
  },
  "recommendations": [
    "Consider adding more fiber-rich foods"
  ],
  "cost_estimate": 25.50,
  "shopping_list": [
    {
      "name": "Chicken Breast",
      "quantity": 200,
      "unit": "grams"
    }
  ]
}
```

### 3. Get Ingredients
```
GET /ingredients
```
Returns all available ingredients in the database.

**Response:**
```json
{
  "ingredients": [
    {
      "id": "ing_1",
      "name": "Chicken Breast",
      "name_fa": "سینه مرغ",
      "calories_per_100g": 165,
      "protein_per_100g": 31,
      "carbs_per_100g": 0,
      "fat_per_100g": 3.6,
      "category": "protein",
      "suitable_meals": ["breakfast", "lunch", "dinner"],
      "price_per_kg": 15.0
    }
  ]
}
```

### 4. Add Ingredients
```
POST /add-ingredients
```
Add new ingredients to the database.

**Request Body:**
```json
[
  {
    "name": "New Ingredient",
    "name_fa": "ماده غذایی جدید",
    "calories_per_100g": 100,
    "protein_per_100g": 10,
    "carbs_per_100g": 15,
    "fat_per_100g": 5,
    "category": "protein",
    "suitable_meals": ["lunch", "dinner"]
  }
]
```

### 5. Get Meal Times
```
GET /meal-times
```
Returns available meal times.

**Response:**
```json
{
  "meal_times": [
    "breakfast",
    "morning_snack",
    "lunch",
    "afternoon_snack",
    "evening_snack",
    "dinner"
  ]
}
```

## Optimization Methods

### 1. Linear Programming (PuLP)
- **Best for**: Small to medium problems, exact solutions
- **Advantages**: Guaranteed optimal solution, fast for small problems
- **Use case**: When you need the mathematically optimal solution

### 2. Genetic Algorithm (DEAP)
- **Best for**: Complex, multi-objective problems
- **Advantages**: Can handle non-linear constraints, good for exploration
- **Use case**: When the problem is complex or has multiple conflicting objectives

### 3. Differential Evolution (SciPy)
- **Best for**: Continuous optimization problems
- **Advantages**: Robust, good for noisy objective functions
- **Use case**: When you need a robust solution for complex landscapes

### 4. Hybrid Approach
- **Best for**: General use cases
- **Advantages**: Combines strengths of multiple methods
- **Use case**: Default approach that tries multiple methods

## Data Models

### Ingredient
```python
class Ingredient(BaseModel):
    id: Optional[str]
    name: str                    # English name
    name_fa: Optional[str]       # Persian name
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    fiber_per_100g: Optional[float]
    sugar_per_100g: Optional[float]
    sodium_per_100g: Optional[float]
    category: str                # protein, vegetable, grain, etc.
    suitable_meals: List[MealTime]
    price_per_kg: Optional[float]
    availability: bool
```

### NutritionalTarget
```python
class NutritionalTarget(BaseModel):
    calories: float
    protein: float
    carbohydrates: float
    fat: float
    fiber: Optional[float]
    sugar: Optional[float]
    sodium: Optional[float]
```

### UserPreferences
```python
class UserPreferences(BaseModel):
    dietary_restrictions: List[str]    # vegetarian, vegan, gluten-free
    allergies: List[str]               # nuts, dairy, etc.
    preferred_cuisines: List[str]      # mediterranean, persian, etc.
    cooking_time_preference: str       # quick, medium, elaborate
    budget_constraint: Optional[float] # daily budget
    taste_preferences: Dict[str, float] # preference scores
```

## Usage Examples

### Python Client
```python
import requests

# Optimize meal plan
response = requests.post(
    "http://localhost:8000/optimize-meal",
    json={
        "user_id": "user_123",
        "ingredients": [...],  # Your ingredients
        "target_macros": {
            "calories": 2000,
            "protein": 150,
            "carbohydrates": 200,
            "fat": 65
        },
        "user_preferences": {
            "dietary_restrictions": ["vegetarian"],
            "allergies": []
        }
    }
)

result = response.json()
print(f"Optimization method: {result['optimization_result']['optimization_method']}")
```

### JavaScript/Node.js Client
```javascript
const axios = require('axios');

const response = await axios.post('http://localhost:8000/optimize-meal', {
  user_id: 'user_123',
  ingredients: [...], // Your ingredients
  target_macros: {
    calories: 2000,
    protein: 150,
    carbohydrates: 200,
    fat: 65
  },
  user_preferences: {
    dietary_restrictions: ['vegetarian'],
    allergies: []
  }
});

console.log(`Optimization method: ${response.data.optimization_result.optimization_method}`);
```

## Error Handling

The API returns appropriate HTTP status codes:

- **200**: Success
- **400**: Bad Request (invalid input)
- **500**: Internal Server Error (optimization failed)

Error responses include details about what went wrong:

```json
{
  "detail": "Optimization failed: All optimization methods failed"
}
```

## Performance Considerations

- **Small problems** (< 50 ingredients): Linear programming, typically < 1 second
- **Medium problems** (50-200 ingredients): Genetic algorithm, typically 5-30 seconds
- **Large problems** (> 200 ingredients): Differential evolution, typically 30-120 seconds

## Configuration

The system can be configured through environment variables or the `config.py` file:

- `OPTIMIZATION_TIMEOUT`: Maximum time for optimization (default: 300 seconds)
- `GA_POPULATION_SIZE`: Genetic algorithm population size (default: 50)
- `GA_GENERATIONS`: Number of generations (default: 30)
- `DE_MAX_ITERATIONS`: Differential evolution iterations (default: 100)

## Best Practices

1. **Ingredient Quality**: Provide accurate nutritional data for best results
2. **Target Macros**: Set realistic targets based on individual needs
3. **User Preferences**: Include relevant dietary restrictions and allergies
4. **Meal Times**: Specify only the meal times you want to optimize
5. **Error Handling**: Always check the response status and handle errors gracefully

## Support

For questions or issues:
1. Check the logs for detailed error information
2. Verify your input data format
3. Ensure all required fields are provided
4. Check that the server is running and accessible

