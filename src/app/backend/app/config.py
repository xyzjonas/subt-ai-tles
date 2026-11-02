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
    # Translation cache: a dedicated cache-only Redis (evicts), NOT the Celery broker.
    cache_redis_url: str = "redis://localhost:6379/1"
    # Shared by web and worker so a re-run of an interrupted job is cheap. None: no expiry,
    # the instance's LRU eviction bounds the size.
    cache_ttl_seconds: int | None = None
    # Proxies in front of the app that append to X-Forwarded-For (the bundled nginx is one).
    # Set to 0 when the app is reachable directly, so the header is ignored.
    trusted_proxy_hops: int = 1
    # Public membership request form: submissions per hour per client, and across everyone.
    membership_request_ip_limit: int = 5
    membership_request_global_limit: int = 30


settings = Settings()
