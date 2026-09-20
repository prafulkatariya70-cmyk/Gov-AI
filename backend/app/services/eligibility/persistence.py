from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.job_eligibility import JobEligibility
from app.services.documents.parsing.notification_parser import (
    ParsedNotification,
)
from app.services.documents.parsing.rules.normalizer import (
    EligibilityNormalizer,
)
from app.services.eligibility.serialization import (
    normalized_eligibility_to_dict,
)


def _value(field) -> object | None:
    """
    Safely extract the value from a ParsedField.
    """

    if field is None:
        return None

    return getattr(
        field,
        "value",
        None,
    )


def save_parsed_eligibility(
    db: Session,
    job: Job,
    parsed: ParsedNotification,
) -> JobEligibility:
    """
    Create or update the eligibility record for a job.

    The parser produces ParsedField objects.

    This function:

    1. Stores the existing flattened parsed values.
    2. Builds the normalized eligibility rule tree.
    3. Serializes that rule tree into JSON.
    4. Stores it in JobEligibility.normalized_rules.
    """

    eligibility = job.eligibility

    if eligibility is None:

        eligibility = JobEligibility(
            job_id=job.id,
        )

        db.add(
            eligibility,
        )

    # ================================================================
    # APPLICATION DATES
    # ================================================================

    application_start = _value(
        parsed.application_start,
    )

    application_end = _value(
        parsed.application_end,
    )

    if application_start is not None:
        job.application_start = application_start

    if application_end is not None:
        job.application_end = application_end


    # ================================================================
    # AGE
    # ================================================================

    minimum_age = _value(
        parsed.minimum_age,
    )

    maximum_age = _value(
        parsed.maximum_age,
    )

    eligibility.minimum_age = (
        int(minimum_age)
        if minimum_age is not None
        else None
    )

    eligibility.maximum_age = (
        int(maximum_age)
        if maximum_age is not None
        else None
    )

    # ================================================================
    # EDUCATION
    # ================================================================

    eligibility.education_level = _value(
        parsed.education_level,
    )

    eligibility.degree = _value(
        parsed.degree,
    )

    eligibility.branch = _value(
        parsed.branch,
    )

    # ================================================================
    # EXPERIENCE
    # ================================================================

    minimum_experience = _value(
        parsed.minimum_experience_years,
    )

    eligibility.minimum_experience_years = (
        int(minimum_experience)
        if minimum_experience is not None
        else 0
    )

    eligibility.experience_requirement = _value(
        parsed.experience_requirement,
    )

    # ================================================================
    # GOVERNMENT / SERVICE
    # ================================================================

    government_service = _value(
        parsed.requires_government_service,
    )

    eligibility.requires_government_service = bool(
        government_service,
    )

    eligibility.service_requirement = _value(
        parsed.service_requirement,
    )

    eligibility.department_requirement = _value(
        parsed.department_requirement,
    )

    # ================================================================
    # QUALIFICATION
    # ================================================================

    eligibility.qualification_text = _value(
        parsed.qualification_text,
    )

    # ================================================================
    # SPECIAL REQUIREMENTS
    # ================================================================

    eligibility.special_requirements = _value(
        parsed.special_requirements,
    )

    # ================================================================
    # NORMALIZE ELIGIBILITY
    # ================================================================

    normalizer = EligibilityNormalizer()

    normalized = normalizer.normalize(
        parsed,
    )

    # ================================================================
    # SERIALIZE NORMALIZED RULE TREE
    # ================================================================

    eligibility.normalized_rules = (
        normalized_eligibility_to_dict(
            normalized,
        )
    )

    # ================================================================
    # DATABASE FLUSH
    # ================================================================

    db.flush()

    return eligibility