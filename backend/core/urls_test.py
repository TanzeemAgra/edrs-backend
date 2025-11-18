"""
Ultra-simple URL configuration for testing
"""
from django.http import JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

def health(request):
    return JsonResponse({"status": "alive", "message": "EDRS Backend is working"})

@csrf_exempt
def simple_upload(request):
    """Ultra-simple upload test endpoint"""
    return JsonResponse({
        'status': 'success',
        'message': 'Upload endpoint is reachable',
        'method': request.method,
        'path': request.path
    })

urlpatterns = [
    path('health/', health, name='health'),
    path('api/core/upload-document/', simple_upload, name='upload_document'),
]