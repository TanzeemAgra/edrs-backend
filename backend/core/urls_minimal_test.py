"""
Ultra-minimal URL configuration for Railway deployment test
"""

from django.http import JsonResponse
from django.urls import path


def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({"status": "ok", "message": "Backend is working"})


def test_upload(request):
    """Test upload endpoint"""
    if request.method == 'POST':
        return JsonResponse({"status": "success", "message": "Upload received"})
    return JsonResponse({"status": "ready", "message": "Upload endpoint ready"})


urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('api/test-upload/', test_upload, name='test_upload'),
]