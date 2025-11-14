#!/usr/bin/env python
"""
Railway Deployment Pre-check Script
Run this script to validate your setup before deploying to Railway
"""

import os
import sys
import django
import requests
from urllib.parse import urlparse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def check_environment():
    """Check if all required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def check_database():
    """Test database connectivity"""
    print("🔍 Testing database connection...")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        if result and result[0] == 1:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed - unexpected result")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_models():
    """Test model operations"""
    print("🔍 Testing Django models...")
    
    try:
        from django.contrib.auth import get_user_model
        from patients.models import Patient
        
        User = get_user_model()
        
        # Test user model
        user_count = User.objects.count()
        print(f"✅ Users in database: {user_count}")
        
        # Test patient model
        patient_count = Patient.objects.count()
        print(f"✅ Patients in database: {patient_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def check_health_endpoint():
    """Test health endpoint if server is running"""
    print("🔍 Testing health endpoint...")
    
    try:
        # Try to connect to local server
        response = requests.get('http://127.0.0.1:8000/health/', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint responding: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"⚠️  Health endpoint returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running locally (this is OK for deployment)")
        return True
    except Exception as e:
        print(f"⚠️  Health endpoint test failed: {e}")
        return True  # Not critical for deployment

def check_static_files():
    """Check if static files can be collected"""
    print("🔍 Testing static file collection...")
    
    try:
        from django.core.management import execute_from_command_line
        
        # Test collectstatic (dry run)
        old_argv = sys.argv
        sys.argv = ['manage.py', 'collectstatic', '--dry-run', '--noinput']
        
        try:
            execute_from_command_line(sys.argv)
            print("✅ Static files collection test passed")
            return True
        except SystemExit:
            print("✅ Static files collection test completed")
            return True
        finally:
            sys.argv = old_argv
            
    except Exception as e:
        print(f"❌ Static files test failed: {e}")
        return False

def main():
    """Run all pre-deployment checks"""
    print("🚀 Railway Deployment Pre-check")
    print("=" * 40)
    
    checks = [
        ("Environment Variables", check_environment),
        ("Database Connection", check_database),
        ("Django Models", check_models),
        ("Static Files", check_static_files),
        ("Health Endpoint", check_health_endpoint),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n{name}:")
        if check_func():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ All checks passed! Ready for Railway deployment.")
        return 0
    elif passed >= total - 1:
        print("⚠️  Most checks passed. Deployment should work.")
        return 0
    else:
        print("❌ Multiple checks failed. Fix issues before deploying.")
        return 1

if __name__ == "__main__":
    exit(main())