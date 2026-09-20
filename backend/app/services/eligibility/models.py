from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


EligibilityStatus = Literal[
    "ELIGIBLE",
    "NOT_ELIGIBLE",
    "NEEDS_REVIEW",
]


RequirementStatus = Literal[
    "PASS",
    "FAIL",
    "UNKNOWN",
]


@dataclass
class CandidateProfile:
    """
    Candidate information used by the eligibility engine.

    None means the information is unknown.
    Unknown information must not automatically
    cause rejection.
    """

    age: int | None = None

    government_employee: bool | None = None

    analogous_post: bool | None = None

    regular_service_years: float | None = None

    current_pay_level: int | None = None

    parent_cadre: bool | None = None

    qualifying_examination: bool | None = None

    required_training: bool | None = None

    relevant_experience_years: float | None = None

    experience_areas: list[str] = field(
        default_factory=list
    )

    qualification_text: str | None = None


@dataclass
class RequirementResult:
    """
    Result of evaluating one eligibility requirement.
    """

    rule_type: str

    status: RequirementStatus

    required: object | None = None

    actual: object | None = None

    reason: str | None = None

    evidence: str | None = None

    confidence: str = "high"

    children: list[
        RequirementResult
    ] = field(
        default_factory=list
    )


@dataclass
class EligibilityResult:
    """
    Complete candidate eligibility result.
    """

    status: EligibilityStatus

    confidence: str

    requirements: list[
        RequirementResult
    ] = field(
        default_factory=list
    )

    passed: list[
        RequirementResult
    ] = field(
        default_factory=list
    )

    failed: list[
        RequirementResult
    ] = field(
        default_factory=list
    )

    unknown: list[
        RequirementResult
    ] = field(
        default_factory=list
    )

    reasons: list[str] = field(
        default_factory=list
    )