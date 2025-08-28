#!/usr/bin/env python3
"""
Test script to verify meal type normalization works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_optimization_engine import RAGMealOptimizer

def test_meal_type_normalization():
    """Test meal type normalization"""
    
    optimizer = RAGMealOptimizer()
    
    print("🧪 Testing Meal Type Normalization")
    print("=" * 60)
    
    # Test various meal type formats
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
        "dinner",
        "Unknown Meal",
        ""
    ]
    
    print("📋 Testing meal type normalization:")
    for meal_type in test_cases:
        normalized = optimizer._normalize_meal_type(meal_type)
        print(f"   '{meal_type}' -> '{normalized}'")
        
        # Check if normalized type exists in helper_ingredients
        if normalized in optimizer.helper_ingredients:
            print(f"     ✅ Found in helper_ingredients")
        else:
            print(f"     ❌ NOT found in helper_ingredients")
    
    print("\n🔍 Checking helper_ingredients keys:")
    for key in optimizer.helper_ingredients.keys():
        print(f"   - {key}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_meal_type_normalization()
