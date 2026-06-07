# 🫁 Respiratory Risk Assessment System - Startup Guide

## ⚙️ **System Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCTOR'S COMPUTER                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  REACT UI (Frontend)                                 │  │
│  │  URL: http://localhost:3000                          │  │
│  │                                                       │  │
│  │  • Clean form with 7 input fields                    │  │
│  │  • Doctor enters vital signs                         │  │
│  │  • Shows risk predictions with colors               │  │
│  │  • Displays clinical recommendations                │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↑↓ (HTTP)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FLASK API (Backend)                                 │  │
│  │  URL: http://localhost:8000                          │  │
│  │                                                       │  │
│  │  • Receives 7 raw vital signs                        │  │
│  │  • Calculates 4 risk scores automatically            │  │
│  │  • Runs ML model (99.15% accuracy)                  │  │
│  │  • Returns predictions with confidence               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 **STARTUP PROCEDURE (3 STEPS)**

### **Step 1: Start the Backend API Server**

Open **Terminal 1** and run:

```bash
cd /Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training
python api_server.py
```

**Expected Output:**
```
======================================================================
🫁 RESPIRATORY AGENT API SERVER
======================================================================

Endpoints:
  GET  http://localhost:8000/health
  POST http://localhost:8000/predict
  POST http://localhost:8000/batch
  GET  http://localhost:8000/model-info
  GET  http://localhost:8000/example-patients

======================================================================
Starting server on http://localhost:8000...
======================================================================

 * Serving Flask app 'api_server'
 * Debug mode: off
 * Running on http://127.0.0.1:8000
```

✅ **Backend is ready when you see: "Running on http://127.0.0.1:8000"**

---

### **Step 2: Start the Frontend React UI**

Open **Terminal 2** and run:

```bash
cd /Users/taneeshkpatel/Desktop/OVGU_Projects/respiratory-ui
npm start
```

**Expected Output (takes ~30-50 seconds):**
```
Compiled successfully!

You can now view respiratory-ui in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000

Note that the development build is not optimized.
To create a production build, use npm run build.
```

✅ **Frontend is ready when you see: "Compiled successfully!"**

---

### **Step 3: Open the Application in Browser**

Open your **browser** and go to:

```
http://localhost:3000
```

You should see:
- Clean form with 7 input fields
- Patient vital signs section
- Blue "Predict Risk Level" button
- Green example buttons

---

## ✅ **System Health Check**

To verify both servers are running properly, run this in a **third terminal**:

```bash
# Check Backend API
curl -s http://localhost:8000/health | python -m json.tool

# Check Frontend
curl -s http://localhost:3000 | head -5
```

**Expected Backend Response:**
```json
{
    "status": "healthy",
    "agent": "respiratory",
    "model_loaded": true
}
```

---

## 🧪 **Test the System**

Once both servers are running:

### **Test 1: Healthy Patient**
Fill the form with:
```
SpO₂: 97 %
Respiratory Rate: 16 breaths/min
Temperature: 36.8 °C
Heart Rate: 70 bpm
Age: 40 years
Sex: Male
Age Group: 30-50
```
Click "Predict Risk Level"
**Expected Result: 🟢 LOW RISK (Green)**

### **Test 2: High-Risk Patient**
Fill the form with:
```
SpO₂: 85 %
Respiratory Rate: 32 breaths/min
Temperature: 39.2 °C
Heart Rate: 115 bpm
Age: 65 years
Sex: Female
Age Group: 60+
```
Click "Predict Risk Level"
**Expected Result: 🔴 HIGH RISK (Red)**

### **Test 3: Quick Example Load**
Click "📊 Healthy Example" or "⚠️ High-Risk Example"
Should auto-fill the form with test data

---

## 🔧 **Backend Auto-Calculation**

When you submit the form:

**Step 1 - You Send (7 fields):**
```json
{
  "spo2": 97,
  "respiratory_rate": 16,
  "temperature": 36.8,
  "heart_rate": 70,
  "age": 40,
  "sex": "M",
  "age_group": "30-50"
}
```

**Step 2 - Backend Calculates (4 additional fields):**
```
SpO₂ Risk Score: 0.1 (normal range = low risk)
RR Risk Score: 0.2 (normal breathing = low risk)
Temperature Risk Score: 0.1 (normal temp = low risk)
Respiratory Distress Index: 0.133 (combined metric)
```

**Step 3 - Model Predicts (using all 11 features):**
```json
{
  "risk_level": "LOW",
  "risk_class": 0,
  "confidence": 95.3%,
  "clinical_action": "Low respiratory risk - continue routine monitoring"
}
```

---

## 🛑 **Stopping the Servers**

### **Stop Backend:**
In Terminal 1, press: `Ctrl + C`

### **Stop Frontend:**
In Terminal 2, press: `Ctrl + C`

---

## ❌ **Troubleshooting**

### **Port 8000 already in use:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Then restart API
```

### **Port 3000 already in use:**
```bash
# Find what's using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Then restart React
```

### **Models not loading:**
```bash
# Check if model files exist
ls -lah *.joblib

# Should show:
# respiratory_rf_pipeline.joblib (63 MB)
# respiratory_rf_ensemble.joblib (314 MB)
```

### **MetaMask or Crypto Extension Errors:**
These are from browser extensions and NOT from our application. They can be safely ignored. Our app doesn't use any blockchain or MetaMask features.

To disable them:
1. Go to `chrome://extensions/` (or equivalent in your browser)
2. Find MetaMask or similar crypto extensions
3. Toggle them OFF or remove them
4. Refresh the page

---

## 📊 **API Endpoints Reference**

### **1. Health Check**
```bash
curl http://localhost:8000/health
```

### **2. Single Patient Prediction**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "spo2": 97,
    "respiratory_rate": 16,
    "temperature": 36.8,
    "heart_rate": 70,
    "age": 40,
    "sex": "M",
    "age_group": "30-50"
  }'
```

### **3. Batch Predictions**
```bash
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '[
    {"spo2": 97, "respiratory_rate": 16, ...},
    {"spo2": 85, "respiratory_rate": 32, ...}
  ]'
```

### **4. Model Information**
```bash
curl http://localhost:8000/model-info
```

### **5. Example Patients**
```bash
curl http://localhost:8000/example-patients
```

---

## 📋 **File Locations**

| File | Location | Purpose |
|------|----------|---------|
| Backend API | `api_server.py` | Flask server (port 8000) |
| ML Agent | `respiratory_agent_api.py` | Prediction logic |
| Models | `respiratory_rf_pipeline.joblib` | Main ML model (63 MB) |
| Ensemble | `respiratory_rf_ensemble.joblib` | Uncertainty estimation (314 MB) |
| Frontend | `respiratory-ui/src/App.js` | React component (port 3000) |
| Styling | `respiratory-ui/src/App.css` | UI design |

---

## ✨ **Quick Start Script (All in One)**

If you want to start everything at once:

```bash
# Terminal 1
cd /Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training && python api_server.py &

# Terminal 2
cd /Users/taneeshkpatel/Desktop/OVGU_Projects/respiratory-ui && npm start &

# Then open browser
open http://localhost:3000
```

---

## 🎯 **System Ready When:**

- ✅ Terminal 1 shows: "Running on http://127.0.0.1:8000"
- ✅ Terminal 2 shows: "Compiled successfully!"
- ✅ Browser loads http://localhost:3000 without errors
- ✅ Form has 7 input fields (no risk score fields)
- ✅ Clicking predict button works and returns results

---

**Questions?** Check the troubleshooting section or verify both servers are running! 🚀
