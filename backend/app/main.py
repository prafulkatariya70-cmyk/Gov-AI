from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.profile import router as profile_router
from app.api.routes.auth import router as auth_router
from app.api.routes.application_tracker import router as tracker_router
from app.api.routes.sync import router as sync_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(tracker_router, prefix="/api/v1")
app.include_router(sync_router, prefix="/api/v1")
