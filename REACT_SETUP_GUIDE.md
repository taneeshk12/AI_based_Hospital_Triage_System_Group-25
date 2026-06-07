# React UI for Respiratory Agent - Complete Setup Guide

## Overview

You'll have:
- **Backend**: Flask REST API (exposes agent predictions)
- **Frontend**: React Dashboard (beautiful UI for clinicians)
- **Communication**: HTTP requests between them

```
┌─────────────────────┐
│   React Frontend    │
│  (Port 3000)        │
│  - Patient form     │
│  - Risk dashboard   │
│  - History charts   │
└──────────┬──────────┘
           │ HTTP requests
           ▼
┌─────────────────────┐
│  Flask API Server   │
│  (Port 5000)        │
│  - /predict         │
│  - /batch           │
│  - /health          │
└──────────┬──────────┘
           │ Loads models
           ▼
┌─────────────────────┐
│ Respiratory Agent   │
│ (.joblib models)    │
└─────────────────────┘
```

---

## Part 1: Backend Setup (Flask API)

### Step 1.1: Create Flask API Server

Create file: `api_server.py`

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from respiratory_agent_api import RespiratoryAgent
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable React frontend to call this API

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load agent once (on startup)
try:
    agent = RespiratoryAgent()
    logger.info("✓ Respiratory Agent loaded successfully")
except Exception as e:
    logger.error(f"Failed to load agent: {e}")
    agent = None

# ==================== ENDPOINTS ====================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'agent': 'respiratory',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': agent is not None
    }), 200

@app.route('/predict', methods=['POST'])
def predict():
    """
    Single patient prediction
    
    POST /predict
    Body: {
        "spo2": 95,
        "respiratory_rate": 18,
        "respiratory_distress_index": 1.2,
        "spo2_risk_score": 0.5,
        "rr_risk_score": 0.3,
        "temp_risk_score": 0.1,
        "temperature": 37.2,
        "heart_rate": 72,
        "age": 45,
        "sex": "M",
        "age_group": "adult"
    }
    """
    try:
        if agent is None:
            return jsonify({'error': 'Agent not loaded'}), 503
        
        patient_data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'spo2', 'respiratory_rate', 'respiratory_distress_index',
            'spo2_risk_score', 'rr_risk_score', 'temp_risk_score',
            'temperature', 'heart_rate', 'age', 'sex', 'age_group'
        ]
        
        missing_fields = [f for f in required_fields if f not in patient_data]
        if missing_fields:
            return jsonify({
                'error': f'Missing fields: {", ".join(missing_fields)}'
            }), 400
        
        # Get prediction
        result = agent.predict(patient_data)
        
        # Add timestamp
        result['timestamp'] = datetime.now().isoformat()
        result['patient_data'] = patient_data
        
        logger.info(f"Prediction: {result['risk_level']} (conf: {result['confidence']:.2%})")
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/batch', methods=['POST'])
def batch_predict():
    """
    Multiple patients prediction
    
    POST /batch
    Body: [
        {patient1_data},
        {patient2_data},
        ...
    ]
    """
    try:
        if agent is None:
            return jsonify({'error': 'Agent not loaded'}), 503
        
        patients = request.get_json()
        
        if not isinstance(patients, list):
            return jsonify({'error': 'Body must be a JSON array'}), 400
        
        results = []
        for i, patient in enumerate(patients):
            try:
                result = agent.predict(patient)
                result['patient_index'] = i
                result['timestamp'] = datetime.now().isoformat()
                results.append(result)
            except Exception as e:
                results.append({
                    'patient_index': i,
                    'error': str(e),
                    'status': 'error'
                })
        
        logger.info(f"Batch prediction: {len(results)} patients processed")
        
        return jsonify({
            'total': len(results),
            'predictions': results
        }), 200
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/model-info', methods=['GET'])
def model_info():
    """Get model metadata"""
    return jsonify({
        'model_type': 'RandomForest',
        'n_estimators': 300,
        'test_accuracy': 0.9915,
        'classes': {
            0: 'LOW',
            1: 'MEDIUM',
            2: 'HIGH'
        },
        'features': [
            'spo2', 'respiratory_rate', 'respiratory_distress_index',
            'spo2_risk_score', 'rr_risk_score', 'temp_risk_score',
            'temperature', 'heart_rate', 'age', 'sex', 'age_group'
        ],
        'thresholds': {
            'confidence_high': 0.85,
            'confidence_medium': 0.60,
            'uncertainty_alert': 0.02
        }
    }), 200

