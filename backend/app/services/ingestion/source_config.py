from dataclasses import dataclass


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
}


def get_source_config(
    source_name: str,
) -> SourceConfig:
    config = SOURCE_CONFIGS.get(source_name)

    if config is None:
        raise ValueError(
            f"No configuration found for source: {source_name}"
        )

    return config