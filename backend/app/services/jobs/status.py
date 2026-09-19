from __future__ import annotations

from dataclasses import dataclass
from datetime import date


UPCOMING = "UPCOMING"
OPEN = "OPEN"
CLOSED = "CLOSED"
NO_DEADLINE = "NO_DEADLINE"


@dataclass(frozen=True)
class JobStatus:
    status: str
    is_closing_soon: bool
    is_new_today: bool


def derive_job_status(
    *,
    start_date: date | None,
    last_date: date | None,
    notification_date: date | None = None,
    today: date | None = None,
    closing_soon_days: int = 3,
) -> JobStatus:
    """Derive job lifecycle flags from persisted notification dates."""
    current = today or date.today()

    if start_date and last_date and start_date > last_date:
        raise ValueError("Application start date cannot be after the last date.")

    if start_date and start_date > current:
        status = UPCOMING
    elif last_date and last_date < current:
        status = CLOSED
    elif start_date or last_date:
        status = OPEN
    else:
        status = NO_DEADLINE

    closing_soon = (
        status == OPEN
        and last_date is not None
        and 0 <= (last_date - current).days <= closing_soon_days
    )

    is_new_today = notification_date == current if notification_date else False

    return JobStatus(
        status=status,
        is_closing_soon=closing_soon,
        is_new_today=is_new_today,
    )
