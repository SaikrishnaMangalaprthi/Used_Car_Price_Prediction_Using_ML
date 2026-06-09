import joblib
import numpy as np
import datetime
import os
import pandas as pd

# Absolute base path — works on local and Render
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATASET_PATH = os.path.join(BASE_DIR, 'dataset', 'cardekho_dataset.csv')

# ── Cache models in memory (loaded once per process, not per request) ──
_cache = {}

def _load(name):
    if name not in _cache:
        _cache[name] = joblib.load(os.path.join(MODELS_DIR, name))
    return _cache[name]

import traceback
def predict_price(input_dict):
    model          = _load('best_model.pkl')
    scaler         = _load('scaler.pkl')
    label_encoders = _load('label_encoders.pkl')
    feature_names  = _load('feature_names.pkl')

    current_year = datetime.datetime.now().year
    vehicle_age  = max(current_year - int(input_dict['year']), 1)
    mileage_per_year = int(input_dict['km_driven']) / vehicle_age

    processed = {
        'km_driven':        int(input_dict['km_driven']),
        'vehicle_age':      vehicle_age,
        'mileage_per_year': mileage_per_year,
    }

    field_map = {
        'fuel_type':         input_dict.get('fuel_type') or input_dict.get('fuel', 'Petrol'),
        'transmission_type': input_dict.get('transmission_type') or input_dict.get('transmission', 'Manual'),
        'seller_type':       input_dict.get('seller_type', 'Individual'),
        'brand':             input_dict.get('brand', ''),
        'car_model':         input_dict.get('car_model', ''),
    }

    for field, val in field_map.items():
        if field in label_encoders:
            le  = label_encoders[field]
            val = str(val).strip()
            processed[field] = int(le.transform([val])[0]) if val in le.classes_ else 0

    defaults = {'mileage': 18.0, 'engine': 1200.0, 'max_power': 80.0, 'seats': 5.0}
    for k, default in defaults.items():
        if k in feature_names:
            processed[k] = float(input_dict.get(k, default) or default)

    arr        = pd.DataFrame([processed], columns=feature_names)
    try:
        arr_scaled = scaler.transform(arr)
        print("Scaler worked")

        pred = float(model.predict(arr_scaled)[0])
        print("Prediction worked:", pred)

    except Exception as e:
        print("ERROR OCCURRED:", str(e))
        traceback.print_exc()
        raise

    return {
        'predicted':           round(pred, 0),
        'lower':               round(pred * 0.90, 0),
        'upper':               round(pred * 1.10, 0),
        'predicted_formatted': f'₹{pred:,.0f}',
        'lower_formatted':     f'₹{pred*0.90:,.0f}',
        'upper_formatted':     f'₹{pred*1.10:,.0f}',
    }


def get_similar_cars(brand, fuel, vehicle_age, car_model=None, sample_size=5):
    try:
        df = pd.read_csv(DATASET_PATH)

        fuel_col  = next((c for c in ['fuel_type', 'fuel', 'Fuel', 'Fuel_Type'] if c in df.columns), None)
        km_col    = next((c for c in ['km_driven', 'kms_driven', 'Kms_Driven'] if c in df.columns), None)
        price_col = next((c for c in ['selling_price', 'Selling_Price', 'price'] if c in df.columns), None)

        if 'vehicle_age' not in df.columns or fuel_col is None or price_col is None:
            return []

        brand_mask = df['brand'].astype(str).str.lower() == brand.lower()
        fuel_mask  = df[fuel_col].astype(str).str.lower() == fuel.lower()
        age_mask   = abs(df['vehicle_age'] - vehicle_age) <= 3

        similar = pd.DataFrame()

        if car_model and 'model' in df.columns:
            model_mask = df['model'].astype(str).str.lower() == car_model.lower()
            for mask in [
                brand_mask & model_mask & fuel_mask & age_mask,
                brand_mask & model_mask & fuel_mask,
                brand_mask & model_mask,
            ]:
                similar = df[mask]
                if len(similar) >= 3:
                    break

        if len(similar) < 3:
            for mask in [
                brand_mask & fuel_mask & age_mask,
                brand_mask & fuel_mask,
                brand_mask,
            ]:
                similar = df[mask]
                if len(similar) >= 3:
                    break

        similar = similar.dropna(subset=[price_col])
        if len(similar) == 0:
            return []

        dedup_cols = [c for c in ['model', 'year', 'vehicle_age'] if c in similar.columns]
        if dedup_cols:
            similar = similar.drop_duplicates(subset=dedup_cols)

        similar = similar.copy()
        similar['age_diff'] = abs(similar['vehicle_age'] - vehicle_age)
        similar = similar.sort_values('age_diff').head(sample_size)

        current_year = datetime.datetime.now().year
        results = []
        for _, row in similar.iterrows():
            year = (current_year - int(row['vehicle_age'])) if pd.notna(row['vehicle_age']) else 'N/A'
            results.append({
                'brand': row.get('brand', brand),
                'model': row.get('model', 'N/A'),
                'year':  year,
                'km':    f"{int(row[km_col]):,} km" if km_col and pd.notna(row[km_col]) else 'N/A',
                'fuel':  row[fuel_col] if fuel_col else fuel,
                'price': f"₹{int(row[price_col]):,}" if pd.notna(row[price_col]) else 'N/A',
            })
        return results

    except Exception as e:
        print("get_similar_cars ERROR:", e)
        return []


