"""
EDRS P&ID Analysis URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

app_name = 'pid_analysis'

# Create main router
router = DefaultRouter()
router.register(r'pid-analysis/projects', views.PIDProjectViewSet, basename='pidproject')
router.register(r'pid-analysis/analysis-sessions', views.AnalysisSessionViewSet, basename='pidanalysissession')

# Create nested routers for project-related resources
projects_router = routers.NestedDefaultRouter(router, r'pid-analysis/projects', lookup='project')
projects_router.register(r'diagrams', views.PIDDiagramViewSet, basename='project-diagrams')

# Create nested router for diagram-related resources
diagrams_router = routers.NestedDefaultRouter(projects_router, r'diagrams', lookup='diagram')
diagrams_router.register(r'results', views.AnalysisResultViewSet, basename='diagram-results')

urlpatterns = [
    # Main router URLs
    path('', include(router.urls)),
    
    # Nested router URLs
    path('', include(projects_router.urls)),
    path('', include(diagrams_router.urls)),
]