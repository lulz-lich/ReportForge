"""Typer command-line interface for ReportForge."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from reportforge import __version__
from reportforge.core.doctor import run_doctor
from reportforge.core.io import project_report_path, read_report, write_report
from reportforge.core.metrics import report_metrics
from reportforge.core.project import add_finding as add_finding_to_project
from reportforge.core.project import create_project
from reportforge.core.quality import check_report_quality
from reportforge.core.redaction import find_sensitive_content, redacted_report
from reportforge.core.scoring import (
    risk_score,
    severity_counts,
    severity_label,
    sorted_findings,
    status_counts,
    status_label,
)
from reportforge.exporters import export_html, export_json, export_markdown, export_pdf
from reportforge.schemas import Effort, FindingStatus, Language, Report, Severity

app = typer.Typer(
    name="reportforge",
    help="Professional bilingual pentest reporting engine. Documentation only; no scanning or exploitation.",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)
console = Console()


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"reportforge {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the ReportForge version.",
    ),
) -> None:
    """ReportForge CLI entrypoint."""


@app.command("new")
def new_project(
    project_dir: Path = typer.Argument(..., help="Directory for the new report project."),
    title: str = typer.Option("Authorized Penetration Test Report", "--title", "-t"),
    client: str = typer.Option(..., "--client", "-c", help="Client or organization name."),
    language: Language = typer.Option(Language.EN, "--language", "-l", help="Report language: en or pt."),
    prepared_by: str = typer.Option("Security Team", "--prepared-by", "-p"),
) -> None:
    """Create a new report project with a starter report.yaml."""

    report_path = create_project(
        project_dir,
        title=title,
        client=client,
        language=language,
        prepared_by=prepared_by,
    )
    console.print(_banner("new project"))
    console.print(Panel(f"Created report project: [bold green]{report_path}[/bold green]", border_style="green"))


@app.command("add-finding")
def add_finding(
    project_dir: Path = typer.Argument(..., help="Report project directory."),
    title: str = typer.Option(..., "--title", "-t"),
    severity: Severity = typer.Option(..., "--severity", "-s"),
    likelihood: Severity = typer.Option(Severity.MEDIUM, "--likelihood", help="Likelihood rating."),
    status: FindingStatus = typer.Option(FindingStatus.OPEN, "--status", help="Finding lifecycle status."),
    remediation_effort: Effort = typer.Option(Effort.MEDIUM, "--effort", help="Estimated remediation effort."),
    affected_asset: str = typer.Option(..., "--asset", "-a"),
    description: str = typer.Option(..., "--description", "-d"),
    impact: str = typer.Option(..., "--impact", "-i"),
    evidence: str = typer.Option(..., "--evidence", "-e", help="Safe, redacted evidence summary."),
    recommendation: str = typer.Option(..., "--recommendation", "-r"),
    reference: list[str] = typer.Option(None, "--reference", help="Reference URL or standard. Repeatable."),
    tag: list[str] = typer.Option(None, "--tag", help="Finding tag. Repeatable."),
) -> None:
    """Add a technical finding to an existing report project."""

    report_path = project_report_path(project_dir)
    finding = add_finding_to_project(
        report_path,
        title=title,
        severity=severity,
        likelihood=likelihood,
        status=status,
        remediation_effort=remediation_effort,
        affected_asset=affected_asset,
        description=description,
        impact=impact,
        evidence_description=evidence,
        recommendation=recommendation,
        references=reference or [],
        tags=tag or [],
    )
    console.print(_banner("finding added"))
    console.print(Panel(f"Added finding [bold green]{finding.id}[/bold green]: {finding.title}", border_style="green"))


@app.command("validate")
def validate(
    report_file: Path = typer.Argument(..., help="Path to report.yaml, report.yml, or report.json."),
    strict: bool = typer.Option(False, "--strict", help="Fail when quality warnings are found."),
) -> None:
    """Validate a report schema and show a concise summary."""

    report = read_report(report_file)
    console.print(_banner("schema validated"))
    _print_summary(report)
    issues = check_report_quality(report)
    if issues:
        _print_quality_issues(issues)
        if strict:
            raise typer.Exit(2)
    else:
        console.print(Panel("No quality warnings found.", border_style="green"))


@app.command("export")
def export_report(
    report_file: Path = typer.Argument(..., help="Path to report.yaml, report.yml, or report.json."),
    output: Path = typer.Option(..., "--output", "-o", help="Output file path."),
    format: str = typer.Option("markdown", "--format", "-f", help="Export format: markdown, html, pdf, or json."),
) -> None:
    """Export a report to Markdown, HTML, PDF, or normalized JSON."""

    report = read_report(report_file)
    normalized_format = format.lower().strip()
    if normalized_format in {"markdown", "md"}:
        rendered = export_markdown(report)
    elif normalized_format == "html":
        rendered = export_html(report)
    elif normalized_format == "pdf":
        rendered = export_pdf(report)
    elif normalized_format == "json":
        rendered = export_json(report)
    else:
        raise typer.BadParameter("format must be markdown, md, html, pdf, or json")

    output.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(rendered, bytes):
        output.write_bytes(rendered)
    else:
        output.write_text(rendered, encoding="utf-8")
    console.print(_banner("export complete"))
    console.print(Panel(f"Exported [bold green]{normalized_format}[/bold green] report to {output}", border_style="green"))


@app.command("redact")
def redact(
    report_file: Path = typer.Argument(..., help="Path to report.yaml, report.yml, or report.json."),
    output: Path = typer.Option(..., "--output", "-o", help="Output YAML path for redacted report data."),
) -> None:
    """Write a redacted copy of report data for safer sharing."""

    report = read_report(report_file)
    matches = find_sensitive_content(report)
    sanitized = redacted_report(report)
    write_report(output, sanitized)
    console.print(_banner("redaction pass"))
    if matches:
        table = Table(title="Redacted Matches", border_style="yellow")
        table.add_column("Pattern", style="yellow")
        table.add_column("Location")
        for match in matches:
            table.add_row(match.pattern_name, match.location)
        console.print(table)
    else:
        console.print(Panel("No sensitive-looking values were detected.", border_style="green"))
    console.print(Panel(f"Redacted report written to {output}", border_style="green"))


@app.command("metrics")
def metrics(
    report_file: Path = typer.Argument(..., help="Path to report.yaml, report.yml, or report.json."),
    json_output: bool = typer.Option(False, "--json", help="Print metrics as JSON."),
) -> None:
    """Show executive metrics for a report."""

    report = read_report(report_file)
    computed = report_metrics(report)
    if json_output:
        console.print(json.dumps(computed.to_dict(), indent=2))
        return

    table = Table(title=f"Metrics - {report.title}", border_style="green")
    table.add_column("Metric", style="bold white")
    table.add_column("Value", style="green", justify="right")
    for key, value in computed.to_dict().items():
        table.add_row(key.replace("_", " ").title(), str(value))
    console.print(_banner("executive metrics"))
    console.print(table)


@app.command("doctor")
def doctor(
    project_root: Path = typer.Option(Path("."), "--project-root", help="Repository/project root to inspect."),
) -> None:
    """Check local ReportForge templates, example data, and exporters."""

    checks = run_doctor(project_root)
    table = Table(title="ReportForge Doctor", border_style="green")
    table.add_column("Check", style="bold")
    table.add_column("Status")
    table.add_column("Detail")
    for check in checks:
        table.add_row(check.name, "ok" if check.ok else "fail", check.detail)
    console.print(_banner("doctor"))
    console.print(table)
    if not all(check.ok for check in checks):
        raise typer.Exit(1)


@app.command("list-findings")
def list_findings(
    report_file: Path = typer.Argument(..., help="Path to report.yaml, report.yml, or report.json."),
) -> None:
    """List findings ordered by priority score."""

    report = read_report(report_file)
    table = Table(title=f"Findings - {report.title}", border_style="green")
    table.add_column("ID", style="bold green")
    table.add_column("Severity")
    table.add_column("Status")
    table.add_column("Score", justify="right")
    table.add_column("Title")
    for finding in sorted_findings(report.findings):
        table.add_row(
            finding.id,
            severity_label(finding.severity, report.language.value),
            status_label(finding.status, report.language.value),
            str(risk_score(finding)),
            finding.title,
        )
    console.print(_banner("finding index"))
    console.print(table)


@app.command("schema")
def schema(
    output: Path | None = typer.Option(None, "--output", "-o", help="Optional JSON schema output file."),
) -> None:
    """Print or write the ReportForge JSON schema."""

    schema_json = Report.model_json_schema()
    rendered = json.dumps(schema_json, indent=2)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        console.print(Panel(f"Schema written to {output}", border_style="green"))
    else:
        console.print(rendered)


def _print_summary(report) -> None:
    counts = severity_counts(report)
    table = Table(title=report.title, border_style="green")
    table.add_column("Metric", style="bold white")
    table.add_column("Value", style="green")
    table.add_row("Client", report.client)
    table.add_row("Language", report.language.value)
    table.add_row("Classification", report.classification.value)
    table.add_row("Findings", str(len(report.findings)))
    table.add_row(
        "Severities",
        "  ".join(
            f"{severity_label(severity, report.language.value)}:{counts[severity]}"
            for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
        ),
    )
    statuses = status_counts(report)
    table.add_row(
        "Status",
        "  ".join(
            f"{status_label(status, report.language.value)}:{statuses[status]}"
            for status in [
                FindingStatus.OPEN,
                FindingStatus.IN_PROGRESS,
                FindingStatus.REMEDIATED,
                FindingStatus.RISK_ACCEPTED,
            ]
        ),
    )
    console.print(table)


def _print_quality_issues(issues) -> None:
    table = Table(title="Quality Warnings", border_style="yellow")
    table.add_column("Level", style="yellow")
    table.add_column("Code", style="bold")
    table.add_column("Message")
    for issue in issues:
        table.add_row(issue.level, issue.code, issue.message)
    console.print(table)


def _banner(action: str) -> Panel:
    art = rf"""
 reportforge::{action}
 [scope] -> [findings] -> [evidence] -> [report]
       \         |             |           /
        '--------+-------------+----------'
"""
    return Panel(Text(art, style="green"), border_style="green", padding=(0, 1))
