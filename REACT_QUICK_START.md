# 🚀 Quick Start: React + Flask Setup (5 Minutes)

## The Complete Architecture

```
┌─────────────────────────┐
│  React Browser App      │
│  (localhost:3000)       │
│  ✓ Beautiful UI         │
│  ✓ Patient Form         │
│  ✓ Results Display      │
│  ✓ History Charts       │
└────────────┬────────────┘
             │ HTTP POST
             │ /predict
             ▼
┌─────────────────────────┐
│  Flask REST API         │
│  (localhost:5000)       │
│  ✓ /predict endpoint    │
│  ✓ /batch endpoint      │
│  ✓ /health check        │
└────────────┬────────────┘
             │ Loads models
             ▼
┌─────────────────────────┐
│  Respiratory Agent      │
│  (ML Model)             │
│  ✓ RandomForest         │
│  ✓ 99.15% accuracy      │
│  ✓ Uncertainty est.     │
└─────────────────────────┘
```

---

## ⚡ Quick Setup (Copy-Paste)

### Prerequisites (Check You Have These)

```bash
# Python 3.8+
python --version

# Node.js 14+
node --version
npm --version
```

If not installed, install from:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/

---

## 📋 Step-by-Step Installation

### STEP 1: Install Flask API Dependencies

```bash
cd /Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training

# Install Flask
pip install flask flask-cors

# Verify
python -c "from flask import Flask; print('✓ Flask ready')"
```

**Expected output:** `✓ Flask ready`

---

### STEP 2: Create React Project

Open **NEW Terminal** (keep first one available):

```bash
cd /Users/taneeshkpatel/Desktop/OVGU_Projects

# Create React app (takes 5-10 min)
npx create-react-app respiratory-ui

# Navigate into it
cd respiratory-ui
```

**Expected output:**
```
Happy hacking!
```

---

### STEP 3: Install React Dependencies

```bash
cd /Users/taneeshkpatel/Desktop/OVGU_Projects/respiratory-ui

# Install packages
npm install axios recharts

# Verify
npm list axios recharts
```

**Expected output:** Both packages listed with versions.

---

### STEP 4: Create Environment File

```bash
# Still in respiratory-ui folder
cat > .env << 'EOF'
REACT_APP_API_URL=http://localhost:5000
EOF

# Verify
cat .env
```

**Expected output:**
```
REACT_APP_API_URL=http://localhost:5000
```

---

### STEP 5: Create Components Directory

```bash
mkdir -p src/components
```

---

### STEP 6: Copy React Component Files

Copy the files from `REACT_SETUP_GUIDE.md`:

**File 1:** `src/components/RespiratoryAgent.jsx` (from guide)
**File 2:** `src/components/RespiratoryAgent.css` (from guide)

Or create them manually:

```bash
# Create empty files
touch src/components/RespiratoryAgent.jsx
touch src/components/RespiratoryAgent.css
```

Then paste the code from `REACT_SETUP_GUIDE.md` into each.

---

### STEP 7: Update App.js

Replace content of `src/App.js`:

```jsx
import React from 'react';
import RespiratoryAgent from './components/RespiratoryAgent';
import './App.css';

function App() {
  return (
    <div className="App">
      <RespiratoryAgent />
    </div>
  );
}

export default App;
```

---

### STEP 8: Update App.css

Replace content of `src/App.css`:

```css
.App {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 0;
}
```

---

## 🎯 Running Everything

### Terminal 1: Start Flask Backend

```bash
cd /Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training
python api_server.py
```

**Expected:**
```
======================================================================
🫁 RESPIRATORY AGENT API SERVER
======================================================================

Endpoints:
  GET  http://localhost:5000/health
  POST http://localhost:5000/predict
  ...

Running on http://0.0.0.0:5000
```

✅ Keep this running!

---

### Terminal 2: Start React Frontend

```bash
cd /Users/taneeshkpatel/Desktop/OVGU_Projects/respiratory-ui
npm start
```

**Expected:**
```
webpack compiled successfully

Local:            http://localhost:3000
On Your Network:  http://192.168.x.x:3000
```

✅ Browser should auto-open!

---

### Terminal 3: Open Browser (If Not Auto-Opened)

```
http://localhost:3000
```

**You should see:**
- 🫁 Beautiful purple gradient UI
- ✅ "Server Status: ✅ Connected"
- Form with patient input fields
- Three buttons: Get Prediction, Load Healthy Example, Load High-Risk Example

---

## 🧪 Test It

### Test 1: Load Example Patient

1. Click **"Load Healthy Example"** button
2. Form auto-fills with healthy patient data
3. Click **"Get Prediction"**
4. **Result:** Risk Level = **LOW** ✅

### Test 2: High-Risk Patient

1. Click **"Load High-Risk Example"** button
2. Form auto-fills with high-risk patient data
3. Click **"Get Prediction"**
4. **Result:** Risk Level = **HIGH** ✅

### Test 3: Manual Entry

1. Change SpO2 to 88 (low oxygen)
2. Change Respiratory Rate to 28 (high)
3. Click **"Get Prediction"**
4. **Result:** Risk Level = **MEDIUM** or **HIGH** ✅

---

## ✨ Features You Now Have

✅ **Beautiful React Dashboard**
- Modern gradient UI (purple theme)
- Real-time form validation
- Responsive design (works on mobile too)
- Clean typography

✅ **Interactive Results**
- Risk level display (LOW/MEDIUM/HIGH)
- Confidence percentage
- Probability bars
- Clinical recommendation
- Top contributing factors
- Uncertainty metrics

