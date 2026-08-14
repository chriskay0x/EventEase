from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import ClientRegistrationForm, VendorRegistrationForm
from .models import User, VendorProfile

# 1. Client Registration View
def register_client_view(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto log-in after signup
            return redirect('accounts:login')  # Or discovery page
    else:
        form = ClientRegistrationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


# 2. Vendor Registration View
def register_vendor_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:get_started')

    if request.method == 'POST':
        business_name = request.POST.get('business_name')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        city = request.POST.get('city')
        password = request.POST.get('password')
        category = request.POST.get('category')

        # Check if email/username already exists in the database
        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            return render(request, 'accounts/vendor_signup.html', {
                'error': 'An account with this email address already exists. Please log in or use a different email.'
            })

        # Split full_name for first/last name
        name_parts = full_name.strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Create Custom User instance
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='vendor'
        )
        
        # Save Vendor Profile Details
        VendorProfile.objects.create(
            user=user,
            business_name=business_name,
            phone=phone,
            city=city,
            category=category
        )

        # Log in and redirect to business verification
        login(request, user)
        return redirect('accounts:verify_business')

    return render(request, 'accounts/vendor_signup.html')


# 3. Login View (With Role-Based Redirect)
def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:get_started')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                
                # Role-Based Redirection
                # if user.role == 'vendor':
                #     return redirect('accounts:vendor_dashboard')
                # elif user.role == 'admin':
                #     return redirect('admin:index')
                # else:
                #     return redirect('accounts:client_profile')  # Or search page
            else:
                return render(request, 'accounts/login.html', {
                    'error': 'Invalid email address or password.'
                })
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def get_started_view(request):
    # """Entry point screen allowing users to select Client vs Vendor onboarding."""
    # if request.user.is_authenticated:
    #     if request.user.role == 'vendor':
    #         return redirect('accounts:vendor_dashboard')
    #     return redirect('accounts:get_started')
        
    # return render(request, 'accounts/get_started.html')
    
    """Entry point screen allowing users to select Client vs Vendor onboarding."""
    # If already logged in, render or redirect somewhere else (NOT to get_started)
    if request.user.is_authenticated:
        # Temporary stub until Team 2's discovery route or Vendor dashboard is ready
        return render(request, 'accounts/get_started.html', {'logged_in_user': request.user})
        
    return render(request, 'accounts/get_started.html')


# 4. Logout View
def logout_view(request):
    logout(request)
    return redirect('accounts:login')