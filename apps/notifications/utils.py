# ============================================================================
# apps/notifications/utils.py
# ============================================================================

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from .serializers import NotificationSerializer


def send_notification_to_user(user_id, notification):
    """Send notification to user via WebSocket"""
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "notification_message",
                "notification": notification,
            }
        )
    except Exception as e:
        # Redis not available - skip WebSocket notification
        print(f"WebSocket notification failed: {e}")
        pass


def create_notification(recipient, actor, verb, target=None, action_object=None):
    """Create a notification and send via WebSocket"""
    from apps.notifications.models import Notification
    
    notification = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=verb,
        target=target,
        action_object=action_object,
    )
    
    # Try to send WebSocket, but don't fail if Redis unavailable
    try:
        send_notification_to_user(recipient.id, notification)
    except Exception as e:
        print(f"Failed to send WebSocket notification: {e}")
        pass
    
    return notification


def update_unread_count(user_id):
    """
    Send updated unread count to user
    """
    from .models import Notification
    
    channel_layer = get_channel_layer()
    group_name = f'notifications_{user_id}'
    
    # Get unread count
    count = Notification.objects.filter(
        recipient_id=user_id,
        is_read=False
    ).count()
    
    # Send to group
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'unread_count_update',
            'count': count
        }
    )
