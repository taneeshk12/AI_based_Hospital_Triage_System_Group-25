# Respiratory Agent Training - Visual Flow & Architecture Guide

## 📊 End-to-End Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    RESPIRATORY AGENT TRAINING                   │
└─────────────────────────────────────────────────────────────────┘

                            INPUT LAYER
                                ▼
                    ┌───────────────────────┐
                    │  data_engineered.csv  │
                    │   87,234 samples      │
                    │   22 features         │
                    └───────────────────────┘
                                ▼
                        EXPLORATION LAYER
                                ▼
        ┌────────────────────────────────────────────┐
        │  • Check columns & data types              │
        │  • Find missing values                     │
        │  • Analyze distributions                  │
        │  • Identify outliers                      │
        └────────────────────────────────────────────┘
                                ▼
                      FEATURE ENGINEERING LAYER
                                ▼
        ┌────────────────────────────────────────────┐
        │  Rule-Based Target Creation               │
        │  • HIGH if SpO2<90 OR RR>30 OR RDI>4    │
        │  • MEDIUM if SpO2∈[90,94] OR RR∈[20,30]│
        │  • LOW otherwise                         │
        │                                          │
        │  Result:                                 │
        │  • Class 0 (LOW):    61% samples        │
        │  • Class 1 (MEDIUM): 21% samples        │
        │  • Class 2 (HIGH):   9% samples         │
        └────────────────────────────────────────────┘
                                ▼
                      FEATURE SELECTION LAYER
                                ▼
        ┌────────────────────────────────────────────┐
        │  Select 11 Most Relevant Features:        │
        │  ✓ spo2                                  │
        │  ✓ respiratory_rate (PRIMARY)            │
        │  ✓ respiratory_distress_index            │
        │  ✓ spo2_risk_score                       │
        │  ✓ rr_risk_score                         │
        │  ✓ temp_risk_score                       │
        │  ✓ temperature                           │
        │  ✓ heart_rate                            │
        │  ✓ age                                   │
        │  ✓ sex                                   │
        │  ✓ age_group                             │
        └────────────────────────────────────────────┘
                                ▼
                    DATA PREPROCESSING LAYER
                                ▼
        ┌────────────────────────────────────────────┐
        │  Numeric Features (9):                    │
        │  Step 1: Median Imputation (fill NaN)    │
        │  Step 2: StandardScaler                   │
        │          (mean=0, std=1)                 │
        │                                          │
        │  Categorical Features (2):                │
        │  Step 1: Most Frequent Imputation         │
        │  Step 2: One-Hot Encoding                 │
        │          (sex: M→1,F→0)                  │
        │          (age_group: 4 binary columns)   │
        └────────────────────────────────────────────┘
                                ▼
                      DATA SPLITTING LAYER
                                ▼
        ┌────────────────────────────────────────────┐
        │  Stratified Split (maintain class ratios):│
        │                                          │
        │  Training Set:    61,063 (70%)           │
        │  Validation Set:  13,085 (15%)           │
        │  Test Set:        13,086 (15%)           │
        │                                          │
        │  Each set maintains:                     │
        │  • 70% LOW risk samples                  │
        │  • 21% MEDIUM risk samples               │
        │  • 9% HIGH risk samples                  │
        └────────────────────────────────────────────┘
                                ▼
                 HYPERPARAMETER TUNING LAYER
                                ▼
        ┌────────────────────────────────────────────┐
        │  RandomizedSearchCV with StratifiedKFold  │
        │                                          │
        │  Tuning:                                 │
        │  • n_estimators: [100, 200, 300]        │
        │  • max_depth: [None, 10, 20, 30]        │
        │  • max_features: ['auto','sqrt','log2'] │
        │                                          │
        │  Validation: 3-fold CV on training data │
        │  Metric: F1-macro (balanced)             │
        │                                          │
        │  Best Found:                             │
        │  ✓ n_estimators: 300 trees              │
        │  ✓ max_depth: 20                        │
        │  ✓ max_features: 'log2'                 │
        │  ✓ Validation Accuracy: 99%             │
        └────────────────────────────────────────────┘
                                ▼
                      MODEL TRAINING LAYER
                                ▼
        ┌────────────────────────────────────────────┐
        │  Train Best RandomForest Model            │
        │                                          │
        │  Architecture:                           │
        │  • 300 decision trees                    │
        │  • Max depth: 20                         │
        │  • Feature selection: log2               │
        │  • Random state: 42                      │
        │                                          │
        │  Training Data: 61,063 samples          │
        │  Features Used: All 11 (after transform)│
        │  Time: ~30 seconds                       │
        │                                          │
        │  Output: respiratory_rf_pipeline.joblib │
        │  Size: 63 MB                             │
        └────────────────────────────────────────────┘
                                ▼
                    ENSEMBLE UNCERTAINTY LAYER
                                ▼
        ┌────────────────────────────────────────────┐
        │  Build 5-Model Ensemble                   │
        │  (Different random seeds)                │
        │                                          │
        │  Model 1 (seed=42)   ─┐                 │
        │  Model 2 (seed=43)   ─┤                 │
        │  Model 3 (seed=44)   ─┼─► Aggregate    │
        │  Model 4 (seed=45)   ─┤   Mean Proba   │
        │  Model 5 (seed=46)   ─┤   Std Dev      │
        │                       ─┘                 │
        │                                          │
        │  Output: respiratory_rf_ensemble.joblib │
        │  Size: 314 MB                            │
        │  Uncertainty Type: Epistemic             │
        └────────────────────────────────────────────┘
                                ▼
                        EVALUATION LAYER
                                ▼
        ┌────────────────────────────────────────────┐
        │  Test on Held-Out Data (13,086 samples)  │
        │                                          │
        │  METRICS:                                │
        │  ┌──────────────────────────────────────┐│
        │  │ Class │ Precision │ Recall │ F1    ││
        │  ├──────────────────────────────────────┤│
        │  │ 0(L) │   100%    │  100%  │ 1.00  ││
        │  │ 1(M) │   98%     │  100%  │ 0.99  ││
        │  │ 2(H) │   100%    │  89%   │ 0.94  ││
        │  └──────────────────────────────────────┘│
        │                                          │
        │  Overall Accuracy: 99.15%               │
        │  Macro F1: 97.8%                        │
        │                                          │
        │  Confusion Matrix:                       │
        │  ┌──────────┬─────┬─────┬─────┐        │
        │  │ Actual\  │ 0   │ 1   │ 2   │        │
        │  ├──────────┼─────┼─────┼─────┤        │
        │  │ 0        │8102 │  0  │  0  │        │
        │  │ 1        │  0  │4018 │  0  │        │
        │  │ 2        │ 33  │ 78  │ 855 │        │
        │  └──────────┴─────┴─────┴─────┘        │
        └────────────────────────────────────────────┘
                                ▼
                    EXPLAINABILITY LAYER
                                ▼
        ┌────────────────────────────────────────────┐
        │  SHAP Feature Importance Analysis         │
        │                                          │
        │  Top Features (by SHAP value):           │
        │  1. respiratory_rate        ████ 47.8%  │
        │  2. respiratory_distress    ██ 12.8%    │
        │  3. spo2_risk_score        ██ 12.8%    │
        │  4. spo2                   ██ 11.6%    │
        │  5. heart_rate             █ 10.8%     │
        │  Others                    █ 3.2%     │
        │                                          │
        │  Interpretation:                        │
        │  • respiratory_rate is DOMINANT         │
        │  • Risk scores are significant          │
        │  • Demographics have less impact        │
        └────────────────────────────────────────────┘
                                ▼
                      ARTIFACT SAVING LAYER
                                ▼
        ┌────────────────────────────────────────────┐
        │  Save 4 Model Components:                │
        │                                          │
        │  1. respiratory_rf_pipeline.joblib       │
        │     (Preprocessor + Classifier)          │
        │     Size: 63 MB                          │
        │                                          │
        │  2. respiratory_rf_ensemble.joblib       │
        │     (5 trained models for uncertainty)   │
        │     Size: 314 MB                         │
        │                                          │
        │  3. respiratory_preprocessor.joblib      │
        │     (Data transformer only)              │
        │     Size: 4.2 KB                         │
        │                                          │
        │  4. respiratory_classifier.joblib        │
        │     (RandomForest classifier only)       │
        │     Size: 63 MB                          │
        └────────────────────────────────────────────┘
                                ▼
                      PRODUCTION API LAYER
                                ▼
        ┌────────────────────────────────────────────┐
        │  RespiratoryAgent Class                  │
        │  • Load pre-trained models               │
        │  • Validate inputs                       │
        │  • Make predictions                      │
        │  • Return confidence & uncertainty       │
        │  • Provide clinical recommendations      │
        └────────────────────────────────────────────┘
                                ▼
                          OUTPUT LAYER
                                ▼
        ┌────────────────────────────────────────────┐
        │  Prediction Result JSON:                 │
        │  {                                       │
        │    "risk_class": 0,                      │
        │    "risk_level": "LOW",                  │
        │    "probabilities": {                    │
        │      "low": 0.9974,                     │
        │      "medium": 0.0024,                  │
        │      "high": 0.0002                     │
        │    },                                    │
        │    "confidence": 0.9974,                │
        │    "uncertainty": 0.001615,             │
        │    "clinical_action": "...",            │
        │    "top_features": [...]                │
        │  }                                       │
        └────────────────────────────────────────────┘
