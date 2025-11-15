from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.db import connection
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Category, Tag, Post, Analytics, ActivityLog
from .serializers import CategorySerializer, TagSerializer, PostSerializer, PostListSerializer

# Import OpenAI service for health checks
try:
    from core.utils.openai_service import get_openai_status
except ImportError:
    def get_openai_status():
        return {"status": "not_available", "message": "OpenAI service not configured"}


# Category Views
class CategoryListCreateView(generics.ListCreateAPIView):
    """List all categories or create a new category"""
    
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a category"""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'


# Tag Views
class TagListCreateView(generics.ListCreateAPIView):
    """List all tags or create a new tag"""
    
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a tag"""
    
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]


# Post Views
class PostListCreateView(generics.ListCreateAPIView):
    """List all posts or create a new post"""
    
    queryset = Post.objects.select_related('author', 'category').prefetch_related('tags')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'category', 'tags']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['created_at', 'published_at', 'views_count', 'title']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostListSerializer
        return PostSerializer


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a post"""
    
    queryset = Post.objects.select_related('author', 'category').prefetch_related('tags')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats_view(request):
    """Get dashboard statistics"""
    
    stats = {
        'total_posts': Post.objects.count(),
        'published_posts': Post.objects.filter(status='published').count(),
        'draft_posts': Post.objects.filter(status='draft').count(),
        'total_categories': Category.objects.filter(is_active=True).count(),
        'total_tags': Tag.objects.count(),
        'recent_posts': PostListSerializer(
            Post.objects.order_by('-created_at')[:5],
            many=True
        ).data
    }
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def track_analytics_view(request):
    """Track analytics event"""
    
    try:
        Analytics(
            user_id=request.user.id,
            event_type=request.data.get('event_type', ''),
            event_data=request.data.get('event_data', {}),
            session_id=request.data.get('session_id', ''),
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        ).save()
        
        return Response({'message': 'Analytics tracked'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def log_activity_view(request):
    """Log user activity"""
    
    try:
        ActivityLog(
            user_id=request.user.id,
            action=request.data.get('action', ''),
            resource_type=request.data.get('resource_type', ''),
            resource_id=request.data.get('resource_id', ''),
            details=request.data.get('details', {}),
            ip_address=request.META.get('REMOTE_ADDR', '')
        ).save()
        
        return Response({'message': 'Activity logged'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([])  # No authentication required
def database_health_view(request):
    """
    Dual database health check endpoint for integration validation
    Tests both PostgreSQL (primary) and MongoDB (documents) connectivity
    """
    
    # Test PostgreSQL (Primary Database)
    postgresql_status = {}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()[0]
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Test table counts
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
            """)
            table_count = cursor.fetchone()[0]
        
        postgresql_status = {
            'status': 'connected',
            'version': db_version.split()[1] if 'PostgreSQL' in db_version else 'Unknown',
            'host': connection.settings_dict.get('HOST', 'localhost'),
            'database': connection.settings_dict.get('NAME', 'unknown'),
            'total_tables': table_count,
            'record_counts': {
                'users': User.objects.count(),
                'categories': Category.objects.count(),
                'tags': Tag.objects.count(),
                'posts': Post.objects.count(),
            },
            'railway_integration': 'railway' in str(connection.settings_dict.get('HOST', '')).lower()
        }
        
    except Exception as e:
        postgresql_status = {
            'status': 'error',
            'error': str(e)
        }
    
    # Test MongoDB (Document Database) 
    mongodb_status = {}
    try:
        import mongoengine
        from django.conf import settings
        
        if hasattr(settings, 'MONGODB_SETTINGS'):
            # Try to connect and test
            mongodb_settings = settings.MONGODB_SETTINGS.copy()
            mongodb_settings.update({
                'connect': False,
                'serverSelectionTimeoutMS': 3000,
                'connectTimeoutMS': 3000,
            })
            
            # Disconnect and reconnect
            mongoengine.disconnect()
            conn = mongoengine.connect(**mongodb_settings)
            
            # Test connection
            db = conn.get_database()
            server_info = conn.server_info()
            collections = db.list_collection_names()
            
            # Count documents
            document_counts = {}
            try:
                document_counts = {
                    'analytics': Analytics.objects.count(),
                    'activity_logs': ActivityLog.objects.count(),
                }
            except:
                document_counts = {'analytics': 0, 'activity_logs': 0}
            
            mongodb_status = {
                'status': 'connected',
                'version': server_info.get('version', 'Unknown'),
                'host': mongodb_settings['host'],
                'database': mongodb_settings['db'],
                'collections': collections,
                'document_counts': document_counts
            }
            
        else:
            mongodb_status = {
                'status': 'not_configured',
                'message': 'MongoDB settings not found in configuration'
            }
            
    except ImportError:
        mongodb_status = {
            'status': 'not_available',
            'message': 'mongoengine package not installed'
        }
    except Exception as e:
        mongodb_status = {
            'status': 'disconnected',
            'error': str(e),
            'message': 'MongoDB service not available (this is normal if not configured)'
        }
    
    # Test OpenAI Service
    openai_status = get_openai_status()
    
    # Overall system status
    system_healthy = postgresql_status.get('status') == 'connected'
    mongodb_available = mongodb_status.get('status') == 'connected'
    openai_available = openai_status.get('status') == 'healthy'
    
    return Response({
        'status': 'success' if system_healthy else 'partial',
        'message': 'Dual database system status',
        'timestamp': timezone.now().isoformat(),
        'databases': {
            'postgresql': {
                **postgresql_status,
                'role': 'Primary database for all CRUD operations',
                'priority': 'required'
            },
            'mongodb': {
                **mongodb_status,
                'role': 'Document storage for analytics and logs', 
                'priority': 'optional'
            }
        },
        'ai_services': {
            'openai': {
                **openai_status,
                'role': 'AI-powered document analysis and suggestions',
                'priority': 'optional'
            }
        },
        'architecture': {
            'primary_database': 'PostgreSQL (Railway)',
            'document_database': 'MongoDB (Optional)',
            'system_operational': system_healthy,
            'full_features': mongodb_available,
            'recommendations': {
                'postgresql': 'Fully operational - all core features working',
                'mongodb': 'Add Railway MongoDB service or MongoDB Atlas for analytics features' if not mongodb_available else 'Operational - analytics features available',
                'openai': 'API key configured - AI features available' if openai_available else 'Add OpenAI API key for AI-powered features'
            }
        }
    }, status=status.HTTP_200_OK if system_healthy else status.HTTP_206_PARTIAL_CONTENT)


