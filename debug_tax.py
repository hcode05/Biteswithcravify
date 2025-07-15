#!/usr/bin/env python
import os
import sys
import django

# Add the project path
sys.path.append('c:/Users/ADMIN/Desktop/foodproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodonline_main.settings')

django.setup()

from marketplace.models import Tax, Cart
from accounts.models import User
from marketplace.context_processors import get_cart_amounts
from django.test import RequestFactory

def test_tax_calculation():
    print("=== Testing Tax System ===")
    
    # Check if there are any taxes configured
    taxes = Tax.objects.all()
    print(f"Total taxes configured: {taxes.count()}")
    
    for tax in taxes:
        print(f"- {tax.tax_type}: {tax.tax_percentage}% (Active: {tax.is_active})")
    
    # Check if there are any active taxes
    active_taxes = Tax.objects.filter(is_active=True)
    print(f"Active taxes: {active_taxes.count()}")
    
    # Check if there are any cart items
    total_cart_items = Cart.objects.count()
    print(f"Total cart items in system: {total_cart_items}")
    
    # Try to simulate cart calculation for a user
    try:
        # Get a user with cart items
        users_with_cart = Cart.objects.values('user').distinct()
        if users_with_cart:
            user_id = users_with_cart[0]['user']
            user = User.objects.get(id=user_id)
            print(f"Testing with user: {user.email}")
            
            # Create a mock request
            factory = RequestFactory()
            request = factory.get('/cart/')
            request.user = user
            
            # Get cart amounts
            amounts = get_cart_amounts(request)
            print("Cart calculation results:")
            print(f"- Subtotal: ${amounts['subtotal']}")
            print(f"- Tax dict: {amounts['tax_dict']}")
            print(f"- Tax total: ${amounts.get('tax', 0)}")
            print(f"- Grand total: ${amounts['grand_total']}")
            
        else:
            print("No cart items found for any user")
            
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test_tax_calculation()
