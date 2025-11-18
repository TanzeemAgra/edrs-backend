"""
EDRS URL Configuration with Authentication
"""
from django.http import JsonResponse
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json

def health(request):
    """Health check endpoint"""
    return JsonResponse({
        "status": "alive", 
        "message": "EDRS Backend is working",
        "environment": "local"
    })

@csrf_exempt
@api_view(['POST', 'OPTIONS'])
def login_view(request):
    """Simple login endpoint for local development"""
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
    
    try:
        data = json.loads(request.body) if request.body else {}
        email = data.get('email', '')
        password = data.get('password', '')
        
        # Simple validation for local development
        if email and password:
            # In a real app, you'd validate credentials here
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'user': {
                    'id': 1,
                    'email': email,
                    'name': 'Test User',
                },
                'token': 'local-dev-token-12345'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except json.JSONDecodeError:
        return Response({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Login failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET', 'OPTIONS'])
def user_view(request):
    """Simple user endpoint for local development"""
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
    
    # For local development, return a mock user
    return Response({
        'id': 1,
        'email': 'tanzeem@rejlers.ae',
        'username': 'tanzeem',
        'first_name': 'Tanzeem',
        'last_name': 'Agra',
        'full_name': 'Tanzeem Agra',
        'is_active': True,
        'is_staff': True
    }, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST', 'OPTIONS'])
def upload_document(request):
    """Document upload endpoint"""
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
    
    try:
        uploaded_files = request.FILES.getlist('files')
        
        if not uploaded_files:
            return Response({
                'status': 'error',
                'message': 'No files uploaded'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        file_info = []
        for file in uploaded_files:
            file_info.append({
                'name': file.name,
                'size': file.size,
                'content_type': getattr(file, 'content_type', 'unknown'),
            })
        
        return Response({
            'status': 'success',
            'message': f'Successfully received {len(uploaded_files)} file(s)',
            'files': file_info,
            'upload_id': 'local-upload-id-123'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Upload failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

urlpatterns = [
    path('health/', health, name='health'),
    path('api/auth/login/', login_view, name='login'),
    path('api/auth/user/', user_view, name='user'),
    path('api/core/upload-document/', upload_document, name='upload_document'),
    
    # Document Management API
    path('api/documents/', include('apps.documents.urls')),
]

# Serve media files in development
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)