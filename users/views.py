import os
import datetime
import pandas as pd
from pathlib import Path
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator
from .models import PredictionHistory, UserProfile

BASE_DIR     = Path(__file__).resolve().parent.parent
MODELS_DIR   = BASE_DIR / 'models'
DATASET_PATH = BASE_DIR / 'dataset' / 'cardekho_dataset.csv'
STATIC_IMAGES_DIR = BASE_DIR / 'static' / 'images'

# ── Load dataset once at startup ──────────────────────────────────────
_df = pd.read_csv(DATASET_PATH)
KNOWN_BRANDS = set(_df['brand'].dropna().unique())
KNOWN_MODELS = set(_df['model'].dropna().unique())
brand_model_map = (
    _df.groupby('brand')['model']
       .apply(lambda x: sorted(x.dropna().unique().tolist()))
       .to_dict()
)

# ── Session helpers ───────────────────────────────────────────────────
def is_logged_in(request):
    return request.session.get('user_id') is not None

def is_admin(request):
    return request.session.get('admin') is not None


# ── Auth views ────────────────────────────────────────────────────────
def UserRegisterActions(request):
    from .forms import UserRegistrationForm
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            name     = form.cleaned_data['name']
            email    = form.cleaned_data['email']
            password = form.cleaned_data['password']
            if UserProfile.objects.filter(email=email).exists():
                return render(request, 'UserRegistrations.html', {
                    'form': form,
                    'error': 'This email is already registered. Please login.'
                })
            UserProfile.objects.create(name=name, email=email, password=password, is_active=True)
            return render(request, 'RegistrationSuccess.html', {})
        return render(request, 'UserRegistrations.html', {'form': form})
    return redirect('UserRegister')


def UserLoginCheck(request):
    if request.method == 'POST':
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        try:
            user = UserProfile.objects.get(email=email, password=password)
            if user.is_active:
                request.session['user_id']   = user.id
                request.session['user_name'] = user.name
                return redirect('UserHome')
            else:
                return render(request, 'UserLogin.html', {
                    'error': 'Account not activated. Please contact the admin.'
                })
        except UserProfile.DoesNotExist:
            return render(request, 'UserLogin.html', {
                'error': 'Invalid email or password. Please try again.'
            })
    return redirect('UserLogin')


@never_cache
def UserHome(request):
    if not is_logged_in(request):
        return redirect('UserLogin')
    user_id = request.session['user_id']
    total   = PredictionHistory.objects.filter(user_id=user_id).count()
    return render(request, 'UserHome.html', {'total_predictions': total})


@never_cache
def logout_user(request):
    request.session.flush()
    return redirect('index')


