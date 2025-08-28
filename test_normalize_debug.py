#!/usr/bin/env python3
"""
Test script to debug _normalize_meal_type method specifically
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_normalize_debug():
    """Test _normalize_meal_type method specifically"""
    
    optimizer = RAGMealOptimizer()
    
    print("🧪 Testing _normalize_meal_type Method")
    print("=" * 60)
    
    # Test various meal types
    test_cases = [
        "Morning Snack",
        "morning_snack",
        "morning snack",
        "MORNING SNACK",
        "MorningSnack",
        "Afternoon Snack",
        "afternoon_snack",
        "Breakfast",
        "breakfast",
        "Lunch",
        "lunch",
        "Dinner",
        "dinner"
    ]
    
    print("📥 Testing meal type normalization...")
    
    for meal_type in test_cases:
        try:
            normalized = optimizer._normalize_meal_type(meal_type)
            print(f"   '{meal_type}' -> '{normalized}'")
            
            # Check if normalized type exists in helper_ingredients
            if normalized in optimizer.helper_ingredients:
                print(f"      ✅ Found in helper_ingredients")
            else:
                print(f"      ❌ NOT found in helper_ingredients")
                
        except Exception as e:
            print(f"   '{meal_type}' -> ERROR: {e}")
    
    print("\n🔍 Checking helper_ingredients keys:")
    print(f"   Available keys: {list(optimizer.helper_ingredients.keys())}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_normalize_debug()
