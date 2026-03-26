# Stage 1: Build
FROM python:3.11-slim AS builder

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock* ./
COPY src/ src/

RUN uv sync --no-dev --frozen 2>/dev/null || uv sync --no-dev

# Stage 2: Runtime
FROM python:3.11-slim AS runtime

RUN groupadd --gid 1000 vectraxis && \
    useradd --uid 1000 --gid vectraxis --shell /bin/bash --create-home vectraxis

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

USER vectraxis

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

CMD ["uvicorn", "vectraxis.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
