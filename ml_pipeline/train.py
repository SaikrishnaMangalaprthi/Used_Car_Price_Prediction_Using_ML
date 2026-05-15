import numpy as np, joblib, sys, os
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml_pipeline.preprocess import preprocess_data
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
from sklearn.ensemble import GradientBoostingRegressor

 
def train_models():
    print("Loading and preprocessing data...")
    X, y, feature_names = preprocess_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Train: {len(X_train)} rows | Test: {len(X_test)} rows")
 
    models = {
        'Linear Regression': LinearRegression(),
        'Ridge Regression': Ridge(alpha=1.0),
        'Lasso Regression': Lasso(alpha=1.0),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting':   GradientBoostingRegressor(n_estimators=200,learning_rate=0.1,max_depth=5,random_state=42),
        'XGBoost':              XGBRegressor(
                                n_estimators=300,
                                learning_rate=0.05,
                                max_depth=6,
                                subsample=0.8,
                                colsample_bytree=0.8,
                                random_state=42,
                                verbosity=0  # suppress XGBoost console spam
                            ),

    }
 
    results = {}
    trained_models = {}
 
    for name, model in models.items():
        print(f"Training {name}...", end=" ")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        results[name] = {'MAE': round(mae,0), 'RMSE': round(rmse,0), 'R2': round(r2,4)}
        trained_models[name] = model
        print(f"MAE=Rs.{mae:.0f} | RMSE=Rs.{rmse:.0f} | R2={r2:.4f}")
 
    best_name = max(results, key=lambda x: results[x]['R2'])
    print(f"\nBest model: {best_name} (R2={results[best_name]['R2']})")
 
    # Save files
    joblib.dump(trained_models[best_name], 'models/best_model.pkl')
    joblib.dump(results, 'models/training_results.pkl')
    joblib.dump(best_name, 'models/best_model_name.pkl')
    joblib.dump(feature_names, 'models/feature_names.pkl')
 
    # Model comparison chart
    names = list(results.keys())
    r2s = [results[m]['R2'] for m in names]
    maes = [results[m]['MAE'] for m in names]
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#9b59b6', '#f39c12', '#1abc9c']
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.bar(names, r2s, color=colors); ax1.set_title('R² Score (higher = better)')
    ax1.set_ylim(0, 1)
    ax2.bar(names, maes, color=colors); ax2.set_title('MAE Rs. (lower = better)')
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig('static/images/model_comparison.png', bbox_inches='tight')
    plt.close()
 
    # Feature importance (Random Forest only)
    if hasattr(trained_models[best_name], 'feature_importances_'):
        imp = trained_models[best_name].feature_importances_
        idx = np.argsort(imp)[::-1]
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(imp)), imp[idx], color='#2E75B6')
        plt.xticks(range(len(imp)), [feature_names[i] for i in idx], rotation=45, ha='right')
        plt.title('Feature Importance — What Drives Used Car Price')
        plt.ylabel('Importance Score')
        plt.tight_layout()
        plt.savefig('static/images/feature_importance.png', bbox_inches='tight')
        plt.close()
 
    # Actual vs Predicted chart
    y_pred_best = trained_models[best_name].predict(X_test)
    plt.figure(figsize=(8, 8))
    plt.scatter(y_test, y_pred_best, alpha=0.3, color='#2E75B6')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel('Actual Price (Rs.)'); plt.ylabel('Predicted Price (Rs.)')
    plt.title('Actual vs Predicted')
    plt.savefig('static/images/actual_vs_predicted.png', bbox_inches='tight')
    plt.close()
 
    print("All charts saved to static/images/")
    return results, feature_names
 
if __name__ == '__main__':
    train_models()
