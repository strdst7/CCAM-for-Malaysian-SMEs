import pytest
from ccam_backend.audit.logger import AuditLogger


@pytest.mark.skip(reason="Requires a running PostgreSQL database")
class TestAuditLogger:
    @pytest.mark.asyncio
    async def test_audit_log_creation(self, db_session):
        logger = AuditLogger(db_session)
        entry = await logger.log(
            tenant_id="test_tenant",
            action="test.action",
            actor_type="system",
            actor_id="test_actor",
            target_type="test_entity",
            target_id="test_target",
            before={"key": "old_value"},
            after={"key": "new_value"},
        )
        assert entry.id is not None
        assert entry.action == "test.action"
        assert entry.before_json == {"key": "old_value"}
        assert entry.after_json == {"key": "new_value"}
        assert entry.tenant_id == "test_tenant"
