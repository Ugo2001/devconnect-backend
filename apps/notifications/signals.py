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
    """Send notification when post is liked"""
    if created and instance.content_type == 'post':
        from apps.posts.models import Post
        
        try:
            post = Post.objects.get(id=instance.object_id)
            if post.author != instance.user:
                create_notification(
                    recipient=post.author,
                    sender=instance.user,
                    notification_type='like',
                    title='New Like',
                    message=f'{instance.user.username} liked your post "{post.title}"',
                    link=f'/posts/{post.slug}',
                    data={'post_id': post.id}
                )
        except Post.DoesNotExist:
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
    """Send notification when snippet is liked"""
    if created:
        snippet = instance.snippet
        if snippet.author != instance.user:
            create_notification(
                recipient=snippet.author,
                sender=instance.user,
                notification_type='like',
                title='New Like',
                message=f'{instance.user.username} liked your snippet "{snippet.title}"',
                link=f'/snippets/{snippet.slug}',
                data={'snippet_id': snippet.id}
            )


@receiver(post_save, sender=SnippetComment)
def notify_snippet_comment(sender, instance, created, **kwargs):
    """Send notification when snippet is commented"""
    if created:
        snippet = instance.snippet
        if snippet.author != instance.author:
            create_notification(
                recipient=snippet.author,
                sender=instance.author,
                notification_type='comment',
                title='New Comment',
                message=f'{instance.author.username} commented on your snippet "{snippet.title}"',
                link=f'/snippets/{snippet.slug}#comment-{instance.id}',
                data={'snippet_id': snippet.id, 'comment_id': instance.id}
            )


@receiver(post_save, sender=Follow)
def notify_new_follower(sender, instance, created, **kwargs):
    """Send notification when user gets a new follower"""
    if created:
        create_notification(
            recipient=instance.following,
            sender=instance.follower,
            notification_type='follow',
            title='New Follower',
            message=f'{instance.follower.username} started following you',
            link=f'/users/{instance.follower.username}',
            data={'user_id': instance.follower.id}
        )


