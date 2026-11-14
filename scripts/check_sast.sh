#!/usr/bin/env bash
set -euo pipefail
umask 077

cd "$(dirname "$0")/.."

SEMGREP="${SEMGREP_BIN:-$HOME/.local/bin/semgrep}"
REPORT="reports/semgrep-sast.json"

if [[ $# -gt 0 ]]; then
    TARGETS=("$@")
else
    TARGETS=(app scripts tests)
fi

for target in "${TARGETS[@]}"; do
    if [[ ! -e "$target" ]]; then
        echo "FAIL [SAST]: Missing target: $target" >&2
        exit 1
    fi
done

mkdir -p reports
rm -f -- "$REPORT"

echo "=== Running Semgrep security gate ==="

STATUS=0

"$SEMGREP" scan \
    --config security/semgrep.yml \
    --no-git-ignore \
    --disable-nosem \
    --disable-version-check \
    --strict \
    --error \
    --metrics=off \
    --json \
    --output "$REPORT" \
    "${TARGETS[@]}" || STATUS=$?

python3 scripts/verify_sast_coverage.py "$REPORT" "${TARGETS[@]}"
python3 scripts/validate_semgrep.py "$REPORT" "$STATUS"
