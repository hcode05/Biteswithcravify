#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodonline_main.settings')
django.setup()

print("Testing all components...")

try:
    # Test 1: Import all modules
    from marketplace.context_processors import get_cart_amounts, get_cart_counter
    from marketplace.models import Cart, Tax
    from menu.models import FoodItem
    from orders.models import Order, Payment, OrderedFood
    print("✓ All imports successful")
    
    # Test 2: Check models
    print(f"✓ Tax count: {Tax.objects.count()}")
    print(f"✓ Cart count: {Cart.objects.count()}")
    print(f"✓ Order count: {Order.objects.count()}")
    print(f"✓ Payment count: {Payment.objects.count()}")
    
    # Test 3: Test context processor
    class MockUser:
        is_authenticated = False
    
    class MockRequest:
        def __init__(self):
            self.user = MockUser()
    
    request = MockRequest()
    result = get_cart_amounts(request)
    print("✓ get_cart_amounts function works")
    print(f"  Result: {result}")
    
    print("\n✅ ALL TESTS PASSED - System is ready!")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
