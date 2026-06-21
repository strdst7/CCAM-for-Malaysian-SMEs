"""High-level notification engine."""
import uuid
from datetime import datetime
from typing import Any

from ccam_notification.models import (Notification, NotificationChannel,
    NotificationPriority, NotificationStatus, NotificationTemplate, SendResult)
from ccam_notification.router import NotificationRouter
from ccam_notification.email_channel import EmailChannel
from ccam_notification.inapp_channel import InAppChannel


class NotificationEngine:
    """Notification engine with template management and multi-channel dispatch."""

    def __init__(self):
        self._router = NotificationRouter()

    @property
    def router(self) -> NotificationRouter:
        return self._router

    def notify(
        self,
        tenant_id: str,
        user_id: str,
        title: str,
        body: str,
        channel: NotificationChannel = NotificationChannel.INAPP,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        template_key: str = "",
        template_data: dict[str, Any] | None = None,
    ) -> list[SendResult]:
        """Create and send a notification.

        Args:
            tenant_id: Tenant scope.
            user_id: Recipient identifier (email for email channel, user ID for in-app).
            title: Notification title.
            body: Notification body text.
            channel: Target channel.
            priority: Notification priority.
            template_key: Optional registered template key.
            template_data: Data for template rendering.

        Returns:
            List of SendResult.
        """
        notification = Notification(
            id=f"n-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            user_id=user_id,
            channel=channel,
            template_key=template_key,
            template_data=template_data or {"title": title, "body": body},
            title=title,
            body=body,
            priority=priority,
            status=NotificationStatus.PENDING,
            created_at=datetime.now(),
        )

        return self._router.send(notification, [channel])

    def notify_email(
        self,
        tenant_id: str,
        email: str,
        subject: str,
        body: str,
        template_data: dict[str, Any] | None = None,
    ) -> list[SendResult]:
        """Convenience: send an email notification."""
        return self.notify(
            tenant_id=tenant_id,
            user_id=email,
            title=subject,
            body=body,
            channel=NotificationChannel.EMAIL,
            template_data=template_data or {"title": subject, "body": body},
        )

    def notify_inapp(
        self,
        tenant_id: str,
        user_id: str,
        title: str,
        body: str,
    ) -> list[SendResult]:
        """Convenience: send an in-app notification."""
        return self.notify(
            tenant_id=tenant_id,
            user_id=user_id,
            title=title,
            body=body,
            channel=NotificationChannel.INAPP,
        )


def send_notification(
    tenant_id: str,
    user_id: str,
    title: str,
    body: str,
    channel: NotificationChannel = NotificationChannel.INAPP,
) -> list[SendResult]:
    """Convenience function — send a notification with default engine."""
    engine = NotificationEngine()
    return engine.notify(tenant_id, user_id, title, body, channel)
