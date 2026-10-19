from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Language(Base):
    __tablename__ = "languages"

    code: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    native: Mapped[str | None]
    flag: Mapped[str]
