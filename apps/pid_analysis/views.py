"""
EDRS P&ID Analysis API Views
Advanced Oil & Gas Process Diagram Analysis System
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
import asyncio
import json
import logging
from typing import Dict, Any

from .models import (
    PIDProject, PIDDiagram, ErrorCategory, 
    PIDAnalysisResult, PIDElement, AnalysisSession
)
from .services.analysis_engine import AdvancedPIDAnalyzer, AnalysisConfig
from .serializers import (
    PIDProjectSerializer, PIDDiagramSerializer, 
    PIDAnalysisResultSerializer, AnalysisSessionSerializer
)

logger = logging.getLogger(__name__)


class PIDProjectViewSet(viewsets.ModelViewSet):
    """P&ID Project Management API"""
    
    serializer_class = PIDProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PIDProject.objects.filter(
            project_manager=self.request.user
        ).prefetch_related('diagrams')
    
    def perform_create(self, serializer):
        serializer.save(project_manager=self.request.user)
    
    @action(detail=True, methods=['get'])
    def analysis_summary(self, request, pk=None):
        """Get project analysis summary and statistics"""
        project = self.get_object()
        
        # Calculate project statistics
        diagrams = project.diagrams.all()
        total_diagrams = diagrams.count()
        analyzed_diagrams = diagrams.exclude(status='uploaded').count()
        
        # Error statistics
        total_errors = 0
        critical_errors = 0
        high_errors = 0
        
        for diagram in diagrams:
            total_errors += diagram.total_errors_found
            critical_errors += diagram.critical_errors
            high_errors += diagram.high_priority_errors
        
        # Recent analysis sessions
        recent_sessions = AnalysisSession.objects.filter(
            diagram__project=project
        ).order_by('-started_at')[:10]
        
        summary = {
            'project_info': {
                'name': project.name,
                'project_type': project.get_project_type_display(),
                'engineering_standard': project.get_engineering_standard_display(),
                'client_company': project.client_company,
            },
            'analysis_statistics': {
                'total_diagrams': total_diagrams,
                'analyzed_diagrams': analyzed_diagrams,
                'analysis_completion': round((analyzed_diagrams / total_diagrams * 100) if total_diagrams > 0 else 0, 1),
                'total_errors_found': total_errors,
                'critical_errors': critical_errors,
                'high_priority_errors': high_errors,
            },
            'recent_sessions': AnalysisSessionSerializer(recent_sessions, many=True).data
        }
        
        return Response(summary)


class PIDDiagramViewSet(viewsets.ModelViewSet):
    """P&ID Diagram Management and Analysis API"""
    
    serializer_class = PIDDiagramSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]
    
    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        if project_id:
            return PIDDiagram.objects.filter(
                project_id=project_id,
                project__project_manager=self.request.user
            ).prefetch_related('analysis_results', 'elements')
        return PIDDiagram.objects.none()
    
    def perform_create(self, serializer):
        project = get_object_or_404(
            PIDProject, 
            pk=self.kwargs['project_pk'],
            project_manager=self.request.user
        )
        serializer.save(
            project=project,
            uploaded_by=self.request.user,
            file_size=self.request.FILES['original_file'].size if 'original_file' in self.request.FILES else 0
        )
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, project_pk=None, pk=None):
        """
        Initiate P&ID analysis for a diagram
        
        POST /api/projects/{project_id}/diagrams/{diagram_id}/analyze/
        Body: {
            "analysis_depth": "standard|quick|deep",
            "include_safety_analysis": true,
            "include_standards_check": true,
            "confidence_threshold": 0.7
        }
        """
        diagram = self.get_object()
        
        # Validate diagram can be analyzed
        if not diagram.original_file:
            return Response(
                {'error': 'No file uploaded for analysis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if diagram.status == 'processing':
            return Response(
                {'error': 'Analysis already in progress'},
                status=status.HTTP_409_CONFLICT
            )
        
        # Parse analysis configuration
        config_data = request.data
        from .services.enhanced_analysis import AnalysisConfig
        analysis_config = AnalysisConfig(
            model=config_data.get('model', 'gpt-4o'),
            temperature=float(config_data.get('temperature', 0.2)),
            confidence_threshold=float(config_data.get('confidence_threshold', 0.7)),
            max_retries=int(config_data.get('max_retries', 3))
        )
        
        # Create analysis session
        session = AnalysisSession.objects.create(
            diagram=diagram,
            llm_model=analysis_config.model,
            analysis_depth='comprehensive',
            include_recommendations=True,
            initiated_by=request.user
        )
        
        # Update diagram status
        diagram.status = 'processing'
        diagram.processing_started_at = timezone.now()
        diagram.save()
        
        # Start enhanced analysis
        try:
            # Import enhanced service
            from .services.enhanced_analysis import analysis_service
            
            # Run analysis in background
            asyncio.create_task(
                self._run_enhanced_analysis_async(diagram, session, analysis_service)
            )
            
            return Response({
                'message': 'Analysis initiated successfully',
                'session_id': str(session.id),
                'estimated_time': self._estimate_analysis_time(analysis_config.analysis_depth),
                'status': 'processing'
            })
            
        except Exception as e:
            logger.error(f"Failed to initiate analysis: {e}")
            session.status = 'failed'
            session.error_message = str(e)
            session.save()
            
            diagram.status = 'error'
            diagram.save()
            
            return Response(
                {'error': f'Failed to initiate analysis: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    async def _run_analysis_async(self, diagram: PIDDiagram, session: AnalysisSession, config: AnalysisConfig):
        """Run P&ID analysis asynchronously"""
        
        async def progress_callback(message: str, percentage: int):
            """Update analysis progress"""
            session.status = message.lower().replace(' ', '_')
            session.progress_percentage = percentage
            session.save()
        
        try:
            # Initialize analyzer
            analyzer = AdvancedPIDAnalyzer(config)
            
            # Prepare project context
            project_context = {
                'facility_name': diagram.project.field_name,
                'process_unit': diagram.process_area,
                'project_type': diagram.project.project_type,
                'standard': diagram.project.engineering_standard,
                'drawing_number': diagram.drawing_number,
                'revision': diagram.revision,
                'operating_conditions': f"P: {diagram.operating_pressure}, T: {diagram.operating_temperature}"
            }
            
            # Run analysis
            detected_errors, analysis_metadata = await analyzer.analyze_pid_diagram(
                diagram.original_file.path,
                project_context,
                progress_callback
            )
            
            # Save results to database
            await self._save_analysis_results(diagram, session, detected_errors, analysis_metadata)
            
            # Update session status
            session.status = 'completed'
            session.completed_at = timezone.now()
            session.total_elements_detected = analysis_metadata.get('elements_detected', 0)
            session.total_errors_found = len(detected_errors)
            session.processing_time_seconds = analysis_metadata.get('total_processing_time', 0)
            session.save()
            
            # Update diagram status
            diagram.status = 'analyzed'
            diagram.processing_completed_at = timezone.now()
            diagram.total_errors_found = len(detected_errors)
            diagram.critical_errors = sum(1 for e in detected_errors if e.severity == 'critical')
            diagram.high_priority_errors = sum(1 for e in detected_errors if e.severity == 'high')
            diagram.medium_priority_errors = sum(1 for e in detected_errors if e.severity == 'medium')
            diagram.low_priority_errors = sum(1 for e in detected_errors if e.severity == 'low')
            diagram.save()
            
            logger.info(f"Analysis completed for diagram {diagram.id}: {len(detected_errors)} errors found")
            
        except Exception as e:
            logger.error(f"Analysis failed for diagram {diagram.id}: {e}")
            
            # Update session with error
            session.status = 'failed'
            session.error_message = str(e)
            session.completed_at = timezone.now()
            session.save()
            
            # Update diagram status
            diagram.status = 'error'
            diagram.save()
    
    async def _save_analysis_results(
        self, 
        diagram: PIDDiagram, 
        session: AnalysisSession, 
        detected_errors, 
        metadata: Dict[str, Any]
    ):
        """Save analysis results to database"""
        
        with transaction.atomic():
            # Clear existing results for this diagram
            PIDAnalysisResult.objects.filter(diagram=diagram).delete()
            PIDElement.objects.filter(diagram=diagram).delete()
            
            # Save detected errors
            for error in detected_errors:
                # Get or create error category
                category, _ = ErrorCategory.objects.get_or_create(
                    name=error.category,
                    defaults={
                        'category_type': self._map_category_type(error.category),
                        'description': f"Errors related to {error.category.lower()}"
                    }
                )
                
                # Create analysis result
                PIDAnalysisResult.objects.create(
                    diagram=diagram,
                    category=category,
                    error_title=error.title,
                    error_description=error.description,
                    root_cause=error.root_cause,
                    recommended_fix=error.recommended_fix,
                    severity_level=error.severity.lower(),
                    confidence_score=error.confidence,
                    element_tag=error.element_tag,
                    line_number=error.line_number,
                    coordinates_x=error.coordinates[0] if error.coordinates else None,
                    coordinates_y=error.coordinates[1] if error.coordinates else None,
                    violated_standard=error.violated_standard,
                    standard_reference=error.standard_reference,
                    llm_model_used=metadata.get('model_used', 'unknown'),
                    processing_time=metadata.get('llm_time', 0)
                )
    
    def _map_category_type(self, category: str) -> str:
        """Map error category to database category type"""
        mapping = {
            'Safety Systems': 'safety',
            'Instrumentation': 'instrumentation',
            'Piping': 'piping',
            'Process': 'mechanical',
            'Drafting': 'drafting',
            'Equipment': 'equipment',
        }
        return mapping.get(category, 'logical')
    
    def _estimate_analysis_time(self, analysis_depth: str) -> int:
        """Estimate analysis time in seconds"""
        estimates = {
            'quick': 30,
            'standard': 90, 
            'deep': 180
        }
        return estimates.get(analysis_depth, 90)
    
    @action(detail=True, methods=['get'])
    def analysis_results(self, request, project_pk=None, pk=None):
        """Get analysis results for a diagram"""
        diagram = self.get_object()
        
        # Get analysis results with filters
        severity_filter = request.query_params.get('severity')
        category_filter = request.query_params.get('category')
        
        results = diagram.analysis_results.select_related('category')
        
        if severity_filter:
            results = results.filter(severity_level=severity_filter)
        if category_filter:
            results = results.filter(category__name__icontains=category_filter)
        
        # Serialize results
        serializer = PIDAnalysisResultSerializer(results, many=True)
        
        # Add summary statistics
        summary = {
            'total_errors': results.count(),
            'by_severity': {
                'critical': results.filter(severity_level='critical').count(),
                'high': results.filter(severity_level='high').count(),
                'medium': results.filter(severity_level='medium').count(),
                'low': results.filter(severity_level='low').count(),
            },
            'by_category': {}
        }
        
        # Category breakdown
        for category in ErrorCategory.objects.all():
            count = results.filter(category=category).count()
            if count > 0:
                summary['by_category'][category.name] = count
        
        return Response({
            'summary': summary,
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def analysis_status(self, request, project_pk=None, pk=None):
        """Get current analysis status"""
        diagram = self.get_object()
        
        # Get latest session
        latest_session = diagram.analysis_sessions.order_by('-started_at').first()
        
        response_data = {
            'diagram_status': diagram.status,
            'processing_started_at': diagram.processing_started_at,
            'processing_completed_at': diagram.processing_completed_at,
            'total_errors_found': diagram.total_errors_found,
        }
        
        if latest_session:
            response_data.update({
                'session_id': str(latest_session.id),
                'session_status': latest_session.status,
                'progress_percentage': latest_session.progress_percentage,
                'estimated_completion': None,  # Could calculate based on progress
                'error_message': latest_session.error_message if latest_session.status == 'failed' else None
            })
        
        return Response(response_data)

    async def _run_enhanced_analysis_async(self, diagram, session, analysis_service):
        """Run enhanced P&ID analysis with fallback capabilities"""
        
        try:
            # Progress callback
            async def progress_callback(message, percent):
                session.status = 'processing'
                session.progress_percent = percent
                session.current_step = message
                await asyncio.to_thread(session.save)
            
            # Prepare project context
            project_context = {
                'name': diagram.project.name,
                'project_type': diagram.project.project_type,
                'engineering_standard': diagram.project.engineering_standard,
                'field_name': getattr(diagram.project, 'field_name', ''),
            }
            
            # Get diagram file path
            diagram_path = diagram.original_file.path if diagram.original_file else None
            
            # Run analysis
            detected_errors, analysis_metadata = await analysis_service.analyze_diagram(
                diagram_path,
                project_context,
                progress_callback
            )
            
            # Save results
            await asyncio.to_thread(self._save_analysis_results, 
                                  diagram, session, detected_errors, analysis_metadata)
            
        except Exception as e:
            # Handle errors gracefully
            await asyncio.to_thread(self._handle_analysis_error, diagram, session, str(e))
    
    def _save_analysis_results(self, diagram, session, errors, metadata):
        """Save analysis results to database"""
        
        from django.db import transaction
        
        with transaction.atomic():
            # Update session
            session.status = 'completed'
            session.progress_percent = 100
            session.current_step = 'Analysis complete'
            session.total_errors_found = len(errors)
            session.processing_time_seconds = metadata.get('total_processing_time', 0)
            session.completed_at = timezone.now()
            session.save()
            
            # Update diagram
            diagram.status = 'analyzed'
            diagram.processing_completed_at = timezone.now()
            diagram.total_errors_found = len(errors)
            
            # Count by severity
            diagram.critical_errors = len([e for e in errors if e.severity == 'Critical'])
            diagram.high_priority_errors = len([e for e in errors if e.severity == 'High'])
            diagram.medium_priority_errors = len([e for e in errors if e.severity == 'Medium'])
            diagram.low_priority_errors = len([e for e in errors if e.severity == 'Low'])
            diagram.save()
            
            # Save individual errors
            for error in errors:
                # Get or create error category
                category, created = ErrorCategory.objects.get_or_create(
                    name=error.category,
                    defaults={
                        'description': f'{error.category} related errors',
                        'severity_level': error.severity.lower(),
                        'is_safety_critical': error.safety_impact
                    }
                )
                
                # Create analysis result
                PIDAnalysisResult.objects.create(
                    diagram=diagram,
                    session=session,
                    category=category,
                    error_type=error.subcategory or 'General',
                    title=error.title,
                    description=error.description,
                    severity=error.severity,
                    confidence_score=error.confidence,
                    element_tag=error.element_tag,
                    coordinates_x=error.coordinates[0] if error.coordinates else 0,
                    coordinates_y=error.coordinates[1] if error.coordinates else 0,
                    violated_standard=error.violated_standard,
                    standard_reference=error.standard_reference,
                    recommended_fix=error.recommended_fix,
                    safety_impact=error.safety_impact,
                    cost_impact=error.cost_impact,
                    root_cause_analysis=error.root_cause,
                    status='identified'
                )
    
    def _handle_analysis_error(self, diagram, session, error_message):
        """Handle analysis errors"""
        
        session.status = 'failed'
        session.error_message = error_message
        session.completed_at = timezone.now()
        session.save()
        
        diagram.status = 'error'
        diagram.save()


class AnalysisResultViewSet(viewsets.ReadOnlyModelViewSet):
    """P&ID Analysis Results API"""
    
    serializer_class = PIDAnalysisResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        diagram_id = self.kwargs.get('diagram_pk')
        if diagram_id:
            return PIDAnalysisResult.objects.filter(
                diagram_id=diagram_id,
                diagram__project__project_manager=self.request.user
            ).select_related('category', 'diagram')
        return PIDAnalysisResult.objects.none()
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, diagram_pk=None, pk=None):
        """Update error status (accept, reject, fix, etc.)"""
        result = self.get_object()
        
        new_status = request.data.get('status')
        review_comments = request.data.get('comments', '')
        
        if new_status not in dict(PIDAnalysisResult.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result.status = new_status
        result.review_comments = review_comments
        result.reviewed_by = request.user
        result.review_date = timezone.now()
        result.save()
        
        return Response({
            'message': 'Status updated successfully',
            'new_status': result.get_status_display()
        })


class AnalysisSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """Analysis Session Monitoring API"""
    
    serializer_class = AnalysisSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AnalysisSession.objects.filter(
            diagram__project__project_manager=self.request.user
        ).select_related('diagram', 'initiated_by')