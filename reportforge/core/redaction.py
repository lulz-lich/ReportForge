"""Evidence redaction helpers for safe report handling."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from reportforge.schemas import Report


@dataclass(frozen=True)
class SensitiveMatch:
    """A possible sensitive value found in report content."""

    pattern_name: str
    location: str


SECRET_PATTERNS: dict[str, re.Pattern[str]] = {
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "bearer_token": re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{16,}\b", re.IGNORECASE),
    "private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "generic_secret_assignment": re.compile(
        r"\b(api[_-]?key|secret|token|password|passwd|pwd)\s*[:=]\s*['\"]?[^'\"\s]{8,}",
        re.IGNORECASE,
    ),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
}


def find_sensitive_content(report: Report) -> list[SensitiveMatch]:
    """Find possible sensitive values in evidence and report narrative."""

    payload = report.model_dump(mode="json")
    matches: list[SensitiveMatch] = []
    _walk(payload, "$", matches)
    return matches


def redacted_report(report: Report) -> Report:
    """Return a copy of a report with sensitive-looking values redacted."""

    payload = report.model_dump(mode="json")
    redacted = _redact_value(payload)
    return Report.model_validate(redacted)


def _walk(value: Any, location: str, matches: list[SensitiveMatch]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            _walk(item, f"{location}.{key}", matches)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _walk(item, f"{location}[{index}]", matches)
    elif isinstance(value, str):
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(value):
                matches.append(SensitiveMatch(name, location))


def _redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _redact_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    if isinstance(value, str):
        redacted = value
        for pattern in SECRET_PATTERNS.values():
            redacted = pattern.sub("[REDACTED]", redacted)
        return redacted
    return value
