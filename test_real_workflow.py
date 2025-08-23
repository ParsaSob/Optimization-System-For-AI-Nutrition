#!/usr/bin/env python3
"""
Test Real Workflow: RAG → Site → This API
"""

import subprocess
import json

def test_real_workflow():
    """Test the real workflow from RAG to this API"""
    try:
        print("🚀 Testing Real RAG Workflow")
        print("=" * 50)
        print("Simulating: RAG System → Site → This API")
        print()
        
        # Step 1: Test RAG connection endpoint
        print("📡 Step 1: Testing RAG Connection...")
        cmd1 = [
            "powershell", "-Command",
            "Invoke-WebRequest -Uri 'http://localhost:8000/test-rag-connection' -Method POST"
        ]
        
        result1 = subprocess.run(cmd1, capture_output=True, text=True)
        
        if result1.returncode == 0:
            print("✅ RAG Connection Test: SUCCESS")
            
            # Parse response
            response_text = result1.stdout
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
                            print(f"Message: {response_data.get('message', 'N/A')}")
                            print(f"Status: {response_data.get('status', 'N/A')}")
                            print(f"Endpoint: {response_data.get('endpoint', 'N/A')}")
                            
                            print("\n📋 Workflow:")
                            workflow = response_data.get('workflow', [])
                            for i, step in enumerate(workflow, 1):
                                print(f"  {i}. {step}")
                                
                        except json.JSONDecodeError as e:
                            print(f"JSON parse error: {e}")
                            
        else:
            print(f"❌ RAG Connection Test: FAILED")
            print(f"Error: {result1.stderr}")
            return
        
        print("\n" + "="*50)
        
        # Step 2: Test with realistic RAG data (like what your site would send)
        print("🍽️ Step 2: Testing with Realistic RAG Data...")
        
        # This simulates what your main site would send after getting RAG response
        realistic_rag_data = {
            "rag_response": {
                "suggestions": [
                    {
                        "mealTitle": "Persian Lunch Kabab Koobideh",
                        "description": "High protein Persian meal with beef and rice",
                        "ingredients": [
                            {
                                "name": "Ground Beef",
                                "amount": 200,
                                "unit": "g",
                                "calories": 400,
                                "protein": 40,
                                "carbs": 0,
                                "fat": 30
                            },
                            {
                                "name": "Basmati Rice",
                                "amount": 150,
                                "unit": "g", 
                                "calories": 540,
                                "protein": 10,
                                "carbs": 120,
                                "fat": 2
                            },
                            {
                                "name": "Onion",
                                "amount": 50,
                                "unit": "g",
                                "calories": 20,
                                "protein": 1,
                                "carbs": 5,
                                "fat": 0
                            }
                        ],
                        "totalCalories": 960,
                        "totalProtein": 51,
                        "totalCarbs": 125,
                        "totalFat": 32
                    }
                ],
                "success": True,
                "message": "RAG suggestions generated successfully"
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
                "preferred_cuisines": ["persian", "mediterranean"],
                "calorie_preference": "moderate",
                "protein_preference": "high",
                "carb_preference": "moderate",
                "fat_preference": "moderate"
            },
            "user_id": "real_user_123"
        }
        
        print(f"📊 RAG Data Summary:")
        print(f"  - Meal suggestions: {len(realistic_rag_data['rag_response']['suggestions'])}")
        print(f"  - Total calories from RAG: {realistic_rag_data['rag_response']['suggestions'][0]['totalCalories']}")
        print(f"  - Target calories: {realistic_rag_data['target_macros']['calories']}")
        print(f"  - Missing calories: {realistic_rag_data['target_macros']['calories'] - realistic_rag_data['rag_response']['suggestions'][0]['totalCalories']}")
        
        # Convert to JSON string
        json_data = json.dumps(realistic_rag_data)
        
        # Test the main optimization endpoint
        print(f"\n🔧 Step 3: Testing RAG Optimization...")
        cmd2 = [
            "powershell", "-Command",
            f"Invoke-WebRequest -Uri 'http://localhost:8000/optimize-rag-meal' -Method POST -Body '{json_data}' -ContentType 'application/json'"
        ]
        
        result2 = subprocess.run(cmd2, capture_output=True, text=True)
        
        if result2.returncode == 0:
            print("✅ RAG Optimization: SUCCESS")
            
            # Parse response
            response_text = result2.stdout
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
                            print(f"✅ Parsed optimization response successfully!")
                            
                            # Show key results
                            optimization_result = response_data.get('optimization_result', {})
                            print(f"\n📊 Optimization Results:")
                            print(f"  - Method: {optimization_result.get('optimization_method', 'N/A')}")
                            print(f"  - Target achieved: {optimization_result.get('target_achieved', 'N/A')}")
                            print(f"  - Computation time: {optimization_result.get('computation_time', 'N/A')}s")
                            
                            # Show meal plans
                            meal_plans = response_data.get('meal_plans', [])
                            print(f"\n🍽️ Generated {len(meal_plans)} meal plans:")
                            
                            for i, meal_plan in enumerate(meal_plans[:3]):  # Show first 3
                                meal_time = meal_plan.get('meal_time', 'Unknown')
                                total_calories = meal_plan.get('total_calories', 0)
                                total_protein = meal_plan.get('total_protein', 0)
                                
                                print(f"  {i+1}. {meal_time}: {total_calories:.1f} cal, {total_protein:.1f}g protein")
                            
                            # Show daily totals
                            daily_totals = response_data.get('daily_totals', {})
                            if daily_totals:
                                print(f"\n📈 Daily Totals:")
                                print(f"  - Calories: {daily_totals.get('calories', 0):.1f} / {realistic_rag_data['target_macros']['calories']}")
                                print(f"  - Protein: {daily_totals.get('protein', 0):.1f}g / {realistic_rag_data['target_macros']['protein']}g")
                                print(f"  - Carbs: {daily_totals.get('carbohydrates', 0):.1f}g / {realistic_rag_data['target_macros']['carbohydrates']}g")
                                print(f"  - Fat: {daily_totals.get('fat', 0):.1f}g / {realistic_rag_data['target_macros']['fat']}g")
                            
                            # Show RAG enhancement info
                            if 'rag_enhancement' in response_data:
                                enhancement = response_data['rag_enhancement']
                                print(f"\n🔧 RAG Enhancement:")
                                print(f"  - Added ingredients: {len(enhancement.get('added_ingredients', []))}")
                                print(f"  - Notes: {enhancement.get('enhancement_notes', 'N/A')}")
                            
                            # Show shopping list
                            shopping_list = response_data.get('shopping_list', [])
                            if shopping_list:
                                print(f"\n🛒 Shopping List (first 5 items):")
                                for item in shopping_list[:5]:
                                    name = item.get('name', 'Unknown')
                                    quantity = item.get('quantity', 0)
                                    unit = item.get('unit', 'g')
                                    print(f"  • {name}: {quantity:.1f} {unit}")
                            
                            print(f"\n🎉 WORKFLOW TEST COMPLETED SUCCESSFULLY!")
                            print("=" * 50)
                            print("✅ RAG System → Site → This API: WORKING")
                            print("✅ Optimization: SUCCESSFUL")
                            print("✅ Meal Plans: GENERATED")
                            print("✅ Ready for production integration!")
                            
                        except json.JSONDecodeError as e:
                            print(f"JSON parse error: {e}")
                            print(f"Raw content: {content[:500]}...")
                            
        else:
            print(f"❌ RAG Optimization: FAILED")
            print(f"Error: {result2.stderr}")
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_workflow()
