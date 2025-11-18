"""
EDRS Document Management Models
Complete database schema for document storage, analysis, and reporting
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import os


def document_upload_path(instance, filename):
    """Generate organized upload path for documents"""
    # Extract file extension
    ext = filename.split('.')[-1] if '.' in filename else 'unknown'
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{ext}"
    
    # Organize by user, project, and date
    date_path = timezone.now().strftime('%Y/%m')
    return f"documents/{instance.project.id}/{date_path}/{unique_filename}"


class Project(models.Model):
    """Engineering project for organizing documents"""
    ENGINEERING_STANDARDS = [
        ('iso', 'ISO Standard'),
        ('api', 'API Standard'), 
        ('asme', 'ASME Standard'),
        ('astm', 'ASTM Standard'),
        ('dnv', 'DNV Standard'),
        ('custom', 'Custom Standard'),
    ]
    
    PROJECT_TYPES = [
        ('oil_gas', 'Oil & Gas'),
        ('petrochemical', 'Petrochemical'),
        ('refinery', 'Refinery'),
        ('offshore', 'Offshore Platform'),
        ('pipeline', 'Pipeline'),
        ('facility', 'Process Facility'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project_type = models.CharField(max_length=50, choices=PROJECT_TYPES, default='oil_gas')
    engineering_standard = models.CharField(max_length=50, choices=ENGINEERING_STANDARDS, default='iso')
    client_name = models.CharField(max_length=200, blank=True)
    project_number = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project_type', 'status']),
            models.Index(fields=['created_by', 'status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.project_type})"
    
    @property
    def document_count(self):
        return self.documents.count()
    
    @property
    def analysis_count(self):
        return Analysis.objects.filter(document__project=self).count()


class Document(models.Model):
    """Engineering document with metadata and file storage"""
    DOCUMENT_TYPES = [
        ('pid', 'P&ID Diagram'),
        ('isometric', 'Isometric Drawing'),
        ('plan', 'Plan View'),
        ('elevation', 'Elevation View'),
        ('section', 'Section View'),
        ('detail', 'Detail Drawing'),
        ('specification', 'Technical Specification'),
        ('datasheet', 'Equipment Datasheet'),
        ('manual', 'Operation Manual'),
        ('report', 'Engineering Report'),
        ('other', 'Other Document'),
    ]
    
    STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('error', 'Error'),
        ('archived', 'Archived'),
    ]
    
    QUALITY_LEVELS = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('issued', 'Issued for Construction'),
        ('as_built', 'As-Built'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    
    # File Information
    file = models.FileField(upload_to=document_upload_path)
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField(help_text="File size in bytes")
    file_type = models.CharField(max_length=50)  # pdf, dwg, png, etc.
    file_hash = models.CharField(max_length=64, blank=True)  # SHA-256 hash
    
    # Document Metadata
    title = models.CharField(max_length=300)
    drawing_number = models.CharField(max_length=100, blank=True)
    revision = models.CharField(max_length=20, blank=True)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    discipline = models.CharField(max_length=100, blank=True)  # Process, Mechanical, Electrical, etc.
    
    # Engineering Metadata
    plant_area = models.CharField(max_length=200, blank=True)
    system_tag = models.CharField(max_length=100, blank=True)
    equipment_list = models.JSONField(default=list, blank=True)  # List of equipment found
    
    # Status and Quality
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
    quality_level = models.CharField(max_length=20, choices=QUALITY_LEVELS, default='draft')
    
    # Processing Information
    ocr_text = models.TextField(blank=True)  # Extracted text content
    metadata_extracted = models.JSONField(default=dict, blank=True)  # AI-extracted metadata
    processing_notes = models.TextField(blank=True)
    
    # User and Time Tracking
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['project', 'document_type']),
            models.Index(fields=['status', 'uploaded_at']),
            models.Index(fields=['drawing_number']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'drawing_number', 'revision'],
                condition=models.Q(drawing_number__isnull=False) & ~models.Q(drawing_number=''),
                name='unique_drawing_per_project'
            )
        ]
    
    def __str__(self):
        return f"{self.title} ({self.document_type})"
    
    @property
    def display_name(self):
        """Human-readable document name"""
        if self.drawing_number:
            return f"{self.drawing_number} - {self.title}"
        return self.title
    
    @property
    def file_extension(self):
        return os.path.splitext(self.original_filename)[1].lower()
    
    def get_analysis_results(self):
        """Get all analysis results for this document"""
        return self.analyses.filter(status='completed').order_by('-created_at')


class Analysis(models.Model):
    """AI Analysis results for engineering documents"""
    ANALYSIS_TYPES = [
        ('symbol_detection', 'Symbol Detection'),
        ('equipment_identification', 'Equipment Identification'),
        ('piping_analysis', 'Piping & Instrumentation Analysis'),
        ('safety_review', 'Safety & Compliance Review'),
        ('completeness_check', 'Drawing Completeness Check'),
        ('standard_compliance', 'Standards Compliance'),
        ('full_analysis', 'Complete P&ID Analysis'),
    ]
    
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('low', 'Low Confidence'),
        ('medium', 'Medium Confidence'),
        ('high', 'High Confidence'),
        ('very_high', 'Very High Confidence'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='analyses')
    analysis_type = models.CharField(max_length=50, choices=ANALYSIS_TYPES)
    
    # Analysis Configuration
    configuration = models.JSONField(default=dict)  # Analysis parameters
    ai_model_used = models.CharField(max_length=100, blank=True)  # GPT-4, Claude, etc.
    
    # Results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    confidence_level = models.CharField(max_length=20, choices=CONFIDENCE_LEVELS, blank=True)
    results = models.JSONField(default=dict)  # Structured analysis results
    summary = models.TextField(blank=True)  # Human-readable summary
    
    # Equipment and Symbols Found
    equipment_detected = models.JSONField(default=list)  # List of equipment with coordinates
    symbols_detected = models.JSONField(default=list)  # List of symbols with coordinates
    piping_detected = models.JSONField(default=list)  # Piping connections and flow paths
    
    # Issues and Recommendations
    issues_found = models.JSONField(default=list)  # List of issues/errors detected
    recommendations = models.JSONField(default=list)  # Improvement suggestions
    compliance_notes = models.TextField(blank=True)  # Standards compliance notes
    
    # Processing Information
    processing_time = models.FloatField(null=True, blank=True)  # Seconds
    error_message = models.TextField(blank=True)
    
    # User and Time Tracking
    started_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='started_analyses')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document', 'analysis_type']),
            models.Index(fields=['status', 'created_at']),
        ]
        verbose_name_plural = 'Analyses'
    
    def __str__(self):
        return f"{self.analysis_type} for {self.document.title}"
    
    @property
    def duration(self):
        """Calculate analysis duration"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def equipment_count(self):
        return len(self.equipment_detected)
    
    @property
    def issues_count(self):
        return len(self.issues_found)


