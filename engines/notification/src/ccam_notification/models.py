from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from enum import Enum


class NotificationChannel(Enum):
    EMAIL = "email"
    INAPP = "in_app"


class NotificationPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"  # in-app only


@dataclass
class Notification:
    id: str
    tenant_id: str
    user_id: str
    channel: NotificationChannel
    template_key: str
    template_data: dict[str, Any]
    title: str = ""
    body: str = ""
    priority: NotificationPriority = NotificationPriority.NORMAL
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    sent_at: datetime | None = None
    error_message: str = ""


@dataclass
class NotificationTemplate:
    key: str
    subject_template: str    # string.Template format
    body_template: str       # string.Template format
    channel: NotificationChannel


@dataclass
class SendResult:
    success: bool
    channel: NotificationChannel
    notification_id: str
    error: str = ""
