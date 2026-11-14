#!/usr/bin/env bash
set -euo pipefail
umask 077

cd "$(dirname "$0")/.."

TRIVY_IMAGE="ghcr.io/aquasecurity/trivy@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb"

APP_IMAGE="${1:-secure-delivery-pipeline:local}"

REPORT="$PWD/reports/trivy-image-gate.json"
CACHE="$HOME/.cache/trivy"

mkdir -p reports "$CACHE"

TEMP_DIR=$(mktemp -d "$HOME/sdp-trivy-gate.XXXXXX")
trap 'rm -rf -- "$TEMP_DIR"' EXIT

echo "=== Checking application image ==="

IMAGE_ID=$(docker image inspect "$APP_IMAGE" --format '{{.Id}}')
echo "Image: $APP_IMAGE"
echo "Image ID: $IMAGE_ID"

echo "=== Exporting candidate image ==="

docker save \
    --output "$TEMP_DIR/image.tar" \
    "$APP_IMAGE"

echo "=== Running Trivy vulnerability scan ==="

rm -f -- "$REPORT"

STATUS=0

docker run --rm \
    --user "$(id -u):$(id -g)" \
    -v "$TEMP_DIR:/input:ro" \
    -v "$CACHE:/cache" \
    -v "$PWD/reports:/reports" \
    "$TRIVY_IMAGE" image \
    --input /input/image.tar \
    --cache-dir /cache \
    --scanners vuln \
    --pkg-types os,library \
    --format json \
    --exit-code 0 \
    --output /reports/trivy-image-gate.json \
    || STATUS=$?

echo "Scanner exit code: $STATUS"

python3 scripts/validate_trivy_vulns.py \
    "$REPORT" "$STATUS"

echo "PASS: Image vulnerability gate completed"
