from django.shortcuts import get_object_or_404,render,redirect
from django.http import HttpResponse, JsonResponse
from accounts.forms import UserProfileForm
from .forms import VendorForm,OpeningHourForm
from accounts.models import UserProfile
from vendor.models import Vendor
from django.contrib import messages
from orders.models import Order, OrderedFood
from orders.utils import order_total_by_vendor

from django.contrib.auth.decorators import login_required
from accounts.views import user_passes_test, check_role_vendor
from django.contrib.auth import update_session_auth_hash

from unicodedata import category
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem
from django.template.defaultfilters import slugify
from django.db import IntegrityError
from django.forms import inlineformset_factory
from .models import OpeningHour, Vendor
from .models import DAYS
from django.db.models import Sum
from django.utils import timezone


def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Settings updated.')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance = profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }
    return render(request, 'vendor/vprofile.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/menu_builder.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {
        'fooditems': fooditems,
        'category': category,
    }
    return render(request, 'vendor/fooditems_by_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            
            category.save() # here the category id will be generated
            category.slug = slugify(category_name)+'-'+str(category.id) # chicken-15
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)

    else:
        form = CategoryForm()
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)

    else:
        form = CategoryForm(instance=category)
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'vendor/edit_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category has been deleted successfully!')
    return redirect('menu_builder')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle)
            form.save()
            messages.success(request, 'Food Item added successfully!')
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        # modify this form
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_food.html', context)



@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle)
            form.save()
            messages.success(request, 'Food Item updated successfully!')
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)

    else:
        form = FoodItemForm(instance=food)
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
        'food': food,
    }
    return render(request, 'vendor/edit_food.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, 'Food Item has been deleted successfully!')
    return redirect('fooditems_by_category', food.category.id)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor=request.user.vendor).order_by('day')
    
    # Create formset for all days
    OpeningHourFormSet = inlineformset_factory(
        Vendor, OpeningHour, 
        form=OpeningHourForm, 
        extra=0, 
        can_delete=False,
        fields=('day', 'from_hour', 'to_hour', 'is_closed')
    )
    
    if request.method == 'POST':
        formset = OpeningHourFormSet(request.POST, instance=request.user.vendor)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Opening hours updated successfully!')
            return redirect('opening_hours')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        formset = OpeningHourFormSet(instance=request.user.vendor)
        
        # If no opening hours exist, create them
        if not opening_hours.exists():
            for day_num, day_name in DAYS:
                OpeningHour.objects.get_or_create(
                    vendor=request.user.vendor,
                    day=day_num,
                    defaults={'is_closed': True}
                )
            formset = OpeningHourFormSet(instance=request.user.vendor)
    
    context = {
        'formset': formset,
        'opening_hours': opening_hours,
    }
    return render(request, 'vendor/opening_hours.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_opening_hours(request):
    if request.method == 'POST':
        day = request.POST.get('day')
        from_hour = request.POST.get('from_hour')
        to_hour = request.POST.get('to_hour')
        is_closed = request.POST.get('is_closed') == 'True'

        # Optional: prevent duplicate entries for the same day
        if OpeningHour.objects.filter(vendor=request.user.vendor, day=day).exists():
            return JsonResponse({'status': 'fail', 'message': 'Opening hour already exists for this day.'})

        opening_hour = OpeningHour(
            vendor=request.user.vendor,
            day=day,
            from_hour=None if is_closed else from_hour,
            to_hour=None if is_closed else to_hour,
            is_closed=is_closed
        )
        opening_hour.save()

        return JsonResponse({
            'status': 'success',
            'id': opening_hour.id,
            'day': opening_hour.get_day_display(),
            'from_hour': str(opening_hour.from_hour) if opening_hour.from_hour else '',
            'to_hour': str(opening_hour.to_hour) if opening_hour.to_hour else '',
            'is_closed': 'Closed' if opening_hour.is_closed else 'Open'
        })

    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'}, status=400)

def remove_opening_hours(request, pk=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({'status': 'success', 'id': pk})


# Vendor Order Management Views
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendor_orders(request):
    """Vendor's order management page"""
    vendor = get_vendor(request)
    
    # Get all orders for this vendor
    vendor_orders = Order.objects.filter(
        vendors=vendor,
        is_ordered=True
    )
    
    context = {
        'vendor': vendor,
        'orders': vendor_orders,
    }
    return render(request, 'vendor/vendor_orders.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendor_order_detail(request, order_number):
    """Vendor's order detail page"""
    vendor = get_vendor(request)
    
    try:
        order = Order.objects.get(
            order_number=order_number,
            vendors=vendor,
            is_ordered=True
        )
        
        # Get ordered food items for this vendor only
        ordered_food = OrderedFood.objects.filter(
            order=order,
            fooditem__vendor=vendor
        )
        
        # Calculate order totals for this vendor
        order_data = order_total_by_vendor(order, vendor.id)
        
        context = {
            'vendor': vendor,
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': order_data['subtotal'],
            'tax_data': order_data['tax_dict'],
            'grand_total': order_data['grand_total'],
        }
        return render(request, 'vendor/vendor_order_detail.html', context)
        
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('vendor_orders')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def update_order_status(request, order_number):
    """Update order status (Accept/Reject/Complete)"""
    if request.method == 'POST':
        vendor = get_vendor(request)
        new_status = request.POST.get('status')
        
        try:
            order = Order.objects.get(
                order_number=order_number,
                vendors=vendor,
                is_ordered=True
            )
            
            # Update order status
            if new_status in ['Accepted', 'Rejected', 'Completed']:
                order.status = new_status
                order.save()
                messages.success(request, f'Order status updated to {new_status}')
            else:
                messages.error(request, 'Invalid status')
                
        except Order.DoesNotExist:
            messages.error(request, 'Order not found')
    
    return redirect('vendor_order_detail', order_number=order_number)

def vendor_earnings(request):
    return render(request, 'vendor/vendor_earnings.html')

def vendor_statement(request):
    return render(request, 'vendor/vendor_statement.html')

@login_required
def vendor_change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        user = request.user
        if not user.check_password(old_password):
            messages.error(request, 'Old password is incorrect.')
        elif new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password1) < 8:
            messages.error(request, 'New password must be at least 8 characters.')
        else:
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
    return render(request, 'vendor/vendor_change_password.html')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendordashboard(request):
    vendor = get_vendor(request)
    # Total revenue (all time)
    all_orders = Order.objects.filter(vendors=vendor, is_ordered=True)
    total_revenue = 0
    for order in all_orders:
        order_data = order_total_by_vendor(order, vendor.id)
        total_revenue += order_data['grand_total']
    # Current month revenue
    now = timezone.now()
    month_orders = all_orders.filter(created_at__year=now.year, created_at__month=now.month)
    month_revenue = 0
    for order in month_orders:
        order_data = order_total_by_vendor(order, vendor.id)
        month_revenue += order_data['grand_total']
    # Recent orders
    recent_orders = all_orders.order_by('-created_at')[:5]
    context = {
        'vendor': vendor,
        'total_orders': all_orders.count(),
        'total_revenue': total_revenue,
        'month_revenue': month_revenue,
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/vendorDashboard.html', context)