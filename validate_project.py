import os
import django
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodonline_main.settings')

try:
    django.setup()
    print("Django setup successful!")
    
    # Test if models can be imported
    from orders.models import Order, Payment
    from marketplace.models import Cart, Tax
    print("Models imported successfully!")
    
    # Test if views can be imported  
    from orders.views import payments
    from marketplace.views import add_to_cart
    print("Views imported successfully!")
    
    print("All components loaded successfully! No syntax errors detected.")
    print("You can now start the server with: python manage.py runserver")
    
except Exception as e:
    print(f"Error detected: {e}")
    import traceback
    traceback.print_exc()
