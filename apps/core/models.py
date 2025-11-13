from django.db import models
from django.contrib.auth import get_user_model
from mongoengine import Document, StringField, DateTimeField, IntField, DictField
import datetime

User = get_user_model()


# PostgreSQL Models
class BaseModel(models.Model):
    """Base model with common fields"""
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class Category(BaseModel):
    """Category model for organizing content"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Tag(BaseModel):
    """Tag model for content tagging"""
    
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Post(BaseModel):
    """Post model for content management"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    featured_image = models.ImageField(upload_to='posts/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-published_at']),
            models.Index(fields=['category', '-created_at']),
        ]
    
    def __str__(self):
        return self.title


# MongoDB Models (using mongoengine)
class Analytics(Document):
    """Analytics data stored in MongoDB"""
    
    user_id = IntField(required=True)
    event_type = StringField(max_length=50, required=True)
    event_data = DictField()
    timestamp = DateTimeField(default=datetime.datetime.utcnow)
    session_id = StringField(max_length=100)
    ip_address = StringField(max_length=45)
    user_agent = StringField(max_length=500)
    
    meta = {
        'collection': 'analytics',
        'indexes': ['user_id', 'event_type', 'timestamp']
    }


class ActivityLog(Document):
    """Activity log stored in MongoDB"""
    
    user_id = IntField(required=True)
    action = StringField(max_length=100, required=True)
    resource_type = StringField(max_length=50)
    resource_id = StringField(max_length=50)
    details = DictField()
    timestamp = DateTimeField(default=datetime.datetime.utcnow)
    ip_address = StringField(max_length=45)
    
    meta = {
        'collection': 'activity_logs',
        'indexes': ['user_id', 'action', 'timestamp']
    }