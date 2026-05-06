from pathlib import Path

from typer.testing import CliRunner

from reportforge.cli.app import app

runner = CliRunner()


def test_cli_validate_example() -> None:
    result = runner.invoke(app, ["validate", "examples/acme_authorized_pentest.yaml"])

    assert result.exit_code == 0
    assert "Acme Health Demo" in result.output


def test_cli_export_markdown(tmp_path: Path) -> None:
    output = tmp_path / "report.md"

    result = runner.invoke(
        app,
        [
            "export",
            "examples/acme_authorized_pentest.yaml",
            "--format",
            "markdown",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert output.exists()
    assert output.read_text(encoding="utf-8").startswith("# Authorized Web Application")


def test_cli_new_and_add_finding(tmp_path: Path) -> None:
    project_dir = tmp_path / "client-report"

    new_result = runner.invoke(
        app,
        [
            "new",
            str(project_dir),
            "--client",
            "Example Corp",
            "--title",
            "Authorized Pentest Report",
        ],
    )
    add_result = runner.invoke(
        app,
        [
            "add-finding",
            str(project_dir),
            "--title",
            "Missing header",
            "--severity",
            "low",
            "--likelihood",
            "medium",
            "--effort",
            "low",
            "--tag",
            "web",
            "--asset",
            "https://app.example.test",
            "--description",
            "A passive review identified a missing header.",
            "--impact",
            "Defense in depth is reduced.",
            "--evidence",
            "Redacted response metadata.",
            "--recommendation",
            "Apply a header baseline.",
        ],
    )

    assert new_result.exit_code == 0
    assert add_result.exit_code == 0
    assert (project_dir / "report.yaml").exists()


def test_cli_list_findings() -> None:
    result = runner.invoke(app, ["list-findings", "examples/acme_authorized_pentest.yaml"])

    assert result.exit_code == 0
    assert "RF-002" in result.output


def test_cli_metrics_json() -> None:
    result = runner.invoke(app, ["metrics", "examples/acme_authorized_pentest.yaml", "--json"])

    assert result.exit_code == 0
    assert '"total_findings": 2' in result.output


def test_cli_doctor() -> None:
    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "export.pdf" in result.output


def test_cli_schema_writes_json_schema(tmp_path: Path) -> None:
    output = tmp_path / "schema.json"

    result = runner.invoke(app, ["schema", "--output", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    assert '"Report"' in output.read_text(encoding="utf-8")


def test_cli_export_pdf(tmp_path: Path) -> None:
    output = tmp_path / "report.pdf"

    result = runner.invoke(
        app,
        [
            "export",
            "examples/acme_authorized_pentest.yaml",
            "--format",
            "pdf",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert output.read_bytes().startswith(b"%PDF")


def test_cli_export_json(tmp_path: Path) -> None:
    output = tmp_path / "report.json"

    result = runner.invoke(
        app,
        [
            "export",
            "examples/acme_authorized_pentest.yaml",
            "--format",
            "json",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert '"summary"' in output.read_text(encoding="utf-8")


def test_cli_redact_writes_sanitized_yaml(tmp_path: Path) -> None:
    source = tmp_path / "report.yaml"
    output = tmp_path / "redacted.yaml"
    sensitive_key = "pass" + "word"
    source.write_text(
        f"""
report_id: demo
title: Authorized Pentest Report
client: Example Corp
language: en
assessment_start: 2026-04-20
assessment_end: 2026-04-21
prepared_by: Security Team
executive_summary: Authorized assessment summary.
findings:
  - id: RF-001
    title: Evidence handling issue
    severity: medium
    affected_asset: local evidence repository
    description: A safe local test fixture includes a fake sensitive value.
    impact: Sensitive evidence should not be published in reports.
    evidence:
      - title: Fake token
        description: "{sensitive_key}=example-redaction-fixture-12345"
    recommendation: Redact sensitive evidence before sharing.
""",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["redact", str(source), "--output", str(output)])

    assert result.exit_code == 0
    assert "[REDACTED]" in output.read_text(encoding="utf-8")
