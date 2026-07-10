import React from 'react';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import emptyResultsImg from '../assets/empty-results.png';
import { 
  Activity, 
  Wind, 
  Bug, 
  ShieldCheck, 
  ChevronDown, 
  Stethoscope, 
  Download, 
  CheckCircle2, 
  AlertTriangle,
  Bot,
  MessageSquare,
  ClipboardCheck,
  Lock
} from 'lucide-react';

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
        <div className="card-header"><h3>{title}</h3><AlertTriangle size={20} className="error-icon" /></div>
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
  const riskLabel = data.risk_level ? data.risk_level.replace('_RISK', '') : 'N/A';
  const confidencePct = data.confidence != null ? (data.confidence * 100).toFixed(1) : 'N/A';
  const confidencePctInt = data.confidence != null ? (data.confidence * 100).toFixed(0) : '0';
  
  let AgentIcon = ShieldCheck;
  if (modelKey === 'respiratory') AgentIcon = Wind;
  else if (modelKey === 'cardiac') AgentIcon = Activity;
  else if (modelKey === 'sepsis') AgentIcon = Bug;
  
  const isExpanded = !!expandedAgents[modelKey];

  return (
    <motion.div 
      layout
      transition={{ duration: 0.3 }}
      className={`prediction-card ${isExpanded ? 'expanded' : 'collapsed'}`} 
      style={{ '--card-color': color }}
    >
      <div className="card-header clickable-header" onClick={() => setExpandedAgents(prev => ({ ...prev, [modelKey]: !prev[modelKey] }))}>
        <div className="card-title-group">
          <span className="card-icon-container" style={{ color }}><AgentIcon size={22} /></span>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <h3 style={{ margin: 0 }}>{title}</h3>
            {!isExpanded && <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>Click to view analysis</span>}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <div className="risk-badge" style={{ borderColor: color, color, backgroundColor: color + '15', display: 'flex', alignItems: 'center', gap: '6px' }}>
            {riskLabel}
            <span style={{ fontSize: '0.7rem', opacity: 0.8, paddingLeft: '4px', borderLeft: `1px solid ${color}40` }}>
              {confidencePctInt}%
            </span>
          </div>
          <motion.div animate={{ rotate: isExpanded ? 180 : 0 }} style={{ color: 'var(--text-muted)' }}>
            <ChevronDown size={18} />
          </motion.div>
        </div>
      </div>
      <AnimatePresence>
        {isExpanded && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }} 
            animate={{ opacity: 1, height: 'auto' }} 
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="card-body"
            style={{ overflow: 'hidden' }}
          >
            <div className="confidence-meter-container">
              <div className="confidence-header">
                <span>Agent Confidence</span>
                <span className="confidence-value" style={{ color }}>{confidencePct}%</span>
              </div>
              <div className="confidence-bar-wrapper">
                <div className="confidence-bar-fill" style={{ width: `${data.confidence != null ? data.confidence * 100 : 0}%`, backgroundColor: color }}>
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
                          <motion.div 
                            initial={{ width: 0 }} animate={{ width: `${percentage}%` }} transition={{ duration: 0.5, delay: idx * 0.1 }}
                            className={`shap-fill-modern ${isPositive ? 'risk-up' : 'risk-down'}`} 
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : <div className="shap-empty">Baseline values detected</div>}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function ResultsPage({
  predictions, aggregation, llmSummary, fullReport, ragReport,
  patientData, feedbackStatus, setFeedbackStatus,
  overrideValue, setOverrideValue,
  handleFeedback, downloadReport, reportRef,
  expandedAgents, setExpandedAgents,
  activePatientAssessments, selectedAssessmentId, handleLoadAssessment,
}) {
  if (!predictions) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="page-container">
        <div className="empty-state glass-panel" style={{ margin: 'auto', maxWidth: 500, textAlign: 'center', padding: '3rem 2rem' }}>
          <img src={emptyResultsImg} alt="No Results" style={{ width: '100%', maxWidth: '250px', marginBottom: '1.5rem', borderRadius: '12px', boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }} />
          <h2>No Results Available</h2>
          <p>Please complete a <strong>Triage Intake</strong> analysis first to generate an AI assessment report.</p>
        </div>
      </motion.div>
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
    <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="page-container">
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <h2 className="page-title" style={{ margin: 0 }}>Clinical Risk Analysis</h2>
            {aggregation?.triage_mode && (
              <span className={`triage-mode-badge ${aggregation.triage_mode.toLowerCase()}`}>
                {aggregation.triage_mode === 'ENHANCED' ? '🧪 Enhanced Triage' : '🩺 Immediate Triage'}
              </span>
            )}
          </div>
          <p className="page-subtitle">Multi-agent diagnostic output for current patient assessment.</p>
        </div>
        {fullReport && (
          <button className="btn outline" onClick={downloadReport} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Download size={16} />
            Download PDF
          </button>
        )}
      </div>

      {/* DASHBOARD INTEGRATION CARDS */}
      <motion.div 
        initial="hidden" animate="show"
        variants={{
          hidden: { opacity: 0 },
          show: { opacity: 1, transition: { staggerChildren: 0.1 } }
        }}
        className="metrics-dashboard-grid" 
        style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: '15px', marginBottom: '1.5rem' }}
      >
        <motion.div variants={{ hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } }} className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', borderLeft: `4px solid ${riskColor}` }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Prediction</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: riskColor, margin: '8px 0 4px 0' }}>{aggregation?.final_risk}_RISK</div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {aggregation?.safety_alerts && aggregation.safety_alerts.length > 0 ? "⚠️ Safety Override active" : "Consensus risk level"}
          </div>
        </motion.div>

        <motion.div variants={{ hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } }} className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', borderLeft: '4px solid #3b82f6' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Confidence</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#3b82f6', margin: '8px 0 4px 0' }}>{((aggregation?.overall_confidence || 0) * 100).toFixed(0)}%</div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700 }}>
            {aggregation?.overall_confidence >= 0.85 ? "HIGH" : aggregation?.overall_confidence >= 0.70 ? "MEDIUM" : "LOW"} CONFIDENCE
          </div>
        </motion.div>

        {(() => {
          const tColor = aggregation?.trust_score >= 80 ? '#10b981' : aggregation?.trust_score >= 60 ? '#f59e0b' : '#ef4444';
          return (
            <motion.div variants={{ hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } }} className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', borderLeft: `4px solid ${tColor}` }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Trust Score</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: tColor, margin: '8px 0 4px 0' }}>{aggregation?.trust_score}%</div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700 }}>{aggregation?.trust_category}</div>
            </motion.div>
          );
        })()}

        {(() => {
          const sColor = aggregation?.safety_status === 'AGREEMENT' ? '#10b981' : '#ef4444';
          return (
            <motion.div variants={{ hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } }} className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', borderLeft: `4px solid ${sColor}` }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Safety Status</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: sColor, margin: '8px 0 4px 0', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{aggregation?.safety_status}</div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Score: <strong>{aggregation?.safety_score}/100</strong></div>
            </motion.div>
          );
        })()}

        {(() => {
          const rColor = aggregation?.human_review_required ? '#ef4444' : '#10b981';
          return (
            <motion.div variants={{ hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } }} className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', borderLeft: `4px solid ${rColor}` }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Human Review</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: rColor, margin: '8px 0 4px 0' }}>{aggregation?.human_review_required ? "REQUIRED" : "NO"}</div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }} title={aggregation?.human_review_reason || 'Standard review'}>
                {aggregation?.human_review_required ? `Reason: ${aggregation.human_review_reason}` : "Standard oversight"}
              </div>
            </motion.div>
          );
        })()}
      </motion.div>

      {/* Clinical Safety Alerts Banner */}
      {aggregation?.safety_alerts && aggregation.safety_alerts.length > 0 && (
        <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="clinical-safety-banner" style={{
          backgroundColor: 'rgba(239, 68, 68, 0.08)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          padding: '16px 20px',
          marginBottom: '1.5rem',
          display: 'flex',
          gap: '15px',
          alignItems: 'flex-start',
        }}>
          <AlertTriangle color="#ef4444" size={28} />
          <div>
            <h4 style={{ margin: '0 0 6px 0', color: '#ef4444', fontWeight: 700, fontSize: '1rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Critical Clinical Safety Alerts
            </h4>
            <p style={{ margin: '0 0 8px 0', fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
              The patient's raw vitals have triggered immediate clinical safety alerts. Triage priority has been automatically escalated to HIGH.
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {aggregation.safety_alerts.map((alert, idx) => (
                <span key={idx} style={{
                  backgroundColor: 'rgba(239, 68, 68, 0.15)',
                  color: '#ef4444',
                  padding: '4px 10px',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  fontWeight: 700,
                  border: '1px solid rgba(239, 68, 68, 0.2)'
                }}>
                  {alert}
                </span>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Uncertainty & Reliability Analysis Banner */}
      {aggregation?.uncertainty_high && (
        <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="uncertainty-banner" style={{
          backgroundColor: 'rgba(245, 158, 11, 0.06)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          borderRadius: '8px',
          padding: '18px 20px',
          marginBottom: '1.5rem',
          display: 'flex',
          gap: '15px',
          alignItems: 'flex-start',
        }}>
          <AlertTriangle color="#f59e0b" size={28} />
          <div style={{ width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '8px' }}>
              <h4 style={{ margin: 0, color: '#f59e0b', fontWeight: 700, fontSize: '1rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Uncertainty & Reliability Warning
              </h4>
              <span style={{
                backgroundColor: 'rgba(245, 158, 11, 0.15)',
                color: '#f59e0b',
                padding: '2px 8px',
                borderRadius: '4px',
                fontSize: '0.75rem',
                fontWeight: 700,
                textTransform: 'uppercase'
              }}>
                Mandatory Review Required
              </span>
            </div>
            <p style={{ margin: '0 0 10px 0', fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
              The AI assessment reports elevated uncertainty due to the following clinical/model factors:
            </p>
            {aggregation.uncertainty_factors && aggregation.uncertainty_factors.length > 0 && (
              <ul style={{ margin: '0 0 12px 0', paddingLeft: '20px', color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: '1.5' }}>
                {aggregation.uncertainty_factors.map((factor, idx) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>{factor}</li>
                ))}
              </ul>
            )}
            <div style={{
              backgroundColor: 'rgba(245, 158, 11, 0.08)',
              borderLeft: '3px solid #f59e0b',
              padding: '10px 12px',
              borderRadius: '0 4px 4px 0',
              fontSize: '0.85rem',
              color: 'var(--text-muted)',
              lineHeight: '1.4'
            }}>
              <strong>Attending Clinician Guidance:</strong> {aggregation.uncertainty_explanation}
            </div>
          </div>
        </motion.div>
      )}

      {/* Assessment History Timeline */}
      {activePatientAssessments.length > 0 && (
        <div className="assessment-history-panel glass-panel" style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
            <ClipboardCheck size={20} />
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
          <div className="risk-gauge-card glass-panel" style={{ position: 'relative', overflow: 'hidden' }}>
            {/* Background ECG animation */}
            <svg style={{ position: 'absolute', top: '10%', left: 0, width: '100%', height: '80%', opacity: 0.1, zIndex: 0 }} viewBox="0 0 500 100" preserveAspectRatio="none">
              <path className="ecg-line" d="M0,50 L100,50 L120,20 L140,90 L160,10 L180,50 L500,50" fill="none" stroke={riskColor} strokeWidth="2" />
            </svg>
            <div className="risk-gauge-title" style={{ zIndex: 1, position: 'relative' }}>Overall Triage Risk</div>
            <div className="risk-gauge-wrapper ring-gauge-container" style={{ zIndex: 1, position: 'relative' }}>
              <svg viewBox="0 0 200 110" className="risk-gauge-svg">
                <defs>
                  <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#10b981" />
                    <stop offset="50%" stopColor="#f59e0b" />
                    <stop offset="100%" stopColor="#ef4444" />
                  </linearGradient>
                  <filter id="neonGlow">
                    <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                    <feMerge>
                      <feMergeNode in="coloredBlur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>
                </defs>
                <path d="M 20 100 A 80 80 0 0 1 180 100" stroke="rgba(255,255,255,0.05)" strokeWidth="16" fill="none" strokeLinecap="round" />
                <path d="M 20 100 A 80 80 0 0 1 180 100" stroke="url(#gaugeGradient)" strokeWidth="16" fill="none" strokeLinecap="round" filter="url(#neonGlow)"
                  strokeDasharray={`${(riskPercent / 100) * 251.2} 251.2`} style={{ transition: 'stroke-dasharray 1.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)' }} />
                <text x="100" y="88" textAnchor="middle" fontSize="32" fontWeight="800" fill={riskColor} className="risk-alert-pulse">{Math.round(riskPercent)}%</text>
                <text x="100" y="104" textAnchor="middle" fontSize="10" fill="var(--text-muted)">Risk Score</text>
              </svg>
            </div>
            <div className="risk-final-label" style={{ zIndex: 1, position: 'relative', color: riskColor, borderColor: riskColor + '80', background: riskColor + '20', boxShadow: `0 0 15px ${riskColor}40` }}>
              {aggregation.final_risk} RISK
            </div>
            <div className="risk-confidence" style={{ zIndex: 1, position: 'relative' }}>
              Confidence: <strong>{((aggregation.overall_confidence || 0) * 100).toFixed(1)}%</strong>
            </div>
          </div>

          {/* Vitals Radar */}
          <div className="results-radar-card glass-panel">
            <div className="risk-gauge-title">Vitals Risk Profile</div>
            <ResponsiveContainer width="100%" height={220}>
              <RadarChart data={vitalsRadarData} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
                <PolarGrid stroke="var(--radar-grid)" />
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
            <span className="llm-icon"><Bot size={28} /></span>
            <div>
              <h3>AI Clinical Interpretation</h3>
              <span className="llm-sub">Generated by clinical language model</span>
            </div>
          </div>
          <div className="llm-text">{llmSummary}</div>
        </div>
      )}

      {/* RAG Symptom Analysis */}
      {ragReport && (
        <div className="rag-report-card glass-panel">
          <div className="llm-header">
            <span className="llm-icon"><MessageSquare size={24} /></span>
            <div>
              <h3>RAG Symptom Analysis</h3>
              <span className="llm-sub">FAISS knowledge retrieval · Groq llama-3.3-70b-versatile</span>
            </div>
          </div>
          <pre className="rag-report-text">{ragReport.report}</pre>
          {ragReport.sources && ragReport.sources.length > 0 && (
            <div className="rag-sources-row">
              <span className="rag-sources-label">📚 Evidence sources:</span>
              {ragReport.sources.map((s, i) => (
                <span key={i} className="rag-source-chip">
                  <span className={`rag-cat-dot rag-cat-${s.category}`} />
                  {s.title}
                </span>
              ))}
            </div>
          )}
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
              <Lock className="feedback-icon" size={24} />
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
                <CheckCircle2 size={32} />
              </div>
              <div>
                <h4>Assessment Certified & Transmitted</h4>
                <p>Your feedback has been appended to the clinical audit log.</p>
              </div>
            </div>
          ) : (
            <div className="feedback-actions-row">
              <button className="btn-certify" onClick={() => handleFeedback('accept')} disabled={feedbackStatus === 'submitting'}>
                <CheckCircle2 size={18} style={{ marginRight: '8px' }} />
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
                  <AlertTriangle size={18} style={{ marginRight: '8px' }} />
                  Submit Override
                </button>
              </div>
            </div>
          )}
        </div>
      )}

    </motion.div>
  );
}
