import React, { useState } from 'react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts';

const CLINICAL_RANGES = {
  spo2: { min: 70, max: 100, step: 1 },
  respiratory_rate: { min: 5, max: 50, step: 1 },
  temperature: { min: 34.0, max: 42.0, step: 0.1 },
  heart_rate: { min: 30, max: 200, step: 1 },
  systolic_bp: { min: 60, max: 240, step: 1 },
  diastolic_bp: { min: 30, max: 140, step: 1 },
  wbc: { min: 1.0, max: 50.0, step: 0.1 },
  hemoglobin: { min: 5.0, max: 25.0, step: 0.1 },
  glucose: { min: 20, max: 600, step: 5 },
  troponin: { min: 0.0, max: 5.0, step: 0.01 },
  lactate: { min: 0.2, max: 20.0, step: 0.1 },
  creatinine: { min: 0.1, max: 15.0, step: 0.1 },
};

const PARAM_LABELS = {
  spo2: 'SpO₂ (%)',
  respiratory_rate: 'Resp Rate (/min)',
  temperature: 'Temperature (°C)',
  heart_rate: 'Heart Rate (bpm)',
  systolic_bp: 'Systolic BP (mmHg)',
  diastolic_bp: 'Diastolic BP (mmHg)',
  wbc: 'WBC (k/µL)',
  hemoglobin: 'Hemoglobin (g/dL)',
  glucose: 'Glucose (mg/dL)',
  troponin: 'Troponin (ng/mL)',
  lactate: 'Lactate (mmol/L)',
  creatinine: 'Creatinine (mg/dL)',
};

