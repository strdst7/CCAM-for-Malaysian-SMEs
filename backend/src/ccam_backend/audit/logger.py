from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from ccam_backend.models.audit_log import AuditLog


class AuditLogger:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        tenant_id: str,
        action: str,
        actor_type: str,
        actor_id: str,
        target_type: str,
        target_id: str,
        before: dict | None = None,
        after: dict | None = None,
        metadata: dict | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            tenant_id=tenant_id,
            action=action,
            actor_type=actor_type,
            actor_id=actor_id,
            target_type=target_type,
            target_id=target_id,
            before_json=before,
            after_json=after,
            metadata_json=metadata,
            timestamp=datetime.now(timezone.utc),
        )
        self.db.add(entry)
        await self.db.flush()
        return entry
