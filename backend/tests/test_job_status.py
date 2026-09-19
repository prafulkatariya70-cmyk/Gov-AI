from datetime import date

import pytest

from app.services.jobs.status import CLOSED, NO_DEADLINE, OPEN, UPCOMING, derive_job_status


TODAY = date(2026, 9, 19)


def test_upcoming_when_application_start_is_in_future():
    result = derive_job_status(
        start_date=date(2026, 9, 25),
        last_date=date(2026, 10, 5),
        today=TODAY,
    )
    assert result.status == UPCOMING
    assert not result.is_closing_soon


def test_open_when_application_window_contains_today():
    result = derive_job_status(
        start_date=date(2026, 9, 10),
        last_date=date(2026, 9, 22),
        today=TODAY,
    )
    assert result.status == OPEN
    assert not result.is_closing_soon


def test_closing_soon_when_deadline_is_within_three_days():
    result = derive_job_status(
        start_date=date(2026, 9, 10),
        last_date=date(2026, 9, 22),
        today=TODAY,
        closing_soon_days=3,
    )
    assert result.is_closing_soon


def test_closed_after_application_deadline():
    result = derive_job_status(
        start_date=date(2026, 8, 22),
        last_date=date(2026, 9, 11),
        today=TODAY,
    )
    assert result.status == CLOSED
    assert not result.is_closing_soon


def test_no_deadline_when_dates_are_missing():
    result = derive_job_status(start_date=None, last_date=None, today=TODAY)
    assert result.status == NO_DEADLINE


def test_new_today_is_based_on_notification_date():
    result = derive_job_status(
        start_date=date(2026, 9, 19),
        last_date=date(2026, 9, 30),
        notification_date=TODAY,
        today=TODAY,
    )
    assert result.is_new_today


def test_rejects_invalid_application_window():
    with pytest.raises(ValueError, match="cannot be after"):
        derive_job_status(
            start_date=date(2026, 10, 1),
            last_date=date(2026, 9, 30),
            today=TODAY,
        )
