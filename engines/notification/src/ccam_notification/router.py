"""Notification router that selects and dispatches to channels.

Routes notifications to the appropriate channel(s) based on
the notification configuration and user preferences.
"""
import string
from typing import Any

from ccam_notification.models import (Notification, NotificationTemplate,
    NotificationChannel, SendResult)
from ccam_notification.email_channel import EmailChannel
from ccam_notification.inapp_channel import InAppChannel
from ccam_notification.exceptions import TemplateError, ChannelError


class NotificationRouter:
    """Routes notifications to configured channels with template rendering."""

    def __init__(
        self,
        email_channel: EmailChannel | None = None,
        inapp_channel: InAppChannel | None = None,
    ):
        self._email = email_channel or EmailChannel()
        self._inapp = inapp_channel or InAppChannel()
        self._templates: dict[str, NotificationTemplate] = {}
        self._default_templates: dict[NotificationChannel, str] = {}

    def register_template(self, template: NotificationTemplate) -> None:
        """Register a notification template."""
        self._templates[template.key] = template

    def set_default_template(self, channel: NotificationChannel, template_key: str) -> None:
        """Set the default template key for a channel."""
        self._default_templates[channel] = template_key

    def send(
        self,
        notification: Notification,
        channels: list[NotificationChannel] | None = None,
    ) -> list[SendResult]:
        """Send a notification through one or more channels.

        Args:
            notification: The notification to send.
            channels: Channels to use. Defaults to the notification's own channel.

        Returns:
            List of SendResult (one per channel).
        """
        channels = channels or [notification.channel]
        results = []

        for channel in channels:
            # Get template
            template_key = notification.template_key or self._default_templates.get(channel, "")
            template = self._templates.get(template_key)

            if template is None and template_key:
                raise TemplateError(f"Template '{template_key}' not found for channel {channel.value}")

            # Send via appropriate channel
            if channel == NotificationChannel.EMAIL:
                result = self._email.send(notification, template or self._default_email_template())
            elif channel == NotificationChannel.INAPP:
                result = self._inapp.send(notification, template or self._default_inapp_template())
            else:
                raise ChannelError(f"Unsupported channel: {channel}")

            results.append(result)

        return results

    def _default_email_template(self) -> NotificationTemplate:
        return NotificationTemplate(
            key="_default_email",
            subject_template="${title}",
            body_template="${body}",
            channel=NotificationChannel.EMAIL,
        )

    def _default_inapp_template(self) -> NotificationTemplate:
        return NotificationTemplate(
            key="_default_inapp",
            subject_template="${title}",
            body_template="${body}",
            channel=NotificationChannel.INAPP,
        )
