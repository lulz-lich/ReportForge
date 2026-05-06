"""Severity ordering and summary helpers."""

from __future__ import annotations

from collections import Counter

from reportforge.schemas import Finding, FindingStatus, Report, Severity

SEVERITY_ORDER = {
    Severity.INFO: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}


SEVERITY_LABELS = {
    "en": {
        Severity.INFO: "Informational",
        Severity.LOW: "Low",
        Severity.MEDIUM: "Medium",
        Severity.HIGH: "High",
        Severity.CRITICAL: "Critical",
    },
    "pt": {
        Severity.INFO: "Informativo",
        Severity.LOW: "Baixo",
        Severity.MEDIUM: "Medio",
        Severity.HIGH: "Alto",
        Severity.CRITICAL: "Critico",
    },
}

STATUS_LABELS = {
    "en": {
        FindingStatus.OPEN: "Open",
        FindingStatus.IN_PROGRESS: "In Progress",
        FindingStatus.REMEDIATED: "Remediated",
        FindingStatus.RISK_ACCEPTED: "Risk Accepted",
    },
    "pt": {
        FindingStatus.OPEN: "Aberto",
        FindingStatus.IN_PROGRESS: "Em Andamento",
        FindingStatus.REMEDIATED: "Remediado",
        FindingStatus.RISK_ACCEPTED: "Risco Aceito",
    },
}


def sorted_findings(findings: list[Finding]) -> list[Finding]:
    """Sort findings from highest to lowest severity."""

    return sorted(findings, key=lambda finding: (risk_score(finding), finding.id), reverse=True)


def risk_score(finding: Finding) -> int:
    """Return an explainable prioritization score from severity and likelihood."""

    severity_score = SEVERITY_ORDER[finding.severity] * 20
    likelihood_score = SEVERITY_ORDER[finding.likelihood] * 5
    evidence_bonus = min(len(finding.evidence), 3)
    return severity_score + likelihood_score + evidence_bonus


def severity_counts(report: Report) -> dict[Severity, int]:
    """Return count by severity with all severities present."""

    counts = Counter(finding.severity for finding in report.findings)
    return {severity: counts.get(severity, 0) for severity in Severity}


def severity_label(severity: Severity, language: str) -> str:
    """Return a localized severity label."""

    return SEVERITY_LABELS.get(language, SEVERITY_LABELS["en"])[severity]


def status_counts(report: Report) -> dict[FindingStatus, int]:
    """Return count by finding lifecycle status."""

    counts = Counter(finding.status for finding in report.findings)
    return {status: counts.get(status, 0) for status in FindingStatus}


def status_label(status: FindingStatus, language: str) -> str:
    """Return a localized status label."""

    return STATUS_LABELS.get(language, STATUS_LABELS["en"])[status]
