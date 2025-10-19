# ============================================================================
# apps/posts/filters.py
# ============================================================================

import django_filters
from .models import Post


class PostFilter(django_filters.FilterSet):
    """Custom filters for posts"""
    author = django_filters.CharFilter(field_name='author__username')
    tag = django_filters.CharFilter(field_name='tags__slug')
    min_likes = django_filters.NumberFilter(field_name='likes_count', lookup_expr='gte')
    date_from = django_filters.DateFilter(field_name='published_at', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='published_at', lookup_expr='lte')
    
    class Meta:
        model = Post
        fields = ['status', 'author', 'tag']