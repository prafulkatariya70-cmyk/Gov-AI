from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.api.eligibility import router as eligibility_router
from app.api.compatibility import router as compatibility_router
from app.db.session import engine
from app.services.ingestion.scheduler import (
    start_scheduler,
    stop_scheduler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.
    """

    # Start the government job ingestion scheduler.
    start_scheduler()

    yield

    # Stop the scheduler when FastAPI shuts down.
    stop_scheduler()


app = FastAPI(
    title="GovCareer AI API",
    description="AI-powered government career platform for India.",
    version="0.1.0",
    lifespan=lifespan,
)


app.include_router(eligibility_router)
app.include_router(compatibility_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to GovCareer AI API",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/health/database")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()

    return {
        "database": "connected",
        "test_result": value,
    }
