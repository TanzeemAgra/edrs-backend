"""
EDRS Document Library Views
API endpoints for accessing and managing user documents with role-based access
"""

from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.core.paginator import Paginator
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from datetime import datetime, timedelta
import os

from ..models import PIDProject, PIDDiagram
from ..serializers import PIDProjectSerializer, PIDDiagramSerializer
from core.storage import get_user_role_folder, get_rejlers_file_path


class DocumentLibraryView(APIView):
    """
    Document Library API for Rejlers Abu Dhabi
    Provides role-based access to user documents and projects
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get user's document library with filtering and search
        """
        user = request.user
        
        # Get query parameters
        search = request.GET.get('search', '')
        project_type = request.GET.get('project_type', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        document_type = request.GET.get('document_type', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        # Base query - user's projects and accessible projects
        projects_query = Q(created_by=user)
        
        # Add role-based access
        user_role = get_user_role_folder(user)
        if user_role in ['administrators', 'project-managers']:
            # Admins and PMs can see all projects
            projects_query = Q()
        elif user_role == 'lead-engineers':
            # Lead engineers can see their projects and their team's projects
            projects_query |= Q(created_by__groups__name__in=['Process Engineer', 'Design Engineer'])
        
        # Filter projects
        projects = PIDProject.objects.filter(projects_query)
        
        if search:
            projects = projects.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(field_name__icontains=search)
            )
        
        if project_type:
            projects = projects.filter(project_type=project_type)
        
        if date_from:
            projects = projects.filter(created_at__gte=date_from)
        
        if date_to:
            projects = projects.filter(created_at__lte=date_to)
        
        # Get diagrams with document type filter
        diagrams_query = Q(project__in=projects)
        
        if document_type:
            if document_type == 'pdf':
                diagrams_query &= Q(original_file__endswith='.pdf')
            elif document_type == 'dwg':
                diagrams_query &= Q(original_file__endswith='.dwg')
            elif document_type == 'images':
                diagrams_query &= Q(original_file__regex=r'.*\.(png|jpg|jpeg|tiff)$')
        
        diagrams = PIDDiagram.objects.filter(diagrams_query).select_related('project')
        
        # Paginate results
        paginator = Paginator(diagrams, per_page)
        page_obj = paginator.get_page(page)
        
        # Serialize data
        diagram_data = []
        for diagram in page_obj:
            diagram_info = {
                'id': str(diagram.id),
                'name': diagram.name,
                'drawing_number': diagram.drawing_number,
                'drawing_title': diagram.drawing_title,
                'diagram_type': diagram.get_diagram_type_display(),
                'revision': diagram.revision,
                'file_url': diagram.original_file.url if diagram.original_file else None,
                'file_size': diagram.file_size,
                'created_at': diagram.created_at,
                'updated_at': diagram.updated_at,
                'status': diagram.get_status_display(),
                'project': {
                    'id': str(diagram.project.id),
                    'name': diagram.project.name,
                    'project_type': diagram.project.get_project_type_display(),
                    'field_name': diagram.project.field_name,
                },
                'analysis_summary': {
                    'total_errors': diagram.total_errors_found,
                    'critical_errors': diagram.critical_errors,
                    'high_priority_errors': diagram.high_priority_errors,
                    'medium_priority_errors': diagram.medium_priority_errors,
                }
            }
            diagram_data.append(diagram_info)
        
        # Get summary statistics
        stats = {
            'total_projects': projects.count(),
            'total_documents': diagrams.count(),
            'documents_by_type': {
                'pdf': diagrams.filter(original_file__endswith='.pdf').count(),
                'dwg': diagrams.filter(original_file__endswith='.dwg').count(),
                'images': diagrams.filter(original_file__regex=r'.*\.(png|jpg|jpeg|tiff)$').count(),
            },
            'recent_uploads': diagrams.filter(
                created_at__gte=datetime.now() - timedelta(days=7)
            ).count(),
        }
        
        return Response({
            'success': True,
            'documents': diagram_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginator.count,
                'pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            },
            'statistics': stats,
            'filters': {
                'project_types': [
                    {'value': choice[0], 'label': choice[1]}
                    for choice in PIDProject.PROJECT_TYPES
                ],
                'document_types': [
                    {'value': 'pdf', 'label': 'PDF Documents'},
                    {'value': 'dwg', 'label': 'AutoCAD Files'},
                    {'value': 'images', 'label': 'Image Files'},
                ],
                'user_role': user_role,
            }
        })


class S3DocumentBrowserView(APIView):
    """
    Browse S3 documents directly for advanced users
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Browse S3 bucket structure for user's accessible folders
        """
        user = request.user
        user_role = get_user_role_folder(user)
        
        # Only allow certain roles to browse S3 directly
        if user_role not in ['administrators', 'project-managers', 'lead-engineers']:
            return Response({
                'success': False,
                'message': 'Insufficient permissions for S3 browsing'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Get folder prefix based on user role
            root_folder = getattr(settings, 'AWS_S3_ROOT_FOLDER', 'rejlers-abudhabi')
            
            if user_role == 'administrators':
                prefix = f"{root_folder}/"
            elif user_role == 'project-managers':
                prefix = f"{root_folder}/project-managers/"
            else:
                user_id = str(user.id)
                prefix = f"{root_folder}/{user_role}/{user_id}/"
            
            # List objects in S3
            response = s3_client.list_objects_v2(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Prefix=prefix,
                Delimiter='/'
            )
            
            folders = []
            files = []
            
            # Process common prefixes (folders)
            for prefix_info in response.get('CommonPrefixes', []):
                folder_name = prefix_info['Prefix'].rstrip('/').split('/')[-1]
                folders.append({
                    'name': folder_name,
                    'path': prefix_info['Prefix'],
                    'type': 'folder'
                })
            
            # Process objects (files)
            for obj in response.get('Contents', []):
                if not obj['Key'].endswith('/'):  # Skip folder markers
                    file_name = obj['Key'].split('/')[-1]
                    files.append({
                        'name': file_name,
                        'path': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'type': 'file'
                    })
            
            return Response({
                'success': True,
                'current_path': prefix,
                'folders': folders,
                'files': files,
                'user_role': user_role
            })
            
        except ClientError as e:
            return Response({
                'success': False,
                'message': f'S3 access error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DownloadDocumentView(APIView):
    """
    Generate secure download URLs for documents
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Generate signed URL for document download
        """
        user = request.user
        document_id = request.data.get('document_id')
        s3_key = request.data.get('s3_key')
        
        if not document_id and not s3_key:
            return Response({
                'success': False,
                'message': 'Document ID or S3 key required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # If document_id provided, get from database
            if document_id:
                diagram = PIDDiagram.objects.get(id=document_id)
                
                # Check access permissions
                user_role = get_user_role_folder(user)
                if not (diagram.project.created_by == user or 
                       user_role in ['administrators', 'project-managers'] or
                       (user_role == 'lead-engineers' and 
                        diagram.project.created_by.groups.filter(
                            name__in=['Process Engineer', 'Design Engineer']
                        ).exists())):
                    return Response({
                        'success': False,
                        'message': 'Access denied'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                file_url = diagram.original_file.url
                filename = os.path.basename(diagram.original_file.name)
            
            # If S3 key provided, generate direct URL
            else:
                # Verify user has access to this S3 path
                user_role = get_user_role_folder(user)
                root_folder = getattr(settings, 'AWS_S3_ROOT_FOLDER', 'rejlers-abudhabi')
                
                allowed_prefixes = [f"{root_folder}/{user_role}/{user.id}/"]
                if user_role in ['administrators', 'project-managers']:
                    allowed_prefixes.append(f"{root_folder}/")
                elif user_role == 'lead-engineers':
                    allowed_prefixes.extend([
                        f"{root_folder}/process-engineers/",
                        f"{root_folder}/design-engineers/"
                    ])
                
                if not any(s3_key.startswith(prefix) for prefix in allowed_prefixes):
                    return Response({
                        'success': False,
                        'message': 'Access denied to this file'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Generate presigned URL
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )
                
                file_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': s3_key},
                    ExpiresIn=3600  # 1 hour
                )
                filename = os.path.basename(s3_key)
            
            return Response({
                'success': True,
                'download_url': file_url,
                'filename': filename,
                'expires_in': 3600
            })
            
        except PIDDiagram.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Document not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error generating download URL: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_storage_stats(request):
    """
    Get user's storage usage statistics
    """
    user = request.user
    user_role = get_user_role_folder(user)
    
    # Get user's projects and diagrams
    if user_role in ['administrators', 'project-managers']:
        projects = PIDProject.objects.all()
    else:
        projects = PIDProject.objects.filter(created_by=user)
    
    diagrams = PIDDiagram.objects.filter(project__in=projects)
    
    # Calculate storage usage
    total_files = diagrams.count()
    total_size = sum(d.file_size or 0 for d in diagrams)
    
    # Group by file types
    file_types = {}
    for diagram in diagrams:
        if diagram.original_file:
            ext = diagram.original_file.name.split('.')[-1].lower()
            if ext not in file_types:
                file_types[ext] = {'count': 0, 'size': 0}
            file_types[ext]['count'] += 1
            file_types[ext]['size'] += diagram.file_size or 0
    
    # Recent activity
    recent_uploads = diagrams.filter(
        created_at__gte=datetime.now() - timedelta(days=30)
    ).order_by('-created_at')[:10]
    
    return Response({
        'success': True,
        'storage_stats': {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'projects_count': projects.count(),
            'file_types': file_types,
        },
        'recent_activity': [
            {
                'id': str(d.id),
                'name': d.name,
                'project_name': d.project.name,
                'uploaded_at': d.created_at,
                'file_size': d.file_size,
            }
            for d in recent_uploads
        ],
        'user_role': user_role,
        's3_folder_path': f"rejlers-abudhabi/{user_role}/{user.id}"
    })