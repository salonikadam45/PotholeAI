import React from 'react';
import './AgentScorecards.css';

export default function AgentScorecards({ scorecardData }) {
  if (!scorecardData?.scorecards?.length) {
    return (
      <div className="glass-card-static">
        <div className="empty-state">
          <div className="empty-state-icon">🤖</div>
          <div className="empty-state-title">No Agent Data</div>
          <div className="empty-state-text">Seed demo data to see agent performance metrics.</div>
        </div>
      </div>
    );
  }

  const { scorecards, system_metrics } = scorecardData;

  return (
    <div id="agent-scorecards-view">
      {/* System-wide metrics bar */}
      <div className="glass-card-static system-metrics-bar">
        <div className="sys-metric">
          <div className="sys-metric-value">{system_metrics.total_decisions}</div>
          <div className="sys-metric-label">Total Decisions</div>
        </div>
        <div className="sys-metric">
          <div className="sys-metric-value" style={{ color: 'var(--accent-green)' }}>
            {system_metrics.autonomous_rate}%
          </div>
          <div className="sys-metric-label">Autonomous Rate</div>
        </div>
        <div className="sys-metric">
          <div className="sys-metric-value" style={{ color: 'var(--accent-cyan)' }}>
            {(system_metrics.overall_avg_confidence * 100).toFixed(1)}%
          </div>
          <div className="sys-metric-label">Avg Confidence</div>
        </div>
        <div className="sys-metric">
          <div className="sys-metric-value" style={{ color: 'var(--accent-amber)' }}>
            {system_metrics.total_self_corrections}
          </div>
          <div className="sys-metric-label">Self-Corrections</div>
        </div>
        <div className="sys-metric">
          <div className="sys-metric-value" style={{ color: system_metrics.total_errors > 0 ? 'var(--accent-red)' : 'var(--accent-green)' }}>
            {system_metrics.total_errors}
          </div>
          <div className="sys-metric-label">Errors Recovered</div>
        </div>
      </div>

      {/* Individual agent scorecards */}
      <div className="scorecard-grid">
        {scorecards.map((card, i) => (
          <div key={card.agent_id} className="glass-card-static scorecard animate-slide-in"
               style={{ animationDelay: `${i * 100}ms` }}>
            {/* Header */}
            <div className="scorecard-header">
              <div className="scorecard-agent-info">
                <span className="scorecard-icon">{card.icon}</span>
                <div>
                  <div className="scorecard-name">{card.name}</div>
                  <div className="scorecard-id">{card.agent_id}</div>
                </div>
              </div>
              <div className="reliability-ring">
                <svg viewBox="0 0 36 36" className="circular-chart">
                  <path className="circle-bg"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                  <path className="circle-fill"
                    strokeDasharray={`${card.reliability_score}, 100`}
                    style={{ stroke: getReliabilityColor(card.reliability_score) }}
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                </svg>
                <div className="reliability-value" style={{ color: getReliabilityColor(card.reliability_score) }}>
                  {card.reliability_score}
                </div>
              </div>
            </div>

            {/* Metrics grid */}
            <div className="scorecard-metrics">
              <MetricRow label="Processed" value={card.total_processed} icon="📊" />
              <MetricRow label="Avg Duration" value={`${card.avg_duration_ms}ms`} icon="⏱️" />
              <MetricRow label="Avg Confidence" 
                value={`${(card.avg_confidence * 100).toFixed(1)}%`}
                icon="🎯"
                color={card.avg_confidence >= 0.7 ? 'var(--accent-green)' : card.avg_confidence >= 0.5 ? 'var(--accent-amber)' : 'var(--accent-red)'} />
              <MetricRow label="Errors" value={card.error_count}
                icon="❌"
                color={card.error_count > 0 ? 'var(--accent-red)' : 'var(--accent-green)'} />
              <MetricRow label="Self-Corrections" value={card.self_corrections}
                icon="🔄"
                color={card.self_corrections > 0 ? 'var(--accent-amber)' : 'var(--text-dim)'} />
              <MetricRow label="Error Rate" value={`${card.error_rate}%`}
                icon="📉"
                color={card.error_rate > 5 ? 'var(--accent-red)' : 'var(--accent-green)'} />
            </div>

            {/* Confidence distribution */}
            <div className="confidence-dist">
              <div className="conf-bar-label">Confidence Distribution</div>
              <div className="conf-bar-container">
                <div className="conf-bar conf-high"
                     style={{ width: `${card.total_processed ? (card.high_confidence_count / card.total_processed * 100) : 0}%` }}>
                  {card.high_confidence_count > 0 && <span>{card.high_confidence_count}</span>}
                </div>
                <div className="conf-bar conf-mid"
                     style={{ width: `${card.total_processed ? ((card.total_processed - card.high_confidence_count - card.low_confidence_count) / card.total_processed * 100) : 0}%` }}>
                  {(card.total_processed - card.high_confidence_count - card.low_confidence_count) > 0 &&
                    <span>{card.total_processed - card.high_confidence_count - card.low_confidence_count}</span>}
                </div>
                <div className="conf-bar conf-low"
                     style={{ width: `${card.total_processed ? (card.low_confidence_count / card.total_processed * 100) : 0}%` }}>
                  {card.low_confidence_count > 0 && <span>{card.low_confidence_count}</span>}
                </div>
              </div>
              <div className="conf-legend">
                <span><span className="dot high"></span>High</span>
                <span><span className="dot mid"></span>Mid</span>
                <span><span className="dot low"></span>Low</span>
              </div>
            </div>

            {/* Status badge */}
            <div className="scorecard-footer">
              <span className="badge resolved"><span className="badge-dot"></span>{card.status}</span>
              <span className="scorecard-reliability-label">Reliability Score</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function MetricRow({ label, value, icon, color }) {
  return (
    <div className="metric-row">
      <span className="metric-row-icon">{icon}</span>
      <span className="metric-row-label">{label}</span>
      <span className="metric-row-value" style={color ? { color } : {}}>{value}</span>
    </div>
  );
}

function getReliabilityColor(score) {
  if (score >= 90) return '#10b981';
  if (score >= 70) return '#00d4ff';
  if (score >= 50) return '#f59e0b';
  return '#ef4444';
}
