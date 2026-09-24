import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings


if os.getenv("VERCEL") == "1":
    # Vercel functions are short-lived/serverless. Supabase recommends the
    # transaction pooler for this workload; disable psycopg prepared
    # statements because transaction pooling does not support them.
    engine = create_engine(
        settings.database_url,
        poolclass=NullPool,
        pool_pre_ping=True,
        connect_args={
            "prepare_threshold": None,
            "sslmode": "require",
        },
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
