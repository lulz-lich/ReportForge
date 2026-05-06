"""Pydantic schemas for pentest reports."""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Severity(str, Enum):
    """Supported severity ratings."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Language(str, Enum):
    """Supported report languages."""

    EN = "en"
    PT = "pt"


class Classification(str, Enum):
    """Report handling classification."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class FindingStatus(str, Enum):
    """Lifecycle status for a finding."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    REMEDIATED = "remediated"
    RISK_ACCEPTED = "risk_accepted"


class Effort(str, Enum):
    """High-level remediation effort."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Evidence(BaseModel):
    """Evidence item for a finding."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    artifact: str | None = Field(
        default=None,
        description="Safe artifact reference, redacted snippet, screenshot path, or ticket link.",
    )


class TimelineEvent(BaseModel):
    """Timeline event included in the report."""

    model_config = ConfigDict(extra="forbid")

    date: date
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)


class Finding(BaseModel):
    """Technical finding schema."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, examples=["RF-001"])
    title: str = Field(min_length=1)
    severity: Severity
    likelihood: Severity = Severity.MEDIUM
    status: FindingStatus = FindingStatus.OPEN
    remediation_effort: Effort = Effort.MEDIUM
    affected_asset: str = Field(min_length=1)
    description: str = Field(min_length=1)
    impact: str = Field(min_length=1)
    evidence: list[Evidence] = Field(default_factory=list)
    recommendation: str = Field(min_length=1)
    references: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    @field_validator("references")
    @classmethod
    def remove_blank_references(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: list[str]) -> list[str]:
        return sorted({item.strip().lower() for item in value if item.strip()})


class Report(BaseModel):
    """Complete report project schema."""

    model_config = ConfigDict(extra="forbid")

    report_id: str = Field(min_length=1)
    report_version: str = Field(default="1.0", min_length=1)
    title: str = Field(min_length=1)
    client: str = Field(min_length=1)
    language: Language = Language.EN
    classification: Classification = Classification.CONFIDENTIAL
    assessment_type: str = Field(default="Authorized Penetration Test", min_length=1)
    assessment_start: date
    assessment_end: date
    prepared_by: str = Field(min_length=1)
    executive_summary: str = Field(min_length=1)
    methodology: str = Field(
        default=(
            "The assessment used authorized, non-destructive validation and evidence-safe "
            "documentation practices."
        ),
        min_length=1,
    )
    limitations: str = Field(
        default="Testing was limited to the approved scope and rules of engagement.",
        min_length=1,
    )
    conclusion: str = Field(
        default=(
            "Remediation should prioritize high-severity findings, exposed business risk, "
            "and controls that improve detection and response."
        ),
        min_length=1,
    )
    scope: list[str] = Field(default_factory=list)
    rules_of_engagement: list[str] = Field(default_factory=list)
    timeline: list[TimelineEvent] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)

    @field_validator("scope", "rules_of_engagement")
    @classmethod
    def remove_blank_items(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]

    @field_validator("assessment_end")
    @classmethod
    def end_date_must_not_precede_start(cls, value: date, info) -> date:
        start = info.data.get("assessment_start")
        if start and value < start:
            raise ValueError("assessment_end must be on or after assessment_start")
        return value

    @model_validator(mode="after")
    def validate_report_consistency(self) -> Report:
        finding_ids = [finding.id for finding in self.findings]
        duplicate_ids = sorted({finding_id for finding_id in finding_ids if finding_ids.count(finding_id) > 1})
        if duplicate_ids:
            raise ValueError(f"Duplicate finding ids are not allowed: {', '.join(duplicate_ids)}")

        for event in self.timeline:
            if event.date < self.assessment_start or event.date > self.assessment_end:
                raise ValueError(
                    f"Timeline event '{event.title}' must be within the assessment window."
                )
        return self
