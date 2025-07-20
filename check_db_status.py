import os
import django
import sys

# Setup Django
sys.path.append(r'c:\Users\ADMIN\Desktop\foodproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodonline_main.settings')
django.setup()

from orders.models import Order, Payment

print("=== Recent Orders ===")
orders = Order.objects.all().order_by('-created_at')[:5]
for order in orders:
    print(f"Order Number: {order.order_number}")
    print(f"Status: {order.status}")
    print(f"Is Ordered: {order.is_ordered}")
    print(f"Payment: {order.payment}")
    print(f"Total: {order.total}")
    print(f"Created: {order.created_at}")
    print("---")

print("\n=== Recent Payments ===")
payments = Payment.objects.all().order_by('-created_at')[:5]
for payment in payments:
    print(f"Transaction ID: {payment.transaction_id}")
    print(f"Status: {payment.status}")
    print(f"Amount: {payment.amount}")
    print(f"Method: {payment.payment_method}")
    print(f"User: {payment.user}")
    print(f"Created: {payment.created_at}")
    print("---")
