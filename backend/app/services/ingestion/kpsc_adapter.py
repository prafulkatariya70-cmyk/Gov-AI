from __future__ import annotations

import re
from datetime import date, datetime
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.services.documents.extractor import PDFTextExtractor
from app.services.documents.fetcher import DocumentFetcher
from app.services.ingestion.base_adapter import JobSourceAdapter
from app.services.ingestion.models import DiscoveredJob


KPSC_BASE_URL = "https://kpsc.kar.nic.in/"
KPSC_NOTIFICATION_URL = (
    "https://kpsc.kar.nic.in/notification.html"
)
KPSC_SOURCE_NAME = "KPSC"

MAX_NOTIFICATION_LINKS = 20

EXCLUDED_SIGNALS = (
    "corrigendum",
    "addendum",
    "result",
    "answer key",
    "key answers",
    "admit card",
    "hall ticket",
    "timetable",
    "time table",
    "syllabus",
    "departmental examination",
    "departmental examinations",
    "selection list",
    "select list",
    "marks list",
    "cut off",
    "cutoff",
    "press note",
    "press release",
    "withdrawal",
    "cancellation",
    "provisional list",
    "eligibility list",
)

RECRUITMENT_SIGNALS = (
    "notification",
    "recruitment",
    "direct recruitment",
    "posts",
    "vacancies",
    "vacancy",
    "assistant controller",
    "audit officer",
    "gazetted probationer",
)


