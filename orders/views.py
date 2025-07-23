from urllib import response
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from marketplace.models import Cart, Tax
from marketplace.context_processors import get_cart_amounts
from menu.models import FoodItem
from .forms import OrderForm
from .models import Order, OrderedFood, Payment
import json
from .utils import generate_order_number, order_total_by_vendor
from accounts.utils import send_notification
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# import razorpay  # Commented out since module not installed
# from foodonline_main.settings import RZP_KEY_ID, RZP_KEY_SECRET
from django.contrib.sites.shortcuts import get_current_site
from vendor.models import Vendor


# client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))  # Commented out


@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    vendors_ids = []
    for i in cart_items:
        if i.fooditem.vendor.id not in vendors_ids:
            vendors_ids.append(i.fooditem.vendor.id)
    
    # Check if all restaurants in cart are currently open
    closed_restaurants = []
    for vendor_id in vendors_ids:
        vendor = Vendor.objects.get(id=vendor_id)
        if not vendor.is_open:
            closed_restaurants.append(vendor.vendor_name)
    
    if closed_restaurants:
        # If any restaurant is closed, show error and redirect
        from django.contrib import messages
        error_message = f"The following restaurants are currently closed: {', '.join(closed_restaurants)}. Please try again during their opening hours."
        messages.error(request, error_message)
        return redirect('marketplace')
    
    # {"vendor_id":{"subtotal":{"tax_type": {"tax_percentage": "tax_amount"}}}}
    get_tax = Tax.objects.filter(is_active=True)
    subtotal = 0
    total_data = {}
    k = {}
    for i in cart_items:
        fooditem = FoodItem.objects.get(pk=i.fooditem.id, vendor_id__in=vendors_ids)
        v_id = fooditem.vendor.id
        if v_id in k:
            subtotal = k[v_id]
            subtotal += (float(fooditem.price) * i.quantity)  # Convert price to float
            k[v_id] = subtotal
        else:
            subtotal = (float(fooditem.price) * i.quantity)  # Convert price to float
            k[v_id] = subtotal
    
        # Calculate the tax_data
        tax_dict = {}
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = float(i.tax_percentage)  # Convert to float
            tax_amount = round((tax_percentage * subtotal)/100, 2)
            tax_dict.update({tax_type: {str(tax_percentage) : str(tax_amount)}})
        # Construct total data
        total_data.update({fooditem.vendor.id: {str(subtotal): str(tax_dict)}})
    

    subtotal = get_cart_amounts(request)['subtotal']
    total_tax = get_cart_amounts(request)['tax']
    grand_total = get_cart_amounts(request)['grand_total']
    tax_data = get_cart_amounts(request)['tax_dict']
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Double-check restaurant opening hours before creating order
            closed_restaurants = []
            for vendor_id in vendors_ids:
                vendor = Vendor.objects.get(id=vendor_id)
                if not vendor.is_open:
                    closed_restaurants.append(vendor.vendor_name)
            
            if closed_restaurants:
                from django.contrib import messages
                error_message = f"The following restaurants are currently closed: {', '.join(closed_restaurants)}. Please try again during their opening hours."
                messages.error(request, error_message)
                return redirect('marketplace')
            
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = float(grand_total)  # Convert Decimal to float
            order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            order.total_tax = float(total_tax)  # Convert Decimal to float
            order.payment_method = request.POST['payment_method']
            order.save() # order id/ pk is generated
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()

            # RazorPay Payment
            DATA = {
                "amount": float(order.total) * 100,
                "currency": "INR",
                "receipt": "receipt #"+order.order_number,
                "notes": {
                    "key1": "value3",
                    "key2": "value2"
                }
            }
            # rzp_order = client.order.create(data=DATA)
            # rzp_order_id = rzp_order['id']

            context = {
                'order': order,
                'cart_items': cart_items,
                'subtotal': subtotal,
                'grand_total': grand_total,
                'tax_dict': tax_data,
                # 'rzp_order_id': rzp_order_id,
                # 'RZP_KEY_ID': RZP_KEY_ID,
                # 'rzp_amount': float(order.total) * 100,
            }
            return render(request, 'orders/place_order.html', context)

        else:
            print(form.errors)
            # Optionally, re-render the form with errors (not payment page)
            return redirect('marketplace')
    # For GET requests, do not render the payment page with an invalid order
    return redirect('marketplace')


