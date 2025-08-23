import requests
import json
from models import MealRequest, NutritionalTarget, UserPreferences, Ingredient, MealTime

def test_meal_optimization():
    """Test the meal optimization API"""
    
    # API endpoint
    base_url = "http://localhost:8000"
    
    # Test ingredients
    test_ingredients = [
        Ingredient(
            name="Chicken Breast",
            name_fa="سینه مرغ",
            calories_per_100g=165,
            protein_per_100g=31,
            carbs_per_100g=0,
            fat_per_100g=3.6,
            category="protein",
            suitable_meals=[MealTime.BREAKFAST, MealTime.LUNCH, MealTime.DINNER]
        ),
        Ingredient(
            name="Brown Rice",
            name_fa="برنج قهوه‌ای",
            calories_per_100g=111,
            protein_per_100g=2.6,
            carbs_per_100g=23,
            fat_per_100g=0.9,
            category="grain",
            suitable_meals=[MealTime.LUNCH, MealTime.DINNER]
        ),
        Ingredient(
            name="Spinach",
            name_fa="اسفناج",
            calories_per_100g=23,
            protein_per_100g=2.9,
            carbs_per_100g=3.6,
            fat_per_100g=0.4,
            category="vegetable",
            suitable_meals=[MealTime.LUNCH, MealTime.DINNER]
        ),
        Ingredient(
            name="Eggs",
            name_fa="تخم مرغ",
            calories_per_100g=155,
            protein_per_100g=13,
            carbs_per_100g=1.1,
            fat_per_100g=11,
            category="protein",
            suitable_meals=[MealTime.BREAKFAST, MealTime.LUNCH, MealTime.DINNER]
        ),
        Ingredient(
            name="Banana",
            name_fa="موز",
            calories_per_100g=89,
            protein_per_100g=1.1,
            carbs_per_100g=23,
            fat_per_100g=0.3,
            category="fruit",
            suitable_meals=[MealTime.BREAKFAST, MealTime.MORNING_SNACK, MealTime.AFTERNOON_SNACK]
        )
    ]
    
    # Target macros
    target_macros = NutritionalTarget(
        calories=2000,
        protein=150,
        carbohydrates=200,
        fat=65
    )
    
    # User preferences
    user_preferences = UserPreferences(
        dietary_restrictions=["vegetarian"],
        allergies=["nuts"],
        preferred_cuisines=["mediterranean", "persian"],
        cooking_time_preference="medium",
        budget_constraint=50.0
    )
    
    # Create meal request
    meal_request = MealRequest(
        user_id="test_user_001",
        ingredients=test_ingredients,
        target_macros=target_macros,
        user_preferences=user_preferences,
        meal_times=list(MealTime),
        optimization_priority="balanced"
    )
    
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        health_response = requests.get(f"{base_url}/health")
        print(f"Health status: {health_response.status_code}")
        print(f"Health response: {health_response.json()}")
        print()
        
        # Test meal optimization
        print("Testing meal optimization...")
        optimization_response = requests.post(
            f"{base_url}/optimize-meal",
            json=meal_request.model_dump()
        )
        
        if optimization_response.status_code == 200:
            result = optimization_response.json()
            print("✅ Meal optimization successful!")
            print(f"Optimization method: {result['optimization_result']['optimization_method']}")
            print(f"Target achieved: {result['optimization_result']['target_achieved']}")
            print(f"Computation time: {result['optimization_result']['computation_time']:.2f} seconds")
            print()
            
            # Display meal plans
            print("📋 Meal Plans:")
            for meal_plan in result['meal_plans']:
                print(f"\n🍽️ {meal_plan['meal_time'].replace('_', ' ').title()}:")
                print(f"   Calories: {meal_plan['total_calories']:.1f}")
                print(f"   Protein: {meal_plan['total_protein']:.1f}g")
                print(f"   Carbs: {meal_plan['total_carbs']:.1f}g")
                print(f"   Fat: {meal_plan['total_fat']:.1f}g")
                
                if meal_plan['items']:
                    print("   Ingredients:")
                    for item in meal_plan['items']:
                        print(f"     • {item['ingredient']['name']}: {item['quantity_grams']:.1f}g")
            
            print(f"\n📊 Daily Totals:")
            daily = result['daily_totals']
            print(f"   Calories: {daily['calories']:.1f} / {target_macros.calories}")
            print(f"   Protein: {daily['protein']:.1f}g / {target_macros.protein}g")
            print(f"   Carbs: {daily['carbohydrates']:.1f}g / {target_macros.carbohydrates}g")
            print(f"   Fat: {daily['fat']:.1f}g / {target_macros.fat}g")
            
            if result['recommendations']:
                print(f"\n💡 Recommendations:")
                for rec in result['recommendations']:
                    print(f"   • {rec}")
            
            if result['shopping_list']:
                print(f"\n🛒 Shopping List:")
                for item in result['shopping_list']:
                    print(f"   • {item['name']}: {item['quantity']:.1f}g")
            
        else:
            print(f"❌ Meal optimization failed: {optimization_response.status_code}")
            print(f"Error: {optimization_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_ingredients_endpoint():
    """Test the ingredients endpoint"""
    base_url = "http://localhost:8000"
    
    try:
        print("Testing ingredients endpoint...")
        response = requests.get(f"{base_url}/ingredients")
        
        if response.status_code == 200:
            ingredients = response.json()['ingredients']
            print(f"✅ Retrieved {len(ingredients)} ingredients")
            
            # Display first few ingredients
            print("\n📝 Sample Ingredients:")
            for i, ingredient in enumerate(ingredients[:5]):
                print(f"   {i+1}. {ingredient['name']} ({ingredient['name_fa']})")
                print(f"      Category: {ingredient['category']}")
                print(f"      Protein: {ingredient['protein_per_100g']}g/100g")
                print(f"      Carbs: {ingredient['carbs_per_100g']}g/100g")
                print(f"      Fat: {ingredient['fat_per_100g']}g/100g")
                print()
        else:
            print(f"❌ Failed to get ingredients: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Meal Optimization API")
    print("=" * 50)
    
    # Test ingredients endpoint
    test_ingredients_endpoint()
    print()
    
    # Test meal optimization
    test_meal_optimization()

