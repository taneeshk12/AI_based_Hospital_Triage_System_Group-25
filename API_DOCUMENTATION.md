# 🏥 Multi-Agent Diagnostic API Documentation

## Overview

This API provides production-ready endpoints for two diagnostic agents:
1. **🫁 Respiratory Agent** - Predicts respiratory risk (Low/Medium/High)
2. **🏥 General Health Agent** - Predicts ED triage risk using multimodal approach (tabular + clinical embeddings)

Both agents are integrated into a single Flask API server running on `http://localhost:8000`.

---

## Health Check

### GET `/health`
Check API and agent status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-05-29T10:30:45.123456",
  "agents": {
    "respiratory": true,
    "general": true
  }
}
```

---

## 🫁 Respiratory Agent Endpoints

### POST `/respiratory/predict`
**Single patient respiratory risk prediction**

#### Request Body
```json
{
  "spo2": 95,
  "respiratory_rate": 18,
  "temperature": 37.2,
  "heart_rate": 72,
  "age": 45,
  "sex": "M",
  "age_group": "30-50"
}
```

#### Response
```json
{
  "status": "success",
  "risk_class": 0,
  "risk_level": "LOW",
  "probabilities": {
    "low": 0.92,
    "medium": 0.06,
    "high": 0.02
  },
  "confidence": 0.92,
  "confidence_level": "HIGH",
  "uncertainty": 0.015,
  "clinical_action": "Low respiratory risk - continue routine monitoring",
  "top_contributing_features": [
    "spo2",
    "respiratory_rate",
    "respiratory_distress_index"
  ],
  "clinical_alert": false,
  "timestamp": "2026-05-29T10:30:45.123456",
  "patient_data": {...}
}
```

#### Feature Descriptions
- **spo2** (50-100): Oxygen saturation percentage
- **respiratory_rate** (0-60): Breaths per minute
- **temperature** (32-42): Body temperature in Celsius
- **heart_rate** (0-200): Beats per minute
- **age** (0-150): Patient age in years
- **sex** (M/F): Patient sex
- **age_group**: Age range category (e.g., "30-50")

**Note:** Risk scores (spo2_risk_score, rr_risk_score, etc.) are automatically calculated by the backend.

---

### POST `/respiratory/batch`
**Multiple patient predictions**

#### Request Body
```json
[
  {
    "spo2": 95,
    "respiratory_rate": 18,
    "temperature": 37.2,
    "heart_rate": 72,
    "age": 45,
    "sex": "M",
    "age_group": "30-50"
  },
  {
    "spo2": 88,
    "respiratory_rate": 28,
    "temperature": 38.5,
    "heart_rate": 110,
    "age": 65,
    "sex": "F",
    "age_group": "60-70"
  }
]
```

#### Response
```json
{
  "total": 2,
  "predictions": [
    {
      "status": "success",
      "risk_level": "LOW",
      "confidence": 0.92,
      "patient_index": 0,
      "timestamp": "2026-05-29T10:30:45.123456"
    },
    {
      "status": "success",
      "risk_level": "HIGH",
      "confidence": 0.88,
      "patient_index": 1,
      "timestamp": "2026-05-29T10:30:45.234567"
    }
  ]
}
```

---

### GET `/respiratory/model-info`
**Get respiratory model metadata**

#### Response
```json
{
  "model_type": "RandomForest",
  "n_estimators": 300,
  "test_accuracy": 0.9915,
  "classes": {
    "0": "LOW",
    "1": "MEDIUM",
    "2": "HIGH"
  },
  "thresholds": {
    "confidence_high": 0.85,
    "confidence_medium": 0.60,
    "uncertainty_alert": 0.02
  }
}
```

---

### GET `/respiratory/example-patients`
**Get example respiratory patients for testing**

#### Response
```json
{
  "healthy": {
    "data": {...},
    "expected_risk": "LOW"
  },
  "high_risk": {
    "data": {...},
    "expected_risk": "HIGH"
  }
}
```

---

## 🏥 General Health Agent Endpoints

### POST `/general/predict`
**Single patient ED triage risk prediction**

#### Request Body
```json
{
  "age": 45,
  "systolic_bp": 140,
  "diastolic_bp": 90,
  "heart_rate": 95,
  "respiratory_rate": 18,
  "temperature": 37.5,
  "spo2": 96,
  "pain_score": 3,
  "wbc": 7.5,
  "hemoglobin": 13.5,
  "platelet_count": 250,
  "sodium": 138,
  "potassium": 4.0,
  "creatinine": 0.9,
  "glucose": 100,
  "troponin": 0.01,
  "bnp": 50,
  "lactate": 1.5,
  "inr": 1.0,
  "sex": "M",
  "country": "USA",
  "clinical_notes": "Patient presents with chest pain and elevated blood pressure. No acute distress."
}
```

#### Response
```json
{
  "status": "success",
  "risk_class": 1,
  "risk_level": "MID_RISK",
  "probabilities": {
    "low_risk": 0.25,
    "mid_risk": 0.60,
    "high_risk": 0.15
  },
  "confidence": 0.60,
  "confidence_level": "MEDIUM",
  "uncertainty": 0.35,
  "clinical_action": "Medium risk patient - close monitoring required",
  "top_contributing_features": [
    "systolic_bp",
    "heart_rate",
    "troponin"
  ],
  "tabular_importance": 0.65,
  "embedding_importance": 0.35,
  "clinical_alert": false,
  "model_type": "multimodal_lightgbm",
  "timestamp": "2026-05-29T10:30:45.123456"
}
```

#### Feature Descriptions

**Vital Signs:**
- **systolic_bp** (80-200): Systolic blood pressure in mmHg
- **diastolic_bp** (40-120): Diastolic blood pressure in mmHg
- **heart_rate** (30-200): Beats per minute
- **respiratory_rate** (8-60): Breaths per minute
- **temperature** (32-42): Body temperature in Celsius
- **spo2** (50-100): Oxygen saturation percentage
- **pain_score** (0-10): Pain severity scale

**Lab Values:**
- **wbc** (3-15): White blood cell count (K/uL)
- **hemoglobin** (7-20): Hemoglobin level (g/dL)
- **platelet_count** (100-500): Platelets (K/uL)
- **sodium** (120-160): Sodium level (mEq/L)
- **potassium** (2.5-6): Potassium level (mEq/L)
- **creatinine** (0.5-2): Creatinine level (mg/dL)
- **glucose** (50-500): Blood glucose level (mg/dL)
- **troponin** (0-2): Troponin level (ng/mL)
- **bnp** (0-1000): B-type natriuretic peptide (pg/mL)
- **lactate** (0.5-10): Lactate level (mmol/L)
- **inr** (0.8-4): International normalized ratio

**Demographics:**
- **age** (0-150): Patient age in years
- **sex**: "M" or "F"
- **country**: Country code or name

**Clinical Data (Optional):**
- **clinical_notes**: Free-text clinical notes (max 512 chars)
  - Used to generate 768-dimensional clinical embeddings via ClinicalBERT
  - If empty, zero embedding is used

---

### POST `/general/batch`
**Multiple patient ED triage predictions**

#### Request Body
```json
[
  {patient1_data},
  {patient2_data},
  ...
]
```

#### Response
```json
{
  "total": 2,
  "predictions": [
    {
      "status": "success",
      "risk_level": "LOW_RISK",
      "confidence": 0.85,
      "tabular_importance": 0.70,
      "embedding_importance": 0.30,
      "patient_index": 0,
      "model_type": "multimodal_lightgbm",
      "timestamp": "2026-05-29T10:30:45.123456"
    },
    {
      "status": "success",
      "risk_level": "HIGH_RISK",
      "confidence": 0.92,
      "tabular_importance": 0.60,
      "embedding_importance": 0.40,
      "patient_index": 1,
      "model_type": "multimodal_lightgbm",
      "timestamp": "2026-05-29T10:30:45.234567"
    }
  ]
}
```

---

### GET `/general/model-info`
**Get general health model metadata**

#### Response
```json
{
  "model_type": "LightGBM (Multimodal: Tabular + ClinicalBERT)",
  "tabular_features": 23,
  "embedding_dimension": 768,
  "total_features": 791,
  "embedding_model": "medicalai/clinicalBERT",
  "confidence_threshold_high": 0.85,
  "confidence_threshold_medium": 0.70,
  "uncertainty_threshold": 0.15,
  "risk_classes": {
    "0": "LOW_RISK",
    "1": "MID_RISK",
    "2": "HIGH_RISK"
  },
  "training_accuracy": 0.985,
  "training_f1": 0.98,
  "n_estimators": 300,
  "max_depth": 8
}
```

---

### GET `/general/example-patient`
**Get example general health patient for testing**

#### Response
```json
{
  "example": {
    "age": 45,
    "systolic_bp": 140,
    "diastolic_bp": 90,
    "heart_rate": 95,
    "respiratory_rate": 18,
    "temperature": 37.5,
    "spo2": 96,
    "pain_score": 3,
    "wbc": 7.5,
    "hemoglobin": 13.5,
    "platelet_count": 250,
    "sodium": 138,
    "potassium": 4.0,
    "creatinine": 0.9,
    "glucose": 100,
    "troponin": 0.01,
    "bnp": 50,
    "lactate": 1.5,
    "inr": 1.0,
    "sex": "M",
    "country": "USA",
    "clinical_notes": "Patient presents with chest pain and elevated blood pressure. No acute distress."
  },
  "description": "Medium-risk patient with hypertension and chest pain"
}
```

---

## 🔙 Legacy Endpoints (Backward Compatibility)

For backward compatibility with existing code, the following legacy endpoints still work and map to respiratory endpoints:

- `POST /predict` → `/respiratory/predict`
- `POST /batch` → `/respiratory/batch`
- `GET /model-info` → `/respiratory/model-info`
- `GET /example-patients` → `/respiratory/example-patients`

---

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid input) |
| 404 | Endpoint not found |
| 500 | Server error |
| 503 | Agent not loaded |

---

## Error Responses

### Invalid Input
```json
{
  "error": "Missing required features: ['spo2', 'respiratory_rate']",
  "status": "error"
}
```

### Agent Not Loaded
```json
{
  "error": "General Health Agent not loaded",
  "status": 503
}
```

### Prediction Error
```json
{
  "error": "Invalid feature range",
  "status": "error",
  "risk_level": "UNKNOWN"
}
```

---

## Usage Examples

### 1. Python (requests library)
```python
import requests

API_URL = "http://localhost:8000"

# Respiratory prediction
respiratory_patient = {
    "spo2": 95,
    "respiratory_rate": 18,
    "temperature": 37.2,
    "heart_rate": 72,
    "age": 45,
    "sex": "M",
    "age_group": "30-50"
}

response = requests.post(
    f"{API_URL}/respiratory/predict",
    json=respiratory_patient
)
result = response.json()
print(f"Risk: {result['risk_level']}, Confidence: {result['confidence']:.2%}")

# General health prediction
general_patient = {
    "age": 45,
    "systolic_bp": 140,
    "diastolic_bp": 90,
    "heart_rate": 95,
    "respiratory_rate": 18,
    "temperature": 37.5,
    "spo2": 96,
    "pain_score": 3,
    "wbc": 7.5,
    "hemoglobin": 13.5,
    "platelet_count": 250,
    "sodium": 138,
    "potassium": 4.0,
    "creatinine": 0.9,
    "glucose": 100,
    "troponin": 0.01,
    "bnp": 50,
    "lactate": 1.5,
    "inr": 1.0,
    "sex": "M",
    "country": "USA",
    "clinical_notes": "Chest pain and hypertension"
}

response = requests.post(
    f"{API_URL}/general/predict",
    json=general_patient
)
result = response.json()
print(f"Risk: {result['risk_level']}, Tabular importance: {result['tabular_importance']:.1%}")
```

### 2. JavaScript/React
```javascript
const API_URL = "http://localhost:8000";

// Respiratory prediction
const respiratoryPatient = {
  spo2: 95,
  respiratory_rate: 18,
  temperature: 37.2,
  heart_rate: 72,
  age: 45,
  sex: "M",
  age_group: "30-50"
};

fetch(`${API_URL}/respiratory/predict`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(respiratoryPatient)
})
  .then(res => res.json())
  .then(data => {
    console.log(`Risk: ${data.risk_level}, Confidence: ${(data.confidence * 100).toFixed(1)}%`);
  });

// General health prediction
const generalPatient = {
  age: 45,
  systolic_bp: 140,
  diastolic_bp: 90,
  heart_rate: 95,
  respiratory_rate: 18,
  temperature: 37.5,
  spo2: 96,
  pain_score: 3,
  wbc: 7.5,
  hemoglobin: 13.5,
  platelet_count: 250,
  sodium: 138,
  potassium: 4.0,
  creatinine: 0.9,
  glucose: 100,
  troponin: 0.01,
  bnp: 50,
  lactate: 1.5,
  inr: 1.0,
  sex: "M",
  country: "USA",
  clinical_notes: "Chest pain and hypertension"
};

fetch(`${API_URL}/general/predict`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(generalPatient)
})
  .then(res => res.json())
  .then(data => {
    console.log(`Risk: ${data.risk_level}, Tabular: ${(data.tabular_importance * 100).toFixed(1)}%`);
  });
```

### 3. cURL
```bash
# Respiratory prediction
curl -X POST http://localhost:8000/respiratory/predict \
  -H "Content-Type: application/json" \
  -d '{
    "spo2": 95,
    "respiratory_rate": 18,
    "temperature": 37.2,
    "heart_rate": 72,
    "age": 45,
    "sex": "M",
    "age_group": "30-50"
  }'

# General health prediction
curl -X POST http://localhost:8000/general/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 45,
    "systolic_bp": 140,
    "diastolic_bp": 90,
    "heart_rate": 95,
    "respiratory_rate": 18,
    "temperature": 37.5,
    "spo2": 96,
    "pain_score": 3,
    "wbc": 7.5,
    "hemoglobin": 13.5,
    "platelet_count": 250,
    "sodium": 138,
    "potassium": 4.0,
    "creatinine": 0.9,
    "glucose": 100,
    "troponin": 0.01,
    "bnp": 50,
    "lactate": 1.5,
    "inr": 1.0,
    "sex": "M",
    "country": "USA",
    "clinical_notes": "Chest pain and hypertension"
  }'

# Get model info
curl http://localhost:8000/general/model-info
curl http://localhost:8000/respiratory/model-info

# Health check
curl http://localhost:8000/health
```

---

## Deployment

### Start API Server
```bash
python api_server.py
```

### Start with Gunicorn (Production)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 api_server:app
```

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY respiratory_agent_api.py .
COPY general_agent_api.py .
COPY api_server.py .
COPY *.joblib .
COPY *.json .

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "api_server:app"]
```

---

## Configuration

### Model Loading
Models are loaded on server startup. If model files are missing:
- **Respiratory:** `respiratory_rf_pipeline.joblib`, `respiratory_rf_ensemble.joblib`
- **General:** `multimodal_lightgbm_model.pkl`, `shap_tree_explainer.pkl`, `multimodal_model_metadata.json`

### Confidence Thresholds

**Respiratory Agent:**
- High confidence: ≥0.85
- Medium confidence: 0.60-0.85
- Low confidence: <0.60

**General Health Agent:**
- High confidence: ≥0.85
- Medium confidence: 0.70-0.85
- Low confidence: <0.70

---

## Support

For issues or questions:
1. Check agent logs for detailed error messages
2. Verify model files exist and are not corrupted
3. Ensure input features are within valid ranges
4. Test with example patients using `/respiratory/example-patients` or `/general/example-patient`
