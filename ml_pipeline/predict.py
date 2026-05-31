import joblib, numpy as np, datetime
 
def predict_price(input_dict):
    """
    input_dict keys: year, km_driven, fuel, seller_type, transmission,
                     owner, brand, mileage, engine, max_power, seats
    Returns dict with predicted, lower, upper, formatted strings
    """
    model = joblib.load('models/best_model.pkl')
    scaler = joblib.load('models/scaler.pkl')
    label_encoders = joblib.load('models/label_encoders.pkl')
    feature_names = joblib.load('models/feature_names.pkl')
    print(input_dict)
    #current_year = datetime.datetime.now().year
    import datetime
    current_year = datetime.datetime.now().year
    vehicle_age = max(current_year - int(input_dict['year']), 1)
    mileage_per_year = int(input_dict['km_driven']) / vehicle_age
 
    processed = {}
    processed['km_driven'] = int(input_dict['km_driven'])
    processed['vehicle_age'] = vehicle_age
    processed['mileage_per_year'] = mileage_per_year
 
    # Encode categorical fields using saved label encoders
    # Map form field names → dataset column names
    field_map = {
        'fuel_type':         input_dict.get('fuel_type') or input_dict.get('fuel', 'Petrol'),
        'transmission_type': input_dict.get('transmission_type') or input_dict.get('transmission', 'Manual'),
        'seller_type':       input_dict.get('seller_type', 'Individual'),
        'brand':             input_dict.get('brand', ''),
        'car_model':         input_dict.get('car_model', ''),
    }

    for field, val in field_map.items():
        if field in label_encoders:
            le = label_encoders[field]
            val = str(val).strip()
            processed[field] = int(le.transform([val])[0]) if val in le.classes_ else 0

    defaults = {'mileage': 18.0, 'engine': 1200.0, 'max_power': 80.0, 'seats': 5.0}
    for k, default in defaults.items():
        if k in feature_names:
            processed[k] = float(input_dict.get(k, default) or default)
    import pandas as pd
    arr = pd.DataFrame([processed], columns=feature_names)
    arr_scaled = scaler.transform(arr)
    pred = float(model.predict(arr_scaled)[0])
 
    return {
        'predicted': round(pred, 0),
        'lower': round(pred * 0.90, 0),
        'upper': round(pred * 1.10, 0),
        'predicted_formatted': f'₹{pred:,.0f}',
        'lower_formatted': f'₹{pred*0.90:,.0f}',
        'upper_formatted': f'₹{pred*1.10:,.0f}'
    }
def get_similar_cars(brand, fuel, vehicle_age, car_model=None, sample_size=5):
    import pandas as pd

    try:
        df = pd.read_csv('dataset/cardekho_dataset.csv')
        # Brand + Model extraction
        if 'name' in df.columns:
            df['brand'] = df['name'].apply(
                lambda x: str(x).split()[0]
            )
            df['model'] = df['name'].apply(
                lambda x: ' '.join(str(x).split()[1:])
                if len(str(x).split()) > 1 else ''
                )
        elif 'Brand' in df.columns:
            df['brand'] = df['Brand']
        fuel_col = None
        for c in ['fuel', 'fuel_type', 'Fuel', 'Fuel_Type']:
            if c in df.columns:
                fuel_col = c
                break
        km_col = None
        for c in ['km_driven', 'kms_driven', 'Kms_Driven', 'kilometers']:
            if c in df.columns:
                km_col = c
                break
        price_col = None
        for c in ['selling_price', 'Selling_Price', 'price']:
            if c in df.columns:
                price_col = c
                break
        if 'vehicle_age' not in df.columns:
            return []
        if fuel_col is None or price_col is None:
            return []
        brand_mask = (
            df['brand']
            .astype(str)
            .str.lower()
            == brand.lower()
        )
        fuel_mask = (
            df[fuel_col]
            .astype(str)
            .str.lower()
            == fuel.lower()
        )
        age_mask = (
            abs(df['vehicle_age'] - vehicle_age) <= 3
        )
        similar = pd.DataFrame()
        if car_model and 'model' in df.columns:
            model_mask = (
                df['model']
                .astype(str)
                .str.lower()
                == car_model.lower()
            )
            similar = df[
                brand_mask &
                model_mask &
                fuel_mask &
                age_mask
            ]
            if len(similar) < 3:
                similar = df[
                    brand_mask &
                    model_mask &
                    fuel_mask
                ]
            if len(similar) < 3:
                similar = df[
                    brand_mask &
                    model_mask
                ]
   
        if len(similar) < 3:
            similar = df[
                brand_mask &
                fuel_mask &
                age_mask
            ]
     
        if len(similar) < 3:
            similar = df[
                brand_mask &
                fuel_mask
            ]
        
        if len(similar) < 3:
            similar = df[
                brand_mask
            ]
        similar = similar.dropna(subset=[price_col])
        if len(similar) == 0:
            return []

        duplicate_cols = []
        if 'name' in similar.columns:
            duplicate_cols.append('name')
        if 'year' in similar.columns:
            duplicate_cols.append('year')
        if duplicate_cols:
            similar = similar.drop_duplicates(
                subset=duplicate_cols
            )
        similar['age_diff'] = abs(
            similar['vehicle_age'] - vehicle_age
        )
        similar = similar.sort_values(
            by='age_diff'
        )
        sample = similar.head(sample_size)
        current_year = 2026
        results = []
        for _, row in sample.iterrows():
            # Calculate year
            year = (
                current_year - int(row['vehicle_age'])
                if pd.notna(row['vehicle_age'])
                else 'N/A'
            )
            results.append({
                'brand': row['brand'],
                'model': (
                    row['model']
                    if 'model' in row else 'N/A'
                ),
                'year': year,
                'km': (
                    f"{int(row[km_col]):,} km"
                    if km_col and pd.notna(row[km_col])
                    else 'N/A'
                ),
                'fuel': (
                    row[fuel_col]
                    if fuel_col else fuel
                ),
                'price': (
                    f"₹{int(row[price_col]):,}"
                    if pd.notna(row[price_col])
                    else 'N/A'
                )
            })

        return results

    except Exception as e:
        print("get_similar_cars ERROR:", e)
        return []
