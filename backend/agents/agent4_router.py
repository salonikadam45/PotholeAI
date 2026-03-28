"""
Agent 4: Routing & Decision Making
Routes complaints to correct department based on severity, damage type, and location context.
"""

import time
from datetime import datetime, timedelta
from backend.models import (
    DepartmentTicket, DepartmentType, SLARecord, EscalationLevel,
    AgentDecision, AuditLogEntry, SeverityAssessment, SeverityLevel,
    VisionAnalysis, DamageType
)


# SLA hours by severity level
SLA_HOURS = {
    SeverityLevel.CRITICAL: 24,
    SeverityLevel.HIGH: 48,
    SeverityLevel.MEDIUM: 168,   # 7 days
    SeverityLevel.LOW: 336,      # 14 days
}

# Department routing rules
ROUTING_RULES = {
    # (damage_type, severity_level) -> department
    (DamageType.SINKHOLE, SeverityLevel.CRITICAL): DepartmentType.EMERGENCY_SERVICES,
    (DamageType.SINKHOLE, SeverityLevel.HIGH): DepartmentType.EMERGENCY_SERVICES,
    (DamageType.MANHOLE, SeverityLevel.CRITICAL): DepartmentType.EMERGENCY_SERVICES,
    (DamageType.FLOODING, SeverityLevel.CRITICAL): DepartmentType.EMERGENCY_SERVICES,
}

# Hazard-based routing overrides
HAZARD_ROUTING = {
    "near_intersection": DepartmentType.TRAFFIC_MANAGEMENT,
    "high_speed_zone": DepartmentType.TRAFFIC_MANAGEMENT,
    "structural_risk": DepartmentType.EMERGENCY_SERVICES,
    "emergency_lane_blocked": DepartmentType.EMERGENCY_SERVICES,
    "electrical_hazard": DepartmentType.UTILITIES,
}


class RouterDecisionAgent:
    """
    Agent 4: Routing & Decision Making
    
    Routes complaints to the correct department:
    - Roads & Infrastructure: standard potholes, cracks, surface wear
    - Emergency Services: critical hazards, sinkholes, dangerous manholes
    - Traffic Management: near intersections, traffic signals
    - Urban Planning: recurring issues, systemic patterns
    - Utilities: manhole, drainage, electrical issues
    
    Also sets SLA deadlines and provides full decision auditability.
    """
    
    AGENT_ID = "agent-4"
    AGENT_NAME = "Router & Decision Maker"
    
    def process(self, severity: SeverityAssessment, vision: VisionAnalysis,
                location: str = "", recurrence_count: int = 0,
                complaint_id: str = "") -> tuple[DepartmentTicket, SLARecord, AgentDecision, list[AuditLogEntry]]:
        """
        Route complaint to appropriate department and set SLA.
        """
        start_time = time.time()
        audit_entries = []
        routing_reasons = []
        
        # ── Step 1: Check explicit routing rules ─────────────────────
        
        department = None
        rule_key = (vision.damage_type, severity.severity_level)
        
        if rule_key in ROUTING_RULES:
            department = ROUTING_RULES[rule_key]
            routing_reasons.append(f"Matched explicit rule: {vision.damage_type.value} + {severity.severity_level.value} → {department.value}")
        
        # ── Step 2: Check hazard-based routing ───────────────────────
        
        if not department:
            for hazard in vision.hazard_flags:
                if hazard in HAZARD_ROUTING:
                    department = HAZARD_ROUTING[hazard]
                    routing_reasons.append(f"Hazard override: '{hazard}' → {department.value}")
                    break
        
        # ── Step 3: Check recurrence (systemic issue) ────────────────
        
        if not department and recurrence_count >= 3:
            department = DepartmentType.URBAN_PLANNING
            routing_reasons.append(f"Recurrence count ({recurrence_count}) ≥ 3 → Urban Planning for systemic review")
        
        # ── Step 4: Check drainage/utility specific ──────────────────
        
        if not department and vision.damage_type in [DamageType.MANHOLE, DamageType.FLOODING]:
            department = DepartmentType.UTILITIES
            routing_reasons.append(f"Damage type '{vision.damage_type.value}' → Utilities department")
        
        # ── Step 5: Default to Roads & Infrastructure ────────────────
        
        if not department:
            department = DepartmentType.ROADS_INFRASTRUCTURE
            routing_reasons.append(f"Default routing for '{vision.damage_type.value}' → Roads & Infrastructure")
        
        audit_entries.append(self._audit("routing_decision",
            " | ".join(routing_reasons),
            f"Routed to: {department.value}",
            complaint_id))
        
        # ── Step 6: Set SLA deadline ─────────────────────────────────
        
        sla_hours = SLA_HOURS.get(severity.severity_level, 168)
        deadline = datetime.utcnow() + timedelta(hours=sla_hours)
        
        sla = SLARecord(
            deadline=deadline,
            sla_hours=sla_hours,
            breached=False,
            time_remaining_hours=float(sla_hours),
            last_activity=datetime.utcnow()
        )
        
        audit_entries.append(self._audit("sla_assignment",
            f"Severity {severity.severity_level.value} → SLA window: {sla_hours} hours",
            f"Deadline set: {deadline.isoformat()}Z",
            complaint_id))
        
        # ── Step 7: Create department ticket ─────────────────────────
        
        ticket = DepartmentTicket(
            department=department,
            assigned_at=datetime.utcnow(),
            resolution_status="pending"
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        decision = AgentDecision(
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            input_summary=f"Severity: {severity.severity_score}/10 ({severity.severity_level.value}) | "
                         f"Damage: {vision.damage_type.value} | Hazards: {vision.hazard_flags}",
            output_summary=f"Department: {department.value} | SLA: {sla_hours}h | Deadline: {deadline.strftime('%Y-%m-%d %H:%M')}",
            confidence=0.92,
            duration_ms=duration_ms,
            reasoning=" → ".join(routing_reasons) + f". SLA set to {sla_hours}h based on {severity.severity_level.value} priority."
        )
        
        audit_entries.append(self._audit("ticket_created",
            f"Department ticket created for {department.value}",
            f"Ticket assigned. SLA: {sla_hours}h. Status: pending.",
            complaint_id))
        
        return ticket, sla, decision, audit_entries
    
    def _audit(self, action: str, reasoning: str, outcome: str, complaint_id: str) -> AuditLogEntry:
        return AuditLogEntry(
            complaint_id=complaint_id,
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            action=action,
            reasoning=reasoning,
            outcome=outcome
        )
