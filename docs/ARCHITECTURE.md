# Architecture

ReportForge is intentionally split into small, testable modules.

## Layers

- `schemas/`: Pydantic models and validation rules for report data.
- `core/`: business logic for IO, project creation, scoring, metrics, quality checks, redaction, and health checks.
- `templates/`: bilingual Jinja2 Markdown templates.
- `exporters/`: Markdown, HTML, PDF, and normalized JSON exporters.
- `cli/`: Typer command interface and Rich terminal presentation.

## Data Flow

```text
YAML/JSON report data
        |
        v
Pydantic schema validation
        |
        v
core scoring / metrics / quality / redaction
        |
        v
Jinja2 templates and exporters
        |
        v
Markdown / HTML / PDF / JSON artifacts
```

## Safety Boundary

ReportForge never interacts with assessment targets. All operations are local transformations of structured report data. The project is safe to compose with other tools because it accepts findings as input instead of collecting them from live systems.

## Extension Points

- Add a new exporter under `reportforge/exporters`.
- Add a new language template under `reportforge/templates`.
- Add quality rules in `reportforge/core/quality.py`.
- Add computed metrics in `reportforge/core/metrics.py`.
- Extend report data through `reportforge/schemas/report.py`.
