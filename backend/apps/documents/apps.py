"""
Django App Configuration for EDRS Documents
"""
from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.documents'
    verbose_name = 'EDRS Document Management'
    
    def ready(self):
        """Import signal handlers when the app is ready"""
        try:
            import apps.documents.signals
        except ImportError:
            pass