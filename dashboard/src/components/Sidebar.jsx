import React from 'react';
import './Sidebar.css';

const NAV_ITEMS = [
  { id: 'overview', icon: '📊', label: 'Overview' },
  { id: 'pipeline', icon: '🔗', label: 'Agent Pipeline' },
  { id: 'complaints', icon: '📋', label: 'Complaints Feed' },
  { id: 'heatmap', icon: '🗺️', label: 'Priority Heatmap' },
  { id: 'sla', icon: '⚠️', label: 'SLA Tracker' },
  { id: 'departments', icon: '🏢', label: 'Departments' },
  { id: 'audit', icon: '📝', label: 'Audit Trail' },
  { id: 'scorecards', icon: '🏆', label: 'Agent Scorecards' },
  { id: 'notifications', icon: '🔔', label: 'Notifications' },
  { id: 'submit', icon: '➕', label: 'New Complaint' },
];

export default function Sidebar({ activeTab, onTabChange }) {
  return (
    <aside className="sidebar" id="main-sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <span className="logo-icon">🛣️</span>
          <div>
            <div className="logo-title">PotholeAI</div>
            <div className="logo-subtitle">Command Center</div>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-label">Dashboard</div>
        {NAV_ITEMS.slice(0, 4).map(item => (
          <button
            key={item.id}
            id={`nav-${item.id}`}
            className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
            onClick={() => onTabChange(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}

        <div className="nav-section-label">Monitoring</div>
        {NAV_ITEMS.slice(4, 8).map(item => (
          <button
            key={item.id}
            id={`nav-${item.id}`}
            className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
            onClick={() => onTabChange(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}

        <div className="nav-section-label">Actions</div>
        {NAV_ITEMS.slice(8).map(item => (
          <button
            key={item.id}
            id={`nav-${item.id}`}
            className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
            onClick={() => onTabChange(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="system-status">
          <span className="status-dot online"></span>
          <span className="status-text">All Agents Online</span>
        </div>
        <div className="sidebar-version">v1.0.0 — Multi-Agent System</div>
      </div>
    </aside>
  );
}
