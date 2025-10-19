# Register signals - Add to apps/notifications/apps.py:

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = 'Notifications'
    
    def ready(self):
        import apps.notifications.signals
        # Ensures the signals are imported and registered