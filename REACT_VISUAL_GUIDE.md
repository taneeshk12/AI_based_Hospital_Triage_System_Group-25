# React + Flask Setup - Visual Quick Reference

## 🎯 In 60 Seconds

```
GOAL: Build beautiful UI connected to your ML model

┌─────────────────────────────────────────────────────────────────┐
│ 1. INSTALL (5 min)                                              │
│    pip install flask flask-cors                                 │
│    npx create-react-app respiratory-ui                          │
│    npm install axios recharts                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. CREATE (5 min)                                               │
│    Copy React component files from REACT_SETUP_GUIDE.md         │
│    Update App.js and App.css                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. RUN (2 min)                                                  │
│    Terminal 1: python api_server.py                             │
│    Terminal 2: npm start                                        │
│    Browser:   http://localhost:3000                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ ✅ SUCCESS - Beautiful UI running!                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 What Gets Created

```
agent-training/                       (ALREADY EXISTS)
├── api_server.py                     ← CREATE THIS
├── respiratory_agent_api.py          (ALREADY EXISTS)
├── respiratory_rf_pipeline.joblib    (ALREADY EXISTS)
└── example_patient_*.json            (ALREADY EXISTS)

respiratory-ui/                       ← CREATE THIS
├── src/
│   ├── components/
│   │   ├── RespiratoryAgent.jsx     ← CREATE THIS
│   │   └── RespiratoryAgent.css     ← CREATE THIS
│   ├── App.js                        ← EDIT THIS
│   ├── App.css                       ← EDIT THIS
│   └── index.js                      (AUTO-GENERATED)
├── .env                              ← CREATE THIS
├── package.json                      (AUTO-GENERATED)
└── node_modules/                     (AUTO-GENERATED)
```

---

## 🔌 Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: User Opens Browser                                       │
│ → http://localhost:3000                                          │
│ → React loads RespiratoryAgent component                         │
│ → Axios checks Flask health (GET /health)                       │
│ → Status shows: "✅ Connected"                                    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: User Fills Form                                          │
│ → User enters patient vitals (SpO2, RR, etc)                    │
│ → Or clicks "Load Example"                                       │
│ → Form shows populated data                                      │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 3: User Clicks "Get Prediction"                             │
│ → React collects form data                                       │
│ → Axios makes POST request to /predict                           │
│ → Sends JSON with 11 vital signs                                 │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 4: Flask Receives Request                                   │
│ → Validates input data                                           │
│ → Calls RespiratoryAgent.predict()                              │
│ → Agent loads models from disk                                   │
│ → Preprocesses data (scale, impute, encode)                      │
│ → Runs RandomForest inference                                    │
│ → Runs 5-model ensemble for uncertainty                          │
│ → Returns JSON response                                          │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 5: React Receives Results                                   │
│ → Axios callback handles response                                │
│ → React updates state with prediction                            │
│ → Component re-renders with results                              │
│ → Adds prediction to history                                     │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 6: User Sees Results                                        │
│ → Risk level displayed (LOW/MEDIUM/HIGH)                        │
│ → Confidence percentage shown                                    │
│ → Probability bars visualized                                    │
│ → Clinical recommendation displayed                              │
│ → Top factors listed                                             │
│ → Added to history table                                         │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Required Files - Quick Reference

### File 1: `api_server.py`
```
LOCATION: /Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training/
SIZE: ~6 KB
CREATED: YES ✅
PURPOSE: Flask backend server
CONTAINS: 5 endpoints (/predict, /batch, /health, etc)
RUN: python api_server.py
PORT: 5000
```

### File 2: `respiratory-ui/src/components/RespiratoryAgent.jsx`
```
LOCATION: respiratory-ui/src/components/RespiratoryAgent.jsx
SIZE: ~15 KB (in REACT_SETUP_GUIDE.md)
CREATED: NO - Copy from guide
PURPOSE: Main React component
CONTAINS: Form, prediction display, history table
```

### File 3: `respiratory-ui/src/components/RespiratoryAgent.css`
```
LOCATION: respiratory-ui/src/components/RespiratoryAgent.css
SIZE: ~10 KB (in REACT_SETUP_GUIDE.md)
CREATED: NO - Copy from guide
PURPOSE: Styling for component
CONTAINS: Gradient theme, responsive design, animations
```

### File 4: `.env`
```
LOCATION: respiratory-ui/.env
SIZE: 1 line
CREATED: NO - Create manually
PURPOSE: Configuration
CONTAINS: REACT_APP_API_URL=http://localhost:5000
```

### File 5: `package.json`
```
LOCATION: respiratory-ui/package.json
SIZE: ~1 KB
CREATED: YES - Auto-generated by npx create-react-app
PURPOSE: Node dependencies
CONTAINS: axios, recharts, react, etc
```

---

## 🔑 Key Endpoints

```
┌──────────────────────────────────────────────────────┐
│ GET /health                                          │
├──────────────────────────────────────────────────────┤
│ Purpose: Check if API is running                     │
│ Used by: React on component mount                    │
│ Response: {status: "healthy", model_loaded: true}   │
│ Time: <1ms                                           │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ POST /predict                                        │
├──────────────────────────────────────────────────────┤
│ Purpose: Get prediction for one patient              │
│ Input: 11 vital signs (JSON)                         │
│ Output: Risk level, confidence, probabilities        │
│ Time: 30-50ms                                        │
│ Used by: React prediction button                     │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ GET /example-patients                                │
├──────────────────────────────────────────────────────┤
│ Purpose: Load example patients for testing           │
│ Output: healthy and high_risk patient data           │
│ Time: <1ms                                           │
│ Used by: React example buttons                       │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ POST /batch                                          │
├──────────────────────────────────────────────────────┤
│ Purpose: Get predictions for multiple patients       │
│ Input: Array of patient data                         │
│ Output: Array of predictions                         │
│ Time: 30-50ms per patient                            │
│ Used by: Advanced features (future)                  │
└──────────────────────────────────────────────────────┘
```

---

## 📊 Component Architecture

```
RespiratoryAgent Component (Main)
│
├── State Management
│   ├── formData (patient vitals)
│   ├── result (prediction result)
│   ├── history (past predictions)
│   ├── serverHealth (API status)
│   └── error (error messages)
│
├── Effects
│   └── checkServerHealth (on mount)
│
├── Handlers
│   ├── handleInputChange (form input)
│   ├── handlePredict (get prediction)
│   ├── loadExample (load test data)
│   └── checkServerHealth (API check)
│
└── Render
    ├── Header (title + status)
    ├── Form Section (patient data input)
    ├── Results Section (if prediction exists)
    │   ├── Risk Card
    │   ├── Probabilities
    │   ├── Clinical Action
    │   └── Top Features
    └── History Section (past predictions)
