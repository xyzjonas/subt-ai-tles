from enum import StrEnum
from pydantic import BaseModel


class LocaleKey(StrEnum):
    TITLE = "TITLE"
    DESCRIPTION = "DESCRIPTION"
    NEW_UPLOAD = "NEW_UPLOAD"
    NOT_FOUND = "NOT_FOUND"
    FORM_TITLE = "FORM_TITLE"
    FORM_SELECT_ENGINE = "FORM_SELECT_ENGINE"
    FORM_SUBMIT = "FORM_SUBMIT"
    GENERIC_ERROR = "GENERIC_ERROR"
    ONLY_SRT = "ONLY_SRT"
    TRANSLATED_NOT_FOUND = "TRANSLATED_NOT_FOUND"


class Locale(BaseModel):
    TITLE: str = "Subt(AI)tles"
    DESCRIPTION: str = "In hac habitasse platea dictumst. Praesent egestas neque eu enim. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Fusce ac felis sit amet ligula pharetra condimentum."
    NEW_UPLOAD: str = "new upload"
    NOT_FOUND: str = "request {} not found, try uploading the file again"
    FORM_TITLE: str = "Select subtitle file to be translated."
    FORM_SELECT_ENGINE: str = "select model"
    FORM_SUBMIT: str = "translate"
    GENERIC_ERROR: str = "Something very wrong happened :("
    ONLY_SRT: str = "only '.srt' files are allowed, NOT '{extension}'"
    TRANSLATED_NOT_FOUND: str = "Translated subtitles ({language}) not found."


cs = Locale(
    GENERIC_ERROR="Něco se pokazilo :(",
    DESCRIPTION="",
    NEW_UPLOAD="nový překlad",
    ONLY_SRT="jsou povolené jen soubory s příponou '.srt', ne '{}'",
    NOT_FOUND="Takový požadavek tu nemám :( ...zkuste zadat překlad znovu.",
    FORM_TITLE="Vyberte soubor s titulky k přeložení.",
    FORM_SELECT_ENGINE="vyberte model",
    FORM_SUBMIT="přeložit",
    TRANSLATED_NOT_FOUND="Překlad nenalezen ({language})",
)

L = {
    "en": Locale(),
    "cs": cs,
    # ...
}

