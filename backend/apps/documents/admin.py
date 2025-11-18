"""
Django Admin Configuration for EDRS Document Management
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Project, Document, Analysis, Report, AnalysisSession


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'project_type', 'status', 'document_count', 'client_name', 'created_at']
    list_filter = ['project_type', 'status', 'engineering_standard', 'created_at']
    search_fields = ['name', 'client_name', 'project_number', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'document_count', 'analysis_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'project_type', 'engineering_standard')
        }),
        ('Client & Location', {
            'fields': ('client_name', 'project_number', 'location')
        }),
        ('Status', {
            'fields': ('status', 'created_by')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'document_count', 'analysis_count'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'drawing_number', 'document_type', 'project', 'status', 'file_size_mb', 'uploaded_at']
    list_filter = ['document_type', 'status', 'quality_level', 'project__project_type', 'uploaded_at']
    search_fields = ['title', 'drawing_number', 'original_filename', 'project__name']
    readonly_fields = ['id', 'file_size', 'file_type', 'file_hash', 'uploaded_at', 'processed_at', 'updated_at']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('project', 'title', 'drawing_number', 'revision', 'document_type')
        }),
        ('File Information', {
            'fields': ('file', 'original_filename', 'file_size', 'file_type', 'file_hash')
        }),
        ('Engineering Data', {
            'fields': ('discipline', 'plant_area', 'system_tag', 'equipment_list'),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('status', 'quality_level', 'ocr_text', 'metadata_extracted', 'processing_notes'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'uploaded_by', 'uploaded_at', 'processed_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def file_size_mb(self, obj):
        if obj.file_size:
            return f"{obj.file_size / (1024*1024):.2f} MB"
        return "-"
    file_size_mb.short_description = "File Size"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project', 'uploaded_by')


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ['document', 'analysis_type', 'status', 'confidence_level', 'equipment_count', 'issues_count', 'created_at']
    list_filter = ['analysis_type', 'status', 'confidence_level', 'ai_model_used', 'created_at']
    search_fields = ['document__title', 'document__drawing_number', 'summary']
    readonly_fields = ['id', 'processing_time', 'duration', 'equipment_count', 'issues_count', 'created_at', 'started_at', 'completed_at']
    
    fieldsets = (
        ('Analysis Information', {
            'fields': ('document', 'analysis_type', 'ai_model_used', 'configuration')
        }),
        ('Status & Results', {
            'fields': ('status', 'confidence_level', 'summary', 'processing_time', 'duration')
        }),
        ('Detection Results', {
            'fields': ('equipment_detected', 'symbols_detected', 'piping_detected'),
            'classes': ('collapse',)
        }),
        ('Issues & Recommendations', {
            'fields': ('issues_found', 'recommendations', 'compliance_notes'),
            'classes': ('collapse',)
        }),
        ('Full Results', {
            'fields': ('results',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'started_by', 'created_at', 'started_at', 'completed_at', 'error_message'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('document', 'started_by')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'format', 'project', 'status', 'file_size_mb', 'created_at']
    list_filter = ['report_type', 'format', 'status', 'created_at']
    search_fields = ['title', 'project__name']
    readonly_fields = ['id', 'file_size', 'generation_time', 'is_expired', 'created_at', 'completed_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('title', 'report_type', 'format', 'project')
        }),
        ('Configuration', {
            'fields': ('configuration',),
            'classes': ('collapse',)
        }),
        ('Generated Content', {
            'fields': ('file', 'file_size', 'content'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'generation_time', 'error_message', 'expires_at', 'is_expired')
        }),
        ('System Information', {
            'fields': ('id', 'generated_by', 'created_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )
    
    def file_size_mb(self, obj):
        if obj.file_size:
            return f"{obj.file_size / (1024*1024):.2f} MB"
        return "-"
    file_size_mb.short_description = "File Size"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project', 'generated_by')


@admin.register(AnalysisSession)
class AnalysisSessionAdmin(admin.ModelAdmin):
    list_display = ['session_name', 'project', 'status', 'progress_display', 'total_equipment_found', 'total_issues_found', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['session_name', 'project__name']
    readonly_fields = ['id', 'progress_percentage', 'processing_time', 'created_at', 'completed_at']
    
    fieldsets = (
        ('Session Information', {
            'fields': ('session_name', 'project', 'analysis_types', 'configuration')
        }),
        ('Progress', {
            'fields': ('status', 'total_documents', 'completed_documents', 'failed_documents', 'progress_percentage')
        }),
        ('Results Summary', {
            'fields': ('total_equipment_found', 'total_issues_found', 'processing_time')
        }),
        ('System Information', {
            'fields': ('id', 'started_by', 'created_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )
    
    def progress_display(self, obj):
        percentage = obj.progress_percentage
        if percentage == 0:
            return "Not Started"
        elif percentage == 100:
            return "✅ Complete"
        else:
            return f"🔄 {percentage:.1f}%"
    progress_display.short_description = "Progress"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project', 'started_by')


# Customize admin site header and title
admin.site.site_header = "EDRS Document Management System"
admin.site.site_title = "EDRS Admin"
admin.site.index_title = "Engineering Document Record System"