from django.shortcuts import redirect,render
from django.http import HttpResponse
from .forms import UserForm, UserProfileForm
from .models import User, UserProfile
from django.contrib import messages,auth
from vendor.forms import VendorForm
from .utils import detectUser, send_verification_email
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from vendor.models import Vendor
from django.template.defaultfilters import slugify

# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied

def registerUser(request):
    if request.user.is_authenticated:
        return redirect('myAccount')  

    if request.method == 'POST':
        form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid() and profile_form.is_valid():
            try:
                # Create user
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                
                user = User.objects.create_user(
                    first_name=first_name, 
                    last_name=last_name, 
                    username=username, 
                    email=email, 
                    password=password
                )
                user.role = User.CUSTOMER
                user.is_active = True
                user.save()  # This triggers signal to create UserProfile

                # Get the UserProfile created by signal and update it
                user_profile = UserProfile.objects.get(user=user)
                
                # Update the profile with form data
                for field_name in profile_form.cleaned_data:
                    setattr(user_profile, field_name, profile_form.cleaned_data[field_name])
                
                user_profile.save()

                messages.success(request, 'Your account has been registered successfully!')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
                print(f"Registration error: {e}")
        else:
            messages.error(request, 'Please fix the errors below.')
            print("Form errors:", form.errors)
            print("Profile form errors:", profile_form.errors)
    else:
        form = UserForm()
        profile_form = UserProfileForm()

    context = {
        'form': form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/registerUser.html', context)


def registerVendor(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)
            vendor_name = v_form.cleaned_data['vendor_name']
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            send_verification_email(request, user)
            
            return redirect('registerVendor')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()

    context = {
        'form': form,
        'v_form': v_form,
    }

    return render (request, 'accounts/registerVendor.html', context)

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('myAccount')
    else:
        return redirect('myAccount')
        
def login(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in!')
        return redirect('myAccount')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            user = auth.authenticate(request, username=email, password=password)
            
            if user is not None and user.is_active:
                auth.login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('myAccount')
            else:
                messages.error(request, 'Invalid email or password.')
                print(f"Authentication failed for email: {email}")
                return render(request, 'accounts/login.html')
        else:
            messages.error(request, 'Please enter both email and password.')
            return render(request, 'accounts/login.html')

    return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custdashboard(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        # Get recent orders for the dashboard
        from orders.models import Order
        recent_orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')[:5]
        
        context = {
            'user_profile': user_profile,
            'user': request.user,
            'recent_orders': recent_orders,
        }
    except UserProfile.DoesNotExist:
        # If no profile exists, create one with default values
        user_profile = UserProfile.objects.create(user=request.user)
        from orders.models import Order
        recent_orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')[:5]
        
        context = {
            'user_profile': user_profile,
            'user': request.user,
            'recent_orders': recent_orders,
        }
    
    return render(request, 'accounts/custDashboard.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendordashboard(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
        context = {'vendor': vendor}
        return render(request, 'accounts/vendorDashboard.html', context)
    except Vendor.DoesNotExist:
        return redirect('myAccount')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = 'Reset Your Password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            return redirect('login')
        else:
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    # validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        return redirect('reset_password')
    else:
        return redirect('myAccount')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            return redirect('login')
        else:
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')
