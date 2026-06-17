import React from 'react';

export default function TopBar({
  activePage,
  patientName, setPatientName,
  currentPatientId,
  apiStatus,
  isLightMode, setIsLightMode,
  saveStatus, onSave,
  onNewPatient,
  loading,
}) {
  const pageLabels = {
    intake: 'Triage Intake',
    results: 'Results & Analysis',
    simulator: 'What-If Simulator',
    registry: 'Patient Registry',
    settings: 'Settings',
  };

  return (
    <header className="topbar">
      {/* Left: page breadcrumb */}
      <div className="topbar-left">
        <div className="topbar-page-label">
          <span className="topbar-page-name">{pageLabels[activePage] || 'Dashboard'}</span>
        </div>

        {/* Patient name inline edit */}
        <div className="topbar-patient-input-wrapper">
          <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" style={{ opacity: 0.5 }}>
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          <input
            id="patient-name-topbar"
            type="text"
            value={patientName}
            onChange={e => setPatientName(e.target.value)}
            placeholder="Patient name..."
            className="topbar-patient-input"
          />
        </div>

        {/* Patient ID chip */}
        <div className="topbar-pid-chip">
          <span className="topbar-pid-label">ID</span>
          <code className="topbar-pid-value">{currentPatientId}</code>
        </div>
      </div>

      {/* Right: actions + status */}
      <div className="topbar-right">
        {/* API Status */}
        <div className={`topbar-api-status ${apiStatus ? 'online' : 'offline'}`}>
          <span className="topbar-status-dot"></span>
          <span>{apiStatus ? 'Engine Online' : 'Engine Offline'}</span>
        </div>

        {/* Save button */}
        <button
          className={`topbar-btn save-btn ${saveStatus === 'saving' ? 'saving' : saveStatus === 'saved' ? 'saved' : saveStatus === 'error' ? 'error' : ''}`}
          onClick={onSave}
          disabled={saveStatus === 'saving' || loading}
        >
          {saveStatus === 'saving' && <><span className="spinner" style={{ width: '12px', height: '12px', borderWidth: '1.5px' }}></span> Saving...</>}
          {saveStatus === 'saved' && <>✓ Saved</>}
          {saveStatus === 'error' && <>⚠ Failed</>}
          {!saveStatus && (
            <>
              <svg viewBox="0 0 24 24" width="13" height="13" stroke="currentColor" strokeWidth="2" fill="none">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                <polyline points="17 21 17 13 7 13 7 21"/>
                <polyline points="7 3 7 8 15 8"/>
              </svg>
              Save
            </>
          )}
        </button>

        {/* New Patient */}
        <button className="topbar-btn new-btn" onClick={onNewPatient} title="Start new patient">
          <svg viewBox="0 0 24 24" width="13" height="13" stroke="currentColor" strokeWidth="2.5" fill="none">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          New Patient
        </button>

        {/* Theme toggle */}
        <button className="topbar-btn theme-btn" onClick={() => setIsLightMode(!isLightMode)} title="Toggle theme">
          {isLightMode ? (
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2" fill="none">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2" fill="none">
              <circle cx="12" cy="12" r="5"/>
              <line x1="12" y1="1" x2="12" y2="3"/>
              <line x1="12" y1="21" x2="12" y2="23"/>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
              <line x1="1" y1="12" x2="3" y2="12"/>
              <line x1="21" y1="12" x2="23" y2="12"/>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
            </svg>
          )}
        </button>
      </div>
    </header>
  );
}
