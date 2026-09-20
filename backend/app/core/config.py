from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_user: str
    database_password: str
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "govcareer"
    compatibility_development_user_email: str = "development@govcareer.local"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.database_user,
            password=self.database_password,
            host=self.database_host,
            port=self.database_port,
            database=self.database_name,
        )


settings = Settings()
