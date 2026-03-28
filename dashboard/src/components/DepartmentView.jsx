import React from 'react';

const DEPT_ICONS = {
  'Roads & Infrastructure': '🛣️',
  'Emergency Services': '🚨',
  'Traffic Management': '🚦',
  'Urban Planning': '🏙️',
  'Utilities': '⚡',
};

const DEPT_COLORS = {
  'Roads & Infrastructure': 'var(--accent-cyan)',
  'Emergency Services': 'var(--accent-red)',
  'Traffic Management': 'var(--accent-amber)',
  'Urban Planning': 'var(--accent-purple)',
  'Utilities': 'var(--accent-green)',
};

export default function DepartmentView({ departments }) {
  if (!departments || !departments.length) {
    return (
      <div className="glass-card-static">
        <div className="empty-state">
          <div className="empty-state-icon">🏢</div>
          <div className="empty-state-title">No Department Data</div>
          <div className="empty-state-text">Process complaints to see department assignments.</div>
        </div>
      </div>
    );
  }

  return (
    <div id="department-view">
      <div className="section-header">
        <h2 className="section-title">🏢 Department Workload</h2>
      </div>

      <div className="grid-3" style={{ marginBottom: '24px' }}>
        {departments.map((dept, i) => {
          const color = DEPT_COLORS[dept.department] || 'var(--accent-cyan)';
          const icon = DEPT_ICONS[dept.department] || '🏢';
          const total = dept.active_tickets + dept.resolved_tickets;

          return (
            <div key={i} className="dept-card animate-slide-in"
                 style={{ animationDelay: `${i * 80}ms` }}>
              <div className="dept-name" style={{ color }}>
                {icon} {dept.department}
              </div>

              <div className="dept-stats">
                <div className="dept-stat">
                  <div className="dept-stat-value" style={{ color: 'var(--accent-amber)' }}>
                    {dept.active_tickets}
                  </div>
                  <div className="dept-stat-label">Active</div>
                </div>
                <div className="dept-stat">
                  <div className="dept-stat-value" style={{ color: 'var(--accent-green)' }}>
                    {dept.resolved_tickets}
                  </div>
                  <div className="dept-stat-label">Resolved</div>
                </div>
                <div className="dept-stat">
                  <div className="dept-stat-value" style={{ color: 'var(--accent-red)' }}>
                    {dept.sla_breach_count}
                  </div>
                  <div className="dept-stat-label">Breaches</div>
                </div>
                <div className="dept-stat">
                  <div className="dept-stat-value" style={{ color }}>
                    {dept.avg_response_hours}h
                  </div>
                  <div className="dept-stat-label">Avg Response</div>
                </div>
              </div>

              <div style={{ marginTop: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                  <span>Completion Rate</span>
                  <span style={{ color, fontWeight: 700 }}>{dept.completion_rate}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill cyan"
                       style={{ width: `${dept.completion_rate}%`, background: color }}></div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary table */}
      <div className="glass-card-static">
        <h3 className="section-title" style={{ marginBottom: '14px' }}>📊 Summary Table</h3>
        <table className="data-table">
          <thead>
            <tr>
              <th>Department</th>
              <th>Active</th>
              <th>Resolved</th>
              <th>SLA Breaches</th>
              <th>Avg Response</th>
              <th>Completion</th>
            </tr>
          </thead>
          <tbody>
            {departments.map((dept, i) => (
              <tr key={i}>
                <td className="primary">{DEPT_ICONS[dept.department]} {dept.department}</td>
                <td style={{ color: 'var(--accent-amber)' }}>{dept.active_tickets}</td>
                <td style={{ color: 'var(--accent-green)' }}>{dept.resolved_tickets}</td>
                <td style={{ color: 'var(--accent-red)' }}>{dept.sla_breach_count}</td>
                <td>{dept.avg_response_hours}h</td>
                <td style={{ fontWeight: 600 }}>{dept.completion_rate}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
