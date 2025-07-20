#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
project_path = r'c:\Users\ADMIN\Desktop\foodproject'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodonline_main.settings')

# Setup Django
django.setup()

from orders.models import Order, Payment
from accounts.models import User

print("=== Database Status ===")
print(f"Total Orders: {Order.objects.count()}")
print(f"Total Payments: {Payment.objects.count()}")
print(f"Total Users: {User.objects.count()}")

print("\n=== Recent Orders ===")
recent_orders = Order.objects.all().order_by('-created_at')[:5]
for order in recent_orders:
    print(f"Order: {order.order_number} | Status: {order.status} | Is_ordered: {order.is_ordered} | Payment: {order.payment} | User: {order.user}")

print("\n=== Recent Payments ===")
recent_payments = Payment.objects.all().order_by('-created_at')[:5]
for payment in recent_payments:
    print(f"Payment: {payment.transaction_id} | Status: {payment.status} | Amount: {payment.amount} | User: {payment.user}")

print("\n=== Orders without Payments ===")
orders_no_payment = Order.objects.filter(payment__isnull=True)
for order in orders_no_payment:
    print(f"Order: {order.order_number} | Status: {order.status} | Is_ordered: {order.is_ordered} | User: {order.user}")
