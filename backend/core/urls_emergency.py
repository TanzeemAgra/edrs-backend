"""
Absolutely minimal URL configuration - emergency test
"""
from django.http import JsonResponse
from django.urls import path

def health(request):
    return JsonResponse({"status": "alive"})

urlpatterns = [
    path('health/', health),
]