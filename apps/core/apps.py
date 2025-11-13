from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'
    
    def ready(self):
        """Initialize MongoDB connection when Django starts"""
        import mongoengine
        from django.conf import settings
        
        if hasattr(settings, 'MONGODB_SETTINGS'):
            try:
                mongoengine.connect(**settings.MONGODB_SETTINGS)
            except Exception as e:
                print(f"MongoDB connection failed: {e}")
                # Don't crash the app if MongoDB is not available