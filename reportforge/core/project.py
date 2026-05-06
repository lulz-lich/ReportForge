"""Report project lifecycle operations."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from reportforge.core.io import project_report_path, read_report, write_report
from reportforge.schemas import (
    Effort,
    Evidence,
    Finding,
    FindingStatus,
    Language,
    Report,
    Severity,
    TimelineEvent,
)


def create_project(
    project_dir: Path,
    *,
    title: str,
    client: str,
    language: Language,
    prepared_by: str,
) -> Path:
    """Create a new report project with starter metadata."""

    project_dir.mkdir(parents=True, exist_ok=True)
    report_path = project_report_path(project_dir)
    if report_path.exists():
        raise FileExistsError(f"Report project already exists: {report_path}")

    today = date.today()
    report = Report(
        report_id=project_dir.name,
        title=title,
        client=client,
        language=language,
        assessment_start=today,
        assessment_end=today,
        prepared_by=prepared_by,
        executive_summary=(
            "This report documents an authorized security assessment. "
            "Update this summary with business context, key risks, and remediation priorities."
        ),
        scope=["Add approved assets here"],
        rules_of_engagement=[
            "Testing is limited to explicitly authorized systems.",
            "No destructive testing, credential theft, persistence, or unauthorized scanning is permitted.",
        ],
        timeline=[
            TimelineEvent(
                date=today,
                title="Project created",
                description="Report project initialized for authorized assessment documentation.",
            )
        ],
    )
    write_report(report_path, report)
    return report_path


def add_finding(
    report_path: Path,
    *,
    title: str,
    severity: Severity,
    likelihood: Severity,
    status: FindingStatus,
    remediation_effort: Effort,
    affected_asset: str,
    description: str,
    impact: str,
    evidence_description: str,
    recommendation: str,
    references: list[str],
    tags: list[str],
) -> Finding:
    """Add a finding to an existing report project."""

    report = read_report(report_path)
    finding_id = f"RF-{len(report.findings) + 1:03d}"
    finding = Finding(
        id=finding_id,
        title=title,
        severity=severity,
        likelihood=likelihood,
        status=status,
        remediation_effort=remediation_effort,
        affected_asset=affected_asset,
        description=description,
        impact=impact,
        evidence=[
            Evidence(
                title="Evidence summary",
                description=evidence_description,
                artifact=None,
            )
        ],
        recommendation=recommendation,
        references=references,
        tags=tags,
    )
    report.findings.append(finding)
    write_report(report_path, report)
    return finding
