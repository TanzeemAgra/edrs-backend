from rest_framework import serializers
from .models import Category, Tag, Post


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model"""
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model"""
    
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags_data = TagSerializer(source='tags', many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'excerpt', 'slug', 'author', 'author_name',
            'category', 'category_name', 'tags', 'tags_data', 'featured_image',
            'status', 'published_at', 'views_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'views_count', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class PostListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Post list view"""
    
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags_count = serializers.IntegerField(source='tags.count', read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'excerpt', 'slug', 'author_name', 'category_name',
            'tags_count', 'featured_image', 'status', 'published_at',
            'views_count', 'created_at'
        ]