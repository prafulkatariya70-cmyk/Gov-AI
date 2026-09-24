import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings


if os.getenv("VERCEL") == "1":
    # Vercel functions are short-lived/serverless. Avoid keeping a local
    # SQLAlchemy pool per warm function instance; Supabase's pooler handles
    # connection reuse across instances.
    engine = create_engine(
        settings.database_url,
        poolclass=NullPool,
        pool_pre_ping=True,
    )
else:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
    )


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
