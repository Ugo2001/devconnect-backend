# ============================================================================
# Performance Tests
# ============================================================================

import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.posts.models import Post  # Replace 'posts' with your actual app name if different

User = get_user_model()

@pytest.mark.django_db
class TestPerformance:
    """Test query performance and N+1 issues"""
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    def test_post_list_query_count(self, api_client, django_assert_num_queries):
        """Test that post listing doesn't have N+1 queries"""
        user = User.objects.create_user(username='test', email='test@example.com', password='pass')
        
        # Create 10 posts
        for i in range(10):
            Post.objects.create(
                author=user,
                title=f'Post {i}',
                content=f'Content {i}',
                status='published'
            )
        
        # Should use select_related and prefetch_related efficiently
        with django_assert_num_queries(3):  # Adjust based on actual queries
            response = api_client.get('/api/posts/')
            assert response.status_code == 200