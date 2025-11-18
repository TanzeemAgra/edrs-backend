"""
Simple Document Upload API for EDRS
Temporary solution while PID analysis app is being debugged
"""
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import uuid
from datetime import datetime
import json

@api_view(['POST'])
@permission_classes([])  # Temporarily allow unauthenticated access for debugging
@parser_classes([MultiPartParser, FormParser])
def simple_document_upload(request):
    """
    Simple document upload endpoint
    
    POST /api/core/upload-document/
    
    Expected form data:
    - file: The document file
    - project_name: Name of the project
    - document_type: Type of document (e.g., 'pid-diagram', 'document')
    - drawing_number: Optional drawing number
    - drawing_title: Optional drawing title
    """
    
    if 'file' not in request.FILES:
        return Response({
            'error': 'No file provided',
            'message': 'Please select a file to upload'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    uploaded_file = request.FILES['file']
    
    # Validate file type
    allowed_extensions = ['.pdf', '.dwg', '.png', '.jpg', '.jpeg', '.tiff', '.tif']
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    
    if file_ext not in allowed_extensions:
        return Response({
            'error': 'File type not supported',
            'message': f'Please upload files with extensions: {", ".join(allowed_extensions)}',
            'allowed_types': allowed_extensions
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file size (max 50MB)
    max_size = 50 * 1024 * 1024  # 50MB
    if uploaded_file.size > max_size:
        return Response({
            'error': 'File too large',
            'message': f'File size must be less than {max_size // (1024*1024)}MB',
            'max_size_mb': max_size // (1024*1024)
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get metadata from request
    project_name = request.data.get('project_name', 'Default Project')
    document_type = request.data.get('document_type', 'document')
    drawing_number = request.data.get('drawing_number', '')
    drawing_title = request.data.get('drawing_title', uploaded_file.name)
    
    # Generate unique filename
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_filename = f"{timestamp}_{unique_id}_{uploaded_file.name}"
    
    # Create organized file path - handle both authenticated and unauthenticated users
    user_id = request.user.id if request.user.is_authenticated else 'anonymous'
    user_email = request.user.email if request.user.is_authenticated else 'anonymous@example.com'
    user_name = f"{request.user.first_name} {request.user.last_name}".strip() if request.user.is_authenticated else 'Anonymous User'
    year_month = datetime.now().strftime('%Y/%m')
    
    # Organize files by user and date
    file_path = f"uploads/users/{user_id}/{document_type}/{year_month}/{safe_filename}"
    
    try:
        # Save file using Django's default storage
        stored_path = default_storage.save(file_path, ContentFile(uploaded_file.read()))
        
        # Generate file URL
        if hasattr(settings, 'USE_S3') and settings.USE_S3:
            # S3 URL generation
            file_url = default_storage.url(stored_path)
            storage_type = 'aws-s3'
        else:
            # Local file URL
            file_url = f"{settings.MEDIA_URL}{stored_path}"
            storage_type = 'local'
        
        # Create response with document info
        document_info = {
            'success': True,
            'message': 'Document uploaded successfully!',
            'document': {
                'id': unique_id,
                'filename': uploaded_file.name,
                'safe_filename': safe_filename,
                'file_url': file_url,
                'file_path': stored_path,
                'file_size': uploaded_file.size,
                'file_type': file_ext,
                'project_name': project_name,
                'document_type': document_type,
                'drawing_number': drawing_number,
                'drawing_title': drawing_title,
                'uploaded_by': {
                    'id': user_id,
                    'email': user_email,
                    'name': user_name
                },
                'uploaded_at': datetime.now().isoformat(),
                'storage_type': storage_type
            }
        }
        
        # Log upload for analytics
        print(f"📄 Document uploaded: {uploaded_file.name} by {user_email}")
        
        return Response(document_info, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': 'Upload failed',
            'message': f'Failed to save file: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])  # Temporarily allow unauthenticated access for debugging
def list_user_documents(request):
    """
    List user's uploaded documents
    
    GET /api/core/my-documents/
    """
    
    user_id = request.user.id if request.user.is_authenticated else 'anonymous'
    user_email = request.user.email if request.user.is_authenticated else 'anonymous@example.com'
    
    try:
        # For now, return a simple message since we don't have a database model
        # In production, you'd query a Document model here
        
        return Response({
            'message': f'Documents for user {user_email}',
            'user_id': user_id,
            'note': 'Document listing requires database model implementation',
            'upload_endpoint': '/api/core/upload-document/',
            'supported_types': ['.pdf', '.dwg', '.png', '.jpg', '.jpeg', '.tiff', '.tif'],
            'max_size_mb': 50
        })
        
    except Exception as e:
        return Response({
            'error': 'Failed to list documents',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])  # Temporarily allow unauthenticated access for debugging
def test_s3_connection(request):
    """
    Test AWS S3 connection and configuration
    
    GET /api/core/test-s3/
    """
    
    # Check S3 configuration
    s3_config = {
        'USE_S3': getattr(settings, 'USE_S3', False),
        'AWS_ACCESS_KEY_ID': bool(getattr(settings, 'AWS_ACCESS_KEY_ID', None)),
        'AWS_SECRET_ACCESS_KEY': bool(getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)),
        'AWS_STORAGE_BUCKET_NAME': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'not-configured'),
        'AWS_S3_REGION_NAME': getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1'),
        'DEFAULT_FILE_STORAGE': getattr(settings, 'DEFAULT_FILE_STORAGE', 'django.core.files.storage.FileSystemStorage')
    }
    
    # Test S3 connection if configured
    s3_status = 'not-configured'
    if s3_config['USE_S3'] and s3_config['AWS_ACCESS_KEY_ID']:
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError, ClientError
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Try to list buckets
            response = s3_client.list_buckets()
            s3_status = 'connected'
            
        except NoCredentialsError:
            s3_status = 'credentials-invalid'
        except ClientError as e:
            s3_status = f'connection-failed: {e}'
        except ImportError:
            s3_status = 'boto3-not-installed'
        except Exception as e:
            s3_status = f'error: {e}'
    
    return Response({
        'storage_status': {
            'current_storage': 'AWS S3' if s3_config['USE_S3'] else 'Local File System',
            's3_connection_status': s3_status,
            'configuration': s3_config
        },
        'upload_info': {
            'upload_endpoint': '/api/core/upload-document/',
            'supported_formats': ['.pdf', '.dwg', '.png', '.jpg', '.jpeg', '.tiff', '.tif'],
            'max_file_size_mb': 50,
            'file_organization': 'uploads/users/{user_id}/{document_type}/{year}/{month}/'
        },
        'recommendations': {
            'for_production': 'Configure AWS S3 for scalable file storage',
            'contact': 'Rejlers Abu Dhabi IT team for AWS credentials'
        } if s3_status != 'connected' else None
    })