def get_price_tag(predicted_price, brand, fuel, vehicle_age=None, car_model=None):
    try:
        df = pd.read_csv(DATASET_PATH)

        fuel_col  = next((c for c in ['fuel_type', 'fuel', 'Fuel', 'Fuel_Type'] if c in df.columns), None)
        price_col = next((c for c in ['selling_price', 'Selling_Price', 'price'] if c in df.columns), None)

        if price_col is None:
            return {'tag': 'Fair Value', 'color': '#F57C00', 'icon': '⚖️', 'note': 'Could not find price column.'}

        brand_mask = df['brand'].astype(str).str.lower() == brand.lower()
        fuel_mask  = df[fuel_col].astype(str).str.lower() == fuel.lower() if fuel_col else True
        age_mask   = (abs(df['vehicle_age'] - vehicle_age) <= 3) if (vehicle_age is not None and 'vehicle_age' in df.columns) else True

        similar = pd.Series(dtype=float)

        if car_model and 'model' in df.columns:
            model_mask = df['model'].astype(str).str.lower() == car_model.lower()
            for mask in [
                brand_mask & model_mask & fuel_mask & age_mask,
                brand_mask & model_mask & fuel_mask,
                brand_mask & model_mask,
            ]:
                similar = df[mask][price_col].dropna()
                if len(similar) >= 3:
                    break

        if len(similar) < 3:
            for mask in [
                brand_mask & fuel_mask & age_mask,
                brand_mask & fuel_mask,
                brand_mask,
            ]:
                similar = df[mask][price_col].dropna()
                if len(similar) >= 3:
                    break

        if len(similar) < 3:
            return {'tag': 'Fair Value', 'color': '#F57C00', 'icon': '⚖️', 'note': 'Not enough market data to compare.'}

        avg_price = similar.mean()
        pct_diff  = ((predicted_price - avg_price) / avg_price) * 100

        if pct_diff <= -15:
            return {'tag': 'Affordable', 'color': '#2E7D32', 'icon': '✅',
                    'note': f'Price is {abs(pct_diff):.0f}% below market average (₹{avg_price:,.0f}). Good deal!'}
        elif pct_diff >= 15:
            return {'tag': 'Expensive', 'color': '#C62828', 'icon': '⚠️',
                    'note': f'Price is {pct_diff:.0f}% above market average (₹{avg_price:,.0f}). Consider negotiating.'}
        else:
            return {'tag': 'Fair Value', 'color': '#F57C00', 'icon': '⚖️',
                    'note': f'Price is within ±15% of market average (₹{avg_price:,.0f}). Fair deal.'}

    except Exception as e:
        print("get_price_tag ERROR:", e)
        return {'tag': 'Fair Value', 'color': '#F57C00', 'icon': '⚖️', 'note': 'Could not compute market comparison.'}
