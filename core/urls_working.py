"""
Working URL configuration with upload functionality
"""
from django.http import JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import json

def health(request):
    return JsonResponse({"status": "alive", "message": "EDRS Backend is working"})

@csrf_exempt
@api_view(['POST', 'OPTIONS'])
@parser_classes([MultiPartParser, FormParser])
def upload_document(request):
    """Document upload endpoint"""
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    
    if request.method == 'POST':
        try:
            # Get uploaded files
            uploaded_files = request.FILES.getlist('files')
            
            if not uploaded_files:
                return Response({
                    'status': 'error',
                    'message': 'No files uploaded'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Process files (for now, just return info about them)
            file_info = []
            for file in uploaded_files:
                file_info.append({
                    'name': file.name,
                    'size': file.size,
                    'content_type': file.content_type,
                })
            
            return Response({
                'status': 'success',
                'message': f'Successfully received {len(uploaded_files)} file(s)',
                'files': file_info,
                'upload_id': 'temp-upload-id-123'  # Temporary ID
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Upload failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

urlpatterns = [
    path('health/', health, name='health'),
    path('api/core/upload-document/', upload_document, name='upload_document'),
]