# ============================================================================
# apps/posts/serializers.py
# ============================================================================

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Tag, Like, Bookmark

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'description', 'posts_count']
        read_only_fields = ['id', 'slug', 'posts_count']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author', 'parent', 'content', 'content_html',
            'likes_count', 'is_edited', 'created_at', 'updated_at',
            'replies', 'is_liked'
        ]
        read_only_fields = ['id', 'content_html', 'likes_count', 'created_at', 'updated_at']
    
    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'avatar': obj.author.avatar.url if obj.author.avatar else None
        }
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(
                user=request.user,
                content_type='comment',
                object_id=obj.id
            ).exists()
        return False


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    reading_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'cover_image', 'author',
            'tags', 'status', 'views_count', 'likes_count', 'comments_count',
            'bookmarks_count', 'published_at', 'created_at', 'updated_at',
            'is_liked', 'is_bookmarked', 'reading_time'
        ]
    
    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'full_name': obj.author.full_name,
            'avatar': obj.author.avatar.url if obj.author.avatar else None
        }
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(
                user=request.user,
                content_type='post',
                object_id=obj.id
            ).exists()
        return False
    
    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Bookmark.objects.filter(user=request.user, post=obj).exists()
        return False
    
    def get_reading_time(self, obj):
        # Estimate reading time (200 words per minute)
        word_count = len(obj.content.split())
        minutes = max(1, round(word_count / 200))
        return f"{minutes} min read"


class PostDetailSerializer(PostListSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ['content', 'content_html', 'comments']


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'excerpt', 'cover_image',
            'status', 'tags', 'meta_description'
        ]
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        
        # Handle tags
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name.lower())
            post.tags.add(tag)
            if created or not tag.posts_count:
                tag.posts_count = tag.posts.count()
                tag.save()
        
        return post
    
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        
        # Update post fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update tags if provided
        if tags_data is not None:
            instance.tags.clear()
            for tag_name in tags_data:
                tag, created = Tag.objects.get_or_create(name=tag_name.lower())
                instance.tags.add(tag)
        
        return instance