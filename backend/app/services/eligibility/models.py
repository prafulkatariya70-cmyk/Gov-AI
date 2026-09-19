from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CandidateProfile:
    age: int | None = None
    government_employee: bool | None = None
    analogous_post: bool | None = None
    regular_service_years: int | float | None = None
    current_pay_level: int | float | None = None
    parent_cadre: bool | None = None
    qualifying_examination: bool | None = None
    required_training: bool | None = None
    relevant_experience_years: int | float | None = None
    experience_areas: list[str] = field(default_factory=list)
    qualification_text: str | None = None


@dataclass
class RequirementResult:
    rule_type: str
    status: str
    required: object | None = None
    actual: object | None = None
    reason: str | None = None
    evidence: str | None = None
    confidence: str | None = None
    children: list["RequirementResult"] = field(default_factory=list)


@dataclass
class EligibilityResult:
    status: str
    confidence: str
    requirements: list[RequirementResult] = field(default_factory=list)
    passed: list[RequirementResult] = field(default_factory=list)
    failed: list[RequirementResult] = field(default_factory=list)
    unknown: list[RequirementResult] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
