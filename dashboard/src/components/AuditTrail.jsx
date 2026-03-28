import React, { useState } from 'react';

const AGENT_COLORS = {
  'agent-1': 'var(--accent-cyan)',
  'agent-2': 'var(--accent-blue)',
  'agent-3': 'var(--accent-amber)',
  'agent-4': 'var(--accent-purple)',
  'agent-5': 'var(--accent-green)',
  'orchestrator': 'var(--accent-pink)',
};

const ACTION_ICONS = {
  'sla_breach_detected': '🚨',
  'stall_detected': '⏳',
  'self_correction_triggered': '↩️',
  'agent_error_recovery': '🔄',
  'pipeline_complete': '✅',
  'complaint_received': '📥',
  'complaint_resolved': '🎉',
  'routing_decision': '🔀',
  'severity_classified': '⚖️',
  'text_intake': '📝',
  'image_analysis_start': '👁️',
  'analysis_complete': '🔍',
  'health_check_passed': '💚',
  'ticket_created': '🎫',
  default: '📌',
};

function getIcon(action) {
  return ACTION_ICONS[action] || ACTION_ICONS.default;
}

function getTimelineClass(entry) {
  if (entry.action.includes('error') || entry.action.includes('breach') || entry.action.includes('fail'))
    return 'error';
  if (entry.action.includes('complete') || entry.action.includes('resolved') || entry.action.includes('health_check_passed'))
    return 'success';
  if (entry.action.includes('stall') || entry.action.includes('correction') || entry.action.includes('warning'))
    return 'warning';
  return '';
}

export default function AuditTrail({ auditData }) {
  const [filter, setFilter] = useState('all');
  const [expanded, setExpanded] = useState(null);

  if (!auditData || !auditData.entries?.length) {
    return (
      <div className="glass-card-static">
        <div className="empty-state">
          <div className="empty-state-icon">📝</div>
          <div className="empty-state-title">No Audit Entries</div>
          <div className="empty-state-text">Process complaints to generate audit trail.</div>
        </div>
      </div>
    );
  }

  const entries = auditData.entries;
  const agents = [...new Set(entries.map(e => e.agent_id))];
  
  let filtered = entries;
  if (filter !== 'all') {
    filtered = entries.filter(e => e.agent_id === filter);
  }

  return (
    <div id="audit-trail">
      <div className="section-header">
        <h2 className="section-title">📝 Full Audit Trail</h2>
        <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          {auditData.total_entries} total entries
        </span>
      </div>

      {/* Filter tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
        <button className={`btn ${filter === 'all' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setFilter('all')}
                style={{ padding: '6px 14px', fontSize: '0.78rem' }}>
          All ({entries.length})
        </button>
        {agents.map(a => (
          <button key={a}
            className={`btn ${filter === a ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setFilter(a)}
            style={{
              padding: '6px 14px', fontSize: '0.78rem',
              borderColor: filter === a ? AGENT_COLORS[a] : undefined
            }}>
            {a} ({entries.filter(e => e.agent_id === a).length})
          </button>
        ))}
      </div>

      <div className="glass-card-static">
        <div className="timeline">
          {filtered.slice(0, 50).map((entry, i) => (
            <div key={entry.id || i}
                 className={`timeline-item ${getTimelineClass(entry)} animate-slide-in`}
                 style={{ animationDelay: `${i * 30}ms`, cursor: 'pointer' }}
                 onClick={() => setExpanded(expanded === i ? null : i)}>
              <div className="timeline-time">
                {new Date(entry.timestamp).toLocaleString()}
              </div>
              <div className="timeline-agent" style={{ color: AGENT_COLORS[entry.agent_id] || 'var(--accent-cyan)' }}>
                {getIcon(entry.action)} {entry.agent_name}
              </div>
              <div className="timeline-action">{entry.action.replace(/_/g, ' ')}</div>
              <div className="timeline-detail">{entry.outcome}</div>
              
              {expanded === i && (
                <div style={{
                  marginTop: '8px', padding: '12px',
                  background: 'rgba(0, 0, 0, 0.3)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.78rem',
                  animation: 'fadeIn 0.2s ease'
                }}>
                  <div style={{ marginBottom: '4px' }}>
                    <strong style={{ color: 'var(--text-muted)' }}>Complaint:</strong>{' '}
                    <span style={{ fontFamily: 'monospace', color: 'var(--accent-cyan)' }}>
                      {entry.complaint_id}
                    </span>
                  </div>
                  <div style={{ marginBottom: '4px' }}>
                    <strong style={{ color: 'var(--text-muted)' }}>Reasoning:</strong>{' '}
                    <span style={{ color: 'var(--text-secondary)' }}>{entry.reasoning}</span>
                  </div>
                  <div>
                    <strong style={{ color: 'var(--text-muted)' }}>Outcome:</strong>{' '}
                    <span style={{ color: 'var(--text-secondary)' }}>{entry.outcome}</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
