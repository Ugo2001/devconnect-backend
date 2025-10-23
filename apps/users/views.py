# ============================================================================
# apps/users/views.py
# ============================================================================

from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend

from .models import Follow, UserProfile
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    UserUpdateSerializer, FollowSerializer
)
from .permissions import IsOwnerOrReadOnly

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management with search, filtering, and follow functionality
    """
    queryset = User.objects.select_related('profile').all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'bio']
    ordering_fields = ['reputation', 'created_at', 'posts_count']
    ordering = ['-reputation']
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.IsAuthenticatedOrReadOnly()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Annotate users with counts"""
        return User.objects.annotate(
            followers_count=Count('followers', distinct=True),
            following_count=Count('following', distinct=True),
            posts_count=Count('posts', filter=Q(posts__status='published'), distinct=True)
        )
    
    def create(self, request, *args, **kwargs):
        """Register a new user"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Return user data with tokens
        user_serializer = UserSerializer(user)
        
        return Response({
            'user': user_serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Registration successful!'
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update user profile - only own profile"""
        instance = self.get_object()
        
        # Check if user is updating their own profile
        if instance != request.user:
            return Response(
                {'detail': 'You can only update your own profile.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve user with caching"""
        user_id = kwargs.get('pk')
        cache_key = f'user_detail_{user_id}'
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # If not in cache, get from DB
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Cache for 5 minutes
        cache.set(cache_key, serializer.data, 300)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        """Follow a user"""
        user_to_follow = self.get_object()
        
        if user_to_follow == request.user:
            return Response(
                {'error': 'You cannot follow yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        
        if not created:
            return Response(
                {'message': 'Already following this user'},
                status=status.HTTP_200_OK
            )
        
        # Update counts
        request.user.following_count += 1
        request.user.save(update_fields=['following_count'])
        user_to_follow.followers_count += 1
        user_to_follow.save(update_fields=['followers_count'])
        
        # Invalidate cache
        cache.delete(f'user_detail_{user_to_follow.id}')
        cache.delete(f'user_detail_{request.user.id}')
        
        return Response(
            {'message': 'Successfully followed user'},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        """Unfollow a user"""
        user_to_unfollow = self.get_object()
        
        try:
            follow = Follow.objects.get(
                follower=request.user,
                following=user_to_unfollow
            )
            follow.delete()
            
            # Update counts
            request.user.following_count -= 1
            request.user.save(update_fields=['following_count'])
            user_to_unfollow.followers_count -= 1
            user_to_unfollow.save(update_fields=['followers_count'])
            
            # Invalidate cache
            cache.delete(f'user_detail_{user_to_unfollow.id}')
            cache.delete(f'user_detail_{request.user.id}')
            
            return Response(
                {'message': 'Successfully unfollowed user'},
                status=status.HTTP_200_OK
            )
        except Follow.DoesNotExist:
            return Response(
                {'error': 'You are not following this user'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        """Get user's followers"""
        user = self.get_object()
        followers = Follow.objects.filter(following=user).select_related('follower')
        serializer = FollowSerializer(followers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def following(self, request, pk=None):
        """Get users that this user is following"""
        user = self.get_object()
        following = Follow.objects.filter(follower=user).select_related('following')
        serializer = FollowSerializer(following, many=True)
        return Response(serializer.data)
