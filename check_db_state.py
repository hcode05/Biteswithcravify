import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodonline_main.settings')
django.setup()

from django.db import connection

# Get the database cursor
cursor = connection.cursor()

# Check if marketplace_tax table exists
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='marketplace_tax';")
    result = cursor.fetchall()
    if result:
        print("marketplace_tax table exists")
        
        # Get table schema
        cursor.execute("PRAGMA table_info(marketplace_tax);")
        columns = cursor.fetchall()
        print("Columns in marketplace_tax:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    else:
        print("marketplace_tax table does not exist")
        
    # Check migration history
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations';")
    if cursor.fetchall():
        cursor.execute("SELECT app, name FROM django_migrations WHERE app='marketplace' ORDER BY id;")
        migrations = cursor.fetchall()
        print("\nApplied migrations:")
        for migration in migrations:
            print(f"  {migration[0]}.{migration[1]}")
    else:
        print("No migration table found")
        
except Exception as e:
    print(f"Error: {e}")
