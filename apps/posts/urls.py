# ============================================================================
# apps/posts/urls.py - MANUAL URL DEFINITION
# ============================================================================

from django.urls import path
from .views import PostViewSet, CommentViewSet, TagViewSet

urlpatterns = [
    # Posts
    path('', PostViewSet.as_view({'get': 'list', 'post': 'create'}), name='post-list'),
    path('<int:pk>/', PostViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='PostDetail'),
    path('<int:pk>/like/', PostViewSet.as_view({'post': 'like'}), name='post-like'),
    path('<int:pk>/unlike/', PostViewSet.as_view({'post': 'unlike'}), name='post-unlike'),
    path('<int:pk>/bookmark/', PostViewSet.as_view({'post': 'bookmark'}), name='post-bookmark'),
    path('<int:pk>/unbookmark/', PostViewSet.as_view({'post': 'unbookmark'}), name='post-unbookmark'),
    
    # Comments
    path('comments/', CommentViewSet.as_view({'get': 'list', 'post': 'create'}), name='comment-list'),
    path('comments/<int:pk>/', CommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='comment-detail'),
    
    # Tags
    path('tags/', TagViewSet.as_view({'get': 'list'}), name='tag-list'),
    path('tags/<int:pk>/', TagViewSet.as_view({'get': 'retrieve'}), name='tag-detail'),
]