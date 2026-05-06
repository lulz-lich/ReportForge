# Security Policy

ReportForge is a reporting engine. It does not scan targets, exploit vulnerabilities, collect credentials, deploy payloads, or interact with external systems.

## Reporting Security Issues

If you find a vulnerability in ReportForge itself, open a private security advisory or contact the maintainer through the repository's preferred private channel.

Please do not include real client evidence, secrets, credentials, tokens, or sensitive report data in public issues.

## Supported Use

Use ReportForge with authorized assessment data and synthetic demo data. Before publishing examples, run:

```bash
reportforge validate path/to/report.yaml --strict
reportforge redact path/to/report.yaml --output path/to/redacted-report.yaml
```

The redaction helper is a safety aid, not a substitute for human review.
