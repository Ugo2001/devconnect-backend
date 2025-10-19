# ============================================================================
# Performance Monitoring - performance_monitor.py
# ============================================================================

"""
Monitor database query performance
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DevConnect.settings')
django.setup()

from django.db import connection, reset_queries
from django.test.utils import override_settings
from apps.posts.models import Post
from apps.users.models import User


@override_settings(DEBUG=True)
def analyze_queries():
    """Analyze query performance for common operations"""
    
    print("DevConnect Performance Monitor")
    print("=" * 50)
    
    tests = [
        ("List Posts", lambda: list(Post.objects.select_related('author').prefetch_related('tags')[:20])),
        ("Get User Profile", lambda: User.objects.select_related('profile').first()),
        ("Search Posts", lambda: list(Post.objects.filter(title__icontains='python')[:10])),
    ]
    
    for name, test_func in tests:
        reset_queries()
        test_func()
        
        query_count = len(connection.queries)
        total_time = sum(float(q['time']) for q in connection.queries)
        
        print(f"\n{name}:")
        print(f"  Queries: {query_count}")
        print(f"  Time: {total_time:.4f}s")
        
        if query_count > 10:
            print(f"  ⚠ Warning: High query count!")
    
    print("\n" + "=" * 50)


if __name__ == '__main__':
    analyze_queries()