```

---

## ⚙️ Configuration

### Flask (`api_server.py`)
```python
Debug Mode: False (production safe)
Host: 0.0.0.0 (accessible on network)
Port: 5000 (configurable)
CORS: Enabled (React can access)
Logging: INFO level (see errors in terminal)
```

### React (`.env`)
```
REACT_APP_API_URL=http://localhost:5000
```

### Nginx/Load Balancer (Optional, Production)
```
Frontend:
  - Port: 80/443
  - Serve from: dist folder
  - Proxy /api to backend

Backend:
  - Port: 8000 (production)
  - Load balanced across multiple instances
```

---

## 🐛 Common Issues - Visual Troubleshooting

```
❌ "Server Status: Disconnected"
   ↓
   Is Flask running?
   ├─ NO → Run: python api_server.py
   ├─ YES → Is port 5000 available?
   │        └─ NO → Kill: lsof -ti:5000 | xargs kill -9
   └─ Restart everything

❌ "Cannot GET /api/predict"
   ↓
   Is API URL correct in .env?
   ├─ NO → Fix: REACT_APP_API_URL=http://localhost:5000
   ├─ YES → Restart React: npm start
   └─ Check browser console (F12)

❌ "npm: command not found"
   ↓
   Is Node.js installed?
   ├─ NO → Install: https://nodejs.org/
   └─ YES → Restart terminal

