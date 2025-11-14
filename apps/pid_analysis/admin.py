"""
EDRS P&ID Analysis Django Admin Configuration
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    PIDProject, PIDDiagram, ErrorCategory,
    PIDAnalysisResult, PIDElement, AnalysisSession
)


@admin.register(PIDProject)
class PIDProjectAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'project_type', 'engineering_standard', 
        'client_company', 'project_manager', 'total_diagrams',
        'created_at', 'is_active'
    ]
    list_filter = [
        'project_type', 'engineering_standard', 'is_active', 'created_at'
    ]
    search_fields = [
        'name', 'field_name', 'facility_code', 'client_company'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Project Information', {
            'fields': (
                'name', 'description', 'project_type', 'engineering_standard'
            )
        }),
        ('Technical Details', {
            'fields': (
                'field_name', 'facility_code', 'process_unit'
            )
        }),
        ('Project Team', {
            'fields': (
                'client_company', 'engineering_contractor', 'project_manager'
            )
        }),
        ('Status', {
            'fields': (
                'is_active', 'created_at', 'updated_at'
            )
        }),
    )
    
    def total_diagrams(self, obj):
        return obj.diagrams.count()
    total_diagrams.short_description = 'Diagrams'


@admin.register(PIDDiagram)
class PIDDiagramAdmin(admin.ModelAdmin):
    list_display = [
        'drawing_number', 'drawing_title', 'revision', 'project',
        'status', 'total_errors_found', 'uploaded_by', 'created_at'
    ]
    list_filter = [
        'status', 'diagram_type', 'project__project_type', 'created_at'
    ]
    search_fields = [
        'drawing_number', 'drawing_title', 'project__name'
    ]
    readonly_fields = [
        'file_size', 'processing_started_at', 'processing_completed_at',
        'total_errors_found', 'critical_errors', 'high_priority_errors',
        'medium_priority_errors', 'low_priority_errors', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Drawing Information', {
            'fields': (
                'project', 'drawing_number', 'drawing_title', 'diagram_type',
                'revision', 'sheet_number'
            )
        }),
        ('File Management', {
            'fields': (
                'original_file', 'file_size', 'uploaded_by'
            )
        }),
        ('Processing Status', {
            'fields': (
                'status', 'processing_started_at', 'processing_completed_at'
            )
        }),
        ('Analysis Results', {
            'fields': (
                'total_errors_found', 'critical_errors', 'high_priority_errors',
                'medium_priority_errors', 'low_priority_errors'
            )
        }),
        ('Engineering Metadata', {
            'fields': (
                'process_area', 'operating_pressure', 'operating_temperature',
                'design_phase'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project', 'uploaded_by')


@admin.register(ErrorCategory)
class ErrorCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'color_preview', 'is_active']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'description']
    
    def color_preview(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 2px 8px; color: white; border-radius: 3px;">{}</span>',
            obj.color_code,
            obj.color_code
        )
    color_preview.short_description = 'Color'


@admin.register(PIDAnalysisResult)
class PIDAnalysisResultAdmin(admin.ModelAdmin):
    list_display = [
        'error_title', 'diagram', 'category', 'severity_level',
        'status', 'confidence_score', 'reviewed_by', 'created_at'
    ]
    list_filter = [
        'severity_level', 'status', 'category__category_type',
        'diagram__project', 'created_at'
    ]
    search_fields = [
        'error_title', 'error_description', 'element_tag', 
        'diagram__drawing_number'
    ]
    readonly_fields = [
        'confidence_score', 'llm_model_used', 'processing_time', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Error Information', {
            'fields': (
                'diagram', 'category', 'error_title', 'error_description',
                'root_cause', 'recommended_fix'
            )
        }),
        ('Classification', {
            'fields': (
                'severity_level', 'confidence_score', 'status'
            )
        }),
        ('Location', {
            'fields': (
                'element_tag', 'line_number', 'coordinates_x', 'coordinates_y'
            )
        }),
        ('Standards Compliance', {
            'fields': (
                'violated_standard', 'standard_reference'
            )
        }),
        ('Review Information', {
            'fields': (
                'reviewed_by', 'review_comments', 'review_date'
            )
        }),
        ('AI Processing', {
            'fields': (
                'llm_model_used', 'processing_time'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'diagram', 'category', 'reviewed_by'
        )


@admin.register(PIDElement)
class PIDElementAdmin(admin.ModelAdmin):
    list_display = [
        'tag_number', 'element_type', 'diagram', 'service',
        'confidence_score', 'extracted_by_ai', 'created_at'
    ]
    list_filter = [
        'element_type', 'extracted_by_ai', 'diagram__project'
    ]
    search_fields = [
        'tag_number', 'description', 'service', 'diagram__drawing_number'
    ]
    readonly_fields = ['confidence_score', 'extracted_by_ai', 'created_at']
    
    fieldsets = (
        ('Element Information', {
            'fields': (
                'diagram', 'element_type', 'tag_number', 'description'
            )
        }),
        ('Properties', {
            'fields': (
                'size', 'specification', 'service'
            )
        }),
        ('Location', {
            'fields': (
                'coordinates_x', 'coordinates_y'
            )
        }),
        ('AI Metadata', {
            'fields': (
                'confidence_score', 'extracted_by_ai', 'created_at'
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(AnalysisSession)
class AnalysisSessionAdmin(admin.ModelAdmin):
    list_display = [
        'short_id', 'diagram', 'status', 'analysis_depth',
        'progress_percentage', 'total_errors_found', 'started_at', 'initiated_by'
    ]
    list_filter = [
        'status', 'analysis_depth', 'llm_model', 'started_at'
    ]
    search_fields = [
        'diagram__drawing_number', 'initiated_by__username'
    ]
    readonly_fields = [
        'total_elements_detected', 'total_errors_found', 'processing_time_seconds',
        'started_at', 'completed_at'
    ]
    
    fieldsets = (
        ('Session Information', {
            'fields': (
                'diagram', 'llm_model', 'analysis_depth', 'include_recommendations',
                'initiated_by'
            )
        }),
        ('Processing Status', {
            'fields': (
                'status', 'progress_percentage', 'error_message'
            )
        }),
        ('Results', {
            'fields': (
                'total_elements_detected', 'total_errors_found', 'processing_time_seconds'
            )
        }),
        ('Timestamps', {
            'fields': (
                'started_at', 'completed_at'
            )
        }),
    )
    
    def short_id(self, obj):
        return str(obj.id)[:8]
    short_id.short_description = 'Session ID'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'diagram', 'initiated_by'
        )


# Admin site customization
admin.site.site_header = "EDRS - P&ID Analysis Administration"
admin.site.site_title = "EDRS Admin"
admin.site.index_title = "P&ID Analysis Management"