#!/usr/bin/env python
"""
Test script to verify order completion redirect functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodonline_main.settings')
django.setup()

from orders.models import Order, Payment
from django.urls import reverse

def test_order_complete_redirect():
    """Test the order completion redirect functionality"""
    print("=== Testing Order Complete Redirect ===")
    
    # Get the latest order
    try:
        latest_order = Order.objects.filter(is_ordered=True).latest('created_at')
        print(f"✅ Found latest order: {latest_order.order_number}")
        print(f"   Order status: {latest_order.status}")
        print(f"   Is ordered: {latest_order.is_ordered}")
        print(f"   Payment method: {latest_order.payment_method}")
        
        if hasattr(latest_order, 'payment') and latest_order.payment:
            print(f"   Payment ID: {latest_order.payment.id}")
            print(f"   Transaction ID: {latest_order.payment.transaction_id}")
            
            # Generate the redirect URL
            order_complete_url = reverse('order_complete')
            redirect_url = f"{order_complete_url}?order_no={latest_order.order_number}&trans_id={latest_order.payment.transaction_id}"
            
            print(f"✅ Order complete URL: {order_complete_url}")
            print(f"✅ Full redirect URL: {redirect_url}")
            
            # Test if the order has ordered food items
            from orders.models import OrderedFood
            ordered_food_count = OrderedFood.objects.filter(order=latest_order).count()
            print(f"✅ Ordered food items: {ordered_food_count}")
            
            if ordered_food_count > 0:
                print("✅ Order has food items - redirect should work!")
                return redirect_url
            else:
                print("❌ Order has no food items - this might cause issues")
                return None
                
        else:
            print("❌ Order has no payment record")
            return None
            
    except Order.DoesNotExist:
        print("❌ No completed orders found")
        return None
    except Exception as e:
        print(f"❌ Error testing redirect: {str(e)}")
        return None

def test_payment_flow():
    """Test the payment flow and response"""
    print("\n=== Testing Payment Flow ===")
    
    try:
        latest_order = Order.objects.filter(is_ordered=True).latest('created_at')
        latest_payment = Payment.objects.filter(user=latest_order.user).latest('created_at')
        
        print(f"✅ Latest payment found:")
        print(f"   Payment ID: {latest_payment.id}")
        print(f"   Transaction ID: {latest_payment.transaction_id}")
        print(f"   Payment method: {latest_payment.payment_method}")
        print(f"   Status: {latest_payment.status}")
        print(f"   Amount: {latest_payment.amount}")
        
        # Simulate the response that should be sent to frontend
        response_data = {
            'order_number': latest_order.order_number,
            'transaction_id': latest_payment.transaction_id,
            'status': latest_payment.status,
            'order_status': latest_order.status,
            'is_ordered': latest_order.is_ordered,
            'success': True
        }
        
        print(f"✅ Expected AJAX response: {response_data}")
        return response_data
        
    except Exception as e:
        print(f"❌ Error testing payment flow: {str(e)}")
        return None

if __name__ == "__main__":
    print("Starting order completion redirect tests...")
    
    # Test 1: Order complete redirect
    redirect_url = test_order_complete_redirect()
    
    # Test 2: Payment flow
    payment_response = test_payment_flow()
    
    print("\n=== Test Summary ===")
    if redirect_url:
        print(f"✅ Redirect URL generated: {redirect_url}")
        print("   You can test this URL in your browser")
    else:
        print("❌ Could not generate redirect URL")
        
    if payment_response:
        print(f"✅ Payment response ready: {payment_response}")
    else:
        print("❌ Could not generate payment response")
    
    print("\n=== Manual Testing Instructions ===")
    print("1. Go to your order placement page")
    print("2. Complete a payment using the demo button")
    print("3. Check browser console for redirect logs")
    print("4. If redirect doesn't work, manually visit the redirect URL")
    print("5. The test redirect button should also work for debugging") 