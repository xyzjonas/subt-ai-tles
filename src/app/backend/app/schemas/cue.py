from app.schemas.base import CamelModel


class CueOut(CamelModel):
    index: int
    start: int
    end: int
    source: str
    target: str


class CueUpdate(CamelModel):
    target: str


class CueVariant(CamelModel):
    label: str
    text: str


class RetranslateRequest(CamelModel):
    prompt: str | None = None
