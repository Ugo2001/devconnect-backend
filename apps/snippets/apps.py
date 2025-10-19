# Register signals in apps.py

from django.apps import AppConfig


class SnippetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.snippets'
    verbose_name = 'Snippets'

    def ready(self):
        import apps.snippets.signals
        # Ensures the signals are imported and registered