✅ **Prediction History**
- Last 10 predictions in a table
- Timestamp for each
- Risk level color-coded

✅ **REST API**
- Single patient predictions
- Batch predictions
- Model metadata
- Example patients
- Health checks

---

## 🔧 Common Issues & Solutions

### Issue: "Server Status: ❌ Disconnected"

**Solution:**
```bash
# Make sure Flask is running in Terminal 1
# Check it's working:
curl http://localhost:5000/health

# Should return:
# {"status":"healthy","agent":"respiratory",...}
```

---

### Issue: "Port 3000 Already in Use"

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Then restart React
npm start
```

---

### Issue: "Port 5000 Already in Use"

```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Then restart Flask
python api_server.py
```

---

### Issue: CORS Error in Console

**Solution:** 
- Flask server has `CORS(app)` enabled
- Just restart both servers (Ctrl+C then restart)

---

### Issue: "Module Not Found" Errors

```bash
# In respiratory-ui folder, reinstall dependencies
npm install

# Or install specific package
npm install axios recharts
```

---

## 📁 File Structure

```
/Users/taneeshkpatel/Desktop/OVGU_Projects/
├── agent-training/                    ← Your ML models here
│   ├── api_server.py                  ← Flask backend
│   ├── respiratory_agent_api.py       ← Agent API
│   ├── respiratory_agent_training.ipynb
│   ├── respiratory_rf_pipeline.joblib ← Model file
│   ├── example_patient_*.json
│   └── ...
│
└── respiratory-ui/                    ← React frontend
    ├── src/
    │   ├── components/
    │   │   ├── RespiratoryAgent.jsx   ← Main component
    │   │   └── RespiratoryAgent.css   ← Styling
    │   ├── App.js
    │   ├── App.css
    │   └── index.js
    ├── .env                           ← API configuration
    ├── package.json
    ├── public/
    └── node_modules/
```

---

## 🚀 Next Steps

### After Testing Locally:

#### Option 1: Deploy Frontend to Netlify (FREE)
```bash
cd respiratory-ui
npm run build

# Go to https://netlify.com
# Drag & drop the 'build' folder
# Site goes live in seconds
```

#### Option 2: Deploy Backend to Heroku (FREE/PAID)
```bash
cd agent-training
git init
git add .
git commit -m "initial"
heroku create
git push heroku main
```

#### Option 3: Deploy Both to AWS/Azure/GCP
See documentation for each platform.

---

## 📊 What's Happening Behind the Scenes

1. **You fill patient form** → React state updated
2. **Click "Get Prediction"** → React makes HTTP POST to Flask
3. **Flask receives data** → Calls RespiratoryAgent.predict()
4. **Agent loads models** → Runs inference
5. **Agent returns results** → Risk level, probabilities, confidence
6. **Flask sends JSON response** → React receives via axios
7. **React displays results** → Beautiful UI shows:
   - Risk level (LOW/MEDIUM/HIGH)
   - Confidence percentage
   - Probability bars
   - Clinical action
   - Top factors
8. **Added to history** → Table updated

---

## 🎓 Learn More

- **ML Model Details:** See `NOTEBOOK_EXPLANATION.md`
- **API Endpoints:** See `HOW_TO_USE_AGENT.md`
- **Full Setup Guide:** See `REACT_SETUP_GUIDE.md`
- **Architecture Diagrams:** See `VISUAL_GUIDE.md`

---

## ✅ Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 14+ installed
- [ ] Flask + Flask-CORS installed
- [ ] React app created
- [ ] axios + recharts installed
- [ ] .env file created
- [ ] Component files copied
- [ ] App.js updated
- [ ] Flask running on port 5000
- [ ] React running on port 3000
- [ ] Browser shows UI
- [ ] Example predictions work

**If all ✅, you're ready to go!**

---

## 🆘 Still Having Issues?

### Debug Checklist

1. **Is Flask running?**
   ```bash
   curl http://localhost:5000/health
   ```
   Should return JSON, not "Connection refused"

2. **Is React running?**
   ```bash
   curl http://localhost:3000
   ```
   Should return HTML, not error

3. **Are all dependencies installed?**
   ```bash
   python -c "from flask import Flask; print('✓')"
   cd respiratory-ui && npm list axios
   ```

4. **Check browser console (F12)**
   Look for red errors and read the message

5. **Check Flask terminal**
   Look for error messages when making predictions

6. **Check file paths**
   All files in the right place?

---

## 🎉 Success!

When everything works, you'll see:

1. Purple gradient UI at localhost:3000
2. "✅ Connected" server status
3. Patient form with input fields
4. Example buttons load data correctly
5. Predictions return instantly
6. History table shows results
7. Colors match risk levels (🟢 green for LOW)

**Congratulations! Your Respiratory Agent UI is live!** 🚀🫁

---

## 📞 Quick Commands Reference

```bash
# Start Flask
cd /Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training
python api_server.py

# Start React
cd /Users/taneeshkpatel/Desktop/OVGU_Projects/respiratory-ui
npm start

# Stop any service
Ctrl + C

# Check port status
lsof -i :3000   # React
lsof -i :5000   # Flask

# Kill process on port
lsof -ti:3000 | xargs kill -9
lsof -ti:5000 | xargs kill -9

# Reinstall React dependencies
cd respiratory-ui && npm install

# Reinstall Flask dependencies
pip install flask flask-cors
```

---

**Now you're all set! Start the servers and enjoy your UI! 🎉**
