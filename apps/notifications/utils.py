# ============================================================================
# apps/notifications/utils.py
# ============================================================================

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from .serializers import NotificationSerializer


def create_notification(recipient, notification_type, title, message, sender=None, link='', data=None):
    """
    Create a notification and send it via WebSocket
    """
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
        data=data or {}
    )
    
    # Send via WebSocket
    send_notification_to_user(recipient.id, notification)
    
    return notification


def send_notification_to_user(user_id, notification):
    """
    Send notification to user via WebSocket
    """
    channel_layer = get_channel_layer()
    group_name = f'notifications_{user_id}'
    
    # Serialize notification
    serializer = NotificationSerializer(notification)
    
    # Send to group
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'notification_message',
            'notification': serializer.data
        }
    )


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
