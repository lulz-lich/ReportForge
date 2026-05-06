# Usage Guide

ReportForge works with a project directory that contains a `report.yaml` file, or with any standalone YAML, YML, or JSON report file that matches the schema.

## Create a Project

```bash
reportforge new client-report \
  --client "Example Corp" \
  --title "Authorized Penetration Test Report" \
  --language en \
  --prepared-by "Security Team"
```

## Add a Finding

```bash
reportforge add-finding client-report \
  --title "Verbose error responses disclose internal details" \
  --severity medium \
  --likelihood medium \
  --effort low \
  --status open \
  --asset "https://api.example.test/v1/profile" \
  --description "Synthetic requests returned implementation details in error responses." \
  --impact "The behavior can assist targeted reconnaissance." \
  --evidence "Redacted response excerpt stored in approved evidence repository." \
  --recommendation "Return generic client-facing errors and keep diagnostics server-side." \
  --reference "OWASP API Security Top 10" \
  --tag api
```

## Validate Quality

```bash
reportforge validate client-report/report.yaml --strict
```

Strict validation exits with code `2` when quality warnings are present. This is useful in CI pipelines.

## Review Metrics

```bash
reportforge metrics client-report/report.yaml
reportforge metrics client-report/report.yaml --json
```

The JSON form is useful for dashboards, CI summaries, and integration with other local reporting tools.

## Check The Local Project

```bash
reportforge doctor
```

The doctor command verifies bundled templates, example data, and exporters.

## Redact Before Sharing

```bash
reportforge redact client-report/report.yaml --output client-report/redacted-report.yaml
```

The redaction pass checks for common sensitive-value patterns in report content and writes a sanitized copy.

## Export

```bash
reportforge export client-report/report.yaml --format markdown --output reports/client-report.md
reportforge export client-report/report.yaml --format html --output reports/client-report.html
reportforge export client-report/report.yaml --format pdf --output reports/client-report.pdf
reportforge export client-report/report.yaml --format json --output reports/client-report.json
```
