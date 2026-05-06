# ReportForge

[![CI](https://github.com/lulz-lich/ReportForge/actions/workflows/ci.yml/badge.svg)](https://github.com/lulz-lich/ReportForge/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-1.0.0-brightgreen)](https://github.com/lulz-lich/ReportForge/releases/tag/v1.0.0)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

ReportForge is a professional bilingual pentest reporting engine for creating executive summaries, technical findings, evidence sections, severity ratings, remediation guidance, timelines, and Markdown/HTML/PDF/JSON exports.

It is designed as a reusable portfolio-quality reporting tool for Red Team, ethical hacking, offensive security tooling, and authorized security assessment projects. ReportForge does not perform exploitation, scanning, credential collection, persistence, evasion, or destructive actions. It only validates structured report data and generates documentation.

```text
 reportforge::reporting-engine
 [scope] -> [findings] -> [evidence] -> [report]
       \         |             |           /
        '--------+-------------+----------'
```

## Features

- Typer-powered CLI.
- Create a new report project with `report.yaml`.
- Add findings from the command line.
- Pydantic schema validation for report data.
- English and Portuguese Markdown templates.
- Markdown, standalone HTML, and PDF exports.
- Normalized JSON export with computed summaries for downstream tools.
- Severity summaries and ordered technical findings.
- Finding lifecycle status, likelihood, remediation effort, tags, and priority scoring.
- Quality checks for missing scope, rules of engagement, timeline, evidence, and references.
- Local redaction helper for sensitive-looking evidence before sharing.
- JSON Schema generation for integrations.
- Executive metrics and local `doctor` health checks.
- GitHub Actions CI, Makefile, contribution guide, and security policy.
- Example English and Portuguese report datasets.
- Basic pytest coverage for schema validation, report generation, and CLI workflows.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Validate the example report:

```bash
reportforge validate examples/acme_authorized_pentest.yaml
```

Export Markdown:

```bash
reportforge export examples/acme_authorized_pentest.yaml --format markdown --output reports/acme-report.md
```

Export HTML:

```bash
reportforge export examples/acme_authorized_pentest.yaml --format html --output reports/acme-report.html
```

Export PDF:

```bash
reportforge export examples/acme_authorized_pentest.yaml --format pdf --output reports/acme-report.pdf
```

Export normalized JSON:

```bash
reportforge export examples/acme_authorized_pentest.yaml --format json --output reports/acme-report.json
```

List findings by priority:

```bash
reportforge list-findings examples/acme_authorized_pentest.yaml
```

Show executive metrics:

```bash
reportforge metrics examples/acme_authorized_pentest.yaml
reportforge metrics examples/acme_authorized_pentest.yaml --json
```

Check the local installation:

```bash
reportforge doctor
```

Run strict validation with quality gates:

```bash
reportforge validate examples/acme_authorized_pentest.yaml --strict
```

Create a redacted sharing copy:

```bash
reportforge redact examples/acme_authorized_pentest.yaml --output reports/acme-redacted.yaml
```

Write the JSON schema:

```bash
reportforge schema --output docs/reportforge.schema.json
```

Create a new report project:

```bash
reportforge new client-report --client "Example Corp" --title "Authorized Pentest Report" --language en --prepared-by "Security Team"
```

Add a finding:

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
  --tag api \
  --tag hardening
```

## Report Schema

ReportForge supports YAML, YML, and JSON. The canonical project file is `report.yaml`.

```yaml
report_id: example-authorized-pentest
report_version: "1.0"
title: Authorized Web Application Penetration Test Report
client: Example Corp
language: en
classification: confidential
assessment_type: Authorized Web Application Penetration Test
assessment_start: 2026-04-20
assessment_end: 2026-04-24
prepared_by: Security Team
executive_summary: >
  This report documents an authorized security assessment.
methodology: >
  The assessment used authorized, non-destructive validation and evidence-safe documentation.
limitations: >
  Testing was limited to approved assets and rules of engagement.
conclusion: >
  Remediation should prioritize high-severity findings and control improvements.
scope:
  - https://app.example.test
rules_of_engagement:
  - Testing was limited to approved assets.
timeline:
  - date: 2026-04-20
    title: Kickoff
    description: Confirmed scope and reporting expectations.
findings:
  - id: RF-001
    title: Security headers are missing
    severity: low
    likelihood: medium
    status: open
    remediation_effort: low
    affected_asset: https://app.example.test
    description: Passive response review identified missing browser security headers.
    impact: Browser-side defense in depth is reduced.
    evidence:
      - title: Header summary
        description: Content-Security-Policy was not present.
    recommendation: Apply a standard security header baseline.
    references:
      - OWASP Secure Headers Project
    tags:
      - web
      - hardening
```

Valid severities are `info`, `low`, `medium`, `high`, and `critical`. Valid languages are `en` and `pt`.

## Project Structure

```text
reportforge/
  reportforge/
    cli/          Typer commands
    core/         project lifecycle, IO, scoring, quality checks
    templates/    English and Portuguese Jinja2 templates
    exporters/    Markdown, HTML, and PDF exporters
    schemas/      Pydantic report schemas
  examples/       sample bilingual report data
  tests/          pytest coverage
  docs/           ethics, usage, architecture, template, and schema notes
  .github/        CI workflow
  README.md
  pyproject.toml
```

## Safety Scope

ReportForge is documentation-only. It is safe for portfolio use because it does not touch targets, run scans, exploit vulnerabilities, collect credentials, or automate offensive actions. See [docs/ETHICS_AND_SCOPE.md](docs/ETHICS_AND_SCOPE.md).

## Development

Run tests:

```bash
pytest
```

Common project tasks:

```bash
make test
make lint
make smoke
make examples
```

Run the CLI without installing:

```bash
python -m reportforge.cli validate examples/acme_authorized_pentest.yaml
```

## Portfolio Value

ReportForge demonstrates clean Python packaging, CLI design, Pydantic modeling, Jinja2 templating, bilingual report generation, severity normalization, evidence-aware documentation, and professional security tooling boundaries.