# Additional views for document library and contact
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import EmailMessage
import json
import logging
from .models import Document, ContactInquiry

# Get logger for this module  
logger = logging.getLogger(__name__)


def document_library(request):
    """
    Handle document library requests for EDRS system
    """
    try:
        if request.method == 'GET':
            # Get query parameters
            document_type = request.GET.get('type', '')
            search_term = request.GET.get('search', '')
            category = request.GET.get('category', '')
            
            # Start with all documents
            documents = Document.objects.all()
            
            # Apply filters
            if document_type:
                documents = documents.filter(document_type__icontains=document_type)
            if search_term:
                documents = documents.filter(title__icontains=search_term)
            if category:
                documents = documents.filter(category__icontains=category)
            
            # Convert to list of dictionaries
            document_list = []
            for doc in documents:
                document_list.append({
                    'id': doc.id,
                    'title': doc.title,
                    'description': doc.description,
                    'document_type': doc.document_type,
                    'category': doc.category,
                    'file_path': doc.file_path,
                    'created_at': doc.created_at.isoformat(),
                    'updated_at': doc.updated_at.isoformat(),
                })
            
            return JsonResponse({
                'status': 'success',
                'documents': document_list,
                'count': len(document_list),
                'filters_applied': {
                    'type': document_type,
                    'search': search_term,
                    'category': category,
                }
            })
        
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    except Exception as e:
        logger.error(f"Document library error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def contact_create(request):
    """
    Handle contact form submissions with email notifications to mohammed.agra@rejlers.ae
    """
    try:
        data = json.loads(request.body)
        
        # Create contact inquiry
        contact = ContactInquiry.objects.create(
            name=data.get('name', ''),
            email=data.get('email', ''),
            company=data.get('company', ''),
            phone=data.get('phone', ''),
            inquiry_type=data.get('inquiry_type', 'general'),
            subject=data.get('subject', ''),
            message=data.get('message', '')
        )
        
        # Send notification email to Mohammed Agra
        try:
            send_notification_email(contact)
            logger.info(f"Contact notification sent to Mohammed Agra for inquiry #{contact.id}")
        except Exception as email_error:
            logger.error(f"Failed to send notification email: {str(email_error)}")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Your inquiry has been submitted successfully. We will contact you soon.',
            'inquiry_id': contact.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Contact form error: {str(e)}")
        return JsonResponse({'error': 'Failed to process your request'}, status=500)


def contact_info(request):
    """
    Return contact information for EDRS
    """
    return JsonResponse({
        'company': 'Rejlers AB - EDRS Division',
        'email': 'mohammed.agra@rejlers.ae',
        'phone': '+971 XX XXX XXXX',
        'address': 'UAE Office',
        'business_hours': 'Sunday - Thursday: 8:00 AM - 6:00 PM GST',
        'emergency_contact': 'For urgent technical support, please email mohammed.agra@rejlers.ae',
        'response_time': 'We typically respond within 24 hours during business days'
    })


def health_check(request):
    """
    Simple health check endpoint
    """
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'service': 'EDRS Backend API'
    })


