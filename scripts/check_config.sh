#!/usr/bin/env bash
set -euo pipefail
umask 077

cd "$(dirname "$0")/.."

TRIVY_IMAGE="ghcr.io/aquasecurity/trivy@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb"

TARGET="${1:-Dockerfile}"
REPORT="$PWD/reports/trivy-config-gate.json"
CACHE="$HOME/.cache/trivy"

if [[ ! -f "$TARGET" ]]; then
    echo "FAIL [Config]: Dockerfile not found" >&2
    exit 1
fi

mkdir -p reports "$CACHE"

TEMP_DIR=$(mktemp -d "$HOME/sdp-config-gate.XXXXXX")
trap 'rm -rf -- "$TEMP_DIR"' EXIT

cp -- "$TARGET" "$TEMP_DIR/Dockerfile"

rm -f -- "$REPORT"

echo "=== Running Dockerfile security gate ==="

STATUS=0

docker run --rm \
    --user "$(id -u):$(id -g)" \
    -v "$TEMP_DIR:/workspace:ro" \
    -v "$CACHE:/cache" \
    -v "$PWD/reports:/reports" \
    "$TRIVY_IMAGE" config \
    --cache-dir /cache \
    --misconfig-scanners dockerfile \
    --format json \
    --exit-code 0 \
    --output /reports/trivy-config-gate.json \
    /workspace || STATUS=$?

echo "Scanner exit code: $STATUS"

python3 scripts/validate_trivy_config.py \
    "$REPORT" "$STATUS"

echo "PASS: Docker configuration gate completed"
