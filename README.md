# Secure Software Delivery Pipeline

A containerized FastAPI application with automated testing, security checks, and software component inventory through GitHub Actions.

The goal is to detect problems before an application image is considered for release.

## Pipeline

Code push or pull request
    |
    +-- Tests and source security
    |      - Pytest
    |      - Gitleaks
    |      - Semgrep
    |
    +-- Build and image security
           - Docker image build
           - Trivy vulnerability scan
           - Dockerfile configuration scan
           - CycloneDX SBOM
           - Security evidence artifacts

Both jobs must succeed for the workflow to pass.

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

The first GitHub Actions run completed successfully on 14 November 2026.

| Check | Result |
| --- | --- |
| Automated tests | 52 passed |
| Gitleaks | No detected secrets |
| Semgrep | 12 Python files scanned, 0 findings |
| Trivy image scan | Passed |
| Dockerfile configuration scan | Passed |
| CycloneDX SBOM | 45 components |

[View successful CI run and security artifacts](https://github.com/Szin7/secure-delivery-pipeline/actions/runs/43577530636)

## Additional Details

- [Security verification](docs/verification.md)
- [Security gate policy](docs/gate-policy.md)
- [Threat model](docs/threat-model.md)

Security findings depend on the enabled rules and available advisory data. Image publication and deployment approval are separate stages of the project.
