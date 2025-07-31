"""
Simple test script for SkillNavigator API endpoints
Run this after starting the backend to verify everything is working
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_agent_status():
    """Test the agent status endpoint"""
    print("\n🔍 Testing agent status...")
    try:
        response = requests.get(f"{BASE_URL}/agents/status")
        if response.status_code == 200:
            print("✅ Agent status check passed!")
            data = response.json()
            for agent, status in data.items():
                print(f"   {agent}: {status}")
        else:
            print(f"❌ Agent status check failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Agent status error: {e}")

def test_jobs_endpoint():
    """Test the jobs search endpoint"""
    print("\n🔍 Testing jobs search...")
    try:
        params = {
            "q": "python developer",
            "location": "remote",
            "limit": 5
        }
        response = requests.get(f"{BASE_URL}/api/jobs/search", params=params)
        if response.status_code == 200:
            print("✅ Jobs search passed!")
            data = response.json()
            print(f"   Found {len(data.get('jobs', []))} jobs")
            if data.get('jobs'):
                print(f"   First job: {data['jobs'][0]['title']} at {data['jobs'][0]['company']}")
        else:
            print(f"❌ Jobs search failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Jobs search error: {e}")

def test_user_profiles():
    """Test the user profiles endpoint"""
    print("\n🔍 Testing user profiles...")
    try:
        response = requests.get(f"{BASE_URL}/api/users/")
        if response.status_code == 200:
            print("✅ User profiles check passed!")
            data = response.json()
            print(f"   Found {len(data)} users")
            if data:
                print(f"   First user: {data[0]['name']} ({data[0]['email']})")
        else:
            print(f"❌ User profiles check failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ User profiles error: {e}")

def test_applications():
    """Test the applications endpoint"""
    print("\n🔍 Testing applications...")
    try:
        response = requests.get(f"{BASE_URL}/api/tracker/applications")
        if response.status_code == 200:
            print("✅ Applications check passed!")
            data = response.json()
            print(f"   Found {len(data)} applications")
            if data:
                print(f"   First application: {data[0]['status']} for job ID {data[0]['job_id']}")
        else:
            print(f"❌ Applications check failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Applications error: {e}")

def test_scraping_trigger():
    """Test the manual scraping trigger"""
    print("\n🔍 Testing manual scraping trigger...")
    try:
        payload = {
            "portals": ["linkedin"],
            "filters": {
                "keywords": ["python"],
                "location": "remote",
                "max_jobs": 5
            }
        }
        response = requests.post(f"{BASE_URL}/scrape", json=payload)
        if response.status_code in [200, 202]:
            print("✅ Scraping trigger passed!")
            data = response.json()
            print(f"   Response: {data.get('message', 'Started')}")
        else:
            print(f"❌ Scraping trigger failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Scraping trigger error: {e}")

def test_workflow_trigger():
    """Test the workflow trigger"""
    print("\n🔍 Testing workflow trigger...")
    try:
        payload = {
            "user_id": 1,
            "workflow_type": "score_jobs"
        }
        response = requests.post(f"{BASE_URL}/workflow", json=payload)
        if response.status_code in [200, 202]:
            print("✅ Workflow trigger passed!")
            data = response.json()
            print(f"   Response: {data.get('message', 'Started')}")
        else:
            print(f"❌ Workflow trigger failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Workflow trigger error: {e}")

def main():
    """Run all tests"""
    print("🚀 SkillNavigator API Test Suite")
    print("=" * 50)
    print(f"Testing API at: {BASE_URL}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    # Run all tests
    test_health_check()
    test_agent_status()
    test_jobs_endpoint()
    test_user_profiles()
    test_applications()
    test_scraping_trigger()
    test_workflow_trigger()
    
    print("\n🎉 Test suite completed!")
    print("\nIf you see any ❌ errors, please check:")
    print("  1. The backend server is running on localhost:8000")
    print("  2. The database has been initialized with sample data")
    print("  3. Your .env file is configured correctly")

if __name__ == "__main__":
    main()
