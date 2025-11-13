from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='auth-login'),
    path('register/', views.register_view, name='auth-register'),
    path('logout/', views.logout_view, name='auth-logout'),
    path('user/', views.user_view, name='auth-user'),
    path('change-password/', views.change_password_view, name='auth-change-password'),
    path('password-reset/', views.password_reset_view, name='auth-password-reset'),
    path('password-reset-confirm/', views.password_reset_confirm_view, name='auth-password-reset-confirm'),
    path('refresh-token/', views.refresh_token_view, name='auth-refresh-token'),
]