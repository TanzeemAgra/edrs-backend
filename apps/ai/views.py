"""
EDRS AI Integration API Views
Secure endpoints for OpenAI functionality
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
import logging

# Import OpenAI service
try:
    from core.utils.openai_service import (
        openai_service, 
        generate_ai_content, 
        analyze_edrs_document,
        get_openai_status
    )
except ImportError:
    openai_service = None
    def generate_ai_content(*args, **kwargs):
        return None
    def analyze_edrs_document(*args, **kwargs):
        return None
    def get_openai_status():
        return {"status": "not_available", "message": "OpenAI service not installed"}

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([])  # Public endpoint for health checks
def openai_health_view(request):
    """
    OpenAI service health check endpoint
    """
    try:
        health_status = get_openai_status()
        
        return Response({
            'service': 'OpenAI Integration',
            'timestamp': request.META.get('HTTP_DATE', 'N/A'),
            'health': health_status,
            'features': {
                'text_generation': health_status.get('status') == 'healthy',
                'document_analysis': health_status.get('status') == 'healthy',
                'content_suggestions': health_status.get('status') == 'healthy',
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"OpenAI health check failed: {e}")
        return Response({
            'service': 'OpenAI Integration',
            'health': {
                'status': 'error',
                'message': f'Health check failed: {str(e)}'
            }
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_content_view(request):
    """
    Generate AI content based on user prompt
    Requires authentication for security
    """
    try:
        prompt = request.data.get('prompt', '')
        content_type = request.data.get('type', 'general')
        
        if not prompt:
            return Response({
                'error': 'Prompt is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Security: Limit prompt length
        if len(prompt) > 2000:
            return Response({
                'error': 'Prompt too long (max 2000 characters)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate content
        result = generate_ai_content(prompt, content_type)
        
        if result:
            logger.info(f"AI content generated for user {request.user.username}")
            return Response({
                'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
                'type': content_type,
                'result': result,
                'user': request.user.username,
                'success': True
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Failed to generate content. Check OpenAI service status.',
                'service_status': get_openai_status()
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        return Response({
            'error': 'Content generation failed',
            'details': str(e) if request.user.is_superuser else 'Internal error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_document_view(request):
    """
    Analyze document content using AI
    Requires authentication for security
    """
    try:
        content = request.data.get('content', '')
        analysis_type = request.data.get('analysis_type', 'summary')
        
        if not content:
            return Response({
                'error': 'Document content is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Security: Limit content length
        if len(content) > 10000:
            return Response({
                'error': 'Document too long (max 10,000 characters)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Valid analysis types
        valid_types = ['summary', 'keywords', 'sentiment', 'classification']
        if analysis_type not in valid_types:
            return Response({
                'error': f'Invalid analysis type. Must be one of: {", ".join(valid_types)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Analyze document
        result = analyze_edrs_document(content, analysis_type)
        
        if result:
            logger.info(f"Document analysis completed for user {request.user.username}")
            return Response({
                'content_length': len(content),
                'analysis_type': analysis_type,
                'result': result,
                'user': request.user.username,
                'success': True
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Failed to analyze document. Check OpenAI service status.',
                'service_status': get_openai_status()
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
    except Exception as e:
        logger.error(f"Document analysis failed: {e}")
        return Response({
            'error': 'Document analysis failed',
            'details': str(e) if request.user.is_superuser else 'Internal error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_suggestions_view(request):
    """
    Get AI-powered suggestions based on context
    """
    try:
        context = request.data.get('context', '')
        task = request.data.get('task', '')
        
        if not context or not task:
            return Response({
                'error': 'Both context and task are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Security: Limit input length
        if len(context) > 1000 or len(task) > 500:
            return Response({
                'error': 'Input too long (context: max 1000, task: max 500 characters)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get suggestions
        suggestions = openai_service.generate_suggestions(context, task) if openai_service else []
        
        if suggestions:
            logger.info(f"AI suggestions generated for user {request.user.username}")
            return Response({
                'context': context[:100] + '...' if len(context) > 100 else context,
                'task': task,
                'suggestions': suggestions,
                'count': len(suggestions),
                'user': request.user.username,
                'success': True
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Failed to generate suggestions. Check OpenAI service status.',
                'service_status': get_openai_status(),
                'suggestions': []
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
    except Exception as e:
        logger.error(f"Suggestion generation failed: {e}")
        return Response({
            'error': 'Suggestion generation failed',
            'details': str(e) if request.user.is_superuser else 'Internal error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_features_view(request):
    """
    Get available AI features and their status
    """
    try:
        openai_status = get_openai_status()
        
        features = {
            'text_generation': {
                'available': openai_status.get('status') == 'healthy',
                'description': 'Generate content based on prompts',
                'endpoint': '/api/ai/generate/',
                'method': 'POST'
            },
            'document_analysis': {
                'available': openai_status.get('status') == 'healthy',
                'description': 'Analyze documents for summary, keywords, sentiment',
                'endpoint': '/api/ai/analyze/',
                'method': 'POST'
            },
            'suggestions': {
                'available': openai_status.get('status') == 'healthy',
                'description': 'Get AI-powered suggestions based on context',
                'endpoint': '/api/ai/suggestions/',
                'method': 'POST'
            }
        }
        
        return Response({
            'ai_integration': openai_status,
            'features': features,
            'user': request.user.username,
            'is_staff': request.user.is_staff
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"AI features check failed: {e}")
        return Response({
            'error': 'Failed to check AI features',
            'details': str(e) if request.user.is_superuser else 'Internal error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)