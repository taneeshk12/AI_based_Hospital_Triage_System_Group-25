# 🎨 React UI Integration Guide

## Dual-Model Integration for React Frontend

Your existing React UI can now use **both the respiratory and general health models**. This guide shows how to integrate both into your UI.

---

## API Base URL Configuration

Update your API configuration file (e.g., `src/config/api.js` or `.env`):

```javascript
// src/config/api.js
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Respiratory endpoints
export const RESPIRATORY_ENDPOINTS = {
  PREDICT: `${API_BASE_URL}/respiratory/predict`,
  BATCH: `${API_BASE_URL}/respiratory/batch`,
  MODEL_INFO: `${API_BASE_URL}/respiratory/model-info`,
  EXAMPLES: `${API_BASE_URL}/respiratory/example-patients`,
};

// General health endpoints
export const GENERAL_ENDPOINTS = {
  PREDICT: `${API_BASE_URL}/general/predict`,
  BATCH: `${API_BASE_URL}/general/batch`,
  MODEL_INFO: `${API_BASE_URL}/general/model-info`,
  EXAMPLE: `${API_BASE_URL}/general/example-patient`,
};

// Health check
export const HEALTH_CHECK = `${API_BASE_URL}/health`;
```

---

## API Service Module

Create a service module to handle API calls:

```javascript
// src/services/apiService.js
import { RESPIRATORY_ENDPOINTS, GENERAL_ENDPOINTS, HEALTH_CHECK } from '../config/api';

class APIService {
  // ==================== HEALTH ====================
  
  async checkHealth() {
    try {
      const response = await fetch(HEALTH_CHECK);
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      return { status: 'error' };
    }
  }

  // ==================== RESPIRATORY ====================

  async predictRespiratory(patientData) {
    try {
      const response = await fetch(RESPIRATORY_ENDPOINTS.PREDICT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patientData),
      });
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Respiratory prediction error:', error);
      return { status: 'error', error_message: error.message };
    }
  }

  async batchPredictRespiratory(patientsList) {
    try {
      const response = await fetch(RESPIRATORY_ENDPOINTS.BATCH, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patientsList),
      });
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Respiratory batch prediction error:', error);
      return { error: error.message };
    }
  }

  async getRespiratoryModelInfo() {
    try {
      const response = await fetch(RESPIRATORY_ENDPOINTS.MODEL_INFO);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch respiratory model info:', error);
      return {};
    }
  }

  async getRespiratoryExamples() {
    try {
      const response = await fetch(RESPIRATORY_ENDPOINTS.EXAMPLES);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch respiratory examples:', error);
      return {};
    }
  }

  // ==================== GENERAL HEALTH ====================

  async predictGeneral(patientData) {
    try {
      const response = await fetch(GENERAL_ENDPOINTS.PREDICT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patientData),
      });
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('General health prediction error:', error);
      return { status: 'error', error_message: error.message };
    }
  }

  async batchPredictGeneral(patientsList) {
    try {
      const response = await fetch(GENERAL_ENDPOINTS.BATCH, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patientsList),
      });
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('General health batch prediction error:', error);
      return { error: error.message };
    }
  }

  async getGeneralModelInfo() {
    try {
      const response = await fetch(GENERAL_ENDPOINTS.MODEL_INFO);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch general model info:', error);
      return {};
    }
  }

  async getGeneralExample() {
    try {
      const response = await fetch(GENERAL_ENDPOINTS.EXAMPLE);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch general example:', error);
      return {};
    }
  }
}

export default new APIService();
```

---

## React Components

### Respiratory Prediction Component

