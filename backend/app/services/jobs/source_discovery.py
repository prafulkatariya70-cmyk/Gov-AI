from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

@dataclass(frozen=True)
class DiscoveredNotification:
    pdf_url: str
    source_page_url: str
    label: str

class OfficialSourceDiscovery:
    """Discover PDF notification links from an official listing page.

    This deliberately does not crawl beyond the supplied official page.
    """
    def __init__(self, *, timeout_seconds: int = 20):
        self.timeout_seconds = timeout_seconds

    def discover(self, listing_url: str) -> list[DiscoveredNotification]:
        parsed = urlparse(listing_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Listing URL must be an absolute HTTP(S) URL.")
        response = requests.get(
            listing_url,
            timeout=self.timeout_seconds,
            headers={"User-Agent": "GovCareerAI-SourceDiscovery/1.0"},
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results: list[DiscoveredNotification] = []
        seen: set[str] = set()
        for anchor in soup.find_all("a", href=True):
            href = str(anchor.get("href", "")).strip()
            absolute = urljoin(listing_url, href)
            if not absolute.lower().split("?", 1)[0].endswith(".pdf"):
                continue
            if absolute in seen:
                continue
            seen.add(absolute)
            label = anchor.get_text(" ", strip=True) or absolute.rsplit("/", 1)[-1]
            results.append(DiscoveredNotification(absolute, listing_url, label))
        return results
