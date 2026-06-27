FROM python:3.12-slim-bookworm

RUN pip install --no-cache-dir uv

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-cache

COPY src/app/ app/
COPY migrations/ migrations/
COPY alembic.ini .

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

RUN mkdir -p /app/storage/media && \
    adduser --disabled-password --gecos "" app && \
    chown -R app:app /app

USER app

EXPOSE 8000

CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
