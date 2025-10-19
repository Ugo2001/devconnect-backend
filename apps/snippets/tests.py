#============================================================================
# apps/snippets/tests.py
# ============================================================================

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.snippets.models import Snippet, Language

User = get_user_model()


@pytest.mark.django_db
class TestSnippetAPI:
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def language(self):
        return Language.objects.create(
            name='Python',
            extension='.py',
            color='#3776ab'
        )
    
    @pytest.fixture
    def snippet(self, user, language):
        return Snippet.objects.create(
            author=user,
            title='Test Snippet',
            description='A test snippet',
            code='print("Hello, World!")',
            language=language,
            visibility='public'
        )
    
    def test_list_snippets(self, api_client, snippet):
        """Test listing public snippets"""
        response = api_client.get('/api/snippets/')
        assert response.status_code == 200
        assert len(response.data['results']) == 1
    
    def test_create_snippet(self, api_client, user, language):
        """Test creating a new snippet"""
        api_client.force_authenticate(user=user)
        
        data = {
            'title': 'New Snippet',
            'description': 'Test description',
            'code': 'def hello(): pass',
            'language_id': language.id,
            'visibility': 'public',
            'tags': ['python', 'test']
        }
        
        response = api_client.post('/api/snippets/', data, format='json')
        assert response.status_code == 201
        assert Snippet.objects.count() == 1
    
    def test_like_snippet(self, api_client, user, snippet):
        """Test liking a snippet"""
        api_client.force_authenticate(user=user)
        
        response = api_client.post(f'/api/snippets/{snippet.id}/like/')
        assert response.status_code == 201
        
        snippet.refresh_from_db()
        assert snippet.likes_count == 1
    
    def test_fork_snippet(self, api_client, user, snippet):
        """Test forking a snippet"""
        api_client.force_authenticate(user=user)
        
        response = api_client.post(f'/api/snippets/{snippet.id}/fork/')
        assert response.status_code == 201
        assert Snippet.objects.count() == 2
        
        forked_snippet = Snippet.objects.get(forked_from=snippet)
        assert forked_snippet.author == user
        assert forked_snippet.code == snippet.code
    
    def test_private_snippet_visibility(self, api_client, user, language):
        """Test that private snippets are not visible to others"""
        # Create a private snippet
        snippet = Snippet.objects.create(
            author=user,
            title='Private Snippet',
            code='secret code',
            language=language,
            visibility='private'
        )
        
        # Try to access without authentication
        response = api_client.get('/api/snippets/')
        assert response.status_code == 200
        assert len(response.data['results']) == 0
        
        # Access with authentication as owner
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/snippets/')
        assert len(response.data['results']) == 1