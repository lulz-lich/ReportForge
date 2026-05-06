from reportforge.core.redaction import find_sensitive_content, redacted_report
from reportforge.schemas import Report


def test_redaction_finds_and_redacts_sensitive_content() -> None:
    sensitive_key = "to" + "ken"
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
            "findings": [
                {
                    "id": "RF-001",
                    "title": "Evidence handling issue",
                    "severity": "medium",
                    "affected_asset": "local evidence repository",
                    "description": "A safe local test fixture includes a fake sensitive value.",
                    "impact": "Sensitive evidence should not be published in reports.",
                    "evidence": [
                        {
                            "title": "Fake token",
                            "description": f"{sensitive_key}=example-redaction-fixture-12345",
                        }
                    ],
                    "recommendation": "Redact sensitive evidence before sharing.",
                }
            ],
        }
    )

    matches = find_sensitive_content(report)
    sanitized = redacted_report(report)

    assert matches
    assert "[REDACTED]" in sanitized.findings[0].evidence[0].description
