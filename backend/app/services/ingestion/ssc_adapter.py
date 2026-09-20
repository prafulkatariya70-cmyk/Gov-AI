from datetime import datetime
from urllib.parse import urljoin

import httpx

from app.services.ingestion.base_adapter import JobSourceAdapter
from app.services.ingestion.models import DiscoveredJob


SSC_BASE_URL = "https://ssc.gov.in/"
SSC_NOTICE_BOARD_URL = (
    "https://ssc.gov.in/home/notice-board"
)

SSC_API_URL = (
    "https://ssc.gov.in/api/general-website/portal/records"
)

MAX_PAGES_PER_RUN = 5
MAX_RETRIES = 3


class SSCAdapter(JobSourceAdapter):
    """
    Adapter for the official SSC Notice Board API.

    Responsibilities:
    - Fetch SSC notice-board records.
    - Filter irrelevant downstream notices.
    - Identify the opportunity type.
    - Extract notification metadata.
    - Convert SSC records into DiscoveredJob objects.
    """

    source_name = "SSC"

    def discover_jobs(self) -> list[DiscoveredJob]:
        jobs: list[DiscoveredJob] = []

        page = 1
        total_pages = 1

        timeout = httpx.Timeout(
            connect=30.0,
            read=60.0,
            write=30.0,
            pool=30.0,
        )

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/151.0 Safari/537.36"
            ),
            "Accept": "application/json",
            "Referer": SSC_NOTICE_BOARD_URL,
        }

        with httpx.Client(
            timeout=timeout,
            headers=headers,
            follow_redirects=True,
        ) as client:

            while (
                page <= total_pages
                and page <= MAX_PAGES_PER_RUN
            ):
                payload = self._fetch_page(
                    client,
                    page,
                )

                records = payload.get(
                    "data",
                    [],
                )

                pagination = payload.get(
                    "paginate",
                    {},
                )

                total_pages = int(
                    pagination.get(
                        "totalPage",
                        1,
                    )
                )

                for record in records:
                    job = self._parse_record(
                        record
                    )

                    if job is not None:
                        jobs.append(job)

                page += 1

        return jobs

    def _fetch_page(
        self,
        client: httpx.Client,
        page: int,
    ) -> dict:
        """
        Fetch one page from the SSC notice-board API.
        """

        params = {
            "page": page,
            "limit": 10,
            "contentType": "notice-boards",
            "key": "createdAt",
            "order": "DESC",
            "pageType": "filter",
            "isAttachment": "true",
            "attributes": (
                "id,headline,examId,contentType,"
                "redirectUrl,startDate,endDate,"
                "language,createdAt"
            ),
            "queryKey": "startDate,endDate",
            "customKey": "createdAt",
            "exams": "false",
            "date": "false",
            "language": "english",
        }

        last_error = None

        for attempt in range(
            1,
            MAX_RETRIES + 1,
        ):
            try:
                response = client.get(
                    SSC_API_URL,
                    params=params,
                )

                response.raise_for_status()

                return response.json()

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
            f"SSC API request failed after "
            f"{MAX_RETRIES} attempts "
            f"for page {page}: {last_error}"
        )

    def _parse_record(
        self,
        record: dict,
    ) -> DiscoveredJob | None:
        """
        Convert one SSC API record into a DiscoveredJob.
        """

        headline = (
            record.get("headline")
            or ""
        ).strip()

        if not headline:
            return None

        if not self._is_recruitment_notice(
            headline
        ):
            return None

        external_id = record.get("id")

        if not external_id:
            return None

        notification_url = (
            self._get_attachment_url(
                record
            )
        )

        if notification_url is None:
            return None

        opportunity_type = (
            self._classify_opportunity(
                headline
            )
        )

        created_at = self._parse_datetime(
            record.get("createdAt")
        )

        description = (
            f"SSC recruitment notice published "
            f"on {created_at.date().isoformat()}"
            if created_at
            else None
        )

        return DiscoveredJob(
            organization_name=(
                "Staff Selection Commission"
            ),
            title=headline,
            official_url=SSC_NOTICE_BOARD_URL,
            notification_url=notification_url,
            description=description,
            application_start=None,
            application_end=None,
            source_name=self.source_name,
            external_id=str(external_id),
            opportunity_type=opportunity_type,
        )

    def _classify_opportunity(
        self,
        headline: str,
    ) -> str:
        """
        Classify an SSC notice into a high-level
        opportunity type.

        Current supported types:
        - PUBLIC_RECRUITMENT
        - DEPUTATION
        """

        text = " ".join(
            headline.lower().split()
        )

        deputation_signals = [
            "deputation",
            "ex-cadre",
            "ex cadre",
        ]

        if any(
            signal in text
            for signal in deputation_signals
        ):
            return "DEPUTATION"

        return "PUBLIC_RECRUITMENT"

    def _is_recruitment_notice(
        self,
        headline: str,
    ) -> bool:
        """
        Determine whether an SSC notice represents
        a relevant recruitment opportunity.

        Downstream examination and administrative
        notices are excluded here.

        Classification such as PUBLIC_RECRUITMENT
        vs DEPUTATION happens separately.
        """

        text = " ".join(
            headline.lower().split()
        )

        excluded_keywords = [
            "answer key",
            "response sheet",
            "result",
            "corrigendum",
            "addendum",
            "tentative allocation",
            "allocation",
            "identity verification",
            "admit card",
            "departmental examination",
            "departmental examinations",
            "debarred",
            "final answer",
            "marks of",
            "shortlisting",
            "shortlisted",
            "final vacancies",
            "final vacancy",
            "tentative vacancies",
            "tentative vacancy",
            "vacancy position",
            "document verification",
            "physical endurance",
            "physical measurement",
            "physical standard",
            "pet/pst",
            "pst",
            "pe and mt",
            "trade test",
            "skill test",
            "typing test",
            "additional candidates",
            "candidates shortlisted",
            "recommended candidates",
            "withholding",
            "option-cum-preference",
            "option cum preference",
            "preference form",
            "schedule of examination",
            "schedule of examinations",
            "important notice - schedule",
            "cancellation notice",
        ]

        if any(
            keyword in text
            for keyword in excluded_keywords
        ):
            return False

        # Departmental competitive examinations
        # are intended for existing government
        # employees rather than normal public applicants.
        if "limited departmental competitive" in text:
            return False

        recruitment_signals = [
            "notice of",
            "recruitment",
            "online application",
            "application form",
            "submission of online application",
            "re-opening of window",
            "reopening of window",
            "filling up",
        ]

        return any(
            signal in text
            for signal in recruitment_signals
        )

    def _get_attachment_url(
        self,
        record: dict,
    ) -> str | None:
        """
        Build the official SSC notification URL
        from the attachment path supplied by the API.
        """

        attachments = record.get(
            "attachments"
        ) or []

        for attachment in attachments:

            if (
                attachment.get("type")
                != "application/pdf"
            ):
                continue

            path = attachment.get(
                "path"
            )

            if not path:
                continue

            normalized_path = (
                path.replace("\\", "/")
            )

            return urljoin(
                SSC_BASE_URL,
                normalized_path,
            )

        return None

    @staticmethod
    def _parse_datetime(
        value: str | None,
    ) -> datetime | None:
        """
        Parse SSC's ISO datetime value.
        """

        if not value:
            return None

        try:
            return datetime.fromisoformat(
                value.replace(
                    "Z",
                    "+00:00",
                )
            )

        except ValueError:
            return None