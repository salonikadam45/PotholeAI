"""
Citizen Notification Service
Manages notification history and delivery simulation.
"""

from typing import List
from backend.models import CitizenNotification


class NotificationService:
    """
    Stores and queries citizen notifications.
    In production, this would integrate with SMS/email/push APIs.
    """
    
    def __init__(self):
        self._notifications: List[CitizenNotification] = []
    
    def add(self, notification: CitizenNotification):
        """Store a notification."""
        self._notifications.append(notification)
    
    def add_many(self, notifications: List[CitizenNotification]):
        """Store multiple notifications."""
        self._notifications.extend(notifications)
    
    def get_all(self) -> List[CitizenNotification]:
        """Get all notifications (newest first)."""
        return sorted(self._notifications, key=lambda n: n.timestamp, reverse=True)
    
    def get_by_complaint(self, complaint_id: str) -> List[CitizenNotification]:
        """Get all notifications for a specific complaint."""
        return sorted(
            [n for n in self._notifications if n.complaint_id == complaint_id],
            key=lambda n: n.timestamp
        )
    
    def get_recent(self, count: int = 20) -> List[CitizenNotification]:
        """Get the most recent N notifications."""
        sorted_notifs = sorted(self._notifications, key=lambda n: n.timestamp, reverse=True)
        return sorted_notifs[:count]
    
    def count(self) -> int:
        return len(self._notifications)