def get_price_tag(predicted_price, brand, fuel, vehicle_age=None, car_model=None):
    import pandas as pd
    try:
        df = pd.read_csv('dataset/cardekho_dataset.csv')

        if 'name' in df.columns:
            df['brand'] = df['name'].apply(
                lambda x: str(x).split()[0]
            )
            df['model'] = df['name'].apply(
                lambda x: ' '.join(str(x).split()[1:])
                if len(str(x).split()) > 1 else ''
                )
        elif 'Brand' in df.columns:
            df['brand'] = df['Brand']
        fuel_col = None
        for c in ['fuel', 'fuel_type', 'Fuel', 'Fuel_Type']:
            if c in df.columns:
                fuel_col = c
                break

        price_col = None
        for c in ['selling_price', 'Selling_Price', 'price']:
            if c in df.columns:
                price_col = c
                break

        has_age = 'vehicle_age' in df.columns
        if price_col is None:
            return {
                'tag': 'Fair Value',
                'color': '#F57C00',
                'icon': '⚖️',
                'note': 'Could not find price column in dataset.'
            }

        brand_mask = (
            df['brand']
            .astype(str)
            .str.lower()
            == brand.lower()
        )
        fuel_mask = (
            df[fuel_col]
            .astype(str)
            .str.lower()
            == fuel.lower()
        ) if fuel_col else True
        age_mask = (
            abs(df['vehicle_age'] - vehicle_age) <= 3
        ) if (
            has_age and vehicle_age is not None
        ) else True

        similar = pd.Series(dtype=float)

        if car_model and 'model' in df.columns:

            model_mask = (
                df['model']
                .astype(str)
                .str.lower()
                == car_model.lower()
            )
            similar = df[
                brand_mask &
                model_mask &
                fuel_mask &
                age_mask
            ][price_col].dropna()

            if len(similar) < 3:
                similar = df[
                    brand_mask &
                    model_mask &
                    fuel_mask
                ][price_col].dropna()
            if len(similar) < 3:
                similar = df[
                    brand_mask &
                    model_mask
                ][price_col].dropna()
        if len(similar) < 3:
            similar = df[
                brand_mask &
                fuel_mask &
                age_mask
            ][price_col].dropna()
        if len(similar) < 3:
            similar = df[
                brand_mask &
                fuel_mask
            ][price_col].dropna()
        if len(similar) < 3:
            similar = df[
                brand_mask
            ][price_col].dropna()
        if len(similar) < 3:
            return {
                'tag': 'Fair Value',
                'color': '#F57C00',
                'icon': '⚖️',
                'note': 'Not enough market data to compare.'
            }
        avg_price = similar.mean()
        pct_diff = (
            (predicted_price - avg_price)
            / avg_price
        ) * 100

        if pct_diff <= -15:
            return {
                'tag': 'Affordable',
                'color': '#2E7D32',
                'icon': '✅',
                'note':
                    f'Price is {abs(pct_diff):.0f}% below '
                    f'market average (₹{avg_price:,.0f}). '
                    f'Good deal!'
            }
        elif pct_diff >= 15:
            return {
                'tag': 'Expensive',
                'color': '#C62828',
                'icon': '⚠️',
                'note':
                    f'Price is {pct_diff:.0f}% above '
                    f'market average (₹{avg_price:,.0f}). '
                    f'Consider negotiating.'
            }
        else:
            return {
                'tag': 'Fair Value',
                'color': '#F57C00',
                'icon': '⚖️',
                'note':
                    f'Price is within ±15% of '
                    f'market average (₹{avg_price:,.0f}). '
                    f'Fair deal.'
            }
    except Exception as e:
        print("get_price_tag ERROR:", e)
        return {
            'tag': 'Fair Value',
            'color': '#F57C00',
            'icon': '⚖️',
            'note': 'Could not compute market comparison.'
        }