class Report(models.Model):
    """Generated reports combining multiple analyses"""
    REPORT_TYPES = [
        ('summary', 'Executive Summary'),
        ('detailed', 'Detailed Technical Report'),
        ('compliance', 'Compliance Assessment'),
        ('equipment_list', 'Equipment Schedule'),
        ('issues_report', 'Issues & Recommendations'),
        ('comparison', 'Drawing Comparison'),
        ('progress', 'Project Progress Report'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF Document'),
        ('docx', 'Word Document'),
        ('xlsx', 'Excel Spreadsheet'),
        ('html', 'HTML Report'),
        ('json', 'JSON Data'),
    ]
    
    STATUS_CHOICES = [
        ('generating', 'Generating'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports')
    documents = models.ManyToManyField(Document, related_name='reports')
    analyses = models.ManyToManyField(Analysis, related_name='reports')
    
    # Report Configuration
    title = models.CharField(max_length=300)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    configuration = models.JSONField(default=dict)  # Report generation settings
    
    # Generated Content
    content = models.JSONField(default=dict)  # Structured report data
    file = models.FileField(upload_to='reports/', blank=True)  # Generated file
    file_size = models.BigIntegerField(null=True, blank=True)
    
    # Status and Processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generating')
    generation_time = models.FloatField(null=True, blank=True)  # Seconds
    error_message = models.TextField(blank=True)
    
    # Expiration (for temporary reports)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # User and Time Tracking
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'report_type']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.report_type})"
    
    def is_expired(self):
        """Check if report has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class AnalysisSession(models.Model):
    """Tracking session for batch analysis operations"""
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='analysis_sessions')
    documents = models.ManyToManyField(Document, related_name='analysis_sessions')
    
    # Session Configuration
    session_name = models.CharField(max_length=200)
    analysis_types = models.JSONField(default=list)  # Types of analyses to run
    configuration = models.JSONField(default=dict)  # Batch configuration
    
    # Progress Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    total_documents = models.IntegerField(default=0)
    completed_documents = models.IntegerField(default=0)
    failed_documents = models.IntegerField(default=0)
    
    # Results Summary
    total_equipment_found = models.IntegerField(default=0)
    total_issues_found = models.IntegerField(default=0)
    processing_time = models.FloatField(null=True, blank=True)
    
    # User and Time Tracking
    started_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analysis_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.session_name} - {self.status}"
    
    @property
    def progress_percentage(self):
        """Calculate completion percentage"""
        if self.total_documents == 0:
            return 0
        return (self.completed_documents + self.failed_documents) / self.total_documents * 100
    
    def get_analyses(self):
        """Get all analyses created in this session"""
        return Analysis.objects.filter(
            document__in=self.documents.all(),
            created_at__gte=self.created_at
        )