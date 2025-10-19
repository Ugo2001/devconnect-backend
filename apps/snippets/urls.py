# ============================================================================
# apps/snippets/urls.py
# ============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SnippetViewSet, SnippetCommentViewSet, LanguageViewSet

router = DefaultRouter()
router.register(r'', SnippetViewSet, basename='snippet')
router.register(r'comments', SnippetCommentViewSet, basename='snippet-comment')
router.register(r'languages', LanguageViewSet, basename='language')

urlpatterns = [
    path('', include(router.urls)),
]