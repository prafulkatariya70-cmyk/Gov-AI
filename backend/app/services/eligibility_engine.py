from dataclasses import dataclass, field
from datetime import date

from app.models.job_eligibility import JobEligibility
from app.models.user_profile import UserProfile


@dataclass
class EligibilityResult:
    eligible: bool
    score: int
    reasons: list[str] = field(default_factory=list)
    failed_requirements: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def calculate_age(date_of_birth: date, reference_date: date | None = None) -> int:
    """
    Calculate a person's age on a specific date.
    If no reference date is provided, today's date is used.
    """

    if reference_date is None:
        reference_date = date.today()

    age = reference_date.year - date_of_birth.year

    birthday_has_not_occurred = (
        (reference_date.month, reference_date.day)
        < (date_of_birth.month, date_of_birth.day)
    )

    if birthday_has_not_occurred:
        age -= 1

    return age


def check_eligibility(
    profile: UserProfile,
    requirements: JobEligibility,
    reference_date: date | None = None,
) -> EligibilityResult:
    """
    Compare a user's profile against a job's eligibility requirements.
    """

    reasons: list[str] = []
    failed_requirements: list[str] = []
    warnings: list[str] = []

    total_checks = 0
    passed_checks = 0

    # ---------------------------------------------------------
    # AGE
    # ---------------------------------------------------------

    if requirements.minimum_age is not None or requirements.maximum_age is not None:
        total_checks += 1

        if profile.date_of_birth is None:
            warnings.append(
                "Date of birth is missing, so the age requirement could not be verified."
            )
        else:
            age = calculate_age(
                profile.date_of_birth,
                reference_date,
            )

            age_valid = True

            if (
                requirements.minimum_age is not None
                and age < requirements.minimum_age
            ):
                age_valid = False
                failed_requirements.append(
                    f"Minimum age required: {requirements.minimum_age}. "
                    f"Your age: {age}."
                )

            if (
                requirements.maximum_age is not None
                and age > requirements.maximum_age
            ):
                age_valid = False
                failed_requirements.append(
                    f"Maximum age allowed: {requirements.maximum_age}. "
                    f"Your age: {age}."
                )

            if age_valid:
                passed_checks += 1
                reasons.append("Age requirement satisfied.")

    # ---------------------------------------------------------
    # EDUCATION LEVEL
    # ---------------------------------------------------------

    if requirements.education_level:
        total_checks += 1

        if not profile.education_level:
            warnings.append(
                "Education level is missing, so the education requirement "
                "could not be verified."
            )
        elif (
            profile.education_level.strip().lower()
            == requirements.education_level.strip().lower()
        ):
            passed_checks += 1
            reasons.append("Education level requirement satisfied.")
        else:
            failed_requirements.append(
                f"Required education level: {requirements.education_level}. "
                f"Your education level: {profile.education_level}."
            )

    # ---------------------------------------------------------
    # DEGREE
    # ---------------------------------------------------------

    if requirements.degree:
        total_checks += 1

        if not profile.degree:
            warnings.append(
                "Degree is missing, so the degree requirement could not be verified."
            )
        elif (
            profile.degree.strip().lower()
            == requirements.degree.strip().lower()
        ):
            passed_checks += 1
            reasons.append("Degree requirement satisfied.")
        else:
            failed_requirements.append(
                f"Required degree: {requirements.degree}. "
                f"Your degree: {profile.degree}."
            )

    # ---------------------------------------------------------
    # BRANCH
    # ---------------------------------------------------------

    if requirements.branch:
        total_checks += 1

        if not profile.branch:
            warnings.append(
                "Engineering branch is missing, so the branch requirement "
                "could not be verified."
            )
        elif (
            profile.branch.strip().lower()
            == requirements.branch.strip().lower()
        ):
            passed_checks += 1
            reasons.append("Branch requirement satisfied.")
        else:
            failed_requirements.append(
                f"Required branch: {requirements.branch}. "
                f"Your branch: {profile.branch}."
            )

    # ---------------------------------------------------------
    # EXPERIENCE
    # ---------------------------------------------------------

    if requirements.minimum_experience_years > 0:
        total_checks += 1

        if profile.experience_years >= requirements.minimum_experience_years:
            passed_checks += 1
            reasons.append("Experience requirement satisfied.")
        else:
            failed_requirements.append(
                f"Minimum experience required: "
                f"{requirements.minimum_experience_years} years. "
                f"Your experience: {profile.experience_years} years."
            )

    # ---------------------------------------------------------
    # STATE
    # ---------------------------------------------------------

    if requirements.eligible_states:
        total_checks += 1

        if not profile.state:
            warnings.append(
                "State is missing, so the state requirement could not be verified."
            )
        else:
            allowed_states = [
                state.strip().lower()
                for state in requirements.eligible_states.split(",")
                if state.strip()
            ]

            if profile.state.strip().lower() in allowed_states:
                passed_checks += 1
                reasons.append("State requirement satisfied.")
            else:
                failed_requirements.append(
                    f"Eligible states: {requirements.eligible_states}. "
                    f"Your state: {profile.state}."
                )

    # ---------------------------------------------------------
    # CATEGORY
    # ---------------------------------------------------------

    if requirements.eligible_categories:
        total_checks += 1

        if not profile.category:
            warnings.append(
                "Category is missing, so the category requirement could "
                "not be verified."
            )
        else:
            allowed_categories = [
                category.strip().lower()
                for category in requirements.eligible_categories.split(",")
                if category.strip()
            ]

            if profile.category.strip().lower() in allowed_categories:
                passed_checks += 1
                reasons.append("Category requirement satisfied.")
            else:
                failed_requirements.append(
                    f"Eligible categories: {requirements.eligible_categories}. "
                    f"Your category: {profile.category}."
                )

    # ---------------------------------------------------------
    # SCORE
    # ---------------------------------------------------------

    if total_checks == 0:
        score = 0
        warnings.append(
            "No eligibility requirements are available for this job."
        )
    else:
        score = round((passed_checks / total_checks) * 100)

    # ---------------------------------------------------------
    # FINAL ELIGIBILITY
    # ---------------------------------------------------------

    eligible = len(failed_requirements) == 0 and len(warnings) == 0

    return EligibilityResult(
        eligible=eligible,
        score=score,
        reasons=reasons,
        failed_requirements=failed_requirements,
        warnings=warnings,
    )