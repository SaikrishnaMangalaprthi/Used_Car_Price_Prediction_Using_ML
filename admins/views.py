from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
import os, joblib


def index(request):
    return render(request, 'index.html', {})


def AdminLogin(request):
    return render(request, 'AdminLogin.html', {})


def UserLogin(request):
    if request.session.get('user_id'):
        return redirect('UserHome')
    return render(request, 'UserLogin.html', {})


def UserRegister(request):
    from users.forms import UserRegistrationForm
    form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})


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


@never_cache
def AdminHome(request):
    if not request.session.get('admin'):
        return redirect('AdminLogin')
    from users.models import UserProfile, PredictionHistory
    from django.db import models as dm

    BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    best_name  = 'Not trained'
    model_path = os.path.join(BASE_DIR, 'models', 'best_model_name.pkl')
    if os.path.exists(model_path):
        try:
            best_name = joblib.load(model_path)
        except Exception:
            pass

    avg_price = PredictionHistory.objects.aggregate(a=dm.Avg('predicted_price'))['a'] or 0

    context = {
        'total_users':        UserProfile.objects.count(),
        'active_users':       UserProfile.objects.filter(is_active=True).count(),
        'models_trained':     4 if os.path.exists(os.path.join(BASE_DIR, 'models', 'best_model.pkl')) else 0,
        'best_model':         best_name,
        'total_predictions':  PredictionHistory.objects.count(),
        'avg_price':          round(avg_price, 0),
        'recent_users':       UserProfile.objects.order_by('-created_at')[:5],
        'recent_predictions': PredictionHistory.objects.order_by('-created_at')[:5],
    }
    return render(request, 'AdminHome.html', context)


@never_cache
def RegisterUsersView(request):
    if not request.session.get('admin'):
        return redirect('AdminLogin')
    from users.models import UserProfile
    users = UserProfile.objects.all().order_by('-created_at')
    return render(request, 'RegisterUsersView.html', {'users': users})


def ActivaUsers(request):
    if not request.session.get('admin'):
        return redirect('AdminLogin')
    from users.models import UserProfile
    user_id = request.GET.get('id')
    try:
        user = UserProfile.objects.get(id=user_id)
        user.is_active = True
        user.save()
    except UserProfile.DoesNotExist:
        pass

    return redirect('RegisterUsersView')


