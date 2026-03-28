"""
Core data models for the Multi-Agent Pothole Complaint System.
All models use Pydantic for validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime, timedelta
from enum import Enum
import uuid


# ─── Enums ─────────────────────────────────────────────────────────────────────

class ComplaintStatus(str, Enum):
    RECEIVED = "received"
    PARSING = "parsing"
    ANALYZING = "analyzing"
    CLASSIFYING = "classifying"
    ROUTING = "routing"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    STALLED = "stalled"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DepartmentType(str, Enum):
    ROADS_INFRASTRUCTURE = "Roads & Infrastructure"
    EMERGENCY_SERVICES = "Emergency Services"
    TRAFFIC_MANAGEMENT = "Traffic Management"
    URBAN_PLANNING = "Urban Planning"
    UTILITIES = "Utilities"


class InputModality(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"


class DamageType(str, Enum):
    POTHOLE = "pothole"
    CRACK = "crack"
    SINKHOLE = "sinkhole"
    SURFACE_WEAR = "surface_wear"
    FLOODING = "flooding"
    MANHOLE = "manhole"


class EscalationLevel(str, Enum):
    NONE = "none"
    SUPERVISOR = "supervisor"
    DEPARTMENT_HEAD = "department_head"
    CITY_ADMIN = "city_admin"


# ─── Agent Decision Model ──────────────────────────────────────────────────────

class AgentDecision(BaseModel):
    """Records a single agent's analysis and decision."""
    agent_id: str
    agent_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    input_summary: str
    output_summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    duration_ms: int
    reasoning: str
    error: Optional[str] = None
    retry_count: int = 0
    self_corrected: bool = False


# ─── Audit Log ──────────────────────────────────────────────────────────────────

class AuditLogEntry(BaseModel):
    """Append-only audit trail entry."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    complaint_id: str
    agent_id: str
    agent_name: str
    action: str
    reasoning: str
    outcome: str
    metadata: dict = Field(default_factory=dict)


# ─── Vision Analysis ───────────────────────────────────────────────────────────

class VisionAnalysis(BaseModel):
    """Output from Agent 2 — Vision & Multimodal AI."""
    damage_type: DamageType
    area_estimate: Literal["small", "medium", "large"]
    road_type: Literal["highway", "residential", "arterial", "commercial"]
    hazard_flags: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    needs_human_review: bool = False
    raw_analysis: str = ""


# ─── Parsed Complaint ──────────────────────────────────────────────────────────

class ParsedComplaint(BaseModel):
    """Output from Agent 1 — Intake & Parser."""
    original_text: str = ""
    transcribed_audio: str = ""
    extracted_location: str = ""
    complaint_type: str = ""
    urgency_keywords: List[str] = Field(default_factory=list)
    has_image: bool = False
    has_audio: bool = False
    modalities_used: List[InputModality] = Field(default_factory=list)


# ─── Severity Assessment ───────────────────────────────────────────────────────

class SeverityAssessment(BaseModel):
    """Output from Agent 3 — Severity Classifier."""
    severity_score: float = Field(ge=0.0, le=10.0)
    severity_level: SeverityLevel
    text_urgency_score: float = 0.0
    vision_damage_score: float = 0.0
    location_risk_score: float = 0.0
    recurrence_factor: float = 0.0
    cross_validation_passed: bool = True
    flag_for_reanalysis: bool = False


# ─── SLA Record ────────────────────────────────────────────────────────────────

class SLARecord(BaseModel):
    """SLA tracking for a complaint."""
    deadline: datetime
    sla_hours: int
    breached: bool = False
    breach_time: Optional[datetime] = None
    time_remaining_hours: Optional[float] = None
    escalation_level: EscalationLevel = EscalationLevel.NONE
    escalation_count: int = 0
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    stalled: bool = False


# ─── Department Ticket ──────────────────────────────────────────────────────────

class DepartmentTicket(BaseModel):
    """Routed ticket assigned to a department."""
    department: DepartmentType
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    resolution_status: Literal["pending", "in_progress", "completed", "rerouted"] = "pending"
    resolution_proof_url: Optional[str] = None
    reroute_count: int = 0
    rerouted_from: Optional[str] = None


# ─── Citizen Notification ───────────────────────────────────────────────────────

class CitizenNotification(BaseModel):
    """Notification sent to citizen."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    complaint_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    notification_type: Literal[
        "received", "assigned", "in_progress",
        "escalated", "resolved", "update"
    ]
    message: str
    channel: Literal["sms", "email", "app_push"] = "app_push"
    delivered: bool = True


# ─── Main Complaint Model ──────────────────────────────────────────────────────

class Complaint(BaseModel):
    """The central complaint entity — tracks the full lifecycle."""
    id: str = Field(default_factory=lambda: f"PTH-{str(uuid.uuid4())[:6].upper()}")
    citizen_name: str = "Anonymous"
    citizen_contact: str = ""
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    status: ComplaintStatus = ComplaintStatus.RECEIVED
    
    # Raw inputs
    text_input: str = ""
    image_data: Optional[str] = None  # base64 or URL
    audio_data: Optional[str] = None  # file path or base64
    location: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Agent outputs (populated as pipeline progresses)
    parsed: Optional[ParsedComplaint] = None
    vision: Optional[VisionAnalysis] = None
    severity: Optional[SeverityAssessment] = None
    department_ticket: Optional[DepartmentTicket] = None
    sla: Optional[SLARecord] = None
    
    # Pipeline tracking
    agent_decisions: List[AgentDecision] = Field(default_factory=list)
    current_agent: Optional[str] = None
    pipeline_started_at: Optional[datetime] = None
    pipeline_completed_at: Optional[datetime] = None
    total_pipeline_ms: int = 0
    
    # Error recovery
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None
    auto_corrected: bool = False
    
    # Resolution
    resolved_at: Optional[datetime] = None
    resolution_notes: str = ""


# ─── API Request/Response Models ────────────────────────────────────────────────

class ComplaintSubmission(BaseModel):
    """API request model for submitting a new complaint."""
    citizen_name: str = "Anonymous"
    citizen_contact: str = ""
    text_input: str = ""
    image_data: Optional[str] = None
    audio_data: Optional[str] = None
    location: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PipelineHealthResponse(BaseModel):
    """Health metrics for the agent pipeline."""
    total_complaints: int
    active_complaints: int
    resolved_complaints: int
    sla_compliance_rate: float
    avg_resolution_hours: float
    agent_uptime: dict
    stalled_count: int
    escalated_count: int
    autonomous_success_rate: float


class DepartmentStats(BaseModel):
    """Statistics for a single department."""
    department: str
    active_tickets: int
    resolved_tickets: int
    avg_response_hours: float
    sla_breach_count: int
    completion_rate: float
