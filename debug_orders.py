#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodonline_main.settings')
django.setup()

from orders.models import Order, Payment, OrderedFood
from django.contrib.auth.models import User

def debug_orders():
    print("=== DEBUGGING ORDERS AND PAYMENTS ===")
    
    # Get all orders
    orders = Order.objects.all().order_by('-created_at')
    print(f"\nTotal Orders: {orders.count()}")
    
    for order in orders[:5]:  # Show last 5 orders
        print(f"\n--- Order: {order.order_number} ---")
        print(f"User: {order.user}")
        print(f"Status: {order.status}")
        print(f"Is Ordered: {order.is_ordered}")
        print(f"Payment Method: {order.payment_method}")
        print(f"Total: ${order.total}")
        print(f"Created: {order.created_at}")
        
        if order.payment:
            print(f"Payment ID: {order.payment.id}")
            print(f"Transaction ID: {order.payment.transaction_id}")
            print(f"Payment Status: {order.payment.status}")
            print(f"Payment Amount: ${order.payment.amount}")
        else:
            print("Payment: None")
    
    # Get all payments
    payments = Payment.objects.all().order_by('-created_at')
    print(f"\n\nTotal Payments: {payments.count()}")
    
    for payment in payments[:5]:  # Show last 5 payments
        print(f"\n--- Payment: {payment.transaction_id} ---")
        print(f"User: {payment.user}")
        print(f"Method: {payment.payment_method}")
        print(f"Amount: ${payment.amount}")
        print(f"Status: {payment.status}")
        print(f"Created: {payment.created_at}")
    
    # Check for orders without payments
    orders_without_payment = Order.objects.filter(payment__isnull=True)
    print(f"\n\nOrders without payment: {orders_without_payment.count()}")
    
    for order in orders_without_payment:
        print(f"Order {order.order_number} - Status: {order.status} - Is Ordered: {order.is_ordered}")

if __name__ == '__main__':
    debug_orders()
