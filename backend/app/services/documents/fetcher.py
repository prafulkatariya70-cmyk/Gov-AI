from __future__ import annotations

import hashlib
from dataclasses import dataclass
from urllib.parse import urlparse

import requests


@dataclass(frozen=True)
class FetchedDocument:
    url: str
    content: bytes
    content_type: str
    content_hash: str


class DocumentFetcher:
    """Fetch an official notification document with bounded network behavior."""

    def __init__(self, *, timeout_seconds: int = 30, max_bytes: int = 20 * 1024 * 1024) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_bytes = max_bytes

    def fetch(self, url: str) -> FetchedDocument:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Document URL must be an absolute HTTP(S) URL.")

        response = requests.get(
            url,
            timeout=self.timeout_seconds,
            headers={"User-Agent": "GovCareerAI-DocumentFetcher/1.0"},
            stream=True,
        )
        response.raise_for_status()

        chunks: list[bytes] = []
        total = 0
        for chunk in response.iter_content(chunk_size=1024 * 256):
            if not chunk:
                continue
            total += len(chunk)
            if total > self.max_bytes:
                raise ValueError(f"Document exceeds maximum allowed size of {self.max_bytes} bytes.")
            chunks.append(chunk)

        content = b"".join(chunks)
        return FetchedDocument(
            url=url,
            content=content,
            content_type=response.headers.get("content-type", "").split(";", 1)[0].strip().lower(),
            content_hash=hashlib.sha256(content).hexdigest(),
        )
