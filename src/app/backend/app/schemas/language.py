from app.schemas.base import CamelModel


class LanguageOut(CamelModel):
    code: str
    name: str
    native: str | None = None
    flag: str
