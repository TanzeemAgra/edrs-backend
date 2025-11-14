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