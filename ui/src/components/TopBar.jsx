import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { motion } from 'framer-motion';

export default function TopBar({
  activePage,
  apiStatus,
  isLightMode, setIsLightMode,
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
        <motion.div 
          initial={{ x: -10, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          key={activePage}
          className="topbar-page-label"
        >
          <span className="topbar-page-name">{pageLabels[activePage] || 'Dashboard'}</span>
        </motion.div>
      </div>

      {/* Right: actions + status */}
      <div className="topbar-right">
        {/* API Status */}
        <div className={`topbar-api-status ${apiStatus ? 'online' : 'offline'}`}>
          <span className="topbar-status-dot"></span>
          <span>{apiStatus ? 'Engine Online' : 'Engine Offline'}</span>
        </div>

        {/* Theme toggle */}
        <button
          className="topbar-btn theme-btn"
          onClick={() => setIsLightMode(!isLightMode)}
          title={isLightMode ? 'Switch to dark mode' : 'Switch to light mode'}
        >
          {isLightMode ? <Sun size={16} /> : <Moon size={16} />}
        </button>
      </div>
    </header>
  );
}
