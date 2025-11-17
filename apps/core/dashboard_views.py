"""
Dashboard API Views
Provides dashboard statistics and data endpoints
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
from datetime import datetime, timedelta
import random

@api_view(['GET'])
@permission_classes([])  # Allow unauthenticated access for development
def dashboard_stats(request):
    """Dashboard statistics endpoint"""
    
    # Mock data for development
    stats = {
        'total_projects': random.randint(15, 25),
        'active_projects': random.randint(8, 15),
        'completed_analyses': random.randint(45, 75),
        'pending_reviews': random.randint(3, 12),
        'critical_errors': random.randint(0, 5),
        'total_diagrams': random.randint(120, 200),
        'success_rate': round(random.uniform(85.0, 95.0), 1),
        'last_updated': datetime.now().isoformat()
    }
    
    return Response(stats)

@api_view(['GET'])
@permission_classes([])  # Allow unauthenticated access for development
def dashboard_charts(request):
    """Dashboard charts data endpoint"""
    
    # Mock chart data
    charts = {
        'analysis_trend': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'datasets': [{
                'label': 'Analyses Completed',
                'data': [12, 19, 15, 25, 22, 18],
                'borderColor': 'rgb(59, 130, 246)',
                'backgroundColor': 'rgba(59, 130, 246, 0.1)'
            }]
        },
        'error_distribution': {
            'labels': ['Critical', 'High', 'Medium', 'Low'],
            'datasets': [{
                'data': [5, 15, 35, 45],
                'backgroundColor': [
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)', 
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(34, 197, 94, 0.8)'
                ]
            }]
        },
        'project_types': {
            'labels': ['Upstream', 'Midstream', 'Downstream', 'Refining'],
            'datasets': [{
                'data': [30, 25, 25, 20],
                'backgroundColor': [
                    'rgba(99, 102, 241, 0.8)',
                    'rgba(236, 72, 153, 0.8)',
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(251, 191, 36, 0.8)'
                ]
            }]
        }
    }
    
    return Response(charts)

@api_view(['GET'])
@permission_classes([])  # Allow unauthenticated access for development  
def dashboard_notifications(request):
    """Dashboard notifications endpoint"""
    
    # Mock notifications
    notifications = [
        {
            'id': 1,
            'title': 'New P&ID Analysis Complete',
            'message': 'Analysis for Project Alpha-101 has been completed with 3 critical findings.',
            'type': 'success',
            'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
            'read': False
        },
        {
            'id': 2,
            'title': 'Review Required',
            'message': 'P&ID diagram Beta-205 requires engineering review.',
            'type': 'warning', 
            'timestamp': (datetime.now() - timedelta(hours=5)).isoformat(),
            'read': False
        },
        {
            'id': 3,
            'title': 'System Update',
            'message': 'Enhanced P&ID analysis engine has been deployed successfully.',
            'type': 'info',
            'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
            'read': True
        },
        {
            'id': 4,
            'title': 'Monthly Report Ready',
            'message': 'Your monthly P&ID analysis report is now available for download.',
            'type': 'info',
            'timestamp': (datetime.now() - timedelta(days=2)).isoformat(),
            'read': True
        }
    ]
    
    return Response({
        'notifications': notifications,
        'unread_count': len([n for n in notifications if not n['read']])
    })

@api_view(['GET'])
@permission_classes([])  # Allow unauthenticated access for development
def dashboard_activities(request):
    """Dashboard recent activities endpoint"""
    
    # Mock activities
    activities = [
        {
            'id': 1,
            'action': 'analysis_completed',
            'description': 'Completed P&ID analysis for "Offshore Platform Charlie"',
            'user': 'Mohammed Agra',
            'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
            'project': 'Charlie-301',
            'status': 'success'
        },
        {
            'id': 2,
            'action': 'diagram_uploaded',
            'description': 'Uploaded new P&ID diagram "Process Unit B-102"',
            'user': 'Engineering Team',
            'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
            'project': 'Bravo-102',
            'status': 'info'
        },
        {
            'id': 3,
            'action': 'project_created',
            'description': 'Created new project "Gas Processing Facility Delta"',
            'user': 'Project Manager',
            'timestamp': (datetime.now() - timedelta(hours=3)).isoformat(),
            'project': 'Delta-400',
            'status': 'success'
        },
        {
            'id': 4,
            'action': 'review_completed', 
            'description': 'Reviewed and approved 5 P&ID error findings',
            'user': 'Senior Engineer',
            'timestamp': (datetime.now() - timedelta(hours=6)).isoformat(),
            'project': 'Alpha-101',
            'status': 'success'
        },
        {
            'id': 5,
            'action': 'error_flagged',
            'description': 'Critical safety issue flagged in diagram Echo-501',
            'user': 'Analysis System',
            'timestamp': (datetime.now() - timedelta(hours=8)).isoformat(),
            'project': 'Echo-501', 
            'status': 'warning'
        }
    ]
    
    return Response({
        'activities': activities,
        'total_count': len(activities)
    })