"""Pydantic schemas for worker job API."""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class JobEnqueueRequest(BaseModel):
    microflow_yaml: str = Field(..., description="YAML microflow definition", min_length=1)
    payload: Optional[dict] = Field(None, description="Input data for microflow execution")
    idempotency_key: Optional[str] = Field(
        None, description="Dedup key: skips execution if job with same key completed", max_length=255
    )


class JobResponse(BaseModel):
    id: str
    tenant_id: str
    status: str
    microflow_yaml: str
    payload: Optional[dict] = None
    idempotency_key: Optional[str] = None
    result: Optional[Any] = None
    error_message: Optional[str] = None
    retry_count: int
    max_retries: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int
