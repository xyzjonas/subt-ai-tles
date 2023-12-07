import os

import deepl
from deepl import Translator
from subtaitles.translate.lang import LANG, Lang


def init() -> Translator:
    url = os.environ.get("DEEPL_AUTH_KEY")
    if not url:
        raise RuntimeError("DEEPL_AUTH_KEY is not set")

    return deepl.Translator(os.environ.get("DEEPL_AUTH_KEY"))


async def translate(items: list[str], lang_from: Lang, lang_to: Lang) -> list[str]:
    if lang_from.iso != "en":
        raise RuntimeError("Only english is available as a source lang for depl implementation.")

    translator = init()
    result = translator.translate_text("\n\n".join(items), target_lang=lang_to.iso).text
    return result.split("\n\n")
