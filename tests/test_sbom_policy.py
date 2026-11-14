import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest


VALIDATOR = (
    Path(__file__).resolve().parents[1]
    / "scripts/validate_sbom.py"
)


def valid_sbom():
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.7",
        "metadata": {
            "component": {
                "name": "/input/image.tar",
                "type": "container",
            }
        },
        "components": [
            {
                "name": "zlib",
                "version": "1.4-r0",
                "purl": "pkg:apk/alpine/zlib@1.4-r0",
            },
            {
                "name": "fastapi",
                "version": "0.162.7",
                "purl": "pkg:pypi/fastapi@0.162.7",
            },
            {
                "name": "uvicorn",
                "version": "0.54.0",
                "purl": "pkg:pypi/uvicorn@0.54.0",
            },
            {
                "name": "pydantic",
                "version": "2.14.3",
                "purl": "pkg:pypi/pydantic@2.14.3",
            },
        ],
    }


def run_validator(tmp_path, content):
    report = tmp_path / "sbom.cdx.json"

    if content is not None:
        if isinstance(content, str):
            report.write_text(content)
        else:
            report.write_text(json.dumps(content))

    return subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            str(report),
        ],
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize(
    "scenario,expected_pass",
    [
        ("valid", True),
        ("missing_report", False),
        ("malformed_json", False),
        ("wrong_format", False),
        ("wrong_version", False),
        ("missing_metadata", False),
        ("missing_image_identity", False),
        ("missing_components", False),
        ("empty_components", False),
        ("missing_alpine", False),
        ("missing_python", False),
        ("missing_fastapi", False),
        ("missing_uvicorn", False),
        ("missing_pydantic", False),
        ("missing_zlib", False),
        ("missing_package_version", False),
        ("unversioned_purl", False),
        ("malformed_component", False),
        ("malformed_purl", False),
    ],
)
def test_sbom_policy(tmp_path, scenario, expected_pass):
    data = copy.deepcopy(valid_sbom())

    if scenario == "missing_report":
        data = None

    elif scenario == "malformed_json":
        data = "{invalid-json"

    elif scenario == "wrong_format":
        data["bomFormat"] = "SPDX"

    elif scenario == "wrong_version":
        data["specVersion"] = "0.1"

    elif scenario == "missing_metadata":
        data.pop("metadata")

    elif scenario == "missing_image_identity":
        data["metadata"]["component"]["name"] = ""

    elif scenario == "missing_components":
        data.pop("components")

    elif scenario == "empty_components":
        data["components"] = []

    elif scenario == "missing_alpine":
        data["components"] = [
            item for item in data["components"]
            if item["name"] != "zlib"
        ]

    elif scenario == "missing_python":
        data["components"] = [
            item for item in data["components"]
            if item["name"] == "zlib"
        ]

    elif scenario == "missing_package_version":
        data["components"][0].pop("version")

    elif scenario.startswith("missing_"):
        name = scenario.removeprefix("missing_")

        data["components"] = [
            item for item in data["components"]
            if item["name"] != name
        ]

    elif scenario == "unversioned_purl":
        data["components"][0]["purl"] = (
            "pkg:apk/alpine/zlib"
        )

    elif scenario == "malformed_component":
        data["components"][0] = "invalid-component"

    elif scenario == "malformed_purl":
        data["components"][0]["purl"] = {
            "invalid": True
        }

    result = run_validator(tmp_path, data)

    actual_pass = result.returncode == 0

    assert actual_pass == expected_pass, (
        f"Scenario: {scenario}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
