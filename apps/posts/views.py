# ============================================================================
# apps/posts/views.py - FIXED VERSION
# ============================================================================

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q, F
from django.core.cache import cache
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType
import logging

from .models import Post, Comment, Tag, Like, Bookmark
from .serializers import (
    PostListSerializer, PostDetailSerializer,
    PostCreateUpdateSerializer, CommentSerializer, TagSerializer
)
from .permissions import IsAuthorOrReadOnly
from .filters import PostFilter

logger = logging.getLogger(__name__)


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog posts with full-text search
    """
    queryset = Post.objects.select_related('author').prefetch_related('tags').filter(status='published')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['published_at', 'views_count', 'likes_count', 'comments_count']
    ordering = ['-published_at']
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAuthorOrReadOnly()]
        return super().get_permissions()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Allow authors to see their own drafts
        if self.request.user.is_authenticated:
            queryset = Post.objects.select_related('author').prefetch_related('tags').filter(
                Q(status='published') | Q(author=self.request.user)
            )
        
        # Full-text search
        search_query = self.request.query_params.get('search', None)
        if search_query:
            search_vector = SearchVector('title', weight='A') + SearchVector('content', weight='B')
            search_query_obj = SearchQuery(search_query)
            queryset = queryset.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query_obj)
            ).filter(search=search_query_obj).order_by('-rank')
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve post and increment view count"""
        instance = self.get_object()
        
        # Increment view count (use cache to prevent spam)
        cache_key = f'post_view_{instance.id}_{request.META.get("REMOTE_ADDR")}'
        if not cache.get(cache_key):
            instance.views_count = F('views_count') + 1
            instance.save(update_fields=['views_count'])
            instance.refresh_from_db()
            cache.set(cache_key, True, 300)  # 5 minutes
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        
        # Set published_at if status is published
        if post.status == 'published' and not post.published_at:
            post.published_at = timezone.now()
            post.save()
        
        # Update user's post count
        self.request.user.posts_count = F('posts_count') + 1
        self.request.user.save(update_fields=['posts_count'])
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """Like a post"""
        post = self.get_object()
        
        # Get the ContentType for Post model
        post_content_type = ContentType.objects.get_for_model(Post)
        
        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type=post_content_type,
            object_id=post.id
        )
        
        if created:
            post.likes_count = F('likes_count') + 1
            post.save(update_fields=['likes_count'])
            post.refresh_from_db()
            
            # Give author reputation points
            try:
                post.author.update_reputation(5)
            except Exception as e:
                logger.warning(f"Failed to update reputation: {e}")
            
            return Response(
                {'message': 'Post liked', 'likes_count': post.likes_count},
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {'message': 'Already liked', 'likes_count': post.likes_count},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        """Unlike a post"""
        post = self.get_object()
        
        # Get the ContentType for Post model
        post_content_type = ContentType.objects.get_for_model(Post)
        
        try:
            like = Like.objects.get(
                user=request.user,
                content_type=post_content_type,
                object_id=post.id
            )
            like.delete()
            
            post.likes_count = F('likes_count') - 1
            post.save(update_fields=['likes_count'])
            post.refresh_from_db()
            
            # Remove reputation points from author
            try:
                post.author.update_reputation(-5)
            except Exception as e:
                logger.warning(f"Failed to update reputation: {e}")
            
            return Response(
                {'message': 'Post unliked', 'likes_count': post.likes_count},
                status=status.HTTP_200_OK
            )
        except Like.DoesNotExist:
            return Response(
                {'error': 'Post not liked'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def bookmark(self, request, pk=None):
        """Bookmark a post"""
        post = self.get_object()
        
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            post=post
        )
        
        if created:
            post.bookmarks_count = F('bookmarks_count') + 1
            post.save(update_fields=['bookmarks_count'])
            post.refresh_from_db()
            
            return Response(
                {'message': 'Post bookmarked', 'bookmarks_count': post.bookmarks_count},
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {'message': 'Already bookmarked', 'bookmarks_count': post.bookmarks_count},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unbookmark(self, request, pk=None):
        """Remove bookmark from post"""
        post = self.get_object()
        
        try:
            bookmark = Bookmark.objects.get(user=request.user, post=post)
            bookmark.delete()
            
            post.bookmarks_count = F('bookmarks_count') - 1
            post.save(update_fields=['bookmarks_count'])
            post.refresh_from_db()
            
            return Response(
                {'message': 'Bookmark removed', 'bookmarks_count': post.bookmarks_count},
                status=status.HTTP_200_OK
            )
        except Bookmark.DoesNotExist:
            return Response(
                {'error': 'Post not bookmarked'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def feed(self, request):
        """Get personalized feed for authenticated user"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get posts from followed users
        following_ids = request.user.following.values_list('following_id', flat=True)
        posts = Post.objects.filter(
            author_id__in=following_ids,
            status='published'
        ).select_related('author').prefetch_related('tags')[:20]
        
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending posts based on recent activity"""
        cache_key = 'trending_posts'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Posts with high engagement in last 7 days
        from datetime import timedelta
        
        seven_days_ago = timezone.now() - timedelta(days=7)
        posts = Post.objects.filter(
            status='published',
            published_at__gte=seven_days_ago
        ).order_by('-likes_count', '-comments_count', '-views_count')[:20]
        
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        
        try:
            cache.set(cache_key, serializer.data, 600)  # Cache for 10 minutes
        except Exception as e:
            logger.warning(f"Failed to cache trending posts: {e}")
        
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing comments"""
    queryset = Comment.objects.select_related('author', 'post').all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        post_id = self.request.query_params.get('post', None)
        
        if post_id:
            queryset = queryset.filter(post_id=post_id, parent__isnull=True)
        
        return queryset
    
    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)
        
        # Update post comment count
        post = comment.post
        post.comments_count = F('comments_count') + 1
        post.save(update_fields=['comments_count'])
        
        # Give author reputation points
        try:
            post.author.update_reputation(2)
        except Exception as e:
            logger.warning(f"Failed to update reputation: {e}")
    
    def perform_destroy(self, instance):
        # Update post comment count
        post = instance.post
        post.comments_count = F('comments_count') - 1
        post.save(update_fields=['comments_count'])
        
        instance.delete()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """Like a comment"""
        comment = self.get_object()
        
        # Get the ContentType for Comment model
        comment_content_type = ContentType.objects.get_for_model(Comment)
        
        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type=comment_content_type,
            object_id=comment.id
        )
        
        if created:
            comment.likes_count = F('likes_count') + 1
            comment.save(update_fields=['likes_count'])
            comment.refresh_from_db()
            
            return Response(
                {'message': 'Comment liked', 'likes_count': comment.likes_count},
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {'message': 'Already liked', 'likes_count': comment.likes_count},
            status=status.HTTP_200_OK
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for browsing tags"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['posts_count', 'name']
    ordering = ['-posts_count']
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get all posts with this tag"""
        tag = self.get_object()
        posts = tag.posts.filter(status='published')
        
        # Apply pagination
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)