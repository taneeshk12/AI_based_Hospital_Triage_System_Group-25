import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [patientData, setPatientData] = useState({
    spo2: 97,
    respiratory_rate: 16,
    temperature: 36.8,
    heart_rate: 70,
    age: 40,
    sex: 'M',
    age_group: '30-50'
  });

  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState(false);
  const [history, setHistory] = useState([]);

  // Check API health on mount
  useEffect(() => {
    checkApiHealth();
    const interval = setInterval(checkApiHealth, 10000); // Check every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await axios.get(`${API_URL}/health`);
      setApiStatus(response.data.model_loaded);
    } catch (err) {
      setApiStatus(false);
      console.error('API not available:', err.message);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setPatientData(prev => ({
      ...prev,
      [name]: isNaN(value) ? value : parseFloat(value)
    }));
  };

  const handlePredict = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/predict`, patientData);
      
      if (response.data.status === 'success') {
        setPrediction(response.data);
        setHistory(prev => [response.data, ...prev].slice(0, 5));
      } else {
        setError(response.data.error_message || 'Prediction failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Connection error. Is the API running?');
    } finally {
      setLoading(false);
    }
  };

  const loadHealthyExample = () => {
    setPatientData({
      spo2: 97,
      respiratory_rate: 16,
      temperature: 36.8,
      heart_rate: 70,
      age: 40,
      sex: 'M',
      age_group: '30-50'
    });
    setPrediction(null);
  };

  const loadHighRiskExample = () => {
    setPatientData({
      spo2: 85,
      respiratory_rate: 32,
      temperature: 39.2,
      heart_rate: 115,
      age: 65,
      sex: 'F',
      age_group: '60+'
    });
    setPrediction(null);
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'LOW': return '#10b981';
      case 'MEDIUM': return '#f59e0b';
      case 'HIGH': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1>🫁 Respiratory Risk Assessment</h1>
          <p>AI-powered respiratory health monitoring system</p>
          <div className="api-status">
            <span className={`status-indicator ${apiStatus ? 'connected' : 'disconnected'}`}></span>
            <span>
              {apiStatus ? '✅ API Connected' : '❌ API Disconnected - Check backend'}
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-container">
        <div className="content-grid">
          {/* Input Form */}
          <section className="form-section">
            <h2>Patient Vital Signs</h2>
            
            <div className="form-grid">
              {/* Numeric Inputs */}
              <div className="form-group">
                <label>SpO₂ (%)</label>
                <input
                  type="number"
                  name="spo2"
                  value={patientData.spo2}
                  onChange={handleInputChange}
                  min="50"
                  max="100"
                  step="0.1"
                />
              </div>

              <div className="form-group">
                <label>Respiratory Rate (breaths/min)</label>
                <input
                  type="number"
                  name="respiratory_rate"
                  value={patientData.respiratory_rate}
                  onChange={handleInputChange}
                  min="0"
                  max="60"
                  step="0.1"
                />
              </div>

              <div className="form-group">
                <label>Temperature (°C)</label>
                <input
                  type="number"
                  name="temperature"
                  value={patientData.temperature}
                  onChange={handleInputChange}
                  min="0"
                  max="42"
                  step="0.1"
                />
              </div>

              <div className="form-group">
                <label>Heart Rate (bpm)</label>
                <input
                  type="number"
                  name="heart_rate"
                  value={patientData.heart_rate}
                  onChange={handleInputChange}
                  min="0"
                  max="200"
                  step="0.1"
                />
              </div>

              <div className="form-group">
                <label>Age (years)</label>
                <input
                  type="number"
                  name="age"
                  value={patientData.age}
                  onChange={handleInputChange}
                  min="0"
                  max="120"
                  step="1"
                />
              </div>

              <div className="form-group">
                <label>Sex</label>
                <select
                  name="sex"
                  value={patientData.sex}
                  onChange={handleInputChange}
                >
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                  <option value="O">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label>Age Group</label>
                <select
                  name="age_group"
                  value={patientData.age_group}
                  onChange={handleInputChange}
                >
                  <option value="0-12">0-12</option>
                  <option value="13-19">13-19</option>
                  <option value="20-30">20-30</option>
                  <option value="30-50">30-50</option>
                  <option value="50-60">50-60</option>
                  <option value="60+">60+</option>
                </select>
              </div>
            </div>

            {/* Buttons */}
            <div className="button-group">
              <button
                className="btn btn-primary"
                onClick={handlePredict}
                disabled={loading || !apiStatus}
              >
                {loading ? '⏳ Analyzing...' : '🔍 Predict Risk Level'}
              </button>

              <button
                className="btn btn-secondary"
                onClick={loadHealthyExample}
                disabled={loading}
              >
                📊 Healthy Example
              </button>

              <button
                className="btn btn-secondary"
                onClick={loadHighRiskExample}
                disabled={loading}
              >
                ⚠️ High-Risk Example
              </button>
            </div>
          </section>

          {/* Results Section */}
          <section className="results-section">
            {error && (
              <div className="alert alert-error">
                <strong>Error:</strong> {error}
              </div>
            )}

            {!apiStatus && (
              <div className="alert alert-warning">
                <strong>⚠️ Backend Not Connected</strong>
                <p>Please start the API server on port 8000</p>
              </div>
            )}

            {prediction && (
              <div className="prediction-card">
                <h2>Prediction Results</h2>

                {/* Risk Level Display */}
                <div className="risk-display" style={{ borderColor: getRiskColor(prediction.risk_level) }}>
                  <div className="risk-level" style={{ color: getRiskColor(prediction.risk_level) }}>
                    {prediction.risk_level}
                  </div>
                  <div className="risk-class">Risk Class: {prediction.risk_class}</div>
                </div>

                {/* Confidence & Alert */}
                <div className="confidence-section">
                  <div className="confidence-item">
                    <span className="label">Confidence Level:</span>
                    <span className={`badge badge-${prediction.confidence_level.toLowerCase()}`}>
                      {prediction.confidence_level}
                    </span>
                  </div>
                  <div className="confidence-item">
                    <span className="label">Confidence Score:</span>
                    <span className="value">{(prediction.confidence * 100).toFixed(1)}%</span>
                  </div>
                  {prediction.clinical_alert && (
                    <div className="alert-badge">⚠️ Clinical Alert</div>
                  )}
                </div>

                {/* Probabilities */}
                <div className="probabilities">
                  <h3>Risk Probabilities</h3>
                  
                  <div className="probability-item">
                    <div className="prob-label">
                      <span>🟢 LOW</span>
                      <span>{(prediction.probabilities.low * 100).toFixed(1)}%</span>
                    </div>
                    <div className="prob-bar">
                      <div
                        className="prob-fill"
                        style={{
                          width: `${prediction.probabilities.low * 100}%`,
                          backgroundColor: '#10b981'
                        }}
                      ></div>
                    </div>
                  </div>

                  <div className="probability-item">
                    <div className="prob-label">
                      <span>🟡 MEDIUM</span>
                      <span>{(prediction.probabilities.medium * 100).toFixed(1)}%</span>
                    </div>
                    <div className="prob-bar">
                      <div
                        className="prob-fill"
                        style={{
                          width: `${prediction.probabilities.medium * 100}%`,
                          backgroundColor: '#f59e0b'
                        }}
                      ></div>
                    </div>
                  </div>

                  <div className="probability-item">
                    <div className="prob-label">
                      <span>🔴 HIGH</span>
                      <span>{(prediction.probabilities.high * 100).toFixed(1)}%</span>
                    </div>
                    <div className="prob-bar">
                      <div
                        className="prob-fill"
                        style={{
                          width: `${prediction.probabilities.high * 100}%`,
                          backgroundColor: '#ef4444'
                        }}
                      ></div>
                    </div>
                  </div>
                </div>

                {/* Clinical Action */}
                <div className="clinical-section">
                  <h3>Clinical Action</h3>
                  <p className="clinical-action">{prediction.clinical_action}</p>
                </div>

                {/* Top Features */}
                {prediction.top_contributing_features && (
                  <div className="features-section">
                    <h3>Top Contributing Features</h3>
                    <ul className="features-list">
                      {prediction.top_contributing_features.map((feature, idx) => (
                        <li key={idx}>
                          <span className="feature-rank">{idx + 1}</span>
                          <span className="feature-name">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Uncertainty */}
                <div className="uncertainty-section">
                  <span className="label">Model Uncertainty:</span>
                  <span className="value">{(prediction.uncertainty * 100).toFixed(2)}%</span>
                </div>

                {/* Timestamp */}
                <div className="timestamp">
                  <small>Prediction made: {new Date(prediction.timestamp).toLocaleString()}</small>
                </div>
              </div>
            )}

            {!prediction && !error && (
              <div className="empty-state">
                <p>👈 Fill in patient data and click "Predict Risk Level"</p>
                <p>or use the example buttons to test the system</p>
              </div>
            )}
          </section>
        </div>

        {/* History Section */}
        {history.length > 0 && (
          <section className="history-section">
            <h2>Recent Predictions</h2>
            <div className="history-grid">
              {history.map((item, idx) => (
                <div key={idx} className="history-card" style={{ borderLeft: `4px solid ${getRiskColor(item.risk_level)}` }}>
                  <div className="history-risk" style={{ color: getRiskColor(item.risk_level) }}>
                    {item.risk_level}
                  </div>
                  <div className="history-confidence">
                    Confidence: {(item.confidence * 100).toFixed(0)}%
                  </div>
                  <div className="history-time">
                    {new Date(item.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>🫁 Respiratory Risk Assessment System • Built with React & Flask • API: {API_URL}</p>
      </footer>
    </div>
  );
}

export default App;
