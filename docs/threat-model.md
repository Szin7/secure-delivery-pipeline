# Threat Model

## Purpose

This project demonstrates security checks between a source
change and a locally running container.

## Assets

- Application source code and dependencies
- GitHub Actions workflows and security policies
- Container images and release metadata
- Publishing credentials and GitHub permissions
- Existing local application containers

## Trust Boundaries

1. Pull request code is untrusted.
2. Release publishing is restricted to trusted workflows.
3. Registry images are not trusted solely because they exist.
4. Local execution requires verification of the expected
   release identity.

## Main Risks

- A credential is accidentally committed.
- Unsafe application code passes review.
- A vulnerable dependency enters the release.
- An insecure container configuration goes unnoticed.
- A scanner fails but the pipeline continues.
- An image is substituted or comes from an unexpected source.
- A failed deployment replaces a healthy local application.

## Planned Controls

- Gitleaks for secret detection
- Semgrep for selected code patterns
- Trivy for vulnerabilities and configuration checks
- Restricted GitHub Actions permissions
- Image digest and attestation verification
- Local deployment that rejects unverified candidates

## Limitations

Automated scanning cannot find every vulnerability.
Signed attestations provide origin evidence, not a
guarantee that software is secure.
