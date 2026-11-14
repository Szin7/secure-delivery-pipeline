import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "deploy/compose.release.yaml"
VALIDATOR = ROOT / "scripts/check_release_policy.py"


def validate(manifest):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(manifest)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_approved_release_passes():
    result = validate(MANIFEST)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "original,replacement,reason",
    [
        (
            "    init: true\n",
            '    init: true\n    user: "0"\n',
            "Release override forbidden: user",
        ),
        (
            "    init: true\n",
            '    init: true\n    command: ["sh"]\n',
            "Release override forbidden: command",
        ),
        (
            "      - no-new-privileges:true\n",
            "      - no-new-privileges:true\n"
            "      - seccomp:unconfined\n",
            "Unexpected security options",
        ),
    ],
)
def test_unsafe_override_rejected(
    tmp_path, original, replacement, reason
):
    content = MANIFEST.read_text()
    assert content.count(original) == 1

    fixture = tmp_path / "compose.yaml"
    fixture.write_text(content.replace(original, replacement))

    result = validate(fixture)

    assert result.returncode != 0
    assert f"BLOCK [release]: {reason}" in (
        result.stdout + result.stderr
    )
