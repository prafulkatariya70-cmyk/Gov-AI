from abc import ABC, abstractmethod

from app.services.ingestion.models import DiscoveredJob


class JobSourceAdapter(ABC):
    """
    Base interface for every government job source.
    """

    source_name: str

    @abstractmethod
    def discover_jobs(self) -> list[DiscoveredJob]:
        """
        Discover and normalize jobs from the source.
        """
        raise NotImplementedError