# Security policy

## Supported versions

This repository publishes generated open-data snapshots. Security issues are reviewed for the repository, exporter, website integration, and any accidentally exposed secrets or personal data.

| Version | Supported |
| --- | --- |
| `main` | Yes |
| Older tags and snapshots | No |

## Reporting a vulnerability

Please do **not** open a public Issue for a security vulnerability.

Use [GitHub private vulnerability reporting](https://github.com/AMPM-AIOPS-HQ/awesome-ai-tools-pricing/security/advisories/new) if it is enabled. Otherwise, contact the repository maintainers through the private contact method listed on the [AMPM-AIOPS-HQ organization page](https://github.com/AMPM-AIOPS-HQ).

Include:

- A clear description of the issue
- The affected file, workflow, endpoint, or commit
- Reproduction steps or a minimal proof of concept
- The potential impact
- Any suggested mitigation

Please redact credentials, tokens, personal data, and other sensitive information from reports.

## What to report

Examples include:

- Exposed API keys, passwords, tokens, or secrets
- A workflow that could be used to execute untrusted code with write access
- Malicious modification of generated data or release artifacts
- Personal or confidential information accidentally committed
- A vulnerability in repository automation or an unsafe external integration

Incorrect prices, missing sources, stale rows, and ordinary data-quality problems are not security vulnerabilities. Please report those through the [data correction issue template](https://github.com/AMPM-AIOPS-HQ/awesome-ai-tools-pricing/issues/new?template=data_correction.md).

## Response expectations

The maintainers will acknowledge valid private reports when reasonably possible, investigate the issue, and coordinate a fix or disclosure. Please avoid publicly disclosing the issue until a fix is available.
