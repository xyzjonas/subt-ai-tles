from enum import Enum

from subtaitles.environment import env

from .gpt import GptTranslator
from .libretranslate import LibreTranslateTranslator
from .protocol import TranslateProtocol
from .pyd_ai import PydanticAiTranslator


class Engine(Enum):
    GPT = "gpt"
    LIBRE = "libre"
    PYDANTIC_AI = "pydantic-ai"


def get_translator(engine: Engine) -> TranslateProtocol:
    if engine == Engine.GPT:
        return GptTranslator()
    if engine == Engine.LIBRE:
        return LibreTranslateTranslator(env.LIBRETRANSLATE_API_URL())
    if engine == Engine.PYDANTIC_AI:
        return PydanticAiTranslator()

    msg = f"Unsupported translation engine: {engine}"
    raise ValueError(msg)
