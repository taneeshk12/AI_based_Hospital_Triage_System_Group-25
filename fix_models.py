"""
Fix scikit-learn model compatibility by retraining with current version.
This script retrains the ensemble models to be compatible with scikit-learn 1.8.0
"""

import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the data
logger.info("Loading data...")
df = pd.read_csv('data_engineered.csv')

# Recreate target column based on rules (from notebook)
logger.info("Creating target column with clinical rules...")

def create_respiratory_risk(row):
    """Create respiratory risk category based on clinical rules"""
    spo2_low = row['spo2'] < 92
    rr_high = row['respiratory_rate'] > 24
    rdi_high = row['respiratory_distress_index'] > 1.5
    rr_risk = row['rr_risk_score'] > 0.6
    spo2_risk = row['spo2_risk_score'] > 0.5
    temp_risk = row['temp_risk_score'] > 0.4
    
    risk_count = sum([spo2_low, rr_high, rdi_high, rr_risk, spo2_risk, temp_risk])
    
    if risk_count >= 3:
        return 2  # HIGH
    elif risk_count >= 1:
        return 1  # MEDIUM
    else:
        return 0  # LOW

df['resp_risk_cat'] = df.apply(create_respiratory_risk, axis=1)
logger.info(f"✓ Target distribution: {df['resp_risk_cat'].value_counts().to_dict()}")

# Split features and target
features = [
    'spo2', 'respiratory_rate', 'respiratory_distress_index', 
    'spo2_risk_score', 'rr_risk_score', 'temp_risk_score',
    'temperature', 'heart_rate', 'age', 'sex', 'age_group'
]

X = df[features]
y = df['resp_risk_cat']

# Create preprocessor
numeric_features = ['spo2', 'respiratory_rate', 'respiratory_distress_index', 
                   'spo2_risk_score', 'rr_risk_score', 'temp_risk_score',
                   'temperature', 'heart_rate', 'age']
categorical_features = ['sex', 'age_group']

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ]
)

# Train main model
logger.info("Training main RandomForest model...")
best_rf = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(
        n_estimators=300, 
        max_depth=20, 
        random_state=42,
        n_jobs=-1
    ))
])

best_rf.fit(X, y)
logger.info("✓ Main model trained")

# Train ensemble (5 models with different seeds)
logger.info("Training ensemble models (5 seeds)...")
ensemble = []
for seed in [42, 123, 456, 789, 999]:
    rf = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(
            n_estimators=300, 
            max_depth=20, 
            random_state=seed,
            n_jobs=-1
        ))
    ])
    rf.fit(X, y)
    ensemble.append(rf)
    logger.info(f"  Seed {seed}: ✓")

# Save models
logger.info("Saving models...")
joblib.dump(best_rf, 'respiratory_rf_pipeline.joblib')
logger.info("✓ Saved: respiratory_rf_pipeline.joblib")

joblib.dump(ensemble, 'respiratory_rf_ensemble.joblib')
logger.info("✓ Saved: respiratory_rf_ensemble.joblib")

# Test predictions
logger.info("\nTesting predictions...")
test_pred = best_rf.predict(X.iloc[:5])
test_proba = best_rf.predict_proba(X.iloc[:5])
logger.info(f"✓ Sample predictions: {test_pred}")
logger.info(f"✓ Sample probabilities shape: {test_proba.shape}")

logger.info("\n✅ Model retraining complete! Models are now compatible with scikit-learn 1.8.0")