class KPSCAdapter(JobSourceAdapter):
    """
    Adapter for Karnataka Public Service Commission recruitment
    notifications.

    Discovery is intentionally limited to the official KPSC
    notification archive. Each candidate PDF is fetched and parsed
    before it is converted into a DiscoveredJob.
    """

    source_name = KPSC_SOURCE_NAME

    def discover_jobs(self) -> list[DiscoveredJob]:
        html = self._fetch_notification_page()
        links = self._extract_notification_links(html)

        discovered_jobs: list[DiscoveredJob] = []

        for notification_url, anchor_text in links:
            job = self._parse_notification(
                notification_url=notification_url,
                anchor_text=anchor_text,
            )

            if job is not None:
                discovered_jobs.append(job)

        return discovered_jobs

    def _fetch_notification_page(self) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/151.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
            "Referer": KPSC_BASE_URL,
        }

        timeout = httpx.Timeout(
            connect=30.0,
            read=60.0,
            write=30.0,
            pool=30.0,
        )

        response = httpx.get(
            KPSC_NOTIFICATION_URL,
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        )
        response.raise_for_status()
        return response.text

    def _extract_notification_links(
        self,
        html: str,
    ) -> list[tuple[str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        candidates: list[tuple[str, str]] = []
        seen_urls: set[str] = set()

        for anchor in soup.find_all("a", href=True):
            href = str(anchor.get("href") or "").strip()
            text = " ".join(
                anchor.get_text(" ", strip=True).split()
            )

            if not href or not text:
                continue

            normalized = f"{text} {href}".lower()

            if "2026" not in normalized:
                continue

            if any(signal in normalized for signal in EXCLUDED_SIGNALS):
                continue

            if not any(
                signal in normalized
                for signal in RECRUITMENT_SIGNALS
            ):
                continue

            absolute_url = urljoin(
                KPSC_NOTIFICATION_URL,
                href,
            )

            if not absolute_url.lower().endswith(".pdf"):
                continue

            if absolute_url in seen_urls:
                continue

            seen_urls.add(absolute_url)
            candidates.append((absolute_url, text))

            if len(candidates) >= MAX_NOTIFICATION_LINKS:
                break

        return candidates

    def _parse_notification(
        self,
        notification_url: str,
        anchor_text: str,
    ) -> DiscoveredJob | None:
        fetcher = DocumentFetcher()
        fetched = fetcher.fetch(notification_url)

        if not fetched.success or not fetched.content:
            return None

        extractor = PDFTextExtractor()
        extracted = extractor.extract(fetched.content)

        if not extracted.success or not extracted.text:
            return None

        text = extracted.text

        if self._is_excluded_notification(text):
            return None

        application_start, application_end = (
            self._extract_application_window(text)
        )

        if application_start is None and application_end is None:
            return None

        notification_number = self._extract_notification_number(text)

        title = self._extract_title(
            text=text,
            anchor_text=anchor_text,
            notification_number=notification_number,
        )

        if not title:
            return None

        external_id = (
            notification_number
            or self._build_url_id(notification_url)
        )

        description = self._build_description(
            text=text,
            title=title,
            notification_number=notification_number,
        )

        return DiscoveredJob(
            organization_name=(
                "Karnataka Public Service Commission"
            ),
            title=title,
            official_url=KPSC_NOTIFICATION_URL,
            notification_url=notification_url,
            description=description,
            application_start=application_start,
            application_end=application_end,
            source_name=self.source_name,
            external_id=external_id,
            opportunity_type="PUBLIC_RECRUITMENT",
        )

    @staticmethod
    def _is_excluded_notification(text: str) -> bool:
        normalized = " ".join(text.lower().split())

        return any(
            signal in normalized
            for signal in EXCLUDED_SIGNALS
        )

    @staticmethod
    def _extract_notification_number(
        text: str,
    ) -> str | None:
        patterns = (
            r"\bKPSCKA/[A-Z0-9/.-]+\b",
            r"\bKPSC[A-Z0-9/.-]{8,}\b",
        )

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if match:
                return " ".join(
                    match.group(0).split()
                ).rstrip(".,;")

        return None

    @staticmethod
    def _extract_application_window(
        text: str,
    ) -> tuple[date | None, date | None]:
        normalized = " ".join(text.split())

        date_pattern = (
            r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})"
        )

        patterns = (
            rf"(?:from|w\.e\.f\.?|online applications? "
            rf"(?:are|is)?\s*(?:invited|open)?[^0-9]{{0,120}})"
            rf"({date_pattern})[^0-9]{{0,120}}"
            rf"(?:to|till|upto|up to|last date)[^0-9]{{0,40}}"
            rf"({date_pattern})",

            rf"(?:online application|application)[^0-9]{{0,120}}"
            rf"({date_pattern})[^0-9]{{0,100}}"
            rf"({date_pattern})",
        )

        for pattern in patterns:
            match = re.search(
                pattern,
                normalized,
                flags=re.IGNORECASE,
            )

            if not match:
                continue

            dates = re.findall(
                date_pattern,
                match.group(0),
            )

            if len(dates) < 2:
                continue

            start = KPSCAdapter._to_date(dates[0])
            end = KPSCAdapter._to_date(dates[1])

            if start and end and start <= end:
                return start, end

        return None, None

    @staticmethod
    def _to_date(
        parts: tuple[str, str, str],
    ) -> date | None:
        try:
            return date(
                int(parts[2]),
                int(parts[1]),
                int(parts[0]),
            )
        except ValueError:
            return None

    @staticmethod
    def _extract_title(
        text: str,
        anchor_text: str,
        notification_number: str | None,
    ) -> str | None:
        lines = [
            " ".join(line.split())
            for line in text.splitlines()
            if line.strip()
        ]

        recruitment_keywords = (
            "recruitment",
            "gazetted probationer",
            "assistant controller",
            "audit officer",
            "posts",
            "vacancies",
        )

        for line in lines[:120]:
            normalized = line.lower()

            if len(line) < 15 or len(line) > 220:
                continue

            if notification_number and normalized == notification_number.lower():
                continue

            if any(
                keyword in normalized
                for keyword in recruitment_keywords
            ):
                cleaned = re.sub(
                    r"^notification\s*[:.-]?\s*",
                    "",
                    line,
                    flags=re.IGNORECASE,
                ).strip()

                if cleaned:
                    return cleaned

        cleaned_anchor = " ".join(anchor_text.split())

        if cleaned_anchor:
            cleaned_anchor = re.sub(
                r"\s*\(.*?\)\s*$",
                "",
                cleaned_anchor,
            ).strip()

            return cleaned_anchor

        return None

    @staticmethod
    def _build_description(
        text: str,
        title: str,
        notification_number: str | None,
    ) -> str:
        normalized = " ".join(text.split())

        vacancy_match = re.search(
            r"\b(?:total\s+)?(?:number\s+of\s+)?"
            r"(?:posts|vacancies)\s*[:=-]?\s*(\d{1,5})\b",
            normalized,
            flags=re.IGNORECASE,
        )

        description = title

        if notification_number:
            description += f". Notification: {notification_number}."

        if vacancy_match:
            description += (
                f" Total posts/vacancies: "
                f"{vacancy_match.group(1)}."
            )

        return description

    @staticmethod
    def _build_url_id(url: str) -> str:
        filename = url.rstrip("/").rsplit("/", 1)[-1]
        filename = re.sub(
            r"\.pdf$",
            "",
            filename,
            flags=re.IGNORECASE,
        )
        normalized = re.sub(
            r"[^a-z0-9]+",
            "-",
            filename.lower(),
        ).strip("-")

        return (
            f"kpsc-{normalized}"
            if normalized
            else "kpsc-notification"
        )
