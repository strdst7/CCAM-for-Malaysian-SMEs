"""
RLS Setup for audit_log immutability.

Run: python -m ccam_backend.rls.setup
"""
import asyncio
from sqlalchemy import text
from ccam_backend.database import engine

RLS_SQL = """
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ccam_app') THEN
        CREATE ROLE ccam_app WITH LOGIN PASSWORD 'ccam_app_password';
    END IF;
END
$$;

GRANT INSERT ON audit_logs TO ccam_app;

CREATE POLICY audit_log_insert_only ON audit_logs
    FOR INSERT
    TO ccam_app
    WITH CHECK (true);

CREATE POLICY audit_log_no_update ON audit_logs
    FOR UPDATE
    TO ccam_app
    WITH CHECK (false);

CREATE POLICY audit_log_no_delete ON audit_logs
    FOR DELETE
    TO ccam_app
    USING (false);
"""


async def setup_rls() -> None:
    async with engine.connect() as conn:
        for statement in RLS_SQL.split(";"):
            stmt = statement.strip()
            if stmt:
                await conn.execute(text(stmt + ";"))
        await conn.commit()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(setup_rls())
