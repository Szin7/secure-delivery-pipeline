import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest


VALIDATOR = (
    Path(__file__).resolve().parents[1]
    / "scripts/validate_trivy_vulns.py"
)


def clean_report():
    return {
        "ArtifactType": "container_image",
        "Results": [
            {
                "Type": "alpine",
                "Packages": [{"Name": "zlib"}],
                "Vulnerabilities": [],
            },
            {
                "Type": "python-pkg",
                "Packages": [{"Name": "fastapi"}],
                "Vulnerabilities": [],
            },
        ],
    }


def run_validator(tmp_path, data, scanner_exit=0):
    report = tmp_path / "report.json"

    if data is not None:
        if isinstance(data, str):
            report.write_text(data)
        else:
            report.write_text(json.dumps(data))

    return subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            str(report),
            str(scanner_exit),
        ],
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize(
    "scenario,expected_pass",
    [
        ("clean", True),
        ("medium", True),
        ("high", False),
        ("critical", False),
        ("missing_os", False),
        ("empty_packages", False),
        ("malformed", False),
        ("missing_report", False),
        ("scanner_error", False),
        ("invalid_severity", False),
    ],
)
def test_trivy_policy(tmp_path, scenario, expected_pass):
    data = clean_report()
    scanner_exit = 0

    if scenario in ("medium", "high", "critical"):
        data["Results"][0]["Vulnerabilities"] = [
            {
                "VulnerabilityID": "TEST-ONLY-001",
                "Severity": scenario.upper(),
            }
        ]

    elif scenario == "missing_os":
        data["Results"] = data["Results"][1:]

    elif scenario == "empty_packages":
        data["Results"][0]["Packages"] = []

    elif scenario == "malformed":
        data = "{invalid-json"

    elif scenario == "missing_report":
        data = None

    elif scenario == "scanner_error":
        scanner_exit = 2

    elif scenario == "invalid_severity":
        data["Results"][0]["Vulnerabilities"] = [
            {
                "VulnerabilityID": "TEST-ONLY-002",
                "Severity": "UNRECOGNIZED",
            }
        ]

    result = run_validator(
        tmp_path,
        data,
        scanner_exit,
    )

    actual_pass = result.returncode == 0

    assert actual_pass == expected_pass, (
        f"{scenario}: unexpected result\n"
        f"{result.stdout}\n{result.stderr}"
    )
