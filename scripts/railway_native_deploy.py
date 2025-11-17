#!/usr/bin/env python
"""
Railway Native Deployment Script
Validates and prepares Django app for Railway's Python buildpack
"""

import os
import sys
import subprocess

def check_requirements():
    """Check if requirements.txt exists and is valid"""
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    print("✅ requirements.txt found")
    return True

def check_runtime():
    """Check if runtime.txt exists"""
    if not os.path.exists('runtime.txt'):
        print("❌ runtime.txt not found")
        return False
    
    with open('runtime.txt', 'r') as f:
        python_version = f.read().strip()
    
    print(f"✅ runtime.txt found: {python_version}")
    return True

def check_procfile():
    """Check if Procfile exists"""
    if not os.path.exists('Procfile'):
        print("❌ Procfile not found")
        return False
    
    print("✅ Procfile found")
    return True

def check_django_setup():
    """Validate Django setup"""
    try:
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        
        # Import Django
        import django
        django.setup()
        
        # Test basic functionality
        from django.conf import settings
        from django.db import connection
        
        print("✅ Django setup valid")
        return True
        
    except Exception as e:
        print(f"❌ Django setup error: {e}")
        return False

def validate_settings():
    """Check Django settings for Railway deployment"""
    try:
        from django.conf import settings
        
        # Check required settings
        required_settings = [
            'SECRET_KEY',
            'DATABASES',
            'ALLOWED_HOSTS',
        ]
        
        for setting in required_settings:
            if not hasattr(settings, setting):
                print(f"❌ Missing setting: {setting}")
                return False
        
        # Check ALLOWED_HOSTS includes Railway domains
        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        if not any(['railway.app' in host or '*' in allowed_hosts for host in allowed_hosts]):
            print("⚠️  ALLOWED_HOSTS should include Railway domains")
        
        print("✅ Django settings validated")
        return True
        
    except Exception as e:
        print(f"❌ Settings validation error: {e}")
        return False

def check_environment_vars():
    """Check for required environment variables"""
    print("\n📋 Environment Variables Check:")
    
    env_vars = {
        'DATABASE_URL': 'Railway PostgreSQL connection',
        'SECRET_KEY': 'Django secret key',
    }
    
    missing_vars = []
    for var, description in env_vars.items():
        if os.environ.get(var):
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Missing ({description})")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Set these variables in Railway dashboard:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    return True

def main():
    """Run all deployment checks"""
    print("🚀 Railway Native Deployment Validation")
    print("=" * 50)
    
    checks = [
        ("Requirements File", check_requirements),
        ("Runtime File", check_runtime),
        ("Procfile", check_procfile),
        ("Django Setup", check_django_setup),
        ("Django Settings", validate_settings),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n{name}:")
        if check_func():
            passed += 1
    
    # Environment variables check (informational)
    check_environment_vars()
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ Ready for Railway native deployment!")
        print("\n📝 Deployment Steps:")
        print("1. Push code to GitHub repository")
        print("2. Connect repository to Railway")
        print("3. Set environment variables in Railway dashboard")
        print("4. Railway will auto-deploy using Python buildpack")
        return 0
    else:
        print("❌ Fix issues before deploying to Railway")
        return 1

if __name__ == "__main__":
    exit(main())