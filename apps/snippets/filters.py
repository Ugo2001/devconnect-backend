# ============================================================================
# apps/snippets/filters.py
# ============================================================================

import django_filters
from .models import Snippet


class SnippetFilter(django_filters.FilterSet):
    """Custom filters for snippets"""
    author = django_filters.CharFilter(field_name='author__username')
    language = django_filters.CharFilter(field_name='language__slug')
    tag = django_filters.CharFilter(method='filter_by_tag')
    min_likes = django_filters.NumberFilter(field_name='likes_count', lookup_expr='gte')
    
    class Meta:
        model = Snippet
        fields = ['visibility', 'author', 'language']
    
    def filter_by_tag(self, queryset, name, value):
        return queryset.filter(tags__contains=[value])