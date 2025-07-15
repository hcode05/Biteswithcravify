from django.shortcuts import get_object_or_404,render,redirect
from django.http import HttpResponse, JsonResponse
from accounts.forms import UserProfileForm
from .forms import VendorForm,OpeningHourForm
from accounts.models import UserProfile
from vendor.models import Vendor
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from django.contrib.auth.decorators import login_required
from accounts.views import user_passes_test, check_role_vendor

from unicodedata import category
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem
from django.template.defaultfilters import slugify
from django.db import IntegrityError
from django.forms import inlineformset_factory
from .models import OpeningHour, Vendor
from .models import DAYS


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
        'form': OpeningHourForm(),  # Add a simple form for adding new hours
    }
    return render(request, 'vendor/opening_hours.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_opening_hours(request):
    if request.method == 'POST':
        try:
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed') == 'True'

            # Validate required fields
            if not day:
                return JsonResponse({'status': 'fail', 'message': 'Please select a day.'})

            if not is_closed and (not from_hour or not to_hour):
                return JsonResponse({'status': 'fail', 'message': 'Please provide both from and to hours when not closed.'})

            # Check if vendor exists
            if not hasattr(request.user, 'vendor'):
                return JsonResponse({'status': 'fail', 'message': 'Vendor profile not found.'})

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

        except Exception as e:
            return JsonResponse({'status': 'fail', 'message': f'An error occurred: {str(e)}'})

    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'}, status=400)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def remove_opening_hours(request, pk=None):
    try:
        # Ensure the opening hour belongs to the current vendor
        hour = get_object_or_404(OpeningHour, pk=pk, vendor=request.user.vendor)
        hour.delete()
        return JsonResponse({'status': 'success', 'id': pk})
    except OpeningHour.DoesNotExist:
        return JsonResponse({'status': 'fail', 'message': 'Opening hour not found.'})
    except Exception as e:
        return JsonResponse({'status': 'fail', 'message': f'An error occurred: {str(e)}'})