# Template Guide

ReportForge uses Jinja2 templates stored in `reportforge/templates`.

- `report_en.md.j2` renders English reports.
- `report_pt.md.j2` renders Portuguese reports.

The Markdown template is the canonical narrative format. HTML and PDF exporters are generated from structured report data and Markdown-oriented content.

## Available Template Variables

- `report`: full Pydantic report object.
- `findings`: findings ordered by priority score.
- `severity_counts`: count map by severity.
- `status_counts`: count map by lifecycle status.
- `severity_label(severity, language)`: localized severity label.
- `status_label(status, language)`: localized status label.
- `risk_score(finding)`: explainable priority score.
- `severities`: ordered severities from critical to informational.
- `statuses`: supported finding statuses.

## Safety Notes

Templates should never encourage exploitation steps, payloads, credential handling, persistence, evasion, or unauthorized activity. Keep examples synthetic and remediation-focused.
