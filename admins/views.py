from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
# ── MAIN PAGES ────────────────────────────────────────────────────────
# URL: http://127.0.0.1:8000/
# What it does: Shows the homepage with Login/Register/Admin Login buttons
def index(request):
    return render(request, 'index.html', {})
 
# URL: http://127.0.0.1:8000/AdminLogin/
# What it does: Shows the admin login form
def AdminLogin(request):
    return render(request, 'AdminLogin.html', {})
 
# URL: http://127.0.0.1:8000/UserLogin/
# What it does: Shows the user login form
def UserLogin(request):
    return render(request, 'UserLogin.html', {})
 
# URL: http://127.0.0.1:8000/UserRegister/
# What it does: Shows the user registration form
def UserRegister(request):
    from users.forms import UserRegistrationForm
    form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})
 
# ── ADMIN VIEWS ───────────────────────────────────────────────────────
# URL: http://127.0.0.1:8000/AdminLoginCheck/
# What it does: Receives admin login form POST, checks credentials, sets session
def AdminLoginCheck(request):
    from django.conf import settings
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            request.session['admin'] = True
            return redirect('AdminHome')
        return render(request, 'AdminLogin.html', {'error': 'Invalid credentials'})
    return redirect('AdminLogin')
 
# URL: http://127.0.0.1:8000/AdminHome/
# What it does: Admin dashboard — shows user count, prediction stats
# Protected: redirects to AdminLogin if admin session not set
@never_cache
def AdminHome(request):
    if not request.session.get('admin'):
        return redirect('AdminLogin')
    from users.models import UserProfile, PredictionHistory
    from django.db import models as dm
    total_users = UserProfile.objects.count()
    active_users = UserProfile.objects.filter(is_active=True).count()
    total_preds = PredictionHistory.objects.count()
    avg_price = PredictionHistory.objects.aggregate(a=dm.Avg('predicted_price'))['a'] or 0
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_predictions': total_preds,
        'avg_price': round(avg_price, 0)
    }
    return render(request, 'AdminHome.html', context)
 
# URL: http://127.0.0.1:8000/RegisterUsersView/
# What it does: Shows table of all registered users with Activate buttons
@never_cache
def RegisterUsersView(request):
    if not request.session.get('admin'):
        return redirect('AdminLogin')
    from users.models import UserProfile
    users = UserProfile.objects.all().order_by('-created_at')
    return render(request, 'RegisterUsersView.html', {'users': users})
 
# URL: http://127.0.0.1:8000/ActivaUsers/?id=5
# What it does: Sets is_active=True for user with given id, redirects back
def ActivaUsers(request):
    if not request.session.get('admin'):
        return redirect('AdminLogin')
    from users.models import UserProfile
    user_id = request.GET.get('id')
    user = UserProfile.objects.get(id=user_id)
    user.is_active = True
    user.save()
    return redirect('RegisterUsersView')
