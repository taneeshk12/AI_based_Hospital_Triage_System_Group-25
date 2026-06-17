import React from 'react';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Tooltip,
  ResponsiveContainer,
} from 'recharts';

const HeartPulseIcon = () => (
  <svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" strokeWidth="2.5" fill="none" strokeLinecap="round" strokeLinejoin="round" className="icon-svg pulsing-icon">
    <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
  </svg>
);
const LungsIcon = () => (
  <svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" strokeWidth="2.5" fill="none" strokeLinecap="round" strokeLinejoin="round" className="icon-svg">
    <path d="M12 4v16M12 7c-2.5-3-7-3-9 0v7c2.2 3 6.8 3 9 0M12 7c2.5-3 7-3 9 0v7c-2.2 3-6.8 3-9 0" />
    <path d="M5 14c1-1 2-1 3 0M16 14c1-1 2-1 3 0" />
  </svg>
);
const MicrobeIcon = () => (
  <svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" strokeWidth="2.5" fill="none" strokeLinecap="round" strokeLinejoin="round" className="icon-svg">
    <circle cx="12" cy="12" r="5" /><circle cx="12" cy="12" r="2" />
    <path d="M12 2v4M12 18v4M2 12h4M18 12h4M5 5l2.5 2.5M16.5 16.5 19 19M19 5l-2.5 2.5M7.5 16.5 5 19" />
  </svg>
);
const ShieldIcon = () => (
  <svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" strokeWidth="2.5" fill="none" strokeLinecap="round" strokeLinejoin="round" className="icon-svg">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
  </svg>
);
const ChevronDownIcon = ({ expanded }) => (
  <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2.5" fill="none" strokeLinecap="round" strokeLinejoin="round"
    style={{ transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.3s' }}>
    <polyline points="6 9 12 15 18 9" />
  </svg>
);

const getRiskColor = (riskLevel) => {
  if (!riskLevel) return '#94a3b8';
  if (riskLevel.includes('LOW')) return '#10b981';
  if (riskLevel.includes('MEDIUM') || riskLevel.includes('MID')) return '#f59e0b';
  if (riskLevel.includes('HIGH')) return '#ef4444';
  return '#94a3b8';
};

function AgentCard({ title, modelKey, data, expandedAgents, setExpandedAgents }) {
  if (!data) return null;
  if (data.status === 'error') {
    return (
      <div className="prediction-card error-card">
        <div className="card-header"><h3>{title}</h3><span className="error-icon">⚠️</span></div>
        <p className="error-desc">Assessment Failed: {data.error_message}</p>
      </div>
    );
  }
  const color = getRiskColor(data.risk_level);
  const probs = data.probabilities ? {
    low: data.probabilities.low ?? data.probabilities.low_risk ?? 0,
    medium: data.probabilities.medium ?? data.probabilities.mid_risk ?? 0,
    high: data.probabilities.high ?? data.probabilities.high_risk ?? 0,
  } : null;
  let AgentIcon = ShieldIcon;
  if (modelKey === 'respiratory') AgentIcon = LungsIcon;
  else if (modelKey === 'cardiac') AgentIcon = HeartPulseIcon;
  else if (modelKey === 'sepsis') AgentIcon = MicrobeIcon;
  const isExpanded = !!expandedAgents[modelKey];

  return (
    <div className={`prediction-card ${isExpanded ? 'expanded' : 'collapsed'}`} style={{ '--card-color': color }}>
      <div className="card-header clickable-header" onClick={() => setExpandedAgents(prev => ({ ...prev, [modelKey]: !prev[modelKey] }))}>
        <div className="card-title-group">
          <span className="card-icon-container" style={{ color }}><AgentIcon /></span>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <h3 style={{ margin: 0 }}>{title}</h3>
            {!isExpanded && <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>Click to view analysis</span>}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <div className="risk-badge" style={{ borderColor: color, color, backgroundColor: color + '15', display: 'flex', alignItems: 'center', gap: '6px' }}>
            {data.risk_level.replace('_RISK', '')}
            <span style={{ fontSize: '0.7rem', opacity: 0.8, paddingLeft: '4px', borderLeft: `1px solid ${color}40` }}>
              {(data.confidence * 100).toFixed(0)}%
            </span>
          </div>
          <div className="expand-toggle" style={{ color: 'var(--text-muted)' }}><ChevronDownIcon expanded={isExpanded} /></div>
        </div>
      </div>
      {isExpanded && (
        <div className="card-body animate-slide-down">
          <div className="confidence-meter-container">
            <div className="confidence-header">
              <span>Agent Confidence</span>
              <span className="confidence-value" style={{ color }}>{(data.confidence * 100).toFixed(1)}%</span>
            </div>
            <div className="confidence-bar-wrapper">
              <div className="confidence-bar-fill" style={{ width: `${data.confidence * 100}%`, backgroundColor: color }}>
                <span className="confidence-pulse-dot" style={{ backgroundColor: color }}></span>
              </div>
            </div>
          </div>
          <div className="action-text">
            <span className="action-label">Recommendation:</span>
            <p>{data.clinical_action}</p>
          </div>
          <div className="probabilities-section">
            <span className="section-small-title">Risk Distribution</span>
            <div className="probabilities-bar">
              {probs && (
                <>
                  <div className="prob-segment" style={{ width: `${probs.low * 100}%`, backgroundColor: '#10b981' }}></div>
                  <div className="prob-segment" style={{ width: `${probs.medium * 100}%`, backgroundColor: '#f59e0b' }}></div>
                  <div className="prob-segment" style={{ width: `${probs.high * 100}%`, backgroundColor: '#ef4444' }}></div>
                </>
              )}
            </div>
            <div className="probabilities-labels">
              <span>L: {((probs?.low || 0) * 100).toFixed(0)}%</span>
              <span>M: {((probs?.medium || 0) * 100).toFixed(0)}%</span>
              <span>H: {((probs?.high || 0) * 100).toFixed(0)}%</span>
            </div>
          </div>
          <div className="shap-section">
            <h4 className="shap-title">Key Clinical Drivers</h4>
            {data.top_contributing_features && data.top_contributing_features.length > 0 ? (
              <div className="shap-bars">
                {data.top_contributing_features.map((feat, idx) => {
                  const maxVal = Math.max(...data.top_contributing_features.map(f => Math.abs(f.value)), 0.001);
                  const percentage = Math.min(100, Math.max(10, (Math.abs(feat.value) / maxVal) * 100));
                  const isPositive = feat.impact === 'positive';
                  return (
                    <div key={idx} className="shap-row-modern">
                      <div className="shap-label-row">
                        <span className="shap-feat-name">{feat.feature.replace(/_/g, ' ')}</span>
                        <span className={`shap-feat-impact-tag ${isPositive ? 'positive' : 'negative'}`}>
                          {isPositive ? '↑' : '↓'} {Math.abs(feat.value).toFixed(2)}
                        </span>
                      </div>
                      <div className="shap-track-modern">
                        <div className={`shap-fill-modern ${isPositive ? 'risk-up' : 'risk-down'}`} style={{ width: `${percentage}%` }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : <div className="shap-empty">Baseline values detected</div>}
          </div>
        </div>
      )}
    </div>
  );
}

export default function ResultsPage({
  predictions, aggregation, llmSummary, fullReport,
  patientData, feedbackStatus, setFeedbackStatus,
  overrideValue, setOverrideValue,
  handleFeedback, downloadReport, reportRef,
  expandedAgents, setExpandedAgents,
  activePatientAssessments, selectedAssessmentId, handleLoadAssessment,
}) {
  if (!predictions) {
    return (
      <div className="page-container animate-fade-in">
        <div className="empty-state glass-panel" style={{ margin: 'auto', maxWidth: 600 }}>
          <div className="radar-sonar-container">
            <div className="sonar-wave"></div>
            <div className="sonar-center">🩺</div>
          </div>
          <h2>No Analysis Yet</h2>
          <p>Go to <strong>Triage Intake</strong>, enter patient data, and click <strong>Run Clinical Risk Analysis</strong>.</p>
        </div>
      </div>
    );
  }

  const riskColor = getRiskColor(aggregation?.final_risk);
  const riskPercent = (() => {
    if (!aggregation) return 0;
    const conf = aggregation.overall_confidence ?? 0.5;
    if (aggregation.final_risk === 'HIGH') return 75 + conf * 25;
    if (aggregation.final_risk === 'MEDIUM' || aggregation.final_risk === 'MID') return 35 + conf * 40;
    return conf * 35;
  })();

  const vitalsRadarData = [
    { subject: 'Heart Rate', A: Math.max(0, Math.min(100, 50 + ((patientData.heart_rate - 75) / (120 - 75)) * 50)), fullMark: 100, original: `${patientData.heart_rate} bpm` },
    { subject: 'Resp Rate', A: Math.max(0, Math.min(100, 50 + ((patientData.respiratory_rate - 16) / (30 - 16)) * 50)), fullMark: 100, original: `${patientData.respiratory_rate} /min` },
    { subject: 'SpO2 (Inv)', A: Math.max(0, Math.min(100, 50 + ((100 - patientData.spo2 - 2) / (10 - 2)) * 50)), fullMark: 100, original: `${patientData.spo2}%` },
    { subject: 'Temp', A: Math.max(0, Math.min(100, 50 + ((patientData.temperature - 37) / (39.5 - 37)) * 50)), fullMark: 100, original: `${patientData.temperature}°C` },
    { subject: 'Systolic BP', A: Math.max(0, Math.min(100, 50 + ((patientData.systolic_bp - 120) / (180 - 120)) * 50)), fullMark: 100, original: `${patientData.systolic_bp} mmHg` },
  ];

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">Clinical Risk Analysis</h2>
          <p className="page-subtitle">Multi-agent diagnostic output for current patient assessment.</p>
        </div>
        {fullReport && (
          <button className="btn outline" onClick={downloadReport} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            Download PDF
          </button>
        )}
      </div>

      {/* Assessment History Timeline */}
      {activePatientAssessments.length > 0 && (
        <div className="assessment-history-panel glass-panel" style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
            <span style={{ fontSize: '1rem' }}>📋</span>
            <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>Assessment History</h3>
            <span style={{ marginLeft: 'auto', fontSize: '0.75rem', opacity: 0.5 }}>{activePatientAssessments.length} run{activePatientAssessments.length > 1 ? 's' : ''}</span>
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
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Main Risk Gauge + Radar 2-col */}
      {aggregation && (
        <div className="results-top-grid">
          {/* Risk Gauge */}
          <div className="risk-gauge-card glass-panel">
            <div className="risk-gauge-title">Overall Triage Risk</div>
            <div className="risk-gauge-wrapper">
              <svg viewBox="0 0 200 110" className="risk-gauge-svg">
                <defs>
                  <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#10b981" />
                    <stop offset="50%" stopColor="#f59e0b" />
                    <stop offset="100%" stopColor="#ef4444" />
                  </linearGradient>
                </defs>
                <path d="M 20 100 A 80 80 0 0 1 180 100" stroke="rgba(255,255,255,0.07)" strokeWidth="16" fill="none" strokeLinecap="round" />
                <path d="M 20 100 A 80 80 0 0 1 180 100" stroke="url(#gaugeGradient)" strokeWidth="16" fill="none" strokeLinecap="round"
                  strokeDasharray={`${(riskPercent / 100) * 251.2} 251.2`} style={{ transition: 'stroke-dasharray 1s ease' }} />
                <text x="100" y="88" textAnchor="middle" fontSize="28" fontWeight="bold" fill={riskColor}>{Math.round(riskPercent)}%</text>
                <text x="100" y="104" textAnchor="middle" fontSize="10" fill="rgba(255,255,255,0.5)">Risk Score</text>
              </svg>
            </div>
            <div className="risk-final-label" style={{ color: riskColor, borderColor: riskColor + '40', background: riskColor + '15' }}>
              {aggregation.final_risk} RISK
            </div>
            <div className="risk-confidence">
              Confidence: <strong>{((aggregation.overall_confidence || 0) * 100).toFixed(1)}%</strong>
            </div>
          </div>

          {/* Vitals Radar */}
          <div className="results-radar-card glass-panel">
            <div className="risk-gauge-title">Vitals Risk Profile</div>
            <ResponsiveContainer width="100%" height={220}>
              <RadarChart data={vitalsRadarData} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                <Radar name="Risk Index" dataKey="A" stroke={riskColor} fill={riskColor} fillOpacity={0.2} strokeWidth={2} />
                <Tooltip content={({ active, payload }) => active && payload?.length ? (
                  <div className="radar-tooltip">
                    <p className="tooltip-label">{payload[0].payload.subject}</p>
                    <p className="tooltip-value">Value: <strong>{payload[0].payload.original}</strong></p>
                    <p className="tooltip-normalized">Risk Index: {Math.round(payload[0].payload.A)}/100</p>
                  </div>
                ) : null} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* LLM Summary */}
      {llmSummary && (
        <div className="llm-summary-card glass-panel">
          <div className="llm-header">
            <span className="llm-icon">🤖</span>
            <div>
              <h3>AI Clinical Interpretation</h3>
              <span className="llm-sub">Generated by clinical language model</span>
            </div>
          </div>
          <div className="llm-text">{llmSummary}</div>
        </div>
      )}

      {/* Agent Cards grid */}
      <div className="dashboard-grid">
        <AgentCard title="Respiratory Sub-Agent" modelKey="respiratory" data={predictions.respiratory} expandedAgents={expandedAgents} setExpandedAgents={setExpandedAgents} />
        <AgentCard title="Cardiac Sub-Agent" modelKey="cardiac" data={predictions.cardiac} expandedAgents={expandedAgents} setExpandedAgents={setExpandedAgents} />
        <AgentCard title="Sepsis Sub-Agent" modelKey="sepsis" data={predictions.sepsis} expandedAgents={expandedAgents} setExpandedAgents={setExpandedAgents} />
        <AgentCard title="General Health Sub-Agent" modelKey="general" data={predictions.general} expandedAgents={expandedAgents} setExpandedAgents={setExpandedAgents} />
      </div>

      {/* Attestation */}
      {aggregation && (
        <div className="clinician-feedback-card glass-panel">
          <div className="feedback-badge-header">
            <div className="feedback-title-group">
              <span className="feedback-icon">🔒</span>
              <h3>Diagnostic Attestation & Sign-off</h3>
            </div>
            <span className="status-badge-pending">Pending Review</span>
          </div>
          <p className="feedback-description">
            Review the multi-agent diagnostic outputs. Certify the AI's triage risk assessment or log a clinician override.
          </p>
          {feedbackStatus === 'success' ? (
            <div className="feedback-success-state">
              <div className="success-checkmark-circle">
                <svg viewBox="0 0 24 24" width="32" height="32" stroke="currentColor" strokeWidth="3" fill="none"><polyline points="20 6 9 17 4 12" /></svg>
              </div>
              <div>
                <h4>Assessment Certified & Transmitted</h4>
                <p>Your feedback has been appended to the clinical audit log.</p>
              </div>
            </div>
          ) : (
            <div className="feedback-actions-row">
              <button className="btn-certify" onClick={() => handleFeedback('accept')} disabled={feedbackStatus === 'submitting'}>
                <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2.5" fill="none" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '8px' }}><polyline points="20 6 9 17 4 12" /></svg>
                Certify AI Prediction
              </button>
              <div className="feedback-divider"><span>OR</span></div>
              <div className="override-control-group">
                <select value={overrideValue} onChange={e => setOverrideValue(e.target.value)} className="override-select">
                  <option value="LOW">Low Risk</option>
                  <option value="MEDIUM">Medium Risk</option>
                  <option value="HIGH">High Risk</option>
                </select>
                <button className="btn-override" onClick={() => handleFeedback('override')} disabled={feedbackStatus === 'submitting'}>
                  <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2.5" fill="none" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '8px' }}><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /></svg>
                  Submit Override
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Hidden PDF template */}
      <div style={{ position: 'absolute', left: '-9999px', top: '-9999px', visibility: 'hidden', overflow: 'hidden' }}>
        <div ref={reportRef}></div>
      </div>
    </div>
  );
}