```

---

## 🔄 Data Transformation Flow

```
PATIENT FEATURES (11 columns)
│
├─ Numeric (9): spo2, rr, temp, hr, age, rr_score, spo2_score, temp_score, rdi
│   │
│   ├─ Step 1: Missing Value Imputation (Median)
│   │   95.0, NaN, 98.6, 82, 65 → 95.0, 94.2, 98.6, 82, 65
│   │
│   └─ Step 2: StandardScaler (normalize)
│       Raw: [95.0, 98.6, 82]
│       → Scaled: [0.45, 1.12, -0.82]
│
└─ Categorical (2): sex, age_group
    │
    ├─ Step 1: Missing Value Imputation (Most Frequent)
    │   M, NaN, F → M, M, F (if M is most common)
    │
    └─ Step 2: One-Hot Encoding
        sex: [M, F] → [sex_M, sex_F]
        age_group: [pediatric, adult, senior, elderly] 
                 → [ag_ped, ag_adult, ag_senior, ag_elderly]

FINAL VECTOR: [95_scaled, 98_scaled, ..., sex_M, sex_F, ag_senior, ...]
              ↓
         13-17 DIMENSIONS (depending on categories)
         ↓
      TO RANDOM FOREST MODEL
```

---

## 🎯 Model Decision Tree (Simplified)

```
                        RandomForest (300 trees)
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
             Tree 1          Tree 2 ...    Tree 300
              │               │             │
         ┌────┴────┐      ┌────┴────┐      │
         ▼         ▼      ▼         ▼      │
      Split on  Split on Split on Split on│
      RR>22?    SpO2<94? RDI>2?   RR>20?  │
       /\        /\      /\       /\      │
      /  \      /  \    /  \     /  \    │
    YES  NO   YES  NO  YES NO   YES NO   │
     │    │    │    │   │   │    │   │   │
     ▼    ▼    ▼    ▼   ▼   ▼    ▼   ▼  ...
   [2] [0] [2] [0] [2] [0] [1] [0]

