from loguru import logger

from subtaitles.locale import LocaleKey, Locale


class AppError(Exception):

    def __init__(self, locale_key: str = LocaleKey.GENERIC_ERROR, **kwargs):
        super().__init__(str, locale_key, kwargs)
        self.key = locale_key
        self.kwargs = kwargs

    def render(self, locale: Locale) -> str:
        error_string = str(getattr(locale, self.key, None))
        if not error_string:
            logger.error(f"Invalid Locale key: {self.key!r}")
            return locale.GENERIC_ERROR

        if self.kwargs:
            return error_string.format(self.kwargs)

        return error_string
