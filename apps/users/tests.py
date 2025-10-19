# apps/users/tests.py

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import Follow, UserProfile

User = get_user_model()


@pytest.mark.django_db
class TestUserAuthentication:
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def user_data(self):
        return {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_user_registration(self, api_client, user_data):
        """Test user registration"""
        response = api_client.post('/api/users/', user_data, format='json')
        assert response.status_code == 201
        assert User.objects.count() == 1
        assert User.objects.get().username == 'testuser'
    
    def test_user_registration_password_mismatch(self, api_client, user_data):
        """Test registration fails with password mismatch"""
        user_data['password_confirm'] = 'different'
        response = api_client.post('/api/users/', user_data, format='json')
        assert response.status_code == 400
    
    def test_jwt_token_obtain(self, api_client):
        """Test JWT token generation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        response = api_client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_authenticated_request(self, api_client):
        """Test making authenticated requests"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/users/me/')
        
        assert response.status_code == 200
        assert response.data['username'] == 'testuser'


@pytest.mark.django_db
class TestUserProfile:
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=user)
        return user
    
    def test_get_user_profile(self, api_client, user):
        """Test retrieving user profile"""
        api_client.force_authenticate(user=user)
        response = api_client.get(f'/api/users/{user.id}/')
        assert response.status_code == 200
        assert response.data['username'] == 'testuser'
    
    def test_update_user_profile(self, api_client, user):
        """Test updating user profile"""
        api_client.force_authenticate(user=user)
        
        data = {
            'bio': 'Updated bio',
            'location': 'New York',
            'profile': {
                'job_title': 'Software Engineer',
                'skills': ['Python', 'Django', 'React']
            }
        }
        
        response = api_client.patch(f'/api/users/{user.id}/', data, format='json')
        assert response.status_code == 200
        
        user.refresh_from_db()
        assert user.bio == 'Updated bio'
        assert user.profile.job_title == 'Software Engineer'
    
    def test_cannot_update_other_user(self, api_client):
        """Test that users cannot update other users' profiles"""
        user1 = User.objects.create_user(username='user1', email='user1@example.com', password='pass123')
        user2 = User.objects.create_user(username='user2', email='user2@example.com', password='pass123')
        
        api_client.force_authenticate(user=user1)
        response = api_client.patch(f'/api/users/{user2.id}/', {'bio': 'Hacked'}, format='json')
        
        assert response.status_code == 403


@pytest.mark.django_db
class TestFollowSystem:
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def users(self):
        user1 = User.objects.create_user(username='user1', email='user1@example.com', password='pass123')
        user2 = User.objects.create_user(username='user2', email='user2@example.com', password='pass123')
        UserProfile.objects.create(user=user1)
        UserProfile.objects.create(user=user2)
        return user1, user2
    
    def test_follow_user(self, api_client, users):
        """Test following another user"""
        user1, user2 = users
        api_client.force_authenticate(user=user1)
        
        response = api_client.post(f'/api/users/{user2.id}/follow/')
        assert response.status_code == 201
        assert Follow.objects.count() == 1
        
        user1.refresh_from_db()
        user2.refresh_from_db()
        assert user1.following_count == 1
        assert user2.followers_count == 1
    
    def test_cannot_follow_self(self, api_client, users):
        """Test that users cannot follow themselves"""
        user1, _ = users
        api_client.force_authenticate(user=user1)
        
        response = api_client.post(f'/api/users/{user1.id}/follow/')
        assert response.status_code == 400
    
    def test_unfollow_user(self, api_client, users):
        """Test unfollowing a user"""
        user1, user2 = users
        Follow.objects.create(follower=user1, following=user2)
        user1.following_count = 1
        user2.followers_count = 1
        user1.save()
        user2.save()
        
        api_client.force_authenticate(user=user1)
        response = api_client.post(f'/api/users/{user2.id}/unfollow/')
        
        assert response.status_code == 200
        assert Follow.objects.count() == 0
    
    def test_get_followers(self, api_client, users):
        """Test getting user's followers"""
        user1, user2 = users
        Follow.objects.create(follower=user1, following=user2)
        
        api_client.force_authenticate(user=user1)
        response = api_client.get(f'/api/users/{user2.id}/followers/')
        assert response.status_code == 200
        assert len(response.data) == 1
    
    def test_get_following(self, api_client, users):
        """Test getting users that a user is following"""
        user1, user2 = users
        Follow.objects.create(follower=user1, following=user2)
        
        api_client.force_authenticate(user=user1)
        response = api_client.get(f'/api/users/{user1.id}/following/')
        assert response.status_code == 200
        assert len(response.data) == 1

