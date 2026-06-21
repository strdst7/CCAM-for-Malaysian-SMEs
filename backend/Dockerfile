FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv

WORKDIR /app

COPY pyproject.toml .
RUN uv sync --no-dev --frozen

FROM python:3.14-slim AS runner

RUN groupadd -r ccam && useradd -r -g ccam -d /app -s /bin/false ccam

WORKDIR /app

COPY --from=builder /app/.venv .venv
COPY src/ src/
COPY alembic.ini .
COPY alembic/ alembic/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

USER ccam

EXPOSE 8000

CMD ["uvicorn", "ccam_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
