from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./subtaitles.db"
    # Bootstrap admin, only used when the users table is empty.
    admin_username: str | None = None
    admin_password: str | None = None
    max_srt_bytes: int = 25 * 1024 * 1024


settings = Settings()
