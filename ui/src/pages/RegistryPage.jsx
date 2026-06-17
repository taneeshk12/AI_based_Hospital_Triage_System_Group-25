import React, { useState } from 'react';

export default function RegistryPage({
  patientsList, patientSearch, setPatientSearch,
  registryLoading,
  currentPatientId,
  handleLoadPatient, handleDeletePatient, handleNewPatient,
  fetchPatients,
  activePatientAssessments, selectedAssessmentId, handleLoadAssessment,
}) {
  const [filterRisk, setFilterRisk] = useState('ALL');

  const filtered = patientsList.filter(p => {
    const q = patientSearch.toLowerCase();
    const nameMatch = !q || p.patient_name?.toLowerCase().includes(q) || p.patient_id?.toLowerCase().includes(q);
    const riskMatch = filterRisk === 'ALL' || p.risk_prediction === filterRisk;
    return nameMatch && riskMatch;
  });

  const riskCounts = { HIGH: 0, MEDIUM: 0, LOW: 0 };
  patientsList.forEach(p => { if (p.risk_prediction && riskCounts[p.risk_prediction] !== undefined) riskCounts[p.risk_prediction]++; });

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">Patient Registry</h2>
          <p className="page-subtitle">{patientsList.length} patient{patientsList.length !== 1 ? 's' : ''} in the clinical database.</p>
        </div>
        <button className="btn primary" onClick={handleNewPatient} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2.5" fill="none"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          New Patient
        </button>
      </div>

      {/* Stats bar */}
      <div className="registry-stats-bar">
        <div className="reg-stat-card">
          <span className="reg-stat-num">{patientsList.length}</span>
          <span className="reg-stat-label">Total Patients</span>
        </div>
        <div className="reg-stat-card high">
          <span className="reg-stat-num" style={{ color: '#ef4444' }}>{riskCounts.HIGH}</span>
          <span className="reg-stat-label">High Risk</span>
        </div>
        <div className="reg-stat-card medium">
          <span className="reg-stat-num" style={{ color: '#f59e0b' }}>{riskCounts.MEDIUM}</span>
          <span className="reg-stat-label">Medium Risk</span>
        </div>
        <div className="reg-stat-card low">
          <span className="reg-stat-num" style={{ color: '#10b981' }}>{riskCounts.LOW}</span>
          <span className="reg-stat-label">Low Risk</span>
        </div>
      </div>

      {/* Toolbar */}
      <div className="registry-page-toolbar">
        <div className="registry-search-wrapper" style={{ maxWidth: 360 }}>
          <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" strokeWidth="2" fill="none" className="registry-search-icon"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input
            className="registry-search-input"
            type="text"
            placeholder="Search by name or patient ID..."
            value={patientSearch}
            onChange={e => setPatientSearch(e.target.value)}
          />
        </div>
        <div className="reg-filter-group">
          {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map(risk => (
            <button
              key={risk}
              className={`reg-filter-btn ${filterRisk === risk ? 'active' : ''} ${risk !== 'ALL' ? risk.toLowerCase() : ''}`}
              onClick={() => setFilterRisk(risk)}
            >
              {risk}
            </button>
          ))}
        </div>
        <button className="topbar-btn" onClick={fetchPatients} title="Refresh registry" style={{ marginLeft: 'auto' }}>
          <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" strokeWidth="2" fill="none"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
        </button>
      </div>

      {registryLoading && (
        <div className="registry-loading">
          <span className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></span>
          <span>Loading patient data...</span>
        </div>
      )}

      {!registryLoading && patientsList.length === 0 && (
        <div className="registry-empty glass-panel" style={{ marginTop: '2rem' }}>
          <svg viewBox="0 0 24 24" width="52" height="52" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.3"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/></svg>
          <p style={{ fontWeight: 600, marginTop: '1rem' }}>No patients registered yet.</p>
          <p style={{ fontSize: '0.82rem', opacity: 0.5 }}>Run a triage analysis on the Intake page — patients are automatically saved to the registry.</p>
          <button className="btn primary" onClick={handleNewPatient} style={{ marginTop: '1rem' }}>Start First Patient</button>
        </div>
      )}

      {!registryLoading && filtered.length > 0 && (
        <div className="registry-page-table glass-panel">
          {/* Table header */}
          <div className="reg-table-header">
            <span style={{ flex: 2 }}>Patient</span>
            <span style={{ flex: 1 }}>Age / Sex</span>
            <span style={{ flex: 1.5 }}>Last Assessment</span>
            <span style={{ flex: 1 }}>Risk</span>
            <span style={{ width: 80 }}></span>
          </div>

          {filtered.map(p => {
            const riskColor = p.risk_prediction === 'HIGH' ? '#ef4444' : p.risk_prediction === 'MEDIUM' ? '#f59e0b' : p.risk_prediction === 'LOW' ? '#10b981' : '#64748b';
            const isActive = p.patient_id === currentPatientId;
            const lastDate = p.last_assessment_time
              ? new Date(p.last_assessment_time).toLocaleString('en-GB', { day: '2-digit', month: 'short', year: '2-digit', hour: '2-digit', minute: '2-digit' })
              : '—';
            return (
              <div key={p.patient_id} className={`reg-table-row ${isActive ? 'active' : ''}`} onClick={() => handleLoadPatient(p.patient_id)}>
                <div style={{ flex: 2, display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0 }}>
                  <div className="reg-row-avatar" style={{ background: `${riskColor}20`, color: riskColor }}>
                    {(p.patient_name || 'A')[0].toUpperCase()}
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <div className="reg-row-name">{p.patient_name || 'Anonymous'}</div>
                    <div className="reg-row-meta" style={{ fontFamily: 'monospace', fontSize: '0.7rem' }}>{p.patient_id}</div>
                  </div>
                </div>
                <div style={{ flex: 1 }} className="reg-row-meta">{p.age}y · {p.sex === 'M' ? 'Male' : 'Female'}</div>
                <div style={{ flex: 1.5 }} className="reg-row-meta">{lastDate}</div>
                <div style={{ flex: 1 }}>
                  {p.risk_prediction && (
                    <span className="reg-row-risk" style={{ color: riskColor, borderColor: `${riskColor}50`, background: `${riskColor}15` }}>
                      {p.risk_prediction}
                    </span>
                  )}
                </div>
                <div style={{ width: 80, display: 'flex', justifyContent: 'flex-end', gap: '6px' }}>
                  <button
                    className="reg-row-delete"
                    style={{ opacity: 0.4 }}
                    onClick={e => handleDeletePatient(p.patient_id, e)}
                    title="Delete patient"
                  >
                    <svg viewBox="0 0 24 24" width="15" height="15" stroke="currentColor" strokeWidth="2" fill="none"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/></svg>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Assessment History panel for selected patient */}
      {activePatientAssessments.length > 0 && (
        <div className="assessment-history-panel glass-panel animate-fade-in" style={{ marginTop: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
            <span style={{ fontSize: '1rem' }}>📋</span>
            <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>Assessment History — {currentPatientId}</h3>
            <span style={{ marginLeft: 'auto', fontSize: '0.75rem', opacity: 0.5 }}>{activePatientAssessments.length} runs</span>
          </div>
          <div className="assessment-timeline">
            {activePatientAssessments.map((assess, idx) => {
              const rc = assess.risk_prediction === 'HIGH' ? '#ef4444' : assess.risk_prediction === 'MEDIUM' ? '#f59e0b' : '#10b981';
              const isSel = assess.assessment_id === selectedAssessmentId;
              const dt = new Date(assess.timestamp);
              return (
                <div key={assess.assessment_id} className={`assessment-item ${isSel ? 'selected' : ''}`} onClick={() => handleLoadAssessment(assess)}>
                  <div className="assess-timeline-line">
                    <div className="assess-dot" style={{ background: rc, boxShadow: isSel ? `0 0 8px ${rc}80` : 'none' }}></div>
                    {idx < activePatientAssessments.length - 1 && <div className="assess-connector"></div>}
                  </div>
                  <div className="assess-content">
                    <div className="assess-header">
                      <span className="assess-id">{assess.assessment_id}</span>
                      <span className="assess-risk" style={{ color: rc, background: `${rc}18`, borderColor: `${rc}40` }}>{assess.risk_prediction}</span>
                    </div>
                    <div className="assess-time">{dt.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: '2-digit' })} at {dt.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}</div>
                    {assess.confidence_pct && assess.confidence_pct !== 'N/A' && (
                      <div className="assess-conf">Confidence: {assess.confidence_pct}</div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
