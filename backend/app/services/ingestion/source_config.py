from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.job_source import JobSource


@dataclass(frozen=True)
class SourceConfig:
    name: str
    base_url: str
    source_type: str
    check_interval_minutes: int = 30


SOURCE_CONFIGS = {
    "UPSC": SourceConfig(
        name="UPSC",
        base_url="https://www.upsc.gov.in/",
        source_type="government",
        check_interval_minutes=30,
    ),

    "SSC": SourceConfig(
        name="SSC",
        base_url="https://ssc.gov.in/",
        source_type="government",
        check_interval_minutes=30,
    ),

    "RRB": SourceConfig(
        name="RRB",
        base_url="https://www.rrb.gov.in/",
        source_type="government",
        check_interval_minutes=30,
    ),

    "KARNATAKA_TEACHER": SourceConfig(
        name="KARNATAKA_TEACHER",
        base_url="https://sts.karnataka.gov.in/GPSTRNHK/",
        source_type="government",
        check_interval_minutes=30,
    ),

    "KPSC": SourceConfig(
        name="KPSC",
        base_url="https://kpsc.kar.nic.in/",
        source_type="government",
        check_interval_minutes=30,
    ),
}


def ensure_configured_sources(
    db: Session,
) -> int:
    """
    Ensure every configured official source has a database row.

    The operation is idempotent and allows newly added adapters,
    such as KPSC, to become active without manual SQL inserts.
    """

    created = 0

    for config in SOURCE_CONFIGS.values():
        existing = (
            db.query(JobSource)
            .filter(JobSource.name == config.name)
            .one_or_none()
        )

        if existing is not None:
            continue

        db.add(
            JobSource(
                name=config.name,
                base_url=config.base_url,
                source_type=config.source_type,
                is_active=True,
                check_interval_minutes=(
                    config.check_interval_minutes
                ),
            )
        )

        created += 1

    if created:
        db.commit()

    return created


def get_source_config(
    source_name: str,
) -> SourceConfig:
    config = SOURCE_CONFIGS.get(source_name)

    if config is None:
        raise ValueError(
            f"No configuration found for source: {source_name}"
        )

    return config
