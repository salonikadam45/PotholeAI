import React, { useState } from 'react';

function getSeverityBadge(complaint) {
  const sev = complaint.severity;
  if (!sev) return <span className="badge received">Pending</span>;
  const level = sev.severity_level;
  return (
    <span className={`badge ${level}`}>
      <span className="badge-dot"></span>
      {sev.severity_score}/10 {level}
    </span>
  );
}

function getStatusBadge(status) {
  const map = {
    received: 'received', parsing: 'assigned', analyzing: 'assigned',
    classifying: 'assigned', routing: 'assigned', assigned: 'assigned',
    in_progress: 'medium', stalled: 'stalled', escalated: 'escalated',
    resolved: 'resolved', closed: 'resolved',
  };
  return <span className={`badge ${map[status] || 'received'}`}>
    <span className="badge-dot"></span> {status}
  </span>;
}

export default function ComplaintsFeed({ complaints, onSelectComplaint, onComplaintClick }) {
  const handleClick = onComplaintClick || onSelectComplaint;
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  
  if (!complaints || !complaints.length) {
    return (
      <div className="glass-card-static">
        <div className="empty-state">
          <div className="empty-state-icon">📋</div>
          <div className="empty-state-title">No Complaints Yet</div>
          <div className="empty-state-text">Seed demo data or submit a complaint to get started.</div>
        </div>
      </div>
    );
  }

  let filtered = complaints;
  if (filter !== 'all') {
    filtered = complaints.filter(c => c.status === filter);
  }
  if (search) {
    const q = search.toLowerCase();
    filtered = filtered.filter(c =>
      c.id.toLowerCase().includes(q) ||
      c.text_input?.toLowerCase().includes(q) ||
      c.location?.toLowerCase().includes(q) ||
      c.citizen_name?.toLowerCase().includes(q)
    );
  }

  return (
    <div className="glass-card-static" id="complaints-feed">
      <div className="section-header">
        <h2 className="section-title">📋 Complaints Feed</h2>
        <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          {filtered.length} of {complaints.length} — click any row to view details
        </span>
      </div>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '16px', flexWrap: 'wrap' }}>
        <input
          className="form-input"
          placeholder="Search by ID, text, location..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ maxWidth: '300px' }}
          id="complaints-search"
        />
        {['all', 'assigned', 'stalled', 'escalated', 'resolved'].map(f => (
          <button key={f}
            className={`btn ${filter === f ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setFilter(f)}
            style={{ padding: '6px 14px', fontSize: '0.78rem' }}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Citizen</th>
              <th>Location</th>
              <th>Status</th>
              <th>Severity</th>
              <th>Department</th>
              <th>SLA</th>
              <th>Pipeline</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(c => (
              <tr key={c.id} style={{ cursor: 'pointer' }}
                  onClick={() => handleClick && handleClick(c.id)}>
                <td className="primary" style={{ color: 'var(--accent-cyan)', fontFamily: 'monospace' }}>
                  {c.id}
                </td>
                <td>{c.citizen_name}</td>
                <td className="primary">{c.location || c.parsed?.extracted_location || '—'}</td>
                <td>{getStatusBadge(c.status)}</td>
                <td>{getSeverityBadge(c)}</td>
                <td style={{ fontSize: '0.78rem' }}>
                  {c.department_display || '—'}
                </td>
                <td>
                  {c.sla_display ? (
                    <span style={{
                      color: c.sla?.breached ? 'var(--accent-red)' :
                             (c.sla?.time_remaining_hours < 12 ? 'var(--accent-amber)' : 'var(--accent-green)'),
                      fontSize: '0.78rem', fontWeight: 600
                    }}>
                      {c.sla_display}
                    </span>
                  ) : '—'}
                </td>
                <td style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  {c.pipeline_duration_display}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
