# ============================================================================
# apps/snippets/views.py
# ============================================================================

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db.models import Q, F
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend

from .models import Snippet, Language, SnippetComment, SnippetLike
from .serializers import (
    SnippetListSerializer, SnippetDetailSerializer,
    SnippetCreateUpdateSerializer, LanguageSerializer,
    SnippetCommentSerializer
)
from .permissions import IsAuthorOrReadOnly
from .filters import SnippetFilter


class SnippetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing code snippets
    """
    queryset = Snippet.objects.select_related('author', 'language').filter(visibility='public')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SnippetFilter
    search_fields = ['title', 'description', 'code']
    ordering_fields = ['created_at', 'views_count', 'likes_count', 'forks_count']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SnippetListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SnippetCreateUpdateSerializer
        return SnippetDetailSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAuthorOrReadOnly()]
        return super().get_permissions()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Show user's own private/unlisted snippets
        if self.request.user.is_authenticated:
            queryset = Snippet.objects.select_related('author', 'language').filter(
                Q(visibility='public') | Q(author=self.request.user)
            )
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve snippet and increment view count"""
        instance = self.get_object()
        
        # Increment view count (use cache to prevent spam)
        cache_key = f'snippet_view_{instance.id}_{request.META.get("REMOTE_ADDR")}'
        if not cache.get(cache_key):
            instance.views_count = F('views_count') + 1
            instance.save(update_fields=['views_count'])
            instance.refresh_from_db()
            cache.set(cache_key, True, 300)  # 5 minutes
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        snippet = serializer.save(author=self.request.user)
        
        # Update user's snippet count
        self.request.user.snippets_count = F('snippets_count') + 1
        self.request.user.save(update_fields=['snippets_count'])
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like a snippet"""
        snippet = self.get_object()
        
        like, created = SnippetLike.objects.get_or_create(
            user=request.user,
            snippet=snippet
        )
        
        if created:
            snippet.likes_count = F('likes_count') + 1
            snippet.save(update_fields=['likes_count'])
            snippet.refresh_from_db()
            
            # Give author reputation points
            snippet.author.update_reputation(3)
            
            return Response(
                {'message': 'Snippet liked', 'likes_count': snippet.likes_count},
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {'message': 'Already liked', 'likes_count': snippet.likes_count},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        """Unlike a snippet"""
        snippet = self.get_object()
        
        try:
            like = SnippetLike.objects.get(user=request.user, snippet=snippet)
            like.delete()
            
            snippet.likes_count = F('likes_count') - 1
            snippet.save(update_fields=['likes_count'])
            snippet.refresh_from_db()
            
            # Remove reputation points
            snippet.author.update_reputation(-3)
            
            return Response(
                {'message': 'Snippet unliked', 'likes_count': snippet.likes_count},
                status=status.HTTP_200_OK
            )
        except SnippetLike.DoesNotExist:
            return Response(
                {'error': 'Snippet not liked'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def fork(self, request, pk=None):
        """Fork a snippet"""
        original_snippet = self.get_object()
        
        # Create a copy
        forked_snippet = Snippet.objects.create(
            author=request.user,
            title=f"{original_snippet.title} (Fork)",
            description=original_snippet.description,
            code=original_snippet.code,
            language=original_snippet.language,
            visibility='public',
            tags=original_snippet.tags,
            forked_from=original_snippet
        )
        
        # Update fork count
        original_snippet.forks_count = F('forks_count') + 1
        original_snippet.save(update_fields=['forks_count'])
        
        # Update user's snippet count
        request.user.snippets_count = F('snippets_count') + 1
        request.user.save(update_fields=['snippets_count'])
        
        serializer = SnippetDetailSerializer(forked_snippet, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def my_snippets(self, request):
        """Get current user's snippets"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        snippets = Snippet.objects.filter(author=request.user)
        page = self.paginate_queryset(snippets)
        
        if page is not None:
            serializer = SnippetListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = SnippetListSerializer(snippets, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending snippets"""
        cache_key = 'trending_snippets'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Get snippets with high engagement
        from django.utils import timezone
        from datetime import timedelta
        
        seven_days_ago = timezone.now() - timedelta(days=7)
        snippets = Snippet.objects.filter(
            visibility='public',
            created_at__gte=seven_days_ago
        ).order_by('-likes_count', '-views_count')[:20]
        
        serializer = SnippetListSerializer(snippets, many=True, context={'request': request})
        cache.set(cache_key, serializer.data, 600)  # Cache for 10 minutes
        
        return Response(serializer.data)


class SnippetCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for snippet comments"""
    queryset = SnippetComment.objects.select_related('author', 'snippet').all()
    serializer_class = SnippetCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        snippet_id = self.request.query_params.get('snippet', None)
        
        if snippet_id:
            queryset = queryset.filter(snippet_id=snippet_id)
        
        return queryset
    
    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)
        
        # Give snippet author reputation points
        comment.snippet.author.update_reputation(1)


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for programming languages"""
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['snippets_count', 'name']
    ordering = ['-snippets_count']
    
    @action(detail=True, methods=['get'])
    def snippets(self, request, pk=None):
        """Get all snippets for this language"""
        language = self.get_object()
        snippets = language.snippets.filter(visibility='public')
        
        page = self.paginate_queryset(snippets)
        if page is not None:
            serializer = SnippetListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = SnippetListSerializer(snippets, many=True, context={'request': request})
        return Response(serializer.data)

