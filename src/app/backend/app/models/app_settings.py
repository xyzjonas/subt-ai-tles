from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.config import DEFAULT_MONTHLY_QUOTA
from app.db import Base

SINGLETON_ID = 1


class AppSettings(Base):
    """Global settings, edited by admins at runtime. Always exactly one row."""

    __tablename__ = "app_settings"
    __table_args__ = (
        CheckConstraint(f"id = {SINGLETON_ID}", name="ck_app_settings_singleton"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, default=SINGLETON_ID)
    model: Mapped[str]
    temperature: Mapped[float]
    # Monthly credits a new user starts with.
    default_monthly_quota: Mapped[int] = mapped_column(
        default=DEFAULT_MONTHLY_QUOTA, server_default=str(DEFAULT_MONTHLY_QUOTA)
    )