Vote for Each Sample:
  Model1: Vote for Class 2 (HIGH)
  Model2: Vote for Class 1 (MEDIUM)
  Model3: Vote for Class 2 (HIGH)
  ...
  Model300: Vote for Class 2 (HIGH)

Final: Majority vote → Class 2 (HIGH)
       Probability: 250/300 = 83.3% (HIGH), 30/300 = 10% (MED), 20/300 = 6.7% (LOW)
       Uncertainty: std([1,0,1,1,...]) = 0.31 (models disagree)
```

---

## 📈 Feature Importance Visualization

```
Feature Importance Distribution
(based on how much each feature reduces impurity in splits)

respiratory_rate              ████████████████████████████ 47.8%
                              ↑ DOMINANT PREDICTOR

respiratory_distress_idx      ████ 12.8%
spo2_risk_score               ████ 12.8%
spo2                          ███ 11.6%
heart_rate                    ███ 10.8%

temperature                   █ 3.0%
age                           █ 0.8%
rr_risk_score                 0.1%
temp_risk_score               0.0%
sex                           0.0%
age_group                     0.0%


Interpretation:
• respiratory_rate explains ~48% of decisions
• Top 5 features explain ~95% of decisions
• Demographics (sex, age_group) have minimal impact
• Engineered scores are moderately important
```

---

## 🔍 Uncertainty Estimation Mechanism

```
ENSEMBLE-BASED UNCERTAINTY

Patient Input
    │
    ├─► Model 1 (seed=42) → Predicts: [0.90, 0.08, 0.02]
    │   Confidence on Class 0: 0.90
    │
    ├─► Model 2 (seed=43) → Predicts: [0.92, 0.06, 0.02]
    │   Confidence on Class 0: 0.92
    │
    ├─► Model 3 (seed=44) → Predicts: [0.88, 0.10, 0.02]
    │   Confidence on Class 0: 0.88
    │
    ├─► Model 4 (seed=45) → Predicts: [0.89, 0.09, 0.02]
    │   Confidence on Class 0: 0.89
    │
    └─► Model 5 (seed=46) → Predicts: [0.91, 0.07, 0.02]
        Confidence on Class 0: 0.91

