"""In-app notification channel.

Stores notifications that can be retrieved via API (SSE or polling).
This module provides the in-memory store; backend persistence is
added in Plan 04 via database models.
"""
from datetime import datetime

from ccam_notification.models import (Notification, NotificationTemplate,
    NotificationStatus, SendResult, NotificationChannel)


class InAppChannel:
    """In-app notification store.

    Notifications are stored in memory and retrieved via the
    notification API. The backend (Plan 04) adds database persistence
    and SSE/polling endpoints.
    """

    def __init__(self):
        self._notifications: dict[str, Notification] = {}

    def send(self, notification: Notification, template: NotificationTemplate) -> SendResult:
        """Store an in-app notification."""
        import string
        import uuid

        # Generate body from template
        tmpl = string.Template(template.body_template if template.body_template else template.subject_template)
        rendered_body = tmpl.safe_substitute(**notification.template_data)

        notif = Notification(
            id=notification.id or f"notif-{uuid.uuid4().hex[:12]}",
            tenant_id=notification.tenant_id,
            user_id=notification.user_id,
            channel=NotificationChannel.INAPP,
            template_key=notification.template_key,
            template_data=notification.template_data,
            title=template.subject_template,
            body=rendered_body,
            priority=notification.priority,
            status=NotificationStatus.SENT,
            created_at=datetime.now(),
            sent_at=datetime.now(),
        )

        self._notifications[notif.id] = notif

        return SendResult(
            success=True,
            channel=NotificationChannel.INAPP,
            notification_id=notif.id,
        )

    def get_notifications(self, user_id: str, limit: int = 50) -> list[Notification]:
        """Get in-app notifications for a user, newest first."""
        user_notifs = [
            n for n in self._notifications.values()
            if n.user_id == user_id
        ]
        user_notifs.sort(key=lambda n: n.created_at, reverse=True)
        return user_notifs[:limit]

    def mark_read(self, notification_id: str) -> bool:
        """Mark an in-app notification as read."""
        if notification_id in self._notifications:
            self._notifications[notification_id].status = NotificationStatus.READ
            return True
        return False

    def count_unread(self, user_id: str) -> int:
        """Count unread notifications for a user."""
        return sum(
            1 for n in self._notifications.values()
            if n.user_id == user_id and n.status == NotificationStatus.SENT
        )
