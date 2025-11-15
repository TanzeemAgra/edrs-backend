from django.urls import path
from . import views

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Tags
    path('tags/', views.TagListCreateView.as_view(), name='tag-list-create'),
    path('tags/<int:pk>/', views.TagDetailView.as_view(), name='tag-detail'),
    
    # Posts
    path('posts/', views.PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),
    
    # Dashboard & Analytics
    path('dashboard/stats/', views.dashboard_stats_view, name='dashboard-stats'),
    path('analytics/track/', views.track_analytics_view, name='track-analytics'),
    path('activity/log/', views.log_activity_view, name='log-activity'),
    
    # Database Health Check
    path('database/health/', views.database_health_view, name='database-health'),
    
    # Document Library and Contact
    path('document-library/', views.document_library, name='document_library'),
    path('contact/', views.contact_create, name='contact_create'),
    path('contact/info/', views.contact_info, name='contact_info'),
    path('health/', views.health_check, name='health_check'),
]