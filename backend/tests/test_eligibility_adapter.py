from datetime import date

from app.models.user_profile import UserProfile
from app.services.eligibility.adapter import (
    user_profile_to_candidate_profile,
)


def test_user_profile_maps_to_candidate_profile():

    profile = UserProfile(
        user_id=1,
        date_of_birth=date(
            1996,
            5,
            10,
        ),
        education_level="Graduate",
        degree="B.Com",
        branch="Commerce",
        experience_years=5,
    )

    candidate = user_profile_to_candidate_profile(
        profile,
        reference_date=date(
            2026,
            9,
            1,
        ),
    )

    assert candidate.age == 30

    assert (
        candidate.relevant_experience_years
        == 5
    )

    assert (
        candidate.qualification_text
        == "Graduate, B.Com, Commerce"
    )


def test_missing_departmental_information_remains_unknown():

    profile = UserProfile(
        user_id=1,
        experience_years=5,
    )

    candidate = user_profile_to_candidate_profile(
        profile,
        reference_date=date(
            2026,
            9,
            1,
        ),
    )

    assert candidate.age is None

    assert candidate.government_employee is None

    assert candidate.analogous_post is None

    assert candidate.regular_service_years is None

    assert candidate.current_pay_level is None

    assert candidate.parent_cadre is None

    assert candidate.qualifying_examination is None

    assert candidate.required_training is None

    assert (
        candidate.relevant_experience_years
        == 5
    )

    assert candidate.experience_areas == []