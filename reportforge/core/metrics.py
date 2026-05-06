"""Executive metrics derived from report data."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from reportforge.core.scoring import risk_score, severity_counts, status_counts
from reportforge.schemas import FindingStatus, Report, Severity


@dataclass(frozen=True)
class ReportMetrics:
    """Computed metrics for summaries, exports, and dashboards."""

    total_findings: int
    open_findings: int
    remediated_findings: int
    accepted_risk_findings: int
    highest_severity: str
    average_priority_score: float
    top_priority_score: int
    critical_or_high_open: int
    remediation_progress_percent: float

    def to_dict(self) -> dict[str, int | float | str]:
        """Return JSON-serializable metrics."""

        return asdict(self)


def report_metrics(report: Report) -> ReportMetrics:
    """Compute executive metrics for a report."""

    severities = severity_counts(report)
    statuses = status_counts(report)
    scores = [risk_score(finding) for finding in report.findings]
    highest = _highest_present_severity(severities)
    open_high = sum(
        1
        for finding in report.findings
        if finding.status in {FindingStatus.OPEN, FindingStatus.IN_PROGRESS}
        and finding.severity in {Severity.HIGH, Severity.CRITICAL}
    )
    total = len(report.findings)
    remediated = statuses[FindingStatus.REMEDIATED]
    accepted = statuses[FindingStatus.RISK_ACCEPTED]
    progress = ((remediated + accepted) / total * 100) if total else 100.0
    return ReportMetrics(
        total_findings=total,
        open_findings=statuses[FindingStatus.OPEN] + statuses[FindingStatus.IN_PROGRESS],
        remediated_findings=remediated,
        accepted_risk_findings=accepted,
        highest_severity=highest.value,
        average_priority_score=round(sum(scores) / len(scores), 2) if scores else 0.0,
        top_priority_score=max(scores) if scores else 0,
        critical_or_high_open=open_high,
        remediation_progress_percent=round(progress, 2),
    )


def _highest_present_severity(counts: dict[Severity, int]) -> Severity:
    for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
        if counts[severity]:
            return severity
    return Severity.INFO
