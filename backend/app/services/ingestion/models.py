from dataclasses import dataclass
from datetime import date


@dataclass
class DiscoveredJob:
    organization_name: str
    title: str
    official_url: str
    notification_url: str | None = None

    description: str | None = None

    application_start: date | None = None
    application_end: date | None = None

    source_name: str | None = None

    external_id: str | None = None

    opportunity_type: str = "PUBLIC_RECRUITMENT"