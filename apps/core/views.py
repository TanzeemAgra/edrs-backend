from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.db import connection
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Category, Tag, Post, Analytics, ActivityLog
from .serializers import CategorySerializer, TagSerializer, PostSerializer, PostListSerializer


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
    Database health check endpoint for integration validation
    This endpoint can be used by frontend to verify database connectivity
    """
    
    try:
        # Test basic database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()[0]
        
        # Test model operations
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        stats = {
            'database_status': 'healthy',
            'postgresql_version': db_version.split()[1] if 'PostgreSQL' in db_version else 'Unknown',
            'connection_status': 'connected',
            'table_counts': {
                'users': User.objects.count(),
                'categories': Category.objects.count(),
                'tags': Tag.objects.count(),
                'posts': Post.objects.count(),
            },
            'timestamp': timezone.now().isoformat(),
            'railway_integration': 'postgresql' in str(connection.settings_dict.get('NAME', '')).lower() or 
                                 'railway' in str(connection.settings_dict.get('HOST', '')).lower()
        }
        
        # Test table existence
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
            """)
            table_count = cursor.fetchone()[0]
            stats['total_tables'] = table_count
        
        return Response({
            'status': 'success',
            'message': 'Database integration is working correctly',
            'data': stats
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': 'Database integration failed',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)