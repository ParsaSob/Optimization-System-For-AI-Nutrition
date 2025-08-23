#!/usr/bin/env python3
"""
Simple RAG test client that works
"""

import subprocess
import json

def test_rag_simple():
    """Test RAG endpoint with simple data"""
    try:
        print("Testing RAG endpoint with simple data...")
        
        # Simple test data
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
            "user_id": "test_user_simple"
        }
        
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
            try:
                response_text = result.stdout
                if '"StatusCode" : 200' in response_text:
                    print("Status: 200 OK")
                    
                    # Extract content
                    if '"Content" :' in response_text:
                        content_start = response_text.find('"Content" :') + 12
                        content_end = response_text.find('"RawContent" :')
                        if content_end > content_start:
                            content = response_text[content_start:content_end].strip()
                            print(f"Response preview: {content[:200]}...")
                            
                            # Parse JSON
                            try:
                                response_data = json.loads(content)
                                print(f"✅ Parsed JSON successfully!")
                                print(f"Keys: {list(response_data.keys())}")
                                
                                if 'optimization_result' in response_data:
                                    opt_result = response_data['optimization_result']
                                    print(f"Optimization method: {opt_result.get('optimization_method', 'N/A')}")
                                    print(f"Target achieved: {opt_result.get('target_achieved', 'N/A')}")
                                
                                if 'meal_plans' in response_data:
                                    meal_plans = response_data['meal_plans']
                                    print(f"Generated {len(meal_plans)} meal plans")
                                
                                if 'rag_enhancement' in response_data:
                                    enhancement = response_data['rag_enhancement']
                                    print(f"Added {len(enhancement.get('added_ingredients', []))} ingredients")
                                
                            except json.JSONDecodeError as e:
                                print(f"JSON parse error: {e}")
                                
                    else:
                        print("No content found in response")
                        
                else:
                    print(f"❌ Request failed: {result.stdout}")
                    
            except Exception as e:
                print(f"Response parsing error: {e}")
                
        else:
            print(f"❌ Request failed with return code: {result.returncode}")
            print(f"Error: {result.stderr}")
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_simple()
