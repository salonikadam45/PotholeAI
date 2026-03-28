import React from 'react';
import './Topbar.css';

export default function Topbar({ title, subtitle, onSeedData, onHealthCheck }) {
  return (
    <header className="topbar" id="main-topbar">
      <div className="topbar-left">
        <h1 className="topbar-title">{title}</h1>
        {subtitle && <span className="topbar-subtitle">{subtitle}</span>}
      </div>
      <div className="topbar-right">
        <button className="btn btn-ghost topbar-btn" onClick={onHealthCheck} id="btn-health-check">
          🩺 Health Check
        </button>
        <button className="btn btn-primary topbar-btn" onClick={onSeedData} id="btn-seed-data">
          ⚡ Seed Demo Data
        </button>
        <div className="topbar-time">
          <span className="live-dot"></span>
          {new Date().toLocaleTimeString()}
        </div>
      </div>
    </header>
  );
}
