import React from 'react';

export default function SlaTracker({ slaData }) {
  if (!slaData) return null;

  return (
    <div id="sla-tracker">
      {/* SLA Summary Cards */}
      <div className="kpi-grid" style={{ marginBottom: '24px' }}>
        <div className="kpi-card red">
          <div className="kpi-icon red">🚨</div>
          <div className="kpi-value">{slaData.total_breached}</div>
          <div className="kpi-label">SLA Breached</div>
        </div>
        <div className="kpi-card amber">
          <div className="kpi-icon amber">⏳</div>
          <div className="kpi-value">{slaData.total_stalled}</div>
          <div className="kpi-label">Stalled Tickets</div>
        </div>
        <div className="kpi-card cyan">
          <div className="kpi-icon cyan">⚡</div>
          <div className="kpi-value">{slaData.total_approaching}</div>
          <div className="kpi-label">Approaching Deadline</div>
        </div>
      </div>

      {/* Breached Complaints */}
      {slaData.breached?.length > 0 && (
        <div className="glass-card-static" style={{ marginBottom: '20px' }}>
          <h3 className="section-title" style={{ marginBottom: '14px' }}>
            🚨 SLA Breaches
          </h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Complaint ID</th>
                <th>Location</th>
                <th>Department</th>
                <th>SLA Window</th>
                <th>Escalation</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {slaData.breached.map(c => (
                <tr key={c.id}>
                  <td className="primary" style={{ fontFamily: 'monospace', color: 'var(--accent-red)' }}>
                    {c.id}
                  </td>
                  <td>{c.location || '—'}</td>
                  <td>{c.department_display || '—'}</td>
                  <td>{c.sla?.sla_hours}h</td>
                  <td>
                    <span className="badge escalated">
                      {c.sla?.escalation_level || 'none'}
                    </span>
                  </td>
                  <td><span className="badge escalated">{c.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Stalled Complaints */}
      {slaData.stalled?.length > 0 && (
        <div className="glass-card-static" style={{ marginBottom: '20px' }}>
          <h3 className="section-title" style={{ marginBottom: '14px' }}>
            ⏳ Stalled Tickets
          </h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Complaint ID</th>
                <th>Location</th>
                <th>Department</th>
                <th>Time Remaining</th>
                <th>Last Activity</th>
              </tr>
            </thead>
            <tbody>
              {slaData.stalled.map(c => (
                <tr key={c.id}>
                  <td className="primary" style={{ fontFamily: 'monospace', color: 'var(--accent-amber)' }}>
                    {c.id}
                  </td>
                  <td>{c.location || '—'}</td>
                  <td>{c.department_display || '—'}</td>
                  <td style={{ color: 'var(--accent-amber)' }}>
                    {c.sla?.time_remaining_hours}h
                  </td>
                  <td style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    {c.sla?.last_activity ? new Date(c.sla.last_activity).toLocaleString() : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {slaData.total_breached === 0 && slaData.total_stalled === 0 && (
        <div className="glass-card-static">
          <div className="empty-state">
            <div className="empty-state-icon">✅</div>
            <div className="empty-state-title">All Clear</div>
            <div className="empty-state-text">No SLA breaches or stalled tickets. System is healthy.</div>
          </div>
        </div>
      )}
    </div>
  );
}
