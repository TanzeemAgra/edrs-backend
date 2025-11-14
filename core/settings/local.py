"""
EDRS Local Development Settings
Smart configuration for local Docker environment
Inherits from base settings with local-specific overrides
"""

import os
import sys
from pathlib import Path

# Import from base settings
from .base import *

# =================================================================
# 🔧 ENVIRONMENT CONFIGURATION
# =================================================================

# Environment identifier
ENVIRONMENT = 'local'
DEBUG = True

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =================================================================
# 🔐 SECURITY SETTINGS (Local Development)
# =================================================================

# Secret key for local development
SECRET_KEY = os.getenv('SECRET_KEY', 'local-django-secret-key-for-development-only')

# Allowed hosts (liberal for local development)
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'backend',
    'frontend',
    os.getenv('BACKEND_HOST', '127.0.0.1'),
]

# CORS Configuration (liberal for local development)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://frontend:3000",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# =================================================================
# 📊 DATABASE CONFIGURATION
# =================================================================

# PostgreSQL Database (Primary)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'edrs_local',
        'USER': 'postgres',
        'PASSWORD': 'localpassword123',
        'HOST': 'postgres',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'disable',
        },
        'CONN_MAX_AGE': 60,
        'CONN_HEALTH_CHECKS': True,
    }
}

# MongoDB Configuration (Secondary)
MONGODB_DATABASES = {
    'default': {
        'name': os.getenv('MONGO_DB', 'edrs_local_mongo'),
        'host': os.getenv('MONGO_HOST', 'mongodb'),
        'port': int(os.getenv('MONGO_PORT', '27017')),
        'username': os.getenv('MONGO_USER', 'edrs_mongo_admin'),
        'password': os.getenv('MONGO_PASSWORD', 'LocalMongo123!@#'),
        'authentication_source': 'admin',
        'authentication_mechanism': 'SCRAM-SHA-1',
    }
}

# =================================================================
# 🔄 CACHE CONFIGURATION
# =================================================================

# Redis Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://:{os.getenv('REDIS_PASSWORD', 'LocalRedis123!@#')}@{os.getenv('REDIS_HOST', 'redis')}:{os.getenv('REDIS_PORT', '6379')}/0",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': 'edrs_local',
        'TIMEOUT': 300,
    }
}

# =================================================================
# 🧪 DEVELOPMENT TOOLS
# =================================================================

# Django Debug Toolbar
if os.getenv('ENABLE_DEBUG_TOOLBAR', 'True').lower() == 'true':
    INSTALLED_APPS += [
        'debug_toolbar',
    ]
    
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]
    
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        'SHOW_TEMPLATE_CONTEXT': True,
    }
    
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]

# Django Extensions
if os.getenv('ENABLE_DJANGO_EXTENSIONS', 'True').lower() == 'true':
    INSTALLED_APPS += [
        'django_extensions',
    ]

# =================================================================
# 📧 EMAIL CONFIGURATION
# =================================================================

# Console Email Backend for local development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False').lower() == 'true'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@edrs.local')

# =================================================================
# 📁 STATIC & MEDIA FILES
# =================================================================

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staticfiles'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# =================================================================
# 📊 LOGGING CONFIGURATION
# =================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'colored': {
            'format': '\033[92m{asctime}\033[0m [\033[94m{levelname}\033[0m] \033[95m{name}\033[0m: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'edrs.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': os.getenv('SQL_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'edrs': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# =================================================================
# 🔍 API DOCUMENTATION
# =================================================================

# Swagger UI Configuration
if os.getenv('ENABLE_SWAGGER_UI', 'True').lower() == 'true':
    SWAGGER_SETTINGS = {
        'SHOW_EXTENSIONS': True,
        'SHOW_COMMON_EXTENSIONS': True,
        'USE_SESSION_AUTH': True,
        'LOGIN_URL': '/admin/login/',
        'LOGOUT_URL': '/admin/logout/',
        'PERSIST_AUTH': True,
        'REFETCH_SCHEMA_WITH_AUTH': True,
        'DEFAULT_INFO': 'core.urls.api_info',
    }

# =================================================================
# 🚀 PERFORMANCE SETTINGS
# =================================================================

# Database Query Optimization
if os.getenv('ENABLE_QUERY_DEBUGGING', 'True').lower() == 'true':
    LOGGING['loggers']['django.db.backends'] = {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    }

# Disable migrations for faster testing
if 'test' in sys.argv or os.getenv('TESTING', 'False').lower() == 'true':
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
    DATABASES['default']['NAME'] = ':memory:'
    
    class DisableMigrations:
        def __contains__(self, item):
            return True
        def __getitem__(self, item):
            return None
    
    MIGRATION_MODULES = DisableMigrations()

# =================================================================
# 🔧 DEVELOPMENT MIDDLEWARE
# =================================================================

if os.getenv('ENABLE_DEV_MIDDLEWARE', 'True').lower() == 'true':
    MIDDLEWARE += [
        'core.middleware.local_dev_middleware',
    ]

# =================================================================
# 🧪 FEATURE FLAGS
# =================================================================

# Development Feature Flags
FEATURE_FLAGS = {
    'ENABLE_API_VERSIONING': os.getenv('ENABLE_API_VERSIONING', 'True').lower() == 'true',
    'ENABLE_RATE_LIMITING': os.getenv('ENABLE_RATE_LIMITING', 'False').lower() == 'true',
    'ENABLE_AUTHENTICATION': os.getenv('ENABLE_AUTHENTICATION', 'True').lower() == 'true',
    'ENABLE_PERMISSIONS': os.getenv('ENABLE_PERMISSIONS', 'True').lower() == 'true',
    'ENABLE_MOCK_DATA': os.getenv('ENABLE_MOCK_DATA', 'True').lower() == 'true',
    'ENABLE_TEST_ENDPOINTS': os.getenv('ENABLE_TEST_ENDPOINTS', 'True').lower() == 'true',
}

# =================================================================
# 📦 THIRD-PARTY CONFIGURATIONS
# =================================================================

# OpenAI Configuration (Local Development)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))

# OpenAI Settings
OPENAI_SETTINGS = {
    'api_key': OPENAI_API_KEY,
    'model': OPENAI_MODEL,
    'max_tokens': OPENAI_MAX_TOKENS,
    'temperature': OPENAI_TEMPERATURE,
    'enabled': os.getenv('ENABLE_OPENAI_INTEGRATION', 'True').lower() == 'true',
}

# Django REST Framework (Development Settings)
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Enable browsable API
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/hour',
        'user': '2000/hour'
    } if not FEATURE_FLAGS.get('ENABLE_RATE_LIMITING') else REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES', {}),
})

# =================================================================
# 🔍 HEALTH CHECKS
# =================================================================

# Health Check Configuration
HEALTH_CHECKS = {
    'database': True,
    'cache': True,
    'storage': True,
}

# =================================================================
# 📝 LOCAL DEVELOPMENT NOTES
# =================================================================

print("🚀 EDRS Local Development Environment Loaded")
print(f"📊 Database: {DATABASES['default']['NAME']} @ {DATABASES['default']['HOST']}")
print(f"🔄 Cache: Redis @ {CACHES['default']['LOCATION']}")
print(f"🌐 Debug Mode: {DEBUG}")
print(f"🔧 Environment: {ENVIRONMENT}")
print("=" * 60)