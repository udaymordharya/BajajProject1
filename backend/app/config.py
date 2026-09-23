from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    google_project_id: str = ""
    google_client_email: str = ""
    google_private_key: str = ""
    google_sheet_id: str = ""
    google_sheet_range: str = "Sheet1!A:C"
    realtime_service_url: str = "http://localhost:3001"
    backend_api_key: str = ""
    sync_interval_seconds: float = 2
    frontend_origins: str = "http://localhost:5173"

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
