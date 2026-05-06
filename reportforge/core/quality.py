"""Report quality checks for professional deliverables."""

from __future__ import annotations

from dataclasses import dataclass

from reportforge.core.redaction import find_sensitive_content
from reportforge.schemas import Report, Severity


@dataclass(frozen=True)
class QualityIssue:
    """A warning or error produced by report quality checks."""

    code: str
    message: str
    level: str = "warning"


def check_report_quality(report: Report) -> list[QualityIssue]:
    """Return actionable quality issues for a report."""

    issues: list[QualityIssue] = []
    if not report.scope:
        issues.append(QualityIssue("scope.empty", "Report scope is empty."))
    if not report.rules_of_engagement:
        issues.append(QualityIssue("roe.empty", "Rules of engagement are empty."))
    if not report.timeline:
        issues.append(QualityIssue("timeline.empty", "Timeline is empty."))
    if not report.findings:
        issues.append(QualityIssue("findings.empty", "Report has no findings."))

    for finding in report.findings:
        if finding.severity in {Severity.HIGH, Severity.CRITICAL} and not finding.evidence:
            issues.append(
                QualityIssue(
                    "finding.evidence.empty",
                    f"{finding.id} is high-impact but has no evidence summary.",
                )
            )
        if not finding.references:
            issues.append(
                QualityIssue(
                    "finding.references.empty",
                    f"{finding.id} has no references.",
                )
            )
        if len(finding.description) < 40:
            issues.append(
                QualityIssue(
                    "finding.description.short",
                    f"{finding.id} description is very short.",
                )
            )
    for match in find_sensitive_content(report):
        issues.append(
            QualityIssue(
                "sensitive.content",
                f"Potential sensitive content detected at {match.location} ({match.pattern_name}).",
            )
        )
    return issues
