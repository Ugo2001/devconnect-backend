# ============================================================================
# apps/snippets/models.py
# ============================================================================

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Language(models.Model):
    """Programming languages for syntax highlighting"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    extension = models.CharField(max_length=10)  # e.g., .py, .js
    color = models.CharField(max_length=7, default='#000000')  # Hex color
    snippets_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'languages'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Snippet(models.Model):
    """Code snippets shared by users"""
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('unlisted', 'Unlisted'),
        ('private', 'Private'),
    ]
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='snippets')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(max_length=500, blank=True)
    code = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, related_name='snippets')
    
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    tags = models.JSONField(default=list)  # List of tags
    
    # Stats
    views_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    forks_count = models.IntegerField(default=0)
    
    # Forking
    forked_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='forks'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'snippets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['language', '-created_at']),
            models.Index(fields=['visibility', '-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Snippet.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        super().save(*args, **kwargs)


class SnippetComment(models.Model):
    """Comments on snippets"""
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='snippet_comments')
    content = models.TextField(max_length=1000)
    line_number = models.IntegerField(null=True, blank=True)  # For line-specific comments
    
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'snippet_comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.snippet.title}"


class SnippetLike(models.Model):
    """Likes for snippets"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='snippet_likes')
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'snippet_likes'
        unique_together = ('user', 'snippet')
    
    def __str__(self):
        return f"{self.user.username} likes {self.snippet.title}"


