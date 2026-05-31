import pandas as pd
import numpy as np
import joblib
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler

def preprocess_data(filepath='dataset/cardekho_dataset.csv'):
    df = pd.read_csv(filepath)

    # Drop the useless index column
    df.drop('Unnamed: 0', axis=1, inplace=True)

    # Fix brand capitalisation inconsistency
    df['brand'] = df['brand'].str.strip()
    df['brand'] = df['brand'].replace('ISUZU', 'Isuzu')

    # Drop columns the model cannot use
    # car_name = full name like "Maruti Alto" — redundant, brand+model covers it
    # model = too many unique values, causes overfitting
    # Extract brand AND model from full car name
    # Dataset already has 'brand' and 'model' columns — just rename model to car_model
    if 'model' in df.columns:
        df['car_model'] = df['model']
        df.drop('model', axis=1, inplace=True)

    # Always drop car_name — it's raw text, scaler cannot handle it
    if 'car_name' in df.columns:
        df.drop('car_name', axis=1, inplace=True)

    # Remove outliers
    df = df[df['km_driven'] < 300000]      # remove data entry errors
    df = df[df['km_driven'] > 500]         # remove nearly zero
    df = df[df['seats'] > 0]               # remove impossible seats=0
    df = df[df['selling_price'] >= 40000]  # remove junk prices
    df = df[df['selling_price'] <= 5000000] # remove ultra-luxury outliers
    df = df[df['vehicle_age'] <= 25]       # remove very old cars

    # Encode categorical columns (text → numbers)
    cat_cols = ['brand', 'car_model','seller_type', 'fuel_type', 'transmission_type']
    label_encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le

    os.makedirs('models', exist_ok=True)
    joblib.dump(label_encoders, 'models/label_encoders.pkl')

    # Features and target
    X = df.drop('selling_price', axis=1)
    y = df['selling_price']

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, 'models/scaler.pkl')
    joblib.dump(X.columns.tolist(), 'models/feature_names.pkl')

    print(f"Final shape: {X_scaled.shape}")
    print(f"Features: {X.columns.tolist()}")
    print(f"Price range: Rs.{y.min():,.0f} to Rs.{y.max():,.0f}")

    return X_scaled, y, X.columns.tolist()

if __name__ == '__main__':
    preprocess_data()