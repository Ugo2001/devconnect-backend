# ============================================================================
# apps/notifications/tasks.py (Celery tasks)
# ============================================================================

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@shared_task
def send_daily_digest():
    """
    Send daily digest emails to users
    """
    from .models import Notification
    from django.core.mail import send_mail
    from django.conf import settings
    
    yesterday = timezone.now() - timedelta(days=1)
    
    # Get users with unread notifications from yesterday
    users_with_notifications = User.objects.filter(
        notifications__created_at__gte=yesterday,
        notifications__is_read=False,
        email_notifications=True
    ).distinct()
    
    for user in users_with_notifications:
        unread_count = user.notifications.filter(
            is_read=False,
            created_at__gte=yesterday
        ).count()
        
        if unread_count > 0:
            send_mail(
                subject=f'You have {unread_count} unread notifications on DevConnect',
                message=f'Hi {user.username},\n\nYou have {unread_count} unread notifications waiting for you.\n\nVisit DevConnect to check them out!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
    
    return f'Digest sent to {users_with_notifications.count()} users'


@shared_task
def cleanup_old_notifications():
    """
    Delete read notifications older than 30 days
    """
    from .models import Notification
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    deleted_count = Notification.objects.filter(
        is_read=True,
        read_at__lt=thirty_days_ago
    ).delete()[0]
    
    return f'Deleted {deleted_count} old notifications'
