"""
Django REST Framework Serializers for EDRS Document Management
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Document, Analysis, Report, AnalysisSession


class UserSerializer(serializers.ModelSerializer):
    """Simplified user serializer for document references"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class ProjectSerializer(serializers.ModelSerializer):
    """Project serializer with computed fields"""
    created_by = UserSerializer(read_only=True)
    document_count = serializers.ReadOnlyField()
    analysis_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'project_type', 'engineering_standard',
            'client_name', 'project_number', 'location', 'status',
            'created_by', 'created_at', 'updated_at',
            'document_count', 'analysis_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Automatically set the created_by field - handle anonymous users for development
        request = self.context['request']
        if request.user.is_authenticated:
            user = request.user
        else:
            # Create or get a default user for testing
            from django.contrib.auth.models import User
            user, created = User.objects.get_or_create(
                username='tanzeem',
                defaults={
                    'email': 'tanzeem@rejlers.ae',
                    'first_name': 'Tanzeem',
                    'last_name': 'Agra'
                }
            )
        
        validated_data['created_by'] = user
        return super().create(validated_data)


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight document serializer for list views"""
    project = ProjectSerializer(read_only=True)
    uploaded_by = UserSerializer(read_only=True)
    file_extension = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    analysis_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'drawing_number', 'revision', 'document_type',
            'original_filename', 'file_extension', 'display_name',
            'file_size', 'status', 'quality_level', 'project',
            'uploaded_by', 'uploaded_at', 'analysis_count'
        ]
    
    def get_analysis_count(self, obj):
        return obj.analyses.count()


class DocumentSerializer(serializers.ModelSerializer):
    """Full document serializer with all fields"""
    project = ProjectSerializer(read_only=True)
    project_id = serializers.UUIDField(write_only=True)
    uploaded_by = UserSerializer(read_only=True)
    file_extension = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    analyses = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'project', 'project_id', 'file', 'original_filename',
            'file_size', 'file_type', 'file_hash', 'file_extension',
            'title', 'drawing_number', 'revision', 'document_type',
            'discipline', 'plant_area', 'system_tag', 'equipment_list',
            'status', 'quality_level', 'ocr_text', 'metadata_extracted',
            'processing_notes', 'display_name', 'uploaded_by',
            'uploaded_at', 'processed_at', 'updated_at', 'analyses'
        ]
        read_only_fields = [
            'id', 'file_size', 'file_type', 'file_hash',
            'uploaded_at', 'processed_at', 'updated_at'
        ]
    
    def get_analyses(self, obj):
        """Get recent analyses for this document"""
        recent_analyses = obj.analyses.all()[:5]  # Latest 5 analyses
        return AnalysisListSerializer(recent_analyses, many=True).data
    
    def create(self, validated_data):
        # Set the uploaded_by field and process file
        validated_data['uploaded_by'] = self.context['request'].user
        validated_data['original_filename'] = validated_data['file'].name
        validated_data['file_type'] = validated_data['file'].name.split('.')[-1].lower()
        
        return super().create(validated_data)


class AnalysisListSerializer(serializers.ModelSerializer):
    """Lightweight analysis serializer for list views"""
    document = DocumentListSerializer(read_only=True)
    started_by = UserSerializer(read_only=True)
    equipment_count = serializers.ReadOnlyField()
    issues_count = serializers.ReadOnlyField()
    duration = serializers.ReadOnlyField()
    
    class Meta:
        model = Analysis
        fields = [
            'id', 'document', 'analysis_type', 'status', 'confidence_level',
            'ai_model_used', 'summary', 'equipment_count', 'issues_count',
            'duration', 'started_by', 'created_at', 'completed_at'
        ]


class AnalysisSerializer(serializers.ModelSerializer):
    """Full analysis serializer with all results"""
    document = DocumentListSerializer(read_only=True)
    document_id = serializers.UUIDField(write_only=True)
    started_by = UserSerializer(read_only=True)
    equipment_count = serializers.ReadOnlyField()
    issues_count = serializers.ReadOnlyField()
    duration = serializers.ReadOnlyField()
    
    class Meta:
        model = Analysis
        fields = [
            'id', 'document', 'document_id', 'analysis_type', 'configuration',
            'ai_model_used', 'status', 'confidence_level', 'results', 'summary',
            'equipment_detected', 'symbols_detected', 'piping_detected',
            'issues_found', 'recommendations', 'compliance_notes',
            'processing_time', 'error_message', 'equipment_count',
            'issues_count', 'duration', 'started_by', 'created_at',
            'started_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'processing_time', 'created_at', 'started_at', 'completed_at'
        ]
    
    def create(self, validated_data):
        # Set the started_by field
        request = self.context['request']
        if request.user.is_authenticated:
            user = request.user
        else:
            from django.contrib.auth.models import User
            user, created = User.objects.get_or_create(username='tanzeem')
        
        validated_data['started_by'] = user
        return super().create(validated_data)


class ReportSerializer(serializers.ModelSerializer):
    """Report serializer with project and generation info"""
    project = ProjectSerializer(read_only=True)
    project_id = serializers.UUIDField(write_only=True)
    generated_by = UserSerializer(read_only=True)
    documents = DocumentListSerializer(many=True, read_only=True)
    analyses = AnalysisListSerializer(many=True, read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'project', 'project_id', 'documents', 'analyses',
            'title', 'report_type', 'format', 'configuration', 'content',
            'file', 'file_size', 'status', 'generation_time', 'error_message',
            'expires_at', 'is_expired', 'generated_by', 'created_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'generation_time', 'created_at', 'completed_at'
        ]
    
    def create(self, validated_data):
        # Set the generated_by field
        request = self.context['request']
        if request.user.is_authenticated:
            user = request.user
        else:
            from django.contrib.auth.models import User
            user, created = User.objects.get_or_create(username='tanzeem')
        
        validated_data['generated_by'] = user
        return super().create(validated_data)


class AnalysisSessionSerializer(serializers.ModelSerializer):
    """Analysis session serializer with progress tracking"""
    project = ProjectSerializer(read_only=True)
    project_id = serializers.UUIDField(write_only=True)
    documents = DocumentListSerializer(many=True, read_only=True)
    document_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    started_by = UserSerializer(read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = AnalysisSession
        fields = [
            'id', 'project', 'project_id', 'documents', 'document_ids',
            'session_name', 'analysis_types', 'configuration', 'status',
            'total_documents', 'completed_documents', 'failed_documents',
            'progress_percentage', 'total_equipment_found', 'total_issues_found',
            'processing_time', 'started_by', 'created_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'total_documents', 'completed_documents', 'failed_documents',
            'total_equipment_found', 'total_issues_found', 'processing_time',
            'created_at', 'completed_at'
        ]
    
    def create(self, validated_data):
        # Handle document IDs and set started_by
        document_ids = validated_data.pop('document_ids', [])
        validated_data['started_by'] = self.context['request'].user
        
        session = super().create(validated_data)
        
        # Add documents if provided
        if document_ids:
            documents = Document.objects.filter(id__in=document_ids)
            session.documents.set(documents)
            session.total_documents = documents.count()
            session.save()
        
        return session


# Document upload-specific serializers
class DocumentUploadSerializer(serializers.ModelSerializer):
    """Optimized serializer for document uploads"""
    project_name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Document
        fields = [
            'file', 'title', 'drawing_number', 'revision', 'document_type',
            'discipline', 'plant_area', 'system_tag', 'project_name'
        ]
    
    def create(self, validated_data):
        # Handle project creation/selection
        project_name = validated_data.pop('project_name', None)
        request = self.context['request']
        
        # Get or create a user (for unauthenticated access)
        from django.contrib.auth.models import User
        from django.utils import timezone
        
        if request.user.is_authenticated:
            user = request.user
        else:
            # Create or get a default user for testing
            user, created = User.objects.get_or_create(
                username='tanzeem',
                defaults={
                    'email': 'tanzeem@rejlers.ae',
                    'first_name': 'Tanzeem',
                    'last_name': 'Agra'
                }
            )
        
        # Find or create project
        if project_name:
            project, created = Project.objects.get_or_create(
                name=project_name,
                created_by=user,
                defaults={
                    'project_type': 'oil_gas',
                    'status': 'active'
                }
            )
        else:
            # Create a default project if none specified
            project = Project.objects.create(
                name=f"Project {timezone.now().strftime('%Y%m%d_%H%M%S')}",
                created_by=user,
                project_type='oil_gas',
                status='active'
            )
        
        # Set document fields
        validated_data['project'] = project
        validated_data['uploaded_by'] = user
        validated_data['original_filename'] = validated_data['file'].name
        validated_data['file_type'] = validated_data['file'].name.split('.')[-1].lower()
        validated_data['status'] = 'processing'
        
        # Set title if not provided
        if not validated_data.get('title'):
            validated_data['title'] = validated_data['original_filename']
        
        return super().create(validated_data)