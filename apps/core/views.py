from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Minimal views to prevent import errors

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok', 'app': 'core'})

@api_view(['GET'])
def database_health_view(request):
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        return Response({'database': 'connected'})
    except Exception as e:
        return Response({'database': 'error', 'message': str(e)[:100]})

@api_view(['GET'])
def document_library(request):
    return Response({'message': 'Document library endpoint'})

@api_view(['POST'])  
def contact_create(request):
    return Response({'message': 'Contact form submitted'})

@api_view(['GET'])
def contact_info(request):
    return Response({'message': 'Contact info endpoint'})

# Analytics endpoints (minimal)
@api_view(['POST'])
def track_analytics_view(request):
    return Response({'tracked': True})

@api_view(['POST'])  
def log_activity_view(request):
    return Response({'logged': True})

# Category endpoints (minimal)
class CategoryListCreateView:
    def as_view(self):
        def view(request):
            return JsonResponse({'categories': []})
        return view

class CategoryDetailView:
    def as_view(self):
        def view(request, slug):
            return JsonResponse({'category': slug})
        return view

# Tag endpoints (minimal)
class TagListCreateView:
    def as_view(self):
        def view(request):
            return JsonResponse({'tags': []})
        return view

class TagDetailView:
    def as_view(self):
        def view(request, pk):
            return JsonResponse({'tag': pk})
        return view

# Post endpoints (minimal)
class PostListCreateView:
    def as_view(self):
        def view(request):
            return JsonResponse({'posts': []})
        return view

class PostDetailView:
    def as_view(self):
        def view(request, slug):
            return JsonResponse({'post': slug})
        return view