# ── Training view ─────────────────────────────────────────────────────
def training(request):
    if not is_logged_in(request) and not is_admin(request):
        return redirect('UserLogin')

    if request.method == 'POST':
        import sys, numpy as np
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from ml_pipeline.preprocess import preprocess_data
        from sklearn.model_selection import train_test_split
        from sklearn.linear_model import LinearRegression, Ridge, Lasso
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        import joblib

        STATIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        MODELS_DIR.mkdir(parents=True, exist_ok=True)

        X, y, feature_names = preprocess_data()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        models = {
            'Linear Regression':  LinearRegression(),
            'Ridge Regression':   Ridge(alpha=1.0),
            'Lasso Regression':   Lasso(alpha=1.0),
            'Random Forest':      RandomForestRegressor(n_estimators=100, random_state=42),
            'Gradient Boosting':  GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42),
        }

        results, trained = {}, {}
        for nm, md in models.items():
            md.fit(X_train, y_train)
            yp = md.predict(X_test)
            results[nm] = {
                'MAE':  round(mean_absolute_error(y_test, yp), 0),
                'RMSE': round(np.sqrt(mean_squared_error(y_test, yp)), 0),
                'R2':   round(r2_score(y_test, yp), 4),
            }
            trained[nm] = md

        best = max(results, key=lambda x: results[x]['R2'])

        joblib.dump(trained[best],  str(MODELS_DIR / 'best_model.pkl'))
        joblib.dump(best,           str(MODELS_DIR / 'best_model_name.pkl'))
        joblib.dump(results,        str(MODELS_DIR / 'training_results.pkl'))
        joblib.dump(feature_names,  str(MODELS_DIR / 'feature_names.pkl'))

        # Clear cached models so next prediction uses new files
        try:
            from ml_pipeline.predict import _cache
            _cache.clear()
        except Exception:
            pass

        # R2 + MAE chart
        names = list(results.keys())
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        colors = ['#2563EB', '#166534', '#D97706', '#991B1B', '#7C3AED']
        ax1.bar(names, [results[m]['R2']  for m in names], color=colors)
        ax1.set_title('R² Score (higher = better)')
        ax1.set_ylim(0, 1)
        ax2.bar(names, [results[m]['MAE'] for m in names], color=colors)
        ax2.set_title('MAE ₹ (lower = better)')
        plt.xticks(rotation=20)
        plt.tight_layout()
        plt.savefig(str(STATIC_IMAGES_DIR / 'model_comparison.png'), bbox_inches='tight')
        plt.close()

        # Feature importance
        if hasattr(trained[best], 'feature_importances_'):
            imp = trained[best].feature_importances_
            idx = np.argsort(imp)[::-1]
            plt.figure(figsize=(9, 5))
            plt.bar(range(len(imp)), imp[idx], color='#2563EB')
            plt.xticks(range(len(imp)), [feature_names[i] for i in idx], rotation=40, ha='right')
            plt.title('Feature Importance')
            plt.tight_layout()
            plt.savefig(str(STATIC_IMAGES_DIR / 'feature_importance.png'), bbox_inches='tight')
            plt.close()

        # Actual vs Predicted
        yp_best = trained[best].predict(X_test)
        plt.figure(figsize=(7, 7))
        plt.scatter(y_test, yp_best, alpha=0.35, color='#2563EB')
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        plt.xlabel('Actual')
        plt.ylabel('Predicted')
        plt.title('Actual vs Predicted')
        plt.tight_layout()
        plt.savefig(str(STATIC_IMAGES_DIR / 'actual_vs_predicted.png'), bbox_inches='tight')
        plt.close()

        return render(request, 'training.html', {
            'results':    results,
            'best_model': best,
            'best_r2':    results[best]['R2'],
            'trained':    True,
        })

    return render(request, 'training.html', {
        'results': {}, 'best_model': None, 'best_r2': None, 'trained': False
    })


