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
 
    current_year = datetime.datetime.now().year
    vehicle_age = max(current_year - int(input_dict['year']), 1)
    mileage_per_year = int(input_dict['km_driven']) / vehicle_age
 
    processed = {}
    processed['km_driven'] = int(input_dict['km_driven'])
    processed['vehicle_age'] = vehicle_age
    processed['mileage_per_year'] = mileage_per_year
 
    # Encode categorical fields using saved label encoders
    for field in ['fuel', 'seller_type', 'transmission', 'owner', 'brand']:
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
