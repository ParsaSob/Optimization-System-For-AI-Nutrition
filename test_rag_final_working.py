#!/usr/bin/env python3
"""
Working RAG test client
"""

import subprocess
import json

def test_rag_working():
    """Test RAG endpoint with working client"""
    try:
        print("🚀 Testing RAG-based Meal Optimization")
        print("=" * 50)
        
        # Test data
        test_data = {
            "rag_response": {
                "suggestions": [
                    {
                        "ingredients": [
                            {
                                "name": "Ground Beef",
                                "amount": 200,
                                "calories": 400,
                                "protein": 40,
                                "carbs": 0,
                                "fat": 30
                            }
                        ]
                    }
                ]
            },
            "target_macros": {
                "calories": 2000.0,
                "protein": 150.0,
                "carbohydrates": 200.0,
                "fat": 65.0
            },
            "user_preferences": {
                "dietary_restrictions": [],
                "allergies": [],
                "preferred_cuisines": ["persian"],
                "calorie_preference": "moderate",
                "protein_preference": "high",
                "carb_preference": "moderate",
                "fat_preference": "moderate"
            },
            "user_id": "test_user_final"
        }
        
        print("📝 Testing RAG meal optimization...")
        
        # Convert to JSON string
        json_data = json.dumps(test_data)
        
        # Test with PowerShell
        cmd = [
            "powershell", "-Command",
            f"Invoke-WebRequest -Uri 'http://localhost:8000/optimize-rag-meal' -Method POST -Body '{json_data}' -ContentType 'application/json'"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ RAG optimization successful!")
            
            # Parse response
            response_text = result.stdout
            if '"StatusCode" : 200' in response_text:
                print("Status: 200 OK")
                
                # Extract content
                if '"Content" :' in response_text:
                    content_start = response_text.find('"Content" :') + 12
                    content_end = response_text.find('"RawContent" :')
                    if content_end > content_start:
                        content = response_text[content_start:content_end].strip()
                        
                        # Parse JSON
                        try:
                            response_data = json.loads(content)
                            print(f"✅ Parsed JSON successfully!")
                            
                            # Display results
                            optimization_result = response_data.get('optimization_result', {})
                            print(f"Optimization method: {optimization_result.get('optimization_method', 'N/A')}")
                            print(f"Target achieved: {optimization_result.get('target_achieved', 'N/A')}")
                            
                            # Show meal plans
                            meal_plans = response_data.get('meal_plans', [])
                            print(f"\n📋 Generated {len(meal_plans)} meal plans:")
                            
                            for i, meal_plan in enumerate(meal_plans[:3]):  # Show first 3
                                meal_time = meal_plan.get('meal_time', 'Unknown')
                                total_calories = meal_plan.get('total_calories', 0)
                                total_protein = meal_plan.get('total_protein', 0)
                                
                                print(f"  {i+1}. {meal_time}: {total_calories:.1f} cal, {total_protein:.1f}g protein")
                            
                            # Show daily totals
                            daily_totals = response_data.get('daily_totals', {})
                            if daily_totals:
                                print(f"\n📊 Daily Totals:")
                                print(f"   Calories: {daily_totals.get('calories', 0):.1f}")
                                print(f"   Protein: {daily_totals.get('protein', 0):.1f}g")
                                print(f"   Carbs: {daily_totals.get('carbohydrates', 0):.1f}g")
                                print(f"   Fat: {daily_totals.get('fat', 0):.1f}g")
                            
                            # Show RAG enhancement info
                            if 'rag_enhancement' in response_data:
                                enhancement = response_data['rag_enhancement']
                                print(f"\n🔧 RAG Enhancement:")
                                print(f"   Added ingredients: {len(enhancement.get('added_ingredients', []))}")
                                print(f"   Notes: {enhancement.get('enhancement_notes', 'N/A')}")
                            
                            # Show recommendations
                            recommendations = response_data.get('recommendations', [])
                            if recommendations:
                                print(f"\n💡 Recommendations:")
                                for rec in recommendations[:3]:  # Show first 3
                                    print(f"   • {rec}")
                            
                            # Show shopping list
                            shopping_list = response_data.get('shopping_list', [])
                            if shopping_list:
                                print(f"\n🛒 Shopping List:")
                                for item in shopping_list[:5]:  # Show first 5
                                    name = item.get('name', 'Unknown')
                                    quantity = item.get('quantity', 0)
                                    unit = item.get('unit', 'g')
                                    print(f"   • {name}: {quantity:.1f} {unit}")
                            
                        except json.JSONDecodeError as e:
                            print(f"JSON parse error: {e}")
                            print(f"Raw content: {content[:500]}...")
                    else:
                        print("No content found in response")
                else:
                    print("No content found in response")
            else:
                print(f"❌ Request failed: {result.stdout}")
                
        else:
            print(f"❌ Request failed with return code: {result.returncode}")
            print(f"Error: {result.stderr}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_working()
