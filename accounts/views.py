from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import ClientRegistrationForm, VendorRegistrationForm
from .models import User, VendorProfile, BookingRequest, VendorActivity
from django.db.models import Sum
from django.contrib import messages

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

# Verify Business View
@login_required(login_url='accounts:login')
def verify_business_view(request):
    """View to collect business verification documents from vendor partners."""
    vendor_profile, created = VendorProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action', 'submit')
        legal_business_name = request.POST.get('legal_business_name')
        uploaded_doc = request.FILES.get('verification_document')

        if legal_business_name:
            vendor_profile.legal_business_name = legal_business_name

        if uploaded_doc:
            vendor_profile.verification_document = uploaded_doc

        if action == 'submit':
            vendor_profile.verification_status = VendorProfile.VerificationStatus.PENDING
            vendor_profile.save()
            return redirect('accounts:verification_pending')
        else:
            vendor_profile.verification_status = VendorProfile.VerificationStatus.DRAFT
            vendor_profile.save()
            return redirect('accounts:get_started')

    return render(request, 'accounts/verify_business.html', {
        'vendor_profile': vendor_profile
    })
    
    
@login_required(login_url='accounts:login')
def verification_pending_view(request):
    """Screen shown to vendors while their submitted documents are under review."""
    vendor_profile = getattr(request.user, 'vendor_profile', None)
    return render(request, 'accounts/verification_pending.html', {
        'vendor_profile': vendor_profile
    })
    
    
@login_required(login_url='accounts:login')
def vendor_settings_view(request):
    vendor_profile, _ = VendorProfile.objects.get_or_create(user=request.user)
    user = request.user

    if request.method == 'POST':
        # 1. Profile Photo actions
        if request.POST.get('remove_photo') == 'true':
            if vendor_profile.avatar:
                vendor_profile.avatar.delete(save=False)
                vendor_profile.avatar = None
        elif 'avatar' in request.FILES:
            vendor_profile.avatar = request.FILES['avatar']

        # 2. Personal Details
        full_name = request.POST.get('full_name', '').strip()
        if full_name:
            name_parts = full_name.split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        email = request.POST.get('email', '').strip()
        if email:
            user.email = email
            user.username = email
        user.save()

        # 3. Business Information
        vendor_profile.phone = request.POST.get('phone', vendor_profile.phone)
        vendor_profile.bio = request.POST.get('bio', vendor_profile.bio)
        vendor_profile.instagram_handle = request.POST.get('instagram_handle', vendor_profile.instagram_handle)
        vendor_profile.website_url = request.POST.get('website_url', vendor_profile.website_url)
        vendor_profile.city = request.POST.get('city', vendor_profile.city)

        # 4. Notification & Security Switches (Checkboxes)
        vendor_profile.email_notifications = request.POST.get('email_notifications') == 'on'
        vendor_profile.sms_alerts = request.POST.get('sms_alerts') == 'on'
        vendor_profile.two_factor_enabled = request.POST.get('two_factor_enabled') == 'on'
        vendor_profile.save()

        # 5. Password Update (Optional)
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if current_password and new_password:
            if not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
                return redirect('accounts:vendor_settings')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
                return redirect('accounts:vendor_settings')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
                return redirect('accounts:vendor_settings')
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Keep user logged in
                messages.success(request, 'Password and settings updated successfully!')
                return redirect('accounts:vendor_settings')

        messages.success(request, 'Account settings saved successfully!')
        return redirect('accounts:vendor_settings')

    return render(request, 'accounts/vendor_settings.html', {
        'vendor_profile': vendor_profile,
        'user': user
    })
    
    
    
@login_required(login_url='accounts:login')
def vendor_dashboard_view(request):
    """Vendor Hub Overview Dashboard."""
    vendor_profile, _ = VendorProfile.objects.get_or_create(user=request.user)

    # Populate default demo records if empty for a fresh vendor
    if not vendor_profile.booking_requests.exists():
        BookingRequest.objects.create(vendor=vendor_profile, client_name="Eleanor Shellstrop", event_date="2026-10-24", status="pending", amount=12000)
        BookingRequest.objects.create(vendor=vendor_profile, client_name="Chidi Anagonye", event_date="2026-11-12", status="confirmed", amount=8500)
        BookingRequest.objects.create(vendor=vendor_profile, client_name="Tahani Al-Jamil", event_date="2026-12-05", status="pending", amount=4000)

    if not vendor_profile.activities.exists():
        VendorActivity.objects.create(vendor=vendor_profile, title="Jason Mendoza left a 5-star review for The Grand Ballroom.", activity_type="review")
        VendorActivity.objects.create(vendor=vendor_profile, title="New listing view surge on Riverside Garden.", activity_type="surge")
        VendorActivity.objects.create(vendor=vendor_profile, title="Scheduled maintenance for your dashboard completed.", activity_type="system")

    # Metrics
    total_revenue = vendor_profile.booking_requests.filter(status='confirmed').aggregate(Sum('amount'))['amount__sum'] or 24500
    active_bookings_count = vendor_profile.booking_requests.count()
    pending_inquiries_count = vendor_profile.booking_requests.filter(status='pending').count()

    booking_requests = vendor_profile.booking_requests.all().order_by('-created_at')[:5]
    activities = vendor_profile.activities.all()[:5]

    return render(request, 'accounts/vendor_dashboard.html', {
        'vendor_profile': vendor_profile,
        'user': request.user,
        'total_revenue': total_revenue,
        'active_bookings_count': active_bookings_count,
        'pending_inquiries_count': pending_inquiries_count,
        'booking_requests': booking_requests,
        'activities': activities,
    })