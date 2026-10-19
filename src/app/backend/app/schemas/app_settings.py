from pydantic import Field

from app.models import TranslationModel
from app.schemas.base import CamelModel


class ModelOption(CamelModel):
    id: TranslationModel
    label: str
    description: str
    supports_temperature: bool
    input_credits_per_1k: float
    output_credits_per_1k: float


class AppSettingsIn(CamelModel):
    model: TranslationModel
    temperature: float = Field(ge=0, le=1)


class AppSettingsOut(CamelModel):
    model: TranslationModel
    temperature: float
    models: list[ModelOption]
