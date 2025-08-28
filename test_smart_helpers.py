#!/usr/bin/env python3
"""
Test script for the new smart helper ingredient logic
Tests conflict prevention, meal-specific selection, and realistic quantities
"""

import requests
import json
import time

def test_smart_helpers():
    """Test the smart helper ingredient logic"""
    
    # Test different scenarios
    test_scenarios = [
        {
            "name": "Beef Lunch - Should avoid chicken",
            "rag_response": "یک وعده غذایی ناهار با گوشت گاو",
            "target_macros": {"calories": 800, "protein": 50, "carbs": 80, "fat": 25},
            "user_preferences": "گوشت مجاز است",
            "meal_type": "lunch"
        },
        {
            "name": "Breakfast - Should use dairy/eggs",
            "rag_response": "صبحانه سالم",
            "target_macros": {"calories": 600, "protein": 30, "carbs": 70, "fat": 20},
            "user_preferences": "گیاهی نیست",
            "meal_type": "breakfast"
        },
        {
            "name": "Evening Snack - Should use light options",
            "rag_response": "میان وعده عصر",
            "target_macros": {"calories": 200, "protein": 15, "carbs": 25, "fat": 8},
            "user_preferences": "سبک باشد",
            "meal_type": "evening_snack"
        },
        {
            "name": "Fish Dinner - Should avoid more fish",
            "rag_response": "شام با ماهی سالمون",
            "target_macros": {"calories": 700, "protein": 45, "carbs": 60, "fat": 30},
            "user_preferences": "ماهی مجاز است",
            "meal_type": "dinner"
        }
    ]
    
    print("🧠 Testing Smart Helper Ingredient Logic...")
    print("=" * 80)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🔬 Test {i}: {scenario['name']}")
        print("-" * 60)
        
        try:
            # Send request to the main optimization endpoint
            print(f"🌐 Testing {scenario['meal_type']} meal...")
            
            response = requests.post(
                "http://localhost:5000/optimize-single-meal-rag-advanced",
                json=scenario,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Optimization completed.")
                
                # Print helper ingredients added
                helper_ingredients = result.get('helper_ingredients_added', [])
                if helper_ingredients:
                    print(f"\n🔧 Helper Ingredients Added:")
                    for helper in helper_ingredients:
                        print(f"  • {helper['name']}: {helper['protein_per_100g']}g protein, {helper['carbs_per_100g']}g carbs, {helper['fat_per_100g']}g fat")
                    
                    # Analyze protein sources for conflicts
                    analyze_helper_conflicts(scenario, helper_ingredients)
                else:
                    print(f"\n🔧 No helper ingredients were added")
                
                # Print optimization steps
                optimization_steps = result.get('optimization_steps', {})
                if optimization_steps:
                    print(f"\n🔄 Optimization Steps:")
                    for step, description in optimization_steps.items():
                        print(f"  • {step}: {description}")
                
                # Print final nutrition
                final_nutrition = result.get('final_nutrition', {})
                if final_nutrition:
                    print(f"\n📊 Final Nutrition:")
                    print(f"  • Calories: {final_nutrition['calories']:.1f} kcal")
                    print(f"  • Protein: {final_nutrition['protein']:.1f} g")
                    print(f"  • Carbs: {final_nutrition['carbs']:.1f} g")
                    print(f"  • Fat: {final_nutrition['fat']:.1f} g")
                
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
        
        print("-" * 60)
    
    print("\n" + "=" * 80)
    print("🏁 All tests completed!")

def analyze_helper_conflicts(scenario, helper_ingredients):
    """Analyze helper ingredients for potential conflicts"""
    print(f"\n🔍 Conflict Analysis:")
    
    # Check for protein source conflicts
    protein_sources = {
        'red_meat': ['beef', 'lamb', 'pork', 'steak', 'burger'],
        'white_meat': ['chicken', 'turkey', 'duck'],
        'fish': ['salmon', 'tuna', 'cod', 'fish', 'seafood'],
        'plant_based': ['tofu', 'tempeh', 'bean', 'lentil', 'chickpea'],
        'dairy_eggs': ['egg', 'yogurt', 'cheese', 'milk']
    }
    
    # Analyze scenario description
    scenario_desc = scenario['rag_response'].lower()
    scenario_proteins = []
    
    for source_type, keywords in protein_sources.items():
        if any(keyword in scenario_desc for keyword in keywords):
            scenario_proteins.append(source_type)
    
    if scenario_proteins:
        print(f"  📝 Scenario contains: {', '.join(scenario_proteins)}")
    
    # Analyze helper ingredients
    helper_proteins = []
    for helper in helper_ingredients:
        name = helper['name'].lower()
        for source_type, keywords in protein_sources.items():
            if any(keyword in name for keyword in keywords):
                helper_proteins.append(source_type)
                break
    
    if helper_proteins:
        print(f"  🔧 Helpers contain: {', '.join(helper_proteins)}")
        
        # Check for conflicts
        conflicts = set(scenario_proteins) & set(helper_proteins)
        if conflicts:
            print(f"  ⚠️  CONFLICT DETECTED: {', '.join(conflicts)}")
        else:
            print(f"  ✅ No conflicts detected")
    else:
        print(f"  🔧 No protein helpers added")

if __name__ == "__main__":
    print("🧠 Smart Helper Ingredient Logic Test Script")
    print("=" * 80)
    
    # Wait a bit for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Run the tests
    test_smart_helpers()
    
    print("\n" + "=" * 80)
    print("�� Test completed!")
