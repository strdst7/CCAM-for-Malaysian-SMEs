from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ccam_backend.api.deps import get_db
from ccam_backend.auth.middleware import verify_hmac
from ccam_backend.models.notification_log import NotificationLog
from ccam_notification import NotificationEngine, NotificationChannel

router = APIRouter(tags=["notifications"])


class SendNotificationRequest(BaseModel):
    user_id: str = Field(..., description="Email for email channel, user ID for in-app")
    title: str = Field(..., max_length=500)
    body: str = Field(..., max_length=5000)
    channel: str = Field(default="in_app", pattern="^(email|in_app)$")


class NotificationResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    channel: str
    title: str
    body: str
    status: str
    is_read: bool
    created_at: str
    sent_at: str | None


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    unread_count: int


@router.post("/notifications/send", response_model=NotificationResponse, status_code=201)
async def send_notification(request: Request, body: SendNotificationRequest,
        db: AsyncSession = Depends(get_db), auth: tuple = Depends(verify_hmac)):
    tenant_id, _ = auth
    channel = NotificationChannel.EMAIL if body.channel == "email" else NotificationChannel.INAPP
    engine = NotificationEngine()
    results = engine.notify(tenant_id=tenant_id, user_id=body.user_id,
        title=body.title, body=body.body, channel=channel)

    # Persist to DB
    log = NotificationLog(
        tenant_id=tenant_id, user_id=body.user_id, channel=body.channel,
        title=body.title, body=body.body, status=results[0].status.value if results else "sent",
        is_read=False, sent_at=datetime.now(timezone.utc),
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)

    return NotificationResponse(id=log.id, tenant_id=log.tenant_id, user_id=log.user_id,
        channel=log.channel, title=log.title, body=log.body, status=log.status,
        is_read=log.is_read, created_at=log.created_at.isoformat() if log.created_at else "",
        sent_at=log.sent_at.isoformat() if log.sent_at else None)


@router.get("/notifications", response_model=NotificationListResponse)
async def list_notifications(request: Request, db: AsyncSession = Depends(get_db),
        auth: tuple = Depends(verify_hmac), page: int = Query(1, ge=1),
        page_size: int = Query(50, ge=1, le=100)):
    tenant_id, _ = auth
    # Count
    count_q = select(func.count()).select_from(NotificationLog).where(NotificationLog.tenant_id == tenant_id)
    total = (await db.execute(count_q)).scalar() or 0
    unread_q = count_q.where(~NotificationLog.is_read)
    unread = (await db.execute(unread_q)).scalar() or 0
    # Fetch
    q = select(NotificationLog).where(NotificationLog.tenant_id == tenant_id).order_by(NotificationLog.created_at.desc())
    q = q.offset((page-1)*page_size).limit(page_size)
    rows = (await db.execute(q)).scalars().all()
    items = [NotificationResponse(id=r.id, tenant_id=r.tenant_id, user_id=r.user_id,
        channel=r.channel, title=r.title, body=r.body, status=r.status,
        is_read=r.is_read, created_at=r.created_at.isoformat() if r.created_at else "",
        sent_at=r.sent_at.isoformat() if r.sent_at else None) for r in rows]
    return NotificationListResponse(items=items, total=total, unread_count=unread)
