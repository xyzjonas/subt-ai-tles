from enum import Enum

# from subtaitles.environment import env
from .openai import OpenAiTranslator

# from .libretranslate import LibreTranslateTranslator
from .protocol import TranslateProtocol


class Engine(Enum):
    OPEN_AI = "openai"
    # LIBRE = "libre"


def get_translator(engine: Engine) -> TranslateProtocol:
    if engine == Engine.OPEN_AI:
        return OpenAiTranslator()
    # if engine == Engine.LIBRE:
    #     return LibreTranslateTranslator(env.LIBRETRANSLATE_API_URL())

    msg = f"Unsupported translation engine: {engine}"
    raise ValueError(msg)
