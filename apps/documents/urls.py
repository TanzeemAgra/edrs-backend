"""
URL Configuration for EDRS Document Management API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API URL patterns
urlpatterns = [
    # Projects
    path('projects/', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<uuid:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    
    # Documents
    path('documents/', views.DocumentListCreateView.as_view(), name='document-list-create'),
    path('documents/<uuid:pk>/', views.DocumentDetailView.as_view(), name='document-detail'),
    path('documents/<uuid:document_id>/download/', views.download_document, name='document-download'),
    
    # Bulk operations
    path('documents/bulk-upload/', views.bulk_upload_documents, name='document-bulk-upload'),
    
    # Analysis
    path('analyses/', views.AnalysisListCreateView.as_view(), name='analysis-list-create'),
    path('analyses/<uuid:pk>/', views.AnalysisDetailView.as_view(), name='analysis-detail'),
    path('analyses/start-batch/', views.start_batch_analysis, name='analysis-start-batch'),
    
    # Analysis Sessions
    path('analysis-sessions/', views.AnalysisSessionListCreateView.as_view(), name='analysis-session-list-create'),
    path('analysis-sessions/<uuid:pk>/', views.AnalysisSessionDetailView.as_view(), name='analysis-session-detail'),
    
    # Reports
    path('reports/', views.ReportListCreateView.as_view(), name='report-list-create'),
    path('reports/<uuid:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('reports/<uuid:report_id>/download/', views.download_report, name='report-download'),
    
    # Dashboard and Statistics
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    path('document-library/stats/', views.document_library_stats, name='document-library-stats'),
    
    # PDF Reports
    path('documents/<uuid:document_id>/pdf-report/', views.download_document_pdf_report, name='document-pdf-report'),
    path('projects/<uuid:project_id>/pdf-report/', views.download_project_pdf_report, name='project-pdf-report'),
]

app_name = 'documents'