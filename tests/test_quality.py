from reportforge.core.quality import check_report_quality
from reportforge.schemas import Report


def test_quality_checks_warn_on_incomplete_report() -> None:
    report = Report.model_validate(
        {
            "report_id": "demo",
            "title": "Authorized Pentest Report",
            "client": "Example Corp",
            "language": "en",
            "assessment_start": "2026-04-20",
            "assessment_end": "2026-04-21",
            "prepared_by": "Security Team",
            "executive_summary": "Authorized assessment summary.",
            "findings": [],
        }
    )

    issues = check_report_quality(report)

    assert {issue.code for issue in issues} >= {"scope.empty", "findings.empty"}
