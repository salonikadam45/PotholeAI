import React, { useEffect, useRef, useState } from 'react';
import './Heatmap.css';

// We use Leaflet via CDN approach with vanilla JS inside React
// to avoid complex react-leaflet setup issues
export default function Heatmap({ heatmapData }) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const [selectedZone, setSelectedZone] = useState(null);
  const [view, setView] = useState('map'); // 'map' or 'table'

  useEffect(() => {
    if (!heatmapData?.points?.length || !mapRef.current) return;
    if (mapInstanceRef.current) return; // already initialized

    // Dynamically load Leaflet CSS
    if (!document.getElementById('leaflet-css')) {
      const link = document.createElement('link');
      link.id = 'leaflet-css';
      link.rel = 'stylesheet';
      link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      document.head.appendChild(link);
    }

    // Dynamically load Leaflet JS
    const loadLeaflet = () => {
      return new Promise((resolve) => {
        if (window.L) { resolve(window.L); return; }
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
        script.onload = () => resolve(window.L);
        document.head.appendChild(script);
      });
    };

    loadLeaflet().then((L) => {
      const center = heatmapData.center || { lat: 18.5204, lng: 73.8567 };
      const map = L.map(mapRef.current, {
        zoomControl: true,
        scrollWheelZoom: true,
      }).setView([center.lat, center.lng], heatmapData.zoom || 13);

      // Dark map tiles
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '© CartoDB',
        maxZoom: 19,
      }).addTo(map);

      // Add markers for each complaint location
      heatmapData.points.forEach((point) => {
        const color = getMarkerColor(point.priority_score);
        const radius = Math.max(12, Math.min(35, point.count * 8 + point.avg_severity * 2));

        // Circle marker with glow effect
        const circle = L.circleMarker([point.lat, point.lng], {
          radius: radius,
          fillColor: color,
          color: color,
          weight: 2,
          opacity: 0.9,
          fillOpacity: 0.35,
        }).addTo(map);

        // Inner dot
        L.circleMarker([point.lat, point.lng], {
          radius: 5,
          fillColor: color,
          color: '#fff',
          weight: 1,
          opacity: 1,
          fillOpacity: 1,
        }).addTo(map);

        // Popup
        circle.bindPopup(`
          <div style="font-family:Inter,sans-serif;font-size:13px;min-width:200px">
            <div style="font-weight:700;font-size:14px;margin-bottom:6px;color:#111">
              📍 ${point.location}
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;margin-bottom:6px">
              <div><strong>${point.count}</strong> complaints</div>
              <div>Severity: <strong>${point.avg_severity}/10</strong></div>
              <div style="color:#ef4444"><strong>${point.critical}</strong> critical</div>
              <div style="color:#f59e0b"><strong>${point.high}</strong> high</div>
              <div>Active: <strong>${point.active}</strong></div>
              <div>Resolved: <strong>${point.resolved}</strong></div>
            </div>
            <div style="padding:6px 8px;border-radius:6px;text-align:center;font-weight:700;color:#fff;
              background:${color}">
              Priority Score: ${point.priority_score}/10
            </div>
          </div>
        `, { className: 'dark-popup' });

        circle.on('click', () => {
          setSelectedZone(point);
        });
      });

      mapInstanceRef.current = map;

      // Fix map sizing
      setTimeout(() => map.invalidateSize(), 200);
    });

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [heatmapData]);

  if (!heatmapData?.points?.length) {
    return (
      <div className="glass-card-static">
        <div className="empty-state">
          <div className="empty-state-icon">🗺️</div>
          <div className="empty-state-title">No Heatmap Data</div>
          <div className="empty-state-text">Seed demo data or submit complaints to see the heatmap.</div>
        </div>
      </div>
    );
  }

  const topZones = heatmapData.points.slice(0, 10);

  return (
    <div id="heatmap-view">
      {/* View toggle */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        <button className={`btn ${view === 'map' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setView('map')}>
          🗺️ Map View
        </button>
        <button className={`btn ${view === 'table' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setView('table')}>
          📊 Priority Table
        </button>
      </div>

      <div className="heatmap-layout">
        {/* Map / Table */}
        <div className="heatmap-main">
          {view === 'map' ? (
            <div className="glass-card-static heatmap-card">
              <div className="section-header">
                <h2 className="section-title">🗺️ Complaint Heatmap — Priority Zones</h2>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  {heatmapData.total_locations} locations
                </span>
              </div>
              <div ref={mapRef} className="heatmap-container"></div>
              <div className="heatmap-legend">
                <span className="legend-entry"><span className="legend-circle critical"></span> Critical (8-10)</span>
                <span className="legend-entry"><span className="legend-circle high"></span> High (6-8)</span>
                <span className="legend-entry"><span className="legend-circle medium"></span> Medium (4-6)</span>
                <span className="legend-entry"><span className="legend-circle low"></span> Low (0-4)</span>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginLeft: '12px' }}>
                  Circle size = complaint density
                </span>
              </div>
            </div>
          ) : (
            <div className="glass-card-static">
              <div className="section-header">
                <h2 className="section-title">📊 Reconstruction Priority Ranking</h2>
              </div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Location</th>
                    <th>Complaints</th>
                    <th>Avg Severity</th>
                    <th>Critical</th>
                    <th>Active</th>
                    <th>Breached</th>
                    <th>Priority Score</th>
                  </tr>
                </thead>
                <tbody>
                  {heatmapData.points.map((p, i) => (
                    <tr key={p.location}
                        style={{ cursor: 'pointer' }}
                        onClick={() => setSelectedZone(p)}
                        className={selectedZone?.location === p.location ? 'row-selected' : ''}>
                      <td>
                        <span className={`rank-badge rank-${i < 3 ? 'top' : 'normal'}`}>
                          {i + 1}
                        </span>
                      </td>
                      <td className="primary">📍 {p.location}</td>
                      <td style={{ fontWeight: 700 }}>{p.count}</td>
                      <td>
                        <span style={{ color: getSeverityColor(p.avg_severity), fontWeight: 700 }}>
                          {p.avg_severity}/10
                        </span>
                      </td>
                      <td style={{ color: p.critical > 0 ? 'var(--accent-red)' : 'var(--text-dim)', fontWeight: 700 }}>
                        {p.critical}
                      </td>
                      <td style={{ color: 'var(--accent-amber)' }}>{p.active}</td>
                      <td style={{ color: p.breached > 0 ? 'var(--accent-red)' : 'var(--text-dim)' }}>
                        {p.breached}
                      </td>
                      <td>
                        <div className="priority-cell">
                          <div className="priority-bar-bg">
                            <div className="priority-bar-fill"
                                 style={{
                                   width: `${p.priority_score * 10}%`,
                                   background: getMarkerColor(p.priority_score)
                                 }}></div>
                          </div>
                          <span style={{ color: getMarkerColor(p.priority_score), fontWeight: 800 }}>
                            {p.priority_score}
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Sidebar: Top Priority Zones */}
        <div className="heatmap-sidebar">
          <div className="glass-card-static">
            <h3 className="section-title" style={{ marginBottom: '14px' }}>
              🔥 Top Priority Zones
            </h3>
            {topZones.map((zone, i) => (
              <div key={zone.location}
                   className={`priority-zone-card ${selectedZone?.location === zone.location ? 'selected' : ''}`}
                   onClick={() => setSelectedZone(zone)}>
                <div className="zone-rank" style={{ background: getMarkerColor(zone.priority_score) }}>
                  #{i + 1}
                </div>
                <div className="zone-info">
                  <div className="zone-name">{zone.location}</div>
                  <div className="zone-meta">
                    <span>{zone.count} complaints</span>
                    <span>•</span>
                    <span style={{ color: getSeverityColor(zone.avg_severity) }}>
                      Sev: {zone.avg_severity}
                    </span>
                  </div>
                  <div className="zone-breakdown">
                    {zone.critical > 0 && <span className="zone-tag critical">{zone.critical} critical</span>}
                    {zone.high > 0 && <span className="zone-tag high">{zone.high} high</span>}
                    {zone.breached > 0 && <span className="zone-tag breached">{zone.breached} breached</span>}
                  </div>
                </div>
                <div className="zone-score" style={{ color: getMarkerColor(zone.priority_score) }}>
                  {zone.priority_score}
                </div>
              </div>
            ))}
          </div>

          {/* Selected zone details */}
          {selectedZone && (
            <div className="glass-card-static animate-slide-in" style={{ marginTop: '16px' }}>
              <h3 className="section-title" style={{ marginBottom: '12px' }}>
                📍 {selectedZone.location}
              </h3>
              <div className="zone-detail-grid">
                <DetailStat label="Total Complaints" value={selectedZone.count} color="var(--accent-cyan)" />
                <DetailStat label="Avg Severity" value={`${selectedZone.avg_severity}/10`}
                            color={getSeverityColor(selectedZone.avg_severity)} />
                <DetailStat label="Critical" value={selectedZone.critical} color="var(--accent-red)" />
                <DetailStat label="High" value={selectedZone.high} color="var(--accent-amber)" />
                <DetailStat label="Medium" value={selectedZone.medium} color="var(--accent-cyan)" />
                <DetailStat label="Low" value={selectedZone.low} color="var(--accent-green)" />
                <DetailStat label="Active" value={selectedZone.active} color="var(--accent-amber)" />
                <DetailStat label="Resolved" value={selectedZone.resolved} color="var(--accent-green)" />
                <DetailStat label="SLA Breached" value={selectedZone.breached} color="var(--accent-red)" />
                <DetailStat label="Priority Score" value={`${selectedZone.priority_score}/10`}
                            color={getMarkerColor(selectedZone.priority_score)} />
              </div>
              <div style={{ marginTop: '12px', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                Complaint IDs: {selectedZone.complaint_ids?.join(', ')}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function DetailStat({ label, value, color }) {
  return (
    <div className="zone-detail-stat">
      <div className="zone-detail-value" style={{ color }}>{value}</div>
      <div className="zone-detail-label">{label}</div>
    </div>
  );
}

function getMarkerColor(score) {
  if (score >= 8) return '#ef4444';
  if (score >= 6) return '#f59e0b';
  if (score >= 4) return '#00d4ff';
  return '#10b981';
}

function getSeverityColor(severity) {
  if (severity >= 8) return 'var(--accent-red)';
  if (severity >= 6) return 'var(--accent-amber)';
  if (severity >= 4) return 'var(--accent-cyan)';
  return 'var(--accent-green)';
}
