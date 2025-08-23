#!/usr/bin/env python3
"""
Simple endpoint test
"""

import asyncio
import httpx
import json

async def test_endpoint():
    """Test RAG endpoint with minimal data"""
    try:
        print("Testing RAG endpoint...")
        
        simple_data = {
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
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/optimize-rag-meal",
                json=simple_data,
                timeout=30.0
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("✅ Endpoint working!")
            else:
                print(f"❌ Endpoint failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_endpoint())
