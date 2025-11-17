from django.urls import path
from . import views
from . import dashboard_views
from . import simple_upload

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
    path('dashboard/stats/', dashboard_views.dashboard_stats, name='dashboard-stats'),
    path('dashboard/charts/', dashboard_views.dashboard_charts, name='dashboard-charts'),
    path('dashboard/notifications/', dashboard_views.dashboard_notifications, name='dashboard-notifications'),
    path('dashboard/activities/', dashboard_views.dashboard_activities, name='dashboard-activities'),
    path('analytics/track/', views.track_analytics_view, name='track-analytics'),
    path('activity/log/', views.log_activity_view, name='log-activity'),
    
    # Database Health Check
    path('database/health/', views.database_health_view, name='database-health'),
    
    # Simple Document Upload (temporary solution)
    path('upload-document/', simple_upload.simple_document_upload, name='simple-upload'),
    path('my-documents/', simple_upload.list_user_documents, name='my-documents'),
    path('test-s3/', simple_upload.test_s3_connection, name='test-s3'),
    
    # Document Library and Contact
    path('document-library/', views.document_library, name='document_library'),
    path('contact/', views.contact_create, name='contact_create'),
    path('contact/info/', views.contact_info, name='contact_info'),
    path('health/', views.health_check, name='health_check'),
]