#!/usr/bin/env python3
"""Validate the release manifest against the recorded approved image."""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMPOSE = ROOT / "deploy/compose.release.yaml"
APPROVED_FILE = ROOT / "deploy/approved-image.txt"


def require(condition, message):
    if not condition:
        raise SystemExit(f"BLOCK [release]: {message}")


def main():
    require(len(sys.argv) <= 2, "Expected at most one manifest path")

    manifest = Path(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_COMPOSE
    require(manifest.is_file(), "Release manifest missing")
    require(APPROVED_FILE.is_file(), "Approved image record missing")

    approved = APPROVED_FILE.read_text().strip()

    require(
        re.fullmatch(
            r"ghcr\.io/szin7/secure-delivery-pipeline@sha256:[0-9a-f]{64}",
            approved,
        ) is not None,
        "Invalid approved image reference",
    )

    result = subprocess.run(
        ["docker", "compose", "-f", str(manifest), "config", "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )

    require(result.returncode == 0, "Invalid Compose configuration")

    try:
        config = json.loads(result.stdout)
        services = config["services"]
    except (ValueError, KeyError, TypeError):
        raise SystemExit("BLOCK [release]: Invalid Compose output")

    require(set(services) == {"api"}, "Unexpected services")

    api = services["api"]

    require("build" not in api, "Release must not rebuild source")
    require(api.get("image") == approved, "Image is not the approved digest")
    require(api.get("read_only") is True, "Read-only filesystem required")
    require(api.get("privileged", False) is False, "Privileged mode forbidden")
    require(not api.get("cap_add"), "Additional capabilities forbidden")
    require("ALL" in api.get("cap_drop", []), "Capabilities must be dropped")
    require(
        "no-new-privileges:true" in api.get("security_opt", []),
        "No-new-privileges required",
    )
    require(api.get("pids_limit") == 128, "Process limit mismatch")
    require(api.get("init") is True, "Init process required")
    require(not api.get("volumes"), "Unexpected volume mounts")
    require(not api.get("devices"), "Unexpected device access")

    ports = api.get("ports", [])
    require(
        len(ports) == 1
        and ports[0].get("host_ip") == "127.0.0.1"
        and ports[0].get("target") == 8000,
        "Expected localhost-only port mapping",
    )

    print("PASS [release]: Approved image and runtime policy verified")


if __name__ == "__main__":
    main()
