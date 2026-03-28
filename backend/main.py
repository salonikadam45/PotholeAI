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
