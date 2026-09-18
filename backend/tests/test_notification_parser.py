from datetime import date

from app.services.documents.parsing.notification_parser import NotificationParser


def test_parses_synthetic_ssc_notification():
    text = """
    Staff Selection Commission
    Recruitment to the post of Assistant Section Officer.
    Total Vacancies: 25
    Age limit: 18 to 30 years.
    Bachelor's degree from a recognized university.
    2 years of experience.
    Pay Level-7 (Rs.44,900 - 1,42,400)
    Applications are invited from 01.09.2026 to 30.09.2026.
    """

    parsed = NotificationParser().parse(text)

    assert parsed.organization_name.value == "Staff Selection Commission"
    assert parsed.title.value == "Assistant Section Officer"
    assert parsed.vacancy_count.value == 25
    assert parsed.minimum_age.value == 18
    assert parsed.maximum_age.value == 30
    assert parsed.minimum_experience_years.value == 2
    assert parsed.pay_level.value == "Level-7"
    assert parsed.application_start.value == date(2026, 9, 1)
    assert parsed.application_end.value == date(2026, 9, 30)


def test_parses_deputation_ssc_notification():
    text = """
    Staff Selection Commission (HQ)
    post of Accounts Officer
    Filling up 04 ex-Cadre posts on deputation basis.
    Maximum age limit shall not exceed 56 years.
    Possessing the following qualifications and experience:
    A pass in the Subordinate Accounts Services or equivalent examination
    conducted by the Accounts Departments of the Central Government.
    Five years' experience in Cash, Accounts and Budget work.
    Officers under the Central Government.
    Pay Level-7 (Rs.44,900 - 1,42,400)
    """

    parsed = NotificationParser().parse(text)

    assert parsed.organization_name.value == "Staff Selection Commission (HQ)"
    assert parsed.title.value == "Accounts Officer"
    assert parsed.vacancy_count.value == 4
    assert parsed.opportunity_type.value == "DEPUTATION"
    assert parsed.maximum_age.value == 56
    assert parsed.education_level.value == "PROFESSIONAL_ACCOUNTING_EXAM"
    assert parsed.minimum_experience_years.value == 5
    assert parsed.requires_government_service.value is True
    assert parsed.pay_level.value == "Level-7"


def test_does_not_treat_generic_ms_as_degree():
    parsed = NotificationParser().parse(
        "Applications from Ms. Sharma are invited. "
        "Degree from a recognized university is required."
    )

    assert parsed.degree.value is None


def test_parses_dotted_application_dates():
    parsed = NotificationParser().parse(
        "Applications are invited from 01.09.2026 to 30.09.2026."
    )

    assert parsed.application_start.value == date(2026, 9, 1)
    assert parsed.application_end.value == date(2026, 9, 30)


def test_parses_common_age_and_vacancy_phrasings():
    parser = NotificationParser()

    parsed_age = parser.parse("Age limit: 21 to 35 years.")
    assert parsed_age.minimum_age.value == 21
    assert parsed_age.maximum_age.value == 35

    parsed_vacancy = parser.parse(
        "Applications are invited for 12 posts."
    )
    assert parsed_vacancy.vacancy_count.value == 12


def test_empty_input_is_conservative():
    parsed = NotificationParser().parse("   ")

    assert parsed.organization_name.value is None
    assert parsed.title.value is None
    assert parsed.vacancy_count.value is None
    assert parsed.minimum_age.value is None
    assert parsed.maximum_age.value is None
