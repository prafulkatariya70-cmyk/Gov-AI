from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


RuleOperator = Literal["AND", "OR"]


@dataclass
class EligibilityRule:
    """One atomic eligibility requirement."""

    rule_type: str
    value: object | None = None
    confidence: str = "low"
    evidence: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class EligibilityRuleGroup:
    """A logical group containing atomic rules and/or nested groups."""

    operator: RuleOperator
    rules: list[EligibilityRule | EligibilityRuleGroup] = field(
        default_factory=list
    )


@dataclass
class NormalizedEligibility:
    """Complete machine-readable eligibility tree."""

    age_rules: list[EligibilityRule] = field(default_factory=list)
    service_rules: list[EligibilityRule | EligibilityRuleGroup] = field(
        default_factory=list
    )
    qualification_rules: list[EligibilityRule | EligibilityRuleGroup] = field(
        default_factory=list
    )
    experience_rules: list[EligibilityRule | EligibilityRuleGroup] = field(
        default_factory=list
    )
    department_rules: list[EligibilityRule] = field(default_factory=list)
    special_rules: list[EligibilityRule] = field(default_factory=list)
    pay_rules: list[EligibilityRule] = field(default_factory=list)
