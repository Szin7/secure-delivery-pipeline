# Security Gate Policy

## Purpose

Security checks must produce a clear decision before
an application image is approved for release.

## Required Checks

### Application Tests

Unit and API tests must pass. A failed test blocks
the release.

### Secret Detection

Gitleaks checks the configured repository scope.

Any confirmed secret finding blocks the release.
Reports must not expose credential values.

### Static Analysis

Semgrep checks selected security-sensitive patterns.

Findings matching the project's blocking rules
must be resolved or explicitly reviewed under
the exception policy.

### Vulnerability and Configuration Scanning

Trivy checks application dependencies, container
packages, and relevant configuration.

Unexcepted HIGH and CRITICAL findings block
the release.

Lower-severity findings remain visible for review.

### Scanner Failures

A scanner crash, missing scan, unsupported option,
or malformed required report fails the gate.

Scanner failures must not be presented as
successful security checks.

## Exceptions

Every exception must record:

- Finding identifier
- Affected package or file
- Reason for the exception
- Compensating control, where applicable
- Responsible owner
- Expiration date

Expired exceptions are not valid.

Exceptions must be as narrow as possible.

## Release Approval

A release is eligible only when:

1. Application tests pass.
2. Required security gates pass.
3. The candidate image passes its smoke test.
4. The tested and scanned image is the one published.
5. Its expected release identity can be verified.

Publishing an image does not automatically approve
it for execution.

## Negative Tests

Controlled test fixtures must demonstrate that
each implemented security gate detects or rejects
the intended problem.

A scanner outage is not evidence of vulnerability
detection.

## Scope

This policy initially applies to the local application
and the GitHub Actions delivery pipeline.

It does not establish production readiness or
guarantee the absence of vulnerabilities.
