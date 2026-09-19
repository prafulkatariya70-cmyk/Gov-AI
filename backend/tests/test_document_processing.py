from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import fitz

from app.core.database import Base
from app.services.documents.fetcher import FetchedDocument
from app.services.documents.processing import NotificationProcessingService


TEXT = """Staff Selection Commission (HQ)\nRecruitment to the post of Accounts Officer.\nApplications are invited for 4 posts.\nAge limit: 21 to 56 years.\nFive years' experience in Cash, Accounts and Budget work.\nCandidates should have experience in government service.\nThe post is at Pay Level-7.\n"""


def make_pdf() -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((50, 70), TEXT, fontsize=12)
    content = document.tobytes()
    document.close()
    return content


def test_processing_pipeline_extracts_parses_and_persists():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    db = Session(engine)

    class FakeFetcher:
        def fetch(self, url):
            content = make_pdf()
            import hashlib
            return FetchedDocument(url, content, "application/pdf", hashlib.sha256(content).hexdigest())

    try:
        service = NotificationProcessingService(db, fetcher=FakeFetcher())
        result = service.process(
            notification_pdf_url="https://ssc.gov.in/accounts-officer.pdf",
            official_source_url="https://ssc.gov.in/accounts-officer",
        )
        assert result.extraction_method == "native_pdf_text"
        assert result.page_count == 1
        assert result.extracted_text_length > 100
        assert db.query(__import__("app.models", fromlist=["Job"]).Job).count() == 1
    finally:
        db.close()
