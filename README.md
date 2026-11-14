# Secure Software Delivery Pipeline

A containerized FastAPI application with automated testing, security checks, and software component inventory through GitHub Actions.

The goal is to detect problems before an application image is considered for release.

## Pipeline

Pull requests run three required checks:

1. Tests, Gitleaks secret detection, and Semgrep static analysis.
2. Docker image smoke test, Trivy scans, and CycloneDX SBOM validation.
3. Release configuration policy validation.

On a push to protected `main`, all three checks must pass.
Publication then waits for manual approval in the
`release-publication` GitHub Environment.

After approval, GHCR receives the previously scanned image.
The image is not rebuilt during publication.

## Technology

Python, FastAPI, Docker, GitHub Actions, Gitleaks, Semgrep, Trivy, and CycloneDX.

## Run Locally

Build and start the application:

    docker compose up --build -d

Check application health:

    curl http://127.0.0.1:8765/health

Run the tests:

    uv run --locked python -m pytest -q

Run the security checks:

    ./scripts/check_secrets.sh
    ./scripts/check_sast.sh
    ./scripts/check_image_vulns.sh
    ./scripts/check_config.sh
    ./scripts/generate_sbom.sh

The commands require Docker, uv, and the configured Semgrep CLI.

## Verified Results

The approved GitHub Actions workflow passed on 14 November 2026.

| Check | Result |
| --- | --- |
| Automated tests | 56 passed |
| Gitleaks | No detected secrets |
| Semgrep | 14 Python files scanned, 0 findings |
| Trivy image scan | Passed |
| Dockerfile configuration scan | Passed |
| CycloneDX SBOM | 45 components |

[View successful CI run and security artifacts](https://github.com/Szin7/secure-delivery-pipeline/actions/runs/43583807171)

## Additional Details

- [Security verification](docs/verification.md)
- [Security gate policy](docs/gate-policy.md)
- [Threat model](docs/threat-model.md)

Security findings depend on the enabled rules and available advisory data. Image publication and deployment approval are separate stages of the project.

## Image Publication and Release

After security checks and manual release approval, the pipeline
publishes the previously scanned image to GitHub Container Registry. The
published image is identified by its SHA-256 digest.

The example release configuration in
`deploy/compose.release.yaml` uses a fixed image digest,
not a mutable tag or local rebuild.

Validate the release configuration:

    python3 scripts/check_release_policy.py

The release uses localhost-only networking, a read-only
filesystem, dropped capabilities, and a non-root user.

The release was verified locally with working `/health`
and `/version` endpoints. Deployment is currently manual.

[Successful four-job CI run](https://github.com/Szin7/secure-delivery-pipeline/actions/runs/43579799966)

[Rejected unsafe deployment PR](https://github.com/Szin7/secure-delivery-pipeline/pull/2)
