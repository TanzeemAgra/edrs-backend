"""
API Views for EDRS Document Management System
Complete REST API for document upload, analysis, and reporting
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponse, Http404
import os
import hashlib
from datetime import timedelta

from .models import Project, Document, Analysis, Report, AnalysisSession
from .serializers import (
    ProjectSerializer, DocumentSerializer, DocumentListSerializer,
    AnalysisSerializer, AnalysisListSerializer, ReportSerializer,
    AnalysisSessionSerializer, DocumentUploadSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# Project Views
class ProjectListCreateView(generics.ListCreateAPIView):
    """List all projects or create a new project"""
    serializer_class = ProjectSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.AllowAny]  # Temporarily allow unauthenticated access
    
    def get_queryset(self):
        # Handle anonymous users for development
        if self.request.user.is_anonymous:
            queryset = Project.objects.all()
        else:
            queryset = Project.objects.filter(created_by=self.request.user)
        
        # Filter by project type
        project_type = self.request.query_params.get('project_type')
        if project_type:
            queryset = queryset.filter(project_type=project_type)
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Search in name, client, or project number
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(client_name__icontains=search) |
                Q(project_number__icontains=search)
            )
        
        return queryset.order_by('-created_at')


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a project"""
    serializer_class = ProjectSerializer
    permission_classes = [permissions.AllowAny]  # Temporarily allow unauthenticated access
    
    def get_queryset(self):
        # Handle anonymous users for development
        if self.request.user.is_anonymous:
            return Project.objects.all()
        else:
            return Project.objects.filter(created_by=self.request.user)


# Document Views
class DocumentListCreateView(generics.ListCreateAPIView):
    """List all documents or upload a new document"""
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.AllowAny]  # Temporarily allow unauthenticated access
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentUploadSerializer
        return DocumentListSerializer
    
    def get_queryset(self):
        # Handle unauthenticated users for testing
        if self.request.user.is_authenticated:
            user = self.request.user
        else:
            from django.contrib.auth.models import User
            user, created = User.objects.get_or_create(username='tanzeem')
        
        queryset = Document.objects.filter(
            project__created_by=user
        ).select_related('project', 'uploaded_by')
        
        # Filter by project
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by document type
        document_type = self.request.query_params.get('document_type')
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Search in title, drawing number, or filename
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(drawing_number__icontains=search) |
                Q(original_filename__icontains=search)
            )
        
        return queryset.order_by('-uploaded_at')
    
    def perform_create(self, serializer):
        # Calculate file hash
        file_obj = serializer.validated_data['file']
        file_obj.seek(0)
        file_hash = hashlib.sha256(file_obj.read()).hexdigest()
        file_obj.seek(0)
        
        # Save with additional computed fields
        document = serializer.save(
            file_size=file_obj.size,
            file_hash=file_hash
        )
        
        # Mark as ready for processing
        document.status = 'ready'
        document.processed_at = timezone.now()
        document.save()


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a document"""
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Document.objects.filter(
            project__created_by=self.request.user
        ).select_related('project', 'uploaded_by')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Temporarily allow unauthenticated access
def download_document(request, document_id):
    """Download a document file"""
    try:
        # Handle anonymous users for development
        if request.user.is_anonymous:
            document = Document.objects.get(id=document_id)
        else:
            document = Document.objects.get(
                id=document_id,
                project__created_by=request.user
            )
        
        if document.file and os.path.exists(document.file.path):
            return FileResponse(
                document.file,
                as_attachment=True,
                filename=document.original_filename
            )
        else:
            return Response(
                {'error': 'File not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    except Document.DoesNotExist:
        return Response(
            {'error': 'Document not found'},
            status=status.HTTP_404_NOT_FOUND
        )


# Analysis Views
class AnalysisListCreateView(generics.ListCreateAPIView):
    """List all analyses or start a new analysis"""
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.AllowAny]  # Temporarily allow unauthenticated access
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AnalysisSerializer
        return AnalysisListSerializer
    
    def get_queryset(self):
        # Handle unauthenticated users for testing
        if self.request.user.is_authenticated:
            user = self.request.user
        else:
            from django.contrib.auth.models import User
            user, created = User.objects.get_or_create(username='tanzeem')
        
        queryset = Analysis.objects.filter(
            document__project__created_by=user
        ).select_related('document', 'started_by')
        
        # Filter by document
        document_id = self.request.query_params.get('document')
        if document_id:
            queryset = queryset.filter(document_id=document_id)
        
        # Filter by analysis type
        analysis_type = self.request.query_params.get('analysis_type')
        if analysis_type:
            queryset = queryset.filter(analysis_type=analysis_type)
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        # Start analysis with basic configuration
        analysis = serializer.save(
            status='queued',
            started_at=timezone.now()
        )
        
        # In a real implementation, you would queue this for background processing
        # For now, we'll create a mock successful analysis
        self._create_mock_analysis_results(analysis)
    
    def _create_mock_analysis_results(self, analysis):
        """Create mock analysis results for demonstration"""
        import json
        
        mock_results = {
            'symbols_detected': [
                {'type': 'valve', 'confidence': 0.95, 'coordinates': [100, 200]},
                {'type': 'pump', 'confidence': 0.89, 'coordinates': [300, 400]},
            ],
            'equipment_identified': [
                {'tag': 'P-001', 'type': 'pump', 'confidence': 0.92},
                {'tag': 'V-001', 'type': 'valve', 'confidence': 0.88},
            ],
            'piping_connections': [
                {'from': 'P-001', 'to': 'V-001', 'line_size': '6"'},
            ]
        }
        
        mock_equipment = [
            {'tag': 'P-001', 'type': 'Centrifugal Pump', 'coordinates': [300, 400]},
            {'tag': 'V-001', 'type': 'Gate Valve', 'coordinates': [100, 200]},
        ]
        
        mock_issues = [
            {
                'type': 'missing_tag',
                'description': 'Valve at coordinates (150, 250) missing equipment tag',
                'severity': 'medium',
                'coordinates': [150, 250]
            }
        ]
        
        mock_recommendations = [
            {
                'category': 'labeling',
                'description': 'Add equipment tags to all valves for better traceability',
                'priority': 'medium'
            }
        ]
        
        # Update analysis with results
        analysis.status = 'completed'
        analysis.confidence_level = 'high'
        analysis.results = mock_results
        analysis.equipment_detected = mock_equipment
        analysis.issues_found = mock_issues
        analysis.recommendations = mock_recommendations
        analysis.summary = f"Analysis completed successfully. Found {len(mock_equipment)} equipment items and {len(mock_issues)} issues."
        analysis.processing_time = 2.5  # Mock processing time
        analysis.completed_at = timezone.now()
        analysis.save()


class AnalysisDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an analysis"""
    serializer_class = AnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Analysis.objects.filter(
            document__project__created_by=self.request.user
        )


