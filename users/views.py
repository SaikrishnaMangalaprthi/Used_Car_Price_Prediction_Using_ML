from django.shortcuts import render, redirect
from django.http import HttpResponse
import time
from django.views.decorators.cache import never_cache
from sklearn.metrics import mean_absolute_error, r2_score
from .models import PredictionHistory, UserProfile

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
@never_cache
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
@never_cache
def prediction(request):
    if not is_logged_in(request): 
        return redirect('UserLogin')
    if request.method == 'POST':
        errors = []
        form_data = {
        'year':         request.POST.get('year', '').strip(),
        'km_driven':    request.POST.get('km_driven', '').strip(),
        'fuel':         request.POST.get('fuel', ''),
        'seller_type':  request.POST.get('seller_type', 'Individual'),
        'transmission': request.POST.get('transmission', ''),
        'owner':        request.POST.get('owner', ''),
        'brand':        request.POST.get('brand', ''),
        'mileage':      request.POST.get('mileage', '18'),
        'engine':       request.POST.get('engine', '1200'),
        'max_power':    request.POST.get('max_power', '80'),
        'seats':        request.POST.get('seats', '5'),
        }
 
    # Validate year
        try:
            year_val = int(form_data['year'])
            if year_val < 1990:
                errors.append('Year cannot be before 1990. Oldest data in dataset is from 1990.')
            elif year_val > 2025:
                errors.append('Year cannot be in the future. Maximum allowed year is 2025.')
        except ValueError:
            errors.append('Year must be a number (e.g. 2019). You entered: "' + form_data['year'] + '"')
 
    # Validate km driven
        try:
            km_val = int(form_data['km_driven'])
            if km_val < 500:
                errors.append('KM driven seems too low. Minimum is 500 km. Did you mean to enter more?')
            elif km_val > 500000:
                errors.append('KM driven exceeds 5,00,000. Maximum allowed is 5,00,000 km.')
        except ValueError:
            errors.append('KM driven must be a number (e.g. 45000). Do not include commas or letters.')
 
    # Validate optional numeric fields
        try:
            ml = float(form_data['mileage'])
            if ml < 5 or ml > 60:
              errors.append('Mileage should be between 5 and 60 kmpl. Entered: ' + form_data['mileage'])
        except ValueError:
            errors.append('Mileage must be a number (e.g. 23.0)')
 
        try:
            eng = float(form_data['engine'])
            if eng < 500 or eng > 6000:
                 errors.append('Engine CC should be between 500 and 6000. Entered: ' + form_data['engine'])
        except ValueError:
            errors.append('Engine CC must be a number (e.g. 1197)')
 
    # If model file not found, give a helpful message
        import os
        if not os.path.exists('models/best_model.pkl'):
            errors.append('⚠️ Model not trained yet. Please go to Train Model page first and click Start Training.')
 
        if errors:
            return render(request, 'prediction.html', {
            'errors': errors,
            'form_data': form_data  # Preserve filled values
        })


        vehicle_age = 2026 - int(form_data['year'])

        input_dict = {
            'vehicle_age': vehicle_age,
            'km_driven': int(form_data['km_driven']),
            'fuel_type': form_data['fuel'],
            'seller_type': form_data['seller_type'],
            'transmission_type': form_data['transmission'],
            'owner': form_data['owner'],
            'brand': form_data['brand'],
            'mileage': float(form_data['mileage']),
            'engine': float(form_data['engine']),
            'max_power': float(form_data['max_power']),
            'seats': int(form_data['seats'])
        }
        input_dict['year'] = form_data['year']
        input_dict['fuel'] = form_data['fuel']
        input_dict['transmission'] = form_data['transmission']
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        from ml_pipeline.predict import predict_price, get_similar_cars, get_price_tag
        result = predict_price(input_dict)

        warning = None

        similar = get_similar_cars(
            brand=input_dict['brand'],
            fuel=input_dict['fuel_type'],
            vehicle_age=input_dict['vehicle_age']       )         
        price_tag = get_price_tag(
            predicted_price=result['predicted'],
            brand=input_dict['brand'],
            fuel=input_dict['fuel_type']
                )
        from .models import PredictionHistory
        user = UserProfile.objects.get(id=request.session['user_id'])
        PredictionHistory.objects.create(
            user=user,

            brand=form_data['brand'],
            vehicle_age=vehicle_age,
            km_driven=form_data['km_driven'],
            fuel_type=form_data['fuel'],
            transmission_type=form_data['transmission'],

            predicted_price=result['predicted'],
            lower_bound=result['lower'],
            upper_bound=result['upper']
        )
        

        return render(request, 'prediction_result.html', {
                'result': result,
                'input': input_dict,
                'warning': warning,
                'similar': similar,
                'price_tag': price_tag,
            })
    return render(request, 'prediction.html')
