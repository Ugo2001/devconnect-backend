# ============================================================================
# apps/posts/tests.py
# ============================================================================

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.posts.models import Post, Comment, Tag, Like, Bookmark

User = get_user_model()


@pytest.mark.django_db
class TestPostAPI:
    
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
    def post(self, user):
        return Post.objects.create(
            author=user,
            title='Test Post',
            content='# Test Content\n\nThis is a test post.',
            status='published'
        )
    
    def test_list_posts(self, api_client, post):
        """Test listing published posts"""
        response = api_client.get('/api/posts/')
        assert response.status_code == 200
        assert len(response.data['results']) == 1
    
    def test_create_post(self, api_client, user):
        """Test creating a new post"""
        api_client.force_authenticate(user=user)
        
        data = {
            'title': 'New Post',
            'content': '# Hello World\n\nThis is my post.',
            'status': 'published',
            'tags': ['python', 'django']
        }
        
        response = api_client.post('/api/posts/', data, format='json')
        assert response.status_code == 201
        
        post = Post.objects.get()
        assert post.title == 'New Post'
        assert post.tags.count() == 2
        assert '<h1>Hello World</h1>' in post.content_html
    
    def test_update_post(self, api_client, user, post):
        """Test updating a post"""
        api_client.force_authenticate(user=user)
        
        data = {
            'title': 'Updated Title',
            'content': 'Updated content',
            'status': 'published'
        }
        
        response = api_client.patch(f'/api/posts/{post.id}/', data, format='json')
        assert response.status_code == 200
        
        post.refresh_from_db()
        assert post.title == 'Updated Title'
    
    def test_cannot_update_other_user_post(self, api_client, post):
        """Test that users cannot update other users' posts"""
        other_user = User.objects.create_user(username='other', email='other@example.com', password='pass123')
        api_client.force_authenticate(user=other_user)
        
        response = api_client.patch(f'/api/posts/{post.id}/', {'title': 'Hacked'}, format='json')
        assert response.status_code == 403
    
    def test_like_post(self, api_client, user, post):
        """Test liking a post"""
        api_client.force_authenticate(user=user)
        
        response = api_client.post(f'/api/posts/{post.id}/like/')
        assert response.status_code == 201
        
        post.refresh_from_db()
        assert post.likes_count == 1
        assert Like.objects.count() == 1
    
    def test_unlike_post(self, api_client, user, post):
        """Test unliking a post"""
        Like.objects.create(user=user, content_type='post', object_id=post.id)
        post.likes_count = 1
        post.save()
        
        api_client.force_authenticate(user=user)
        response = api_client.post(f'/api/posts/{post.id}/unlike/')
        
        assert response.status_code == 200
        post.refresh_from_db()
        assert post.likes_count == 0
    
    def test_bookmark_post(self, api_client, user, post):
        """Test bookmarking a post"""
        api_client.force_authenticate(user=user)
        
        response = api_client.post(f'/api/posts/{post.id}/bookmark/')
        assert response.status_code == 201
        assert Bookmark.objects.count() == 1
    
    def test_full_text_search(self, api_client, user):
        """Test full-text search functionality"""
        Post.objects.create(
            author=user,
            title='Python Tutorial',
            content='Learn Python programming',
            status='published'
        )
        Post.objects.create(
            author=user,
            title='JavaScript Guide',
            content='Learn JavaScript',
            status='published'
        )
        
        response = api_client.get('/api/posts/?search=python')
        assert response.status_code == 200
        assert len(response.data['results']) >= 1


@pytest.mark.django_db
class TestCommentAPI:
    
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
    def post(self, user):
        return Post.objects.create(
            author=user,
            title='Test Post',
            content='Test content',
            status='published'
        )
    
    def test_create_comment(self, api_client, user, post):
        """Test creating a comment"""
        api_client.force_authenticate(user=user)
        
        data = {
            'post': post.id,
            'content': 'Great post!'
        }
        
        response = api_client.post('/api/posts/comments/', data, format='json')
        assert response.status_code == 201
        
        post.refresh_from_db()
        assert post.comments_count == 1
    
    def test_nested_replies(self, api_client, user, post):
        """Test creating nested comment replies"""
        api_client.force_authenticate(user=user)
        
        # Create parent comment
        parent = Comment.objects.create(
            post=post,
            author=user,
            content='Parent comment'
        )
        
        # Create reply
        data = {
            'post': post.id,
            'parent': parent.id,
            'content': 'Reply to parent'
        }
        
        response = api_client.post('/api/posts/comments/', data, format='json')
        assert response.status_code == 201
        assert Comment.objects.count() == 2


@pytest.mark.django_db
class TestTagAPI:
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    def test_list_tags(self, api_client):
        """Test listing tags"""
        Tag.objects.create(name='Python', posts_count=5)
        Tag.objects.create(name='Django', posts_count=3)
        
        response = api_client.get('/api/posts/tags/')
        assert response.status_code == 200
        assert len(response.data['results']) == 2
