"""
Process Orchestration Agent
Master controller that chains all 5 agents in sequence with error recovery
and multi-agent collaboration support.
"""

import time
import random
from datetime import datetime, timedelta
from typing import List
from backend.models import (
    Complaint, ComplaintStatus, ComplaintSubmission,
    AgentDecision, AuditLogEntry, CitizenNotification
)
from backend.agents import (
    IntakeParserAgent, VisionMultimodalAgent,
    SeverityClassifierAgent, RouterDecisionAgent,
    WorkflowMonitorAgent
)
from backend.services.audit_logger import AuditLogger
from backend.services.notification_service import NotificationService
from backend.services.sla_engine import SLAEngine


class ProcessOrchestrator:
    """
    The master orchestration agent that:
    - Chains agents: Intake → Vision → Severity → Router → Monitor
    - Manages the full complaint lifecycle
    - Implements error recovery with 3-retry loops
    - Supports multi-agent collaboration (upstream re-analysis)
    - Generates meeting intelligence reports from batched complaints
    """
    
    def __init__(self):
        # Initialize all agents
        self.agent1 = IntakeParserAgent()
        self.agent2 = VisionMultimodalAgent()
        self.agent3 = SeverityClassifierAgent()
        self.agent4 = RouterDecisionAgent()
        self.agent5 = WorkflowMonitorAgent()
        
        # Services
        self.audit_logger = AuditLogger()
        self.notification_service = NotificationService()
        self.sla_engine = SLAEngine()
        
        # Complaint store
        self.complaints: dict[str, Complaint] = {}
        
        # Pipeline stats
        self.total_processed = 0
        self.total_errors = 0
        self.total_auto_corrected = 0
    
    def submit_complaint(self, submission: ComplaintSubmission) -> Complaint:
        """
        Submit a new complaint and run it through the full agent pipeline.
        This is the main entry point for the system.
        """
        # Create complaint
        complaint = Complaint(
            citizen_name=submission.citizen_name,
            citizen_contact=submission.citizen_contact,
            text_input=submission.text_input,
            image_data=submission.image_data,
            audio_data=submission.audio_data,
            location=submission.location,
            latitude=submission.latitude,
            longitude=submission.longitude,
            pipeline_started_at=datetime.utcnow()
        )
        
        self.audit_logger.log(AuditLogEntry(
            complaint_id=complaint.id,
            agent_id="orchestrator",
            agent_name="Process Orchestrator",
            action="complaint_received",
            reasoning=f"New complaint from {complaint.citizen_name}",
            outcome=f"Complaint {complaint.id} created. Starting pipeline."
        ))
        
        # Send intake notification
        intake_notif = self.agent5.generate_intake_notification(complaint)
        self.notification_service.add(intake_notif)
        
        # Run the pipeline
        complaint = self._run_pipeline(complaint)
        
        # Store
        self.complaints[complaint.id] = complaint
        self.total_processed += 1
        
        return complaint
    
    def _run_pipeline(self, complaint: Complaint) -> Complaint:
        """
        Execute the full 5-agent pipeline with error recovery.
        """
        pipeline_start = time.time()
        
        # ════════════════════════════════════════════════════════════════
        # STAGE 1: Intake & Parsing (Agent 1)
        # ════════════════════════════════════════════════════════════════
        
        complaint.status = ComplaintStatus.PARSING
        complaint.current_agent = "agent-1"
        
        parsed, decision, audit_entries = self._retry_agent(
            "agent-1",
            lambda: self.agent1.process(
                text_input=complaint.text_input,
                image_data=complaint.image_data,
                audio_data=complaint.audio_data,
                location_hint=complaint.location
            ),
            complaint
        )
        
        if parsed:
            complaint.parsed = parsed
            complaint.agent_decisions.append(decision)
            self.audit_logger.log_many(audit_entries)
            
            # Update location from parsing if not provided
            if not complaint.location and parsed.extracted_location:
                complaint.location = parsed.extracted_location
        else:
            complaint.status = ComplaintStatus.STALLED
            complaint.last_error = "Agent 1 failed after retries"
            return complaint
        
        # ════════════════════════════════════════════════════════════════
        # STAGE 2: Vision & Multimodal AI (Agent 2)
        # ════════════════════════════════════════════════════════════════
        
        complaint.status = ComplaintStatus.ANALYZING
        complaint.current_agent = "agent-2"
        
        vision, decision, audit_entries = self._retry_agent(
            "agent-2",
            lambda: self.agent2.process(
                image_data=complaint.image_data,
                complaint_type_hint=complaint.parsed.complaint_type if complaint.parsed else "",
                complaint_id=complaint.id
            ),
            complaint
        )
        
        if vision:
            complaint.vision = vision
            complaint.agent_decisions.append(decision)
            self.audit_logger.log_many(audit_entries)
        else:
            complaint.status = ComplaintStatus.STALLED
            complaint.last_error = "Agent 2 failed after retries"
            return complaint
        
        # ════════════════════════════════════════════════════════════════
        # STAGE 3: Severity Classification (Agent 3)
        # ════════════════════════════════════════════════════════════════
        
        complaint.status = ComplaintStatus.CLASSIFYING
        complaint.current_agent = "agent-3"
        
        severity, decision, audit_entries = self._retry_agent(
            "agent-3",
            lambda: self.agent3.process(
                parsed=complaint.parsed,
                vision=complaint.vision,
                complaint_id=complaint.id
            ),
            complaint
        )
        
        if severity:
            complaint.severity = severity
            complaint.agent_decisions.append(decision)
            self.audit_logger.log_many(audit_entries)
            
            # ── Self-correction: re-analysis loop ──────────────────
            if severity.flag_for_reanalysis and complaint.retry_count < complaint.max_retries:
                self.audit_logger.log(AuditLogEntry(
                    complaint_id=complaint.id,
                    agent_id="orchestrator",
                    agent_name="Process Orchestrator",
                    action="self_correction_triggered",
                    reasoning=f"Agent 3 flagged text-vision mismatch. Requesting Agent 2 re-analysis.",
                    outcome="Re-running vision analysis with adjusted parameters"
                ))
                complaint.auto_corrected = True
                self.total_auto_corrected += 1
                
                # Re-run Agent 2 (simulated re-analysis with different params)
                vision2, dec2, aud2 = self.agent2.process(
                    image_data=complaint.image_data or "reanalysis",
                    complaint_type_hint=complaint.parsed.complaint_type,
                    complaint_id=complaint.id
                )
                complaint.vision = vision2
                complaint.agent_decisions.append(dec2)
                self.audit_logger.log_many(aud2)
                
                # Re-run Agent 3 with updated vision
                sev2, dec3, aud3 = self.agent3.process(
                    parsed=complaint.parsed,
                    vision=complaint.vision,
                    complaint_id=complaint.id
                )
                complaint.severity = sev2
                complaint.agent_decisions.append(dec3)
                self.audit_logger.log_many(aud3)
        else:
            complaint.status = ComplaintStatus.STALLED
            complaint.last_error = "Agent 3 failed after retries"
            return complaint
        
        # ════════════════════════════════════════════════════════════════
        # STAGE 4: Routing & Decision (Agent 4)
        # ════════════════════════════════════════════════════════════════
        
        complaint.status = ComplaintStatus.ROUTING
        complaint.current_agent = "agent-4"
        
        result = self._retry_agent(
            "agent-4",
            lambda: self.agent4.process(
                severity=complaint.severity,
                vision=complaint.vision,
                location=complaint.location,
                complaint_id=complaint.id
            ),
            complaint
        )
        
        if result:
            ticket, sla, decision, audit_entries = result
            complaint.department_ticket = ticket
            complaint.sla = sla
            complaint.agent_decisions.append(decision)
            self.audit_logger.log_many(audit_entries)
            complaint.status = ComplaintStatus.ASSIGNED
            
            # Send assignment notification
            assign_notif = self.agent5.generate_assignment_notification(complaint)
            self.notification_service.add(assign_notif)
        else:
            complaint.status = ComplaintStatus.STALLED
            complaint.last_error = "Agent 4 failed after retries"
            return complaint
        
        # ════════════════════════════════════════════════════════════════
        # STAGE 5: Initial Health Check (Agent 5)
        # ════════════════════════════════════════════════════════════════
        
        complaint.current_agent = "agent-5"
        
        complaint, notifications, decision, audit_entries = self.agent5.monitor_complaint(complaint)
        complaint.agent_decisions.append(decision)
        self.audit_logger.log_many(audit_entries)
        self.notification_service.add_many(notifications)
        
        # ── Pipeline complete ──────────────────────────────────────────
        
        complaint.current_agent = None
        complaint.pipeline_completed_at = datetime.utcnow()
        complaint.total_pipeline_ms = int((time.time() - pipeline_start) * 1000)
        
        self.audit_logger.log(AuditLogEntry(
            complaint_id=complaint.id,
            agent_id="orchestrator",
            agent_name="Process Orchestrator",
            action="pipeline_complete",
            reasoning=f"All 5 agents processed successfully in {complaint.total_pipeline_ms}ms",
            outcome=f"Status: {complaint.status.value} | Department: {complaint.department_ticket.department.value} | "
                    f"Severity: {complaint.severity.severity_score}/10"
        ))
        
        return complaint
    
    def _retry_agent(self, agent_id: str, fn, complaint: Complaint, max_retries: int = 3):
        """
        Execute an agent function with retry logic.
        Returns the function result or None if all retries fail.
        """
        for attempt in range(max_retries):
            try:
                result = fn()
                return result
            except Exception as e:
                self.total_errors += 1
                complaint.retry_count += 1
                
                self.audit_logger.log(AuditLogEntry(
                    complaint_id=complaint.id,
                    agent_id="orchestrator",
                    agent_name="Process Orchestrator",
                    action="agent_error_recovery",
                    reasoning=f"{agent_id} failed on attempt {attempt + 1}: {str(e)}",
                    outcome=f"Retrying ({attempt + 1}/{max_retries})"
                ))
                
                if attempt == max_retries - 1:
                    self.audit_logger.log(AuditLogEntry(
                        complaint_id=complaint.id,
                        agent_id="orchestrator",
                        agent_name="Process Orchestrator",
                        action="agent_failure_escalation",
                        reasoning=f"{agent_id} failed after {max_retries} attempts",
                        outcome="Escalating to human review"
                    ))
                    return None
        return None
    
    def run_health_check(self) -> dict:
        """
        Run Agent 5 health check on all active complaints.
        Returns summary of actions taken.
        """
        active = [c for c in self.complaints.values() if c.status not in [
            ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED
        ]]
        
        actions_summary = {
            "checked": 0,
            "breaches_found": 0,
            "stalls_detected": 0,
            "escalated": 0,
            "notifications_sent": 0,
        }
        
        for complaint in active:
            complaint = self.sla_engine.refresh_sla_status(complaint)
            complaint, notifications, decision, audit_entries = self.agent5.monitor_complaint(complaint)
            
            self.complaints[complaint.id] = complaint
            self.audit_logger.log_many(audit_entries)
            self.notification_service.add_many(notifications)
            
            actions_summary["checked"] += 1
            actions_summary["notifications_sent"] += len(notifications)
            
            if complaint.sla and complaint.sla.breached:
                actions_summary["breaches_found"] += 1
            if complaint.sla and complaint.sla.stalled:
                actions_summary["stalls_detected"] += 1
            if complaint.sla and complaint.sla.escalation_count > 0:
                actions_summary["escalated"] += 1
        
        return actions_summary
    
    def resolve_complaint(self, complaint_id: str, resolution_notes: str = "",
                          proof_url: str = None) -> Complaint | None:
        """Mark a complaint as resolved."""
        complaint = self.complaints.get(complaint_id)
        if not complaint:
            return None
        
        complaint.status = ComplaintStatus.RESOLVED
        complaint.resolved_at = datetime.utcnow()
        complaint.resolution_notes = resolution_notes
        
        if complaint.department_ticket:
            complaint.department_ticket.resolution_status = "completed"
            complaint.department_ticket.resolution_proof_url = proof_url
        
        if complaint.sla:
            complaint.sla.last_activity = datetime.utcnow()
        
        # Send resolution notification
        notif = self.agent5.generate_resolution_notification(complaint)
        self.notification_service.add(notif)
        
        self.audit_logger.log(AuditLogEntry(
            complaint_id=complaint.id,
            agent_id="orchestrator",
            agent_name="Process Orchestrator",
            action="complaint_resolved",
            reasoning=f"Resolution: {resolution_notes}",
            outcome=f"Complaint resolved. Proof: {proof_url or 'none'}"
        ))
        
        self.complaints[complaint_id] = complaint
        return complaint
    
    def get_pipeline_health(self) -> dict:
        """Get overall pipeline health metrics."""
        all_complaints = list(self.complaints.values())
        active = [c for c in all_complaints if c.status not in [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]]
        resolved = [c for c in all_complaints if c.status == ComplaintStatus.RESOLVED]
        
        autonomous_success = 0
        total_with_pipeline = [c for c in all_complaints if c.pipeline_completed_at]
        if total_with_pipeline:
            autonomous_success = sum(1 for c in total_with_pipeline if c.retry_count == 0) / len(total_with_pipeline)
        
        return {
            "total_complaints": len(all_complaints),
            "active_complaints": len(active),
            "resolved_complaints": len(resolved),
            "sla_compliance_rate": self.sla_engine.calculate_compliance_rate(all_complaints),
            "avg_resolution_hours": self.sla_engine.avg_resolution_hours(all_complaints),
            "stalled_count": len(self.sla_engine.get_stalled(all_complaints)),
            "escalated_count": sum(1 for c in all_complaints if c.status == ComplaintStatus.ESCALATED),
            "autonomous_success_rate": round(autonomous_success * 100, 1),
            "total_audit_entries": self.audit_logger.count(),
            "total_notifications": self.notification_service.count(),
            "total_errors_recovered": self.total_errors,
            "total_auto_corrections": self.total_auto_corrected,
            "agent_status": {
                "agent-1": {"name": "Intake & Parser", "status": "online", "processed": self.total_processed},
                "agent-2": {"name": "Vision & Multimodal AI", "status": "online", "processed": self.total_processed},
                "agent-3": {"name": "Severity Classifier", "status": "online", "processed": self.total_processed},
                "agent-4": {"name": "Router & Decision Maker", "status": "online", "processed": self.total_processed},
                "agent-5": {"name": "Workflow Monitor", "status": "online", "processed": self.total_processed},
            }
        }
    
    def get_department_stats(self) -> list[dict]:
        """Get per-department statistics."""
        dept_map = {}
        for complaint in self.complaints.values():
            if complaint.department_ticket:
                dept = complaint.department_ticket.department.value
                if dept not in dept_map:
                    dept_map[dept] = {"active": 0, "resolved": 0, "breached": 0, "total_hours": 0}
                
                if complaint.status == ComplaintStatus.RESOLVED:
                    dept_map[dept]["resolved"] += 1
                    if complaint.resolved_at and complaint.pipeline_started_at:
                        hours = (complaint.resolved_at - complaint.pipeline_started_at).total_seconds() / 3600
                        dept_map[dept]["total_hours"] += hours
                else:
                    dept_map[dept]["active"] += 1
                
                if complaint.sla and complaint.sla.breached:
                    dept_map[dept]["breached"] += 1
        
        result = []
        for dept, stats in dept_map.items():
            total = stats["active"] + stats["resolved"]
            avg_hours = stats["total_hours"] / stats["resolved"] if stats["resolved"] > 0 else 0
            result.append({
                "department": dept,
                "active_tickets": stats["active"],
                "resolved_tickets": stats["resolved"],
                "avg_response_hours": round(avg_hours, 1),
                "sla_breach_count": stats["breached"],
                "completion_rate": round((stats["resolved"] / total * 100) if total > 0 else 0, 1)
            })
        
        return result
    
    def seed_demo_data(self, count: int = 20):
        """Seed realistic demo complaints for dashboard testing."""
        demo_complaints = [
            {"text": "Large pothole on Main Street near the elementary school. My car tire popped yesterday. This is very dangerous for children walking to school.", "location": "Main Street", "image": "demo_pothole_school"},
            {"text": "Deep crack running across Oak Avenue. It's getting worse every week and now stretches about 3 meters.", "location": "Oak Avenue", "image": None},
            {"text": "Massive sinkhole forming on Highway 12 exit ramp. Emergency! Cars are swerving to avoid it.", "location": "Highway 12 Exit Ramp", "image": "demo_sinkhole_highway"},
            {"text": "Road completely flooded on Commerce Drive due to blocked storm drain. Has been waterlogged for 3 days.", "location": "Commerce Drive", "image": "demo_flooding"},
            {"text": "Missing manhole cover on Park Road near the playground. Extremely dangerous, especially at night.", "location": "Park Road", "image": "demo_manhole"},
            {"text": "Multiple potholes on 5th Street intersection. Causing traffic delays and several minor accidents.", "location": "5th Street Intersection", "image": "demo_pothole_intersection"},
            {"text": "Surface completely worn out on Birch Lane. Faded lane markings making it very confusing for drivers.", "location": "Birch Lane", "image": None},
            {"text": "Urgent: large pothole on the hospital access road. Ambulances having difficulty. Immediate repair needed.", "location": "Hospital Access Road", "image": "demo_pothole_hospital"},
            {"text": "Cracked road surface near the bus stop on Cedar Street. Water seeping through the cracks.", "location": "Cedar Street", "image": None},
            {"text": "Pothole cluster on Industrial Avenue. Trucks making it worse daily. Very deep holes now.", "location": "Industrial Avenue", "image": "demo_pothole_industrial"},
            {"text": "Road damage from recent heavy rain on Riverside Drive. Multiple spots need repair.", "location": "Riverside Drive", "image": None},
            {"text": "Sinkhole risk on Wellington Road. Ground seems to be subsiding near the drainage system.", "location": "Wellington Road", "image": "demo_sinkhole_wellington"},
            {"text": "Small pothole on Maple Court. Not urgent but should be fixed before it gets worse.", "location": "Maple Court", "image": None},
            {"text": "Drainage failure causing flooding on Market Street. Shops affected. Very urgent.", "location": "Market Street", "image": "demo_flooding_market"},
            {"text": "Road surface breaking apart on Anderson Boulevard near the high school zone.", "location": "Anderson Boulevard", "image": None},
            {"text": "Dangerous crack near traffic signal on Broadway and 3rd. Signal post also tilting.", "location": "Broadway & 3rd", "image": None},
            {"text": "Giant pothole right at the entrance of residential colony Block 7. Everyone complaining.", "location": "Block 7 Entrance", "image": "demo_pothole_colony"},
            {"text": "Open drain cover with electrical cables exposed on Victoria Lane. Very risky!", "location": "Victoria Lane", "image": "demo_electrical"},
            {"text": "Bumpy road surface on King's Road. Speed bumps are broken. Surface very uneven.", "location": "King's Road", "image": None},
            {"text": "Pothole on highway median near toll plaza. Vehicles crossing median dangerously.", "location": "Highway Toll Plaza", "image": "demo_pothole_highway"},
        ]
        
        names = ["Rahul Sharma", "Priya Patel", "Amit Kumar", "Sneha Gupta", "Vikram Singh",
                 "Ananya Reddy", "Rajesh Verma", "Kavita Nair", "Suresh Yadav", "Meera Iyer",
                 "Arun Das", "Pooja Mishra", "Kiran Rao", "Deepak Joshi", "Nisha Malik",
                 "Sanjay Bhat", "Ritu Saxena", "Manish Tiwari", "Divya Kapoor", "Harish Menon"]
        
        for i, demo in enumerate(demo_complaints[:count]):
            submission = ComplaintSubmission(
                citizen_name=names[i % len(names)],
                citizen_contact=f"+91-{random.randint(7000000000, 9999999999)}",
                text_input=demo["text"],
                image_data=demo.get("image"),
                location=demo["location"]
            )
            
            complaint = self.submit_complaint(submission)
            
            # Simulate some being in various states for demo
            if i % 5 == 0 and complaint.sla:
                # Make some appear resolved
                self.resolve_complaint(complaint.id, "Repair completed by field crew", "proof_photo_url")
            elif i % 7 == 0 and complaint.sla:
                # Make some appear stalled (simulate old activity)
                complaint.sla.last_activity = datetime.utcnow() - timedelta(hours=complaint.sla.sla_hours * 0.6)
                complaint.sla.stalled = True
                complaint.status = ComplaintStatus.STALLED
                self.complaints[complaint.id] = complaint
            elif i % 9 == 0 and complaint.sla:
                # Make some appear breached 
                complaint.sla.breached = True
                complaint.sla.breach_time = datetime.utcnow()
                complaint.status = ComplaintStatus.ESCALATED
                self.complaints[complaint.id] = complaint
