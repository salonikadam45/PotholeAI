import React from 'react';

export default function KpiCards({ data }) {
  if (!data) return null;

  const cards = [
    {
      icon: '📥', label: 'Total Complaints', value: data.total_complaints,
      color: 'cyan', change: `${data.total_audit_entries} audit entries`,
    },
    {
      icon: '⚡', label: 'Active Pipeline', value: data.active_complaints,
      color: 'amber', change: `${data.resolved_complaints} resolved`,
    },
    {
      icon: '✅', label: 'SLA Compliance', value: `${data.sla_compliance_rate}%`,
      color: 'green', change: data.sla_compliance_rate >= 90 ? '↑ On Target' : '↓ Below Target',
      changeType: data.sla_compliance_rate >= 90 ? 'positive' : 'negative',
    },
    {
      icon: '🤖', label: 'Autonomous Rate', value: `${data.autonomous_success_rate}%`,
      color: 'purple', change: `${data.total_auto_corrections} self-corrections`,
    },
    {
      icon: '🚨', label: 'Stalled / Escalated',
      value: `${data.stalled_count} / ${data.escalated_count}`,
      color: 'red', change: `${data.total_errors_recovered} errors recovered`,
    },
    {
      icon: '🔔', label: 'Notifications Sent', value: data.total_notifications,
      color: 'cyan', change: 'Citizen updates',
    },
  ];

  return (
    <div className="kpi-grid" id="kpi-cards">
      {cards.map((card, i) => (
        <div key={i} className={`kpi-card ${card.color} animate-slide-in`}
             style={{ animationDelay: `${i * 60}ms` }}>
          <div className={`kpi-icon ${card.color}`}>{card.icon}</div>
          <div className="kpi-value">{card.value}</div>
          <div className="kpi-label">{card.label}</div>
          <div className={`kpi-change ${card.changeType || ''}`}>{card.change}</div>
        </div>
      ))}
    </div>
  );
}
