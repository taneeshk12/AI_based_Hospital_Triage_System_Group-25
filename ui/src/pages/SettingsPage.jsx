import React from 'react';
import { Sun, Moon, Monitor, Info, Layout } from 'lucide-react';

export default function SettingsPage({ apiStatus, isLightMode, setIsLightMode }) {
  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">Settings</h2>
          <p className="page-subtitle">View system information and configure interface preferences.</p>
        </div>
      </div>

      <div className="settings-grid">
        {/* Appearance Settings */}
        <div className="settings-card glass-panel">
          <div className="settings-card-title">
            <Layout size={18} />
            Appearance Configuration
          </div>
          <p className="settings-about-text" style={{ marginBottom: '1.2rem' }}>
            Select your preferred display mode. The high-contrast clinical themes are optimized to prevent eye strain during long shifts.
          </p>
          <div className="theme-selector-group" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <button 
              className={`theme-select-card ${!isLightMode ? 'active' : ''}`}
              onClick={() => setIsLightMode(false)}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '8px',
                padding: '16px',
                borderRadius: '12px',
                border: '2px solid ' + (!isLightMode ? 'var(--accent-blue)' : 'var(--border-color)'),
                background: !isLightMode ? 'rgba(59, 130, 246, 0.08)' : 'var(--input-bg)',
                color: 'var(--text-primary)',
                cursor: 'pointer',
                fontFamily: 'inherit',
                fontWeight: 600,
                transition: 'all 0.2s'
              }}
            >
              <Moon size={24} color={!isLightMode ? '#3b82f6' : 'var(--text-muted)'} />
              <span>Dark Clinical</span>
            </button>
            <button 
              className={`theme-select-card ${isLightMode ? 'active' : ''}`}
              onClick={() => setIsLightMode(true)}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '8px',
                padding: '16px',
                borderRadius: '12px',
                border: '2px solid ' + (isLightMode ? 'var(--accent-blue)' : 'var(--border-color)'),
                background: isLightMode ? 'rgba(37, 99, 235, 0.08)' : 'var(--input-bg)',
                color: 'var(--text-primary)',
                cursor: 'pointer',
                fontFamily: 'inherit',
                fontWeight: 600,
                transition: 'all 0.2s'
              }}
            >
              <Sun size={24} color={isLightMode ? '#2563eb' : 'var(--text-muted)'} />
              <span>Light Clinical</span>
            </button>
          </div>
        </div>

        {/* System Info */}
        <div className="settings-card glass-panel">
          <div className="settings-card-title">
            <Monitor size={18} />
            System Information
          </div>
          <div className="settings-info-table">
            <div className="settings-info-row">
              <span>API Engine</span>
              <span className={`api-status-pill ${apiStatus ? 'online' : 'offline'}`}>
                <span className="status-dot"></span>
                {apiStatus ? 'Connected' : 'Offline'}
              </span>
            </div>
            <div className="settings-info-row">
              <span>API Endpoint</span>
              <code>http://localhost:8000</code>
            </div>
            <div className="settings-info-row">
              <span>Application Version</span>
              <span>v2.0.0</span>
            </div>
            <div className="settings-info-row">
              <span>AI Engine</span>
              <span>HCAI Multi-Agent v2</span>
            </div>
          </div>
        </div>

        {/* About */}
        <div className="settings-card glass-panel" style={{ gridColumn: 'span 2' }}>
          <div className="settings-card-title">
            <Info size={18} />
            About OmniHealth
          </div>
          <p className="settings-about-text">
            OmniHealth Diagnostics is a <strong>Clinical Multi-Agent Decision Support Engine</strong> built for triage risk stratification. 
            It uses specialized sub-agents for Respiratory, Cardiac, Sepsis, and General Health assessment with real-time SHAP-based explainability.
          </p>
          <div className="settings-models-list" style={{ marginTop: '1.2rem' }}>
            <div className="model-badge respiratory">🫁 Respiratory Agent · Random Forest</div>
            <div className="model-badge cardiac">❤️ Cardiac Agent · XGBoost</div>
            <div className="model-badge sepsis">🦠 Sepsis Agent · XGBoost</div>
            <div className="model-badge general">🛡️ General Agent · XGBoost</div>
          </div>
        </div>
      </div>
    </div>
  );
}
