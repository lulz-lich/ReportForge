import pytest
from pydantic import ValidationError

from reportforge.schemas import Report


def test_report_schema_accepts_valid_data() -> None:
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

    assert report.language.value == "en"


def test_report_schema_rejects_invalid_severity() -> None:
    with pytest.raises(ValidationError):
        Report.model_validate(
            {
                "report_id": "demo",
                "title": "Authorized Pentest Report",
                "client": "Example Corp",
                "language": "en",
                "assessment_start": "2026-04-20",
                "assessment_end": "2026-04-21",
                "prepared_by": "Security Team",
                "executive_summary": "Authorized assessment summary.",
                "findings": [
                    {
                        "id": "RF-001",
                        "title": "Invalid severity",
                        "severity": "urgent",
                        "affected_asset": "https://app.example.test",
                        "description": "Description",
                        "impact": "Impact",
                        "recommendation": "Recommendation",
                    }
                ],
            }
        )


def test_report_schema_rejects_duplicate_finding_ids() -> None:
    with pytest.raises(ValidationError):
        Report.model_validate(
            {
                "report_id": "demo",
                "title": "Authorized Pentest Report",
                "client": "Example Corp",
                "language": "en",
                "assessment_start": "2026-04-20",
                "assessment_end": "2026-04-21",
                "prepared_by": "Security Team",
                "executive_summary": "Authorized assessment summary.",
                "findings": [
                    {
                        "id": "RF-001",
                        "title": "First finding",
                        "severity": "low",
                        "affected_asset": "https://app.example.test",
                        "description": "Description with enough context for a valid finding.",
                        "impact": "Impact",
                        "recommendation": "Recommendation",
                    },
                    {
                        "id": "RF-001",
                        "title": "Second finding",
                        "severity": "medium",
                        "affected_asset": "https://api.example.test",
                        "description": "Description with enough context for a valid finding.",
                        "impact": "Impact",
                        "recommendation": "Recommendation",
                    },
                ],
            }
        )


def test_report_schema_rejects_timeline_outside_assessment_window() -> None:
    with pytest.raises(ValidationError):
        Report.model_validate(
            {
                "report_id": "demo",
                "title": "Authorized Pentest Report",
                "client": "Example Corp",
                "language": "en",
                "assessment_start": "2026-04-20",
                "assessment_end": "2026-04-21",
                "prepared_by": "Security Team",
                "executive_summary": "Authorized assessment summary.",
                "timeline": [
                    {
                        "date": "2026-04-25",
                        "title": "Late event",
                        "description": "This event is outside the assessment window.",
                    }
                ],
            }
        )
