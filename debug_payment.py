#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodonline_main.settings')
django.setup()

from orders.models import Order, Payment
from django.contrib.auth.models import User

def test_payment_scenario():
    print("=== TESTING PAYMENT SCENARIO ===")
    
    # Get the latest order
    try:
        latest_order = Order.objects.latest('created_at')
        print(f"Latest Order: {latest_order.order_number}")
        print(f"Status: {latest_order.status}")
        print(f"Is Ordered: {latest_order.is_ordered}")
        print(f"Payment: {latest_order.payment}")
        print(f"Total: {latest_order.total}")
        print(f"Payment Method: {latest_order.payment_method}")
        
        # Check if there are any payments for this order
        payments = Payment.objects.filter(user=latest_order.user).order_by('-created_at')
        print(f"\nPayments for user {latest_order.user}:")
        for payment in payments[:3]:
            print(f"  Payment ID: {payment.id}, Transaction: {payment.transaction_id}, Status: {payment.status}, Amount: {payment.amount}")
            
    except Order.DoesNotExist:
        print("No orders found")
        
    # Show all orders with status
    print(f"\nAll Orders Summary:")
    orders = Order.objects.all().order_by('-created_at')[:5]
    for order in orders:
        print(f"Order: {order.order_number} | Status: {order.status} | Ordered: {order.is_ordered} | Payment: {'Yes' if order.payment else 'No'}")

if __name__ == '__main__':
    test_payment_scenario()
