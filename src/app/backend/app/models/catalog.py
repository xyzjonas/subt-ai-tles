"""The curated list of translation models the app offers (rates live in `model_rates`)."""

from dataclasses import dataclass
from enum import StrEnum


class TranslationModel(StrEnum):
    GPT_4_1_NANO = "gpt-4.1-nano"
    GPT_5_NANO = "gpt-5-nano"
    GPT_6_LUNA = "gpt-6-luna"


DEFAULT_MODEL = TranslationModel.GPT_4_1_NANO
DEFAULT_TEMPERATURE = 0.0


@dataclass(frozen=True)
class ModelInfo:
    label: str
    description: str
    # Models that manage their own randomness reject (or ignore) a temperature.
    supports_temperature: bool


MODEL_INFO: dict[TranslationModel, ModelInfo] = {
    TranslationModel.GPT_4_1_NANO: ModelInfo(
        label="GPT-4.1 nano",
        description="Fast and inexpensive. A dependable all-rounder for everyday subtitles.",
        supports_temperature=True,
    ),
    TranslationModel.GPT_5_NANO: ModelInfo(
        label="GPT-5 nano",
        description="The cheapest option. It thinks a little before answering, which can help "
        "with tricky phrasing.",
        supports_temperature=False,
    ),
    TranslationModel.GPT_6_LUNA: ModelInfo(
        label="GPT-6 luna",
        description="The newest small model. Costs a little more, with the latest "
        "improvements.",
        supports_temperature=False,
    ),
}
