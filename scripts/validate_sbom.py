import json
import sys
from collections import Counter
from pathlib import Path

EXPECTED_PACKAGES = {
    "apk": {"zlib"},
    "pypi": {"fastapi", "uvicorn", "pydantic"},
}


def fail(message):
    raise SystemExit(f"FAIL [SBOM]: {message}")


def main():
    if len(sys.argv) != 2:
        fail("Usage: validate_sbom.py REPORT")

    report = Path(sys.argv[1])

    if not report.is_file():
        fail("Missing SBOM report")

    try:
        data = json.loads(report.read_text())
    except (OSError, UnicodeError, ValueError):
        fail("Invalid JSON report")

    if not isinstance(data, dict):
        fail("Invalid SBOM structure")

    if data.get("bomFormat") != "CycloneDX":
        fail("Unexpected SBOM format")

    if data.get("specVersion") != "1.7":
        fail("Unexpected CycloneDX specification version")

    metadata = data.get("metadata")

    if not isinstance(metadata, dict):
        fail("Missing SBOM metadata")

    image = metadata.get("component")

    if (
        not isinstance(image, dict)
        or not isinstance(image.get("name"), str)
        or not image["name"].strip()
    ):
        fail("Missing image identity metadata")

    components = data.get("components")

    if not isinstance(components, list) or not components:
        fail("Missing component inventory")

    counts = Counter()
    package_names = {
        "apk": set(),
        "pypi": set(),
    }

    for component in components:
        if not isinstance(component, dict):
            fail("Malformed component")

        name = component.get("name")

        if not isinstance(name, str) or not name.strip():
            fail("Component name missing")

        purl = component.get("purl")

        if purl is not None and not isinstance(purl, str):
            fail("Malformed package URL")

        purl = purl or ""

        if purl.startswith("pkg:apk/"):
            ecosystem = "apk"
        elif purl.startswith("pkg:pypi/"):
            ecosystem = "pypi"
        else:
            counts["other"] += 1
            continue

        version = component.get("version")

        if not isinstance(version, str) or not version.strip():
            fail(f"Missing version for {name}")

        if "@" not in purl:
            fail(f"Unversioned package URL for {name}")

        counts[ecosystem] += 1
        package_names[ecosystem].add(name.lower())

    for ecosystem in ("apk", "pypi"):
        if counts[ecosystem] == 0:
            fail(f"Missing {ecosystem} package inventory")

        missing = EXPECTED_PACKAGES[ecosystem] - package_names[ecosystem]

        if missing:
            fail(
                f"Missing required {ecosystem} packages: "
                f"{sorted(missing)}"
            )

    print("SBOM format: CycloneDX 1.7")
    print("Total components:", len(components))
    print("Alpine packages:", counts["apk"])
    print("Python packages:", counts["pypi"])
    print("Other components:", counts["other"])

    print("PASS [SBOM]: Required component inventory verified")


if __name__ == "__main__":
    main()
