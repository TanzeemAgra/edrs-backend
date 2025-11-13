# This file makes Python treat the directory as a package
import mongoengine
from django.conf import settings

# Initialize MongoDB connection
def connect_mongodb():
    """Initialize MongoDB connection using mongoengine"""
    if hasattr(settings, 'MONGODB_SETTINGS'):
        try:
            mongoengine.connect(**settings.MONGODB_SETTINGS)
        except Exception as e:
            print(f"MongoDB connection failed: {e}")

# Auto-connect when the package is imported
try:
    connect_mongodb()
except Exception:
    # Don't fail if MongoDB is not available during initial setup
    pass