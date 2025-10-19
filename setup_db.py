# ============================================================================
# Database Setup Script - setup_db.py
# ============================================================================

"""
Run this script to set up the database with initial data:
python setup_db.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DevConnect.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()


def setup_database():
    print("=" * 50)
    print("DevConnect Database Setup")
    print("=" * 50)
    
    # Run migrations
    print("\n1. Running migrations...")
    call_command('migrate')
    
    # Create superuser
    print("\n2. Creating superuser...")
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@devconnect.com',
            password='admin123'
        )
        print("   ✓ Superuser created: admin / admin123")
    else:
        print("   - Superuser already exists")
    
    # Populate languages
    print("\n3. Populating programming languages...")
    call_command('populate_languages')
    
    # Create test data
    print("\n4. Creating test data...")
    response = input("   Do you want to create test data? (y/n): ")
    if response.lower() == 'y':
        call_command('create_test_data', users=10, posts=20, snippets=15)
    else:
        print("   - Skipped test data creation")
    
    # Update search vectors
    print("\n5. Updating search vectors...")
    call_command('update_search_vectors')
    
    # Collect static files
    print("\n6. Collecting static files...")
    call_command('collectstatic', '--noinput')
    
    print("\n" + "=" * 50)
    print("✓ Database setup complete!")
    print("=" * 50)
    print("\nYou can now:")
    print("1. Start the development server: python manage.py runserver")
    print("2. Access admin panel: http://localhost:8000/admin/")
    print("3. Admin credentials: admin / admin123")
    print("=" * 50)


if __name__ == '__main__':
    setup_database()