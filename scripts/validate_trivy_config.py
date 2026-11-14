import json
import sys
from collections import Counter
from pathlib import Path

VALID_SEVERITIES = {
    "CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"
}
BLOCKING = {"CRITICAL", "HIGH"}


def fail(message):
    raise SystemExit(f"FAIL [Config]: {message}")


def main():
    if len(sys.argv) != 3:
        fail("Usage: validate_trivy_config.py REPORT EXIT_CODE")

    report = Path(sys.argv[1])

    try:
        status = int(sys.argv[2])
    except ValueError:
        fail("Invalid scanner exit code")

    if status != 0:
        fail(f"Scanner failed with exit code {status}")

    if not report.is_file():
        fail("Missing configuration report")

    try:
        data = json.loads(report.read_text())
    except (OSError, ValueError):
        fail("Invalid JSON report")

    if not isinstance(data, dict):
        fail("Invalid report structure")

    if data.get("Errors"):
        fail("Scanner reported errors")

    results = data.get("Results")

    if not isinstance(results, list) or not results:
        fail("Missing scan results")

    dockerfiles = [
        item for item in results
        if isinstance(item, dict)
        and item.get("Type") == "dockerfile"
    ]

    if len(dockerfiles) != 1:
        fail("Expected exactly one Dockerfile result")

    target = dockerfiles[0].get("Target")

    if not isinstance(target, str) or Path(target).name != "Dockerfile":
        fail("Unexpected scan target")

    findings = dockerfiles[0].get("Misconfigurations")

    if findings is None:
        findings = []

    if not isinstance(findings, list):
        fail("Malformed findings list")

    counts = Counter()
    rules = set()

    for finding in findings:
        if not isinstance(finding, dict):
            fail("Malformed finding")

        severity = finding.get("Severity")
        rule = finding.get("ID")

        if severity not in VALID_SEVERITIES:
            fail("Invalid finding severity")

        if not isinstance(rule, str) or not rule:
            fail("Missing rule ID")

        counts[severity] += 1
        rules.add(rule)

    print("Dockerfile targets: 1")

    for severity in (
        "CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"
    ):
        print(f"{severity}: {counts[severity]}")

    blocked = sum(counts[level] for level in BLOCKING)

    if blocked:
        print(f"BLOCK [Config]: {blocked} blocking finding(s)")
        print("Rules:", ", ".join(sorted(rules)))
        raise SystemExit(1)

    print("PASS [Config]: No HIGH/CRITICAL misconfigurations")


if __name__ == "__main__":
    main()
