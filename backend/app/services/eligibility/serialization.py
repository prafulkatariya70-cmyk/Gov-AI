from __future__ import annotations

from typing import Any

from app.services.documents.parsing.rules.models import (
    EligibilityRule,
    EligibilityRuleGroup,
    NormalizedEligibility,
)


def eligibility_rule_to_dict(
    rule: EligibilityRule,
) -> dict[str, Any]:
    """
    Convert one atomic EligibilityRule into a JSON-safe dictionary.
    """

    return {
        "rule_type": rule.rule_type,
        "value": rule.value,
        "confidence": rule.confidence,
        "evidence": rule.evidence,
        "metadata": rule.metadata,
    }


def eligibility_node_to_dict(
    node: EligibilityRule | EligibilityRuleGroup,
) -> dict[str, Any]:
    """
    Convert either an atomic rule or a logical rule group
    into a JSON-safe dictionary.
    """

    if isinstance(node, EligibilityRule):

        return eligibility_rule_to_dict(
            node,
        )

    if isinstance(node, EligibilityRuleGroup):

        return {
            "operator": node.operator,
            "rules": [
                eligibility_node_to_dict(child)
                for child in node.rules
            ],
        }

    raise TypeError(
        "Unsupported eligibility node type: "
        f"{type(node).__name__}"
    )


def normalized_eligibility_to_dict(
    normalized: NormalizedEligibility,
) -> dict[str, Any]:
    """
    Convert a complete NormalizedEligibility object
    into a JSON-safe dictionary suitable for SQLAlchemy JSON storage.
    """

    return {
        "age_rules": [
            eligibility_node_to_dict(rule)
            for rule in normalized.age_rules
        ],
        "service_rules": [
            eligibility_node_to_dict(rule)
            for rule in normalized.service_rules
        ],
        "qualification_rules": [
            eligibility_node_to_dict(rule)
            for rule in normalized.qualification_rules
        ],
        "experience_rules": [
            eligibility_node_to_dict(rule)
            for rule in normalized.experience_rules
        ],
        "department_rules": [
            eligibility_node_to_dict(rule)
            for rule in normalized.department_rules
        ],
        "special_rules": [
            eligibility_node_to_dict(rule)
            for rule in normalized.special_rules
        ],
        "pay_rules": [
            eligibility_node_to_dict(rule)
            for rule in normalized.pay_rules
        ],
    }


def eligibility_rule_from_dict(
    data: dict[str, Any],
) -> EligibilityRule:
    """
    Reconstruct one atomic EligibilityRule from JSON data.
    """

    return EligibilityRule(
        rule_type=str(
            data.get(
                "rule_type",
                "",
            )
        ),
        value=data.get(
            "value",
        ),
        confidence=str(
            data.get(
                "confidence",
                "low",
            )
        ),
        evidence=data.get(
            "evidence",
        ),
        metadata=dict(
            data.get(
                "metadata",
                {},
            )
        ),
    )


def eligibility_node_from_dict(
    data: dict[str, Any],
) -> EligibilityRule | EligibilityRuleGroup:
    """
    Reconstruct an EligibilityRule or EligibilityRuleGroup
    from JSON data.
    """

    if "operator" in data:

        operator = data.get(
            "operator",
        )

        if operator not in {
            "AND",
            "OR",
        }:
            raise ValueError(
                "Invalid eligibility group operator: "
                f"{operator}"
            )

        return EligibilityRuleGroup(
            operator=operator,
            rules=[
                eligibility_node_from_dict(child)
                for child in data.get(
                    "rules",
                    [],
                )
            ],
        )

    return eligibility_rule_from_dict(
        data,
    )


def normalized_eligibility_from_dict(
    data: dict[str, Any],
) -> NormalizedEligibility:
    """
    Reconstruct a complete NormalizedEligibility object
    from its JSON representation.
    """

    return NormalizedEligibility(
        age_rules=[
            eligibility_node_from_dict(rule)
            for rule in data.get(
                "age_rules",
                [],
            )
        ],
        service_rules=[
            eligibility_node_from_dict(rule)
            for rule in data.get(
                "service_rules",
                [],
            )
        ],
        qualification_rules=[
            eligibility_node_from_dict(rule)
            for rule in data.get(
                "qualification_rules",
                [],
            )
        ],
        experience_rules=[
            eligibility_node_from_dict(rule)
            for rule in data.get(
                "experience_rules",
                [],
            )
        ],
        department_rules=[
            eligibility_node_from_dict(rule)
            for rule in data.get(
                "department_rules",
                [],
            )
        ],
        special_rules=[
            eligibility_node_from_dict(rule)
            for rule in data.get(
                "special_rules",
                [],
            )
        ],
        pay_rules=[
            eligibility_node_from_dict(rule)
            for rule in data.get(
                "pay_rules",
                [],
            )
        ],
    )