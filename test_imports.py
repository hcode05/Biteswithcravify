#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodonline_main.settings')

try:
    django.setup()
    print("✓ Django setup successful")
    
    # Test imports
    from orders.views import payments, place_order, order_complete
    print("✓ Orders views imported successfully")
    
    from marketplace.views import add_to_cart, decrease_cart, delete_cart
    print("✓ Marketplace views imported successfully")
    
    from marketplace.context_processors import get_cart_amounts, get_cart_counter
    print("✓ Context processors imported successfully")
    
    from orders.models import Order, Payment, OrderedFood
    print("✓ Order models imported successfully")
    
    print("\n🎉 ALL IMPORTS SUCCESSFUL - No syntax errors!")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
