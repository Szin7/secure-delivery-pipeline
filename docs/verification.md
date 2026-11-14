# Security Verification

The project uses automated checks to catch security issues before an application image is approved for release.

## Run the Checks

Build the image:

    docker build --platform linux/amd64 -t secure-delivery-pipeline:local .

Run the tests and scanners:

    uv run --locked python -m pytest -q
    ./scripts/check_secrets.sh
    ./scripts/check_sast.sh
    ./scripts/check_image_vulns.sh
    ./scripts/check_config.sh
    ./scripts/generate_sbom.sh

## Verified Results

14 November 2026

| Check | Result |
| --- | --- |
| Automated tests | 56 passed |
| Gitleaks | No detected secrets |
| Semgrep | No findings across 14 scanned Python files |
| Trivy image scan | 0 reported vulnerabilities |
| Dockerfile security scan | 0 findings |
| CycloneDX SBOM | 45 components |

The test suite includes security-policy and release-policy regression tests. Controlled negative tests confirm that blocking findings, invalid reports, and scanner failures are rejected.

## Notes

Semgrep uses a project-specific rule, and vulnerability results depend on the scanner database. Generated scan reports remain local under the Git-ignored reports directory. GitHub Actions evidence is available through the linked workflow runs.

## CI Evidence

- [Approved publication run](https://github.com/Szin7/secure-delivery-pipeline/actions/runs/43583807171)
- [Rejected unsafe Python code](https://github.com/Szin7/secure-delivery-pipeline/pull/1)
- [Rejected unsafe release configuration](https://github.com/Szin7/secure-delivery-pipeline/pull/2)

Workflow artifacts have limited retention.
