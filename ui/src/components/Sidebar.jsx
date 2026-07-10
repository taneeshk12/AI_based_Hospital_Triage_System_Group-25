import React from 'react';
import { 
  ClipboardPlus, 
  Activity, 
  GitBranch, 
  Users, 
  ShieldCheck, 
  Settings, 
  Stethoscope, 
  ChevronLeft, 
  ChevronRight,
  Home
} from 'lucide-react';
import { motion } from 'framer-motion';

const NAV_ITEMS = [
  { id: 'landing', label: 'Welcome', icon: <Home size={20} /> },
  { id: 'intake', label: 'Triage Intake', icon: <ClipboardPlus size={20} /> },
  { id: 'results', label: 'Results & Analysis', icon: <Activity size={20} /> },
  { id: 'simulator', label: 'What-If Simulator', icon: <GitBranch size={20} /> },
  { id: 'registry', label: 'Patient Registry', icon: <Users size={20} /> },
  { id: 'evaluation', label: 'Safety Evaluation', icon: <ShieldCheck size={20} /> },
  { id: 'settings', label: 'Settings', icon: <Settings size={20} /> },
];

export default function Sidebar({ activePage, setActivePage, collapsed, setCollapsed, patientsList, hasResults }) {
  return (
    <motion.aside 
      initial={false}
      animate={{ width: collapsed ? 72 : 260 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className={`sidebar ${collapsed ? 'collapsed' : ''}`}
    >
      {/* Logo / Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-logo">
          <Stethoscope size={24} />
        </div>
        {!collapsed && (
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            transition={{ delay: 0.1 }}
            className="sidebar-brand-text"
          >
            <span className="sidebar-brand-name">OmniHealth</span>
            <span className="sidebar-brand-sub">Clinical AI</span>
          </motion.div>
        )}
      </div>

      {/* Collapse toggle */}
      <button className="sidebar-collapse-btn" onClick={() => setCollapsed(!collapsed)} title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}>
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>

      {/* Nav items */}
      <nav className="sidebar-nav">
        {NAV_ITEMS.map(item => {
          const isActive = activePage === item.id;
          const isDisabled = (item.id === 'results' || item.id === 'simulator') && !hasResults;
          const badge = item.id === 'registry' && patientsList.length > 0 ? patientsList.length : null;

          return (
            <button
              key={item.id}
              className={`sidebar-nav-item ${isActive ? 'active' : ''} ${isDisabled ? 'disabled' : ''}`}
              onClick={() => !isDisabled && setActivePage(item.id)}
              title={collapsed ? item.label : undefined}
              disabled={isDisabled}
            >
              <span className="nav-icon">{item.icon}</span>
              {!collapsed && (
                <motion.span 
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                  className="nav-label"
                >
                  {item.label}
                </motion.span>
              )}
              {badge && !collapsed && <span className="nav-badge">{badge}</span>}
              {badge && collapsed && <span className="nav-badge-dot"></span>}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        {!collapsed && <span className="sidebar-version">v2.0 · HCAI Engine</span>}
        {collapsed && <span className="sidebar-version-dot">v2</span>}
      </div>
    </motion.aside>
  );
}
