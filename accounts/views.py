from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import ClientRegistrationForm, VendorRegistrationForm

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
    
    return render(request, 'accounts/register_client.html', {'form': form})


# 2. Vendor Registration View
def register_vendor_view(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:login')
    else:
        form = VendorRegistrationForm()

    return render(request, 'accounts/register_vendor.html', {'form': form})


# 3. Login View (With Role-Based Redirect)
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Role-Based Redirection
                if user.role == 'vendor':
                    return redirect('accounts:vendor_dashboard')
                elif user.role == 'admin':
                    return redirect('admin:index')
                else:
                    return redirect('accounts:client_profile')  # Or search page
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def get_started_view(request):
    """Entry point screen allowing users to select Client vs Vendor onboarding."""
    if request.user.is_authenticated:
        if request.user.role == 'vendor':
            return redirect('accounts:vendor_dashboard')
        return redirect('listings:search')
        
    return render(request, 'accounts/get_started.html')


# 4. Logout View
def logout_view(request):
    logout(request)
    return redirect('accounts:login')
