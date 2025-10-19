# ============================================================================
# Integration Tests
# ============================================================================

import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestIntegrationWorkflow:
    """Test complete user workflows"""
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    def test_complete_user_journey(self, api_client):
        """Test a complete user journey from registration to posting"""
        
        # 1. Register user
        register_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post('/api/users/', register_data, format='json')
        assert response.status_code == 201
        user_id = response.data['id']
        
        # 2. Login and get token
        token_response = api_client.post('/api/token/', {
            'username': 'newuser',
            'password': 'securepass123'
        }, format='json')
        assert token_response.status_code == 200
        token = token_response.data['access']
        
        # 3. Authenticate with token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # 4. Update profile
        profile_data = {
            'bio': 'I love coding!',
            'location': 'San Francisco',
            'profile': {
                'job_title': 'Developer',
                'skills': ['Python', 'Django']
            }
        }
        response = api_client.patch(f'/api/users/{user_id}/', profile_data, format='json')
        assert response.status_code == 200
        
        # 5. Create a post
        post_data = {
            'title': 'My First Post',
            'content': '# Welcome\n\nThis is my first post!',
            'status': 'published',
            'tags': ['introduction', 'hello']
        }
        response = api_client.post('/api/posts/', post_data, format='json')
        assert response.status_code == 201
        post_id = response.data['id']
        
        # 6. Comment on own post
        comment_data = {
            'post': post_id,
            'content': 'Thanks for reading!'
        }
        response = api_client.post('/api/posts/comments/', comment_data, format='json')
        assert response.status_code == 201
        
        # 7. Create a snippet
        from apps.snippets.models import Language
        from apps.posts.models import Post
        python = Language.objects.create(name='Python', extension='.py')
        
        snippet_data = {
            'title': 'Hello World',
            'description': 'A simple hello world program',
            'code': 'print("Hello, World!")',
            'language_id': python.id,
            'visibility': 'public',
            'tags': ['python', 'beginner']
        }
        response = api_client.post('/api/snippets/', snippet_data, format='json')
        assert response.status_code == 201
        
        # Verify final state
        user = User.objects.get(id=user_id)
        assert user.posts_count == 1
        assert user.snippets_count == 1
        assert Post.objects.filter(author=user).count() == 1
