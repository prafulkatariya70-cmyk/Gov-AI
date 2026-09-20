from __future__ import annotations

from datetime import date

from app.models.user_profile import UserProfile
from app.services.eligibility.models import CandidateProfile


def calculate_age(
    date_of_birth: date,
    reference_date: date | None = None,
) -> int:
    """
    Calculate the candidate's age on the reference date.
    """

    if reference_date is None:
        reference_date = date.today()

    age = (
        reference_date.year
        - date_of_birth.year
    )

    birthday_not_reached = (
        (
            reference_date.month,
            reference_date.day,
        )
        < (
            date_of_birth.month,
            date_of_birth.day,
        )
    )

    if birthday_not_reached:
        age -= 1

    return age


def user_profile_to_candidate_profile(
    profile: UserProfile,
    reference_date: date | None = None,
) -> CandidateProfile:
    """
    Convert the database UserProfile into the
    CandidateProfile consumed by the rule-tree
    eligibility evaluator.

    Only information actually represented by
    UserProfile is mapped.

    Missing departmental/deputation information
    remains None and is therefore evaluated as
    UNKNOWN by the eligibility engine.
    """

    # ---------------------------------------------------------
    # AGE
    # ---------------------------------------------------------

    age = None

    if profile.date_of_birth is not None:
        age = calculate_age(
            profile.date_of_birth,
            reference_date,
        )

    # ---------------------------------------------------------
    # EXPERIENCE
    # ---------------------------------------------------------

    relevant_experience_years = (
        float(profile.experience_years)
        if profile.experience_years is not None
        else None
    )

    # ---------------------------------------------------------
    # QUALIFICATION TEXT
    # ---------------------------------------------------------

    qualification_parts = []

    if profile.education_level:
        qualification_parts.append(
            profile.education_level.strip()
        )

    if profile.degree:
        qualification_parts.append(
            profile.degree.strip()
        )

    if profile.branch:
        qualification_parts.append(
            profile.branch.strip()
        )

    qualification_text = (
        ", ".join(qualification_parts)
        if qualification_parts
        else None
    )

    # ---------------------------------------------------------
    # BUILD CANDIDATE PROFILE
    # ---------------------------------------------------------

    return CandidateProfile(
        age=age,

        # These fields are not currently represented
        # by UserProfile. Do not guess them.
        government_employee=None,
        analogous_post=None,
        regular_service_years=None,
        current_pay_level=None,
        parent_cadre=None,
        qualifying_examination=None,
        required_training=None,

        # UserProfile's generic experience value can
        # safely represent total/reported experience,
        # but not government service years.
        relevant_experience_years=(
            relevant_experience_years
        ),

        # Experience areas are not currently captured
        # by UserProfile.
        experience_areas=[],

        qualification_text=qualification_text,
    )