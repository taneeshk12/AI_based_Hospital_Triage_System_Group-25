# 🎯 Simple Guide - How to Use

## What is This?

You have **2 AI doctors**:
- 🫁 **Lung Doctor** - Checks breathing health
- 🏥 **Hospital Doctor** - Checks overall health

They help predict if a patient is sick or healthy.

---

## Step 1: Start the AI Doctors

Open a terminal and type:

```bash
python api_server.py
```

You should see:
```
✅ Starting API Server...
✅ Doctors are ready!
http://localhost:8000
```

**Leave this terminal open while using the app!**

---

## Step 2: Use in Your React App

Your app (`respiratory-ui`) is already ready to talk to the doctors.

### Option A: Use Existing App

Just open your app in browser:
```
http://localhost:3000
```

It should connect to the doctors automatically ✅

---

## Step 3: How to Add to Your App

### If you made a new React project:

**Step A:** Copy these 4 files into your `src` folder:

1. **Create file:** `src/services/apiService.js`
   - This talks to the doctors
   - Copy code from REACT_INTEGRATION_GUIDE.md → "API Service Code"

2. **Create file:** `src/components/RespiratoryPredictor.jsx`
   - Form for lung doctor
   - Copy code from REACT_INTEGRATION_GUIDE.md → "Respiratory Component"

3. **Create file:** `src/components/GeneralHealthPredictor.jsx`
   - Form for hospital doctor
   - Copy code from REACT_INTEGRATION_GUIDE.md → "General Component"

4. **Create file:** `src/components/Dashboard.jsx`
   - Main page with tabs
   - Copy code from REACT_INTEGRATION_GUIDE.md → "Dashboard Component"

**Step B:** Copy CSS into `src/App.css`
   - Copy from REACT_INTEGRATION_GUIDE.md → "CSS Styling"

**Step C:** Update `src/App.jsx`:

```jsx
import React from 'react';
import { Dashboard } from './components/Dashboard';
import './App.css';

function App() {
  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}

export default App;
```

**Step D:** Create file `.env` in your project root:

```
REACT_APP_API_URL=http://localhost:8000
```

**Step E:** Start your app:

```bash
npm start
```

---

## Step 4: How to Use the App

### For Lung Doctor:

1. Click "Lung Doctor" tab
2. Fill in patient info:
   - Oxygen level (85-100)
   - Breathing rate (10-40)
   - Temperature (36-40)
   - Heart rate (50-120)
   - Age
   - Gender

3. Click "Predict"

4. See result:
   - **GREEN** = Healthy ✅
   - **YELLOW** = Watch carefully ⚠️
   - **RED** = Very sick 🚨

---

### For Hospital Doctor:

1. Click "Hospital Doctor" tab
2. Fill in patient info:
   - Blood pressure (top and bottom)
   - Oxygen level
   - Temperature
   - All blood test results
   - Optional: Write notes about patient

3. Click "Predict"

4. See result with explanation

---

## Step 5: Quick Test (No App Needed!)

Want to test without React? Use this:

### Test Lung Doctor:

Open Terminal and type:

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

You will get:
```json
{
  "risk_level": "LOW",
  "confidence": 0.92
}
```

---

### Test Hospital Doctor:

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
    "clinical_notes": "Patient has chest pain"
  }'
```

You will get:
```json
{
  "risk_level": "MID_RISK",
  "confidence": 0.60
}
```

---

## Common Problems & Fix

| Problem | Fix |
|---------|-----|
| "Connection refused" | Did you run `python api_server.py`? |
| Nothing appears | Check your `.env` file has `REACT_APP_API_URL=http://localhost:8000` |
| Slow response | Hospital doctor is slower (uses AI to read notes) - wait 2-3 seconds |
| "Port 8000 already used" | Run: `lsof -ti:8000 \| xargs kill -9` then restart |

---

## What Each Doctor Needs

### 🫁 Lung Doctor
**EASY** - Only 7 things:
- Oxygen level
- Breathing rate
- Temperature
- Heart rate
- Age
- Gender
- Age group

**Answer in:** 0.1 seconds ⚡

---

### 🏥 Hospital Doctor
**MEDIUM** - About 23 things:
- Blood pressure (2 numbers)
- Heart rate
- Breathing rate
- Temperature
- Oxygen level
- Pain level (1-10)
- White blood cells
- Hemoglobin
- Platelets
- Sodium
- Potassium
- Creatinine
- Glucose
- Troponin
- BNP
- Lactate
- INR
- Gender
- Country
- Optional: Patient notes

**Answer in:** 1-3 seconds ⏱️

---

## 3 Ways to Use

### Way 1: Simple (No Code)
1. Run `python api_server.py`
2. Open your app
3. Fill form
4. Click predict
5. See result

✅ **BEST FOR:** Normal users

---

### Way 2: Python Code
```python
import requests

result = requests.post('http://localhost:8000/respiratory/predict', json={
    "spo2": 95,
    "respiratory_rate": 18,
    "temperature": 37.2,
    "heart_rate": 72,
    "age": 45,
    "sex": "M",
    "age_group": "30-50"
})

print(result.json())
```

✅ **BEST FOR:** Data scientists

---

### Way 3: Your Code (Advanced)
Copy components from `REACT_INTEGRATION_GUIDE.md` into your React app and customize.

✅ **BEST FOR:** Developers

---

## Summary

1. **Start doctors:** `python api_server.py`
2. **Open app:** `http://localhost:3000`
3. **Fill patient info**
4. **Click predict**
5. **See result** ✅

That's it! 🎉

---

## Need More Help?

- **API details:** Read `API_DOCUMENTATION.md`
- **React code:** Read `REACT_INTEGRATION_GUIDE.md`
- **All info:** Read `GENERAL_MODEL_INTEGRATION_SUMMARY.md`
- **Quick commands:** Read `QUICK_START_GUIDE.md`

**Questions?** Check these guides! 📚
