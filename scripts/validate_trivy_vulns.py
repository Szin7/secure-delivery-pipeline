import json
import sys
from collections import Counter
from pathlib import Path

REQUIRED_TYPES = {"alpine", "python-pkg"}
VALID_SEVERITIES = {
    "CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"
}
BLOCKING_SEVERITIES = {"CRITICAL", "HIGH"}


def fail(message):
    raise SystemExit(f"FAIL [Trivy]: {message}")


def main():
    if len(sys.argv) != 3:
        fail("Usage: validate_trivy_vulns.py REPORT EXIT_CODE")

    report = Path(sys.argv[1])

    try:
        status = int(sys.argv[2])
    except ValueError:
        fail("Invalid scanner exit code")

    if status != 0:
        fail(f"Scanner did not complete successfully (exit {status})")

    if not report.is_file():
        fail("Missing scan report")

    try:
        data = json.loads(report.read_text())
    except (OSError, ValueError):
        fail("Invalid JSON report")

    if not isinstance(data, dict):
        fail("Invalid report structure")

    if data.get("ArtifactType") != "container_image":
        fail("Unexpected artifact type")

    if data.get("Errors"):
        fail("Scanner reported errors")

    results = data.get("Results")

    if not isinstance(results, list) or not results:
        fail("Missing scan results")

    covered = set()
    counts = Counter()
    package_count = 0

    for result in results:
        if not isinstance(result, dict):
            fail("Malformed scan result")

        kind = result.get("Type")

        if kind not in REQUIRED_TYPES:
            continue

        packages = result.get("Packages")

        if not isinstance(packages, list) or not packages:
            fail(f"Missing package inventory for {kind}")

        package_count += len(packages)
        covered.add(kind)

        findings = result.get("Vulnerabilities")

        if findings is None:
            findings = []

        if not isinstance(findings, list):
            fail(f"Malformed vulnerability list for {kind}")

        for finding in findings:
            if not isinstance(finding, dict):
                fail("Malformed vulnerability record")

            severity = finding.get("Severity")
            identifier = finding.get("VulnerabilityID")

            if severity not in VALID_SEVERITIES:
                fail("Missing or invalid vulnerability severity")

            if not isinstance(identifier, str) or not identifier:
                fail("Missing vulnerability identifier")

            counts[severity] += 1

    missing = REQUIRED_TYPES - covered

    if missing:
        fail(f"Missing required coverage: {sorted(missing)}")

    print(f"Packages inspected: {package_count}")

    for severity in (
        "CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"
    ):
        print(f"{severity}: {counts[severity]}")

    blocking = sum(
        counts[severity] for severity in BLOCKING_SEVERITIES
    )

    if blocking:
        print(f"BLOCK [Trivy]: {blocking} HIGH/CRITICAL findings")
        raise SystemExit(1)

    print("PASS [Trivy]: Required image coverage verified")
    print("PASS [Trivy]: No HIGH/CRITICAL findings")


if __name__ == "__main__":
    main()
