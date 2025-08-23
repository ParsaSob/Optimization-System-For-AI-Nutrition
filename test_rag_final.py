#!/usr/bin/env python3
"""
Final RAG test client
"""

import subprocess
import json

def test_rag_endpoint():
    """Test RAG endpoint with proper data"""
    try:
        print("Testing RAG endpoint with proper data...")
        
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
            "user_id": "test_user"
        }
        
        # Convert to JSON string
        json_data = json.dumps(test_data)
        
        # Test with PowerShell
        cmd = [
            "powershell", "-Command",
            f"Invoke-WebRequest -Uri 'http://localhost:8000/optimize-rag-meal' -Method POST -Body '{json_data}' -ContentType 'application/json'"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_rag_endpoint()
