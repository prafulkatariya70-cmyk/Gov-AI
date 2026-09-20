from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.services.ingestion.base_adapter import JobSourceAdapter
from app.services.ingestion.models import DiscoveredJob


UPSC_BASE_URL = "https://www.upsc.gov.in/"

UPSC_RECRUITMENT_URL = (
    "https://www.upsc.gov.in/recruitment/recruitment-advertisement"
)


class UPSCAdapter(JobSourceAdapter):
    """
    Adapter for UPSC recruitment advertisements.

    Responsibilities:
    - Fetch the official UPSC recruitment advertisement page.
    - Identify recruitment advertisement entries.
    - Extract the advertisement title.
    - Extract the official notification/PDF URL.
    - Convert entries into DiscoveredJob objects.
    """

    source_name = "UPSC"

    def discover_jobs(self) -> list[DiscoveredJob]:
        """
        Discover current UPSC recruitment advertisements.
        """

        html = self._fetch_page()

        return self._parse_page(html)

    def _fetch_page(self) -> str:
        """
        Fetch the official UPSC recruitment advertisement page.
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
        }

        response = httpx.get(
            UPSC_RECRUITMENT_URL,
            headers=headers,
            timeout=30.0,
            follow_redirects=True,
        )

        response.raise_for_status()

        return response.text

    def _parse_page(
        self,
        html: str,
    ) -> list[DiscoveredJob]:
        """
        Parse UPSC recruitment advertisement entries.

        The current UPSC page places the advertisement title
        inside an <li>, while the PDF URL is inside an <a>
        nested within that <li>.
        """

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        discovered_jobs: list[DiscoveredJob] = []

        for list_item in soup.find_all("li"):

            text = list_item.get_text(
                " ",
                strip=True,
            )

            if not text:
                continue

            normalized_text = " ".join(
                text.lower().split()
            )

            if "advertisement no." not in normalized_text:
                continue

            link = list_item.find(
                "a",
                href=True,
            )

            if link is None:
                continue

            href = link.get("href")

            if not href:
                continue

            notification_url = urljoin(
                UPSC_BASE_URL,
                href,
            )

            title = self._clean_title(
                text
            )

            external_id = self._extract_external_id(
                title
            )

            discovered_jobs.append(
                DiscoveredJob(
                    organization_name=(
                        "Union Public Service Commission"
                    ),
                    title=title,
                    official_url=UPSC_RECRUITMENT_URL,
                    notification_url=notification_url,
                    source_name=self.source_name,
                    external_id=external_id,
                    opportunity_type="PUBLIC_RECRUITMENT",
                )
            )

        return discovered_jobs

    @staticmethod
    def _clean_title(
        text: str,
    ) -> str:
        """
        Remove the PDF file-size text from the
        advertisement title.

        Example:
            Advertisement No.52 - 2026 (Special) (1.49 MB)

        becomes:
            Advertisement No.52 - 2026 (Special)
        """

        title = " ".join(
            text.split()
        )

        if "(" in title:
            parts = title.rsplit(
                "(",
                1,
            )

            possible_size = parts[-1].strip()

            if possible_size.lower().endswith(
                "mb)"
            ) or possible_size.lower().endswith(
                "kb)"
            ):
                title = parts[0].strip()

        return title

    @staticmethod
    def _extract_external_id(
        title: str,
    ) -> str | None:
        """
        Extract the UPSC advertisement number.

        Example:
            Advertisement No.52 - 2026 (Special)

        becomes:
            52-2026
        """

        normalized = " ".join(
            title.split()
        )

        marker = "Advertisement No."

        marker_index = normalized.lower().find(
            marker.lower()
        )

        if marker_index == -1:
            return None

        value = normalized[
            marker_index + len(marker):
        ].strip()

        if not value:
            return None

        return value