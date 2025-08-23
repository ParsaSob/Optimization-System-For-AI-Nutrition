#!/usr/bin/env python3
"""
Test database manager
"""

import asyncio
from database import DatabaseManager

async def test_db():
    """Test database manager"""
    try:
        print("Creating database manager...")
        dm = DatabaseManager()
        
        print("Initializing database...")
        await dm.initialize()
        
        print("Getting ingredients...")
        ingredients = await dm.get_all_ingredients()
        
        print(f"✅ Got {len(ingredients)} ingredients")
        for i, ing in enumerate(ingredients[:3]):
            print(f"  {i+1}. {ing.name} - {ing.calories_per_100g} cal/100g")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_db())
