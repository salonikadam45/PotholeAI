"""
Append-only Audit Logger
Records every agent decision with full traceability.
"""

import json
from datetime import datetime
from typing import List, Optional
from backend.models import AuditLogEntry


class AuditLogger:
    """
    Centralized, append-only audit trail.
    Every agent action is logged here for full traceability and compliance.
    """
    
    def __init__(self):
        self._entries: List[AuditLogEntry] = []
    
    def log(self, entry: AuditLogEntry):
        """Append a single audit entry."""
        self._entries.append(entry)
    
    def log_many(self, entries: List[AuditLogEntry]):
        """Append multiple audit entries."""
        self._entries.extend(entries)
    
    def get_all(self) -> List[AuditLogEntry]:
        """Get all audit entries (sorted by timestamp)."""
        return sorted(self._entries, key=lambda e: e.timestamp, reverse=True)
    
    def get_by_complaint(self, complaint_id: str) -> List[AuditLogEntry]:
        """Get all audit entries for a specific complaint."""
        return sorted(
            [e for e in self._entries if e.complaint_id == complaint_id],
            key=lambda e: e.timestamp
        )
    
    def get_by_agent(self, agent_id: str) -> List[AuditLogEntry]:
        """Get all entries from a specific agent."""
        return [e for e in self._entries if e.agent_id == agent_id]
    
    def get_recent(self, count: int = 50) -> List[AuditLogEntry]:
        """Get the most recent N entries."""
        sorted_entries = sorted(self._entries, key=lambda e: e.timestamp, reverse=True)
        return sorted_entries[:count]
    
    def count(self) -> int:
        """Total number of audit entries."""
        return len(self._entries)
    
    def export_json(self) -> str:
        """Export all entries as JSON."""
        return json.dumps(
            [e.model_dump(mode="json") for e in self._entries],
            indent=2, default=str
        )
