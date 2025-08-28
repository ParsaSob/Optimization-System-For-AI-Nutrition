#!/usr/bin/env python3
"""
Test script to debug snack helper ingredients issue
"""

from rag_optimization_engine import RAGMealOptimizer

def test_snack_helpers():
    """Test if snack helper ingredients are properly loaded"""
    
    # Initialize the optimizer
    optimizer = RAGMealOptimizer()
    
    print("🔍 Testing snack helper ingredients...")
    print(f"Available meal types: {list(optimizer.helper_ingredients.keys())}")
    
    # Test morning_snack
    if 'morning_snack' in optimizer.helper_ingredients:
        print(f"\n✅ morning_snack found!")
        print(f"Protein helpers: {len(optimizer.helper_ingredients['morning_snack']['protein'])}")
        print(f"Carbs helpers: {len(optimizer.helper_ingredients['morning_snack']['carbs'])}")
        print(f"Fat helpers: {len(optimizer.helper_ingredients['morning_snack']['fat'])}")
        
        # Test protein helpers
        protein_helpers = optimizer.helper_ingredients['morning_snack']['protein']
        print(f"\nProtein helpers: {[h['name'] for h in protein_helpers]}")
        
    else:
        print("❌ morning_snack NOT found!")
    
    # Test the _select_best_helper_candidate method
    print(f"\n🧪 Testing _select_best_helper_candidate for morning_snack...")
    
    # Mock existing names
    existing_names = set()
    
    # Test protein helper selection
    protein_helper = optimizer._select_best_helper_candidate('morning_snack', 'protein', existing_names)
    if protein_helper:
        print(f"✅ Selected protein helper: {protein_helper['name']}")
    else:
        print("❌ No protein helper selected")
    
    # Test carbs helper selection
    carbs_helper = optimizer._select_best_helper_candidate('morning_snack', 'carbs', existing_names)
    if carbs_helper:
        print(f"✅ Selected carbs helper: {carbs_helper['name']}")
    else:
        print("❌ No carbs helper selected")
    
    # Test fat helper selection
    fat_helper = optimizer._select_best_helper_candidate('morning_snack', 'fat', existing_names)
    if fat_helper:
        print(f"✅ Selected fat helper: {fat_helper['name']}")
    else:
        print("❌ No fat helper selected")

if __name__ == "__main__":
    test_snack_helpers()
