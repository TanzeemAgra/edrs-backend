#!/usr/bin/env python3
"""
Pre-deployment check for EDRS backend
Verifies all required modules can be imported
"""

import sys

def check_imports():
    required_modules = [
        'django',
        'rest_framework', 
        'corsheaders',
        'drf_spectacular',
        'storages',
        'boto3',
        'rest_framework_simplejwt',
        'allauth',
        'PIL',
        'requests',
        'gunicorn',
        'decouple',
        'whitenoise'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Missing modules: {', '.join(missing_modules)}")
        sys.exit(1)
    else:
        print("\n✅ All modules imported successfully!")
        return True

if __name__ == "__main__":
    check_imports()