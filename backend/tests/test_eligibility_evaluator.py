from app.services.documents.parsing.rules.models import (
    EligibilityRule,
    EligibilityRuleGroup,
    NormalizedEligibility,
)
from app.services.eligibility.evaluator import (
    EligibilityEvaluator,
)
from app.services.eligibility.models import (
    CandidateProfile,
)


def make_candidate(**overrides):
    data = {
        "age": 30,
        "government_employee": True,
        "analogous_post": True,
        "regular_service_years": 8,
        "current_pay_level": 10,
        "parent_cadre": True,
        "qualifying_examination": True,
        "required_training": False,
        "relevant_experience_years": 5,
        "experience_areas": [
            "Cash",
            "Accounts",
            "Budget",
        ],
        "qualification_text": "Graduate",
    }

    data.update(overrides)

    return CandidateProfile(**data)


def make_rules(**overrides):
    data = {
        "age_rules": [],
        "service_rules": [],
        "qualification_rules": [],
        "experience_rules": [],
        "department_rules": [],
        "special_rules": [],
        "pay_rules": [],
    }

    data.update(overrides)

    return NormalizedEligibility(**data)


# ============================================================
# BASIC PASS
# ============================================================


def test_all_requirements_pass():

    rules = make_rules(
        age_rules=[
            EligibilityRule(
                rule_type="MINIMUM_AGE",
                value=18,
            )
        ]
    )

    candidate = make_candidate(
        age=30,
    )

    result = EligibilityEvaluator().evaluate(
        candidate,
        rules,
    )

    assert result.status == "ELIGIBLE"
    assert result.failed == []
    assert result.unknown == []


# ============================================================
# BASIC FAILURE
# ============================================================


def test_failed_requirement_makes_candidate_not_eligible():

    rules = make_rules(
        age_rules=[
            EligibilityRule(
                rule_type="MINIMUM_AGE",
                value=35,
            )
        ]
    )

    candidate = make_candidate(
        age=30,
    )

    result = EligibilityEvaluator().evaluate(
        candidate,
        rules,
    )

    assert result.status == "NOT_ELIGIBLE"
    assert len(result.failed) == 1
    assert result.unknown == []


# ============================================================
# UNKNOWN
# ============================================================


def test_missing_candidate_information_requires_review():

    rules = make_rules(
        age_rules=[
            EligibilityRule(
                rule_type="MINIMUM_AGE",
                value=18,
            )
        ]
    )

    candidate = make_candidate(
        age=None,
    )

    result = EligibilityEvaluator().evaluate(
        candidate,
        rules,
    )

    assert result.status == "NEEDS_REVIEW"
    assert result.failed == []
    assert len(result.unknown) == 1


# ============================================================
# OR GROUP
# ============================================================


def test_or_group_passes_when_one_branch_passes():

    rules = make_rules(
        qualification_rules=[
            EligibilityRuleGroup(
                operator="OR",
                rules=[
                    EligibilityRule(
                        rule_type="QUALIFYING_EXAMINATION",
                        value=True,
                    ),
                    EligibilityRule(
                        rule_type="REQUIRED_TRAINING",
                        value=True,
                    ),
                ],
            )
        ]
    )

    candidate = make_candidate(
        qualifying_examination=True,
        required_training=False,
    )

    result = EligibilityEvaluator().evaluate(
        candidate,
        rules,
    )

    assert result.status == "ELIGIBLE"

    assert result.failed == []

    assert len(result.passed) == 1
    assert result.passed[0].rule_type == "OR_GROUP"


def test_or_group_fails_when_all_branches_fail():

    rules = make_rules(
        qualification_rules=[
            EligibilityRuleGroup(
                operator="OR",
                rules=[
                    EligibilityRule(
                        rule_type="QUALIFYING_EXAMINATION",
                        value=True,
                    ),
                    EligibilityRule(
                        rule_type="REQUIRED_TRAINING",
                        value=True,
                    ),
                ],
            )
        ]
    )

    candidate = make_candidate(
        qualifying_examination=False,
        required_training=False,
    )

    result = EligibilityEvaluator().evaluate(
        candidate,
        rules,
    )

    assert result.status == "NOT_ELIGIBLE"

    assert len(result.failed) == 1
    assert result.failed[0].rule_type == "OR_GROUP"


def test_or_group_requires_review_when_no_branch_passes_but_one_is_unknown():

    rules = make_rules(
        qualification_rules=[
            EligibilityRuleGroup(
                operator="OR",
                rules=[
                    EligibilityRule(
                        rule_type="QUALIFYING_EXAMINATION",
                        value=True,
                    ),
                    EligibilityRule(
                        rule_type="REQUIRED_TRAINING",
                        value=True,
                    ),
                ],
            )
        ]
    )

    candidate = make_candidate(
        qualifying_examination=None,
        required_training=False,
    )

    result = EligibilityEvaluator().evaluate(
        candidate,
        rules,
    )

    assert result.status == "NEEDS_REVIEW"

    assert result.failed == []

    assert len(result.unknown) == 1
    assert result.unknown[0].rule_type == "OR_GROUP"


# ============================================================
# AND GROUP
# ============================================================


