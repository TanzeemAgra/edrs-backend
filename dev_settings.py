"""
Quick settings override for development server startup
"""
import os
import sys
from pathlib import Path

# Import base settings
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.settings import *

# Override for development
DEBUG = True
SECRET_KEY = 'django-insecure-dev-key-for-local-development-only'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Ensure CORS works
CORS_ALLOW_ALL_ORIGINS = True

print("🔧 Using dev settings override - DEBUG=True, ALLOWED_HOSTS configured")