from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile


class UserProfileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user_id(self, user_id: UUID) -> UserProfile | None:
        return self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        ).scalar_one_or_none()

    def upsert(self, user_id: UUID, values: dict) -> UserProfile:
        profile = self.get_by_user_id(user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id, **values)
            self.db.add(profile)
        else:
            for field, value in values.items():
                setattr(profile, field, value)
        self.db.commit()
        self.db.refresh(profile)
        return profile
