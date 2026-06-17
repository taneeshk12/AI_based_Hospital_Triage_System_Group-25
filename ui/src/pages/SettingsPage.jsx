import React from 'react';

export default function SettingsPage({ isLightMode, setIsLightMode, apiStatus }) {
  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">Settings</h2>
          <p className="page-subtitle">Configure display preferences and view system information.</p>
        </div>
      </div>

      <div className="settings-grid">
        {/* Appearance */}
        <div className="settings-card glass-panel">
          <div className="settings-card-title">
            <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2" fill="none"><circle cx="12" cy="12" r="10"/><path d="M12 2a10 10 0 0 1 0 20"/><path d="M2 12h20"/></svg>
            Appearance
          </div>
          <div className="settings-row">
            <div>
              <div className="settings-row-label">Interface Theme</div>
              <div className="settings-row-desc">Switch between dark clinical mode and light mode</div>
            </div>
            <button
              className={`theme-toggle-switch ${isLightMode ? 'light' : 'dark'}`}
              onClick={() => setIsLightMode(!isLightMode)}
            >
              <span className="toggle-thumb"></span>
              <span className="toggle-label">{isLightMode ? '☀️ Clinical Light' : '🌙 Dark Terminal'}</span>
            </button>
          </div>
        </div>

        {/* System Info */}
        <div className="settings-card glass-panel">
          <div className="settings-card-title">
            <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2" fill="none"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
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
        <div className="settings-card glass-panel">
          <div className="settings-card-title">
            <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2" fill="none"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            About OmniHealth
          </div>
          <p className="settings-about-text">
            OmniHealth Diagnostics is a <strong>Clinical Multi-Agent Decision Support Engine</strong> built for triage risk stratification. 
            It uses specialized sub-agents for Respiratory, Cardiac, Sepsis, and General Health assessment with real-time SHAP-based explainability.
          </p>
          <div className="settings-models-list">
            <div className="model-badge respiratory">🫁 Respiratory Agent · XGBoost</div>
            <div className="model-badge cardiac">❤️ Cardiac Agent · Random Forest</div>
            <div className="model-badge sepsis">🦠 Sepsis Agent · Gradient Boost</div>
            <div className="model-badge general">🛡️ General Agent · Ensemble</div>
          </div>
        </div>
      </div>
    </div>
  );
}
