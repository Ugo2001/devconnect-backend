# ============================================================================
# apps/posts/management/commands/update_search_vectors.py
# ============================================================================

from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector
from apps.posts.models import Post


class Command(BaseCommand):
    help = 'Update search vectors for all posts'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Updating search vectors...')
        
        posts = Post.objects.all()
        for post in posts:
            post.search_vector = SearchVector('title', weight='A') + \
                                 SearchVector('content', weight='B')
            post.save(update_fields=['search_vector'])
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {posts.count()} posts')
        )