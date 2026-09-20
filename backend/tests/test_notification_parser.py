from datetime import date

from app.services.documents.parsing.notification_parser import (
    NotificationParser,
)


def parse(text: str):
    return NotificationParser().parse(text)


# ============================================================
# BASIC RECRUITMENT NOTIFICATION
# ============================================================


def test_parses_basic_recruitment_notification():
    text = """
    GOVERNMENT OF INDIA
    MINISTRY OF EXAMPLE
    Staff Selection Commission

    Recruitment to the post of Assistant Section Officer

    Total Vacancies: 25

    Candidates must possess a Bachelor's Degree from a recognized
    university.

    Age limit: 18 to 30 years.

    Essential qualification:
    Bachelor's Degree in any discipline.

    Minimum 2 years experience in government service.

    Pay Level-7 in the Pay Matrix.
    Pay Scale: Rs. 44,900 - 1,42,400.

    Applications are invited from 01.09.2026 to 30.09.2026.
    """

    result = parse(text)

    assert result.organization_name.value is not None
    assert result.title.value is not None
    assert result.vacancy_count.value == 25

    assert result.minimum_age.value == 18
    assert result.maximum_age.value == 30

    assert result.minimum_experience_years.value == 2

    assert result.pay_level.value is not None
    assert result.salary_text.value is not None


# ============================================================
# SSC DEPUTATION NOTIFICATION
# ============================================================


def test_parses_ssc_accounts_officer_notification():
    text = """
    Staff Selection Commission (HQ)

    Filling up 04 (four) ex-Cadre posts of Accounts Officer
    in various Regional Offices on deputation basis.

    The maximum age limit on deputation shall not exceed 56 years.

    Officers under the Central Government holding analogous posts
    on regular basis in the parent cadre or Department OR With
    5 years' service in the grade rendered after appointment thereto
    on a regular basis in the scale of Pay Level-6 or equivalent
    in the parent cadre/department.

    Possessing the following qualifications and experience:

    (i) A pass in the Subordinate Accounts Services or equivalent
    examination conducted by the Accounts Departments of the
    Central Government;

    or

    (ii) Successful completion of training in the Cash and Accounts
    Work in the ISTM or equivalent;

    and

    (iii) Five years' experience in Cash, Accounts and Budget work.

    Pay Level-7
    Rs.44,900 - 1,42,400
    """

    result = parse(text)

    assert result.organization_name.value == "Staff Selection Commission (HQ)"

    assert result.vacancy_count.value == 4

    assert result.maximum_age.value == 56

    assert result.minimum_experience_years.value == 5

    assert result.requires_government_service.value is True

    assert result.education_level.value == "PROFESSIONAL_ACCOUNTING_EXAM"

    assert result.degree.value is None

    assert result.pay_level.value == "Level-7"

    assert result.salary_text.value == "Rs.44,900 - 1,42,400"


# ============================================================
# DEGREE DETECTION
# ============================================================


def test_detects_specific_degree():
    text = """
    Essential Qualification:
    Bachelor of Technology (B.Tech) in Computer Science
    from a recognized university.
    """

    result = parse(text)

    assert result.degree.value is not None


def test_does_not_treat_generic_degree_word_as_degree():
    text = """
    Candidates should have a Degree from a recognized university.
    """

    result = parse(text)

    assert result.degree.value is None


def test_does_not_treat_ms_as_degree_without_academic_context():
    text = """
    The notification was issued by the MS office.
    Officers should submit the application through proper channel.
    """

    result = parse(text)

    assert result.degree.value is None


def test_detects_ms_with_academic_context():
    text = """
    Essential Qualification:
    M.S. in Computer Science or related discipline
    from a recognized university.
    """

    result = parse(text)

    assert result.degree.value is not None


# ============================================================
# EXPERIENCE
# ============================================================


def test_parses_numeric_experience():
    text = """
    Candidates must have at least 3 years experience
    in Accounts and Finance.
    """

    result = parse(text)

    assert result.minimum_experience_years.value == 3


def test_parses_word_based_experience():
    text = """
    Candidates must have Five years' experience
    in Cash, Accounts and Budget work.
    """

    result = parse(text)

    assert result.minimum_experience_years.value == 5


# ============================================================
# VACANCIES
# ============================================================


def test_parses_vacancy_count_from_number():
    text = """
    Applications are invited for 12 posts of Junior Engineer.
    """

    result = parse(text)

    assert result.vacancy_count.value == 12


def test_parses_vacancy_count_from_number_and_word():
    text = """
    Filling up 04 (four) ex-Cadre posts of Accounts Officer.
    """

    result = parse(text)

    assert result.vacancy_count.value == 4


# ============================================================
# AGE
# ============================================================


def test_parses_minimum_and_maximum_age():
    text = """
    Age limit: 21 to 35 years.
    """

    result = parse(text)

    assert result.minimum_age.value == 21
    assert result.maximum_age.value == 35


def test_parses_maximum_age_only():
    text = """
    The maximum age limit shall not exceed 56 years.
    """

    result = parse(text)

    assert result.maximum_age.value == 56


# ============================================================
# OPPORTUNITY TYPE
# ============================================================


def test_detects_deputation_opportunity():
    text = """
    The post will be filled up on deputation basis.
    """

    result = parse(text)

    assert result.opportunity_type.value == "DEPUTATION"


# ============================================================
# GOVERNMENT SERVICE
# ============================================================


def test_detects_government_service_requirement():
    text = """
    Officers under the Central Government holding analogous
    posts on regular basis in the parent cadre or Department.
    """

    result = parse(text)

    assert result.requires_government_service.value is True


# ============================================================
# QUALIFICATION TEXT
# ============================================================


def test_extracts_full_qualification_block():
    text = """
    Possessing the following qualifications and experience:

    (i) Bachelor's Degree from a recognized university;

    (ii) Two years' experience in administration;

    (iii) Knowledge of government procedures.

    Note-1: The qualification must be supported by documents.

    Applications should be submitted through proper channel.
    """

    result = parse(text)

    assert result.qualification_text.value is not None

    qualification = result.qualification_text.value

    assert "Bachelor's Degree" in qualification
    assert "Two years' experience" in qualification
    assert "Knowledge of government procedures" in qualification

    assert "Note-1" not in qualification


# ============================================================
# PAY AND SALARY
# ============================================================


def test_parses_pay_level_and_salary():
    text = """
    Pay Level-7 in the Pay Matrix.
    Pay Scale: Rs.44,900 - 1,42,400.
    """

    result = parse(text)

    assert result.pay_level.value == "Level-7"
    assert result.salary_text.value == "Rs.44,900 - 1,42,400"


# ============================================================
# APPLICATION DATES
# ============================================================


def test_parses_application_dates():
    text = """
    Online applications will be accepted from 01.09.2026
    to 30.09.2026.
    """

    result = parse(text)

    assert result.application_start.value == date(2026, 9, 1)
    assert result.application_end.value == date(2026, 9, 30)


# ============================================================
# RELATIVE DEADLINE
# ============================================================


def test_relative_deadline_does_not_create_fake_application_date():
    text = """
    Applications should reach the Commission within 2 months
    from publication in Employment News.
    """

    result = parse(text)

    assert result.application_start.value is None
    assert result.application_end.value is None


# ============================================================
# CONSERVATIVE PARSING
# ============================================================


def test_empty_text_does_not_crash():
    result = parse("")

    assert result is not None


def test_unrelated_text_does_not_invent_degree():
    text = """
    The department will conduct a meeting regarding recruitment.
    Officers must attend the meeting.
    """

    result = parse(text)

    assert result.degree.value is None