from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_MONTHLY_QUOTA = 1000


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./subtaitles.db"
    # Bootstrap admin, only used when the users table is empty.
    admin_username: str | None = None
    admin_password: str | None = None
    max_srt_bytes: int = 25 * 1024 * 1024
    # Celery broker.
    redis_url: str = "redis://localhost:6379/0"
    # Translation engine credentials. Model and temperature are app settings (database).
    openai_api_key: str | None = None
    openai_org_id: str | None = None
    # Shared by web and worker so a re-run of an interrupted job is cheap.
    srt_cache_dir: str | None = None


settings = Settings()
