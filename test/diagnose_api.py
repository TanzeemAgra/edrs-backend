"""
EDRS API Connection Diagnostic Tool
Diagnoses specific API connection issues between frontend and backend
"""

import requests
import json
import time
import subprocess
import sys
from urllib.parse import urljoin

class APIDiagnostic:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
        self.frontend_url = "http://localhost:3000"
        
    def test_backend_health(self):
        """Test backend health and availability"""
        print("🏥 Testing Backend Health...")
        
        try:
            response = requests.get(f"{self.base_url}/health/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Backend is healthy: {data}")
                return True
            else:
                print(f"  ❌ Health check failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Backend not reachable: {e}")
            return False
    
    def test_cors_preflight(self):
        """Test CORS preflight requests"""
        print("🌐 Testing CORS Configuration...")
        
        # Test OPTIONS request (preflight)
        try:
            headers = {
                'Origin': self.frontend_url,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = requests.options(
                f"{self.api_url}/auth/login/",
                headers=headers,
                timeout=5
            )
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
            }
            
            print(f"  📡 CORS Response ({response.status_code}):")
            for key, value in cors_headers.items():
                status = "✅" if value else "❌"
                print(f"    {status} {key}: {value}")
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ CORS preflight failed: {e}")
            return False
    
    def test_auth_endpoint(self):
        """Test authentication endpoint"""
        print("🔐 Testing Authentication Endpoint...")
        
        try:
            # Test with correct email format
            headers = {
                'Content-Type': 'application/json',
                'Origin': self.frontend_url
            }
            
            data = {
                'email': 'test@example.com',
                'password': 'testpassword'
            }
            
            response = requests.post(
                f"{self.api_url}/auth/login/",
                headers=headers,
                json=data,
                timeout=5
            )
            
            print(f"  📡 Auth Response ({response.status_code}):")
            print(f"    Response: {response.text[:200]}...")
            
            if response.status_code == 400:
                print("    ✅ Endpoint is working (400 = validation error, expected for fake credentials)")
                return True
            elif response.status_code == 200:
                print("    ✅ Login successful")
                return True
            else:
                print(f"    ⚠️  Unexpected status code: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Auth endpoint failed: {e}")
            return False
    
    def test_dashboard_endpoints(self):
        """Test dashboard endpoints that are failing in console"""
        print("📊 Testing Dashboard Endpoints...")
        
        endpoints = [
            '/dashboard/stats/',
            '/dashboard/charts/', 
            '/dashboard/notifications/',
            '/dashboard/activities/'
        ]
        
        results = {}
        
        for endpoint in endpoints:
            try:
                headers = {'Origin': self.frontend_url}
                response = requests.get(
                    f"{self.api_url}{endpoint}",
                    headers=headers,
                    timeout=5
                )
                
                status = "✅" if response.status_code in [200, 401] else "❌"
                results[endpoint] = response.status_code
                print(f"    {status} {endpoint}: {response.status_code}")
                
            except requests.exceptions.RequestException as e:
                print(f"    ❌ {endpoint}: Failed - {e}")
                results[endpoint] = "ERROR"
        
        return results
    
    def test_frontend_config(self):
        """Test frontend configuration"""
        print("⚙️  Testing Frontend Configuration...")
        
        try:
            # Check if frontend is running
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                print(f"  ✅ Frontend is running on {self.frontend_url}")
            else:
                print(f"  ⚠️  Frontend returned {response.status_code}")
                
        except requests.exceptions.RequestException:
            print(f"  ❌ Frontend not accessible at {self.frontend_url}")
        
        # Check environment file
        try:
            import os
            from pathlib import Path
            
            env_file = Path(__file__).parent / "frontend" / ".env"
            if env_file.exists():
                with open(env_file, 'r') as f:
                    content = f.read()
                    if "localhost:8001" in content:
                        print("  ✅ Frontend .env configured for port 8001")
                    else:
                        print("  ⚠️  Frontend .env might be misconfigured")
            else:
                print("  ⚠️  Frontend .env file not found")
                
        except Exception as e:
            print(f"  ❌ Error checking frontend config: {e}")
    
    def provide_recommendations(self):
        """Provide specific recommendations based on test results"""
        print("\n💡 RECOMMENDATIONS:")
        
        print("\n1. 🔧 If CORS is the issue:")
        print("   Add this to backend settings.py:")
        print("   CORS_ALLOW_ALL_ORIGINS = True  # For development only")
        
        print("\n2. 🔐 If authentication format is wrong:")
        print("   Frontend should send:")
        print("   {\"email\": \"user@example.com\", \"password\": \"password\"}")
        
        print("\n3. 🌐 If API URLs are wrong:")
        print("   Verify frontend .env has:")
        print("   VITE_API_URL=http://localhost:8001/api")
        
        print("\n4. 🚀 Quick fix - restart both servers:")
        print("   Backend: python manage.py runserver 0.0.0.0:8001")
        print("   Frontend: npm run dev")
        
        print("\n5. 🧪 Test manually:")
        print("   Open browser to http://localhost:3000")
        print("   Open DevTools → Network tab")
        print("   Try to login and check failed requests")
    
    def run_full_diagnostic(self):
        """Run complete diagnostic suite"""
        print("🔍 EDRS API Connection Diagnostic")
        print("=" * 60)
        
        results = {
            'backend_health': self.test_backend_health(),
            'cors_preflight': self.test_cors_preflight(),
            'auth_endpoint': self.test_auth_endpoint(),
            'dashboard_endpoints': self.test_dashboard_endpoints(),
        }
        
        print("\n" + "=" * 60)
        print("📋 DIAGNOSTIC SUMMARY")
        print("=" * 60)
        
        overall_status = "🟢 GOOD"
        
        for test, result in results.items():
            if test == 'dashboard_endpoints':
                continue  # Skip this one for overall status
                
            if result:
                print(f"✅ {test.replace('_', ' ').title()}: PASS")
            else:
                print(f"❌ {test.replace('_', ' ').title()}: FAIL")
                overall_status = "🔴 ISSUES DETECTED"
        
        print(f"\n🎯 Overall Status: {overall_status}")
        
        self.test_frontend_config()
        self.provide_recommendations()
        
        return results

if __name__ == "__main__":
    diagnostic = APIDiagnostic()
    diagnostic.run_full_diagnostic()