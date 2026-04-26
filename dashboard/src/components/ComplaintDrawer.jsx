import React, { useState, useEffect } from 'react';
import { api } from '../hooks/useApi';
import './ComplaintDrawer.css';

export default function ComplaintDrawer({ complaintId, onClose }) {
  const [complaint, setComplaint] = useState(null);
  const [auditTrail, setAuditTrail] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState('pipeline');

  useEffect(() => {
    if (!complaintId) return;
    setLoading(true);
    Promise.all([
      api.getComplaint(complaintId),
      api.getComplaintAudit(complaintId),
    ]).then(([comp, audit]) => {
      setComplaint(comp);
      setAuditTrail(audit?.entries || []);
      setLoading(false);
    });
  }, [complaintId]);

  if (!complaintId) return null;

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        {/* Close button */}
        <button className="drawer-close" onClick={onClose}>✕</button>

        {loading ? (
          <div className="drawer-loading">
            <div className="empty-state-icon" style={{ animation: 'spin 1s linear infinite' }}>⚙️</div>
            <div>Loading complaint details...</div>
          </div>
        ) : complaint ? (
          <>
            {/* Header */}
            <div className="drawer-header">
              <div className="drawer-id">{complaint.id}</div>
              <h2 className="drawer-title">
                {complaint.text_input?.slice(0, 80)}
                {complaint.text_input?.length > 80 ? '...' : ''}
              </h2>
              <div className="drawer-meta">
                <span className={`badge ${complaint.status}`}>
                  <span className="badge-dot"></span>
                  {complaint.status}
                </span>
                {complaint.severity_display && (
                  <span className="drawer-severity" style={{ color: getSeverityColor(complaint.severity?.severity_score || 0) }}>
                    Severity: {complaint.severity_display}
                  </span>
                )}
                {complaint.department_display && (
                  <span className="drawer-dept">🏢 {complaint.department_display}</span>
                )}
              </div>
            </div>

            {/* Section tabs */}
            <div className="drawer-tabs">
              <button className={`drawer-tab ${activeSection === 'pipeline' ? 'active' : ''}`}
                      onClick={() => setActiveSection('pipeline')}>🔗 Pipeline Journey</button>
              <button className={`drawer-tab ${activeSection === 'audit' ? 'active' : ''}`}
                      onClick={() => setActiveSection('audit')}>📝 Audit Trail</button>
              <button className={`drawer-tab ${activeSection === 'details' ? 'active' : ''}`}
                      onClick={() => setActiveSection('details')}>📄 Raw Data</button>
            </div>

            {/* Pipeline Journey */}
            {activeSection === 'pipeline' && (
              <div className="drawer-section animate-fade-in">
                <div className="pipeline-journey">
                  {/* Info cards row */}
                  <div className="journey-info-row">
                    <InfoCard label="Citizen" value={complaint.citizen_name || 'Anonymous'} icon="👤" />
                    <InfoCard label="Location" value={complaint.location || 'Unknown'} icon="📍" />
                    <InfoCard label="Pipeline Time" value={complaint.pipeline_duration_display} icon="⏱️" />
                    <InfoCard label="Agents Run" value={complaint.agent_count} icon="🤖" />
                  </div>

                  {/* Agent decision timeline */}
                  <h3 className="drawer-subtitle">Agent Decision Timeline</h3>
                  <div className="agent-journey-timeline">
                    {(complaint.agent_decisions || []).map((decision, i) => (
                      <div key={i} className="journey-step animate-slide-in" style={{ animationDelay: `${i * 80}ms` }}>
                        <div className="journey-node">
                          <div className="journey-node-dot" style={{
                            background: decision.confidence >= 0.7 ? '#10b981' :
                                        decision.confidence >= 0.5 ? '#f59e0b' : '#ef4444'
                          }}></div>
                          {i < (complaint.agent_decisions || []).length - 1 && <div className="journey-connector"></div>}
                        </div>
                        <div className="journey-card glass-card-static">
                          <div className="journey-card-header">
                            <span className="journey-agent-icon">{getAgentIcon(decision.agent_id)}</span>
                            <div className="journey-agent-info">
                              <span className="journey-agent-name">{decision.agent_name}</span>
                              <span className="journey-agent-id">{decision.agent_id}</span>
                            </div>
                            <div className="journey-confidence">
                              <span style={{ color: decision.confidence >= 0.7 ? '#10b981' : decision.confidence >= 0.5 ? '#f59e0b' : '#ef4444' }}>
                                {(decision.confidence * 100).toFixed(0)}%
                              </span>
                              <span className="journey-duration">{decision.duration_ms}ms</span>
                            </div>
                          </div>
                          <div className="journey-card-body">
                            <div className="journey-row">
                              <span className="journey-label">Input:</span>
                              <span className="journey-value">{decision.input_summary}</span>
                            </div>
                            <div className="journey-row">
                              <span className="journey-label">Output:</span>
                              <span className="journey-value output">{decision.output_summary}</span>
                            </div>
                            <div className="journey-reasoning">
                              <span className="journey-label">Reasoning:</span>
                              <p>{decision.reasoning}</p>
                            </div>
                            {decision.error && (
                              <div className="journey-error">
                                ⚠️ {decision.error}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Self-correction indicator */}
                  {complaint.auto_corrected && (
                    <div className="self-correction-banner">
                      <span>🔄</span>
                      <div>
                        <strong>Self-Correction Triggered</strong>
                        <p>Agent 3 detected a text-vision severity mismatch. Agent 2 was re-run for re-analysis and the severity was recalculated.</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Audit Trail */}
            {activeSection === 'audit' && (
              <div className="drawer-section animate-fade-in">
                <h3 className="drawer-subtitle">📝 Complete Audit Trail ({auditTrail.length} entries)</h3>
                <div className="drawer-audit-list">
                  {auditTrail.map((entry, i) => (
                    <div key={i} className="drawer-audit-entry animate-slide-in" style={{ animationDelay: `${i * 40}ms` }}>
                      <div className="drawer-audit-dot" style={{
                        background: getActionColor(entry.action)
                      }}></div>
                      <div className="drawer-audit-content">
                        <div className="drawer-audit-header">
                          <span className="drawer-audit-agent" style={{ color: getActionColor(entry.action) }}>
                            {entry.agent_name}
                          </span>
                          <span className="drawer-audit-time">
                            {new Date(entry.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="drawer-audit-action">{entry.action}</div>
                        <div className="drawer-audit-reasoning">{entry.reasoning}</div>
                        <div className="drawer-audit-outcome">{entry.outcome}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Raw Data */}
            {activeSection === 'details' && (
              <div className="drawer-section animate-fade-in">
                <h3 className="drawer-subtitle">📄 Full Complaint Data</h3>
                <pre className="drawer-json">
                  {JSON.stringify(complaint, null, 2)}
                </pre>
              </div>
            )}
          </>
        ) : (
          <div className="drawer-loading">Complaint not found.</div>
        )}
      </div>
    </div>
  );
}

function InfoCard({ label, value, icon }) {
  return (
    <div className="journey-info-card">
      <span className="journey-info-icon">{icon}</span>
      <div>
        <div className="journey-info-value">{value}</div>
        <div className="journey-info-label">{label}</div>
      </div>
    </div>
  );
}

function getAgentIcon(agentId) {
  const icons = {
    'agent-1': '📥', 'agent-2': '👁️', 'agent-3': '⚖️',
    'agent-4': '🔀', 'agent-5': '📡',
  };
  return icons[agentId] || '🤖';
}

function getSeverityColor(score) {
  if (score >= 8) return '#ef4444';
  if (score >= 6) return '#f59e0b';
  if (score >= 4) return '#00d4ff';
  return '#10b981';
}

function getActionColor(action) {
  if (action.includes('error') || action.includes('fail')) return '#ef4444';
  if (action.includes('correction') || action.includes('duplicate')) return '#f59e0b';
  if (action.includes('complete') || action.includes('resolved')) return '#10b981';
  return '#00d4ff';
}
