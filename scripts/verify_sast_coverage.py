import json
import sys
from pathlib import Path


def main():
    report_path = Path(sys.argv[1])
    targets = [Path(path) for path in sys.argv[2:]]

    try:
        report = json.loads(report_path.read_text())
        scanned = report["paths"]["scanned"]
    except (OSError, ValueError, KeyError, TypeError):
        raise SystemExit("FAIL [SAST]: Invalid coverage report")

    if not isinstance(scanned, list):
        raise SystemExit("FAIL [SAST]: Invalid scanned-file list")

    expected = set()

    for target in targets:
        if target.is_file() and target.suffix == ".py":
            expected.add(target.resolve())
        elif target.is_dir():
            expected.update(
                path.resolve()
                for path in target.rglob("*.py")
                if "__pycache__" not in path.parts
            )

    if not expected:
        raise SystemExit("FAIL [SAST]: No Python targets found")

    actual = {Path(path).resolve() for path in scanned}
    missing = expected - actual

    if missing:
        for path in sorted(missing):
            print(f"NOT SCANNED: {path}")
        raise SystemExit("FAIL [SAST]: Incomplete coverage")

    print(f"PASS [SAST]: Coverage {len(expected)}/{len(expected)}")


if __name__ == "__main__":
    main()
