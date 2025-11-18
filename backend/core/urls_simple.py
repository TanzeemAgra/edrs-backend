"""
Simplified URL configuration with basic upload functionality
"""
from django.http import JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

def health(request):
    return JsonResponse({"status": "alive", "message": "EDRS Backend is working"})

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def upload_document(request):
    """Simplified document upload endpoint"""
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    
    if request.method == 'POST':
        try:
            # Get uploaded files from request
            uploaded_files = request.FILES.getlist('files')
            
            if not uploaded_files:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No files uploaded'
                }, status=400)
            
            # Process files (for now, just return info about them)
            file_info = []
            for file in uploaded_files:
                file_info.append({
                    'name': file.name,
                    'size': file.size,
                    'content_type': getattr(file, 'content_type', 'unknown'),
                })
            
            return JsonResponse({
                'status': 'success',
                'message': f'Successfully received {len(uploaded_files)} file(s)',
                'files': file_info,
                'upload_id': 'temp-upload-id-123'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Upload failed: {str(e)}'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

urlpatterns = [
    path('health/', health, name='health'),
    path('api/core/upload-document/', upload_document, name='upload_document'),
]