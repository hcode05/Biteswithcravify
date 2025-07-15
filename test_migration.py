#!/usr/bin/env python
import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodonline_main.settings')

# Setup Django
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    # Run makemigrations
    execute_from_command_line(['manage.py', 'makemigrations', 'marketplace'])
    print("Migrations created successfully!")