```jsx
// src/components/RespiratoryPredictor.jsx
import React, { useState } from 'react';
import apiService from '../services/apiService';

export function RespiratoryPredictor() {
  const [patientData, setPatientData] = useState({
    spo2: 95,
    respiratory_rate: 18,
    temperature: 37.2,
    heart_rate: 72,
    age: 45,
    sex: 'M',
    age_group: '30-50',
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setPatientData(prev => ({
      ...prev,
      [name]: isNaN(value) ? value : parseFloat(value),
    }));
  };

  const handlePredict = async () => {
    setLoading(true);
    try {
      const prediction = await apiService.predictRespiratory(patientData);
      setResult(prediction);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'LOW': return '#2ecc71'; // Green
      case 'MEDIUM': return '#f39c12'; // Orange
      case 'HIGH': return '#e74c3c'; // Red
      default: return '#95a5a6'; // Gray
    }
  };

  return (
    <div className="card">
      <h2>🫁 Respiratory Risk Predictor</h2>
      
      <div className="input-grid">
        {Object.entries(patientData).map(([key, value]) => (
          <div key={key} className="input-group">
            <label>{key.replace(/_/g, ' ')}:</label>
            <input
              type={typeof value === 'number' ? 'number' : 'text'}
              name={key}
              value={value}
              onChange={handleInputChange}
              disabled={loading}
            />
          </div>
        ))}
      </div>

      <button 
        onClick={handlePredict}
        disabled={loading}
        className="btn-predict"
      >
        {loading ? 'Predicting...' : 'Predict Risk'}
      </button>

      {result && result.status === 'success' && (
        <div className="result-card">
          <div className="risk-badge" style={{ backgroundColor: getRiskColor(result.risk_level) }}>
            {result.risk_level}
          </div>
          
          <div className="result-details">
            <p><strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}% ({result.confidence_level})</p>
            <p><strong>Uncertainty:</strong> {(result.uncertainty * 100).toFixed(2)}%</p>
            <p><strong>Action:</strong> {result.clinical_action}</p>
            
            <div className="probabilities">
              <h4>Class Probabilities</h4>
              <ul>
                <li>LOW: {(result.probabilities.low * 100).toFixed(1)}%</li>
                <li>MEDIUM: {(result.probabilities.medium * 100).toFixed(1)}%</li>
                <li>HIGH: {(result.probabilities.high * 100).toFixed(1)}%</li>
              </ul>
            </div>

            {result.top_contributing_features?.length > 0 && (
              <div className="features">
                <h4>Top Contributing Features</h4>
                <ul>
                  {result.top_contributing_features.map(feat => (
                    <li key={feat}>{feat}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.clinical_alert && (
              <div className="alert alert-warning">
                ⚠️ Clinical Alert: Low confidence or high uncertainty. Review result carefully.
              </div>
            )}
          </div>
        </div>
      )}

      {result?.status === 'error' && (
        <div className="alert alert-error">
          Error: {result.error_message}
        </div>
      )}
    </div>
  );
}
```

### General Health Prediction Component

```jsx
// src/components/GeneralHealthPredictor.jsx
import React, { useState } from 'react';
import apiService from '../services/apiService';

export function GeneralHealthPredictor() {
  const [patientData, setPatientData] = useState({
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
    sex: 'M',
    country: 'USA',
    clinical_notes: 'Patient presents with chest pain and elevated blood pressure.',
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setPatientData(prev => ({
      ...prev,
      [name]: isNaN(value) ? value : parseFloat(value),
    }));
  };

  const handlePredict = async () => {
    setLoading(true);
    try {
      const prediction = await apiService.predictGeneral(patientData);
      setResult(prediction);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'LOW_RISK': return '#2ecc71'; // Green
      case 'MID_RISK': return '#f39c12'; // Orange
      case 'HIGH_RISK': return '#e74c3c'; // Red
      default: return '#95a5a6'; // Gray
    }
  };

  return (
    <div className="card">
      <h2>🏥 General Health ED Triage Predictor</h2>
      
      <div className="input-grid">
        {Object.entries(patientData).map(([key, value]) => (
          <div key={key} className="input-group">
            <label>{key.replace(/_/g, ' ')}:</label>
            {key === 'clinical_notes' ? (
              <textarea
                name={key}
                value={value}
                onChange={handleInputChange}
                disabled={loading}
                rows={3}
              />
            ) : (
              <input
                type={typeof value === 'number' ? 'number' : 'text'}
                name={key}
                value={value}
                onChange={handleInputChange}
                disabled={loading}
              />
            )}
          </div>
        ))}
      </div>

      <button 
        onClick={handlePredict}
        disabled={loading}
        className="btn-predict"
      >
        {loading ? 'Predicting...' : 'Predict Risk'}
      </button>

      {result && result.status === 'success' && (
        <div className="result-card">
          <div className="risk-badge" style={{ backgroundColor: getRiskColor(result.risk_level) }}>
            {result.risk_level}
          </div>
          
          <div className="result-details">
            <p><strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}% ({result.confidence_level})</p>
            <p><strong>Action:</strong> {result.clinical_action}</p>
            
            <div className="importance-scores">
              <h4>Feature Importance</h4>
              <p>Tabular Features: {(result.tabular_importance * 100).toFixed(1)}%</p>
              <p>Clinical Embeddings: {(result.embedding_importance * 100).toFixed(1)}%</p>
            </div>

            <div className="probabilities">
              <h4>Risk Probabilities</h4>
              <ul>
                <li>LOW_RISK: {(result.probabilities.low_risk * 100).toFixed(1)}%</li>
                <li>MID_RISK: {(result.probabilities.mid_risk * 100).toFixed(1)}%</li>
                <li>HIGH_RISK: {(result.probabilities.high_risk * 100).toFixed(1)}%</li>
              </ul>
            </div>

            {result.top_contributing_features?.length > 0 && (
              <div className="features">
                <h4>Top Contributing Features</h4>
                <ul>
                  {result.top_contributing_features.map(feat => (
                    <li key={feat}>{feat}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.clinical_alert && (
              <div className="alert alert-warning">
                ⚠️ Clinical Alert: Review with caution. Model confidence is moderate.
              </div>
            )}
          </div>
        </div>
      )}

      {result?.status === 'error' && (
        <div className="alert alert-error">
          Error: {result.error_message}
        </div>
      )}
    </div>
  );
}
```