@login_required(login_url='login')
@csrf_exempt
def payments(request):
    print(f"DEBUG: ===== PAYMENTS VIEW CALLED =====")
    print(f"DEBUG: Request method: {request.method}")
    print(f"DEBUG: User: {request.user}")
    print(f"DEBUG: User authenticated: {request.user.is_authenticated}")
    print(f"DEBUG: Request headers: {dict(request.headers)}")
    print(f"DEBUG: POST data: {dict(request.POST)}")
    print(f"DEBUG: GET data: {dict(request.GET)}")
    
    # Check if user is authenticated
    if not request.user.is_authenticated:
        print("DEBUG: User not authenticated - returning error")
        return JsonResponse({
            'error': 'Authentication required',
            'message': 'User must be logged in to process payments.'
        }, status=401)
    
    # Check if the request is ajax or POST
    if request.method == 'POST':
        try:
            # STORE THE PAYMENT DETAILS IN THE PAYMENT MODEL
            order_number = request.POST.get('order_number')
            transaction_id = request.POST.get('transaction_id')
            payment_method = request.POST.get('payment_method')
            status = request.POST.get('status')

            print(f"DEBUG: Processing payment for order {order_number}")
            print(f"DEBUG: Received data - Transaction ID: {transaction_id}, Method: {payment_method}, Status: {status}")
            
            if not all([order_number, transaction_id, payment_method, status]):
                print("DEBUG: Missing required payment data")
                print(f"DEBUG: order_number: {order_number}, transaction_id: {transaction_id}, payment_method: {payment_method}, status: {status}")
                return JsonResponse({
                    'error': 'Missing payment data',
                    'message': 'Required payment information is missing.'
                }, status=400)

            # Get the order
            try:
                order = Order.objects.get(user=request.user, order_number=order_number)
                print(f"DEBUG: Found order {order_number} for user {request.user.email}")
            except Order.DoesNotExist:
                print(f"DEBUG: Order {order_number} not found for user {request.user.email}")
                return JsonResponse({
                    'error': 'Order not found',
                    'message': 'Order not found or does not belong to this user.'
                }, status=404)
            except Exception as e:
                print(f"DEBUG: Error getting order: {str(e)}")
                return JsonResponse({
                    'error': 'Database error',
                    'message': f'Error retrieving order: {str(e)}'
                }, status=500)
            
            # Check if order is already paid
            if order.is_ordered:
                print(f"DEBUG: Order {order_number} already processed")
                return JsonResponse({
                    'error': 'Order already processed',
                    'message': 'This order has already been paid for.'
                }, status=400)
            # STORE THE PAYMENT DETAILS IN THE PAYMENT MODEL
            try:
                payment = Payment(
                    user = request.user,
                    transaction_id = transaction_id,
                    payment_method = payment_method,
                    amount = str(order.total),  # Convert to string since model field is CharField
                    status = status
                )
                payment.save()
                print(f"DEBUG: Payment created with ID: {payment.id}, Amount: {payment.amount}")
            except Exception as e:
                print(f"DEBUG: Error creating payment: {str(e)}")
                return JsonResponse({
                    'error': 'Payment creation failed',
                    'message': f'Failed to create payment record: {str(e)}'
                }, status=500)

            # UPDATE THE ORDER MODEL
            try:
                order.payment = payment
                order.is_ordered = True
                
                # Update order status based on payment status (case insensitive)
                status_upper = status.upper() if status else ''
                print(f"DEBUG: Payment status received: '{status}' (normalized: '{status_upper}')")
                
                if status_upper in ['SUCCESS', 'COMPLETED']:
                    order.status = 'Accepted'
                    print(f"DEBUG: Order {order.order_number} status set to Accepted")
                elif status_upper in ['FAILED', 'FAILURE', 'ERROR']:
                    order.status = 'Cancelled'
                    print(f"DEBUG: Order {order.order_number} status set to Cancelled")
                else:
                    order.status = 'New'
                    print(f"DEBUG: Order {order.order_number} status remains New due to unknown status: {status}")
                
                order.save()
                print(f"DEBUG: Order saved - Status: {order.status}, Is Ordered: {order.is_ordered}, Payment ID: {payment.id}")
            except Exception as e:
                print(f"DEBUG: Error updating order: {str(e)}")
                return JsonResponse({
                    'error': 'Order update failed',
                    'message': f'Failed to update order: {str(e)}'
                }, status=500)

            # MOVE THE CART ITEMS TO ORDERED FOOD MODEL
            try:
                cart_items = Cart.objects.filter(user=request.user)
                for item in cart_items:
                    ordered_food = OrderedFood()
                    ordered_food.order = order
                    ordered_food.payment = payment
                    ordered_food.user = request.user
                    ordered_food.fooditem = item.fooditem
                    ordered_food.quantity = item.quantity
                    ordered_food.price = float(item.fooditem.price)  # Convert to float
                    ordered_food.amount = float(item.fooditem.price) * item.quantity # total amount
                    ordered_food.save()
                print(f"DEBUG: Created {cart_items.count()} OrderedFood records")
            except Exception as e:
                print(f"DEBUG: Error creating ordered food records: {str(e)}")
                return JsonResponse({
                    'error': 'OrderedFood creation failed',
                    'message': f'Failed to create ordered food records: {str(e)}'
                }, status=500)
            # SEND ORDER CONFIRMATION EMAIL TO THE CUSTOMER
            try:
                mail_subject = 'Thank you for ordering with us.'
                mail_template = 'orders/order_confirmation_email.html'

                ordered_food = OrderedFood.objects.filter(order=order)
                customer_subtotal = 0
                for item in ordered_food:
                    customer_subtotal += (float(item.price) * item.quantity)
                tax_data = json.loads(order.tax_data)
                context = {
                    'user': request.user,
                    'order': order,
                    'to_email': order.email,
                    'ordered_food': ordered_food,
                    'domain': get_current_site(request),
                    'customer_subtotal': customer_subtotal,
                    'tax_data': tax_data,
                }
                send_notification(mail_subject, mail_template, context)
                print(f"DEBUG: Customer email sent successfully to {order.email}")
            except Exception as e:
                print(f"DEBUG: Failed to send customer email: {str(e)}")
                # Don't return error - continue with vendor emails
            # SEND ORDER RECEIVED EMAIL TO THE VENDOR
            try:
                mail_subject = 'You have received a new order.'
                mail_template = 'orders/new_order_received.html'
                to_emails = []
                for i in cart_items:
                    if i.fooditem.vendor.user.email not in to_emails:
                        to_emails.append(i.fooditem.vendor.user.email)

                        ordered_food_to_vendor = OrderedFood.objects.filter(order=order, fooditem__vendor=i.fooditem.vendor)
                        print(ordered_food_to_vendor)

                
                        context = {
                            'order': order,
                            'to_email': i.fooditem.vendor.user.email,
                            'ordered_food_to_vendor': ordered_food_to_vendor,
                            'vendor_subtotal': order_total_by_vendor(order, i.fooditem.vendor.id)['subtotal'],
                            'tax_data': order_total_by_vendor(order, i.fooditem.vendor.id)['tax_dict'],
                            'vendor_grand_total': order_total_by_vendor(order, i.fooditem.vendor.id)['grand_total'],
                        }
                        send_notification(mail_subject, mail_template, context)
                print(f"DEBUG: Vendor emails sent successfully to {len(to_emails)} vendors")
            except Exception as e:
                print(f"DEBUG: Failed to send vendor emails: {str(e)}")
                # Don't return error - continue with cart clearing

            # CLEAR THE CART IF THE PAYMENT IS SUCCESS
            try:
                status_upper = status.upper() if status else ''
                if status_upper in ['SUCCESS', 'COMPLETED']:
                    cart_items_count = cart_items.count()
                    cart_items.delete()
                    print(f"DEBUG: Cart cleared for user {request.user.email} after successful payment - {cart_items_count} items removed") 
                else:
                    print(f"DEBUG: Cart NOT cleared - payment status was '{status}' (normalized: '{status_upper}')")
            except Exception as e:
                print(f"DEBUG: Failed to clear cart: {str(e)}")
                # Don't return error - continue with response

            # RETURN BACK TO AJAX WITH THE STATUS SUCCESS OR FAILURE
            # Final defensive check before returning success
            if not all([order_number, transaction_id, status, order.status, order.is_ordered]):
                print(f"DEBUG: Final check failed before returning success. Data: order_number={order_number}, transaction_id={transaction_id}, status={status}, order_status={order.status}, is_ordered={order.is_ordered}")
                return JsonResponse({
                    'error': 'Internal error',
                    'message': 'Order processed but response data is incomplete. Please contact support.'
                }, status=500)
            response = {
                'order_number': order_number,
                'transaction_id': transaction_id,
                'status': status,
                'order_status': order.status,
                'is_ordered': order.is_ordered,
                'success': True  # Add explicit success flag
            }
            print(f"DEBUG: Returning response: {response}")
            return JsonResponse(response)
            
        except Exception as e:
            print(f"DEBUG: Error in payment processing: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'error': 'Payment processing failed',
                'message': f'An error occurred: {str(e)}'
            }, status=500)
    else:
        print(f"DEBUG: Invalid request method: {request.method}")
        return JsonResponse({
            'error': 'Invalid request',
            'message': 'This endpoint only accepts POST requests.'
        }, status=400)


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)

        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)
        print(tax_data)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('home')
    