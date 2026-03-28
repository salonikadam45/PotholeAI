"""
Agent 5: Workflow Monitor & SLA Tracker
Monitors active complaints for SLA breaches, stalls, and handles escalation + citizen notification.
"""

import time
from datetime import datetime, timedelta
from backend.models import (
    Complaint, ComplaintStatus, SLARecord, EscalationLevel,
    AgentDecision, AuditLogEntry, CitizenNotification
)


# Escalation ladder
ESCALATION_LADDER = [
    EscalationLevel.NONE,
    EscalationLevel.SUPERVISOR,
    EscalationLevel.DEPARTMENT_HEAD,
    EscalationLevel.CITY_ADMIN,
]

# Notification templates
NOTIFICATION_TEMPLATES = {
    "received": "Your complaint {id} has been received and is being processed by our AI system. "
                "We will keep you updated on progress.",
    "assigned": "Your complaint {id} has been assigned to {department}. "
                "Expected resolution within {sla_hours} hours. Reference: {id}.",
    "in_progress": "Update on complaint {id}: {department} has started working on your report. "
                   "Current status: In Progress.",
    "escalated": "IMPORTANT: Your complaint {id} has been escalated to {escalation_level} "
                 "due to delayed response. We are prioritizing your issue.",
    "resolved": "Great news! Your complaint {id} has been resolved by {department}. "
                "Please verify the repair at your convenience.",
    "stalled": "We noticed a delay in processing your complaint {id}. "
               "We have automatically re-prioritized it. Apologies for the inconvenience.",
}


