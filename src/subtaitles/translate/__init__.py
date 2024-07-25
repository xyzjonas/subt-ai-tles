import re
from enum import StrEnum

from .deepl import translate as deepl_translate
from .lang import Lang, LANG
from .libretranslate import translate as libre_translate
from .gpt import translate as gpt_translate


class Engine(StrEnum):
    LIBRE = "libre"
    DEEPL = "deepl"
    GPT = "gpt"
    GOOGLE = "google"


__engines = {
    Engine.LIBRE: libre_translate,
    Engine.DEEPL: deepl_translate,
    Engine.GPT: gpt_translate,
}


srt_markup_patterns = [
    re.compile(r"<.*?>"),
]


def strip_srt_markup(text: list[str]) -> list[str]:
    def __strip(token: str):
        stripped = token
        for pattern in srt_markup_patterns:
            stripped = re.sub(pattern, "", stripped)

        return stripped

    return [__strip(token) for token in text]


async def translate(text: list[str], source: Lang, target: Lang, engine: Engine = Engine.LIBRE) -> list[str]:
    # todo: validate len of response (skipped/merged items)
    match engine:
        case Engine.GOOGLE:
            raise NotImplementedError(f"{Engine.GOOGLE} model is not implemented on the backend yet!")

    stripped_text = strip_srt_markup(text)

    return await __engines[engine](stripped_text, source, target)
