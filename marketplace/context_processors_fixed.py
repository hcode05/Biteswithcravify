from .models import Cart
from menu.models import FoodItem
from decimal import Decimal


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
            else:
                cart_count = 0
        except:
            cart_count = 0
    return dict(cart_count=cart_count)


def get_cart_amounts(request):
    subtotal = 0
    tax_dict = {}
    grand_total = 0
    
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            fooditem = FoodItem.objects.get(pk=item.fooditem.id)
            subtotal += (fooditem.price * item.quantity)

        # Try to use old tax system first (for compatibility)
        try:
            from .models import Tax
            get_tax = Tax.objects.filter(is_active=True)
            for i in get_tax:
                # Check if this is old tax structure
                if hasattr(i, 'tax_type') and hasattr(i, 'tax_percentage'):
                    tax_type = i.tax_type
                    tax_percentage = i.tax_percentage
                    tax_amount = round((tax_percentage * subtotal)/100, 2)
                    tax_dict.update({tax_type: {str(tax_percentage): tax_amount}})
                else:
                    # This might be new tax structure, skip for now
                    pass
        except Exception as e:
            # No tax system available or error, continue without taxes
            print(f"Tax calculation error: {e}")
            pass

        # Calculate grand total
        total_tax = 0
        for tax_type_data in tax_dict.values():
            for tax_amount in tax_type_data.values():
                total_tax += tax_amount
        
        grand_total = subtotal + total_tax

    return dict(subtotal=subtotal, tax_dict=tax_dict, grand_total=grand_total)
