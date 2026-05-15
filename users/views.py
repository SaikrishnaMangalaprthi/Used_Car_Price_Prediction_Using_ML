from django.shortcuts import render, redirect
from django.http import HttpResponse
 
# Helper functions used by all views below
def is_logged_in(request):
    return request.session.get('user_id') is not None
 
def is_admin(request):
    return request.session.get('admin') is not None
 
# ── TO BE COMPLETED DAY 8 ────────────────────────────────────────────
def UserRegisterActions(request):
    from .forms import UserRegistrationForm
    from .models import UserProfile
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Check if this email is already registered
            if UserProfile.objects.filter(email=email).exists():
                return render(request, 'UserRegistrations.html', {
                    'form': form, 'error': 'This email is already registered. Please login.'})
            # Create user — is_active=False means they cannot login yet
            UserProfile.objects.create(
                name=name, email=email, password=password, is_active=False)
            return render(request, 'RegistrationSuccess.html', {})
        return render(request, 'UserRegistrations.html', {'form': form})
    return redirect('UserRegister')

 
# ── TO BE COMPLETED DAY 9 ────────────────────────────────────────────
def UserLoginCheck(request):
    from .models import UserProfile
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = UserProfile.objects.get(email=email, password=password)
            if user.is_active:
                # Store user info in session so pages know who is logged in
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('UserHome')
            else:
                return render(request, 'UserLogin.html', {
                    'error': 'Your account is not yet activated. Please contact the admin.'})
        except UserProfile.DoesNotExist:
            return render(request, 'UserLogin.html', {'error': 'Invalid email or password'})
    return redirect('UserLogin')

def UserHome(request):
    if not is_logged_in(request): return redirect('UserLogin')
    return render(request, 'UserHome.html', {})

# Logout clears the session immediately
def logout_user(request):
    request.session.flush()
    return redirect('index')
 
# ── TO BE COMPLETED DAY 17 ───────────────────────────────────────────
def training(request):
    if not is_logged_in(request): return redirect('UserLogin')
    return HttpResponse('Training coming Day 17')
 
# ── TO BE COMPLETED DAY 19 ───────────────────────────────────────────
def prediction(request):
    if not is_logged_in(request): return redirect('UserLogin')
    if request.method == 'POST':
        errors = []
        vehicle_age = request.POST.get('vehicle_age', '0')
        km = request.POST.get('km_driven', '0')
        try:
            if int(vehicle_age) < 0 or int(vehicle_age) > 25:
                errors.append('Vehicle age must be between 0 and 25 years')
            if int(km) < 500 or int(km) > 300000:
                errors.append('KM driven must be between 500 and 3,00,000')
        except ValueError:
            errors.append('Please enter valid numbers')
        if errors:
            return render(request, 'prediction.html', {'errors': errors})

        input_dict = {
            'vehicle_age': vehicle_age,
            'km_driven': km,
            'brand': request.POST.get('brand'),
            'seller_type': request.POST.get('seller_type'),
            'fuel_type': request.POST.get('fuel_type'),           # changed
            'transmission_type': request.POST.get('transmission_type'), # changed
            'mileage': request.POST.get('mileage', '18'),
            'engine': request.POST.get('engine', '1200'),
            'max_power': request.POST.get('max_power', '100')
        }
# ── TO BE COMPLETED DAY 21 ───────────────────────────────────────────
def DatasetView(request):
    if not is_logged_in(request): return redirect('UserLogin')
    return HttpResponse('Dataset view coming Day 21')
 
# ── TO BE COMPLETED DAY 22 ───────────────────────────────────────────
def prediction_history(request):
    if not is_logged_in(request): return redirect('UserLogin')
    return HttpResponse('History coming Day 22')