# ── TO BE COMPLETED DAY 21 ───────────────────────────────────────────
@never_cache
def DatasetView(request):
    if not is_logged_in(request): return redirect('UserLogin')
    import pandas as pd
    df = pd.read_csv('dataset/cardekho_dataset.csv')
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
@never_cache
def prediction_history(request):
    if not is_logged_in(request): return redirect('UserLogin')
    from .models import UserProfile, PredictionHistory
    from django.db.models import Avg, Max, Min, Count
    user = UserProfile.objects.get(id=request.session['user_id'])
    history = PredictionHistory.objects.filter(user=user).order_by('-created_at')
    for h in history:
        h.display_year = 2026 - int(h.vehicle_age)
    stats = history.aggregate(
        total=Count('id'),
        avg_price=Avg('predicted_price'),
        max_price=Max('predicted_price'),
        min_price=Min('predicted_price')
    )
    return render(request, 'prediction_history.html', {
        'history': history,
        'user': user,
        'stats': stats
    })


def delete_prediction(request, pk):
    if not is_logged_in(request): return redirect('UserLogin')
    from .models import UserProfile, PredictionHistory
    user = UserProfile.objects.get(id=request.session['user_id'])
    try:
        record = PredictionHistory.objects.get(id=pk, user=user)
        record.delete()
    except PredictionHistory.DoesNotExist:
        pass  # Already deleted or not owned by this user
    return redirect('prediction_history')
@never_cache
def compare_cars(request):
    if not is_logged_in(request): return redirect('UserLogin')
    return render(request, 'compare.html', {})
@never_cache
def compare_result(request):
    if not is_logged_in(request): return redirect('UserLogin')
    if request.method != 'POST':
        return redirect('compare_cars')
 
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ml_pipeline.predict import predict_price
 
    # Car 1 inputs
    car1 = {
        'vehicle_age': 2026 - int(request.POST.get('year1')),
        'km_driven': int(request.POST.get('km1')),
        'fuel_type': request.POST.get('fuel1'),
        'seller_type': request.POST.get('seller1'),
        'transmission_type': request.POST.get('transmission1'),
        'owner': request.POST.get('owner1'),
        'brand': request.POST.get('brand1'),
        'mileage': float(request.POST.get('mileage1', 18)),
        'engine': float(request.POST.get('engine1', 1200)),
        'max_power': float(request.POST.get('power1', 80)),
        'seats': int(request.POST.get('seats1', 5))
    }
    # Car 2 inputs
    car2 = {
        'vehicle_age': 2026 - int(request.POST.get('year2')),
        'km_driven': int(request.POST.get('km2')),
        'fuel_type': request.POST.get('fuel2'),
        'seller_type': request.POST.get('seller2'),
        'transmission_type': request.POST.get('transmission2'),
        'owner': request.POST.get('owner2'),
        'brand': request.POST.get('brand2'),
        'mileage': float(request.POST.get('mileage2', 18)),
        'engine': float(request.POST.get('engine2', 1200)),
        'max_power': float(request.POST.get('power2', 80)),
        'seats': int(request.POST.get('seats2', 5))
    }
 
    r1 = predict_price(car1)
    r2 = predict_price(car2)
 
    # Determine which is better value
    winner = 'car1' if r1['predicted'] < r2['predicted'] else 'car2'
    savings = abs(r1['predicted'] - r2['predicted'])
 
    return render(request, 'compare_result.html', {
        'car1': car1, 'car2': car2,
        'r1': r1,     'r2': r2,
        'winner': winner,
        'savings': f'&#8377;{savings:,.0f}',
    })
