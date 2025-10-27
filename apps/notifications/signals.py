# ============================================================================
# apps/notifications/signals.py
# ============================================================================

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.posts.models import Like, Comment
from apps.snippets.models import SnippetLike, SnippetComment
from apps.users.models import Follow
from .utils import create_notification


@receiver(post_save, sender=Like)
def notify_post_like(sender, instance, created, **kwargs):
    """Notify post author when someone likes their post"""
    if created and instance.user != instance.post.author:
        try:
            create_notification(
                recipient=instance.post.author,
                actor=instance.user,
                verb='liked your post',
                target=instance.post,
                action_object=instance,
            )
        except Exception as e:
            print(f"Failed to create notification: {e}")
            pass


@receiver(post_save, sender=Comment)
def notify_post_comment(sender, instance, created, **kwargs):
    """Notify post author when someone comments"""
    if created and instance.author != instance.post.author:
        try:
            # Don't pass 'sender' to create_notification
            create_notification(
                recipient=instance.post.author,
                actor=instance.author,
                verb='commented on your post',
                target=instance.post,
                action_object=instance,
            )
        except Exception as e:
            # Log error but don't fail the comment creation
            print(f"Failed to create notification: {e}")
            pass


@receiver(post_save, sender=SnippetLike)
def notify_snippet_like(sender, instance, created, **kwargs):
    """Notify snippet author when someone likes their snippet"""
    if created and instance.user != instance.snippet.author:
        try:
            create_notification(
                recipient=instance.snippet.author,
                actor=instance.user,
                verb='liked your snippet',
                target=instance.snippet,
                action_object=instance,
            )
        except Exception as e:
            print(f"Failed to create notification: {e}")
            pass



@receiver(post_save, sender=SnippetComment)
def notify_snippet_comment(sender, instance, created, **kwargs):
    """Send notification when snippet is commented"""
    if created:
        snippet = instance.snippet
        if snippet.author != instance.author:
            try:
                create_notification(
                    recipient=snippet.author,
                    actor=instance.author,  # ✅ Changed from 'sender' to 'actor'
                    verb='commented on your snippet',  # ✅ Changed from 'notification_type'
                    target=snippet,  # ✅ Added target
                    action_object=instance,  # ✅ Added the comment itself
                )
            except Exception as e:
                print(f"Failed to create notification: {e}")
                pass


@receiver(post_save, sender=Follow)
def notify_new_follow(sender, instance, created, **kwargs):
    """Notify user when someone follows them"""
    if created:
        try:
            create_notification(
                recipient=instance.following,
                actor=instance.follower,
                verb='started following you',
                target=instance.following,
                action_object=instance,
            )
        except Exception as e:
            print(f"Failed to create notification: {e}")
            pass


