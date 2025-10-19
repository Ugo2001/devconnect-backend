# ============================================================================
# apps/snippets/signals.py
# ============================================================================

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Snippet, Language


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


