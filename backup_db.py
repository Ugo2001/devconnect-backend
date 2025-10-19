# ============================================================================
# Backup Script - backup_db.py
# ============================================================================

"""
Database backup script
Usage: python backup_db.py
"""

import os
import subprocess
from datetime import datetime
from decouple import config


def backup_database():
    """Create database backup"""
    
    # Get database credentials
    db_name = config('DB_NAME')
    db_user = config('DB_USER')
    db_password = config('DB_PASSWORD')
    db_host = config('DB_HOST', default='localhost')
    
    # Create backup directory
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'devconnect_backup_{timestamp}.sql')
    
    # Run pg_dump
    env = os.environ.copy()
    env['PGPASSWORD'] = db_password
    
    cmd = [
        'pg_dump',
        '-h', db_host,
        '-U', db_user,
        '-d', db_name,
        '-F', 'c',  # Custom format
        '-f', backup_file
    ]
    
    print(f"Creating backup: {backup_file}")
    
    try:
        subprocess.run(cmd, env=env, check=True)
        print(f"✓ Backup completed successfully!")
        print(f"  File: {backup_file}")
        print(f"  Size: {os.path.getsize(backup_file) / 1024 / 1024:.2f} MB")
        
        # Clean up old backups (keep last 7 days)
        cleanup_old_backups(backup_dir, days=7)
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Backup failed: {e}")
        return False
    
    return True


def cleanup_old_backups(backup_dir, days=7):
    """Remove backups older than specified days"""
    import time
    
    now = time.time()
    cutoff = now - (days * 86400)
    
    removed = 0
    for filename in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, filename)
        if os.path.isfile(filepath):
            if os.path.getmtime(filepath) < cutoff:
                os.remove(filepath)
                removed += 1
    
    if removed > 0:
        print(f"\n✓ Cleaned up {removed} old backup(s)")


def restore_database(backup_file):
    """Restore database from backup"""
    
    db_name = config('DB_NAME')
    db_user = config('DB_USER')
    db_password = config('DB_PASSWORD')
    db_host = config('DB_HOST', default='localhost')
    
    env = os.environ.copy()
    env['PGPASSWORD'] = db_password
    
    cmd = [
        'pg_restore',
        '-h', db_host,
        '-U', db_user,
        '-d', db_name,
        '-c',  # Clean before restore
        backup_file
    ]
    
    print(f"Restoring from: {backup_file}")
    
    try:
        subprocess.run(cmd, env=env, check=True)
        print("✓ Restore completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Restore failed: {e}")
        return False


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'restore':
        if len(sys.argv) < 3:
            print("Usage: python backup_db.py restore <backup_file>")
            sys.exit(1)
        restore_database(sys.argv[2])
    else:
        backup_database()
