import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const ShieldIcon = () => (
  <svg viewBox="0 0 24 24" width="32" height="32" stroke="#2563eb" strokeWidth="2.5" fill="none">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    <path d="M12 8v8M8 12h8" />
  </svg>
);

const PdfReportTemplate = React.forwardRef(({ fullReport, patientData }, ref) => {
  if (!fullReport || !patientData) return null;

  const isHigh = fullReport.risk_prediction.includes('HIGH');
  const isMedium = fullReport.risk_prediction.includes('MEDIUM') || fullReport.risk_prediction.includes('MID');
  const riskColor = isHigh ? '#ef4444' : (isMedium ? '#f59e0b' : '#10b981');
  const riskText = fullReport.risk_prediction.replace('_RISK', '');

  const shapData = fullReport.shap_top_features?.map(f => ({
    name: f.feature_label,
    impact: parseFloat(f.abs_impact.toFixed(3)),
    direction: f.direction.includes('increases') ? 'positive' : 'negative'
  })) || [];

  return (
    <div ref={ref} style={{
      width: '794px',
      minHeight: '1123px',
      backgroundColor: '#ffffff',
      color: '#1e293b',
      padding: '40px',
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      boxSizing: 'border-box'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '2px solid #e2e8f0', paddingBottom: '20px', marginBottom: '30px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <ShieldIcon />
          <div>
            <h1 style={{ margin: 0, fontSize: '24px', color: '#0f172a', fontWeight: '700' }}>OmniHealth Diagnostics</h1>
            <p style={{ margin: 0, fontSize: '14px', color: '#64748b' }}>Clinical Triage Assessment</p>
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '16px', fontWeight: '700', color: '#0f172a' }}>{fullReport.patient_name || 'Anonymous'}</div>
          <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '600', marginTop: '2px' }}>PATIENT ID: <span style={{ fontFamily: 'monospace', color: '#2563eb' }}>{fullReport.patient_id || 'N/A'}</span></div>
          <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '5px' }}>REPORT ID: {fullReport.report_id || 'N/A'}</div>
          <div style={{ fontSize: '11px', color: '#94a3b8' }}>{new Date(fullReport.timestamp).toLocaleString()}</div>
        </div>
      </div>

      {/* Patient Profile */}
      <div style={{ marginBottom: '30px', backgroundColor: '#f8fafc', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
        <h2 style={{ margin: '0 0 15px 0', fontSize: '16px', color: '#334155', textTransform: 'uppercase', letterSpacing: '1px' }}>Patient Profile</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '15px' }}>
          <div style={{ gridColumn: 'span 2' }}><div style={{ fontSize: '11px', color: '#64748b' }}>PATIENT NAME</div><div style={{ fontSize: '14px', fontWeight: '700' }}>{fullReport.patient_name || 'Anonymous'}</div></div>
          <div><div style={{ fontSize: '11px', color: '#64748b' }}>PATIENT ID</div><div style={{ fontSize: '13px', fontWeight: '600', fontFamily: 'monospace', color: '#2563eb' }}>{fullReport.patient_id || 'N/A'}</div></div>
          <div></div>
          <div><div style={{ fontSize: '11px', color: '#64748b' }}>AGE</div><div style={{ fontSize: '14px', fontWeight: '600' }}>{patientData.age}</div></div>
          <div><div style={{ fontSize: '11px', color: '#64748b' }}>SEX</div><div style={{ fontSize: '14px', fontWeight: '600' }}>{patientData.sex}</div></div>
          <div><div style={{ fontSize: '11px', color: '#64748b' }}>SpO₂</div><div style={{ fontSize: '14px', fontWeight: '600' }}>{patientData.spo2}%</div></div>
          <div><div style={{ fontSize: '11px', color: '#64748b' }}>HEART RATE</div><div style={{ fontSize: '14px', fontWeight: '600' }}>{patientData.heart_rate} bpm</div></div>
          <div><div style={{ fontSize: '11px', color: '#64748b' }}>BLOOD PRESSURE</div><div style={{ fontSize: '14px', fontWeight: '600' }}>{patientData.systolic_bp}/{patientData.diastolic_bp}</div></div>
          <div><div style={{ fontSize: '11px', color: '#64748b' }}>TEMP</div><div style={{ fontSize: '14px', fontWeight: '600' }}>{patientData.temperature}°C</div></div>
          <div><div style={{ fontSize: '11px', color: '#64748b' }}>RESP RATE</div><div style={{ fontSize: '14px', fontWeight: '600' }}>{patientData.respiratory_rate}/min</div></div>
          <div><div style={{ fontSize: '11px', color: '#64748b' }}>PAIN SCORE</div><div style={{ fontSize: '14px', fontWeight: '600' }}>{patientData.pain_score}/10</div></div>
        </div>
      </div>

      {/* Risk Assessment Banner */}
      <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
        <div style={{ flex: 1, backgroundColor: `${riskColor}15`, border: `2px solid ${riskColor}`, borderRadius: '8px', padding: '25px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: '12px', color: riskColor, fontWeight: '700', letterSpacing: '1px', textTransform: 'uppercase' }}>Triage Classification</div>
            <div style={{ fontSize: '36px', fontWeight: '800', color: riskColor, margin: '5px 0' }}>{riskText} RISK</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '600', textTransform: 'uppercase' }}>AI Confidence</div>
            <div style={{ fontSize: '28px', fontWeight: '700', color: '#334155' }}>{fullReport.confidence_pct}</div>
          </div>
        </div>
      </div>

      {/* LLM Interpretation */}
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{ margin: '0 0 10px 0', fontSize: '18px', color: '#0f172a', borderBottom: '2px solid #f1f5f9', paddingBottom: '8px' }}>AI Clinical Summary</h2>
        <p style={{ fontSize: '15px', lineHeight: '1.6', color: '#334155' }}>
          {fullReport.llm_interpretation}
        </p>
      </div>

      {/* Charts & Symptoms */}
      <div style={{ display: 'flex', gap: '30px', marginBottom: '30px' }}>
        {/* SHAP Chart */}
        <div style={{ flex: '2' }}>
          <h2 style={{ margin: '0 0 15px 0', fontSize: '16px', color: '#0f172a' }}>Top Clinical Drivers</h2>
          {shapData.length > 0 ? (
            <div style={{ height: '220px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={shapData} layout="vertical" margin={{ top: 0, right: 30, left: 0, bottom: 0 }}>
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" width={100} axisLine={false} tickLine={false} style={{ fontSize: '12px', fill: '#475569' }} />
                  <Tooltip cursor={{ fill: '#f1f5f9' }} />
                  <Bar dataKey="impact" radius={[0, 4, 4, 0]} barSize={20}>
                    {shapData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.direction === 'positive' ? riskColor : '#3b82f6'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div style={{ fontSize: '14px', color: '#64748b' }}>No key drivers detected.</div>
          )}
        </div>

        {/* Symptoms */}
        <div style={{ flex: '1', backgroundColor: '#f8fafc', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
          <h2 style={{ margin: '0 0 15px 0', fontSize: '14px', color: '#0f172a', textTransform: 'uppercase' }}>Detected Symptoms</h2>
          {fullReport.detected_symptoms && fullReport.detected_symptoms.length > 0 ? (
            <ul style={{ paddingLeft: '20px', margin: 0, color: '#334155', fontSize: '14px', lineHeight: '1.6' }}>
              {fullReport.detected_symptoms.map((sym, idx) => (
                <li key={idx}>{sym}</li>
              ))}
            </ul>
          ) : (
            <div style={{ fontSize: '14px', color: '#64748b' }}>None detected.</div>
          )}
        </div>
      </div>

      {/* Recommendation & Disclaimer */}
      <div style={{ borderTop: '2px solid #e2e8f0', paddingTop: '20px', marginTop: 'auto' }}>
        <h3 style={{ fontSize: '14px', color: '#0f172a', marginBottom: '8px', textTransform: 'uppercase' }}>Recommendation</h3>
        <p style={{ fontSize: '14px', color: '#334155', margin: '0 0 20px 0', fontWeight: '600' }}>
          {fullReport.recommendation}
        </p>
        
        <p style={{ fontSize: '10px', color: '#94a3b8', margin: 0, lineHeight: '1.4' }}>
          <strong>DISCLAIMER:</strong> {fullReport.disclaimer}
        </p>
      </div>
    </div>
  );
});

export default PdfReportTemplate;
