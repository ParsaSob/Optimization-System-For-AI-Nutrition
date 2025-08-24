# Single Meal RAG Optimization API

## Overview

The Single Meal RAG Optimization API endpoint (`/optimize-single-meal-rag`) provides advanced mathematical optimization for single meal planning based on RAG (Retrieval-Augmented Generation) responses and target nutritional macros. This endpoint uses multiple optimization algorithms including linear programming, differential evolution, genetic algorithms, and machine learning techniques to enhance RAG suggestions and meet specific nutritional targets.

## Endpoint

```
POST /optimize-single-meal-rag
```

## Request Structure

### Request Body

```json
{
  "rag_response": {
    "suggestions": [
      {
        "ingredients": [
          {
            "name": "Ground Beef",
            "amount": 200,
            "unit": "g",
            "calories": 250,
            "protein": 25,
            "carbs": 0,
            "fat": 15
          }
        ]
      }
    ]
  },
  "target_macros": {
    "calories": 825,
    "protein": 46.5,
    "carbohydrates": 41.0,
    "fat": 56.0
  },
  "user_preferences": {
    "dietary_restrictions": [],
    "allergies": [],
    "preferred_cuisines": ["persian", "mediterranean"],
    "cooking_time_preference": "medium",
    "budget_constraint": 15.0
  },
  "meal_type": "lunch"
}
```

### Field Descriptions

#### rag_response
- **suggestions**: Array of meal suggestions from RAG system
  - **ingredients**: Array of ingredients with nutritional data
    - **name**: Ingredient name (string)
    - **amount**: Amount in grams (float)
    - **unit**: Unit of measurement (string)
    - **calories**: Calories for the specified amount (float)
    - **protein**: Protein in grams for the specified amount (float)
    - **carbs**: Carbohydrates in grams for the specified amount (float)
    - **fat**: Fat in grams for the specified amount (float)

#### target_macros
- **calories**: Target calories for the meal (float)
- **protein**: Target protein in grams (float)
- **carbohydrates**: Target carbohydrates in grams (float)
- **fat**: Target fat in grams (float)

#### user_preferences
- **dietary_restrictions**: Array of dietary restrictions (e.g., ["vegetarian", "vegan"])
- **allergies**: Array of food allergies (e.g., ["nuts", "shellfish"])
- **preferred_cuisines**: Array of preferred cuisines (e.g., ["persian", "mediterranean"])
- **cooking_time_preference**: Preferred cooking time ("quick", "medium", "elaborate")
- **budget_constraint**: Daily budget constraint in currency (optional)

#### meal_type
- **meal_type**: Type of meal (string, e.g., "breakfast", "lunch", "dinner", "snack")

## Response Structure

### Success Response (200)

```json
{
  "optimization_result": {
    "success": true,
    "method": "Linear Programming (PuLP)",
    "computation_time": 0.5,
    "target_achieved": true
  },
  "meal": {
    "meal_time": "lunch",
    "total_calories": 825.0,
    "total_protein": 46.5,
    "total_carbs": 41.0,
    "total_fat": 56.0,
    "items": [
      {
        "ingredient": "Ground Beef",
        "quantity_grams": 200.0,
        "calories": 250.0,
        "protein": 25.0,
        "carbs": 0.0,
        "fat": 15.0
      },
      {
        "ingredient": "Brown Rice",
        "quantity_grams": 150.0,
        "calories": 150.0,
        "protein": 3.0,
        "carbs": 30.0,
        "fat": 1.0
      }
    ]
  },
  "target_achievement": {
    "calories_achieved": true,
    "protein_achieved": true,
    "carbs_achieved": true,
    "fat_achieved": true
  },
  "rag_enhancement": {
    "enhancement_method": "Mathematical optimization to meet targets",
    "original_ingredients": 3,
    "supplements_added": 2,
    "total_ingredients": 5,
    "enhancement_ratio": 0.67
  }
}
```

### Error Response (400/500)

```json
{
  "error": "Error description",
  "status": "error"
}
```

## Response Field Descriptions

### optimization_result
- **success**: Whether optimization was successful (boolean)
- **method**: Optimization method used (string)
- **computation_time**: Time taken for optimization in seconds (float)
- **target_achieved**: Whether target macros were achieved (boolean)

### meal
- **meal_time**: Type of meal (string)
- **total_calories**: Total calories in the meal (float)
- **total_protein**: Total protein in grams (float)
- **total_carbs**: Total carbohydrates in grams (float)
- **total_fat**: Total fat in grams (float)
- **items**: Array of meal items with quantities and nutritional values

### target_achievement
- **calories_achieved**: Whether calorie target was achieved (boolean)
- **protein_achieved**: Whether protein target was achieved (boolean)
- **carbs_achieved**: Whether carbohydrate target was achieved (boolean)
- **fat_achieved**: Whether fat target was achieved (boolean)

### rag_enhancement
- **enhancement_method**: Description of enhancement method (string)
- **original_ingredients**: Number of original RAG ingredients (integer)
- **supplements_added**: Number of supplementary ingredients added (integer)
- **total_ingredients**: Total number of ingredients in final meal (integer)
- **enhancement_ratio**: Ratio of supplements to original ingredients (float)