### Dual-Model Dashboard Component

```jsx
// src/components/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { RespiratoryPredictor } from './RespiratoryPredictor';
import { GeneralHealthPredictor } from './GeneralHealthPredictor';
import apiService from '../services/apiService';

export function Dashboard() {
  const [activeTab, setActiveTab] = useState('respiratory');
  const [health, setHealth] = useState({ agents: {} });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      const result = await apiService.checkHealth();
      setHealth(result);
      setLoading(false);
    };
    checkHealth();
  }, []);

  if (loading) {
    return <div className="loading">Initializing agents...</div>;
  }

  const respiratoryHealthy = health.agents?.respiratory;
  const generalHealthy = health.agents?.general;

  return (
    <div className="dashboard">
      <h1>🏥 Multi-Agent Diagnostic System</h1>
      
      <div className="health-status">
        <span className={`status ${respiratoryHealthy ? 'healthy' : 'unhealthy'}`}>
          🫁 Respiratory: {respiratoryHealthy ? '✓ Ready' : '✗ Unavailable'}
        </span>
        <span className={`status ${generalHealthy ? 'healthy' : 'unhealthy'}`}>
          🏥 General Health: {generalHealthy ? '✓ Ready' : '✗ Unavailable'}
        </span>
      </div>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'respiratory' ? 'active' : ''}`}
          onClick={() => setActiveTab('respiratory')}
          disabled={!respiratoryHealthy}
        >
          🫁 Respiratory Model
        </button>
        <button 
          className={`tab ${activeTab === 'general' ? 'active' : ''}`}
          onClick={() => setActiveTab('general')}
          disabled={!generalHealthy}
        >
          🏥 General Health Model
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'respiratory' && <RespiratoryPredictor />}
        {activeTab === 'general' && <GeneralHealthPredictor />}
      </div>
    </div>
  );
}
```

---

## Styling (CSS)

```css
/* src/styles/Dashboard.css */
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.health-status {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.status {
  padding: 10px 15px;
  border-radius: 5px;
  font-weight: bold;
}

.status.healthy {
  background-color: #d4edda;
  color: #155724;
}

.status.unhealthy {
  background-color: #f8d7da;
  color: #721c24;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #ddd;
}

.tab {
  padding: 10px 20px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  color: #666;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
}

.tab.active {
  color: #0066cc;
  border-bottom-color: #0066cc;
}

.tab:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.card {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.input-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group label {
  font-weight: bold;
  margin-bottom: 5px;
  text-transform: capitalize;
}

.input-group input,
.input-group textarea {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.btn-predict {
  background-color: #0066cc;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: background-color 0.3s;
}

.btn-predict:hover:not(:disabled) {
  background-color: #0052a3;
}

.btn-predict:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.result-card {
  background: #f9f9f9;
  border: 2px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
}

.risk-badge {
  display: inline-block;
  padding: 10px 20px;
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 15px;
}

.result-details p {
  margin: 10px 0;
  font-size: 16px;
}

.probabilities,
.features,
.importance-scores {
  margin-top: 15px;
}

.probabilities h4,
.features h4,
.importance-scores h4 {
  margin-bottom: 10px;
  color: #333;
}

.probabilities ul,
.features ul {
  list-style-position: inside;
  margin: 10px 0;
}

.probabilities li,
.features li {
  margin: 5px 0;
  color: #666;
}

.alert {
  padding: 15px;
  border-radius: 4px;
  margin-top: 15px;
}

.alert-error {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

.alert-warning {
  background-color: #fff3cd;
  border: 1px solid #ffeeba;
  color: #856404;
}

.loading {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #666;
}
```

---

## Environment Configuration

Create `.env` file in your React app root:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=30000
```

---

## Testing

```bash
# Start API server
python api_server.py

# Start React dev server (in your React app directory)
npm start

# Your app should be available at http://localhost:3000
```

---

## Next Steps

1. **Install dependencies** if using transformers for embeddings:
   ```bash
   pip install transformers torch
   ```

2. **Ensure model files exist** in the working directory:
   - Respiratory: `respiratory_rf_pipeline.joblib`, `respiratory_rf_ensemble.joblib`
   - General: `multimodal_lightgbm_model.pkl`, `shap_tree_explainer.pkl`, `multimodal_model_metadata.json`

3. **Test both endpoints** using the provided example components

4. **Deploy** using Docker or production WSGI server (Gunicorn)

---

## Troubleshooting

### "General Health Agent not loaded"
- Check if `multimodal_lightgbm_model.pkl` exists
- Check server logs for loading errors
- Ensure TensorFlow/PyTorch are properly installed

### "CUDA not available" error
- General Health Agent can work on CPU, but will be slower
- For GPU support, ensure CUDA-compatible libraries are installed

### Batch predictions timing out
- Increase API timeout in `.env`
- Consider processing smaller batches
- Use production WSGI server with worker threads
