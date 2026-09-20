from dataclasses import dataclass


import httpx


SSC_ATTACHMENT_PREFIX = "/api/attachment/"


@dataclass
class DocumentFetchResult:
    """
    Result of fetching an official government document.
    """

    success: bool

    status_code: int | None = None

    content_type: str | None = None

    final_url: str | None = None

    content: bytes | None = None

    error: str | None = None

    is_pdf: bool = False


class DocumentFetcher:
    """
    Fetches government notification documents.

    SSC requires attachment URLs to be accessed through:

        /api/attachment/uploads/...

    rather than directly through:

        /uploads/...
    """

    def __init__(
        self,
        timeout: float = 60.0,
    ) -> None:

        self.timeout = timeout

    def fetch(
        self,
        url: str,
    ) -> DocumentFetchResult:

        normalized_url = self._normalize_url(
            url
        )

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/151.0 Safari/537.36"
            ),
            "Accept": (
                "application/pdf,"
                "application/octet-stream,"
                "text/html;q=0.8"
            ),
            "Referer": "https://ssc.gov.in/",
        }

        try:
            with httpx.Client(
                timeout=self.timeout,
                follow_redirects=True,
                headers=headers,
            ) as client:

                response = client.get(
                    normalized_url
                )

                content_type = (
                    response.headers.get(
                        "content-type"
                    )
                )

                content = response.content

                is_pdf = self._is_pdf(
                    content,
                    content_type,
                )

                if not is_pdf:
                    return DocumentFetchResult(
                        success=False,
                        status_code=response.status_code,
                        content_type=content_type,
                        final_url=str(
                            response.url
                        ),
                        content=None,
                        error=(
                            "Response is not a valid PDF."
                        ),
                        is_pdf=False,
                    )

                response.raise_for_status()

                return DocumentFetchResult(
                    success=True,
                    status_code=response.status_code,
                    content_type=content_type,
                    final_url=str(
                        response.url
                    ),
                    content=content,
                    error=None,
                    is_pdf=True,
                )

        except httpx.HTTPStatusError as exc:

            return DocumentFetchResult(
                success=False,
                status_code=(
                    exc.response.status_code
                    if exc.response
                    else None
                ),
                content_type=(
                    exc.response.headers.get(
                        "content-type"
                    )
                    if exc.response
                    else None
                ),
                final_url=(
                    str(exc.response.url)
                    if exc.response
                    else normalized_url
                ),
                content=None,
                error=str(exc),
                is_pdf=False,
            )

        except httpx.HTTPError as exc:

            return DocumentFetchResult(
                success=False,
                status_code=None,
                content_type=None,
                final_url=normalized_url,
                content=None,
                error=str(exc),
                is_pdf=False,
            )

        except Exception as exc:

            return DocumentFetchResult(
                success=False,
                status_code=None,
                content_type=None,
                final_url=normalized_url,
                content=None,
                error=str(exc),
                is_pdf=False,
            )

    @staticmethod
    def _normalize_url(
        url: str,
    ) -> str:
        """
        Convert SSC's public attachment path:

            /uploads/masterData/...

        into SSC's actual attachment endpoint:

            /api/attachment/uploads/masterData/...
        """

        if not url:
            return url

        if "ssc.gov.in" not in url:
            return url

        marker = "/uploads/"

        if marker not in url:
            return url

        if "/api/attachment/uploads/" in url:
            return url

        return url.replace(
            marker,
            SSC_ATTACHMENT_PREFIX + "uploads/",
            1,
        )

    @staticmethod
    def _is_pdf(
        content: bytes,
        content_type: str | None,
    ) -> bool:
        """
        Validate the actual file bytes.

        A valid PDF begins with:

            %PDF-
        """

        if not content:
            return False

        return content.startswith(
            b"%PDF-"
        )