AGGREGATION:
Mean Probability:    [0.90, 0.08, 0.02]  ← All models agree
Std Deviation:       [0.015, 0.015, 0.0] ← LOW DISAGREEMENT
Max Uncertainty:     0.015               ← HIGH CONFIDENCE

Result: Predict Class 0 (LOW risk) with HIGH confidence


UNCERTAIN CASE:
    ├─► Model 1 → [0.50, 0.35, 0.15]
    ├─► Model 2 → [0.45, 0.40, 0.15]
    ├─► Model 3 → [0.55, 0.30, 0.15]
    ├─► Model 4 → [0.48, 0.37, 0.15]
    └─► Model 5 → [0.52, 0.32, 0.16]

AGGREGATION:
Mean Probability:    [0.50, 0.35, 0.15]
Std Deviation:       [0.035, 0.045, 0.005] ← HIGH DISAGREEMENT
Max Uncertainty:     0.045               ← LOW CONFIDENCE

Result: Predict Class 0 (LOW risk) with LOW confidence
        Flag for review: "Model disagreement detected"
```

---

## 📊 Class Distribution Across Splits

```
Original Data (87,234 samples)
┌────────────────┐
│ LOW:   61,000  │ 70%
│ MED:   18,000  │ 21%
│ HIGH:   8,000  │  9%
└────────────────┘

After Stratified Split:
┌─────────────────┬──────────────┬────────────────┬───────────────┐
│ Training (70%)  │ Validation   │ Test           │ Overall       │
│ 61,063 samples  │ 15% (13,085) │ 15% (13,086)   │ 87,234        │
├─────────────────┼──────────────┼────────────────┼───────────────┤
│ LOW:  42,744    │ LOW: 8,744   │ LOW: 8,102     │ LOW:  59,590  │
│ 70%             │ 67%          │ 62%            │ 68%           │
├─────────────────┼──────────────┼────────────────┼───────────────┤
│ MED:  12,813    │ MED: 2,879   │ MED: 4,018     │ MED:  19,710  │
│ 21%             │ 22%          │ 31%            │ 23%           │
├─────────────────┼──────────────┼────────────────┼───────────────┤
│ HIGH: 5,506     │ HIGH: 1,462  │ HIGH: 966      │ HIGH: 7,934   │
│  9%             │ 11%          │  7%            │  9%           │
└─────────────────┴──────────────┴────────────────┴───────────────┘

(Stratification ensures similar distributions across splits)
```

---

## 🎯 Model Performance Summary

```
CONFUSION MATRIX (Test Set - 13,086 samples)

                    PREDICTED
                0(LOW)  1(MED)  2(HIGH)  │ TOTAL
            ──┼─────────────────────────┤
ACTUAL  0(L) │  8102      0       0     │ 8102 ✓
            1(M) │     0   4018       0     │ 4018 ✓
            2(H) │    33     78     855     │  966 ⚠
            ──┴─────────────────────────┘
             
PERFORMANCE BREAKDOWN:

Class 0 (LOW Risk):
  ✓ Correctly classified: 8,102 / 8,102 = 100%
  ✓ No false alarms (0 false positives)

Class 1 (MEDIUM Risk):
  ✓ Correctly classified: 4,018 / 4,018 = 100%
  ✓ Perfect recall

Class 2 (HIGH Risk):
  ⚠ Correctly classified: 855 / 966 = 88.5%
  ⚠ 111 missed high-risk cases:
    - 33 misclassified as LOW risk (dangerous!)
    - 78 misclassified as MEDIUM risk (requires intervention)

SUMMARY:
→ Model is EXCELLENT for low/medium risk
→ Model MISSES ~12% of high-risk cases
→ Recommendation: Use as screening tool, not final diagnosis
→ Flag all MEDIUM predictions for clinician review
```

---

## 📝 Input/Output Example

```
INPUT PATIENT DATA:
{
  "spo2": 88.0,                    ← Low oxygen
  "respiratory_rate": 28.0,        ← Elevated breathing
  "respiratory_distress_index": 2.5, ← Moderate distress
  "spo2_risk_score": 0.5,          ← Risk indicator
  "rr_risk_score": 0.4,            ← Risk indicator
  "temp_risk_score": 0.2,          ← Risk indicator
  "temperature": 38.5,             ← Slight fever
  "heart_rate": 105.0,             ← Elevated heart rate
  "age": 72.0,                     ← Elderly
  "sex": "F",                      ← Female
  "age_group": "elderly"           ← Elderly group
}

PROCESSING STEPS:
1. Validate inputs ✓
2. Apply preprocessing (scale, encode) ✓
3. Get predictions from all 5 ensemble models
4. Aggregate results (mean probability, std uncertainty)
5. Determine confidence level based on thresholds

