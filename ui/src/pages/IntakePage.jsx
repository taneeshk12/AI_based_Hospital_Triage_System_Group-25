import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  User, 
  HeartPulse, 
  TestTubes, 
  MessageSquare, 
  CheckCircle2, 
  AlertTriangle, 
  Play, 
  Stethoscope, 
  Beaker,
  Save,
  Plus
} from 'lucide-react';

const CLINICAL_RANGES = {
  age: { min: 0, max: 120, step: 1 },
  spo2: { min: 70, max: 100, step: 1 },
  respiratory_rate: { min: 5, max: 50, step: 1 },
  temperature: { min: 34.0, max: 42.0, step: 0.1 },
  heart_rate: { min: 30, max: 200, step: 1 },
  systolic_bp: { min: 60, max: 240, step: 1 },
  diastolic_bp: { min: 30, max: 140, step: 1 },
  wbc: { min: 1.0, max: 50.0, step: 0.1 },
  hemoglobin: { min: 5.0, max: 25.0, step: 0.1 },
  platelet_count: { min: 10, max: 1000, step: 5 },
  sodium: { min: 115, max: 160, step: 1 },
  potassium: { min: 1.5, max: 8.0, step: 0.1 },
  creatinine: { min: 0.1, max: 15.0, step: 0.1 },
  glucose: { min: 20, max: 600, step: 5 },
  troponin: { min: 0.0, max: 5.0, step: 0.01 },
  bnp: { min: 5, max: 5000, step: 10 },
  lactate: { min: 0.2, max: 20.0, step: 0.1 },
  inr: { min: 0.5, max: 10.0, step: 0.1 },
};

const API_BASE = 'http://localhost:8000';

const PLACEHOLDERS = {
  age: '45', sex: 'M', altered_mentation: '0', chest_pain: '0', diabetes: '0',
  spo2: '97', respiratory_rate: '16', temperature: '36.8', heart_rate: '70',
  systolic_bp: '120', diastolic_bp: '80', pain_score: '2',
  wbc: '7.5', hemoglobin: '14.0', platelet_count: '250', sodium: '140', potassium: '4.0',
  creatinine: '0.9', glucose: '100', troponin: '0.01', bnp: '50', lactate: '1.2', inr: '1.0'
};

