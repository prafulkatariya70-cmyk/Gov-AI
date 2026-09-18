from app.services.documents.parsing.notification_parser import NotificationParser
from app.services.documents.parsing.rules.normalizer import EligibilityNormalizer
from app.services.eligibility.evaluator import EligibilityEvaluator
from app.services.eligibility.models import CandidateProfile
from app.services.eligibility.service import EligibilityEngine


NOTIFICATION = """
STAFF SELECTION COMMISSION
Recruitment to the post of Accounts Officer
Total Vacancies: 4

Age limit: 18 to 56 years.

Officers under the Central Government:
(a) holding analogous posts on regular basis in the parent cadre or Department; or
(ii) With 5 years' service in the grade rendered after appointment thereto on a regular basis in the scale of Pay Level-6 or equivalent in the parent cadre/department;

and

(b) Possessing the following qualifications and experience:
(i) A pass in the Subordinate Accounts Services or equivalent examination conducted by the Accounts Departments of the Central Government; or
(ii) Successful completion of training in the Cash and Accounts Work in the ISTM or equivalent; and
(iii) Five years' experience in Cash, Accounts and Budget work.

Pay Level-7 (Rs.44,900 - 1,42,400)
"""


def eligible_candidate() -> CandidateProfile:
    return CandidateProfile(
        age=42,
        government_employee=True,
        analogous_post=True,
        regular_service_years=8,
        current_pay_level=7,
        parent_cadre=True,
        qualifying_examination=True,
        required_training=False,
        relevant_experience_years=5,
        experience_areas=["Cash", "Accounts", "Budget"],
    )


def test_parser_normalizer_evaluator_pipeline_is_eligible():
    parser = NotificationParser()
    parsed = parser.parse(NOTIFICATION)
    rules = EligibilityNormalizer().normalize(parsed)
    result = EligibilityEvaluator().evaluate(eligible_candidate(), rules)

    assert parsed.title.value == "Accounts Officer"
    assert parsed.vacancy_count.value == 4
    assert parsed.minimum_age.value == 18
    assert parsed.maximum_age.value == 56
    assert parsed.requires_government_service.value is True

    assert len(rules.service_rules) == 2
    assert len(rules.qualification_rules) == 1
    assert rules.pay_rules[0].value == 7

    assert result.status == "ELIGIBLE"
    assert result.failed == []
    assert result.unknown == []


def test_pipeline_rejects_candidate_over_maximum_age():
    parser = NotificationParser()
    rules = EligibilityNormalizer().normalize(parser.parse(NOTIFICATION))

    candidate = eligible_candidate()
    candidate.age = 60

    result = EligibilityEvaluator().evaluate(candidate, rules)

    assert result.status == "NOT_ELIGIBLE"
    assert any(item.rule_type == "MAXIMUM_AGE" for item in result.failed)


def test_pipeline_requires_review_when_candidate_data_is_missing():
    parser = NotificationParser()
    rules = EligibilityNormalizer().normalize(parser.parse(NOTIFICATION))

    result = EligibilityEvaluator().evaluate(
        CandidateProfile(age=42),
        rules,
    )

    assert result.status == "NEEDS_REVIEW"
    assert result.failed == []
    assert result.unknown


def test_engine_wraps_real_pipeline():
    engine = EligibilityEngine(
        NotificationParser(),
        EligibilityNormalizer(),
        EligibilityEvaluator(),
    )

    result = engine.evaluate_notification(NOTIFICATION, eligible_candidate())

    assert result.status == "ELIGIBLE"
    assert result.confidence == "high"
    assert result.failed_requirements == []
    assert result.unknown_requirements == []
    assert result.evidence
