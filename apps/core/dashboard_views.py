from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Dashboard views (minimal implementations)

@api_view(['GET'])
def dashboard_stats(request):
    return Response({
        'users': 0,
        'documents': 0,
        'projects': 0,
        'uploads_today': 0
    })

@api_view(['GET'])
def dashboard_charts(request):
    return Response({
        'uploads_by_day': [],
        'users_by_month': [],
        'document_types': {}
    })

@api_view(['GET'])
def dashboard_notifications(request):
    return Response({
        'notifications': [],
        'unread_count': 0
    })

@api_view(['GET'])
def dashboard_activities(request):
    return Response({
        'activities': [],
        'recent_activities': []
    })