export default function IntakePage({
  patientData, handleInputChange,
  loading, error, apiStatus,
  handlePredict,
  loadHealthyExample, loadHighRiskExample,
  setRagReport,
  triageMode = 'IMMEDIATE', setTriageMode,
  patientName, setPatientName,
  currentPatientId,
  saveStatus, onSave,
  onNewPatient,
}) {
  const [activeTab, setActiveTab] = useState('vitals');

  useEffect(() => {
    if (triageMode === 'IMMEDIATE' && activeTab === 'labs') {
      setActiveTab('vitals');
    }
  }, [triageMode, activeTab]);

  const renderInput = (label, name, value, type = 'number', unit = '', range = '', options = null, disabled = false) => {
    return (
      <div className="input-group intake-input-group">
        <div className="input-header">
          <label>{label}</label>
          {range && <span className="input-range">{range}</span>}
        </div>
        <div className="input-control-wrapper">
          {options ? (
            <select name={name} value={value} onChange={handleInputChange} disabled={disabled}>
              {value === '' && <option value="">Select...</option>}
              {options.map(opt => <option key={opt.val} value={opt.val}>{opt.lbl}</option>)}
            </select>
          ) : (
            <>
              <input
                type={type}
                name={name}
                value={value}
                onChange={handleInputChange}
                disabled={disabled}
                placeholder={PLACEHOLDERS[name] || ''}
                step={
                  name === 'temperature' ? '0.1'
                  : ['wbc', 'hemoglobin', 'potassium', 'creatinine', 'lactate', 'inr'].includes(name) ? '0.1'
                  : name === 'troponin' ? '0.01'
                  : '1'
                }
              />
              {unit && <span className="input-unit">{unit}</span>}
            </>
          )}
        </div>
      </div>
    );
  };

  const allTabs = [
    { key: 'demographics', label: 'Demographics', icon: <User size={16} /> },
    { key: 'vitals',       label: 'Vitals & SpO₂', icon: <HeartPulse size={16} /> },
    { key: 'labs',         label: 'Lab Reports', icon: <TestTubes size={16} /> },
    { key: 'symptoms',     label: 'Symptoms', icon: <MessageSquare size={16} /> },
  ];

  const tabs = triageMode === 'IMMEDIATE'
    ? allTabs.filter(t => t.key !== 'labs')
    : allTabs;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }} 
      animate={{ opacity: 1, y: 0 }} 
      transition={{ duration: 0.4 }}
      className="page-container"
    >
      <div className="page-header">
        <div>
          <h2 className="page-title">Patient Triage Intake</h2>
          <p className="page-subtitle">Enter patient telemetry, demographics, and lab values to trigger the multi-agent analysis.</p>
        </div>
        <div className="intake-preset-group">
          <button className="btn outline preset-btn" onClick={loadHealthyExample}>
            <CheckCircle2 size={14} />
            Healthy Preset
          </button>
          <button className="btn outline preset-btn critical" onClick={loadHighRiskExample}>
            <AlertTriangle size={14} />
            Critical Preset
          </button>
        </div>
      </div>

      {/* Patient Profile & Registry Card */}
      <div className="patient-registry-card glass-panel" style={{ padding: '16px', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1, minWidth: '220px' }}>
          <label style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--text-secondary)' }}>Patient Name (Optional)</label>
          <input
            type="text"
            value={patientName}
            onChange={e => setPatientName(e.target.value)}
            placeholder="Anonymous Patient / Enter name..."
            style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--input-bg)', color: 'var(--text-primary)', fontSize: '0.85rem', width: '100%' }}
          />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', minWidth: '160px' }}>
          <label style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--text-secondary)' }}>Generated Patient ID</label>
          <code style={{ background: 'var(--input-bg)', border: '1px solid var(--border-color)', padding: '8px 12px', borderRadius: '8px', fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)', display: 'inline-block' }}>{currentPatientId}</code>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignSelf: 'flex-end', height: '36px', minWidth: '280px' }}>
          <button
            className={`topbar-btn save-btn ${saveStatus === 'saving' ? 'saving' : saveStatus === 'saved' ? 'saved' : saveStatus === 'error' ? 'error' : ''}`}
            onClick={onSave}
            disabled={saveStatus === 'saving' || loading}
            style={{ flex: 1, height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', borderRadius: '8px', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer' }}
          >
            {saveStatus === 'saving' && <><span className="spinner" style={{ width: '12px', height: '12px', borderWidth: '1.5px' }}></span> Saving...</>}
            {saveStatus === 'saved' && <>✓ Saved</>}
            {saveStatus === 'error' && <>⚠️ Failed</>}
            {!saveStatus && <><Save size={14} /> Save Patient</>}
          </button>
          <button 
            className="topbar-btn new-btn" 
            onClick={onNewPatient}
            style={{ flex: 1, height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', borderRadius: '8px', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer' }}
          >
            <Plus size={14} /> New Patient
          </button>
        </div>
      </div>

      {/* Triage Mode Selector */}
      <div className="triage-mode-container glass-panel" style={{ padding: '16px', marginBottom: '1rem', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <label style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-secondary)' }}>Triage Assessment Level</label>
        <div className="triage-mode-selector">
          <button
            type="button"
            className={`triage-mode-btn ${triageMode === 'IMMEDIATE' ? 'active' : ''}`}
            onClick={() => setTriageMode('IMMEDIATE')}
          >
            <Stethoscope size={16} style={{ marginRight: 6 }} /> Immediate Triage (ER Arrival)
          </button>
          <button
            type="button"
            className={`triage-mode-btn ${triageMode === 'ENHANCED' ? 'active' : ''}`}
            onClick={() => setTriageMode('ENHANCED')}
          >
            <Beaker size={16} style={{ marginRight: 6 }} /> Enhanced Triage (Labs Available)
          </button>
        </div>
      </div>

      {/* Tab Nav */}
      <div className="tab-navigation intake-tabs" style={{ display: 'flex', gap: '4px' }}>
        {tabs.map(tab => (
          <button
            key={tab.key}
            className={`tab-btn intake-tab-btn ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
            type="button"
            style={{ flex: 1, justifyContent: 'center' }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              {tab.icon}
              {tab.label}
            </span>
          </button>
        ))}
      </div>

      {/* Tab Panels */}
      <div className="intake-panels-grid">
        <AnimatePresence mode="wait">
          {activeTab === 'demographics' && (
            <motion.div 
              key="demographics"
              initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }} transition={{ duration: 0.2 }}
              className="form-tab-panel glass-panel"
            >
              <div className="form-section-title">
                <User size={16} /> Patient Demographics
              </div>
              <div className="form-grid">
                {renderInput('Age', 'age', patientData.age, 'number', 'yrs', 'Range: 0–120')}
                {renderInput('Sex', 'sex', patientData.sex, 'text', '', '', [{ val: 'M', lbl: 'Male' }, { val: 'F', lbl: 'Female' }])}
                {renderInput('Altered Mentation', 'altered_mentation', patientData.altered_mentation, 'number', '', '', [{ val: 0, lbl: 'Alert / Normal' }, { val: 1, lbl: 'Confused / Altered' }])}
                {renderInput('Chest Pain', 'chest_pain', patientData.chest_pain, 'number', '', '', [{ val: 0, lbl: 'No / Absent' }, { val: 1, lbl: 'Yes / Present' }])}
                {renderInput('Diabetes', 'diabetes', patientData.diabetes, 'number', '', '', [{ val: 0, lbl: 'No History' }, { val: 1, lbl: 'Diabetic' }])}
                {renderInput('Pain Score (Auto)', 'pain_score', patientData.pain_score, 'number', '/10', 'Auto-calculated', null, true)}
              </div>
            </motion.div>
          )}

          {activeTab === 'vitals' && (
            <motion.div 
              key="vitals"
              initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }} transition={{ duration: 0.2 }}
              className="form-tab-panel glass-panel"
            >
              <div className="form-section-title">
                <HeartPulse size={16} /> Vital Signs &amp; SpO₂
              </div>
              <div className="form-grid">
                {renderInput('SpO₂', 'spo2', patientData.spo2, 'number', '%', 'Target: 95–100%')}
                {renderInput('Resp Rate', 'respiratory_rate', patientData.respiratory_rate, 'number', '/min', 'Normal: 12–20')}
                {renderInput('Temperature', 'temperature', patientData.temperature, 'number', '°C', 'Normal: 36.5–37.5')}
                {renderInput('Heart Rate', 'heart_rate', patientData.heart_rate, 'number', 'bpm', 'Normal: 60–100')}
                {renderInput('Systolic BP', 'systolic_bp', patientData.systolic_bp, 'number', 'mmHg', 'Normal: 90–120')}
                {renderInput('Diastolic BP', 'diastolic_bp', patientData.diastolic_bp, 'number', 'mmHg', 'Normal: 60–80')}
              </div>
            </motion.div>
          )}

          {activeTab === 'labs' && (
            <motion.div 
              key="labs"
              initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }} transition={{ duration: 0.2 }}
              className="form-tab-panel glass-panel"
            >
              <div className="form-section-title">
                <TestTubes size={16} /> Laboratory Results
              </div>
              <div className="form-grid-labs">
                {renderInput('WBC Count', 'wbc', patientData.wbc, 'number', 'k/µL', 'Normal: 4.5–11.0')}
                {renderInput('Hemoglobin', 'hemoglobin', patientData.hemoglobin, 'number', 'g/dL', 'Normal: 12.0–17.5')}
                {renderInput('Platelets', 'platelet_count', patientData.platelet_count, 'number', 'k/µL', 'Normal: 150–450')}
                {renderInput('Sodium', 'sodium', patientData.sodium, 'number', 'mEq/L', 'Normal: 135–145')}
                {renderInput('Potassium', 'potassium', patientData.potassium, 'number', 'mEq/L', 'Normal: 3.5–5.0')}
                {renderInput('Creatinine', 'creatinine', patientData.creatinine, 'number', 'mg/dL', 'Normal: 0.6–1.2')}
                {renderInput('Glucose', 'glucose', patientData.glucose, 'number', 'mg/dL', 'Normal: 70–140')}
                {renderInput('Troponin', 'troponin', patientData.troponin, 'number', 'ng/mL', 'Normal: < 0.04')}
                {renderInput('BNP', 'bnp', patientData.bnp, 'number', 'pg/mL', 'Normal: < 100')}
                {renderInput('Lactate', 'lactate', patientData.lactate, 'number', 'mmol/L', 'Normal: 0.5–2.2')}
                {renderInput('INR', 'inr', patientData.inr, 'number', '', 'Normal: 0.8–1.2')}
              </div>
            </motion.div>
          )}

          {activeTab === 'symptoms' && (
            <motion.div 
              key="symptoms"
              initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }} transition={{ duration: 0.2 }}
              className="form-tab-panel glass-panel"
            >
              <div className="form-section-title">
                <MessageSquare size={16} /> Patient Symptoms
                <span className="chat-badge">FAISS · Groq llama-3.3-70b</span>
              </div>
              
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem', lineHeight: '1.5' }}>
                Describe the patient's symptoms in plain text. When you run the risk analysis, this will be automatically combined with the patient's demographics and vitals to generate a detailed symptom analysis using the FAISS/Groq RAG system.
              </p>

              <textarea
                className="chat-textarea"
                name="symptoms"
                placeholder="e.g. 65-year-old male with severe shortness of breath, chest pain, and altered mentation..."
                value={patientData.symptoms || ''}
                onChange={handleInputChange}
                rows={8}
                style={{ width: '100%', marginBottom: '1rem', borderRadius: '10px', padding: '12px', background: 'var(--input-bg)', color: 'var(--text-primary)', border: '1px solid var(--input-border)', fontFamily: 'inherit', fontSize: '0.85rem', resize: 'vertical' }}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Analyze Button */}
      <div className="intake-analyze-section">
        {error && <div className="error-msg">⚠️ {error}</div>}
        <motion.button
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.98 }}
          className="btn primary full-width predict-btn"
          onClick={handlePredict}
          disabled={loading || !apiStatus}
          style={{ padding: '14px', fontSize: '1rem', marginTop: '1rem' }}
        >
          {loading ? (
            <span className="spinner-group">
              <span className="spinner"></span>
              <span>Analyzing Clinical Data...</span>
            </span>
          ) : (
            <>
              <Play size={18} fill="currentColor" />
              Run Clinical Risk Analysis
            </>
          )}
        </motion.button>
        {!apiStatus && (
          <p className="api-offline-note">⚠️ API engine is offline. Start the backend server to analyze.</p>
        )}
      </div>
    </motion.div>
  );
}
