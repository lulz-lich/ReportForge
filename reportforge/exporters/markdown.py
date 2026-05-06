"""Markdown export support."""

from __future__ import annotations

from importlib.resources import files

from jinja2 import Environment, PackageLoader, select_autoescape

from reportforge.core.metrics import report_metrics
from reportforge.core.scoring import (
    risk_score,
    severity_counts,
    severity_label,
    sorted_findings,
    status_counts,
    status_label,
)
from reportforge.schemas import FindingStatus, Report, Severity


def export_markdown(report: Report) -> str:
    """Render a report as Markdown using the selected language template."""

    env = Environment(
        loader=PackageLoader("reportforge", "templates"),
        autoescape=select_autoescape(enabled_extensions=("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template_name = f"report_{report.language.value}.md.j2"
    template = env.get_template(template_name)
    return template.render(
        report=report,
        findings=sorted_findings(report.findings),
        severity_counts=severity_counts(report),
        status_counts=status_counts(report),
        metrics=report_metrics(report),
        severity_label=severity_label,
        status_label=status_label,
        risk_score=risk_score,
        severities=[Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO],
        statuses=[
            FindingStatus.OPEN,
            FindingStatus.IN_PROGRESS,
            FindingStatus.REMEDIATED,
            FindingStatus.RISK_ACCEPTED,
        ],
    )


def template_path(language: str) -> str:
    """Return the package template path for diagnostics and tests."""

    return str(files("reportforge.templates").joinpath(f"report_{language}.md.j2"))
