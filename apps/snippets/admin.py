# ============================================================================
# apps/snippets/admin.py
# ============================================================================

from django.contrib import admin
from .models import Snippet, Language, SnippetComment, SnippetLike


@admin.register(Snippet)
class SnippetAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'language', 'visibility', 'views_count', 'likes_count', 'created_at']
    list_filter = ['visibility', 'language', 'created_at']
    search_fields = ['title', 'description', 'code', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'extension', 'snippets_count', 'color']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SnippetComment)
class SnippetCommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'snippet', 'line_number', 'created_at', 'likes_count']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username']


@admin.register(SnippetLike)
class SnippetLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'snippet', 'created_at']
    list_filter = ['created_at']
