import json
import subprocess
import sys
from pathlib import Path

import pytest


VALIDATOR = (
    Path(__file__).resolve().parents[1]
    / "scripts/validate_trivy_config.py"
)


def clean_report():
    return {
        "Results": [
            {
                "Target": "/workspace/Dockerfile",
                "Type": "dockerfile",
                "Misconfigurations": [],
            }
        ]
    }


def run_validator(tmp_path, data, scanner_exit=0):
    report = tmp_path / "config.json"

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
        ("low", True),
        ("medium", True),
        ("high", False),
        ("critical", False),
        ("missing_report", False),
        ("malformed_json", False),
        ("scanner_failure", False),
        ("missing_results", False),
        ("missing_dockerfile", False),
        ("wrong_target", False),
        ("duplicate_targets", False),
        ("invalid_severity", False),
        ("missing_rule", False),
        ("scanner_errors", False),
        ("malformed_findings", False),
    ],
)
def test_configuration_policy(
    tmp_path, scenario, expected_pass
):
    data = clean_report()
    scanner_exit = 0

    if scenario in ("low", "medium", "high", "critical"):
        data["Results"][0]["Misconfigurations"] = [
            {
                "ID": "TEST-CONFIG-001",
                "Severity": scenario.upper(),
            }
        ]

    elif scenario == "missing_report":
        data = None

    elif scenario == "malformed_json":
        data = "{invalid-json"

    elif scenario == "scanner_failure":
        scanner_exit = 2

    elif scenario == "missing_results":
        data["Results"] = []

    elif scenario == "missing_dockerfile":
        data["Results"][0]["Type"] = "yaml"

    elif scenario == "wrong_target":
        data["Results"][0]["Target"] = "unrelated.yml"

    elif scenario == "duplicate_targets":
        data["Results"].append(data["Results"][0].copy())

    elif scenario == "invalid_severity":
        data["Results"][0]["Misconfigurations"] = [
            {
                "ID": "TEST-CONFIG-002",
                "Severity": "INVALID",
            }
        ]

    elif scenario == "missing_rule":
        data["Results"][0]["Misconfigurations"] = [
            {"Severity": "HIGH"}
        ]

    elif scenario == "scanner_errors":
        data["Errors"] = ["Synthetic scanner error"]

    elif scenario == "malformed_findings":
        data["Results"][0]["Misconfigurations"] = {}

    result = run_validator(
        tmp_path,
        data,
        scanner_exit,
    )

    actual_pass = result.returncode == 0

    assert actual_pass == expected_pass, (
        f"Scenario: {scenario}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )

    if scenario in ("high", "critical"):
        assert "BLOCK [Config]" in result.stdout
