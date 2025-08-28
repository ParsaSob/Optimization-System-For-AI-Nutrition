#!/usr/bin/env python3
"""
Test string extraction logic for RAG response
"""

from rag_optimization_engine import RAGMealOptimizer
import logging

# Configure logging to see debug info
logging.basicConfig(level=logging.INFO)

def test_string_extraction():
    optimizer = RAGMealOptimizer()
    
    test_string = "یک وعده غذایی سالم برای ناهار با گوشت، پیاز، گوجه و نان پیتا"
    
    print(f"🔍 Testing extraction from: '{test_string}'")
    
    ingredients = optimizer._extract_rag_ingredients(test_string)
    
    print(f"📋 Extracted ingredients: {len(ingredients)}")
    for ing in ingredients:
        print(f"  - {ing['name']}: {ing.get('quantity', 'N/A')}g")
    
    return ingredients

if __name__ == "__main__":
    test_string_extraction()
