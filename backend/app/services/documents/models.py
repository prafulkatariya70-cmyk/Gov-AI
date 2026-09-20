from dataclasses import dataclass


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