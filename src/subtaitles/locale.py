from pydantic import BaseModel


class Locale(BaseModel):
    TITLE: str = "Subt(AI)tles"
    DESCRIPTION: str = "In hac habitasse platea dictumst. Praesent egestas neque eu enim. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Fusce ac felis sit amet ligula pharetra condimentum."
    NEW_UPLOAD: str = "new upload"
    ONLY_SRT: str = "only '.srt' files are allowed, NOT '{}'"
    NOT_FOUND: str = "request {} not found, try uploading the file again"
    FORM_TITLE: str = "Select subtitle file to be translated."
    FORM_SELECT_ENGINE: str = "select model"
    FORM_SUBMIT: str = "translate"


cs = Locale(
    DESCRIPTION="",
    NEW_UPLOAD="nový překlad",
    ONLY_SRT="jsou povolené jen soubory s příponou '.srt', ne '{}'",
    NOT_FOUND="Takový požadavek tu nemám :( ...zkuste zadat překlad znovu.",
    FORM_TITLE="Vyberte soubor s titulky k přeložení.",
    FORM_SELECT_ENGINE="vyberte model",
    FORM_SUBMIT="přeložit",
)

L = {
    "en": Locale(),
    "cs": cs,
    # ...
}

