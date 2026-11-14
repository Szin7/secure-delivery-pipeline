#!/usr/bin/env bash
set -euo pipefail
umask 077

cd "$(dirname "$0")/.."

IMAGE="ghcr.io/gitleaks/gitleaks@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f"

mkdir -p reports

run_scan() {
    local scope="$1"
    local report="reports/gitleaks-${scope}.json"
    local status=0

    rm -f -- "$report"

    case "$scope" in
        history)
            docker run --rm --network none \
                -v "$PWD:/repo:ro" \
                -v "$PWD/reports:/output" \
                -w /repo \
                -e GIT_CONFIG_COUNT=1 \
                -e GIT_CONFIG_KEY_0=safe.directory \
                -e GIT_CONFIG_VALUE_0=/repo \
                "$IMAGE" git \
                --no-banner \
                --redact=100 \
                --exit-code=3 \
                --log-opts="--all" \
                --report-format=json \
                --report-path=/output/gitleaks-history.json \
                /repo || status=$?
            ;;

        working-tree)
            docker run --rm --network none \
                -v "$TEMP_DIR/source:/source:ro" \
                -v "$PWD/reports:/output" \
                "$IMAGE" dir \
                --no-banner \
                --redact=100 \
                --exit-code=3 \
                --report-format=json \
                --report-path=/output/gitleaks-working-tree.json \
                /source || status=$?
            ;;

        *)
            echo "Unknown scan scope: $scope" >&2
            return 1
            ;;
    esac

    python3 scripts/validate_gitleaks.py \
        "$report" "$status" "$scope"
}

echo "=== Scanning complete Git history ==="
run_scan history

echo "=== Preparing working-tree snapshot ==="

TEMP_DIR=$(mktemp -d "$HOME/sdp-source-scan.XXXXXX")
trap 'rm -rf -- "$TEMP_DIR"' EXIT

mkdir -p "$TEMP_DIR/source"

git ls-files --cached --others --exclude-standard -z \
    | tar --null --no-recursion -T - -cf - \
    | tar -xf - -C "$TEMP_DIR/source"

echo "=== Scanning current project files ==="
run_scan working-tree

echo "PASS: All required Gitleaks checks completed"
