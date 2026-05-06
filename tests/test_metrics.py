from pathlib import Path

from reportforge.core.io import read_report
from reportforge.core.metrics import report_metrics


def test_report_metrics_for_example() -> None:
    report = read_report(Path("examples/acme_authorized_pentest.yaml"))

    metrics = report_metrics(report)

    assert metrics.total_findings == 2
    assert metrics.highest_severity == "high"
    assert metrics.critical_or_high_open == 1
    assert metrics.top_priority_score > 0
