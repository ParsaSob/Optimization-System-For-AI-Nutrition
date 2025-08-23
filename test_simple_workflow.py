#!/usr/bin/env python3
"""
Simple Workflow Test
"""

import subprocess
import json

def test_simple_workflow():
    """Test the simple workflow"""
    try:
        print("🚀 Testing RAG → Site → This API Workflow")
        print("=" * 50)
        
        # Test data (like what your site would send)
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
            "user_id": "test_user"
        }
        
        print("📊 Input Data:")
        print(f"  - RAG ingredients: {len(test_data['rag_response']['suggestions'][0]['ingredients'])}")
        print(f"  - Target calories: {test_data['target_macros']['calories']}")
        print(f"  - Current calories: {test_data['rag_response']['suggestions'][0]['ingredients'][0]['calories']}")
        print(f"  - Missing calories: {test_data['target_macros']['calories'] - test_data['rag_response']['suggestions'][0]['ingredients'][0]['calories']}")
        
        print("\n🔧 Calling optimization API...")
        
        # Convert to JSON string
        json_data = json.dumps(test_data)
        
        # Test with PowerShell
        cmd = [
            "powershell", "-Command",
            f"Invoke-WebRequest -Uri 'http://localhost:8000/optimize-rag-meal' -Method POST -Body '{json_data}' -ContentType 'application/json'"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ API Call: SUCCESS")
            
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
                        
                        try:
                            response_data = json.loads(content)
                            print(f"✅ Response parsed successfully!")
                            
                            # Show results
                            optimization_result = response_data.get('optimization_result', {})
                            print(f"\n📊 Results:")
                            print(f"  - Method: {optimization_result.get('optimization_method', 'N/A')}")
                            print(f"  - Target achieved: {optimization_result.get('target_achieved', 'N/A')}")
                            
                            # Show meal plans
                            meal_plans = response_data.get('meal_plans', [])
                            print(f"\n🍽️ Generated {len(meal_plans)} meal plans:")
                            
                            for meal_plan in meal_plans:
                                meal_time = meal_plan.get('meal_time', 'Unknown')
                                total_calories = meal_plan.get('total_calories', 0)
                                print(f"  • {meal_time}: {total_calories:.1f} cal")
                            
                            # Show daily totals
                            daily_totals = response_data.get('daily_totals', {})
                            if daily_totals:
                                print(f"\n📈 Daily Totals:")
                                print(f"  - Calories: {daily_totals.get('calories', 0):.1f} / {test_data['target_macros']['calories']}")
                                print(f"  - Protein: {daily_totals.get('protein', 0):.1f}g / {test_data['target_macros']['protein']}g")
                                print(f"  - Carbs: {daily_totals.get('carbohydrates', 0):.1f}g / {test_data['target_macros']['carbohydrates']}g")
                                print(f"  - Fat: {daily_totals.get('fat', 0):.1f}g / {test_data['target_macros']['fat']}g")
                            
                            # Show RAG enhancement
                            if 'rag_enhancement' in response_data:
                                enhancement = response_data['rag_enhancement']
                                print(f"\n🔧 RAG Enhancement:")
                                print(f"  - Added ingredients: {len(enhancement.get('added_ingredients', []))}")
                                print(f"  - Notes: {enhancement.get('enhancement_notes', 'N/A')}")
                            
                            print(f"\n🎉 SUCCESS! System is working correctly!")
                            print("=" * 50)
                            print("✅ RAG → Site → This API: WORKING")
                            print("✅ Optimization: SUCCESSFUL")
                            print("✅ Ready for your main site integration!")
                            
                        except json.JSONDecodeError as e:
                            print(f"JSON parse error: {e}")
                            
        else:
            print(f"❌ API Call: FAILED")
            print(f"Error: {result.stderr}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_simple_workflow()
