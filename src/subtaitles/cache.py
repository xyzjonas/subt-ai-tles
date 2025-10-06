from diskcache import Cache

from subtaitles import Lang, env

cache = Cache(env.CACHE_DIR.value)


def get_cache_key(text: str, lang_from: Lang, lang_to: Lang) -> str:
    return f"{text}-{lang_from}-{lang_to}"
