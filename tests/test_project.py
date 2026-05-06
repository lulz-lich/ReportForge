from pathlib import Path

from reportforge.core.io import project_report_path, read_report
from reportforge.core.project import add_finding, create_project
from reportforge.schemas import Effort, FindingStatus, Language, Severity


def test_create_project_writes_report_yaml(tmp_path: Path) -> None:
    project_dir = tmp_path / "client-report"

    report_path = create_project(
        project_dir,
        title="Authorized Pentest Report",
        client="Example Corp",
        language=Language.EN,
        prepared_by="Security Team",
    )

    assert report_path == project_report_path(project_dir)
    report = read_report(report_path)
    assert report.client == "Example Corp"


def test_add_finding_appends_valid_finding(tmp_path: Path) -> None:
    project_dir = tmp_path / "client-report"
    report_path = create_project(
        project_dir,
        title="Authorized Pentest Report",
        client="Example Corp",
        language=Language.EN,
        prepared_by="Security Team",
    )

    finding = add_finding(
        report_path,
        title="Security headers are missing",
        severity=Severity.LOW,
        likelihood=Severity.MEDIUM,
        status=FindingStatus.OPEN,
        remediation_effort=Effort.LOW,
        affected_asset="https://app.example.test",
        description="Passive review identified missing headers.",
        impact="Defense in depth is reduced.",
        evidence_description="Redacted header summary.",
        recommendation="Apply a security header baseline.",
        references=["OWASP Secure Headers Project"],
        tags=["web", "hardening"],
    )

    report = read_report(report_path)
    assert finding.id == "RF-001"
    assert report.findings[0].title == "Security headers are missing"
    assert report.findings[0].tags == ["hardening", "web"]
