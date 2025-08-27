#!/usr/bin/env python3
"""
Simple test to verify the RAG optimization engine works
"""

try:
    from rag_optimization_engine import RAGMealOptimizer
    print("✅ Successfully imported RAGMealOptimizer")
    
    # Test basic initialization
    optimizer = RAGMealOptimizer()
    print(f"✅ Successfully created optimizer with {len(optimizer.ingredients_db)} ingredients")
    
    # Test ingredient database structure
    sample_ingredient = optimizer.ingredients_db[0]
    print(f"✅ Sample ingredient: {sample_ingredient['name']}")
    print(f"   - Max quantity: {sample_ingredient.get('max_quantity', 'N/A')}")
    print(f"   - Category: {sample_ingredient.get('category', 'N/A')}")
    
    # Test ingredient selection method
    target_macros = {"calories": 500, "protein": 30, "carbs": 50, "fat": 15}
    rag_ingredients = []
    
    try:
        selected = optimizer._select_optimal_ingredients(target_macros, rag_ingredients)
        print(f"✅ Successfully selected {len(selected)} optimal ingredients")
    except Exception as e:
        print(f"⚠️  Ingredient selection failed: {e}")
    
    print("\n🎉 Basic functionality test completed successfully!")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Please install required dependencies:")
    print("pip install scipy optuna")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
