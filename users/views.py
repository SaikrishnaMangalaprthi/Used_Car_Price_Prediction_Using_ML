from django.shortcuts import render, redirect
from django.http import HttpResponse
import time

from sklearn.metrics import mean_absolute_error, r2_score


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
    if request.method == 'POST':
        import sys, os, numpy as np
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from ml_pipeline.preprocess import preprocess_data
        from sklearn.model_selection import train_test_split
        from sklearn.linear_model import LinearRegression, Ridge, Lasso
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        import joblib

        X, y, feature_names = preprocess_data()
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42)

        models = {
            'Linear Regression':  LinearRegression(),
            'Ridge Regression':   Ridge(alpha=1.0),
            'Lasso Regression':   Lasso(alpha=1.0),
            'Random Forest':      RandomForestRegressor(n_estimators=100, random_state=42),
            'Gradient Boosting':  GradientBoostingRegressor(
                                      n_estimators=200, learning_rate=0.1,
                                      max_depth=5, random_state=42),
        }

        results = {}
        trained = {}

        # ── Loop trains ALL models first, THEN saves ──────────────────
        for name, model in models.items():
            print(f"Training {name}...", flush=True)
            model.fit(X_train, y_train)
            yp = model.predict(X_test)
            results[name] = {
                'MAE':  round(mean_absolute_error(y_test, yp), 0),
                'RMSE': round(np.sqrt(mean_squared_error(y_test, yp)), 0),
                'R2':   round(r2_score(y_test, yp), 4)
            }
            trained[name] = model
            print(f"  Done — R2={results[name]['R2']}", flush=True)

        # ── Everything below runs AFTER all models finish ─────────────
        best_name = max(results, key=lambda x: results[x]['R2'])
        joblib.dump(trained[best_name], 'models/best_model.pkl')
        joblib.dump(results, 'models/training_results.pkl')
        joblib.dump(feature_names, 'models/feature_names.pkl')

        # Model comparison chart
        names  = list(results.keys())
        colors = ['#3498db','#e74c3c','#2ecc71','#9b59b6','#f39c12']
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        ax1.bar(names, [results[m]['R2'] for m in names], color=colors)
        ax1.set_title('R² Score — Higher is Better')
        ax1.set_ylim(0, 1)
        ax1.tick_params(axis='x', rotation=30)
        ax2.bar(names, [results[m]['MAE']/100000 for m in names], color=colors)
        ax2.set_title('MAE (Lakhs) — Lower is Better')
        ax2.tick_params(axis='x', rotation=30)
        plt.tight_layout()
        plt.savefig('static/images/model_comparison.png', dpi=100)
        plt.close()

        return render(request, 'training.html', {
            'results': results,
            'best_model': best_name,
            'trained': True
        })

    return render(request, 'training.html', {'trained': False})
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
    import pandas as pd
    df = pd.read_csv('dataset/car_data.csv')
    context = {
        'columns': df.columns.tolist(),
        'rows': df.head(100).values.tolist(),
        'total_rows': len(df),
        'total_cols': len(df.columns),
        'price_min': f"Rs.{df['selling_price'].min():,.0f}" if 'selling_price' in df.columns else 'N/A',
        'price_max': f"Rs.{df['selling_price'].max():,.0f}" if 'selling_price' in df.columns else 'N/A',
    }
    return render(request, 'DatasetView.html', context)

# ── TO BE COMPLETED DAY 22 ───────────────────────────────────────────
def prediction_history(request):
    if not is_logged_in(request): return redirect('UserLogin')
    from .models import UserProfile, PredictionHistory
    user = UserProfile.objects.get(id=request.session['user_id'])
    history = PredictionHistory.objects.filter(user=user).order_by('-created_at')
    return render(request, 'prediction_history.html', {'history': history, 'user': user})