@app.route('/example-patients', methods=['GET'])
def example_patients():
    """Get example patients for testing"""
    import json
    
    try:
        with open('example_patient_healthy.json') as f:
            healthy = json.load(f)
        
        with open('example_patient_high_risk.json') as f:
            high_risk = json.load(f)
        
        return jsonify({
            'healthy': {
                'data': healthy,
                'expected_risk': 'LOW'
            },
            'high_risk': {
                'data': high_risk,
                'expected_risk': 'HIGH'
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🫁 RESPIRATORY AGENT API SERVER")
    print("="*70)
    print("\nEndpoints:")
    print("  GET  http://localhost:5000/health")
    print("  POST http://localhost:5000/predict")
    print("  POST http://localhost:5000/batch")
    print("  GET  http://localhost:5000/model-info")
    print("  GET  http://localhost:5000/example-patients")
    print("\n" + "="*70)
    print("Starting server on http://localhost:5000...")
    print("="*70 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000)
```

### Step 1.2: Install Flask Dependencies

```bash
cd /Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training

# Install Flask and CORS
pip install flask flask-cors

# Verify installation
python -c "from flask import Flask; print('✓ Flask installed')"
```

### Step 1.3: Start the Flask Server

```bash
python api_server.py
```

**Output:**
```
======================================================================
🫁 RESPIRATORY AGENT API SERVER
======================================================================

Endpoints:
  GET  http://localhost:5000/health
  POST http://localhost:5000/predict
  POST http://localhost:5000/batch
  GET  http://localhost:5000/model-info
  GET  http://localhost:5000/example-patients

======================================================================
Starting server on http://localhost:5000...
======================================================================

 * Running on http://0.0.0.0:5000
```

✅ Backend is now running! Keep this terminal open.

---

## Part 2: Frontend Setup (React)

### Step 2.1: Create React Project (NEW Terminal)

Open a **new terminal** and run:

```bash
# Navigate to parent directory (NOT inside agent-training)
cd /Users/taneeshkpatel/Desktop/OVGU_Projects

# Create React app
npx create-react-app respiratory-ui
cd respiratory-ui
```

This creates a new React project. Wait for installation to complete (5-10 minutes).

### Step 2.2: Install React Dependencies

```bash
npm install axios recharts
```

- `axios`: For HTTP requests to Flask API
- `recharts`: For beautiful charts

### Step 2.3: Create Environment File

Create file: `respiratory-ui/.env`

```
REACT_APP_API_URL=http://localhost:5000
```

### Step 2.4: Create the Main Component

Create file: `respiratory-ui/src/components/RespiratoryAgent.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import './RespiratoryAgent.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const RespiratoryAgent = () => {
  const [formData, setFormData] = useState({
    spo2: 95,
    respiratory_rate: 18,
    respiratory_distress_index: 1.2,
    spo2_risk_score: 0.5,
    rr_risk_score: 0.3,
    temp_risk_score: 0.1,
    temperature: 37.2,
    heart_rate: 72,
    age: 45,
    sex: 'M',
    age_group: 'adult'
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const [serverHealth, setServerHealth] = useState('checking...');

  // Check API health on component mount
  useEffect(() => {
    checkServerHealth();
  }, []);

  const checkServerHealth = async () => {
    try {
      const response = await axios.get(`${API_URL}/health`);
      setServerHealth('✅ Connected');
    } catch (err) {
      setServerHealth('❌ Disconnected - Flask server not running');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: isNaN(value) ? value : parseFloat(value)
    }));
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/predict`, formData);
      const prediction = response.data;
      
      setResult(prediction);
      
      // Add to history
      const historyEntry = {
        timestamp: new Date().toLocaleTimeString(),
        risk_level: prediction.risk_level,
        confidence: (prediction.confidence * 100).toFixed(1),
        spo2: formData.spo2,
        rr: formData.respiratory_rate
      };
      setHistory(prev => [historyEntry, ...prev].slice(0, 10)); // Keep last 10
      
    } catch (err) {
      setError(err.response?.data?.error || 'Prediction failed. Check if Flask server is running.');
    } finally {
      setLoading(false);
    }
  };

  const loadExample = async (type) => {
    try {
      const response = await axios.get(`${API_URL}/example-patients`);
      const example = type === 'healthy' ? response.data.healthy.data : response.data.high_risk.data;
      setFormData(example);
    } catch (err) {
      setError('Failed to load example patient');
    }
  };

  const getRiskColor = (risk) => {
    if (risk === 'LOW') return '#10b981';
    if (risk === 'MEDIUM') return '#f59e0b';
    return '#ef4444';
  };

  const getRiskBgColor = (risk) => {
    if (risk === 'LOW') return '#d1fae5';
    if (risk === 'MEDIUM') return '#fef3c7';
    return '#fee2e2';
  };

  return (
    <div className="container">
      <header className="header">
        <h1>🫁 Respiratory Risk Assessment Agent</h1>
        <div className="server-status">Server Status: {serverHealth}</div>
      </header>

      <main className="main">
        {error && (
          <div className="error-box">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Form Section */}
        <section className="form-section">
          <h2>Patient Data Input</h2>
          
          <form onSubmit={handlePredict}>
            <div className="form-grid">
              {/* Vital Signs */}
              <div className="form-group">
                <label>SpO2 (%)</label>
                <input
                  type="number"
                  name="spo2"
                  min="50"
                  max="100"
                  step="0.1"
                  value={formData.spo2}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>Respiratory Rate (breaths/min)</label>
                <input
                  type="number"
                  name="respiratory_rate"
                  min="0"
                  max="60"
                  step="0.1"
                  value={formData.respiratory_rate}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>Respiratory Distress Index</label>
                <input
                  type="number"
                  name="respiratory_distress_index"
                  min="0"
                  max="10"
                  step="0.1"
                  value={formData.respiratory_distress_index}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>SpO2 Risk Score</label>
                <input
                  type="number"
                  name="spo2_risk_score"
                  min="0"
                  max="10"
                  step="0.1"
                  value={formData.spo2_risk_score}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>RR Risk Score</label>
                <input
                  type="number"
                  name="rr_risk_score"
                  min="0"
                  max="10"
                  step="0.1"
                  value={formData.rr_risk_score}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>Temp Risk Score</label>
                <input
                  type="number"
                  name="temp_risk_score"
                  min="0"
                  max="10"
                  step="0.1"
                  value={formData.temp_risk_score}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>Temperature (°C)</label>
                <input
                  type="number"
                  name="temperature"
                  min="0"
                  max="42"
                  step="0.1"
                  value={formData.temperature}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>Heart Rate (bpm)</label>
                <input
                  type="number"
                  name="heart_rate"
                  min="0"
                  max="200"
                  step="1"
                  value={formData.heart_rate}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>Age (years)</label>
                <input
                  type="number"
                  name="age"
                  min="0"
                  max="120"
                  step="1"
                  value={formData.age}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>Sex</label>
                <select name="sex" value={formData.sex} onChange={handleInputChange}>
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                </select>
              </div>

              <div className="form-group">
                <label>Age Group</label>
                <select name="age_group" value={formData.age_group} onChange={handleInputChange}>
                  <option value="pediatric">Pediatric</option>
                  <option value="adult">Adult</option>
                  <option value="senior">Senior</option>
                  <option value="elderly">Elderly</option>
                </select>
              </div>
            </div>

            <div className="button-group">
              <button type="submit" disabled={loading} className="btn-primary">
                {loading ? 'Predicting...' : 'Get Prediction'}
              </button>
              <button type="button" onClick={() => loadExample('healthy')} className="btn-secondary">
                Load Healthy Example
              </button>
              <button type="button" onClick={() => loadExample('high_risk')} className="btn-secondary">
                Load High-Risk Example
              </button>
            </div>
          </form>
        </section>

        {/* Results Section */}
        {result && (
          <section className="results-section">
            <h2>Prediction Results</h2>
            
            <div className="risk-card" style={{ backgroundColor: getRiskBgColor(result.risk_level) }}>
              <div className="risk-level" style={{ color: getRiskColor(result.risk_level) }}>
                {result.risk_level}
              </div>
              <div className="risk-details">
                <p><strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%</p>
                <p><strong>Uncertainty:</strong> {result.uncertainty.toFixed(6)}</p>
              </div>
            </div>

            <div className="probabilities">
              <h3>Risk Probabilities</h3>
              <div className="prob-bars">
                <div className="prob-bar">
                  <label>Low Risk</label>
                  <div className="bar">
                    <div className="fill" style={{
                      width: `${result.probabilities.low * 100}%`,
                      backgroundColor: '#10b981'
                    }}></div>
                  </div>
                  <span>{(result.probabilities.low * 100).toFixed(1)}%</span>
                </div>

                <div className="prob-bar">
                  <label>Medium Risk</label>
                  <div className="bar">
                    <div className="fill" style={{
                      width: `${result.probabilities.medium * 100}%`,
                      backgroundColor: '#f59e0b'
                    }}></div>
                  </div>
                  <span>{(result.probabilities.medium * 100).toFixed(1)}%</span>
                </div>

                <div className="prob-bar">
                  <label>High Risk</label>
                  <div className="bar">
                    <div className="fill" style={{
                      width: `${result.probabilities.high * 100}%`,
                      backgroundColor: '#ef4444'
                    }}></div>
                  </div>
                  <span>{(result.probabilities.high * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>

            <div className="clinical-action">
              <h3>Clinical Recommendation</h3>
              <p>{result.clinical_action}</p>
            </div>

            {result.top_contributing_features && (
              <div className="top-features">
                <h3>Top Contributing Factors</h3>
                <ul>
                  {result.top_contributing_features.map((feature, idx) => (
                    <li key={idx}>{idx + 1}. {feature}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}

        {/* History Section */}
        {history.length > 0 && (
          <section className="history-section">
            <h2>Prediction History</h2>
            <div className="history-table">
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Risk Level</th>
                    <th>Confidence</th>
                    <th>SpO2</th>
                    <th>RR</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((entry, idx) => (
                    <tr key={idx}>
                      <td>{entry.timestamp}</td>
                      <td>
                        <span className={`risk-badge risk-${entry.risk_level.toLowerCase()}`}>
                          {entry.risk_level}
                        </span>
                      </td>
                      <td>{entry.confidence}%</td>
                      <td>{entry.spo2}%</td>
                      <td>{entry.rr}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>
    </div>
  );
};

export default RespiratoryAgent;
```

### Step 2.5: Create Stylesheet

Create file: `respiratory-ui/src/components/RespiratoryAgent.css`

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu',
    'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  font-size: 32px;
  color: #333;
}

.server-status {
  font-size: 14px;
  padding: 8px 16px;
  background: #f0f9ff;
  border-radius: 6px;
  color: #0369a1;
  border: 1px solid #0ea5e9;
}

.error-box {
  background: #fee2e2;
  border: 1px solid #fca5a5;
  color: #7f1d1d;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.main {
  display: grid;
  gap: 30px;
}

section {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

section h2 {
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #667eea;
  padding-bottom: 10px;
}

section h3 {
  font-size: 18px;
  color: #555;
  margin-bottom: 15px;
}

/* Form Styling */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  font-size: 14px;
}

.form-group input,
.form-group select {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Button Styling */
.button-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 20px;
}

button {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e0e7ff;
  color: #667eea;
}

.btn-secondary:hover {
  background: #c7d2fe;
  transform: translateY(-2px);
}

/* Risk Card */
.risk-card {
  padding: 30px;
  border-radius: 12px;
  border-left: 5px solid;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.risk-card.low {
  border-color: #10b981;
}

.risk-card.medium {
  border-color: #f59e0b;
}

.risk-card.high {
  border-color: #ef4444;
}

.risk-level {
  font-size: 36px;
  font-weight: 700;
}

.risk-details {
  text-align: right;
}

.risk-details p {
  margin: 5px 0;
  color: #555;
}

/* Probabilities */
.probabilities {
  margin-bottom: 20px;
}

.prob-bars {
  display: grid;
  gap: 15px;
}

.prob-bar {
  display: grid;
  grid-template-columns: 120px 1fr 60px;
  gap: 10px;
  align-items: center;
}

.prob-bar label {
  font-weight: 600;
  font-size: 14px;
}

.prob-bar .bar {
  height: 30px;
  background: #f0f0f0;
  border-radius: 6px;
  overflow: hidden;
}

.prob-bar .fill {
  height: 100%;
  transition: width 0.3s;
}

.prob-bar span {
  font-weight: 600;
  color: #333;
}

/* Clinical Action */
.clinical-action {
  background: #f0fdf4;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #10b981;
  margin-bottom: 20px;
}

.clinical-action p {
  color: #166534;
  font-size: 15px;
  line-height: 1.6;
}

/* Top Features */
.top-features ul {
  list-style: none;
}

.top-features li {
  padding: 8px 0;
  color: #555;
  border-bottom: 1px solid #eee;
  padding-left: 20px;
}

.top-features li:last-child {
  border-bottom: none;
}

/* History Table */
.history-table {
  overflow-x: auto;
}

.history-table table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th {
  background: #f3f4f6;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #e5e7eb;
}

.history-table td {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.risk-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.risk-badge.risk-low {
  background: #d1fae5;
  color: #065f46;
}

.risk-badge.risk-medium {
  background: #fef3c7;
  color: #92400e;
}

.risk-badge.risk-high {
  background: #fee2e2;
  color: #7f1d1d;
}

/* Responsive */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 15px;
  }

  .header h1 {
    font-size: 24px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .button-group {
    flex-direction: column;
  }

  button {
    width: 100%;
  }

  .risk-card {
    flex-direction: column;
    text-align: center;
  }

  .risk-details {
    text-align: center;
    margin-top: 10px;
  }
}
```

### Step 2.6: Update App.js

Replace the content of `respiratory-ui/src/App.js`:

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

### Step 2.7: Update App.css

Replace the content of `respiratory-ui/src/App.css`:

```css
.App {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 0;
}
```

---

## Part 3: Run Everything Together

### Terminal 1: Start Flask Backend
```bash
cd /Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training
python api_server.py
```

**Expected output:**
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

### Terminal 2: Start React Frontend
```bash
cd /Users/taneeshkpatel/Desktop/OVGU_Projects/respiratory-ui
npm start
```

**Expected output:**
```
On Your Network:  http://192.168.x.x:3000

Local:            http://localhost:3000
```

### Terminal 3: Open Browser
```
http://localhost:3000
```

**You should see:**
- Beautiful UI with patient input form
- "Server Status: ✅ Connected"
- Ready to make predictions!

---

## Part 4: How to Use the React App

### Testing with Example Patients

1. Click **"Load Healthy Example"** button
   - Form populates with healthy patient data
   - Click **"Get Prediction"**
   - Result: **LOW** risk ✅

2. Click **"Load High-Risk Example"** button
   - Form populates with high-risk patient data
   - Click **"Get Prediction"**
   - Result: **HIGH** risk ✅

### Manual Entry

1. Fill in patient vitals manually
2. Click **"Get Prediction"**
3. See results with:
   - Risk level (LOW/MEDIUM/HIGH)
   - Confidence percentage
   - Probability bars
   - Clinical recommendation
   - Top contributing factors

### History

- Every prediction is added to **Prediction History** table
- Shows last 10 predictions
- Risk level color-coded (🟢 🟡 🔴)

---

## Part 5: Architecture Diagram

```
┌──────────────────────────────┐
│   React Frontend             │
│   (Port 3000)                │
│  - Patient Form              │
│  - Results Display           │
│  - History Table             │
│  - Status Indicator          │
└─────────────┬────────────────┘
              │ axios HTTP POST
              │ /predict
              ▼
┌──────────────────────────────┐
│   Flask API Server           │
│   (Port 5000)                │
│  /predict (single)           │
│  /batch (multiple)           │
│  /model-info (metadata)      │
│  /example-patients (test)    │
└─────────────┬────────────────┘
              │ Loads models
              │ from joblib
              ▼
┌──────────────────────────────┐
│   Respiratory Agent          │
│  - Pipeline                  │
│  - Ensemble                  │
│  - Model weights             │
└──────────────────────────────┘
```

---

## Part 6: Troubleshooting

### "Server Status: ❌ Disconnected"
```bash
# Make sure Flask is running in Terminal 1
# Check: http://localhost:5000/health
curl http://localhost:5000/health
```

### Port 3000 or 5000 Already in Use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### Prediction Button Not Working
1. Check browser console (F12)
2. Check Flask terminal for errors
3. Verify all required fields are filled

### CORS Error
```
This should be fixed by flask-cors, but if not:
- Ensure api_server.py has CORS(app)
- Restart Flask server
```

---

## Part 7: Production Deployment

### Deploy React to Netlify (Free)
```bash
cd respiratory-ui
npm run build
# Follow: https://netlify.com/drop (drag & drop build folder)
```

### Deploy Flask to Heroku (Free/Paid)
```bash
cd agent-training
git init
git add .
git commit -m "initial"
heroku create
heroku config:set PYTHONUNBUFFERED=1
git push heroku main
```

### Deploy Both to AWS, GCP, Azure
See documentation for each platform.

---

## Summary

✅ **You now have:**
- React frontend with beautiful UI
- Flask REST API backend
- Connected to your trained respiratory agent
- Ready for production use!

**Next Steps:**
1. Start both servers (Terminals 1 & 2)
2. Open browser to localhost:3000
3. Test with example patients
4. Customize styling/features as needed
5. Deploy to production when ready
