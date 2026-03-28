import React, { useState } from 'react';

export default function ComplaintForm({ onSubmit }) {
  const [form, setForm] = useState({
    citizen_name: '',
    citizen_contact: '',
    text_input: '',
    location: '',
    image_data: null,
    audio_data: null,
  });
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  const handleChange = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => handleChange('image_data', reader.result);
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.text_input.trim() && !form.image_data) {
      alert('Please provide at least a text description or an image.');
      return;
    }

    setSubmitting(true);
    setResult(null);

    try {
      const res = await onSubmit(form);
      setResult(res);
      setForm({ citizen_name: '', citizen_contact: '', text_input: '', location: '', image_data: null, audio_data: null });
    } catch (err) {
      setResult({ error: err.message });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div id="complaint-form">
      <div className="section-header">
        <h2 className="section-title">➕ Submit New Complaint</h2>
      </div>

      <div className="grid-2">
        <div className="glass-card-static">
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px', color: 'var(--accent-cyan)' }}>
            Complaint Details
          </h3>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Citizen Name</label>
              <input className="form-input" placeholder="Your name"
                     value={form.citizen_name}
                     onChange={e => handleChange('citizen_name', e.target.value)}
                     id="input-citizen-name" />
            </div>

            <div className="form-group">
              <label className="form-label">Contact Number</label>
              <input className="form-input" placeholder="+91-XXXXXXXXXX"
                     value={form.citizen_contact}
                     onChange={e => handleChange('citizen_contact', e.target.value)}
                     id="input-citizen-contact" />
            </div>

            <div className="form-group">
              <label className="form-label">Complaint Description *</label>
              <textarea className="form-textarea"
                        placeholder="Describe the pothole problem, location details, and any urgency..."
                        value={form.text_input}
                        onChange={e => handleChange('text_input', e.target.value)}
                        id="input-complaint-text" />
            </div>

            <div className="form-group">
              <label className="form-label">Location</label>
              <input className="form-input" placeholder="Street name, area, landmark..."
                     value={form.location}
                     onChange={e => handleChange('location', e.target.value)}
                     id="input-location" />
            </div>

            <div className="form-group">
              <label className="form-label">📸 Upload Image</label>
              <input type="file" accept="image/*"
                     onChange={handleImageUpload}
                     className="form-input"
                     id="input-image-upload"
                     style={{ padding: '8px' }} />
              {form.image_data && (
                <div style={{ marginTop: '8px', fontSize: '0.78rem', color: 'var(--accent-green)' }}>
                  ✓ Image attached
                </div>
              )}
            </div>

            <div className="form-group">
              <label className="form-label">🎙️ Audio Complaint</label>
              <button type="button" className="btn btn-ghost" style={{ width: '100%' }}
                      onClick={() => handleChange('audio_data', 'simulated_audio_recording')}
                      id="btn-audio-record">
                {form.audio_data ? '✓ Audio Recorded (Simulated)' : '🎤 Record Audio (Simulated)'}
              </button>
            </div>

            <button type="submit" className="btn btn-primary"
                    style={{ width: '100%', marginTop: '8px', justifyContent: 'center' }}
                    disabled={submitting}
                    id="btn-submit-complaint">
              {submitting ? '⏳ Processing through 5 agents...' : '🚀 Submit Complaint'}
            </button>
          </form>
        </div>

        {/* Result preview */}
        <div className="glass-card-static">
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px', color: 'var(--accent-cyan)' }}>
            🤖 Agent Pipeline Result
          </h3>

          {!result ? (
            <div className="empty-state">
              <div className="empty-state-icon">🔍</div>
              <div className="empty-state-title">Awaiting Submission</div>
              <div className="empty-state-text">
                Submit a complaint to see real-time agent processing results here.
              </div>
              <div style={{ marginTop: '20px', textAlign: 'left' }}>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
                  The complaint will pass through:
                </div>
                {['📥 Agent 1: Intake & Parser', '👁️ Agent 2: Vision & Multimodal AI',
                  '⚖️ Agent 3: Severity Classifier', '🔀 Agent 4: Router & Decision Maker',
                  '📡 Agent 5: Workflow Monitor & SLA'].map((agent, i) => (
                  <div key={i} style={{
                    padding: '8px 12px', marginBottom: '4px',
                    background: 'rgba(0, 0, 0, 0.2)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.82rem',
                    color: 'var(--text-secondary)'
                  }}>
                    {agent}
                  </div>
                ))}
              </div>
            </div>
          ) : result.error ? (
            <div style={{ color: 'var(--accent-red)' }}>Error: {result.error}</div>
          ) : (
            <div className="animate-fade-in">
              <div style={{ marginBottom: '16px', padding: '12px',
                background: 'rgba(16, 185, 129, 0.1)', borderRadius: 'var(--radius-sm)',
                border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                <div style={{ color: 'var(--accent-green)', fontWeight: 700 }}>✅ Complaint Processed!</div>
                <div style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: 'var(--accent-cyan)', marginTop: '4px' }}>
                  {result.complaint?.id}
                </div>
              </div>

              {result.complaint && (
                <div style={{ display: 'grid', gap: '10px' }}>
                  <InfoRow label="Status" value={result.complaint.status} />
                  <InfoRow label="Severity" value={result.complaint.severity_display} />
                  <InfoRow label="Department" value={result.complaint.department_display} />
                  <InfoRow label="SLA" value={result.complaint.sla_display} />
                  <InfoRow label="Agents Run" value={`${result.complaint.agent_count} decisions logged`} />
                  <InfoRow label="Pipeline Time" value={result.complaint.pipeline_duration_display} />
                  <InfoRow label="Auto-corrected" value={result.complaint.auto_corrected ? 'Yes ↩️' : 'No'} />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between',
      padding: '8px 12px', background: 'rgba(0, 0, 0, 0.2)',
      borderRadius: 'var(--radius-sm)' }}>
      <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{label}</span>
      <span style={{ fontSize: '0.82rem', color: 'var(--text-primary)', fontWeight: 600 }}>{value || '—'}</span>
    </div>
  );
}