# Report Views
class ReportListCreateView(generics.ListCreateAPIView):
    """List all reports or generate a new report"""
    serializer_class = ReportSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.AllowAny]  # Temporarily allow unauthenticated access
    
    def get_queryset(self):
        # Handle unauthenticated users for testing
        if self.request.user.is_authenticated:
            user = self.request.user
        else:
            from django.contrib.auth.models import User
            user, created = User.objects.get_or_create(username='tanzeem')
        
        queryset = Report.objects.filter(
            project__created_by=user
        ).select_related('project', 'generated_by')
        
        # Filter by project
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by report type
        report_type = self.request.query_params.get('report_type')
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        # Generate report
        report = serializer.save(status='generating')
        
        # In a real implementation, this would be done in background
        self._generate_mock_report(report)
    
    def _generate_mock_report(self, report):
        """Generate a mock report for demonstration"""
        mock_content = {
            'executive_summary': 'Project analysis completed successfully.',
            'total_documents': report.project.documents.count(),
            'total_analyses': Analysis.objects.filter(document__project=report.project).count(),
            'equipment_summary': {
                'pumps': 3,
                'valves': 12,
                'instruments': 8
            },
            'issues_summary': {
                'high': 1,
                'medium': 5,
                'low': 2
            },
            'recommendations': [
                'Complete missing equipment tags',
                'Review valve specifications',
                'Update P&ID legends'
            ]
        }
        
        report.status = 'ready'
        report.content = mock_content
        report.generation_time = 1.2
        report.completed_at = timezone.now()
        report.save()


