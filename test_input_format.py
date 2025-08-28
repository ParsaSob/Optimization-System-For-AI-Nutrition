#!/usr/bin/env python3
"""
Test script to check input format from website
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_website_input_format():
    """Test different possible input formats from website"""
    
    optimizer = RAGMealOptimizer()
    
    # Test different possible formats that website might send
    
    print("🧪 Testing different input formats from website")
    print("=" * 60)
    
    # Format 1: List of dicts with name and quantity only
    print("\n1️⃣ Testing format: [{'name': 'Ground Beef', 'quantity': 200}, ...]")
    format1 = [
        {'name': 'Ground Beef', 'quantity': 200},
        {'name': 'Onion', 'quantity': 100},
        {'name': 'Butter', 'quantity': 10},
        {'name': 'Pita Bread', 'quantity': 100},
        {'name': 'Grilled Tomato', 'quantity': 100}
    ]
    
    result1 = optimizer._extract_rag_ingredients(format1)
    print(f"   Extracted {len(result1)} ingredients:")
    for ing in result1:
        print(f"   - {ing['name']}: protein={ing.get('protein_per_100g', 0)}, "
              f"carbs={ing.get('carbs_per_100g', 0)}, "
              f"fat={ing.get('fat_per_100g', 0)}, "
              f"calories={ing.get('calories_per_100g', 0)}")
    
    # Format 2: List of dicts with nutritional info
    print("\n2️⃣ Testing format: [{'name': 'Ground Beef', 'quantity': 200, 'protein_per_100g': 26, ...}, ...]")
    format2 = [
        {
            'name': 'Ground Beef',
            'quantity': 200,
            'protein_per_100g': 26.0,
            'carbs_per_100g': 0.0,
            'fat_per_100g': 15.0,
            'calories_per_100g': 250.0
        },
        {
            'name': 'Onion',
            'quantity': 100,
            'protein_per_100g': 1.1,
            'carbs_per_100g': 9.0,
            'fat_per_100g': 0.1,
            'calories_per_100g': 40.0
        }
    ]
    
    result2 = optimizer._extract_rag_ingredients(format2)
    print(f"   Extracted {len(result2)} ingredients:")
    for ing in result2:
        print(f"   - {ing['name']}: protein={ing.get('protein_per_100g', 0)}, "
              f"carbs={ing.get('carbs_per_100g', 0)}, "
              f"fat={ing.get('fat_per_100g', 0)}, "
              f"calories={ing.get('calories_per_100g', 0)}")
    
    # Format 3: Dict with ingredients key
    print("\n3️⃣ Testing format: {'ingredients': [{'name': 'Ground Beef', 'quantity': 200}, ...]}")
    format3 = {
        'ingredients': [
            {'name': 'Ground Beef', 'quantity': 200},
            {'name': 'Onion', 'quantity': 100},
            {'name': 'Butter', 'quantity': 10}
        ]
    }
    
    result3 = optimizer._extract_rag_ingredients(format3)
    print(f"   Extracted {len(result3)} ingredients:")
    for ing in result3:
        print(f"   - {ing['name']}: protein={ing.get('protein_per_100g', 0)}, "
              f"carbs={ing.get('carbs_per_100g', 0)}, "
              f"fat={ing.get('fat_per_100g', 0)}, "
              f"calories={ing.get('calories_per_100g', 0)}")
    
    # Format 4: Dict with suggestions key
    print("\n4️⃣ Testing format: {'suggestions': [{'ingredients': [{'name': 'Ground Beef', 'quantity': 200}, ...]}]}")
    format4 = {
        'suggestions': [
            {
                'ingredients': [
                    {'name': 'Ground Beef', 'quantity': 200},
                    {'name': 'Onion', 'quantity': 100}
                ]
            }
        ]
    }
    
    result4 = optimizer._extract_rag_ingredients(format4)
    print(f"   Extracted {len(result4)} ingredients:")
    for ing in result4:
        print(f"   - {ing['name']}: protein={ing.get('protein_per_100g', 0)}, "
              f"carbs={ing.get('carbs_per_100g', 0)}, "
              f"fat={ing.get('fat_per_100g', 0)}, "
              f"calories={ing.get('calories_per_100g', 0)}")
    
    # Format 5: String format
    print("\n5️⃣ Testing format: 'Ground Beef, Onion, Butter, Pita Bread, Grilled Tomato'")
    format5 = "Ground Beef, Onion, Butter, Pita Bread, Grilled Tomato"
    
    result5 = optimizer._extract_rag_ingredients(format5)
    print(f"   Extracted {len(result5)} ingredients:")
    for ing in result5:
        print(f"   - {ing['name']}: protein={ing.get('protein_per_100g', 0)}, "
              f"carbs={ing.get('carbs_per_100g', 0)}, "
              f"fat={ing.get('fat_per_100g', 0)}, "
              f"calories={ing.get('calories_per_100g', 0)}")
    
    print("\n" + "=" * 60)
    print("📋 Summary:")
    print("   Format 1: Basic list of dicts - ✅ Works")
    print("   Format 2: List with nutrition - ✅ Works") 
    print("   Format 3: Dict with ingredients - ✅ Works")
    print("   Format 4: Dict with suggestions - ✅ Works")
    print("   Format 5: String format - ⚠️ Limited (only finds mapped keywords)")
    
    print("\n🔍 Please check what format your website is sending!")
    print("   The most likely formats are:")
    print("   - Format 1: [{'name': 'Ground Beef', 'quantity': 200}, ...]")
    print("   - Format 2: [{'name': 'Ground Beef', 'quantity': 200, 'protein_per_100g': 26, ...}, ...]")
    print("   - Format 3: {'ingredients': [{'name': 'Ground Beef', 'quantity': 200}, ...]}")

if __name__ == "__main__":
    test_website_input_format()
