"""Project file input/output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from reportforge.schemas import Report

REPORT_FILE_NAME = "report.yaml"


def read_report(path: Path) -> Report:
    """Read a report from a YAML, YML, or JSON file."""

    if not path.exists():
        raise FileNotFoundError(f"Report file not found: {path}")

    raw = path.read_text(encoding="utf-8")
    data = _parse(path, raw)
    if not isinstance(data, dict):
        raise ValueError("Report data must be a mapping/object.")
    return Report.model_validate(data)


def write_report(path: Path, report: Report) -> None:
    """Write a report as YAML."""

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = report.model_dump(mode="json")
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def project_report_path(project_dir: Path) -> Path:
    """Return the conventional report data path for a project directory."""

    return project_dir / REPORT_FILE_NAME


def _parse(path: Path, raw: str) -> Any:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return json.loads(raw)
    if suffix in {".yaml", ".yml"}:
        return yaml.safe_load(raw)
    raise ValueError("Unsupported report format. Use .json, .yaml, or .yml.")
