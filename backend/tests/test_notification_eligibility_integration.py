from app.services.documents.parsing.notification_parser import (
    NotificationParser,
)
from app.services.documents.parsing.rules.normalizer import (
    EligibilityNormalizer,
)
from app.services.eligibility.evaluator import (
    EligibilityEvaluator,
)
from app.services.eligibility.models import (
    CandidateProfile,
)


NOTIFICATION_TEXT = """
STAFF SELECTION COMMISSION

Applications are invited for the post of Assistant Section Officer.

Total Vacancies: 25

Age limit: 21 to 35 years.

Possessing the following qualifications and experience:

(i) A pass in the Subordinate Accounts Services or equivalent
examination conducted by the Accounts Departments of the Central
Government; or

(ii) Successful completion of training in the Cash and Accounts Work
in the ISTM or equivalent;

and

5 years' experience in Cash, Accounts and Budget work.

The candidate should be a government employee holding an analogous
post or having 5 years service at Pay Level-6 or equivalent.

Pay Level-7.

Applications are invited from 01.09.2026 to 30.09.2026.
"""


def test_parser_output_feeds_normalizer():
    """
    Verify that parser output can be passed directly into
    the EligibilityNormalizer and produces the expected
    machine-readable rules.
    """

    parsed = NotificationParser().parse(
        NOTIFICATION_TEXT
    )

    assert parsed.organization_name.value.lower() == (
        "staff selection commission"
    )

    assert parsed.title.value == (
        "Assistant Section Officer"
    )

    assert parsed.vacancy_count.value == 25

    assert parsed.minimum_age.value == 21
    assert parsed.maximum_age.value == 35

    assert parsed.minimum_experience_years.value == 5

    assert parsed.requires_government_service.value is True

    assert parsed.pay_level.value == "Level-7"

    assert parsed.qualification_text.value is not None

    normalized = EligibilityNormalizer().normalize(
        parsed
    )

    assert normalized.age_rules

    assert any(
        rule.rule_type == "MINIMUM_AGE"
        and rule.value == 21
        for rule in normalized.age_rules
    )

    assert any(
        rule.rule_type == "MAXIMUM_AGE"
        and rule.value == 35
        for rule in normalized.age_rules
    )

    assert normalized.service_rules

    assert normalized.qualification_rules

    assert normalized.pay_rules

    assert any(
        rule.rule_type == "PAY_LEVEL"
        and rule.value == 7
        for rule in normalized.pay_rules
    )


def test_complete_pipeline_returns_eligible_for_clean_rules():
    """
    Verify the complete Parser -> Normalizer -> Evaluator
    pipeline using a clean notification that contains only
    requirements the current evaluator can fully evaluate.
    """

    text = """
    STAFF SELECTION COMMISSION

    Applications are invited for the post of Assistant Section Officer.

    Total Vacancies: 25

    Age limit: 21 to 35 years.

    Candidates must have completed 5 years of relevant experience
    in Cash, Accounts and Budget work.

    Pay Level-7.

    Applications are invited from 01.09.2026 to 30.09.2026.
    """

    parsed = NotificationParser().parse(
        text
    )

    normalized = EligibilityNormalizer().normalize(
        parsed
    )

    candidate = CandidateProfile(
        age=28,
        relevant_experience_years=6,
        experience_areas=[
            "Cash",
            "Accounts",
            "Budget",
        ],
        current_pay_level=7,
    )

    result = EligibilityEvaluator().evaluate(
        candidate,
        normalized,
    )

    assert result.status == "ELIGIBLE"

    assert result.failed == []

    assert result.unknown == []


def test_complete_pipeline_rejects_ineligible_candidate():
    """
    Verify that a candidate who definitely fails an
    evaluated requirement is marked NOT_ELIGIBLE.
    """

    text = """
    STAFF SELECTION COMMISSION

    Applications are invited for the post of Assistant Section Officer.

    Age limit: 21 to 35 years.

    Candidates must have completed 5 years of relevant experience
    in Cash, Accounts and Budget work.

    Pay Level-7.
    """

    parsed = NotificationParser().parse(
        text
    )

    normalized = EligibilityNormalizer().normalize(
        parsed
    )

    candidate = CandidateProfile(
        age=40,
        relevant_experience_years=6,
        experience_areas=[
            "Cash",
            "Accounts",
            "Budget",
        ],
        current_pay_level=7,
    )

    result = EligibilityEvaluator().evaluate(
        candidate,
        normalized,
    )

    assert result.status == "NOT_ELIGIBLE"

    assert result.failed


def test_complete_pipeline_requires_review_for_missing_information():
    """
    Missing candidate information must produce NEEDS_REVIEW
    rather than automatic rejection.
    """

    text = """
    STAFF SELECTION COMMISSION

    Applications are invited for the post of Assistant Section Officer.

    Age limit: 21 to 35 years.

    Candidates must have completed 5 years of relevant experience
    in Cash, Accounts and Budget work.

    Pay Level-7.
    """

    parsed = NotificationParser().parse(
        text
    )

    normalized = EligibilityNormalizer().normalize(
        parsed
    )

    candidate = CandidateProfile()

    result = EligibilityEvaluator().evaluate(
        candidate,
        normalized,
    )

    assert result.status == "NEEDS_REVIEW"

    assert result.unknown

    assert result.failed == []