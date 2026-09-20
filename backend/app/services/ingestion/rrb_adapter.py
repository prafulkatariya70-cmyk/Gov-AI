from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.services.ingestion.base_adapter import JobSourceAdapter
from app.services.ingestion.models import DiscoveredJob


RRB_BASE_URL = "https://rrbbbs.gov.in/"

RRB_CEN_URL = (
    "https://rrbbbs.gov.in/notifications.php"
)

MAX_RETRIES = 3


class RRBAdapter(JobSourceAdapter):
    """
    Adapter for Railway Recruitment Board recruitment
    notifications.

    The RRB ecosystem publishes Centralised Employment
    Notices (CENs) for recruitment opportunities.

    This adapter currently uses the official RRB
    Bhubaneswar recruitment notification page as the
    first supported RRB source.

    The adapter is intentionally isolated from the
    ingestion pipeline so additional RRB regional
    sources can be added later without changing the
    persistence layer.
    """

    source_name = "RRB"

    def discover_jobs(self) -> list[DiscoveredJob]:
        """
        Discover current RRB CEN recruitment notices.
        """

        html = self._fetch_page()

        return self._parse_page(html)

    def _fetch_page(self) -> str:
        """
        Fetch the official RRB recruitment page.
        """

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
            "Referer": RRB_BASE_URL,
        }

        timeout = httpx.Timeout(
            connect=30.0,
            read=60.0,
            write=30.0,
            pool=30.0,
        )

        last_error = None

        for attempt in range(
            1,
            MAX_RETRIES + 1,
        ):
            try:
                response = httpx.get(
                    RRB_CEN_URL,
                    headers=headers,
                    timeout=timeout,
                    follow_redirects=True,
                )

                response.raise_for_status()

                return response.text

            except (
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.ConnectError,
                httpx.RemoteProtocolError,
            ) as exc:

                last_error = exc

                if attempt < MAX_RETRIES:
                    continue

        raise RuntimeError(
            "RRB recruitment page request failed "
            f"after {MAX_RETRIES} attempts: "
            f"{last_error}"
        )

    def _parse_page(
        self,
        html: str,
    ) -> list[DiscoveredJob]:
        """
        Parse the official RRB CEN notification page.
        """

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        discovered_jobs: list[DiscoveredJob] = []

        seen_cens: set[str] = set()

        # RRB currently exposes recruitment CENs in
        # a table containing date, CEN number, title,
        # posts and current status.
        for row in soup.find_all("tr"):

            cells = row.find_all(
                ["td", "th"]
            )

            if len(cells) < 3:
                continue

            cell_text = [
                cell.get_text(
                    " ",
                    strip=True,
                )
                for cell in cells
            ]

            row_text = " ".join(cell_text)

            cen_number = self._extract_cen_number(
                row_text
            )

            if not cen_number:
                continue

            # We only want recruitment CEN records,
            # not arbitrary notices/results.
            if not self._is_recruitment_cen(
                row_text
            ):
                continue

            if cen_number in seen_cens:
                continue

            title = self._extract_title(
                cell_text
            )

            if not title:
                title = f"Railway Recruitment {cen_number}"

            notification_url = (
                self._extract_notification_url(
                    row
                )
            )

            if notification_url is None:
                notification_url = RRB_CEN_URL

            posts = self._extract_posts(
                cell_text
            )

            description = self._build_description(
                cen_number=cen_number,
                title=title,
                posts=posts,
            )

            discovered_jobs.append(
                DiscoveredJob(
                    organization_name=(
                        "Railway Recruitment Boards"
                    ),
                    title=title,
                    official_url=RRB_BASE_URL,
                    notification_url=notification_url,
                    description=description,
                    application_start=None,
                    application_end=None,
                    source_name=self.source_name,
                    external_id=cen_number,
                    opportunity_type=(
                        "PUBLIC_RECRUITMENT"
                    ),
                )
            )

            seen_cens.add(cen_number)

        return discovered_jobs

    @staticmethod
    def _extract_cen_number(
        text: str,
    ) -> str | None:
        """
        Extract a normalized CEN identifier.

        Examples:

            CEN 03/2026
            CEN 09/2025
            CEN 01/2026
        """

        match = re.search(
            r"\bCEN\s*([0-9]{1,3})\s*/\s*([0-9]{4})\b",
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            return None

        number = match.group(1).zfill(2)
        year = match.group(2)

        return f"CEN {number}/{year}"

    @staticmethod
    def _is_recruitment_cen(
        text: str,
    ) -> bool:
        """
        Determine whether a row represents a
        recruitment CEN rather than a downstream
        examination/result/update notice.
        """

        normalized = " ".join(
            text.lower().split()
        )

        excluded_signals = [
            "result",
            "cut off",
            "cutoff",
            "answer key",
            "response sheet",
            "document verification",
            "medical examination",
            "city intimation",
            "e-call letter",
            "call letter",
            "corrigendum",
            "mock test",
            "schedule of cbt",
            "revised schedule",
            "objection",
            "shortlisted",
            "shortlisting",
            "final panel",
            "panel",
            "marks",
            "exam date",
        ]

        if any(
            signal in normalized
            for signal in excluded_signals
        ):
            return False

        recruitment_signals = [
            "recruitment",
            "posts",
            "section controller",
            "technician",
            "assistant loco pilot",
            "level 1",
            "junior engineer",
            "depot material",
            "chemical",
            "metallurgical",
            "isolated category",
        ]

        return any(
            signal in normalized
            for signal in recruitment_signals
        )

    @staticmethod
    def _extract_title(
        cells: list[str],
    ) -> str | None:
        """
        Extract the recruitment title.

        The current RRB table structure places the
        recruitment title after the CEN number.
        """

        for value in cells:

            cleaned = value.strip()

            if not cleaned:
                continue

            if re.search(
                r"\bCEN\s*[0-9]{1,3}\s*/\s*[0-9]{4}\b",
                cleaned,
                flags=re.IGNORECASE,
            ):
                continue

            if re.match(
                r"^\d{2}-\d{2}-\d{4}$",
                cleaned,
            ):
                continue

            if cleaned.lower() in {
                "new",
                "current",
                "status",
            }:
                continue

            return cleaned

        return None

    @staticmethod
    def _extract_posts(
        cells: list[str],
    ) -> str | None:
        """
        Extract the posts column when available.
        """

        if len(cells) >= 4:
            posts = cells[3].strip()

            if posts:
                return posts

        return None

    @staticmethod
    def _extract_notification_url(
        row,
    ) -> str | None:
        """
        Extract the official notification/detail URL
        from links in the CEN row.
        """

        for link in row.find_all(
            "a",
            href=True,
        ):
            href = link.get("href")

            if not href:
                continue

            href_text = link.get_text(
                " ",
                strip=True,
            ).lower()

            href_lower = href.lower()

            if (
                "cen" in href_text
                or "notification" in href_lower
                or "cen.php" in href_lower
                or "documentexplorer" in href_lower
            ):
                return urljoin(
                    RRB_BASE_URL,
                    href,
                )

        return None

    @staticmethod
    def _build_description(
        cen_number: str,
        title: str,
        posts: str | None,
    ) -> str:
        """
        Build a concise normalized description.
        """

        description = (
            f"{cen_number}: {title}"
        )

        if posts:
            description += (
                f". Posts: {posts}"
            )

        return description