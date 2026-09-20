import re
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from app.services.ingestion.base_adapter import JobSourceAdapter
from app.services.ingestion.models import DiscoveredJob


KARNATAKA_TEACHER_BASE_URL = (
    "https://sts.karnataka.gov.in/GPSTRNHK/"
)

KARNATAKA_TEACHER_FINAL_URL = (
    "https://sts.karnataka.gov.in/GPSTRNHK/final.aspx"
)

KARNATAKA_TEACHER_SOURCE_NAME = "KARNATAKA_TEACHER"


class KarnatakaTeacherAdapter(JobSourceAdapter):
    """
    Adapter for the official Karnataka Teacher Recruitment portal.
    """

    source_name = KARNATAKA_TEACHER_SOURCE_NAME

    def discover_jobs(self) -> list[DiscoveredJob]:
        """
        Discover the current Karnataka teacher recruitment event.
        """

        html = self._fetch_page()

        job = self._parse_page(html)

        if job is None:
            return []

        return [job]

    def _fetch_page(self) -> str:
        """
        Fetch the official Karnataka teacher recruitment event page.
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
            "Referer": KARNATAKA_TEACHER_BASE_URL,
        }

        timeout = httpx.Timeout(
            connect=30.0,
            read=60.0,
            write=30.0,
            pool=30.0,
        )

        response = httpx.get(
            KARNATAKA_TEACHER_FINAL_URL,
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        )

        response.raise_for_status()

        return response.text

    def _parse_page(
        self,
        html: str,
    ) -> DiscoveredJob | None:
        """
        Parse the official Karnataka teacher recruitment event page.
        """

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        title = self._extract_title(soup)

        if not title:
            return None

        registration_start, registration_end = (
            self._extract_registration_window(soup)
        )

        if registration_start is None or registration_end is None:
            return None

        cycle = self._extract_cycle(soup)

        external_id = self._build_external_id(
            cycle=cycle,
        )

        description = self._build_description(
            soup=soup,
            title=title,
            registration_start=registration_start,
            registration_end=registration_end,
        )

        return DiscoveredJob(
            organization_name="Government of Karnataka",
            title=title,
            official_url=KARNATAKA_TEACHER_FINAL_URL,
            notification_url=None,
            description=description,
            application_start=registration_start.date(),
            application_end=registration_end.date(),
            source_name=self.source_name,
            external_id=external_id,
            opportunity_type="PUBLIC_RECRUITMENT",
        )

    @staticmethod
    def _extract_title(
        soup: BeautifulSoup,
    ) -> str | None:
        """
        Extract the recruitment title from the official page.
        """

        candidates: list[str] = []

        for element in soup.find_all(
            ["span", "div", "td", "h1", "h2", "h3"],
        ):
            text = element.get_text(
                " ",
                strip=True,
            )

            if not text:
                continue

            normalized = " ".join(
                text.split()
            )

            if "Teachers Recruitment" not in normalized:
                continue

            normalized = re.sub(
                r"\s+Government of Karnataka,\s*"
                r"Bengaluru\s*\.?$",
                "",
                normalized,
                flags=re.IGNORECASE,
            ).strip()

            if normalized:
                candidates.append(normalized)

        if not candidates:
            return None

        candidates.sort(
            key=len,
        )

        return candidates[0]

    @staticmethod
    def _extract_registration_window(
        soup: BeautifulSoup,
    ) -> tuple[datetime | None, datetime | None]:
        """
        Extract the Applicant Registration start/end values
        from the official event table.
        """

        table = soup.find(
            id="ContentPlaceHolder1_grd",
        )

        if table is None:
            return None, None

        for row in table.find_all("tr"):
            cells = row.find_all(
                ["td", "th"],
            )

            if len(cells) < 3:
                continue

            values = [
                " ".join(
                    cell.get_text(
                        " ",
                        strip=True,
                    ).split()
                )
                for cell in cells
            ]

            event_name = values[0].lower()

            if event_name != "applicant registration":
                continue

            start = KarnatakaTeacherAdapter._parse_datetime(
                values[1],
            )

            end = KarnatakaTeacherAdapter._parse_datetime(
                values[2],
            )

            return start, end

        return None, None

    @staticmethod
    def _parse_datetime(
        value: str,
    ) -> datetime | None:
        """
        Parse the official DD-MM-YYYY HH:MM format.
        """

        try:
            return datetime.strptime(
                value.strip(),
                "%d-%m-%Y %H:%M",
            )
        except ValueError:
            return None

    @staticmethod
    def _extract_cycle(
        soup: BeautifulSoup,
    ) -> str | None:
        """
        Extract the GSTR recruitment cycle when publicly available.
        """

        page_text = " ".join(
            soup.stripped_strings,
        )

        match = re.search(
            r"\bGSTR[-\s]?(\d{4})\b",
            page_text,
            flags=re.IGNORECASE,
        )

        if not match:
            return None

        return f"GSTR-{match.group(1)}"

    @staticmethod
    def _build_external_id(
        cycle: str | None,
    ) -> str:
        """
        Build a deterministic source-scoped identifier.

        If the public page exposes a GSTR cycle, use it.
        Otherwise use a stable source-level identifier.
        """

        if cycle:
            normalized_cycle = cycle.lower().replace(
                " ",
                "-",
            )

            return (
                "karnataka-gpsthrnhk-"
                f"{normalized_cycle}"
            )

        return "karnataka-gpsthrnhk-recruitment"

    @staticmethod
    def _build_description(
        soup: BeautifulSoup,
        title: str,
        registration_start: datetime,
        registration_end: datetime,
    ) -> str:
        """
        Build a concise description using only information
        available on the official page.
        """

        page_text = " ".join(
            soup.stripped_strings,
        )

        location = None

        location_match = re.search(
            r"Centralized Admission Cell,\s*"
            r"K\.G Road,\s*Bengaluru-\d+",
            page_text,
            flags=re.IGNORECASE,
        )

        if location_match:
            location = location_match.group(0)

        description = (
            f"{title}. "
            f"Applicant Registration: "
            f"{registration_start.strftime('%d-%m-%Y %H:%M')} "
            f"to "
            f"{registration_end.strftime('%d-%m-%Y %H:%M')}."
        )

        if location:
            description += f" {location}."

        return description