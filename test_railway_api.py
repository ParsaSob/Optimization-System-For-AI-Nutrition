import requests
import json

def test_railway_api():
    """Test the Railway API endpoints to identify issues"""
    
    base_url = "https://web-production-c541.up.railway.app"
    
    print("🚀 Testing Railway API...")
    print("=" * 50)
    
    # Test 1: Health endpoint
    print("\n1️⃣ Testing /health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        if response.status_code == 200:
            print("   ✅ Health endpoint working")
        else:
            print("   ❌ Health endpoint failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Ingredients endpoint
    print("\n2️⃣ Testing /ingredients endpoint...")
    try:
        response = requests.get(f"{base_url}/ingredients", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Ingredients endpoint working - {len(data)} ingredients")
        else:
            print(f"   ❌ Ingredients endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test RAG connection endpoint
    print("\n3️⃣ Testing /test-rag-connection endpoint...")
    try:
        response = requests.post(f"{base_url}/test-rag-connection", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        if response.status_code == 200:
            print("   ✅ RAG connection test working")
        else:
            print("   ❌ RAG connection test failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Simple RAG optimization with minimal data
    print("\n4️⃣ Testing /optimize-rag-meal endpoint...")
    try:
        test_data = {
            "rag_response": {
                "suggestions": [
                    {
                        "ingredients": [
                            {
                                "name": "Test Ingredient",
                                "amount": 100,
                                "unit": "g",
                                "calories": 100,
                                "protein": 10,
                                "carbs": 10,
                                "fat": 5
                            }
                        ]
                    }
                ],
                "success": True
            },
            "target_macros": {
                "calories": 2000,
                "protein": 150,
                "carbohydrates": 200,
                "fat": 65
            },
            "user_preferences": {
                "dietary_restrictions": [],
                "allergies": [],
                "preferred_cuisines": ["persian"],
                "calorie_preference": "moderate",
                "protein_preference": "high",
                "carb_preference": "moderate",
                "fat_preference": "moderate"
            },
            "user_id": "test_user"
        }
        
        response = requests.post(
            f"{base_url}/optimize-rag-meal",
            json=test_data,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ RAG optimization working")
            data = response.json()
            print(f"   📊 Result: {data.get('optimization_result', {}).get('success', 'Unknown')}")
        else:
            print(f"   ❌ RAG optimization failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing complete!")

if __name__ == "__main__":
    test_railway_api()
