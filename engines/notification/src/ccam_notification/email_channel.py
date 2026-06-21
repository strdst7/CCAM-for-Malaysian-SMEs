"""Email notification channel — SendGrid primary, SMTP fallback."""
import os
import smtplib
import string
from email.mime.text import MIMEText
from email.utils import formatdate

from ccam_notification.models import (Notification, NotificationTemplate,
    NotificationStatus, SendResult, NotificationChannel)
from ccam_notification.exceptions import DeliveryError


class EmailChannel:
    """Email notification delivery channel."""

    def __init__(
        self,
        from_email: str | None = None,
        sendgrid_api_key: str | None = None,
    ):
        self._from_email = from_email or os.environ.get(
            "SENDGRID_FROM_EMAIL", "noreply@ccam.local"
        )
        self._sendgrid_key = sendgrid_api_key or os.environ.get("SENDGRID_API_KEY", "")

    def send(self, notification: Notification, template: NotificationTemplate) -> SendResult:
        """Send a notification via email.

        Uses SendGrid if API key is configured, otherwise falls back to SMTP.
        """
        try:
            # Render template
            tmpl = string.Template(template.subject_template)
            subject = tmpl.safe_substitute(**notification.template_data)
            tmpl = string.Template(template.body_template)
            body = tmpl.safe_substitute(**notification.template_data)

            if self._sendgrid_key:
                return self._send_via_sendgrid(notification, subject, body)
            else:
                return self._send_via_smtp(notification, subject, body)

        except Exception as e:
            return SendResult(
                success=False, channel=NotificationChannel.EMAIL,
                notification_id=notification.id, error=str(e),
            )

    def _send_via_sendgrid(self, notification: Notification, subject: str, body: str) -> SendResult:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email
        message = Mail(
            from_email=Email(self._from_email),
            to_emails=Email(notification.user_id),  # user_id = email in v1
            subject=subject,
            plain_text_content=body,
        )
        sg = SendGridAPIClient(self._sendgrid_key)
        response = sg.send(message)
        return SendResult(
            success=response.status_code in (200, 201, 202),
            channel=NotificationChannel.EMAIL,
            notification_id=notification.id,
        )

    def _send_via_smtp(self, notification: Notification, subject: str, body: str) -> SendResult:
        msg = MIMEText(body)
        msg["From"] = self._from_email
        msg["To"] = notification.user_id
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)

        smtp_host = os.environ.get("SMTP_HOST", "localhost")
        smtp_port = int(os.environ.get("SMTP_PORT", "25"))
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            user = os.environ.get("SMTP_USER", "")
            if user:
                server.login(user, os.environ.get("SMTP_PASS", ""))
            server.send_message(msg)

        return SendResult(
            success=True, channel=NotificationChannel.EMAIL,
            notification_id=notification.id,
        )
