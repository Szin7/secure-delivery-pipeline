import json
import sys
from pathlib import Path


def main():
    report = Path(sys.argv[1])
    exit_code = int(sys.argv[2])
    scope = sys.argv[3]

    if not report.is_file():
        raise SystemExit(f"FAIL [{scope}]: Missing scanner report")

    try:
        findings = json.loads(report.read_text())
    except (OSError, ValueError):
        raise SystemExit(f"FAIL [{scope}]: Invalid JSON report")

    if not isinstance(findings, list):
        raise SystemExit(f"FAIL [{scope}]: Unexpected report format")

    if exit_code == 0 and not findings:
        print(f"PASS [{scope}]: No secrets detected")
        return

    if exit_code == 3 and findings:
        rules = sorted({
            item.get("RuleID", "unknown")
            for item in findings
            if isinstance(item, dict)
        })
        print(
            f"BLOCK [{scope}]: {len(findings)} finding(s); "
            f"rules: {', '.join(rules)}"
        )
        raise SystemExit(1)

    raise SystemExit(
        f"FAIL [{scope}]: Scanner/report mismatch "
        f"(exit code {exit_code})"
    )


if __name__ == "__main__":
    main()
