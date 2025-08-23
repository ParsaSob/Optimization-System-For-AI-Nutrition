#!/usr/bin/env python3
"""
Very simple test client
"""

import asyncio
import httpx

async def test_simple():
    """Test with minimal data"""
    try:
        print("Testing simple endpoint...")
        
        async with httpx.AsyncClient() as client:
            # Test with empty JSON
            response = await client.post(
                "http://localhost:8000/optimize-rag-meal",
                json={},
                timeout=10.0
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple())