def test_and_group_fails_when_one_requirement_fails():

    rules = make_rules(
        service_rules=[
            EligibilityRuleGroup(
                operator="AND",
                rules=[
                    EligibilityRule(
                        rule_type="MINIMUM_SERVICE_YEARS",
                        value=5,
                    ),
                    EligibilityRule(
                        rule_type="MINIMUM_SERVICE_PAY_LEVEL",
                        value=10,
                    ),
                ],
            )
        ]
    )

    candidate = make_candidate(
        regular_service_years=3,
        current_pay_level=10,
    )

    result = EligibilityEvaluator().evaluate(
        candidate,
        rules,
    )

    assert result.status == "NOT_ELIGIBLE"

    assert len(result.failed) >= 1


def test_and_group_requires_review_when_requirement_is_unknown():

    rules = make_rules(
        service_rules=[
            EligibilityRuleGroup(
                operator="AND",
                rules=[
                    EligibilityRule(
                        rule_type="MINIMUM_SERVICE_YEARS",
                        value=5,
                    ),
                    EligibilityRule(
                        rule_type="MINIMUM_SERVICE_PAY_LEVEL",
                        value=10,
                    ),
                ],
            )
        ]
    )

    candidate = make_candidate(
        regular_service_years=None,
        current_pay_level=10,
    )

    result = EligibilityEvaluator().evaluate(
        candidate,
        rules,
    )

    assert result.status == "NEEDS_REVIEW"

    assert len(result.unknown) >= 1


# ============================================================
# NESTED LOGIC
# ============================================================


def test_nested_and_or_logic():

    rules = make_rules(
        qualification_rules=[
            EligibilityRuleGroup(
                operator="AND",
                rules=[
                    EligibilityRuleGroup(
                        operator="OR",
                        rules=[
                            EligibilityRule(
                                rule_type="QUALIFYING_EXAMINATION",
                                value=True,
                            ),
                            EligibilityRule(
                                rule_type="REQUIRED_TRAINING",
                                value=True,
                            ),
                        ],
                    ),
                    EligibilityRule(
                        rule_type="MINIMUM_RELEVANT_EXPERIENCE",
                        value={
                            "years": 5,
                            "areas": [
                                "Cash",
                                "Accounts",
                                "Budget",
                            ],
                        },
                    ),
                ],
            )
        ]
    )

    candidate = make_candidate(
        qualifying_examination=True,
        required_training=False,
        relevant_experience_years=5,
        experience_areas=[
            "Cash",
            "Accounts",
            "Budget",
        ],
    )

    result = EligibilityEvaluator().evaluate(
        candidate,
        rules,
    )

    assert result.status == "ELIGIBLE"


# ============================================================
# RELEVANT EXPERIENCE
# ============================================================


def test_relevant_experience_fails_when_years_are_insufficient():

    rules = make_rules(
        experience_rules=[
            EligibilityRule(
                rule_type="MINIMUM_RELEVANT_EXPERIENCE",
                value={
                    "years": 5,
                    "areas": [
                        "Cash",
                        "Accounts",
                    ],
                },
            )
        ]
    )

    candidate = make_candidate(
        relevant_experience_years=3,
        experience_areas=[
            "Cash",
            "Accounts",
        ],
    )

    result = EligibilityEvaluator().evaluate(
        candidate,
        rules,
    )

    assert result.status == "NOT_ELIGIBLE"


def test_relevant_experience_fails_when_area_is_missing():

    rules = make_rules(
        experience_rules=[
            EligibilityRule(
                rule_type="MINIMUM_RELEVANT_EXPERIENCE",
                value={
                    "years": 5,
                    "areas": [
                        "Cash",
                        "Accounts",
                        "Budget",
                    ],
                },
            )
        ]
    )

    candidate = make_candidate(
        relevant_experience_years=5,
        experience_areas=[
            "Cash",
            "Accounts",
        ],
    )

    result = EligibilityEvaluator().evaluate(
        candidate,
        rules,
    )

    assert result.status == "NOT_ELIGIBLE"


# ============================================================
# UNKNOWN MUST NOT BECOME FAILURE
# ============================================================


def test_unknown_information_is_not_treated_as_failure():

    rules = make_rules(
        service_rules=[
            EligibilityRule(
                rule_type="GOVERNMENT_SERVICE_REQUIRED",
                value=True,
            )
        ]
    )

    candidate = make_candidate(
        government_employee=None,
    )

    result = EligibilityEvaluator().evaluate(
        candidate,
        rules,
    )

    assert result.status == "NEEDS_REVIEW"

    assert result.failed == []

    assert len(result.unknown) == 1

def test_empty_rule_set_requires_review():
    from app.services.documents.parsing.rules.models import (
        NormalizedEligibility,
    )

    from app.services.eligibility.models import (
        CandidateProfile,
    )

    evaluator = EligibilityEvaluator()

    rules = NormalizedEligibility()

    candidate = CandidateProfile(
        age=21,
        relevant_experience_years=0,
    )

    result = evaluator.evaluate(
        candidate,
        rules,
    )

    assert result.status == "NEEDS_REVIEW"
    assert result.confidence == "medium"
    assert result.failed == []
    assert result.passed == []