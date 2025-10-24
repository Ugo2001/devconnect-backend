from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user operations"""
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]
    
    def get_queryset(self):
        """Annotate users with counts"""
        return User.objects.annotate(
            total_followers=Count('followers', distinct=True),
            total_following=Count('following', distinct=True),
            total_posts=Count('posts', filter=Q(posts__status='published'), distinct=True)
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
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        """Follow a user"""
        user_to_follow = self.get_object()
        
        if user_to_follow == request.user:
            return Response(
                {'detail': 'You cannot follow yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Import here to avoid circular import
        from .models import Follow
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        
        if not created:
            return Response(
                {'detail': 'You are already following this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {'detail': 'Successfully followed user.'},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        """Unfollow a user"""
        user_to_unfollow = self.get_object()
        
        from .models import Follow
        
        try:
            follow = Follow.objects.get(
                follower=request.user,
                following=user_to_unfollow
            )
            follow.delete()
            return Response(
                {'detail': 'Successfully unfollowed user.'},
                status=status.HTTP_200_OK
            )
        except Follow.DoesNotExist:
            return Response(
                {'detail': 'You are not following this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )