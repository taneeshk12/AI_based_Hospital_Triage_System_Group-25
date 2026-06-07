"""
Retrain General Health XGBoost model from data_engineered.csv
ESI levels: 1,2 -> HIGH_RISK(2)  |  3 -> MID_RISK(1)  |  4,5 -> LOW_RISK(0)
Saves: general_xgb_model.joblib + general_xgb_meta.json
"""
import pandas as pd
import numpy as np
import joblib
import json
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

print("Loading data...")
df = pd.read_csv('data_engineered.csv')
print(f"  Shape: {df.shape}")

# ── Map ESI → 3 risk classes ────────────────────────────────
# ESI 1,2 = critical/emergent -> HIGH_RISK (2)
# ESI 3   = urgent            -> MID_RISK  (1)
# ESI 4,5 = less/non-urgent   -> LOW_RISK  (0)
esi_map = {1: 2, 2: 2, 3: 1, 4: 0, 5: 0}
df['risk_class'] = df['esi_level'].map(esi_map)
df = df.dropna(subset=['risk_class'])
df['risk_class'] = df['risk_class'].astype(int)

print(f"  Risk class distribution:\n{df['risk_class'].value_counts().sort_index()}")

# ── Encode categoricals ─────────────────────────────────────
df['sex_encoded'] = (df['sex'].str.upper() == 'F').astype(int)
df['country_encoded'] = (df['country'].str.upper() == 'USA').astype(int)

# ── Feature set (matches GeneralHealthAgent.FEATURE_NAMES) ──
FEATURES = [
    'age', 'systolic_bp', 'diastolic_bp', 'heart_rate',
    'respiratory_rate', 'temperature', 'spo2', 'pain_score',
    'wbc', 'hemoglobin', 'platelet_count', 'sodium',
    'potassium', 'creatinine', 'glucose', 'troponin',
    'bnp', 'lactate', 'inr',
    'sex_encoded', 'country_encoded',
]
# chest_pain and diabetes not in dataset — add as zeros
df['chest_pain'] = 0
df['diabetes']   = 0
FEATURES += ['chest_pain', 'diabetes']

X = df[FEATURES].fillna(df[FEATURES].median())
y = df['risk_class']

print(f"\nFeatures ({len(FEATURES)}): {FEATURES}")

# ── Train/test split ─────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\nTrain: {X_train.shape}, Test: {X_test.shape}")

# ── Train XGBoost ────────────────────────────────────────────
print("\nTraining XGBoost...")
model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective='multi:softprob',
    num_class=3,
    eval_metric='mlogloss',
    random_state=42,
    verbosity=0,
)
model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

# ── Evaluate ─────────────────────────────────────────────────
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\nTest Accuracy: {acc:.4f} ({acc*100:.2f}%)")
print(classification_report(y_test, y_pred, target_names=['LOW_RISK','MID_RISK','HIGH_RISK']))

# ── Feature importances ───────────────────────────────────────
importances = model.feature_importances_
top5_idx = np.argsort(importances)[-5:][::-1]
print("Top 5 features:", [FEATURES[i] for i in top5_idx])

# ── Save model ───────────────────────────────────────────────
joblib.dump(model, 'general_xgb_model.joblib')
print("\n✓ Saved: general_xgb_model.joblib")

# ── Save metadata ─────────────────────────────────────────────
meta = {
    'model_type': 'XGBoost',
    'n_estimators': 300,
    'max_depth': 6,
    'learning_rate': 0.05,
    'test_accuracy': round(acc, 4),
    'n_features': len(FEATURES),
    'feature_names': FEATURES,
    'risk_classes': {0: 'LOW_RISK', 1: 'MID_RISK', 2: 'HIGH_RISK'},
    'esi_mapping': {'1,2': 'HIGH_RISK', '3': 'MID_RISK', '4,5': 'LOW_RISK'},
    'top_features': [FEATURES[i] for i in top5_idx],
    'training_samples': len(X_train),
    'test_samples': len(X_test),
}
with open('general_xgb_meta.json', 'w') as f:
    json.dump(meta, f, indent=2)
print("✓ Saved: general_xgb_meta.json")
print("\n✅ Done! Restart the Flask server to load the new model.")
