"""
Multi-Agent Pothole Complaint System — FastAPI Backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models import ComplaintSubmission
from backend.orchestrator import ProcessOrchestrator

app = FastAPI(
    title="Pothole Complaint Multi-Agent System",
    description="AI-powered multi-agent system for managing citizen pothole complaints",
    version="1.0.0"
)

# CORS for React dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator (single instance)
orchestrator = ProcessOrchestrator()


# ─── Complaint Endpoints ─────────────────────────────────────────────────────

@app.get("/api/complaints")
def list_complaints(status: str = None, department: str = None):
    """List all complaints with optional filters."""
    complaints = list(orchestrator.complaints.values())
    
    if status:
        complaints = [c for c in complaints if c.status.value == status]
    if department:
        complaints = [c for c in complaints if c.department_ticket and c.department_ticket.department.value == department]
    
    # Sort by submitted_at descending
    complaints.sort(key=lambda c: c.submitted_at, reverse=True)
    
    return {
        "count": len(complaints),
        "complaints": [_serialize_complaint(c) for c in complaints]
    }


@app.post("/api/complaints")
def submit_complaint(submission: ComplaintSubmission):
    """Submit a new complaint and run it through the agent pipeline."""
    complaint = orchestrator.submit_complaint(submission)
    return {
        "message": f"Complaint {complaint.id} processed successfully",
        "complaint": _serialize_complaint(complaint)
    }


@app.get("/api/complaints/{complaint_id}")
def get_complaint(complaint_id: str):
    """Get full complaint detail including agent pipeline results."""
    complaint = orchestrator.complaints.get(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return _serialize_complaint(complaint)


@app.get("/api/complaints/{complaint_id}/audit")
def get_complaint_audit(complaint_id: str):
    """Get full audit trail for a complaint."""
    entries = orchestrator.audit_logger.get_by_complaint(complaint_id)
    return {
        "complaint_id": complaint_id,
        "count": len(entries),
        "entries": [e.model_dump(mode="json") for e in entries]
    }


# ─── Pipeline Endpoints ──────────────────────────────────────────────────────

@app.get("/api/pipeline/status")
def pipeline_status():
    """Get real-time pipeline health metrics."""
    return orchestrator.get_pipeline_health()


@app.post("/api/pipeline/health-check")
def run_health_check():
    """Trigger Agent 5 health check on all active complaints."""
    result = orchestrator.run_health_check()
    return {"message": "Health check completed", "summary": result}


# ─── Department Endpoints ─────────────────────────────────────────────────────

@app.get("/api/departments")
def get_departments():
    """Get department workload and SLA stats."""
    return {"departments": orchestrator.get_department_stats()}


# ─── SLA Endpoints ────────────────────────────────────────────────────────────

@app.get("/api/sla/breaches")
def get_sla_breaches():
    """Get all SLA breaches and stalled tickets."""
    all_complaints = list(orchestrator.complaints.values())
    breached = orchestrator.sla_engine.get_breached(all_complaints)
    stalled = orchestrator.sla_engine.get_stalled(all_complaints)
    approaching = orchestrator.sla_engine.get_approaching_deadline(all_complaints)
    
    return {
        "breached": [_serialize_complaint(c) for c in breached],
        "stalled": [_serialize_complaint(c) for c in stalled],
        "approaching_deadline": [_serialize_complaint(c) for c in approaching],
        "total_breached": len(breached),
        "total_stalled": len(stalled),
        "total_approaching": len(approaching)
    }


# ─── Audit Endpoints ─────────────────────────────────────────────────────────

@app.get("/api/audit")
def get_audit_log(count: int = 50):
    """Get recent audit trail entries."""
    entries = orchestrator.audit_logger.get_recent(count)
    return {
        "total_entries": orchestrator.audit_logger.count(),
        "entries": [e.model_dump(mode="json") for e in entries]
    }


# ─── Notification Endpoints ──────────────────────────────────────────────────

@app.get("/api/notifications")
def get_notifications(count: int = 50):
    """Get recent citizen notifications."""
    notifications = orchestrator.notification_service.get_recent(count)
    return {
        "total_notifications": orchestrator.notification_service.count(),
        "notifications": [n.model_dump(mode="json") for n in notifications]
    }


# ─── Resolution Endpoints ────────────────────────────────────────────────────

@app.post("/api/complaints/{complaint_id}/resolve")
def resolve_complaint(complaint_id: str, resolution_notes: str = "Repair completed", proof_url: str = None):
    """Mark a complaint as resolved."""
    complaint = orchestrator.resolve_complaint(complaint_id, resolution_notes, proof_url)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return {"message": "Complaint resolved", "complaint": _serialize_complaint(complaint)}


# ─── Demo Endpoints ──────────────────────────────────────────────────────────

@app.post("/api/demo/seed")
def seed_demo_data(count: int = 20):
    """Seed realistic demo complaints for testing."""
    orchestrator.seed_demo_data(count)
    return {
        "message": f"Seeded {count} demo complaints",
        "total_complaints": len(orchestrator.complaints)
    }


# ─── Heatmap Endpoints ───────────────────────────────────────────────────────

# Simulated geo-coordinates for demo locations
LOCATION_COORDS = {
    "Main Street": {"lat": 18.5204, "lng": 73.8567},
    "Oak Avenue": {"lat": 18.5304, "lng": 73.8467},
    "Highway 12 Exit Ramp": {"lat": 18.5504, "lng": 73.8267},
    "Commerce Drive": {"lat": 18.5104, "lng": 73.8767},
    "Park Road": {"lat": 18.5254, "lng": 73.8517},
    "5th Street Intersection": {"lat": 18.5354, "lng": 73.8617},
    "Birch Lane": {"lat": 18.5154, "lng": 73.8417},
    "Hospital Access Road": {"lat": 18.5404, "lng": 73.8367},
    "Cedar Street": {"lat": 18.5054, "lng": 73.8667},
    "Industrial Avenue": {"lat": 18.5454, "lng": 73.8167},
    "Riverside Drive": {"lat": 18.4954, "lng": 73.8867},
    "Wellington Road": {"lat": 18.5604, "lng": 73.8067},
    "Maple Court": {"lat": 18.5174, "lng": 73.8537},
    "Market Street": {"lat": 18.5224, "lng": 73.8487},
    "Anderson Boulevard": {"lat": 18.5324, "lng": 73.8387},
    "Broadway & 3rd": {"lat": 18.5124, "lng": 73.8587},
    "Block 7 Entrance": {"lat": 18.5274, "lng": 73.8437},
    "Victoria Lane": {"lat": 18.5374, "lng": 73.8337},
    "King's Road": {"lat": 18.5074, "lng": 73.8737},
    "Highway Toll Plaza": {"lat": 18.5554, "lng": 73.8137},
    "Highway 101, School Zone": {"lat": 18.5424, "lng": 73.8297},
}

import random

@app.get("/api/heatmap")
def get_heatmap_data():
    """Get location-aggregated complaint data for heatmap visualization."""
    location_data = {}
    
    for complaint in orchestrator.complaints.values():
        loc = complaint.location or (complaint.parsed.extracted_location if complaint.parsed else "Unknown")
        if not loc or loc == "Location not specified":
            loc = "Unknown"
        
        if loc not in location_data:
            location_data[loc] = {
                "location": loc,
                "complaints": [],
                "count": 0,
                "total_severity": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "resolved_count": 0,
                "active_count": 0,
                "breached_count": 0,
            }
        
        entry = location_data[loc]
        entry["count"] += 1
        entry["complaints"].append(complaint.id)
        
        if complaint.severity:
            entry["total_severity"] += complaint.severity.severity_score
            level = complaint.severity.severity_level.value
            if level == "critical":
                entry["critical_count"] += 1
            elif level == "high":
                entry["high_count"] += 1
            elif level == "medium":
                entry["medium_count"] += 1
            else:
                entry["low_count"] += 1
        
        if complaint.status.value == "resolved":
            entry["resolved_count"] += 1
        else:
            entry["active_count"] += 1
        
        if complaint.sla and complaint.sla.breached:
            entry["breached_count"] += 1
    
    # Build heatmap points with coordinates
    heatmap_points = []
    for loc, data in location_data.items():
        avg_severity = data["total_severity"] / data["count"] if data["count"] > 0 else 0
        
        # Priority score: weighted combination of count, severity, active, breaches
        priority_score = round(
            0.3 * min(data["count"] / 5, 1) * 10 +
            0.35 * avg_severity +
            0.2 * min(data["active_count"] / 3, 1) * 10 +
            0.15 * min(data["breached_count"], 3) * 3.3,
            1
        )
        
        # Get coordinates (use known or generate near default center)
        coords = LOCATION_COORDS.get(loc)
        if not coords:
            # Generate deterministic coords near Pune city center
            hash_val = hash(loc)
            coords = {
                "lat": 18.52 + (hash_val % 100) * 0.001 - 0.05,
                "lng": 73.85 + (hash_val % 73) * 0.001 - 0.035
            }
        
        heatmap_points.append({
            "location": loc,
            "lat": coords["lat"],
            "lng": coords["lng"],
            "count": data["count"],
            "avg_severity": round(avg_severity, 1),
            "priority_score": priority_score,
            "critical": data["critical_count"],
            "high": data["high_count"],
            "medium": data["medium_count"],
            "low": data["low_count"],
            "active": data["active_count"],
            "resolved": data["resolved_count"],
            "breached": data["breached_count"],
            "complaint_ids": data["complaints"],
        })
    
    # Sort by priority score descending
    heatmap_points.sort(key=lambda x: x["priority_score"], reverse=True)
    
    return {
        "total_locations": len(heatmap_points),
        "points": heatmap_points,
        "center": {"lat": 18.5204, "lng": 73.8567},  # Pune center
        "zoom": 13
    }


# ─── Agent Scorecards ────────────────────────────────────────────────────────

@app.get("/api/agents/scorecards")
def get_agent_scorecards():
    """Get per-agent performance scorecards with detailed metrics."""
    all_complaints = list(orchestrator.complaints.values())
    audit_entries = orchestrator.audit_logger.get_recent(10000)
    
    # Aggregate per-agent metrics from decisions
    agent_metrics = {
        "agent-1": {"name": "Intake & Parser", "icon": "📥", "decisions": [], "errors": 0, "corrections": 0},
        "agent-2": {"name": "Vision & Multimodal AI", "icon": "👁️", "decisions": [], "errors": 0, "corrections": 0},
        "agent-3": {"name": "Severity Classifier", "icon": "⚖️", "decisions": [], "errors": 0, "corrections": 0},
        "agent-4": {"name": "Router & Decision Maker", "icon": "🔀", "decisions": [], "errors": 0, "corrections": 0},
        "agent-5": {"name": "Workflow Monitor", "icon": "📡", "decisions": [], "errors": 0, "corrections": 0},
    }
    
    # Collect decisions from complaints
    for complaint in all_complaints:
        for decision in complaint.agent_decisions:
            agent_id = decision.agent_id
            if agent_id in agent_metrics:
                agent_metrics[agent_id]["decisions"].append(decision)
    
    # Count errors and corrections from audit log
    for entry in audit_entries:
        if entry.action == "agent_error_recovery" and entry.agent_id == "orchestrator":
            # Extract which agent errored from reasoning
            for aid in agent_metrics:
                if aid in entry.reasoning:
                    agent_metrics[aid]["errors"] += 1
        if entry.action == "self_correction_triggered":
            agent_metrics["agent-3"]["corrections"] += 1
        if entry.action == "cross_validation_failed":
            agent_metrics["agent-3"]["corrections"] += 1
        if entry.action == "duplicate_detected":
            agent_metrics["agent-1"]["corrections"] += 1
    
    # Build scorecards
    scorecards = []
    for agent_id, metrics in agent_metrics.items():
        decisions = metrics["decisions"]
        total = len(decisions)
        
        avg_duration = 0
        avg_confidence = 0
        high_conf = 0
        low_conf = 0
        
        if total > 0:
            avg_duration = sum(d.duration_ms for d in decisions) / total
            avg_confidence = sum(d.confidence for d in decisions) / total
            high_conf = sum(1 for d in decisions if d.confidence >= 0.7)
            low_conf = sum(1 for d in decisions if d.confidence < 0.5)
        
        error_rate = metrics["errors"] / max(total, 1) * 100
        
        # Calculate reliability score (0-100)
        reliability = min(100, max(0, round(
            100 - error_rate * 5 + (avg_confidence * 20) + (metrics["corrections"] * 2)
        )))
        
        scorecards.append({
            "agent_id": agent_id,
            "name": metrics["name"],
            "icon": metrics["icon"],
            "total_processed": total,
            "avg_duration_ms": round(avg_duration, 1),
            "avg_confidence": round(avg_confidence, 3),
            "high_confidence_count": high_conf,
            "low_confidence_count": low_conf,
            "error_count": metrics["errors"],
            "error_rate": round(error_rate, 1),
            "self_corrections": metrics["corrections"],
            "reliability_score": reliability,
            "status": "online",
        })
    
    # Overall system metrics
    total_decisions = sum(s["total_processed"] for s in scorecards)
    overall_confidence = sum(s["avg_confidence"] * s["total_processed"] for s in scorecards) / max(total_decisions, 1)
    
    return {
        "scorecards": scorecards,
        "system_metrics": {
            "total_decisions": total_decisions,
            "overall_avg_confidence": round(overall_confidence, 3),
            "total_errors": orchestrator.total_errors,
            "total_self_corrections": orchestrator.total_auto_corrected,
            "total_complaints": len(all_complaints),
            "autonomous_rate": round((len([c for c in all_complaints if c.retry_count == 0]) / max(len(all_complaints), 1)) * 100, 1),
        }
    }


# ─── Health Check ─────────────────────────────────────────────────────────────

@app.get("/api/health")
def health_check():
    """System health check."""
    return {
        "status": "healthy",
        "agents": 5,
        "total_processed": orchestrator.total_processed,
        "version": "1.0.0"
    }


# ─── Helper Functions ─────────────────────────────────────────────────────────

def _serialize_complaint(complaint) -> dict:
    """Serialize a complaint to a JSON-friendly dict."""
    data = complaint.model_dump(mode="json")
    
    # Add computed fields
    if complaint.severity:
        data["severity_display"] = f"{complaint.severity.severity_score}/10 ({complaint.severity.severity_level.value})"
    if complaint.department_ticket:
        data["department_display"] = complaint.department_ticket.department.value
    if complaint.sla:
        data["sla_display"] = f"{complaint.sla.time_remaining_hours}h remaining" if not complaint.sla.breached else "BREACHED"
    
    data["agent_count"] = len(complaint.agent_decisions)
    data["pipeline_duration_display"] = f"{complaint.total_pipeline_ms}ms"
    
    return data


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
