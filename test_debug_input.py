#!/usr/bin/env python3
"""
Test script to debug the RAG input processing issue
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_input_processing():
    """Test the input processing with the exact format from the website"""
    
    # Create the optimizer
    optimizer = RAGMealOptimizer()
    
    # Test input data (exact format from the website)
    test_input = {
        "rag_response": {
            "suggestions": [
                {
                    "ingredients": [
                        {
                            "name": "Ground Beef",
                            "protein_per_100g": 26,
                            "carbs_per_100g": 0,
                            "fat_per_100g": 15,
                            "calories_per_100g": 250,
                            "quantity_needed": 150
                        },
                        {
                            "name": "Onion",
                            "protein_per_100g": 1.1,
                            "carbs_per_100g": 9.3,
                            "fat_per_100g": 0.1,
                            "calories_per_100g": 40,
                            "quantity_needed": 50
                        },
                        {
                            "name": "Pita Bread",
                            "protein_per_100g": 9.1,
                            "carbs_per_100g": 55.7,
                            "fat_per_100g": 1.2,
                            "calories_per_100g": 275,
                            "quantity_needed": 100
                        },
                        {
                            "name": "Grilled Tomato",
                            "protein_per_100g": 0.9,
                            "carbs_per_100g": 3.9,
                            "fat_per_100g": 0.2,
                            "calories_per_100g": 18,
                            "quantity_needed": 80
                        },
                        {
                            "name": "Grilled Pepper",
                            "protein_per_100g": 1.3,
                            "carbs_per_100g": 6.0,
                            "fat_per_100g": 0.2,
                            "calories_per_100g": 31,
                            "quantity_needed": 60
                        }
                    ]
                }
            ],
            "success": True,
            "message": "Test meal ingredients"
        },
        "target_macros": {
            "calories": 800,
            "protein": 40,
            "carbs": 60,
            "fat": 30
        },
        "user_preferences": {
            "diet_type": "balanced",
            "allergies": [],
            "preferences": []
        },
        "user_id": "test_user",
        "meal_type": "lunch"
    }
    
    print("🧪 Testing input processing...")
    print(f"📥 Input type: {type(test_input)}")
    print(f"📥 Input keys: {list(test_input.keys())}")
    
    # Extract rag_response as the backend would do
    rag_response = test_input['rag_response']
    print(f"📥 RAG response type: {type(rag_response)}")
    print(f"📥 RAG response keys: {list(rag_response.keys())}")
    
    # Test the extraction method
    print("\n🔍 Testing _extract_rag_ingredients...")
    try:
        ingredients = optimizer._extract_rag_ingredients(rag_response)
        print(f"✅ Extraction successful! Found {len(ingredients)} ingredients")
        for i, ing in enumerate(ingredients):
            print(f"   {i+1}. {ing['name']}: protein={ing.get('protein_per_100g', 0)}, carbs={ing.get('carbs_per_100g', 0)}, fat={ing.get('fat_per_100g', 0)}, calories={ing.get('calories_per_100g', 0)}")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_input_processing()