class WorkflowMonitorAgent:
    """
    Agent 5: Workflow Monitor & SLA Tracker
    
    Responsibilities:
    - Run periodic health checks on all active complaints
    - Detect SLA breaches and approaching deadlines
    - Detect stalled complaints (no activity in >50% SLA window)
    - Auto-reroute if department hasn't acknowledged in 25% SLA
    - Escalation ladder: Stalled → Supervisor → Dept Head → City Admin
    - Generate citizen notifications at key milestones
    - Require resolution proof before marking complete
    """
    
    AGENT_ID = "agent-5"
    AGENT_NAME = "Workflow Monitor & SLA Tracker"
    
    def monitor_complaint(self, complaint: Complaint) -> tuple[Complaint, list[CitizenNotification], AgentDecision, list[AuditLogEntry]]:
        """
        Run health check on a single complaint.
        Returns updated complaint, any notifications triggered, decision, and audit entries.
        """
        start_time = time.time()
        audit_entries = []
        notifications = []
        actions_taken = []
        
        if not complaint.sla:
            duration_ms = int((time.time() - start_time) * 1000)
            decision = AgentDecision(
                agent_id=self.AGENT_ID,
                agent_name=self.AGENT_NAME,
                input_summary=f"Complaint {complaint.id} — no SLA record",
                output_summary="Skipped: No SLA data available",
                confidence=1.0,
                duration_ms=duration_ms,
                reasoning="Complaint has no SLA record, likely not yet routed."
            )
            return complaint, notifications, decision, audit_entries
        
        now = datetime.utcnow()
        
        # ── Check 1: SLA Breach ──────────────────────────────────────
        
        if not complaint.sla.breached and now > complaint.sla.deadline:
            complaint.sla.breached = True
            complaint.sla.breach_time = now
            complaint.status = ComplaintStatus.ESCALATED
            actions_taken.append("SLA_BREACHED")
            
            audit_entries.append(self._audit("sla_breach_detected",
                f"Deadline was {complaint.sla.deadline.isoformat()}. Current time: {now.isoformat()}",
                "SLA BREACHED — triggering escalation",
                complaint.id))
            
            # Escalate
            complaint, esc_notification = self._escalate(complaint)
            if esc_notification:
                notifications.append(esc_notification)
        
        # ── Check 2: Time remaining update ───────────────────────────
        
        remaining = (complaint.sla.deadline - now).total_seconds() / 3600
        complaint.sla.time_remaining_hours = round(max(0, remaining), 1)
        
        # ── Check 3: Approaching deadline (< 25% SLA remaining) ─────
        
        sla_25pct = complaint.sla.sla_hours * 0.25
        if remaining > 0 and remaining < sla_25pct and not complaint.sla.breached:
            if complaint.department_ticket and not complaint.department_ticket.acknowledged:
                # Department hasn't acknowledged — auto reroute
                actions_taken.append("AUTO_REROUTE_WARNING")
                audit_entries.append(self._audit("approaching_deadline_no_ack",
                    f"Only {remaining:.1f}h remaining. Department has not acknowledged.",
                    "Flagging for potential auto-reroute.",
                    complaint.id))
        
        # ── Check 4: Stall Detection ────────────────────────────────
        
        stall_threshold_hours = complaint.sla.sla_hours * 0.5
        time_since_activity = (now - complaint.sla.last_activity).total_seconds() / 3600
        
        if time_since_activity > stall_threshold_hours and complaint.status not in [
            ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED
        ]:
            complaint.sla.stalled = True
            complaint.status = ComplaintStatus.STALLED
            actions_taken.append("STALL_DETECTED")
            
            audit_entries.append(self._audit("stall_detected",
                f"No activity for {time_since_activity:.1f}h. Threshold: {stall_threshold_hours:.1f}h (50% SLA)",
                "Complaint STALLED — triggering notification and escalation",
                complaint.id))
            
            notifications.append(self._notify(complaint, "stalled"))
            complaint, esc_notification = self._escalate(complaint)
            if esc_notification:
                notifications.append(esc_notification)
        
        # ── Check 5: Resolution proof required ───────────────────────
        
        if complaint.status == ComplaintStatus.RESOLVED:
            if complaint.department_ticket and not complaint.department_ticket.resolution_proof_url:
                actions_taken.append("RESOLUTION_PROOF_MISSING")
                audit_entries.append(self._audit("proof_required",
                    "Complaint marked resolved but no proof uploaded",
                    "Requesting resolution proof from department",
                    complaint.id))
                complaint.status = ComplaintStatus.IN_PROGRESS
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        decision = AgentDecision(
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            input_summary=f"Complaint {complaint.id} | Status: {complaint.status.value} | "
                         f"SLA: {complaint.sla.time_remaining_hours}h remaining",
            output_summary=f"Actions: {actions_taken or ['HEALTHY']} | "
                          f"Notifications sent: {len(notifications)}",
            confidence=0.95,
            duration_ms=duration_ms,
            reasoning=f"Health check complete. " +
                      (f"Issues found: {', '.join(actions_taken)}" if actions_taken else "All checks passed. Complaint on track.")
        )
        
        if not actions_taken:
            audit_entries.append(self._audit("health_check_passed",
                f"SLA remaining: {complaint.sla.time_remaining_hours}h. No issues detected.",
                "Complaint is healthy and on track.",
                complaint.id))
        
        return complaint, notifications, decision, audit_entries
    
    def generate_intake_notification(self, complaint: Complaint) -> CitizenNotification:
        """Generate the initial 'received' notification."""
        return self._notify(complaint, "received")
    
    def generate_assignment_notification(self, complaint: Complaint) -> CitizenNotification:
        """Generate notification when complaint is assigned to a department."""
        return self._notify(complaint, "assigned")
    
    def generate_resolution_notification(self, complaint: Complaint) -> CitizenNotification:
        """Generate notification when complaint is resolved."""
        return self._notify(complaint, "resolved")
    
    def _escalate(self, complaint: Complaint) -> tuple[Complaint, CitizenNotification | None]:
        """Move complaint up the escalation ladder."""
        current_level = complaint.sla.escalation_level
        current_idx = ESCALATION_LADDER.index(current_level)
        
        if current_idx < len(ESCALATION_LADDER) - 1:
            new_level = ESCALATION_LADDER[current_idx + 1]
            complaint.sla.escalation_level = new_level
            complaint.sla.escalation_count += 1
            notification = self._notify(complaint, "escalated")
            return complaint, notification
        
        return complaint, None
    
    def _notify(self, complaint: Complaint, notification_type: str) -> CitizenNotification:
        """Create a citizen notification from template."""
        dept_name = complaint.department_ticket.department.value if complaint.department_ticket else "Processing"
        sla_hours = complaint.sla.sla_hours if complaint.sla else "N/A"
        esc_level = complaint.sla.escalation_level.value if complaint.sla else "none"
        
        template = NOTIFICATION_TEMPLATES.get(notification_type, "Update on your complaint {id}.")
        message = template.format(
            id=complaint.id,
            department=dept_name,
            sla_hours=sla_hours,
            escalation_level=esc_level
        )
        
        return CitizenNotification(
            complaint_id=complaint.id,
            notification_type=notification_type,
            message=message
        )
    
    def _audit(self, action: str, reasoning: str, outcome: str, complaint_id: str) -> AuditLogEntry:
        return AuditLogEntry(
            complaint_id=complaint_id,
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            action=action,
            reasoning=reasoning,
            outcome=outcome
        )
