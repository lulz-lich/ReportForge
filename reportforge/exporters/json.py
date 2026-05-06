"""JSON export support."""

from __future__ import annotations

import json

from reportforge.core.metrics import report_metrics
from reportforge.core.scoring import risk_score, severity_counts, status_counts
from reportforge.schemas import Report


def export_json(report: Report) -> str:
    """Render normalized report data with computed summary fields."""

    payload = report.model_dump(mode="json")
    payload["summary"] = {
        "severity_counts": {severity.value: count for severity, count in severity_counts(report).items()},
        "status_counts": {status.value: count for status, count in status_counts(report).items()},
        "finding_scores": {finding.id: risk_score(finding) for finding in report.findings},
        "metrics": report_metrics(report).to_dict(),
    }
    return json.dumps(payload, indent=2)
