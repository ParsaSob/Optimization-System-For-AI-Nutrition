#!/usr/bin/env python3
"""
Test script to verify that the macro validation fix works in the RAG optimization engine
"""

try:
    from rag_optimization_engine import RAGMealOptimizer
    print("✅ Successfully imported RAGMealOptimizer")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

def test_different_macro_formats():
    """Test the RAG optimization engine with different macro formats"""
    
    print("\n🧪 Testing Different Macro Formats")
    print("=" * 50)
    
    # Initialize the optimizer
    try:
        optimizer = RAGMealOptimizer()
        print("✅ RAG optimizer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize optimizer: {e}")
        return
    
    # Sample RAG response
    sample_rag_response = {
        "suggestions": [
            {
                "ingredients": [
                    {
                        "name": "chicken_breast",
                        "protein_per_100g": 31,
                        "carbs_per_100g": 0,
                        "fat_per_100g": 3.6,
                        "calories_per_100g": 165,
                        "quantity_needed": 150
                    }
                ]
            }
        ]
    }
    
    # Test Case 1: Standard format
    print("\n📋 Test Case 1: Standard format")
    target_macros_1 = {
        "calories": 800,
        "protein": 60,
        "carbs": 80,
        "fat": 25
    }
    
    try:
        result = optimizer.optimize_single_meal(
            rag_response=sample_rag_response,
            target_macros=target_macros_1,
            user_preferences={"diet_type": "high_protein"},
            meal_type="lunch"
        )
        print("✅ Standard format: Success")
        print(f"   Method: {result.get('optimization_result', {}).get('method', 'Unknown')}")
        print(f"   Success: {result.get('optimization_result', {}).get('success', False)}")
    except Exception as e:
        print(f"❌ Standard format: Failed - {e}")
    
    # Test Case 2: Alternative format (Next.js style)
    print("\n📋 Test Case 2: Alternative format (Next.js style)")
    target_macros_2 = {
        "calories": 800,
        "protein": 60,
        "carbohydrates": 80,  # Note: 'carbohydrates' instead of 'carbs'
        "fat": 25
    }
    
    try:
        result = optimizer.optimize_single_meal(
            rag_response=sample_rag_response,
            target_macros=target_macros_2,
            user_preferences={"diet_type": "high_protein"},
            meal_type="lunch"
        )
        print("✅ Alternative format: Success")
        print(f"   Method: {result.get('optimization_result', {}).get('method', 'Unknown')}")
        print(f"   Success: {result.get('optimization_result', {}).get('success', False)}")
    except Exception as e:
        print(f"❌ Alternative format: Failed - {e}")
    
    # Test Case 3: Missing macros (should use defaults)
    print("\n📋 Test Case 3: Missing macros (should use defaults)")
    target_macros_3 = {
        "calories": 800,
        "protein": 60
        # Missing carbs and fat
    }
    
    try:
        result = optimizer.optimize_single_meal(
            rag_response=sample_rag_response,
            target_macros=target_macros_3,
            user_preferences={"diet_type": "high_protein"},
            meal_type="lunch"
        )
        print("✅ Missing macros: Success (used defaults)")
        print(f"   Method: {result.get('optimization_result', {}).get('method', 'Unknown')}")
        print(f"   Success: {result.get('optimization_result', {}).get('success', False)}")
    except Exception as e:
        print(f"❌ Missing macros: Failed - {e}")
    
    # Test Case 4: Mixed format
    print("\n📋 Test Case 4: Mixed format")
    target_macros_4 = {
        "calories": 800,
        "proteins": 60,  # Note: 'proteins' instead of 'protein'
        "carb": 80,      # Note: 'carb' instead of 'carbs'
        "fats": 25       # Note: 'fats' instead of 'fat'
    }
    
    try:
        result = optimizer.optimize_single_meal(
            rag_response=sample_rag_response,
            target_macros=target_macros_4,
            user_preferences={"diet_type": "high_protein"},
            meal_type="lunch"
        )
        print("✅ Mixed format: Success")
        print(f"   Method: {result.get('optimization_result', {}).get('method', 'Unknown')}")
        print(f"   Success: {result.get('optimization_result', {}).get('success', False)}")
    except Exception as e:
        print(f"❌ Mixed format: Failed - {e}")

if __name__ == "__main__":
    print("🧪 Macro Validation Fix Test Suite")
    print("=" * 60)
    
    test_different_macro_formats()
    
    print("\n🎉 All tests completed!")
    print("\n💡 The fix should handle all macro formats without errors.")
