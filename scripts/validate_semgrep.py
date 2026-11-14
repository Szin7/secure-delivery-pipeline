import json
import sys
from pathlib import Path


def main():
    report = Path(sys.argv[1])
    status = int(sys.argv[2])

    if not report.is_file():
        raise SystemExit("FAIL [SAST]: Missing scanner report")

    try:
        data = json.loads(report.read_text())
    except (OSError, ValueError):
        raise SystemExit("FAIL [SAST]: Invalid JSON report")

    if not isinstance(data, dict):
        raise SystemExit("FAIL [SAST]: Invalid report structure")

    findings = data.get("results")
    errors = data.get("errors")
    paths = data.get("paths")

    if not isinstance(findings, list):
        raise SystemExit("FAIL [SAST]: Invalid findings list")

    if not isinstance(errors, list):
        raise SystemExit("FAIL [SAST]: Invalid errors list")

    if not isinstance(paths, dict):
        raise SystemExit("FAIL [SAST]: Missing scan paths")

    scanned = paths.get("scanned")

    if not isinstance(scanned, list) or not scanned:
        raise SystemExit("FAIL [SAST]: No files scanned")

    if errors:
        raise SystemExit(
            f"FAIL [SAST]: {len(errors)} scanner error(s)"
        )

    if not all(isinstance(item, dict) for item in findings):
        raise SystemExit("FAIL [SAST]: Malformed findings")

    if status == 0 and not findings:
        print(
            f"PASS [SAST]: {len(scanned)} files scanned, "
            "no findings"
        )
        return

    if status == 1 and findings:
        rules = sorted({
            str(item.get("check_id", "unknown"))
            for item in findings
        })

        print(
            f"BLOCK [SAST]: {len(findings)} finding(s); "
            f"rules: {', '.join(rules)}"
        )
        raise SystemExit(1)

    raise SystemExit(
        f"FAIL [SAST]: Scanner/report mismatch "
        f"(exit code {status})"
    )


if __name__ == "__main__":
    main()