## Optimization Algorithms

The API uses multiple optimization techniques to ensure the best possible solution:

### 1. Linear Programming (PuLP)
- **Purpose**: Primary optimization method using mathematical programming
- **Advantages**: Guaranteed optimal solution, fast for small problems
- **Use Case**: Standard meal optimization scenarios

### 2. Differential Evolution (SciPy)
- **Purpose**: Global optimization for complex nutritional constraints
- **Advantages**: Handles non-linear constraints, robust
- **Use Case**: Complex macro balancing scenarios

### 3. Genetic Algorithm (DEAP)
- **Purpose**: Evolutionary optimization for ingredient selection
- **Advantages**: Can handle discrete choices, good for large ingredient sets
- **Use Case**: Large ingredient databases with complex preferences

### 4. Hybrid Approach
- **Purpose**: Combines multiple methods for best results
- **Advantages**: Fallback strategies, robust optimization
- **Use Case**: When primary methods fail

## Target Achievement Tolerance

The API uses a ±10% tolerance for target achievement:
- **Calories**: ±10% of target
- **Protein**: ±10% of target  
- **Carbohydrates**: ±10% of target
- **Fat**: ±10% of target

## Error Handling

### Common Error Scenarios

1. **Missing Required Fields**: Returns 400 with specific field name
2. **Invalid Nutritional Data**: Returns 400 with validation error
3. **Optimization Failure**: Returns 500 with fallback method details
4. **Server Errors**: Returns 500 with error description

### Fallback Strategies

When primary optimization methods fail, the API automatically falls back to:
1. **Simpler optimization methods**
2. **Scaling-based approaches**
3. **Basic ingredient supplementation**

## Usage Examples

### Python Example

```python
import requests
import json

# API endpoint
url = "http://localhost:5000/optimize-single-meal-rag"

# Request data
data = {
    "rag_response": {
        "suggestions": [
            {
                "ingredients": [
                    {
                        "name": "Chicken Breast",
                        "amount": 150,
                        "unit": "g",
                        "calories": 165,
                        "protein": 31,
                        "carbs": 0,
                        "fat": 3.6
                    }
                ]
            }
        ]
    },
    "target_macros": {
        "calories": 600,
        "protein": 80,
        "carbohydrates": 50,
        "fat": 20
    },
    "user_preferences": {
        "dietary_restrictions": [],
        "allergies": [],
        "preferred_cuisines": ["persian"]
    },
    "meal_type": "dinner"
}

# Make request
response = requests.post(url, json=data)
result = response.json()

# Process results
if response.status_code == 200:
    print(f"Optimization successful using {result['optimization_result']['method']}")
    print(f"Target achieved: {result['optimization_result']['target_achieved']}")
    print(f"Total calories: {result['meal']['total_calories']}")
else:
    print(f"Error: {result['error']}")
```

### cURL Example

```bash
curl -X POST http://localhost:5000/optimize-single-meal-rag \
  -H "Content-Type: application/json" \
  -d '{
    "rag_response": {
      "suggestions": [
        {
          "ingredients": [
            {
              "name": "Ground Beef",
              "amount": 200,
              "unit": "g",
              "calories": 250,
              "protein": 25,
              "carbs": 0,
              "fat": 15
            }
          ]
        }
      ]
    },
    "target_macros": {
      "calories": 825,
      "protein": 46.5,
      "carbohydrates": 41.0,
      "fat": 56.0
    },
    "user_preferences": {
      "dietary_restrictions": [],
      "allergies": [],
      "preferred_cuisines": ["persian"]
    },
    "meal_type": "lunch"
  }'
```

## Performance Characteristics

### Computation Time
- **Simple cases**: 0.1-0.5 seconds
- **Complex cases**: 0.5-2.0 seconds
- **Edge cases**: 2.0-5.0 seconds

### Scalability
- **Small meals (1-5 ingredients)**: < 1 second
- **Medium meals (6-15 ingredients)**: 1-3 seconds
- **Large meals (16+ ingredients)**: 3-10 seconds

## Best Practices

### Request Optimization
1. **Provide accurate nutritional data** for RAG ingredients
2. **Set realistic target macros** within achievable ranges
3. **Include specific dietary restrictions** to improve results
4. **Use appropriate meal types** for better ingredient selection

### Response Handling
1. **Check target_achieved** before using results
2. **Monitor computation_time** for performance insights
3. **Review rag_enhancement** to understand changes made
4. **Handle errors gracefully** with fallback strategies

## Testing

Use the provided test script to verify API functionality:

```bash
python test_single_meal_rag.py
```

The test script covers:
- Basic functionality testing
- Edge case scenarios
- Error handling
- Performance benchmarking

## Dependencies

The API requires the following Python packages:
- `flask`: Web framework
- `pulp`: Linear programming optimization
- `scipy`: Scientific computing and optimization
- `deap`: Genetic algorithm implementation
- `numpy`: Numerical computing
- `scikit-learn`: Machine learning algorithms

## Support

For technical support or questions about the API:
1. Check the server logs for detailed error information
2. Verify request format matches the expected structure
3. Ensure all required fields are provided
4. Test with simple cases before complex scenarios
