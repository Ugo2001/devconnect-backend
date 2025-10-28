# ============================================================================
# apps/snippets/signals.py
# ============================================================================

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Snippet, Language, SnippetLike, SnippetComment
from apps.notifications.utils import create_notification


@receiver(post_save, sender=Snippet)
def update_language_count_on_create(sender, instance, created, **kwargs):
    """Update language snippet count when snippet is created"""
    if created and instance.language:
        instance.language.snippets_count = instance.language.snippets.count()
        instance.language.save(update_fields=['snippets_count'])


@receiver(post_delete, sender=Snippet)
def update_language_count_on_delete(sender, instance, **kwargs):
    """Update language snippet count when snippet is deleted"""
    if instance.language:
        instance.language.snippets_count = instance.language.snippets.count()
        instance.language.save(update_fields=['snippets_count'])


@receiver(post_save, sender=SnippetLike)
def notify_snippet_like(sender, instance, created, **kwargs):
    """Notify snippet author when someone likes their snippet"""
    if created and instance.user != instance.snippet.author:
        try:
            create_notification(
                recipient=instance.snippet.author,
                sender=instance.user,
                notification_type='like',
                title='New Like',
                message=f'{instance.user.username} liked your snippet "{instance.snippet.title}"',
                link=f'/snippets/{instance.snippet.slug}',
                data={'snippet_id': instance.snippet.id}
            )
        except Exception as e:
            print(f"Failed to create notification: {e}")


@receiver(post_save, sender=SnippetComment)
def notify_snippet_comment(sender, instance, created, **kwargs):
    """Notify snippet author when someone comments"""
    if created and instance.author != instance.snippet.author:
        try:
            create_notification(
                recipient=instance.snippet.author,
                sender=instance.author,
                notification_type='comment',
                title='New Comment',
                message=f'{instance.author.username} commented on your snippet "{instance.snippet.title}"',
                link=f'/snippets/{instance.snippet.slug}#comment-{instance.id}',
                data={'snippet_id': instance.snippet.id, 'comment_id': instance.id}
            )
        except Exception as e:
            print(f"Failed to create notification: {e}")


# If snippet has forking functionality, add this:
@receiver(post_save, sender=Snippet)
def notify_snippet_fork(sender, instance, created, **kwargs):
    """Notify original author when someone forks their snippet"""
    if created and instance.forked_from and instance.author != instance.forked_from.author:
        try:
            create_notification(
                recipient=instance.forked_from.author,
                sender=instance.author,
                notification_type='post',  # or create a 'fork' type
                title='Snippet Forked',
                message=f'{instance.author.username} forked your snippet "{instance.forked_from.title}"',
                link=f'/snippets/{instance.slug}',
                data={
                    'snippet_id': instance.id,
                    'original_snippet_id': instance.forked_from.id
                }
            )
        except Exception as e:
            print(f"Failed to create notification: {e}")