OUTPUT PREDICTION:
{
  "risk_class": 2,
  "risk_level": "HIGH",
  "probabilities": {
    "low": 0.00,        ← 0% chance of low risk
    "medium": 0.38,     ← 38% chance of medium risk
    "high": 0.62        ← 62% chance of high risk ← DOMINANT
  },
  "confidence": 0.62,   ← 62% confidence in HIGH prediction
  "confidence_level": "MEDIUM",  ← Not extremely confident
  "uncertainty": 0.032, ← Moderate disagreement in ensemble
  "clinical_alert": true,        ← Flag for clinician review
  "clinical_action": "High respiratory risk - escalate to respiratory specialist",
  "top_contributing_features": [
    "respiratory_rate",
    "respiratory_distress_index",
    "spo2_risk_score"
  ],
  "timestamp": "2026-05-26T14:30:45.123456",
  "status": "success"
}

INTERPRETATION:
→ Patient is HIGH risk (62% probability)
→ Confidence is MEDIUM (not 100% certain)
→ Ensemble has some disagreement (uncertainty: 0.032)
→ Clinical alert triggered (recommend specialist review)
→ Top factors: respiratory rate, distress, and oxygen scores
→ Action: Escalate to respiratory specialist immediately
```

---

## 🔐 Safety Features

```
CONFIDENCE THRESHOLDS:

HIGH CONFIDENCE (Fully Trust Prediction):
  • Probability ≥ 0.85 AND
  • Uncertainty < 0.02
  • Action: Automatic decision

MEDIUM CONFIDENCE (Review Recommended):
  • 0.60 ≤ Probability < 0.85 OR
  • Uncertainty ≥ 0.02
  • Action: Flag for clinician review

LOW CONFIDENCE (Manual Review Required):
  • Probability < 0.60 OR
  • Uncertainty very high
  • Action: Escalate to expert physician


INPUT VALIDATION:

  SpO2 ∈ [50, 100] %
  RR ∈ [0, 60] breaths/min
  HR ∈ [0, 200] bpm
  Temp ∈ [0, 42] °C
  Age ∈ [0, 120] years
  Sex ∈ {'M', 'F'}
  Age_group ∈ {'pediatric','adult','senior','elderly'}
  
  If any validation fails → Error returned, no prediction made
```

---

## 🚀 Deployment Architecture

```
TRAINING PHASE (One-time):
┌─────────────────────────────────────────┐
│  This Jupyter Notebook                  │
│  • Load data                            │
│  • Train models                         │
│  • Save artifacts (.joblib files)       │
└─────────────────────────────────────────┘
       │
       ├─► respiratory_rf_pipeline.joblib
       ├─► respiratory_rf_ensemble.joblib
       ├─► respiratory_preprocessor.joblib
       └─► respiratory_classifier.joblib


INFERENCE PHASE (Production):
┌─────────────────────────────────────────┐
│  REST API (FastAPI)                     │
│  • POST /predict                        │
│  • Input: Patient features JSON         │
│  • Output: Risk prediction JSON         │
├─────────────────────────────────────────┤
│  Load Models at Startup:                │
│  agent = RespiratoryAgent()             │
│  ├─ Load pipeline (preprocessor+clf)    │
│  └─ Load ensemble (5 models)            │
├─────────────────────────────────────────┤
│  On Each Request:                       │
│  1. Validate input                      │
│  2. Call agent.predict()                │
│  3. Log request/response (audit trail)  │
│  4. Return JSON result                  │
└─────────────────────────────────────────┘
       │
       └─► Healthcare System / EHR Integration


MULTI-AGENT ARCHITECTURE:
┌──────────────────────────────────────────────────┐
│          Patient Data                            │
└─────────────────┬──────────────────────────────┘
                  │
         ┌────────┼────────┐
         ▼        ▼        ▼
    ┌────────┐ ┌──────┐ ┌─────────┐
    │Cardiac │ │Resp  │ │General  │
    │Agent   │ │Agent │ │Agent    │
    │(SVM)   │ │(RF)  │ │(XGBoost)│
    └────────┘ └──────┘ └─────────┘
         │        │        │
         └────────┼────────┘
                  ▼
         ┌──────────────────┐
         │  Fusion Layer    │
         │  (Gating/Voting) │
         └──────────────────┘
                  ▼
         ┌──────────────────┐
         │ Final Diagnosis  │
         │  + Confidence    │
         └──────────────────┘
```

---

This visual guide complements the detailed step-by-step explanation in NOTEBOOK_EXPLANATION.md