def send_notification_email(contact_inquiry):
    """
    Send professional email notification to Mohammed Agra about new contact inquiry
    """
    from django.conf import settings
    
    # Get recipient from settings or fallback to direct email
    recipient_email = getattr(settings, 'CONTACT_RECIPIENTS', ['mohammed.agra@rejlers.ae'])[0]
    
    # Create professional email content
    subject = f'New EDRS Contact Inquiry - {contact_inquiry.inquiry_type.title()} from {contact_inquiry.company or contact_inquiry.name}'
    
    message_body = f"""
Dear Mohammed,

You have received a new contact inquiry through the EDRS system.

INQUIRY DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Name: {contact_inquiry.name}
Company: {contact_inquiry.company or 'Not specified'}
Email: {contact_inquiry.email}
Phone: {contact_inquiry.phone or 'Not provided'}

Inquiry Type: {contact_inquiry.inquiry_type.replace('_', ' ').title()}
Subject: {contact_inquiry.subject}

Message:
{contact_inquiry.message}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Submission Details:
- Inquiry ID: #{contact_inquiry.id}
- Submitted: {contact_inquiry.submitted_at.strftime('%Y-%m-%d at %H:%M:%S UTC')}
- Source: Website Contact Form

NEXT STEPS:
Please respond to {contact_inquiry.email} within 24 hours during business days.

Best regards,
EDRS Notification System
Rejlers AB
"""
    
    try:
        # Use Django's email system (configured with AWS SES)
        email = EmailMessage(
            subject=subject,
            body=message_body,
            from_email='EDRS Support <noreply@rejlers.ae>',
            to=[recipient_email],
            reply_to=[contact_inquiry.email],
        )
        
        # Add headers for better email handling
        email.extra_headers = {
            'X-EDRS-Inquiry-ID': str(contact_inquiry.id),
            'X-EDRS-Type': contact_inquiry.inquiry_type,
            'X-Client-Email': contact_inquiry.email,
        }
        
        email.send(fail_silently=False)
        logger.info(f"Notification email sent successfully to {recipient_email} for inquiry #{contact_inquiry.id}")
        
    except Exception as e:
        logger.error(f"Failed to send notification email: {str(e)}")
        raise e