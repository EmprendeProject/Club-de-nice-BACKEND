from functools import lru_cache
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    gemini_api_key: str = ""
    redis_url: str = ""
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def is_redis_configured(self) -> bool:
        return bool(self.redis_url)

    def is_supabase_configured(self) -> bool:
        url = self.supabase_url
        key = self.supabase_service_role_key
        if not url or not key:
            return False
        if "your-project-id" in url or "your-service-role" in key:
            return False
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme == "https"
                and bool(parsed.hostname)
                and parsed.hostname.endswith(".supabase.co")
            )
        except Exception:
            return False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
