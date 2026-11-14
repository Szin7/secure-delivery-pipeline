# syntax=docker/dockerfile:1

FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /uvx /bin/

ENV UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/tmp/uv-cache

WORKDIR /opt/service

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-install-project \
    && rm -rf /tmp/uv-cache


FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/service/.venv/bin:${PATH}"

WORKDIR /opt/service

RUN groupadd --system app \
    && useradd --system --gid app app

COPY --from=builder /opt/service/.venv ./.venv
COPY app ./app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \
    --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" || exit 1

CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000"]
