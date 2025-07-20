#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodonline_main.settings')
django.setup()

try:
    from marketplace.context_processors import get_cart_amounts, get_cart_counter
    from marketplace.models import Cart, Tax
    from menu.models import FoodItem
    print("✓ All imports successful")
    
    # Test the function with a mock request
    class MockUser:
        is_authenticated = False
    
    class MockRequest:
        def __init__(self):
            self.user = MockUser()
    
    request = MockRequest()
    result = get_cart_amounts(request)
    print("✓ get_cart_amounts function works")
    print("Result:", result)
    
except Exception as e:
    print("ERROR:", str(e))
    import traceback
    traceback.print_exc()
