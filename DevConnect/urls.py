# ============================================================================
# DevConnect/urls.py
# ============================================================================

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import JsonResponse

def api_root(request):
    """API Root endpoint"""
    return JsonResponse({
        'message': 'Welcome to DevConnect API',
        'endpoints': {
            'admin': '/admin/',
            'token': '/api/token/',
            'token_refresh': '/api/token/refresh/',
            'users': '/api/users/',
            'posts': '/api/posts/',
            'snippets': '/api/snippets/',
            'notifications': '/api/notifications/',
        },
        'resources': {
            'users': '/api/users/',
            'posts': '/api/posts/',
            'snippets': '/api/snippets/',
            'notifications': '/api/notifications/',
        },
        'documentation': {
            'swagger': '/api/docs/',
            'redoc': '/api/redoc/',
        }
    })

urlpatterns = [
    # Root endpoint
    path('', api_root, name='api-root'),
    path('api/', api_root, name='api-root-explicit'),
    
    path('admin/', admin.site.urls),
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Social Auth
    path('api/auth/', include('social_django.urls', namespace='social')),
    
    # App URLs
    path('api/users/', include('apps.users.urls')),
    path('api/posts/', include('apps.posts.urls')),
    path('api/snippets/', include('apps.snippets.urls')),
    path('api/notifications/', include('apps.notifications.urls')),

]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)