# syntax=docker/dockerfile:1

FROM python:3.14-alpine3.24@sha256:5862d971d1f0ae26b258cefa4e893556b1d3aba81bd2ff30888704ad378bab67 AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.23@sha256:61d393e44e249f2e4b526b6c7ddcecce245946826e608e11c93ad4f5bba55b21 /uv /uvx /bin/

ENV UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/tmp/uv-cache

WORKDIR /opt/service

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-install-project \
    && rm -rf /tmp/uv-cache


FROM python:3.14-alpine3.24@sha256:5862d971d1f0ae26b258cefa4e893556b1d3aba81bd2ff30888704ad378bab67

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/service/.venv/bin:${PATH}"

WORKDIR /opt/service

RUN apk add --no-cache 'zlib=1.4-r0' \
    && addgroup -S app \
    && adduser -S -G app app \
    && python -m pip uninstall -y pip

COPY --from=builder /opt/service/.venv ./.venv
COPY app ./app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \
    --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" || exit 1

CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000"]
