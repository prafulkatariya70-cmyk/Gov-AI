from app.services.jobs.official_sources import OFFICIAL_SOURCE_REGISTRY, seed_official_sources


def test_official_source_registry_contains_only_expected_official_listing_sources():
    assert len(OFFICIAL_SOURCE_REGISTRY) == 3
    assert all(item["source_type"] == "official_listing" for item in OFFICIAL_SOURCE_REGISTRY)
    assert all(item["listing_url"].startswith("https://") for item in OFFICIAL_SOURCE_REGISTRY)
    assert any(item["organization"] == "Union Public Service Commission" for item in OFFICIAL_SOURCE_REGISTRY)
    assert any(item["organization"] == "Institute of Banking Personnel Selection" for item in OFFICIAL_SOURCE_REGISTRY)


def test_seed_official_sources_is_idempotent():
    class FakeQuery:
        def __init__(self, rows):
            self.rows = rows

        def filter(self, *args):
            return self

        def one_or_none(self):
            return None

    class FakeDB:
        def __init__(self):
            self.added = []
            self.commits = 0

        def query(self, *args):
            return FakeQuery(self.added)

        def add(self, value):
            self.added.append(value)

        def commit(self):
            self.commits += 1

    db = FakeDB()
    created = seed_official_sources(db)
    assert created == len(OFFICIAL_SOURCE_REGISTRY)
    assert len(db.added) == len(OFFICIAL_SOURCE_REGISTRY)
    assert db.commits == 1
