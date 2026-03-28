"""
SLA Engine
Calculates deadlines, detects breaches, and manages SLA compliance metrics.
"""

from datetime import datetime
from typing import List
from backend.models import Complaint, ComplaintStatus, SLARecord


class SLAEngine:
    """
    SLA compliance engine — computes metrics across all complaints.
    """
    
    def calculate_compliance_rate(self, complaints: List[Complaint]) -> float:
        """Calculate overall SLA compliance rate."""
        with_sla = [c for c in complaints if c.sla is not None]
        if not with_sla:
            return 100.0
        
        compliant = sum(1 for c in with_sla if not c.sla.breached)
        return round((compliant / len(with_sla)) * 100, 1)
    
    def get_breached(self, complaints: List[Complaint]) -> List[Complaint]:
        """Get all complaints that have breached SLA."""
        return [c for c in complaints if c.sla and c.sla.breached]
    
    def get_approaching_deadline(self, complaints: List[Complaint], threshold_pct: float = 0.25) -> List[Complaint]:
        """Get complaints approaching their SLA deadline (within threshold % of SLA window)."""
        approaching = []
        for c in complaints:
            if c.sla and not c.sla.breached and c.sla.time_remaining_hours is not None:
                threshold_hours = c.sla.sla_hours * threshold_pct
                if c.sla.time_remaining_hours < threshold_hours:
                    approaching.append(c)
        return approaching
    
    def get_stalled(self, complaints: List[Complaint]) -> List[Complaint]:
        """Get all stalled complaints."""
        return [c for c in complaints if c.sla and c.sla.stalled]
    
    def avg_resolution_hours(self, complaints: List[Complaint]) -> float:
        """Calculate average resolution time in hours."""
        resolved = [c for c in complaints if c.resolved_at and c.pipeline_started_at]
        if not resolved:
            return 0.0
        
        total_hours = sum(
            (c.resolved_at - c.pipeline_started_at).total_seconds() / 3600
            for c in resolved
        )
        return round(total_hours / len(resolved), 1)
    
    def refresh_sla_status(self, complaint: Complaint) -> Complaint:
        """Update SLA time remaining for a complaint."""
        if complaint.sla:
            now = datetime.utcnow()
            remaining = (complaint.sla.deadline - now).total_seconds() / 3600
            complaint.sla.time_remaining_hours = round(max(0, remaining), 1)
            
            if remaining <= 0 and not complaint.sla.breached:
                complaint.sla.breached = True
                complaint.sla.breach_time = now
        
        return complaint
