# ── builder stage ─────────────────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# asyncmy needs a C compiler at build time (no pre-built wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_FROZEN=1 \
    UV_LINK_MODE=copy

# Install dependencies first (layer cache)
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

# Copy project source and install as a non-editable wheel.
# uv sync installs the project in editable mode by default, which creates a .pth
# file pointing to /app/src — that path won't exist in the runner, so we force a
# non-editable install here.
COPY src ./src
COPY migrations ./migrations
COPY alembic.ini .
RUN uv sync --no-dev && uv pip install --force-reinstall --no-deps /app

# ── runner stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

RUN groupadd --system --gid 1001 app && \
    useradd --system --uid 1001 --gid app --no-create-home app && \
    mkdir -p /app/storage/media && \
    chown -R app:app /app

COPY --from=builder --chown=app:app /app/.venv ./.venv
COPY --from=builder --chown=app:app /app/migrations ./migrations
COPY --from=builder --chown=app:app /app/alembic.ini .

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

CMD uvicorn app.main:app --host 0.0.0.0 --port 8000
