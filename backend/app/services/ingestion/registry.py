from app.services.ingestion.base_adapter import JobSourceAdapter
from app.services.ingestion.karnataka_teacher_adapter import (
    KarnatakaTeacherAdapter,
)
from app.services.ingestion.rrb_adapter import RRBAdapter
from app.services.ingestion.ssc_adapter import SSCAdapter
from app.services.ingestion.upsc_adapter import UPSCAdapter


ADAPTER_REGISTRY: dict[str, type[JobSourceAdapter]] = {
    "UPSC": UPSCAdapter,
    "SSC": SSCAdapter,
    "RRB": RRBAdapter,
    "KARNATAKA_TEACHER": KarnatakaTeacherAdapter,
}


def get_adapter(
    source_name: str,
) -> JobSourceAdapter:
    """
    Return the adapter configured for a source.
    """

    adapter_class = ADAPTER_REGISTRY.get(
        source_name
    )

    if adapter_class is None:
        raise ValueError(
            f"No adapter registered for source: {source_name}"
        )

    return adapter_class()