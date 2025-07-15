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

        # Try to use new tax system, fallback to old system
        try:
            # Check if new Tax model structure exists
            from .models import Tax, TaxCategory
            # New dynamic tax system
            taxes = Tax.objects.filter(is_active=True).order_by('priority')
            
            for tax in taxes:
                if tax.calculation_type == 'percentage':
                    tax_amount = round((tax.rate * subtotal) / 100, 2)
                else:  # fixed amount
                    tax_amount = tax.rate
                
                tax_category = tax.category.name
                if tax_category not in tax_dict:
                    tax_dict[tax_category] = {}
                
                tax_dict[tax_category][f"{tax.rate}%"] = tax_amount
                
        except (ImportError, Exception):
            # Fallback to old tax system
            try:
                from .models import Tax
                get_tax = Tax.objects.filter(is_active=True)
                for i in get_tax:
                    tax_type = i.tax_type
                    tax_percentage = i.tax_percentage
                    tax_amount = round((tax_percentage * subtotal)/100, 2)
                    tax_dict.update({tax_type: {str(tax_percentage): tax_amount}})
            except:
                # No tax system available
                pass

        # Calculate grand total
        total_tax = 0
        for key in tax_dict.values():
            for x in key:
                total_tax += tax_dict[tax_type][x]
        
        grand_total = subtotal + total_tax

    return dict(subtotal=subtotal, tax_dict=tax_dict, grand_total=grand_total)
