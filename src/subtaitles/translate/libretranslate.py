import os

from libretranslatepy import LibreTranslateAPI

from subtaitles.translate import Lang


def init() -> LibreTranslateAPI:
    url = os.environ.get("LIBRETRANSLATE_BASE_URL")
    if not url:
        raise RuntimeError("LIBRETRANSLATE_BASE_URL is not set")

    return LibreTranslateAPI(os.environ.get("LIBRETRANSLATE_BASE_URL"))


async def translate(items: list[str], lang_from: Lang, lang_to: Lang) -> list[str]:
    lt = init()
    result = lt.translate("\n\n".join(items), source=lang_from.iso, target=lang_to.iso)
    return result.split("\n\n")
