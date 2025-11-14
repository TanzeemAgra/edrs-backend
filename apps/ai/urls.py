"""
EDRS AI Integration URL Configuration
Secure API endpoints for OpenAI features
"""

from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    # Health and status endpoints
    path('health/', views.openai_health_view, name='openai_health'),
    path('features/', views.ai_features_view, name='ai_features'),
    
    # AI functionality endpoints (authenticated)
    path('generate/', views.generate_content_view, name='generate_content'),
    path('analyze/', views.analyze_document_view, name='analyze_document'),
    path('suggestions/', views.get_suggestions_view, name='get_suggestions'),
]