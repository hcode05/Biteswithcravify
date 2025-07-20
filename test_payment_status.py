import os
import sys
import django

# Add the project root directory to the Python path
sys.path.insert(0, r'c:\Users\ADMIN\Desktop\foodproject')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodonline_main.settings')

# Setup Django
django.setup()

# Test the status comparison logic
def test_status_logic():
    test_statuses = ['COMPLETED', 'completed', 'SUCCESS', 'success', 'FAILED', 'failed']
    
    for status in test_statuses:
        status_upper = status.upper() if status else ''
        print(f"Status: '{status}' -> Normalized: '{status_upper}'")
        
        if status_upper in ['SUCCESS', 'COMPLETED']:
            result = 'Accepted'
        elif status_upper in ['FAILED', 'FAILURE', 'ERROR']:
            result = 'Cancelled'
        else:
            result = 'New'
        
        print(f"  -> Order status would be: {result}")
        print()

if __name__ == "__main__":
    test_status_logic()
