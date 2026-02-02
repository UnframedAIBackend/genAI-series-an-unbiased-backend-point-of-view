# syntax=docker/dockerfile:1

# Stage 1: Base image with system dependencies
FROM python:3.12-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    HF_HOME=/app/.cache \
    HF_HUB_OFFLINE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libstdc++6 \
    make \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


# Stage 2: Dependencies build stage
FROM base AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libffi-dev \
    cmake \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy source code
COPY src/ ./src/


# Stage 3: Development image
FROM base AS development

# Copy the environment from the builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY src/ ./src/
COPY pyproject.toml uv.lock ./

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

CMD ["make", "api"]


# Stage 4: Production base
FROM base AS production-base

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH"

COPY src/ ./src/
COPY pyproject.toml uv.lock ./
COPY Makefile ./

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /app/uploads && \
    chown -R appuser:appuser /app/uploads

USER appuser


# Stage 5: API Server (production)
FROM production-base AS api

CMD ["make", "api-prod"]

# Stage 6: Temporal Worker (production)
FROM production-base AS worker

CMD ["make", "rag-worker"]
