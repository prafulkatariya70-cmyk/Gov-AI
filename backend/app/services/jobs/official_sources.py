from __future__ import annotations
from sqlalchemy.orm import Session
from app.models.job_source_registry import JobSourceRegistry
OFFICIAL_SOURCE_REGISTRY=(
 {"organization":"Union Public Service Commission","listing_url":"https://www.upsc.gov.in/recruitment/recruitment-advertisement","source_type":"official_listing"},
 {"organization":"Union Public Service Commission","listing_url":"https://www.upsc.gov.in/recruitment/recruitment-test/notices","source_type":"official_listing"},
 {"organization":"Institute of Banking Personnel Selection","listing_url":"https://www.ibps.in/index.php/recruitment/","source_type":"official_listing"},
)
def seed_official_sources(db: Session)->int:
    created=0
    for values in OFFICIAL_SOURCE_REGISTRY:
        if db.query(JobSourceRegistry).filter(JobSourceRegistry.listing_url==values["listing_url"]).one_or_none() is None:
            db.add(JobSourceRegistry(**values)); created+=1
    if created: db.commit()
    return created
