# ============================================================================
# Health Check Script - health_check.py
# ============================================================================

"""
Health check script for monitoring
Usage: python health_check.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DevConnect.settings')
django.setup()

from django.db import connection
from django.core.cache import cache
from django.contrib.auth import get_user_model
import redis

User = get_user_model()


def check_database():
    """Check database connectivity"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True, "Database OK"
    except Exception as e:
        return False, f"Database Error: {str(e)}"


def check_redis():
    """Check Redis connectivity"""
    try:
        cache.set('health_check', 'ok', 10)
        value = cache.get('health_check')
        if value == 'ok':
            return True, "Redis OK"
        return False, "Redis value mismatch"
    except Exception as e:
        return False, f"Redis Error: {str(e)}"


def check_models():
    """Check if models are accessible"""
    try:
        count = User.objects.count()
        return True, f"Models OK (Users: {count})"
    except Exception as e:
        return False, f"Models Error: {str(e)}"


def main():
    print("DevConnect Health Check")
    print("=" * 50)
    
    checks = [
        ("Database", check_database),
        ("Redis", check_redis),
        ("Models", check_models),
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        success, message = check_func()
        status = "✓" if success else "✗"
        print(f"{status} {name}: {message}")
        
        if not success:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("Status: HEALTHY")
        sys.exit(0)
    else:
        print("Status: UNHEALTHY")
        sys.exit(1)


if __name__ == '__main__':
    main()

