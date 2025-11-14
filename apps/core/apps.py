from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'
    
    def ready(self):
        """Initialize MongoDB connection when Django starts"""
        try:
            import mongoengine
            from django.conf import settings
            
            if hasattr(settings, 'MONGODB_SETTINGS'):
                try:
                    # Add connection timeout and retry logic
                    mongodb_settings = settings.MONGODB_SETTINGS.copy()
                    mongodb_settings.update({
                        'connect': False,  # Lazy connection - only connect when needed
                        'serverSelectionTimeoutMS': 5000,
                        'connectTimeoutMS': 5000,
                        'maxPoolSize': 10,
                        'retryWrites': True
                    })
                    
                    # Disconnect any existing connections first
                    mongoengine.disconnect()
                    mongoengine.connect(**mongodb_settings)
                    print("✅ MongoDB connection initialized successfully")
                    
                except Exception as e:
                    print(f"⚠️  MongoDB connection failed: {e}")
                    print("💡 This is normal if MongoDB service is not running")
                    # Don't crash the app if MongoDB is not available
            else:
                print("⚠️  MongoDB settings not configured")
                
        except ImportError:
            print("⚠️  mongoengine not installed - MongoDB features disabled")
            # Don't crash if mongoengine is not available