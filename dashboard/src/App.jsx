import React, { useState, useEffect, useCallback } from 'react';
import { api } from './hooks/useApi';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import KpiCards from './components/KpiCards';
import AgentPipeline from './components/AgentPipeline';
import ComplaintsFeed from './components/ComplaintsFeed';
import SlaTracker from './components/SlaTracker';
import DepartmentView from './components/DepartmentView';
import AuditTrail from './components/AuditTrail';
import NotificationLog from './components/NotificationLog';
import ComplaintForm from './components/ComplaintForm';

const TAB_TITLES = {
  overview: { title: 'System Overview', subtitle: 'Real-time pipeline health & KPIs' },
  pipeline: { title: 'Agent Pipeline', subtitle: 'Multi-agent workflow visualization' },
  complaints: { title: 'Complaints Feed', subtitle: 'All complaints with severity & status' },
  sla: { title: 'SLA Tracker', subtitle: 'Breaches, stalls & escalations' },
  departments: { title: 'Departments', subtitle: 'Workload distribution & performance' },
  audit: { title: 'Audit Trail', subtitle: 'Every agent decision logged' },
  notifications: { title: 'Notifications', subtitle: 'Citizen communication log' },
  submit: { title: 'New Complaint', subtitle: 'Submit multimodal complaint' },
};

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({
    pipeline: null,
    complaints: null,
    sla: null,
    departments: null,
    audit: null,
    notifications: null,
  });

  const refreshData = useCallback(async () => {
    setLoading(true);
    try {
      const [pipeline, complaints, sla, departments, audit, notifications] = await Promise.all([
        api.getPipelineStatus(),
        api.getComplaints(),
        api.getSlaBreaches(),
        api.getDepartments(),
        api.getAuditLog(100),
        api.getNotifications(50),
      ]);

      setData({
        pipeline,
        complaints: complaints?.complaints || [],
        sla,
        departments: departments?.departments || [],
        audit,
        notifications,
      });
    } catch (err) {
      console.error('Failed to refresh data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshData();
    const interval = setInterval(refreshData, 10000); // Auto-refresh every 10s
    return () => clearInterval(interval);
  }, [refreshData]);

  const handleSeedData = async () => {
    await api.seedDemoData(20);
    await refreshData();
  };

  const handleHealthCheck = async () => {
    await api.runHealthCheck();
    await refreshData();
  };

  const handleSubmitComplaint = async (formData) => {
    const result = await api.submitComplaint(formData);
    await refreshData();
    return result;
  };

  const tabInfo = TAB_TITLES[activeTab] || { title: 'Dashboard', subtitle: '' };

  return (
    <div className="app-layout">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <div className="main-content">
        <Topbar
          title={tabInfo.title}
          subtitle={tabInfo.subtitle}
          onSeedData={handleSeedData}
          onHealthCheck={handleHealthCheck}
        />
        <div className="page-content">
          {loading && !data.pipeline ? (
            <div className="empty-state">
              <div className="empty-state-icon" style={{ animation: 'spin 1s linear infinite' }}>⚙️</div>
              <div className="empty-state-title">Connecting to Backend...</div>
              <div className="empty-state-text">
                Make sure the FastAPI backend is running on port 8000.
                <br /><code style={{ color: 'var(--accent-cyan)' }}>
                  py -m uvicorn backend.main:app --port 8000
                </code>
              </div>
            </div>
          ) : (
            <>
              {/* ═══ Overview Tab ═══ */}
              {activeTab === 'overview' && (
                <div className="animate-fade-in">
                  <KpiCards data={data.pipeline} />
                  <div className="grid-2" style={{ marginBottom: '24px' }}>
                    <div className="glass-card-static">
                      <h3 className="section-title" style={{ marginBottom: '14px' }}>
                        📊 Status Distribution
                      </h3>
                      <StatusChart complaints={data.complaints} />
                    </div>
                    <div className="glass-card-static">
                      <h3 className="section-title" style={{ marginBottom: '14px' }}>
                        🏢 Department Load
                      </h3>
                      <DeptChart departments={data.departments} />
                    </div>
                  </div>
                  <AgentPipeline pipelineData={data.pipeline} complaints={data.complaints} />
                </div>
              )}

              {/* ═══ Pipeline Tab ═══ */}
              {activeTab === 'pipeline' && (
                <div className="animate-fade-in">
                  <AgentPipeline pipelineData={data.pipeline} complaints={data.complaints} />
                  <div style={{ marginTop: '24px' }}>
                    <AgentDetailCards pipeline={data.pipeline} />
                  </div>
                </div>
              )}

              {/* ═══ Complaints Tab ═══ */}
              {activeTab === 'complaints' && (
                <div className="animate-fade-in">
                  <ComplaintsFeed complaints={data.complaints} />
                </div>
              )}

              {/* ═══ SLA Tab ═══ */}
              {activeTab === 'sla' && (
                <div className="animate-fade-in">
                  <SlaTracker slaData={data.sla} />
                </div>
              )}

              {/* ═══ Departments Tab ═══ */}
              {activeTab === 'departments' && (
                <div className="animate-fade-in">
                  <DepartmentView departments={data.departments} />
                </div>
              )}

              {/* ═══ Audit Tab ═══ */}
              {activeTab === 'audit' && (
                <div className="animate-fade-in">
                  <AuditTrail auditData={data.audit} />
                </div>
              )}

              {/* ═══ Notifications Tab ═══ */}
              {activeTab === 'notifications' && (
                <div className="animate-fade-in">
                  <NotificationLog notifications={data.notifications} />
                </div>
              )}

              {/* ═══ Submit Tab ═══ */}
              {activeTab === 'submit' && (
                <div className="animate-fade-in">
                  <ComplaintForm onSubmit={handleSubmitComplaint} />
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}


/* ─── Helper Charts ──────────────────────────────────────────────────────── */

function StatusChart({ complaints }) {
  if (!complaints?.length) return <div className="empty-state-text">No data</div>;

  const counts = {};
  complaints.forEach(c => {
    counts[c.status] = (counts[c.status] || 0) + 1;
  });

  const statusColors = {
    assigned: 'var(--accent-cyan)',
    resolved: 'var(--accent-green)',
    stalled: 'var(--accent-amber)',
    escalated: 'var(--accent-red)',
    in_progress: 'var(--accent-blue)',
    received: 'var(--accent-purple)',
  };

  const maxCount = Math.max(...Object.values(counts));

  return (
    <div>
      <div className="bar-chart" style={{ height: '160px', marginBottom: '24px' }}>
        {Object.entries(counts).map(([status, count]) => (
          <div key={status} className="bar"
               style={{
                 height: `${(count / maxCount) * 100}%`,
                 background: statusColors[status] || 'var(--accent-cyan)',
                 opacity: 0.8
               }}>
            <div style={{
              position: 'absolute', top: '-22px', left: '50%', transform: 'translateX(-50%)',
              fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-primary)'
            }}>
              {count}
            </div>
            <div className="bar-label">{status}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function DeptChart({ departments }) {
  if (!departments?.length) return <div className="empty-state-text">No data</div>;

  const deptColors = [
    'var(--accent-cyan)', 'var(--accent-red)', 'var(--accent-amber)',
    'var(--accent-purple)', 'var(--accent-green)'
  ];

  return (
    <div className="donut-container" style={{ flexDirection: 'column' }}>
      <div className="donut-legend" style={{ width: '100%' }}>
        {departments.map((dept, i) => {
          const total = dept.active_tickets + dept.resolved_tickets;
          return (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '8px 12px', background: 'rgba(0,0,0,0.2)', borderRadius: 'var(--radius-sm)'
            }}>
              <div className="legend-item">
                <div className="legend-dot" style={{ background: deptColors[i % deptColors.length] }}></div>
                <span>{dept.department}</span>
              </div>
              <span style={{ fontWeight: 700, color: deptColors[i % deptColors.length] }}>{total}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function AgentDetailCards({ pipeline }) {
  if (!pipeline?.agent_status) return null;

  const agents = Object.entries(pipeline.agent_status);
  const agentDescriptions = {
    'agent-1': 'Parses text, images, and audio input into structured complaint data. Extracts location, urgency, and complaint type.',
    'agent-2': 'Analyzes images using simulated vision AI. Classifies damage type, estimates area, detects hazards.',
    'agent-3': 'Combines text urgency, vision damage, and location risk into weighted severity score (1-10).',
    'agent-4': 'Routes complaint to correct department based on multi-signal decision tree. Sets SLA deadlines.',
    'agent-5': 'Monitors SLA compliance, detects stalls, manages escalation ladder, sends citizen notifications.',
  };
  const agentIcons = { 'agent-1': '📥', 'agent-2': '👁️', 'agent-3': '⚖️', 'agent-4': '🔀', 'agent-5': '📡' };

  return (
    <div>
      <h3 className="section-title" style={{ marginBottom: '16px' }}>🤖 Agent Details</h3>
      <div className="grid-3">
        {agents.map(([id, info], i) => (
          <div key={id} className="glass-card animate-slide-in" style={{ animationDelay: `${i * 80}ms` }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
              <span style={{ fontSize: '1.5rem' }}>{agentIcons[id]}</span>
              <div>
                <div style={{ fontWeight: 700 }}>{info.name}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontFamily: 'monospace' }}>{id}</div>
              </div>
            </div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '12px', lineHeight: 1.5 }}>
              {agentDescriptions[id]}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="badge resolved">
                <span className="badge-dot"></span> {info.status}
              </span>
              <span style={{ fontSize: '0.82rem', color: 'var(--accent-cyan)', fontWeight: 700 }}>
                {info.processed} processed
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


export default App;
