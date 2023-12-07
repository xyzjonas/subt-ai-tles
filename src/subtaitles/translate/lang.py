from enum import StrEnum
from dataclasses import dataclass


@dataclass
class Lang:
    iso: str
    english: str


class LANG(StrEnum):
    CS = "cs"
    EN = "en"

    @property
    def obj(self) -> Lang:
        return {
            "cs": Lang(iso="cs", english="czech"),
            "en": Lang(iso="en", english="english"),
        }[self.value]
