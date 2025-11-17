from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
# from apps.core.simple_upload import upload_view  # Import when needed

# Health check view
def health_check(request):
    """Simple health check endpoint for Railway"""
    return JsonResponse({'status': 'ok', 'service': 'EDRS Backend', 'timestamp': str(datetime.now())})

# Simple upload endpoint for testing
def simple_upload_test(request):
    """Simple upload endpoint for testing"""
    if request.method == 'POST':
        return JsonResponse({'message': 'Upload endpoint working', 'method': 'POST'})
    return JsonResponse({'message': 'Upload endpoint ready', 'method': 'GET'})

urlpatterns = [
    # Health check (for Railway deployment)
    path('health/', health_check, name='health_check'),
    
    # Simple upload test endpoint
    path('api/core/upload-document/', csrf_exempt(simple_upload_test), name='simple_upload_test'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Routes
    # path('api/auth/', include('apps.authentication.urls')),  # Disabled temporarily
    # path('api/users/', include('apps.users.urls')),          # Disabled temporarily
    # path('api/core/', include('apps.core.urls')),            # Disabled temporarily - causing 500 errors
    # path('api/ai/', include('apps.ai.urls')),                # Disabled temporarily
    
    # Simple contact form (disabled for deployment)
    # path('api/contact/submit/', simple_contact_submit, name='simple-contact-submit'),
    
    # PID Analysis (temporarily disabled for debugging)
    # path('api/', include('apps.pid_analysis.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar
    try:
        import debug_toolbar
        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    except ImportError:
        pass