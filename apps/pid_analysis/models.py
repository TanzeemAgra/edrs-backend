"""
EDRS P&ID Analysis Models
Advanced Oil & Gas Process Diagram Analysis System
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class PIDProject(models.Model):
    """Oil & Gas P&ID Project Management"""
    
    PROJECT_TYPES = [
        ('upstream', 'Upstream (Exploration & Production)'),
        ('midstream', 'Midstream (Transportation & Storage)'),
        ('downstream', 'Downstream (Refining & Petrochemicals)'),
        ('lng', 'LNG (Liquefied Natural Gas)'),
        ('offshore', 'Offshore Platform'),
        ('onshore', 'Onshore Facility'),
        ('pipeline', 'Pipeline System'),
        ('refinery', 'Refinery Unit'),
        ('petrochemical', 'Petrochemical Plant'),
    ]
    
    STANDARDS = [
        ('isa_5_1', 'ISA-5.1 (Instrumentation Symbols)'),
        ('iso_10628', 'ISO 10628 (Flow Diagrams)'),
        ('iec_62424', 'IEC 62424 (Process Control Systems)'),
        ('api_14c', 'API 14C (Offshore Safety Systems)'),
        ('asme_y14_2', 'ASME Y14.2 (Line Conventions)'),
        ('shell_dcs', 'Shell DEP (Design Engineering Practice)'),
        ('exxonmobil_pgs', 'ExxonMobil PGS Standards'),
        ('bp_gsp', 'BP GSP (General Specification)'),
        ('custom', 'Custom Company Standards'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Project name (e.g., 'Haradh Gas Plant Expansion')")
    description = models.TextField(blank=True, help_text="Project description and scope")
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES, default='upstream')
    engineering_standard = models.CharField(max_length=20, choices=STANDARDS, default='isa_5_1')
    
    # Project metadata
    field_name = models.CharField(max_length=100, blank=True, help_text="Oil/Gas field name")
    facility_code = models.CharField(max_length=20, blank=True, help_text="Facility identifier")
    process_unit = models.CharField(max_length=100, blank=True, help_text="Process unit description")
    
    # Client & Engineering
    client_company = models.CharField(max_length=200, blank=True)
    engineering_contractor = models.CharField(max_length=200, blank=True)
    project_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'P&ID Project'
        verbose_name_plural = 'P&ID Projects'
    
    def __str__(self):
        return f"{self.name} ({self.get_project_type_display()})"


class PIDDiagram(models.Model):
    """Individual P&ID Drawing Management"""
    
    DIAGRAM_TYPES = [
        ('process_flow', 'Process Flow Diagram (PFD)'),
        ('piping_instrumentation', 'Piping & Instrumentation Diagram (P&ID)'),
        ('utility_flow', 'Utility Flow Diagram (UFD)'),
        ('safety_shutdown', 'Safety Shutdown Diagram (SSD)'),
        ('fire_gas', 'Fire & Gas System (F&G)'),
        ('electrical_single', 'Electrical Single Line'),
        ('control_logic', 'Control Logic Diagram'),
        ('loop_diagram', 'Instrument Loop Diagram'),
    ]
    
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('analyzed', 'Analysis Complete'),
        ('reviewed', 'Engineering Review'),
        ('approved', 'Approved'),
        ('revision_required', 'Revision Required'),
        ('error', 'Processing Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(PIDProject, on_delete=models.CASCADE, related_name='diagrams')
    
    # Drawing identification
    drawing_number = models.CharField(max_length=50, help_text="Drawing number (e.g., 'P&ID-100-001')")
    drawing_title = models.CharField(max_length=200, help_text="Drawing title")
    diagram_type = models.CharField(max_length=25, choices=DIAGRAM_TYPES, default='piping_instrumentation')
    revision = models.CharField(max_length=10, default='A', help_text="Drawing revision")
    sheet_number = models.CharField(max_length=20, blank=True, help_text="Sheet number (e.g., '1 of 3')")
    
    # File management
    original_file = models.FileField(
        upload_to='pid_diagrams/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'dwg', 'png', 'jpg', 'jpeg', 'tiff'])],
        help_text="Upload P&ID file (PDF, DWG, PNG, JPG, TIFF)"
    )
    file_size = models.BigIntegerField(null=True, blank=True)
    
    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Analysis results
    total_errors_found = models.IntegerField(default=0)
    critical_errors = models.IntegerField(default=0)
    high_priority_errors = models.IntegerField(default=0)
    medium_priority_errors = models.IntegerField(default=0)
    low_priority_errors = models.IntegerField(default=0)
    
    # Engineering metadata
    process_area = models.CharField(max_length=100, blank=True, help_text="Process area (e.g., 'Gas Processing')")
    operating_pressure = models.CharField(max_length=50, blank=True, help_text="Operating pressure range")
    operating_temperature = models.CharField(max_length=50, blank=True, help_text="Operating temperature range")
    design_phase = models.CharField(max_length=50, blank=True, help_text="Engineering phase (FEED, Detail, etc.)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['project', 'drawing_number', 'revision']
        verbose_name = 'P&ID Diagram'
        verbose_name_plural = 'P&ID Diagrams'
    
    def __str__(self):
        return f"{self.drawing_number} Rev.{self.revision} - {self.drawing_title}"


class ErrorCategory(models.Model):
    """P&ID Error Classification System"""
    
    CATEGORY_TYPES = [
        ('instrumentation', 'Instrumentation & Control'),
        ('piping', 'Piping & Flow'),
        ('equipment', 'Equipment & Vessels'),
        ('safety', 'Safety Systems'),
        ('tagging', 'Tag Numbering'),
        ('drafting', 'Drafting Standards'),
        ('logical', 'Process Logic'),
        ('mechanical', 'Mechanical Design'),
        ('electrical', 'Electrical Systems'),
        ('utilities', 'Utilities & Services'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(help_text="Category description and scope")
    color_code = models.CharField(max_length=7, default='#FF0000', help_text="Hex color for UI display")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category_type', 'name']
        verbose_name = 'Error Category'
        verbose_name_plural = 'Error Categories'
    
    def __str__(self):
        return f"{self.get_category_type_display()} - {self.name}"


class PIDAnalysisResult(models.Model):
    """Individual Error Detection Results"""
    
    SEVERITY_LEVELS = [
        ('critical', 'Critical - Safety/Operations Impact'),
        ('high', 'High - Major Engineering Issue'),
        ('medium', 'Medium - Standard Compliance'),
        ('low', 'Low - Minor Improvement'),
        ('info', 'Information - Best Practice'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected - False Positive'),
        ('fixed', 'Fixed'),
        ('deferred', 'Deferred to Future Revision'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    diagram = models.ForeignKey(PIDDiagram, on_delete=models.CASCADE, related_name='analysis_results')
    category = models.ForeignKey(ErrorCategory, on_delete=models.PROTECT)
    
    # Error details
    error_title = models.CharField(max_length=200, help_text="Brief error description")
    error_description = models.TextField(help_text="Detailed error description")
    root_cause = models.TextField(help_text="Root cause analysis")
    recommended_fix = models.TextField(help_text="Engineering recommendation")
    
    # Classification
    severity_level = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    confidence_score = models.FloatField(
        default=0.0, 
        help_text="AI confidence score (0-1)",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # Location in diagram
    element_tag = models.CharField(max_length=50, blank=True, help_text="Equipment/instrument tag")
    line_number = models.CharField(max_length=50, blank=True, help_text="Piping line number")
    coordinates_x = models.FloatField(null=True, blank=True, help_text="X coordinate in diagram")
    coordinates_y = models.FloatField(null=True, blank=True, help_text="Y coordinate in diagram")
    
    # Standards compliance
    violated_standard = models.CharField(max_length=100, blank=True, help_text="Violated engineering standard")
    standard_reference = models.CharField(max_length=200, blank=True, help_text="Standard clause/section")
    
    # Status and workflow
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_errors')
    review_comments = models.TextField(blank=True)
    review_date = models.DateTimeField(null=True, blank=True)
    
    # AI processing metadata
    llm_model_used = models.CharField(max_length=100, blank=True, help_text="LLM model used for detection")
    processing_time = models.FloatField(null=True, blank=True, help_text="Processing time in seconds")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-severity_level', '-confidence_score', '-created_at']
        indexes = [
            models.Index(fields=['diagram', 'severity_level']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['element_tag']),
        ]
        verbose_name = 'Analysis Result'
        verbose_name_plural = 'Analysis Results'
    
    def __str__(self):
        return f"{self.error_title} ({self.get_severity_level_display()})"


class PIDElement(models.Model):
    """Detected P&ID Elements (Equipment, Instruments, Lines)"""
    
    ELEMENT_TYPES = [
        # Equipment
        ('pump', 'Pump'),
        ('compressor', 'Compressor'),
        ('vessel', 'Pressure Vessel'),
        ('tank', 'Storage Tank'),
        ('heat_exchanger', 'Heat Exchanger'),
        ('turbine', 'Turbine'),
        ('generator', 'Generator'),
        ('separator', 'Separator'),
        ('filter', 'Filter'),
        ('knockout_drum', 'Knockout Drum'),
        
        # Instruments
        ('flow_transmitter', 'Flow Transmitter (FT)'),
        ('pressure_transmitter', 'Pressure Transmitter (PT)'),
        ('temperature_transmitter', 'Temperature Transmitter (TT)'),
        ('level_transmitter', 'Level Transmitter (LT)'),
        ('flow_indicator', 'Flow Indicator (FI)'),
        ('pressure_indicator', 'Pressure Indicator (PI)'),
        ('temperature_indicator', 'Temperature Indicator (TI)'),
        ('control_valve', 'Control Valve'),
        ('safety_valve', 'Safety/Relief Valve'),
        
        # Piping
        ('piping_line', 'Piping Line'),
        ('valve_gate', 'Gate Valve'),
        ('valve_ball', 'Ball Valve'),
        ('valve_globe', 'Globe Valve'),
        ('valve_check', 'Check Valve'),
        ('valve_butterfly', 'Butterfly Valve'),
        ('orifice_plate', 'Orifice Plate'),
    ]
    
    diagram = models.ForeignKey(PIDDiagram, on_delete=models.CASCADE, related_name='elements')
    element_type = models.CharField(max_length=30, choices=ELEMENT_TYPES)
    
    # Identification
    tag_number = models.CharField(max_length=50, help_text="Element tag number")
    description = models.CharField(max_length=200, blank=True)
    
    # Properties
    size = models.CharField(max_length=50, blank=True, help_text="Size/rating")
    specification = models.CharField(max_length=100, blank=True, help_text="Material/spec")
    service = models.CharField(max_length=100, blank=True, help_text="Process service")
    
    # Location
    coordinates_x = models.FloatField(null=True, blank=True)
    coordinates_y = models.FloatField(null=True, blank=True)
    
    # AI extraction metadata
    confidence_score = models.FloatField(default=0.0)
    extracted_by_ai = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['element_type', 'tag_number']
        unique_together = ['diagram', 'tag_number']
        verbose_name = 'P&ID Element'
        verbose_name_plural = 'P&ID Elements'
    
    def __str__(self):
        return f"{self.tag_number} ({self.get_element_type_display()})"


class AnalysisSession(models.Model):
    """P&ID Analysis Processing Session"""
    
    SESSION_STATUS = [
        ('initiated', 'Analysis Initiated'),
        ('preprocessing', 'Preprocessing Diagram'),
        ('ocr_processing', 'OCR Text Extraction'),
        ('element_detection', 'Element Detection'),
        ('error_analysis', 'Error Analysis'),
        ('post_processing', 'Post Processing'),
        ('completed', 'Analysis Completed'),
        ('failed', 'Analysis Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    diagram = models.ForeignKey(PIDDiagram, on_delete=models.CASCADE, related_name='analysis_sessions')
    
    # Processing configuration
    llm_model = models.CharField(max_length=100, default='gpt-4')
    analysis_depth = models.CharField(max_length=20, default='standard', 
                                    choices=[('quick', 'Quick Scan'), ('standard', 'Standard Analysis'), ('deep', 'Deep Analysis')])
    include_recommendations = models.BooleanField(default=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='initiated')
    progress_percentage = models.IntegerField(default=0)
    
    # Results summary
    total_elements_detected = models.IntegerField(default=0)
    total_errors_found = models.IntegerField(default=0)
    processing_time_seconds = models.FloatField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Analysis Session'
        verbose_name_plural = 'Analysis Sessions'
    
    def __str__(self):
        return f"Analysis {self.id} - {self.diagram.drawing_number} ({self.status})"