# ── Prediction view ───────────────────────────────────────────────────
@never_cache
def prediction(request):
    if not is_logged_in(request):
        return redirect('UserLogin')

    ctx = {
        'vehicle_ages':   list(range(1, 21)),
        'mileage_opts':   [round(x * 0.5, 1) for x in range(10, 61)],
        'engine_opts':    [800, 1000, 1100, 1197, 1200, 1400, 1500, 1600, 1800, 2000, 2200, 2400, 2500, 3000],
        'power_opts':     [40, 50, 60, 70, 80, 82, 90, 100, 110, 120, 130, 150, 180, 200],
        'brand_model_map': brand_model_map,
    }

    if request.method == 'POST':
        form_data = {
            'year':         request.POST.get('year', '').strip(),
            'car_model':    request.POST.get('car_model', ''),
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

        errors = []

        # Validate year
        try:
            year_val = int(form_data['year'])
            if year_val < 1990:
                errors.append('Year cannot be before 1990.')
            elif year_val > datetime.datetime.now().year:
                errors.append(f'Year cannot be in the future. Max allowed: {datetime.datetime.now().year}.')
        except ValueError:
            errors.append('Year must be a number (e.g. 2019).')

        # Validate km driven
        try:
            km_val = int(form_data['km_driven'])
            if km_val < 500:
                errors.append('KM driven seems too low. Minimum is 500 km.')
            elif km_val > 500000:
                errors.append('KM driven exceeds 5,00,000. Maximum allowed is 5,00,000 km.')
        except ValueError:
            errors.append('KM driven must be a number (e.g. 45000). Do not include commas or letters.')

        # Validate mileage
        try:
            ml = float(form_data['mileage'])
            if ml < 5 or ml > 60:
                errors.append(f'Mileage should be between 5 and 60 kmpl. Entered: {form_data["mileage"]}')
        except ValueError:
            errors.append('Mileage must be a number (e.g. 23.0)')

        # Validate engine
        try:
            eng = float(form_data['engine'])
            if eng < 500 or eng > 6000:
                errors.append(f'Engine CC should be between 500 and 6000. Entered: {form_data["engine"]}')
        except ValueError:
            errors.append('Engine CC must be a number (e.g. 1197)')

        # Check model file
        if not (MODELS_DIR / 'best_model.pkl').exists():
            errors.append('⚠️ Model not trained yet. Please go to Train Model page first and click Start Training.')

        if errors:
            return render(request, 'prediction.html', {**ctx, 'errors': errors, 'form_data': form_data})

        vehicle_age = datetime.datetime.now().year - int(form_data['year'])

        input_dict = {
            'year':              form_data['year'],
            'vehicle_age':       vehicle_age,
            'km_driven':         int(form_data['km_driven']),
            'fuel_type':         form_data['fuel'],
            'fuel':              form_data['fuel'],
            'seller_type':       form_data['seller_type'],
            'transmission_type': form_data['transmission'],
            'transmission':      form_data['transmission'],
            'owner':             form_data['owner'],
            'brand':             form_data['brand'],
            'car_model':         form_data['car_model'],
            'mileage':           float(form_data['mileage']),
            'engine':            float(form_data['engine']),
            'max_power':         float(form_data['max_power']),
            'seats':             int(form_data['seats']),
        }

        from ml_pipeline.predict import predict_price, get_similar_cars, get_price_tag
        result    = predict_price(input_dict)
        similar   = get_similar_cars(brand=input_dict['brand'], fuel=input_dict['fuel_type'],
                                     vehicle_age=input_dict['vehicle_age'], car_model=input_dict['car_model'])
        price_tag = get_price_tag(predicted_price=result['predicted'], brand=input_dict['brand'],
                                   fuel=input_dict['fuel_type'], vehicle_age=input_dict['vehicle_age'],
                                   car_model=input_dict['car_model'])

        user = UserProfile.objects.get(id=request.session['user_id'])
        PredictionHistory.objects.create(
            user=user,
            brand=form_data['brand'],
            car_model=input_dict['car_model'],
            vehicle_age=vehicle_age,
            km_driven=form_data['km_driven'],
            fuel_type=form_data['fuel'],
            transmission_type=form_data['transmission'],
            predicted_price=result['predicted'],
            lower_bound=result['lower'],
            upper_bound=result['upper'],
        )

        return render(request, 'prediction_result.html', {
            'result':    result,
            'input':     input_dict,
            'warning':   None,
            'similar':   similar,
            'price_tag': price_tag,
        })

    return render(request, 'prediction.html', ctx)


# ── Dataset view ──────────────────────────────────────────────────────
@never_cache
def DatasetView(request):
    if not is_logged_in(request):
        return redirect('UserLogin')
    df = pd.read_csv(str(DATASET_PATH))
    context = {
        'columns':    df.columns.tolist(),
        'rows':       df.head(100).values.tolist(),
        'total_rows': len(df),
        'total_cols': len(df.columns),
        'price_min':  f"₹{df['selling_price'].min():,.0f}" if 'selling_price' in df.columns else 'N/A',
        'price_max':  f"₹{df['selling_price'].max():,.0f}" if 'selling_price' in df.columns else 'N/A',
    }
    return render(request, 'DatasetView.html', context)


# ── Prediction history ────────────────────────────────────────────────
@never_cache
def prediction_history(request):
    if not is_logged_in(request):
        return redirect('UserLogin')

    from django.db.models import Avg, Max, Min, Count

    # Admins see all predictions; users see only their own
    if is_admin(request):
        history = PredictionHistory.objects.all().order_by('-created_at')
        user    = None
    else:
        user    = UserProfile.objects.get(id=request.session['user_id'])
        history = PredictionHistory.objects.filter(user=user).order_by('-created_at')

    current_year = datetime.datetime.now().year
    for h in history:
        h.display_year = current_year - int(h.vehicle_age)

    paginator = Paginator(history, 5)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    stats = history.aggregate(
        total=Count('id'),
        avg_price=Avg('predicted_price'),
        max_price=Max('predicted_price'),
        min_price=Min('predicted_price'),
    )

    return render(request, 'prediction_history.html', {
        'history':  history,
        'user':     user,
        'page_obj': page_obj,
        'stats':    stats,
    })


def delete_prediction(request, pk):
    if not is_logged_in(request):
        return redirect('UserLogin')
    user = UserProfile.objects.get(id=request.session['user_id'])
    try:
        PredictionHistory.objects.get(id=pk, user=user).delete()
    except PredictionHistory.DoesNotExist:
        pass
    return redirect('prediction_history')


# ── Compare views ─────────────────────────────────────────────────────
@never_cache
def compare_cars(request):
    if not is_logged_in(request):
        return redirect('UserLogin')
    return render(request, 'compare.html', {
        'seat_options':   [2, 4, 5, 6, 7, 8],
        'brand_model_map': brand_model_map,
    })


@never_cache
def compare_result(request):
    if not is_logged_in(request):
        return redirect('UserLogin')
    if request.method != 'POST':
        return redirect('compare_cars')

    from ml_pipeline.predict import predict_price

    current_year = datetime.datetime.now().year

    def build_car(n):
        year = int(request.POST.get(f'year{n}'))
        return {
            'year':         year,
            'vehicle_age':  current_year - year,
            'km_driven':    int(request.POST.get(f'km{n}')),
            'fuel_type':    request.POST.get(f'fuel{n}'),
            'fuel':         request.POST.get(f'fuel{n}'),
            'seller_type':  request.POST.get(f'seller{n}'),
            'transmission_type': request.POST.get(f'transmission{n}'),
            'transmission': request.POST.get(f'transmission{n}'),
            'owner':        request.POST.get(f'owner{n}'),
            'brand':        request.POST.get(f'brand{n}'),
            'car_model':    request.POST.get(f'car_model{n}'),
            'mileage':      float(request.POST.get(f'mileage{n}', 18)),
            'engine':       float(request.POST.get(f'engine{n}', 1200)),
            'max_power':    float(request.POST.get(f'power{n}', 80)),
            'seats':        int(request.POST.get(f'seats{n}', 5)),
        }

    car1, car2 = build_car(1), build_car(2)
    r1, r2     = predict_price(car1), predict_price(car2)
    winner     = 'car1' if r1['predicted'] < r2['predicted'] else 'car2'
    savings    = abs(r1['predicted'] - r2['predicted'])

    return render(request, 'compare_result.html', {
        'car1': car1, 'car2': car2,
        'r1': r1,     'r2': r2,
        'winner':  winner,
        'savings': f'₹{savings:,.0f}',
    })


# ── History detail ────────────────────────────────────────────────────
def history_detail(request, pk):
    if not is_logged_in(request):
        return redirect('UserLogin')
    user = UserProfile.objects.get(id=request.session['user_id'])
    try:
        pred = PredictionHistory.objects.get(id=pk, user=user)
    except PredictionHistory.DoesNotExist:
        return redirect('prediction_history')

    current_year = datetime.datetime.now().year
    details = [
        ('Brand',         pred.brand),
        ('Car Model',     pred.car_model),
        ('Year',          f'{current_year - pred.vehicle_age} ({pred.vehicle_age} yrs old)'),
        ('Km Driven',     f'{int(pred.km_driven):,} km'),
        ('Fuel Type',     pred.fuel_type),
        ('Transmission',  pred.transmission_type),
        ('Predicted Price', f'₹{pred.predicted_price:,.0f}'),
        ('Price Range',   f'₹{pred.lower_bound:,.0f} – ₹{pred.upper_bound:,.0f}'),
    ]
    return render(request, 'history_detail.html', {'pred': pred, 'details': details})


# ── About & How it works ──────────────────────────────────────────────
def about(request):
    import joblib
    best_r2 = None
    results_path = MODELS_DIR / 'training_results.pkl'
    if results_path.exists():
        try:
            res       = joblib.load(str(results_path))
            best_name = max(res, key=lambda x: res[x]['R2'])
            best_r2   = res[best_name]['R2']
        except Exception:
            pass
    return render(request, 'about.html', {'best_r2': best_r2})


def how_it_works(request):
    if not is_logged_in(request):
        return redirect('UserLogin')
    return render(request, 'how_it_works.html')
