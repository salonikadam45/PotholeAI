import React from 'react';

const AGENTS = [
  { id: 'agent-1', name: 'Intake & Parser', desc: 'Text / Image / Audio' },
  { id: 'agent-2', name: 'Vision AI', desc: 'Damage Classification' },
  { id: 'agent-3',  name: 'Severity', desc: 'Score 1-10' },
  { id: 'agent-4', name: 'Router', desc: 'Department Assignment' },
  { id: 'agent-5', name: 'Monitor', desc: 'SLA & Escalation' },
];

export default function AgentPipeline({ pipelineData, complaints }) {
  const agentStatus = pipelineData?.agent_status || {};

  // Count complaints at each stage
  const stageCounts = {};
  if (complaints) {
    const stageMap = {
      'parsing': 'agent-1', 'analyzing': 'agent-2',
      'classifying': 'agent-3', 'routing': 'agent-4',
      'assigned': 'agent-5', 'in_progress': 'agent-5',
    };
    complaints.forEach(c => {
      const agent = stageMap[c.status] || c.current_agent;
      if (agent) stageCounts[agent] = (stageCounts[agent] || 0) + 1;
    });
  }

  return (
    <div className="glass-card-static" id="agent-pipeline">
      <div className="section-header">
        <h2 className="section-title">🔗 Agent Pipeline — Real-Time Flow</h2>
        <span className="badge assigned">
          <span className="badge-dot"></span> LIVE
        </span>
      </div>

      <div className="pipeline-container">
        {AGENTS.map((agent, i) => {
          const status = agentStatus[agent.id];
          const count = stageCounts[agent.id] || 0;
          const isOnline = status?.status === 'online';

          return (
            <React.Fragment key={agent.id}>
              <div className={`pipeline-node ${isOnline ? 'completed' : ''} animate-slide-in`}
                   style={{ animationDelay: `${i * 100}ms` }}>
                <div className="pipeline-node-icon" style={{
                  background: isOnline ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                  color: isOnline ? 'var(--accent-green)' : 'var(--accent-red)'
                }}>
                  {agent.icon}
                </div>
                <div className="pipeline-node-title">{agent.name}</div>
                <div className="pipeline-node-subtitle">{agent.desc}</div>
                {status && (
                  <div style={{ marginTop: '8px', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    Processed: <span style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>
                      {status.processed}
                    </span>
                  </div>
                )}
                {count > 0 && (
                  <div className="badge medium" style={{ marginTop: '6px', fontSize: '0.68rem' }}>
                    <span className="badge-dot"></span> {count} active
                  </div>
                )}
              </div>
              {i < AGENTS.length - 1 && (
                <div className={`pipeline-arrow ${isOnline ? 'active' : ''}`}>→</div>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Self-correction indicator */}
      {pipelineData?.total_auto_corrections > 0 && (
        <div style={{
          marginTop: '12px', padding: '10px 14px',
          background: 'rgba(245, 158, 11, 0.08)',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid rgba(245, 158, 11, 0.15)',
          fontSize: '0.82rem', color: 'var(--accent-amber)'
        }}>
          ↩️ <strong>{pipelineData.total_auto_corrections}</strong> self-corrections triggered
          — Agent 3 detected text-vision severity mismatches and requested re-analysis from Agent 2
        </div>
      )}
    </div>
  );
}