class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a report"""
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Report.objects.filter(
            project__created_by=self.request.user
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_report(request, report_id):
    """Download a generated report file"""
    try:
        report = Report.objects.get(
            id=report_id,
            project__created_by=request.user
        )
        
        if report.file and os.path.exists(report.file.path):
            return FileResponse(
                report.file,
                as_attachment=True,
                filename=f"{report.title}.{report.format}"
            )
        else:
            # If no file exists, return JSON content
            return Response(report.content)
    except Report.DoesNotExist:
        return Response(
            {'error': 'Report not found'},
            status=status.HTTP_404_NOT_FOUND
        )


# Analysis Session Views
class AnalysisSessionListCreateView(generics.ListCreateAPIView):
    """List all analysis sessions or start a new batch analysis"""
    serializer_class = AnalysisSessionSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AnalysisSession.objects.filter(
            project__created_by=self.request.user
        ).select_related('project', 'started_by')


class AnalysisSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an analysis session"""
    serializer_class = AnalysisSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AnalysisSession.objects.filter(
            project__created_by=self.request.user
        )


# Dashboard and Statistics Views
@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Temporarily allow unauthenticated access
def dashboard_stats(request):
    """Get dashboard statistics for the current user"""
    # Handle unauthenticated users for testing
    if request.user.is_authenticated:
        user = request.user
    else:
        from django.contrib.auth.models import User
        user, created = User.objects.get_or_create(username='tanzeem')
    
    user_projects = Project.objects.filter(created_by=user)
    
    total_documents = Document.objects.filter(project__in=user_projects).count()
    total_analyses = Analysis.objects.filter(document__project__in=user_projects).count()
    
    # Recent activity
    recent_documents = Document.objects.filter(
        project__in=user_projects
    ).order_by('-uploaded_at')[:5]
    
    recent_analyses = Analysis.objects.filter(
        document__project__in=user_projects
    ).order_by('-created_at')[:5]
    
    # Status distribution
    document_status = Document.objects.filter(
        project__in=user_projects
    ).values('status').annotate(count=Count('id'))
    
    analysis_status = Analysis.objects.filter(
        document__project__in=user_projects
    ).values('status').annotate(count=Count('id'))
    
    return Response({
        'totals': {
            'projects': user_projects.count(),
            'documents': total_documents,
            'analyses': total_analyses,
            'reports': Report.objects.filter(project__in=user_projects).count(),
        },
        'recent_activity': {
            'documents': DocumentListSerializer(recent_documents, many=True).data,
            'analyses': AnalysisListSerializer(recent_analyses, many=True).data,
        },
        'status_distribution': {
            'documents': {item['status']: item['count'] for item in document_status},
            'analyses': {item['status']: item['count'] for item in analysis_status},
        },
        'storage_stats': {
            'total_size_bytes': Document.objects.filter(
                project__in=user_projects
            ).aggregate(total=Sum('file_size'))['total'] or 0,
        }
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Temporarily allow unauthenticated access
def document_library_stats(request):
    """Get statistics for the document library page"""
    # Handle unauthenticated users for testing
    if request.user.is_authenticated:
        user = request.user
    else:
        from django.contrib.auth.models import User
        user, created = User.objects.get_or_create(username='tanzeem')
    
    user_projects = Project.objects.filter(created_by=user)
    documents = Document.objects.filter(project__in=user_projects)
    
    # Basic stats
    total_documents = documents.count()
    total_projects = user_projects.count()
    total_size = documents.aggregate(total=Sum('file_size'))['total'] or 0
    
    # Recent uploads (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_uploads = documents.filter(uploaded_at__gte=thirty_days_ago).count()
    
    # Document type distribution
    type_distribution = documents.values('document_type').annotate(count=Count('id'))
    
    # Project distribution
    project_distribution = documents.values('project__name').annotate(count=Count('id'))
    
    return Response({
        'total_documents': total_documents,
        'total_projects': total_projects,
        'total_size_mb': round(total_size / (1024 * 1024), 2) if total_size else 0,
        'recent_uploads': recent_uploads,
        'type_distribution': {item['document_type']: item['count'] for item in type_distribution},
        'project_distribution': {item['project__name']: item['count'] for item in project_distribution},
    })


# Bulk Operations
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def bulk_upload_documents(request):
    """Upload multiple documents at once"""
    files = request.FILES.getlist('files')
    project_id = request.data.get('project_id')
    
    if not files:
        return Response(
            {'error': 'No files provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate project access
    if project_id:
        try:
            project = Project.objects.get(id=project_id, created_by=request.user)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        # Create a new project for bulk upload
        project = Project.objects.create(
            name=f"Bulk Upload {timezone.now().strftime('%Y%m%d_%H%M%S')}",
            created_by=request.user,
            project_type='oil_gas',
            status='active'
        )
    
    # Process each file
    uploaded_documents = []
    errors = []
    
    for file in files:
        try:
            # Create document
            document = Document.objects.create(
                project=project,
                file=file,
                original_filename=file.name,
                title=file.name,
                document_type='other',  # Default type
                file_size=file.size,
                file_type=file.name.split('.')[-1].lower() if '.' in file.name else 'unknown',
                status='ready',
                uploaded_by=request.user,
                processed_at=timezone.now()
            )
            uploaded_documents.append(DocumentListSerializer(document).data)
            
        except Exception as e:
            errors.append({
                'file': file.name,
                'error': str(e)
            })
    
    return Response({
        'success': True,
        'uploaded_count': len(uploaded_documents),
        'error_count': len(errors),
        'project': ProjectSerializer(project).data,
        'documents': uploaded_documents,
        'errors': errors
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_batch_analysis(request):
    """Start analysis for multiple documents"""
    document_ids = request.data.get('document_ids', [])
    analysis_type = request.data.get('analysis_type', 'full_analysis')
    
    if not document_ids:
        return Response(
            {'error': 'No document IDs provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate document access
    documents = Document.objects.filter(
        id__in=document_ids,
        project__created_by=request.user
    )
    
    if documents.count() != len(document_ids):
        return Response(
            {'error': 'Some documents not found or access denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Create analysis session
    session = AnalysisSession.objects.create(
        project=documents.first().project,
        session_name=f"Batch Analysis {timezone.now().strftime('%Y%m%d_%H%M%S')}",
        analysis_types=[analysis_type],
        total_documents=documents.count(),
        started_by=request.user
    )
    session.documents.set(documents)
    
    # Create individual analyses
    analyses_created = []
    for document in documents:
        analysis = Analysis.objects.create(
            document=document,
            analysis_type=analysis_type,
            status='queued',
            started_by=request.user,
            started_at=timezone.now()
        )
        analyses_created.append(analysis.id)
    
    # In a real implementation, you would queue these for background processing
    # For now, mark the session as completed
    session.status = 'completed'
    session.completed_documents = documents.count()
    session.completed_at = timezone.now()
    session.save()
    
    return Response({
        'success': True,
        'session': AnalysisSessionSerializer(session).data,
        'analyses_created': len(analyses_created)
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def download_document_pdf_report(request, document_id):
    """Generate and download a professional PDF report for a document analysis"""
    try:
        # Handle anonymous users for development
        if request.user.is_anonymous:
            document = get_object_or_404(Document, id=document_id)
        else:
            document = get_object_or_404(
                Document,
                id=document_id,
                project__created_by=request.user
            )
        
        # Get the latest analysis for this document
        analysis = Analysis.objects.filter(document=document).order_by('-created_at').first()
        
        # Import PDF generator
        from .pdf_generator import generate_document_pdf_report
        
        # Generate PDF report
        pdf_content = generate_document_pdf_report(document, analysis)
        
        # Create response
        filename = f"analysis_report_{document.title}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return Response(
            {'error': f'Failed to generate PDF report: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def download_project_pdf_report(request, project_id):
    """Generate and download a professional PDF report for a project summary"""
    try:
        # Handle anonymous users for development
        if request.user.is_anonymous:
            project = get_object_or_404(Project, id=project_id)
        else:
            project = get_object_or_404(
                Project,
                id=project_id,
                created_by=request.user
            )
        
        # Get project documents and analyses
        documents = Document.objects.filter(project=project)
        analyses = Analysis.objects.filter(document__project=project)
        
        # Import PDF generator
        from .pdf_generator import generate_project_pdf_report
        
        # Generate PDF report
        pdf_content = generate_project_pdf_report(project, documents, analyses)
        
        # Create response
        filename = f"project_summary_{project.name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return Response(
            {'error': f'Failed to generate PDF report: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )