# ⚡ Quick Start Guide - Multi-Agent API

## 30-Second Setup

### 1. Start API Server
```bash
cd /Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training
python api_server.py
```

Expected output:
```
========================================================================
🏥 MULTI-AGENT DIAGNOSTIC API SERVER
========================================================================

📊 RESPIRATORY ENDPOINTS:
  POST http://localhost:8000/respiratory/predict
  POST http://localhost:8000/respiratory/batch
  GET  http://localhost:8000/respiratory/model-info
  GET  http://localhost:8000/respiratory/example-patients

🏥 GENERAL HEALTH ENDPOINTS:
  POST http://localhost:8000/general/predict
  POST http://localhost:8000/general/batch
  GET  http://localhost:8000/general/model-info
  GET  http://localhost:8000/general/example-patient

========================================================================
Starting server on http://localhost:8000...
```

### 2. Test Respiratory Model
```bash
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
```

Response:
```json
{
  "status": "success",
  "risk_level": "LOW",
  "confidence": 0.92,
  "confidence_level": "HIGH",
  "clinical_action": "Low respiratory risk - continue routine monitoring",
  "probabilities": {
    "low": 0.92,
    "medium": 0.06,
    "high": 0.02
  }
}
```

### 3. Test General Health Model (NEW)
```bash
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
    "clinical_notes": "Patient presents with chest pain and elevated BP."
  }'
```

Response:
```json
{
  "status": "success",
  "risk_level": "MID_RISK",
  "confidence": 0.60,
  "confidence_level": "MEDIUM",
  "tabular_importance": 0.65,
  "embedding_importance": 0.35,
  "clinical_action": "Medium risk patient - close monitoring required",
  "probabilities": {
    "low_risk": 0.25,
    "mid_risk": 0.60,
    "high_risk": 0.15
  }
}
```

### 4. Check Health
```bash
curl http://localhost:8000/health
```

---

## Python Integration

```python
import requests

API = "http://localhost:8000"

# Respiratory prediction
resp = requests.post(f"{API}/respiratory/predict", json={
    "spo2": 95,
    "respiratory_rate": 18,
    "temperature": 37.2,
    "heart_rate": 72,
    "age": 45,
    "sex": "M",
    "age_group": "30-50"
})
print(f"Respiratory: {resp.json()['risk_level']}")

# General health prediction
gen = requests.post(f"{API}/general/predict", json={
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
})
print(f"General: {gen.json()['risk_level']}")
```

---

## React Integration

```jsx
// src/App.jsx
import React from 'react';
import { Dashboard } from './components/Dashboard';

function App() {
  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}

export default App;
```

Setup in `.env`:
```
REACT_APP_API_URL=http://localhost:8000
```

---

## API Endpoints Reference

### Respiratory (Existing)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/respiratory/predict` | Single respiratory patient |
| POST | `/respiratory/batch` | Multiple respiratory patients |
| GET | `/respiratory/model-info` | Model metadata |
| GET | `/respiratory/example-patients` | Example patients |

### General Health (NEW)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/general/predict` | Single general health patient |
| POST | `/general/batch` | Multiple general health patients |
| GET | `/general/model-info` | Model metadata |
| GET | `/general/example-patient` | Example patient |

### Health
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | API status |

---

## File Structure

```
agent-training/
├── api_server.py                          # Main API (UPDATED)
├── respiratory_agent_api.py               # Respiratory model
├── general_agent_api.py                   # General health model (NEW)
├── API_DOCUMENTATION.md                   # Full API docs (NEW)
├── REACT_INTEGRATION_GUIDE.md             # React setup (NEW)
├── GENERAL_MODEL_INTEGRATION_SUMMARY.md   # Integration summary (NEW)
├── QUICK_START_GUIDE.md                   # This file (NEW)
│
├── respiratory_rf_pipeline.joblib         # Respiratory model (existing)
├── respiratory_rf_ensemble.joblib         # Respiratory ensemble (existing)
├── multimodal_lightgbm_model.pkl          # General model (need to copy)
├── shap_tree_explainer.pkl                # SHAP explainer (need to copy)
├── multimodal_model_metadata.json         # Model metadata (need to copy)
└── ...
```

---

## What Each Model Does

### 🫁 Respiratory Model
**Input:** 7 vital signs
**Output:** Respiratory risk (LOW/MEDIUM/HIGH)
**Best For:** Respiratory conditions, oxygen saturation, breathing patterns

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

### 🏥 General Health Model (Multimodal)
**Input:** 23 vital signs + labs + clinical notes
**Output:** ED triage risk (LOW_RISK/MID_RISK/HIGH_RISK)
**Best For:** Emergency department triage, comprehensive health assessment

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
  "clinical_notes": "Patient presents with chest pain..."
}
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 already in use | `lsof -ti:8000 \| xargs kill -9` then restart |
| "Agent not loaded" | Check model files exist in working directory |
| CORS error from React | CORS is enabled by default; check API_URL in .env |
| Slow predictions | General model uses clinical embeddings (slower); run on GPU for speed |
| Missing model files | Download/copy multimodal model files from training notebook |

---

## Next Steps

1. ✅ **Start API:** `python api_server.py`
2. ✅ **Test endpoints:** Use curl commands above
3. ✅ **Integrate React:** Follow REACT_INTEGRATION_GUIDE.md
4. ✅ **Deploy:** Use Docker or Gunicorn for production
5. ✅ **Monitor:** Check health endpoint regularly

---

## Key Differences Between Models

| Feature | Respiratory | General |
|---------|-------------|---------|
| Speed | ⚡ Fast | 🟡 Medium |
| Accuracy | 99.15% | 98.5% |
| Data | Vitals only | Vitals + labs + text |
| Embeddings | None | ClinicalBERT |
| Use Case | Respiratory focus | Full triage |

---

## Full Documentation

- **API Endpoints:** See `API_DOCUMENTATION.md`
- **React Components:** See `REACT_INTEGRATION_GUIDE.md`
- **Integration Details:** See `GENERAL_MODEL_INTEGRATION_SUMMARY.md`

---

**You're ready to go! 🚀**

Start the API server and enjoy dual-model predictions!
