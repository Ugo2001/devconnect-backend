# ============================================================================
# Database Migration Helpers - apps/posts/migrations/0002_add_search_vector.py
# ============================================================================

"""
Custom migration to add full-text search support
"""

from django.contrib.postgres.operations import TrigramExtension, UnaccentExtension
from django.contrib.postgres.search import SearchVector
from django.db import migrations


def compute_search_vectors(apps, schema_editor):
    Post = apps.get_model('posts', 'Post')
    
    for post in Post.objects.all():
        post.search_vector = SearchVector('title', weight='A') + \
                            SearchVector('content', weight='B')
        post.save(update_fields=['search_vector'])


class Migration(migrations.Migration):
    
    dependencies = [
        ('posts', '0001_initial'),
    ]
    
    operations = [
        # Enable PostgreSQL extensions
        TrigramExtension(),
        UnaccentExtension(),
        
        # Populate search vectors
        migrations.RunPython(compute_search_vectors, migrations.RunPython.noop),
    ]