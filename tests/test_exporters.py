from pathlib import Path

from reportforge.core.io import read_report
from reportforge.exporters import export_html, export_json, export_markdown, export_pdf


def test_markdown_export_renders_english_report() -> None:
    report = read_report(Path("examples/acme_authorized_pentest.yaml"))

    rendered = export_markdown(report)

    assert "# Authorized Web Application Penetration Test Report" in rendered
    assert "## Executive Summary" in rendered
    assert "RF-002 - Administrative workflow lacks explicit detection coverage" in rendered
    assert "| High | 1 |" in rendered
    assert "## Finding Status" in rendered
    assert "**Priority Score:**" in rendered


def test_markdown_export_renders_portuguese_report() -> None:
    report = read_report(Path("examples/acme_pt_report.yaml"))

    rendered = export_markdown(report)

    assert "## Resumo Executivo" in rendered
    assert "## Achados Tecnicos" in rendered
    assert "| Baixo | 1 |" in rendered


def test_html_export_contains_standalone_document() -> None:
    report = read_report(Path("examples/acme_authorized_pentest.yaml"))

    rendered = export_html(report)

    assert rendered.startswith("<!doctype html>")
    assert "<main>" in rendered
    assert "Authorized Web Application Penetration Test Report" in rendered


def test_pdf_export_returns_pdf_bytes() -> None:
    report = read_report(Path("examples/acme_authorized_pentest.yaml"))

    rendered = export_pdf(report)

    assert rendered.startswith(b"%PDF")
    assert len(rendered) > 1000


def test_json_export_contains_computed_summary() -> None:
    report = read_report(Path("examples/acme_authorized_pentest.yaml"))

    rendered = export_json(report)

    assert '"summary"' in rendered
    assert '"finding_scores"' in rendered
    assert '"RF-002"' in rendered
