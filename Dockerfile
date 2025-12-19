# syntax=docker/dockerfile:1

# Stage 1: Base image with system dependencies
FROM python:3.12-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    HF_HOME=/app/.cache

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libstdc++6 \
    make \
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

# Preload models to cache them in the image
COPY src/ ./src/

# Copy .env file if available (for build-time convenience)
# This prevents warnings during preload script execution
RUN --mount=type=bind,source=.,target=/tmp/context \
    if [ -f /tmp/context/.env ]; then \
        cp /tmp/context/.env /app/.env; \
    else \
        touch /app/.env; \
    fi

# Accept all required environment variables as build arguments
ARG HF_TOKEN
ARG DATABASE_URL
ARG TEMPORAL_HOST
ARG LOG_LEVEL=INFO
ARG DATABASE_ENGINE=mongodb
# Set them as environment variables for the build stage
ENV HF_TOKEN=${HF_TOKEN} \
    DATABASE_URL=${DATABASE_URL} \
    TEMPORAL_HOST=${TEMPORAL_HOST} \
    LOG_LEVEL=${LOG_LEVEL} \
    DATABASE_ENGINE=${DATABASE_ENGINE}
RUN /app/.venv/bin/python -m src.scripts.preload


# Stage 3: Development image
FROM base AS development

# Copy the environment and cached models from the builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/.cache /app/.cache
ENV PATH="/app/.venv/bin:$PATH"

COPY src/ ./src/
COPY pyproject.toml uv.lock ./

# Copy .env file if available (development convenience)
RUN --mount=type=bind,source=.,target=/tmp/context \
    if [ -f /tmp/context/.env ]; then \
        cp /tmp/context/.env /app/.env; \
    else \
        touch /app/.env; \
    fi

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

CMD ["make", "api"]


# Stage 4: Production base
FROM base AS production-base

# Copy the environment and cached models from the builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/.cache /app/.cache
ENV PATH="/app/.venv/bin:$PATH"

COPY src/ ./src/
COPY pyproject.toml uv.lock ./


RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /app/uploads && \
    chown -R appuser:appuser /app/uploads

USER appuser


# Stage 5: API Server (production)
FROM production-base AS api

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8000/health || exit 1

CMD ["make", "api-prod"]


# Stage 6: Temporal Worker (production)
FROM production-base AS worker

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD pgrep -f "python.*worker.py" > /dev/null || exit 1

CMD ["make", "worker"]
