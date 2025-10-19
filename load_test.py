# ============================================================================
# Load Testing Script - load_test.py
# ============================================================================

"""
Simple load testing script
Requires: pip install locust

Usage: locust -f load_test.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between


class DevConnectUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login user"""
        response = self.client.post("/api/token/", {
            "username": "testuser",
            "password": "testpass123"
        })
        if response.status_code == 200:
            self.token = response.json()['access']
            self.client.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
    
    @task(3)
    def list_posts(self):
        """List posts - most common operation"""
        self.client.get("/api/posts/")
    
    @task(2)
    def view_post(self):
        """View single post"""
        self.client.get("/api/posts/1/")
    
    @task(2)
    def list_snippets(self):
        """List snippets"""
        self.client.get("/api/snippets/")
    
    @task(1)
    def search_posts(self):
        """Search posts"""
        self.client.get("/api/posts/?search=python")
    
    @task(1)
    def get_notifications(self):
        """Get notifications"""
        self.client.get("/api/notifications/")
    
    @task(1)
    def get_profile(self):
        """Get user profile"""
        self.client.get("/api/users/me/")