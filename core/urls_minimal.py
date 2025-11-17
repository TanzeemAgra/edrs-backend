from django.http import JsonResponse
from django.urls import path

def health_check(request):
    return JsonResponse({'status': 'ok', 'message': 'EDRS Backend is running'})

def root_view(request):
    return JsonResponse({'message': 'EDRS Backend API', 'health': '/health/'})

urlpatterns = [
    path('', root_view),
    path('health/', health_check),
]