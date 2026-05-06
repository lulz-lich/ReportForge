"""Local installation and project health checks."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

from reportforge.core.io import read_report
from reportforge.exporters import export_html, export_json, export_markdown, export_pdf


@dataclass(frozen=True)
class DoctorCheck:
    """Result of a local health check."""

    name: str
    ok: bool
    detail: str


def run_doctor(project_root: Path) -> list[DoctorCheck]:
    """Run local checks that help users verify their ReportForge checkout."""

    checks: list[DoctorCheck] = []
    checks.extend(_template_checks())
    example = project_root / "examples" / "acme_authorized_pentest.yaml"
    try:
        report = read_report(example)
        checks.append(DoctorCheck("example.load", True, str(example)))
    except Exception as exc:  # noqa: BLE001 - doctor should report clean failures.
        checks.append(DoctorCheck("example.load", False, str(exc)))
        return checks

    exporter_checks = [
        ("export.markdown", lambda: export_markdown(report).startswith("# ")),
        ("export.html", lambda: export_html(report).startswith("<!doctype html>")),
        ("export.json", lambda: '"summary"' in export_json(report)),
        ("export.pdf", lambda: export_pdf(report).startswith(b"%PDF")),
    ]
    for name, check in exporter_checks:
        try:
            checks.append(DoctorCheck(name, bool(check()), "ok"))
        except Exception as exc:  # noqa: BLE001
            checks.append(DoctorCheck(name, False, str(exc)))
    return checks


def _template_checks() -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []
    template_root = files("reportforge.templates")
    for template_name in ["report_en.md.j2", "report_pt.md.j2"]:
        exists = template_root.joinpath(template_name).is_file()
        checks.append(DoctorCheck(f"template.{template_name}", exists, "found" if exists else "missing"))
    return checks
