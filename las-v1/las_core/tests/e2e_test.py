import requests
import json
import time
import sys
import os

# Configuration
API_URL = os.getenv("LAS_API_URL", "http://localhost:8000")
API_KEY = os.getenv("LAS_API_KEY", "las-secret-key")

def test_health():
    """Test the health endpoint."""
    print(f"Testing Health Endpoint at {API_URL}/health...")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ Health Check Passed")
            return True
        else:
            print(f"❌ Health Check Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health Check Error: {str(e)}")
        return False

def test_query():
    """Test the query endpoint with a simple prompt."""
    print(f"\nTesting Query Endpoint at {API_URL}/query...")
    
    payload = {
        "query": "Hello, are you working?"
    }
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/query", json=payload, headers=headers)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query Successful ({duration:.2f}s)")
            print(f"   Agent: {data.get('agent_name')}")
            print(f"   Answer: {data.get('answer')}")
            return True
        elif response.status_code == 403:
            print("❌ Authentication Failed (403). Check API Key.")
            return False
        else:
            print(f"❌ Query Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Query Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("LAS End-to-End Test Suite")
    print("="*50)
    
    health_ok = test_health()
    if not health_ok:
        print("\n⚠️  Aborting tests due to health check failure.")
        sys.exit(1)
        
    query_ok = test_query()
    
    if health_ok and query_ok:
        print("\n🎉 All Tests Passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed.")
        sys.exit(1)
