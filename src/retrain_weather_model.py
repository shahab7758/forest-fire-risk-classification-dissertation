#!/usr/bin/env python3
"""
Script to retrain the weather model with better practices
This addresses the overfitting issue that causes 100% predictions
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import joblib
import warnings
warnings.filterwarnings('ignore')

def load_and_prepare_data():
    """Load and prepare the dataset"""
    print("Loading dataset...")
    
    # Load the dataset
    df = pd.read_csv("analysis/small datasets/forestfire-classification.csv")
    
    # Drop irrelevant columns
    df.drop(["Unnamed: 0", "day", "month", "year", "Region"], axis=1, inplace=True)
    
    # Encode the target variable
    df["Classes"] = df["Classes"].map({"not fire": 0, "fire": 1})
    
    print(f"Dataset shape: {df.shape}")
    print(f"Class distribution:\n{df['Classes'].value_counts()}")
    
    return df

def create_better_model():
    """Create a more robust model using ensemble methods"""
    print("\nCreating improved model...")
    
    # Load data
    df = load_and_prepare_data()
    
    # Separate features and target
    X = df.drop('Classes', axis=1)
    y = df['Classes']
    
    # Split data with more reasonable test size
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save the scaler
    joblib.dump(scaler, "analysis/std_scaler_weather.pkl")
    
    # Try different models
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5),
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000)
    }
    
    best_model = None
    best_score = 0
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        # Use cross-validation to get a better estimate of performance
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
        print(f"Cross-validation scores: {cv_scores}")
        print(f"Mean CV score: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Train on full training set
        model.fit(X_train_scaled, y_train)
        
        # Evaluate on test set
        test_score = model.score(X_test_scaled, y_test)
        print(f"Test accuracy: {test_score:.3f}")
        
        if test_score > best_score:
            best_score = test_score
            best_model = model
    
    print(f"\nBest model: {best_model.__class__.__name__}")
    print(f"Best test accuracy: {best_score:.3f}")
    
    # Detailed evaluation of best model
    y_pred = best_model.predict(X_test_scaled)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["not fire", "fire"]))
    
    # Save the best model
    if hasattr(best_model, 'predict_proba'):
        # For sklearn models, we need to create a wrapper
        class ModelWrapper:
            def __init__(self, model):
                self.model = model
            
            def predict(self, X):
                # Return probability of fire (class 1)
                return self.model.predict_proba(X)[:, 1:2]
        
        wrapped_model = ModelWrapper(best_model)
    else:
        wrapped_model = best_model
    
    # Save the model
    joblib.dump(wrapped_model, "analysis/meteorological-detection-classification.keras")
    
    print("\nModel saved successfully!")
    
    # Test with some sample predictions
    print("\nTesting sample predictions:")
    sample_data = X_test_scaled[:5]
    predictions = wrapped_model.predict(sample_data)
    
    for i, pred in enumerate(predictions):
        print(f"Sample {i+1}: {pred[0]:.3f} ({pred[0]*100:.1f}%)")
    
    return wrapped_model, scaler

if __name__ == "__main__":
    print("Retraining Weather Model with Better Practices")
    print("=" * 50)
    
    model, scaler = create_better_model()
    
    print("\n" + "=" * 50)
    print("Retraining completed!")
    print("The new model should provide more realistic predictions.")
    print("Run test_weather_fix.py to verify the improvements.") 