❌ "Port 3000 already in use"
   ↓
   Kill existing process:
   lsof -ti:3000 | xargs kill -9
   Then: npm start
```

---

## 📈 Performance Metrics

```
┌─────────────────────────────────────────┐
│ Operation          │ Time      │ Status │
├─────────────────────────────────────────┤
│ React mount        │ 100-200ms │ ✅    │
│ API health check   │ 1-5ms     │ ✅    │
│ Form input         │ <1ms      │ ✅    │
│ HTTP POST          │ 2-10ms    │ ✅    │
│ Model inference    │ 30-50ms   │ ✅    │
│ HTTP Response      │ 1-5ms     │ ✅    │
│ React re-render    │ 10-20ms   │ ✅    │
├─────────────────────────────────────────┤
│ TOTAL (Get to Show)│ <100ms    │ ⚡    │
└─────────────────────────────────────────┘
```

---

## 📚 File Quick Links

| File | What | Where | Read |
|------|------|-------|------|
| **REACT_QUICK_START.md** | START HERE | agent-training/ | 5 min |
| **REACT_SETUP_GUIDE.md** | Full code | agent-training/ | 30 min |
| **api_server.py** | Backend | agent-training/ | Copy |
| **RespiratoryAgent.jsx** | Frontend | REACT_SETUP_GUIDE.md | Copy |
| **RespiratoryAgent.css** | Styling | REACT_SETUP_GUIDE.md | Copy |

---

## ✅ Pre-Flight Checklist

Before you start, verify:

```
Software:
[ ] Python 3.8+ installed
[ ] Node.js 14+ installed
[ ] pip works (python -m pip --version)
[ ] npm works (npm --version)

Directories:
[ ] /Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training/ exists
[ ] respiratory_rf_pipeline.joblib exists
[ ] example_patient_*.json files exist

Dependencies:
[ ] Flask installed (pip list | grep Flask)
[ ] Flask-CORS installed
[ ] axios will be installed (npm install)
[ ] recharts will be installed (npm install)

Ports:
[ ] Port 3000 available (lsof -i :3000)
[ ] Port 5000 available (lsof -i :5000)
```

---

## 🎬 Ready to Start?

```
1. Open 2 terminals side by side

2. Terminal 1 (Backend):
   cd /Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training
   pip install flask flask-cors
   python api_server.py
   
   ✅ Should show: "Running on http://0.0.0.0:5000"

3. Terminal 2 (Frontend):
   cd /Users/taneeshkpatel/Desktop/OVGU_Projects
   npx create-react-app respiratory-ui
   cd respiratory-ui
   npm install axios recharts
   echo "REACT_APP_API_URL=http://localhost:5000" > .env
   mkdir -p src/components
   
   (Copy RespiratoryAgent.jsx and .css from REACT_SETUP_GUIDE.md)
   
   npm start
   
   ✅ Should show: "Local: http://localhost:3000"

4. Browser:
   http://localhost:3000
   
   ✅ Should show: Beautiful purple UI!

5. Test:
   Click "Load Healthy Example" → Get Prediction → See "LOW"
   
   ✅ If you see this, you're done! 🎉
```

---

## 🎯 Success Indicators

When everything is working:

```
✅ Terminal 1 (Flask):
   - No red errors
   - Shows "Running on http://0.0.0.0:5000"
   - Logs requests when predictions made

✅ Terminal 2 (React):
   - No red errors
   - Shows "Compiled successfully"
   - Browser auto-opens at localhost:3000

✅ Browser:
   - Purple gradient background
   - "✅ Connected" status
   - All form fields visible
   - Example buttons work
   - Predictions show results
   - History table updates

✅ Functionality:
   - Healthy patient → LOW risk
   - High-risk patient → HIGH risk
   - Manual entry → Appropriate risk
   - All fields validated
   - No CORS errors
```

---

**You're ready! Follow the checklist and have fun building! 🚀**
