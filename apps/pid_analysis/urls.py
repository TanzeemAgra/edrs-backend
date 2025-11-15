"""
EDRS P&ID Analysis URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    PIDProjectViewSet, PIDDiagramViewSet, 
    AnalysisSessionViewSet, AnalysisResultViewSet
)
from .views.document_library import (
    DocumentLibraryView, 
    S3DocumentBrowserView, 
    DownloadDocumentView,
    user_storage_stats
)

app_name = 'pid_analysis'

# Create main router
router = DefaultRouter()
router.register(r'pid-analysis/projects', PIDProjectViewSet, basename='pidproject')
router.register(r'pid-analysis/analysis-sessions', AnalysisSessionViewSet, basename='pidanalysissession')

# Create nested routers for project-related resources
projects_router = routers.NestedDefaultRouter(router, r'pid-analysis/projects', lookup='project')
projects_router.register(r'diagrams', PIDDiagramViewSet, basename='project-diagrams')

# Create nested router for diagram-related resources
diagrams_router = routers.NestedDefaultRouter(projects_router, r'diagrams', lookup='diagram')
diagrams_router.register(r'results', AnalysisResultViewSet, basename='diagram-results')

urlpatterns = [
    # Main router URLs
    path('', include(router.urls)),
    
    # Nested router URLs
    path('', include(projects_router.urls)),
    path('', include(diagrams_router.urls)),
    
    # Document Library URLs
    path('pid-analysis/document-library/', DocumentLibraryView.as_view(), name='document-library'),
    path('pid-analysis/s3-browser/', S3DocumentBrowserView.as_view(), name='s3-browser'),
    path('pid-analysis/download-document/', DownloadDocumentView.as_view(), name='download-document'),
    path('pid-analysis/storage-stats/', user_storage_stats, name='storage-stats'),
]