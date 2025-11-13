from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('me/', views.UserDetailView.as_view(), name='user-me'),
    path('profile/', views.user_profile_view, name='user-profile'),
    path('profile/update/', views.update_user_profile_view, name='user-profile-update'),
    
    # Extended profiles (MongoDB)
    path('profiles/', views.UserProfileListCreateView.as_view(), name='userprofile-list-create'),
    path('profiles/<str:user_id>/', views.UserProfileDetailView.as_view(), name='userprofile-detail'),
]