#!/usr/bin/env python
import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodonline_main.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

# Now import models
from orders.models import Order, Payment, OrderedFood
from django.contrib.auth import get_user_model

User = get_user_model()

# Check latest data
print("Latest Orders:")
orders = Order.objects.all().order_by('-created_at')[:3]
for order in orders:
    print(f"  Order: {order.order_number} | Status: {order.status} | Is_ordered: {order.is_ordered} | Payment: {order.payment}")

print("\nLatest Payments:")
payments = Payment.objects.all().order_by('-created_at')[:3]
for payment in payments:
    print(f"  Payment: {payment.transaction_id} | Status: {payment.status} | Amount: {payment.amount}")

print("\nLatest Ordered Foods:")
ordered_foods = OrderedFood.objects.all().order_by('-order__created_at')[:3]
for food in ordered_foods:
    print(f"  Food: {food.fooditem.food_title} | Order: {food.order.order_number} | Qty: {food.quantity}")
