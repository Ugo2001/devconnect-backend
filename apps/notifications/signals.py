from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.posts.models import Like, Comment, Post, Bookmark
from apps.users.models import Follow
from apps.notifications.utils import create_notification


@receiver(post_save, sender=Like)
def notify_like(sender, instance, created, **kwargs):
    """Notify when someone likes content"""
    if created:
        try:
            # Post like
            if instance.content_type == 'post':
                try:
                    post = Post.objects.get(id=instance.object_id)
                    if instance.user != post.author:
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
            
            # Comment like
            elif instance.content_type == 'comment':
                try:
                    comment = Comment.objects.get(id=instance.object_id)
                    if instance.user != comment.author:
                        create_notification(
                            recipient=comment.author,
                            sender=instance.user,
                            notification_type='like',
                            title='New Like',
                            message=f'{instance.user.username} liked your comment',
                            link=f'/posts/{comment.post.slug}#comment-{comment.id}',
                            data={'comment_id': comment.id, 'post_id': comment.post.id}
                        )
                except Comment.DoesNotExist:
                    pass
        except Exception as e:
            print(f"Failed to create notification: {e}")


@receiver(post_save, sender=Comment)
def notify_comment(sender, instance, created, **kwargs):
    """Notify when someone comments on a post"""
    if created and instance.author != instance.post.author:
        try:
            create_notification(
                recipient=instance.post.author,
                sender=instance.author,
                notification_type='comment',
                title='New Comment',
                message=f'{instance.author.username} commented on your post "{instance.post.title}"',
                link=f'/posts/{instance.post.slug}#comment-{instance.id}',
                data={'post_id': instance.post.id, 'comment_id': instance.id}
            )
        except Exception as e:
            print(f"Failed to create notification: {e}")


@receiver(post_save, sender=Bookmark)
def notify_bookmark(sender, instance, created, **kwargs):
    """Notify when someone bookmarks a post"""
    if created and instance.user != instance.post.author:
        try:
            create_notification(
                recipient=instance.post.author,
                sender=instance.user,
                notification_type='post',
                title='Post Bookmarked',
                message=f'{instance.user.username} bookmarked your post "{instance.post.title}"',
                link=f'/posts/{instance.post.slug}',
                data={'post_id': instance.post.id}
            )
        except Exception as e:
            print(f"Failed to create notification: {e}")


@receiver(post_save, sender=Follow)
def notify_follow(sender, instance, created, **kwargs):
    """Notify when someone follows a user"""
    if created:
        try:
            create_notification(
                recipient=instance.following,
                sender=instance.follower,
                notification_type='follow',
                title='New Follower',
                message=f'{instance.follower.username} started following you',
                link=f'/users/{instance.follower.username}',
                data={'user_id': instance.follower.id}
            )
        except Exception as e:
            print(f"Failed to create notification: {e}")