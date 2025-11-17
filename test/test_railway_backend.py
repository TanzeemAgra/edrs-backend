#!/usr/bin/env python3
"""
Test Railway Backend Connectivity
"""

import requests
import json

def test_railway_backend():
    base_url = "https://edrs-backend-production.up.railway.app"
    
    print("🔍 Testing Railway Backend...")
    print(f"Base URL: {base_url}")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        "/health/",
        "/api/auth/login/",
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n🌐 Testing: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.text:
                try:
                    data = response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                except:
                    print(f"Response (text): {response.text[:200]}...")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}")
    
    # Test login specifically
    print(f"\n🔑 Testing Login...")
    login_url = f"{base_url}/api/auth/login/"
    login_data = {
        "email": "tanzeem@rejlers.ae",
        "password": "rejlers2025"
    }
    
    try:
        response = requests.post(
            login_url, 
            json=login_data, 
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"Login Status: {response.status_code}")
        if response.text:
            try:
                data = response.json()
                print(f"Login Response: {json.dumps(data, indent=2)}")
            except:
                print(f"Login Response (text): {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Login Error: {e}")

if __name__ == "__main__":
    test_railway_backend()