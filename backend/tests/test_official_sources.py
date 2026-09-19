from app.services.jobs.official_sources import OFFICIAL_SOURCE_REGISTRY


def test_initial_sources_are_official_and_unique():
    urls = [item["listing_url"] for item in OFFICIAL_SOURCE_REGISTRY]
    assert len(urls) == len(set(urls))
    assert all(url.startswith("https://") for url in urls)
    assert all(url.endswith("/") or ".gov.in/" in url or ".in/" in url for url in urls)
