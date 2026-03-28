import React from 'react';

const TYPE_ICONS = {
  received: { icon: '📥', color: 'var(--accent-purple)', bg: 'rgba(139, 92, 246, 0.15)' },
  assigned: { icon: '🏢', color: 'var(--accent-cyan)', bg: 'rgba(0, 212, 255, 0.15)' },
  in_progress: { icon: '🔧', color: 'var(--accent-blue)', bg: 'rgba(59, 130, 246, 0.15)' },
  escalated: { icon: '🚨', color: 'var(--accent-red)', bg: 'rgba(239, 68, 68, 0.15)' },
  resolved: { icon: '✅', color: 'var(--accent-green)', bg: 'rgba(16, 185, 129, 0.15)' },
  stalled: { icon: '⏳', color: 'var(--accent-amber)', bg: 'rgba(245, 158, 11, 0.15)' },
  update: { icon: '📌', color: 'var(--text-secondary)', bg: 'rgba(148, 163, 184, 0.1)' },
};

export default function NotificationLog({ notifications }) {
  if (!notifications || !notifications.notifications?.length) {
    return (
      <div className="glass-card-static">
        <div className="empty-state">
          <div className="empty-state-icon">🔔</div>
          <div className="empty-state-title">No Notifications</div>
          <div className="empty-state-text">Process complaints to generate citizen notifications.</div>
        </div>
      </div>
    );
  }

  const notifs = notifications.notifications;

  return (
    <div id="notification-log">
      <div className="section-header">
        <h2 className="section-title">🔔 Citizen Notifications</h2>
        <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          {notifications.total_notifications} total sent
        </span>
      </div>

      <div className="glass-card-static" style={{ padding: 0 }}>
        {notifs.map((n, i) => {
          const typeInfo = TYPE_ICONS[n.notification_type] || TYPE_ICONS.update;
          return (
            <div key={n.id || i}
                 className="notif-item animate-slide-in"
                 style={{ animationDelay: `${i * 40}ms` }}>
              <div className="notif-icon" style={{ background: typeInfo.bg, color: typeInfo.color }}>
                {typeInfo.icon}
              </div>
              <div className="notif-content">
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span style={{ fontFamily: 'monospace', fontSize: '0.72rem', color: 'var(--accent-cyan)' }}>
                    {n.complaint_id}
                  </span>
                  <span className={`badge ${n.notification_type === 'resolved' ? 'resolved' :
                    n.notification_type === 'escalated' ? 'escalated' : 'assigned'}`}
                    style={{ fontSize: '0.65rem', padding: '1px 6px' }}>
                    {n.notification_type}
                  </span>
                  <span style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>
                    via {n.channel}
                  </span>
                </div>
                <div className="notif-message">{n.message}</div>
                <div className="notif-time">
                  {new Date(n.timestamp).toLocaleString()}
                  {n.delivered && <span style={{ color: 'var(--accent-green)', marginLeft: '8px' }}>✓ Delivered</span>}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
