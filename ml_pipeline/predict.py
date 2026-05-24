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
    vehicle_age = int(input_dict['vehicle_age'])
    mileage_per_year = int(input_dict['km_driven']) / vehicle_age
 
    processed = {}
    processed['km_driven'] = int(input_dict['km_driven'])
    processed['vehicle_age'] = vehicle_age
    processed['mileage_per_year'] = mileage_per_year
 
    # Encode categorical fields using saved label encoders
    for field in ['fuel_type', 'seller_type', 'transmission_type', 'owner', 'brand']:
        if field in label_encoders and field in input_dict:
            le = label_encoders[field]
            val = str(input_dict[field])
            processed[field] = int(le.transform([val])[0]) if val in le.classes_ else 0
 
    # Optional numeric fields with defaults
    defaults = {'mileage': 18.0, 'engine': 1200.0, 'max_power': 80.0, 'seats': 5.0}
    for k, default in defaults.items():
        if k in feature_names:
            processed[k] = float(input_dict.get(k, default) or default)
 
    # Build array in exact order features were trained
    arr = np.array([processed.get(f, 0) for f in feature_names]).reshape(1, -1)
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
def get_similar_cars(brand, fuel,vehicle_age,sample_size=5):
    import pandas as pd
    try:
        df = pd.read_csv('dataset/cardekho_dataset.csv')
        
        # Auto-detect brand column
        if 'brand' not in df.columns and 'name' in df.columns:
            df['brand'] = df['name'].apply(lambda x: str(x).split()[0])
        elif 'Brand' in df.columns:
            df['brand'] = df['Brand']
            
        # Auto-detect fuel column (handle fuel / fuel_type / Fuel)
        fuel_col = None
        for c in ['fuel', 'fuel_type', 'Fuel', 'Fuel_Type']:
            if c in df.columns:
                fuel_col = c
                break
        
        # Auto-detect year column
        current_year = 2026
        
        # Auto-detect km column
        km_col = None
        for c in ['km_driven', 'kms_driven', 'Kms_Driven', 'kilometers']:
            if c in df.columns:
                km_col = c
                break

        # Auto-detect price column
        price_col = None
        for c in ['selling_price', 'Selling_Price', 'price']:
            if c in df.columns:
                price_col = c
                break

        if price_col is None:
            return []

        # Filter by brand (partial match for safety)
        mask = (
            df['brand'].str.lower().str.contains(brand.lower(), na=False)
        ) & (
            df[fuel_col].str.lower().str.contains(fuel.lower(), na=False)
        ) & (
            abs(df['vehicle_age'] - vehicle_age) <= 3
        )
        
        # Also filter by fuel if column found
        if fuel_col:
            fuel_mask = df[fuel_col].str.lower().str.contains(fuel.lower(), na=False)
            combined = df[mask & fuel_mask]
            if len(combined) < 3:
                combined = df[mask]  # fallback to brand only
        else:
            combined = df[mask]

        combined = combined.dropna(subset=[price_col])
        if len(combined) == 0:
            return []

        sample = combined.sample(min(sample_size, len(combined)), random_state=42)

        results = []
        for _, row in sample.iterrows():
            results.append({
                'brand':  brand,
                'year':   current_year - int(row['vehicle_age']) if 'vehicle_age' in row else 'N/A',
                'km':     f"{int(row[km_col]):,} km" if km_col else 'N/A',
                'fuel':   row[fuel_col] if fuel_col else fuel,
                'price':  f"\u20b9{int(row[price_col]):,}",
            })
        return results
    except Exception as e:
        print("get_similar_cars error:", e)
        return []


def get_price_tag(predicted_price, brand, fuel):
    import pandas as pd
    try:
        df = pd.read_csv('dataset/cardekho_dataset.csv')

        if 'brand' not in df.columns and 'name' in df.columns:
            df['brand'] = df['name'].apply(lambda x: str(x).split()[0])
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

        if price_col is None:
            return {'tag': 'Fair', 'color': '#F57C00', 'icon': '⚖️',
                    'note': 'Could not find price column in dataset.'}

        mask = df['brand'].str.lower().str.contains(brand.lower(), na=False)
        if fuel_col:
            fuel_mask = df[fuel_col].str.lower().str.contains(fuel.lower(), na=False)
            similar = df[mask & fuel_mask][price_col].dropna()
            if len(similar) < 3:
                similar = df[mask][price_col].dropna()
        else:
            similar = df[mask][price_col].dropna()

        if len(similar) < 3:
            return {'tag': 'Fair', 'color': '#F57C00', 'icon': '⚖️',
                    'note': 'Not enough data to compare market average.'}

        avg = similar.mean()
        pct_diff = ((predicted_price - avg) / avg) * 100

        if pct_diff <= -15:
            return {'tag': 'Cheap', 'color': '#2E7D32', 'icon': '✅',
                    'note': f'Price is {abs(pct_diff):.0f}% below market average (\u20b9{avg:,.0f}). Good deal!'}
        elif pct_diff >= 15:
            return {'tag': 'Expensive', 'color': '#C62828', 'icon': '⚠️',
                    'note': f'Price is {pct_diff:.0f}% above market average (\u20b9{avg:,.0f}). Consider negotiating.'}
        else:
            return {'tag': 'Fair', 'color': '#F57C00', 'icon': '⚖️',
                    'note': f'Price is within ±15% of market average (\u20b9{avg:,.0f}). Fair deal.'}
    except Exception as e:
        print("get_price_tag error:", e)
        return {'tag': 'Fair', 'color': '#F57C00', 'icon': '⚖️',
                'note': 'Could not compute market comparison.'}