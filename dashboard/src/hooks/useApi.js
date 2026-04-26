/**
 * API hooks for communicating with the FastAPI backend.
 */

const API_BASE = 'http://localhost:8000/api';

async function fetchJSON(url, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${url}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (err) {
    console.error(`API Error [${url}]:`, err);
    return null;
  }
}

export const api = {
  // Complaints
  getComplaints: (status, dept) => {
    const params = new URLSearchParams();
    if (status) params.set('status', status);
    if (dept) params.set('department', dept);
    return fetchJSON(`/complaints?${params}`);
  },
  submitComplaint: (data) => fetchJSON('/complaints', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getComplaint: (id) => fetchJSON(`/complaints/${id}`),
  getComplaintAudit: (id) => fetchJSON(`/complaints/${id}/audit`),
  resolveComplaint: (id, notes, proof) => fetchJSON(
    `/complaints/${id}/resolve?resolution_notes=${encodeURIComponent(notes || 'Repair completed')}${proof ? `&proof_url=${encodeURIComponent(proof)}` : ''}`,
    { method: 'POST' }
  ),

  // Pipeline
  getPipelineStatus: () => fetchJSON('/pipeline/status'),
  runHealthCheck: () => fetchJSON('/pipeline/health-check', { method: 'POST' }),

  // Departments
  getDepartments: () => fetchJSON('/departments'),

  // SLA
  getSlaBreaches: () => fetchJSON('/sla/breaches'),

  // Audit
  getAuditLog: (count = 50) => fetchJSON(`/audit?count=${count}`),

  // Notifications
  getNotifications: (count = 50) => fetchJSON(`/notifications?count=${count}`),

  // Demo
  seedDemoData: (count = 20) => fetchJSON(`/demo/seed?count=${count}`, { method: 'POST' }),

  // Health
  getHealth: () => fetchJSON('/health'),

  // Heatmap
  getHeatmap: () => fetchJSON('/heatmap'),

  // Agent Scorecards
  getAgentScorecards: () => fetchJSON('/agents/scorecards'),
};
