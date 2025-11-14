"""
EDRS P&ID Analysis API Serializers
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    PIDProject, PIDDiagram, ErrorCategory,
    PIDAnalysisResult, PIDElement, AnalysisSession
)

User = get_user_model()


class PIDProjectSerializer(serializers.ModelSerializer):
    """P&ID Project serializer"""
    
    project_manager_name = serializers.CharField(source='project_manager.get_full_name', read_only=True)
    total_diagrams = serializers.SerializerMethodField()
    analyzed_diagrams = serializers.SerializerMethodField()
    total_errors = serializers.SerializerMethodField()
    
    class Meta:
        model = PIDProject
        fields = [
            'id', 'name', 'description', 'project_type', 'engineering_standard',
            'field_name', 'facility_code', 'process_unit', 'client_company',
            'engineering_contractor', 'project_manager', 'project_manager_name',
            'created_at', 'updated_at', 'is_active',
            'total_diagrams', 'analyzed_diagrams', 'total_errors'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_diagrams(self, obj):
        return obj.diagrams.count()
    
    def get_analyzed_diagrams(self, obj):
        return obj.diagrams.exclude(status='uploaded').count()
    
    def get_total_errors(self, obj):
        return sum(diagram.total_errors_found for diagram in obj.diagrams.all())


class PIDDiagramSerializer(serializers.ModelSerializer):
    """P&ID Diagram serializer"""
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_url = serializers.SerializerMethodField()
    analysis_completion_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = PIDDiagram
        fields = [
            'id', 'project', 'project_name', 'drawing_number', 'drawing_title',
            'diagram_type', 'revision', 'sheet_number', 'original_file', 'file_url',
            'file_size', 'status', 'processing_started_at', 'processing_completed_at',
            'total_errors_found', 'critical_errors', 'high_priority_errors',
            'medium_priority_errors', 'low_priority_errors', 'process_area',
            'operating_pressure', 'operating_temperature', 'design_phase',
            'created_at', 'updated_at', 'uploaded_by', 'uploaded_by_name',
            'analysis_completion_percentage'
        ]
        read_only_fields = [
            'id', 'file_size', 'processing_started_at', 'processing_completed_at',
            'total_errors_found', 'critical_errors', 'high_priority_errors',
            'medium_priority_errors', 'low_priority_errors', 'created_at', 'updated_at'
        ]
    
    def get_file_url(self, obj):
        if obj.original_file:
            return obj.original_file.url
        return None
    
    def get_analysis_completion_percentage(self, obj):
        if obj.status == 'uploaded':
            return 0
        elif obj.status == 'processing':
            # Get latest session progress
            latest_session = obj.analysis_sessions.order_by('-started_at').first()
            return latest_session.progress_percentage if latest_session else 0
        elif obj.status in ['analyzed', 'reviewed', 'approved']:
            return 100
        return 0


class ErrorCategorySerializer(serializers.ModelSerializer):
    """Error Category serializer"""
    
    class Meta:
        model = ErrorCategory
        fields = ['id', 'name', 'category_type', 'description', 'color_code', 'is_active']


class PIDAnalysisResultSerializer(serializers.ModelSerializer):
    """P&ID Analysis Result serializer"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color_code', read_only=True)
    diagram_number = serializers.CharField(source='diagram.drawing_number', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    
    class Meta:
        model = PIDAnalysisResult
        fields = [
            'id', 'diagram', 'diagram_number', 'category', 'category_name', 'category_color',
            'error_title', 'error_description', 'root_cause', 'recommended_fix',
            'severity_level', 'confidence_score', 'element_tag', 'line_number',
            'coordinates_x', 'coordinates_y', 'violated_standard', 'standard_reference',
            'status', 'reviewed_by', 'reviewed_by_name', 'review_comments', 'review_date',
            'llm_model_used', 'processing_time', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'diagram', 'category', 'confidence_score', 'llm_model_used',
            'processing_time', 'created_at', 'updated_at'
        ]


class PIDElementSerializer(serializers.ModelSerializer):
    """P&ID Element serializer"""
    
    class Meta:
        model = PIDElement
        fields = [
            'id', 'diagram', 'element_type', 'tag_number', 'description',
            'size', 'specification', 'service', 'coordinates_x', 'coordinates_y',
            'confidence_score', 'extracted_by_ai', 'created_at'
        ]
        read_only_fields = ['id', 'confidence_score', 'extracted_by_ai', 'created_at']


class AnalysisSessionSerializer(serializers.ModelSerializer):
    """Analysis Session serializer"""
    
    diagram_number = serializers.CharField(source='diagram.drawing_number', read_only=True)
    initiated_by_name = serializers.CharField(source='initiated_by.get_full_name', read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalysisSession
        fields = [
            'id', 'diagram', 'diagram_number', 'llm_model', 'analysis_depth',
            'include_recommendations', 'status', 'progress_percentage',
            'total_elements_detected', 'total_errors_found', 'processing_time_seconds',
            'error_message', 'started_at', 'completed_at', 'initiated_by',
            'initiated_by_name', 'duration_seconds'
        ]
        read_only_fields = [
            'id', 'total_elements_detected', 'total_errors_found',
            'processing_time_seconds', 'started_at', 'completed_at'
        ]
    
    def get_duration_seconds(self, obj):
        if obj.completed_at and obj.started_at:
            return (obj.completed_at - obj.started_at).total_seconds()
        return None


class AnalysisRequestSerializer(serializers.Serializer):
    """Analysis request parameters serializer"""
    
    analysis_depth = serializers.ChoiceField(
        choices=[('quick', 'Quick Scan'), ('standard', 'Standard Analysis'), ('deep', 'Deep Analysis')],
        default='standard'
    )
    include_safety_analysis = serializers.BooleanField(default=True)
    include_standards_check = serializers.BooleanField(default=True)
    confidence_threshold = serializers.FloatField(min_value=0.0, max_value=1.0, default=0.7)
    
    def validate_confidence_threshold(self, value):
        if value < 0.5:
            raise serializers.ValidationError("Confidence threshold should be at least 0.5")
        return value


class AnalysisStatusSerializer(serializers.Serializer):
    """Analysis status response serializer"""
    
    diagram_status = serializers.CharField()
    session_status = serializers.CharField(required=False)
    progress_percentage = serializers.IntegerField(required=False)
    total_errors_found = serializers.IntegerField()
    processing_started_at = serializers.DateTimeField(required=False)
    processing_completed_at = serializers.DateTimeField(required=False)
    error_message = serializers.CharField(required=False)


class AnalysisSummarySerializer(serializers.Serializer):
    """Analysis summary response serializer"""
    
    project_info = serializers.DictField()
    analysis_statistics = serializers.DictField()
    recent_sessions = AnalysisSessionSerializer(many=True)


class ErrorStatusUpdateSerializer(serializers.Serializer):
    """Error status update serializer"""
    
    status = serializers.ChoiceField(choices=PIDAnalysisResult.STATUS_CHOICES)
    comments = serializers.CharField(required=False, allow_blank=True)