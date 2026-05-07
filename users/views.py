from django.http import HttpResponse
 
# Helper functions used by all views below
def is_logged_in(request):
    return request.session.get('user_id') is not None
 
def is_admin(request):
    return request.session.get('admin') is not None
 
# ── TO BE COMPLETED DAY 8 ────────────────────────────────────────────
def UserRegisterActions(request):
    return HttpResponse('Registration coming Day 8')
 
# ── TO BE COMPLETED DAY 9 ────────────────────────────────────────────
def UserLoginCheck(request):
    return HttpResponse('Login check coming Day 9')
 
def UserHome(request):
    if not is_logged_in(request): return redirect('UserLogin')
    return HttpResponse('User Home coming Day 9')
 
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
    return HttpResponse('Prediction coming Day 19')
 
# ── TO BE COMPLETED DAY 21 ───────────────────────────────────────────
def DatasetView(request):
    if not is_logged_in(request): return redirect('UserLogin')
    return HttpResponse('Dataset view coming Day 21')
 
# ── TO BE COMPLETED DAY 22 ───────────────────────────────────────────
def prediction_history(request):
    if not is_logged_in(request): return redirect('UserLogin')
    return HttpResponse('History coming Day 22')
