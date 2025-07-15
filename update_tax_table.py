#!/usr/bin/env python
import os
import sys
import django

# Add the project path
sys.path.append('c:/Users/ADMIN/Desktop/foodproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodonline_main.settings')

django.setup()

from django.db import connection

def update_tax_table():
    """Add missing columns to the Tax table"""
    with connection.cursor() as cursor:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(marketplace_tax);")
        columns = [column[1] for column in cursor.fetchall()]
        
        print("Current columns:", columns)
        
        # Add created_at if it doesn't exist
        if 'created_at' not in columns:
            cursor.execute("""
                ALTER TABLE marketplace_tax 
                ADD COLUMN created_at datetime NOT NULL DEFAULT '2024-01-01 00:00:00';
            """)
            print("Added created_at column")
        
        # Add updated_at if it doesn't exist
        if 'updated_at' not in columns:
            cursor.execute("""
                ALTER TABLE marketplace_tax 
                ADD COLUMN updated_at datetime NOT NULL DEFAULT '2024-01-01 00:00:00';
            """)
            print("Added updated_at column")
        
        print("Tax table updated successfully!")

if __name__ == "__main__":
    update_tax_table()