export default function SimulatorPage({
  predictions, patientData, setPatientData,
  baselineData, setBaselineData,
  baselinePredictions, setBaselinePredictions,
  isWhatIfMode, setIsWhatIfMode,
  sensitivityData, setSensitivityData,
  sensitivityParam, setSensitivityParam,
  insightsTab, setInsightsTab,
  debouncedPredict, debouncedSweep, runSensitivitySweep,
  loading, setLoading, setError,
  patientName, currentPatientId,
  API_URL, axios,
  setPredictions, setAggregation, setLlmSummary, setFullReport, setFeedbackStatus,
}) {
  if (!predictions) {
    return (
      <div className="page-container animate-fade-in">
        <div className="empty-state glass-panel" style={{ margin: 'auto', maxWidth: 600 }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎛️</div>
          <h2>Simulator Not Available</h2>
          <p>Please complete a <strong>Triage Intake</strong> analysis first, then return here to explore what-if scenarios.</p>
        </div>
      </div>
    );
  }

  const handleEnterSim = () => {
    setBaselineData({ ...patientData });
    setBaselinePredictions(predictions);
    runSensitivitySweep(patientData, sensitivityParam);
    setIsWhatIfMode(true);
  };

  const handleExitSim = () => {
    setPatientData({ ...baselineData });
    const restoredData = { ...baselineData };
    setBaselineData(null);
    setBaselinePredictions(null);
    setSensitivityData([]);
    setIsWhatIfMode(false);
    setLoading(true);
    setError(null);
    axios.post(`${API_URL}/hcai/analyze`, {
      ...restoredData,
      patient_id: currentPatientId,
      patient_name: patientName.trim() || 'Anonymous',
    }).then(response => {
      if (response.data.status === 'success') {
        setPredictions(response.data.predictions);
        setAggregation(response.data.aggregation);
        setLlmSummary(response.data.hcai_report?.llm_interpretation || null);
        setFullReport(response.data.hcai_report || null);
        setFeedbackStatus(null);
      }
    }).catch(err => console.error('Restore error:', err))
      .finally(() => setLoading(false));
  };

  const processRiskShiftData = () => {
    if (!baselinePredictions || !predictions) return [];
    const getHighRiskProb = (agentData) => {
      if (!agentData || agentData.status === 'error') return 0;
      const probs = agentData.probabilities;
      if (!probs) return 0;
      return Math.round((probs.high ?? probs.high_risk ?? 0) * 100);
    };
    return [
      { name: 'Respiratory', Baseline: getHighRiskProb(baselinePredictions.respiratory), Simulated: getHighRiskProb(predictions.respiratory) },
      { name: 'Cardiac', Baseline: getHighRiskProb(baselinePredictions.cardiac), Simulated: getHighRiskProb(predictions.cardiac) },
      { name: 'Sepsis', Baseline: getHighRiskProb(baselinePredictions.sepsis), Simulated: getHighRiskProb(predictions.sepsis) },
      { name: 'General', Baseline: getHighRiskProb(baselinePredictions.general), Simulated: getHighRiskProb(predictions.general) },
    ];
  };

  const renderSlider = (label, name, value, unit) => {
    const config = CLINICAL_RANGES[name];
    if (!config) return null;
    let deltaText = '';
    let deltaClass = '';
    if (baselineData && baselineData[name] !== undefined) {
      const diff = value - baselineData[name];
      if (!isNaN(diff) && diff !== 0) {
        const step = config.step ?? 1;
        const formattedDiff = diff > 0 ? `+${diff.toFixed(step % 1 === 0 ? 0 : 1)}` : `${diff.toFixed(step % 1 === 0 ? 0 : 1)}`;
        deltaText = `${formattedDiff}${unit ? ' ' + unit : ''}`;
        deltaClass = name === 'spo2' ? (diff > 0 ? 'delta-good' : 'delta-bad') : (diff > 0 ? 'delta-bad' : 'delta-good');
      }
    }
    return (
      <div className="sim-slider-group" key={name}>
        <div className="sim-slider-header">
          <span className="sim-slider-label">{label}</span>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            {deltaText && <span className={`delta-badge ${deltaClass}`}>{deltaText}</span>}
            <span className="sim-slider-value">{typeof value === 'number' ? value.toFixed(config.step % 1 === 0 ? 0 : 1) : value} <span style={{ opacity: 0.5, fontSize: '0.78rem' }}>{unit}</span></span>
          </div>
        </div>
        <input
          type="range"
          name={name}
          min={config.min}
          max={config.max}
          step={config.step}
          value={value}
          onChange={(e) => {
            const val = parseFloat(e.target.value);
            const updatedData = { ...patientData, [name]: val };
            setPatientData(updatedData);
            debouncedPredict(updatedData);
            if (name === sensitivityParam) {
              debouncedSweep(updatedData, name);
            }
          }}
          className="whatif-slider"
        />
        <div className="sim-slider-range-labels">
          <span>{config.min}{unit}</span>
          <span>{config.max}{unit}</span>
        </div>
      </div>
    );
  };

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">What-If Simulator</h2>
          <p className="page-subtitle">Adjust patient vitals in real-time and observe how risk scores respond.</p>
        </div>
        {!isWhatIfMode ? (
          <button className="btn primary" onClick={handleEnterSim} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2" fill="none"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            Enter Simulation
          </button>
        ) : (
          <button className="btn outline" onClick={handleExitSim} style={{ borderColor: '#ef4444', color: '#ef4444', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2" fill="none"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            Exit & Restore Baseline
          </button>
        )}
      </div>

      {!isWhatIfMode ? (
        <div className="sim-inactive-prompt glass-panel">
          <div style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.7 }}>🎛️</div>
          <h3>Ready to Simulate</h3>
          <p>Click <strong>Enter Simulation</strong> above to start adjusting vitals and observe real-time risk shifts. Baseline will be saved and restored on exit.</p>
        </div>
      ) : (
        <div className="sim-active-layout">
          {/* Left: Sliders */}
          <div className="sim-sliders-panel glass-panel">
            <div className="sim-panel-title">
              <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2" fill="none"><circle cx="12" cy="12" r="3"/><line x1="3" y1="12" x2="9" y2="12"/><line x1="15" y1="12" x2="21" y2="12"/><line x1="12" y1="3" x2="12" y2="9"/><line x1="12" y1="15" x2="12" y2="21"/></svg>
              Adjust Parameters
            </div>
            <div className="sim-sliders-grid">
              {renderSlider('SpO₂', 'spo2', patientData.spo2, '%')}
              {renderSlider('Resp Rate', 'respiratory_rate', patientData.respiratory_rate, '/min')}
              {renderSlider('Heart Rate', 'heart_rate', patientData.heart_rate, 'bpm')}
              {renderSlider('Systolic BP', 'systolic_bp', patientData.systolic_bp, 'mmHg')}
              {renderSlider('Temperature', 'temperature', patientData.temperature, '°C')}
              {renderSlider('WBC', 'wbc', patientData.wbc, 'k/µL')}
              {renderSlider('Lactate', 'lactate', patientData.lactate, 'mmol/L')}
              {renderSlider('Troponin', 'troponin', patientData.troponin, 'ng/mL')}
              {renderSlider('Glucose', 'glucose', patientData.glucose, 'mg/dL')}
            </div>
          </div>

          {/* Right: Charts */}
          <div className="sim-charts-panel">
            {/* Tab switch */}
            <div className="tab-navigation" style={{ marginBottom: '1rem' }}>
              <button className={`tab-btn ${insightsTab === 'subsystem' ? 'active' : ''}`} onClick={() => setInsightsTab('subsystem')} type="button">
                <span>Risk Shift</span>
              </button>
              <button className={`tab-btn ${insightsTab === 'sensitivity' ? 'active' : ''}`} onClick={() => setInsightsTab('sensitivity')} type="button">
                <span>Sensitivity Curve</span>
              </button>
            </div>

            {insightsTab === 'subsystem' && (
              <div className="glass-panel sim-chart-card animate-fade-in">
                <div className="sim-chart-title">Sub-System Risk Shift (Baseline vs Simulated)</div>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={processRiskShiftData()} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                    <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} />
                    <YAxis domain={[0, 100]} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} unit="%" />
                    <Tooltip contentStyle={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'var(--text-primary)' }} formatter={v => `${v}%`} />
                    <Legend wrapperStyle={{ color: 'var(--text-muted)', fontSize: '12px' }} />
                    <Bar dataKey="Baseline" fill="#334155" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Simulated" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {insightsTab === 'sensitivity' && (
              <div className="glass-panel sim-chart-card animate-fade-in">
                <div className="sim-chart-title" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
                  <span>Sensitivity Curve</span>
                  <select
                    value={sensitivityParam}
                    onChange={e => {
                      setSensitivityParam(e.target.value);
                      runSensitivitySweep(patientData, e.target.value);
                    }}
                    style={{ fontSize: '0.8rem', padding: '4px 8px', borderRadius: '6px', border: '1px solid var(--border-color)', background: 'var(--input-bg)', color: 'inherit', cursor: 'pointer' }}
                  >
                    {Object.entries(PARAM_LABELS).map(([key, label]) => (
                      <option key={key} value={key}>{label}</option>
                    ))}
                  </select>
                </div>
                {sensitivityData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={260}>
                    <AreaChart data={sensitivityData} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
                      <defs>
                        <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                      <XAxis dataKey="val" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} label={{ value: PARAM_LABELS[sensitivityParam], fill: 'var(--text-muted)', fontSize: 11, position: 'insideBottom', offset: -5 }} height={45} />
                      <YAxis domain={[0, 100]} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} unit="%" />
                      <Tooltip contentStyle={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'var(--text-primary)' }} formatter={v => [`${v}%`, 'Risk Score']} />
                      <Area type="monotone" dataKey="risk" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorRisk)" />
                      <ReferenceLine x={patientData[sensitivityParam]} stroke="#ef4444" strokeWidth={2} strokeDasharray="3 3" label={{ value: 'CURRENT', fill: '#ef4444', fontSize: 9, position: 'top' }} />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div style={{ textAlign: 'center', padding: '3rem', opacity: 0.5 }}>Loading sensitivity data...</div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
