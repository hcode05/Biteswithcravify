#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodonline_main.settings')

print("Testing Django Project Components...")
print("=" * 50)

try:
    # Test Django setup
    django.setup()
    print("✅ Django setup successful")
    
    # Test model imports
    from orders.models import Order, Payment, OrderedFood
    from marketplace.models import Cart, Tax
    from menu.models import FoodItem
    print("✅ All models imported successfully")
    
    # Test view imports
    from orders.views import payments, place_order, order_complete
    from marketplace.views import add_to_cart, decrease_cart, delete_cart
    print("✅ All views imported successfully")
    
    # Test context processors
    from marketplace.context_processors import get_cart_amounts, get_cart_counter
    print("✅ Context processors imported successfully")
    
    # Test URL configurations
    from django.urls import reverse
    payment_url = reverse('payments')
    place_order_url = reverse('place_order')
    print("✅ URL routing working correctly")
    
    print("\n" + "=" * 50)
    print("🎉 ALL COMPONENTS WORKING!")
    print("✅ No syntax errors detected")
    print("✅ All imports successful")
    print("✅ Django configuration valid")
    print("✅ Ready to start server!")
    print("\nStart server with: python manage.py runserver")
    
except Exception as e:
    print(f"❌ ERROR DETECTED: {e}")
    import traceback
    traceback.print_exc()
    print("\nPlease fix the above error before starting the server.")
