import re
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class Language:
    iso: str
    english: str
    aliases: list[str] = field(default_factory=list)


mapping = {
    "af": Language(iso="af", english="afrikaans"),
    "am": Language(iso="am", english="amharic"),
    "ar": Language(iso="ar", english="arabic"),
    "az": Language(iso="az", english="azerbaijani"),
    "be": Language(iso="be", english="belarusian"),
    "bg": Language(iso="bg", english="bulgarian"),
    "bn": Language(iso="bn", english="bangla"),
    "bs": Language(iso="bs", english="bosnian"),
    "ca": Language(iso="ca", english="catalan"),
    "cs": Language(iso="cs", english="czech", aliases=["cze", "cz"]),
    "da": Language(iso="da", english="danish"),
    "de": Language(iso="de", english="german"),
    "el": Language(iso="el", english="greek"),
    "en": Language(iso="en", english="english"),
    "es": Language(iso="es", english="spanish"),
    "et": Language(iso="et", english="estonian"),
    "fa": Language(iso="fa", english="persian"),
    "fi": Language(iso="fi", english="finnish"),
    "fr": Language(iso="fr", english="french"),
    "ga": Language(iso="ga", english="irish"),
    "he": Language(iso="he", english="hebrew"),
    "hi": Language(iso="hi", english="hindi"),
    "hr": Language(iso="hr", english="croatian"),
    "hu": Language(iso="hu", english="hungarian"),
    "hy": Language(iso="hy", english="armenian"),
    "id": Language(iso="id", english="indonesian"),
    "is": Language(iso="is", english="icelandic"),
    "it": Language(iso="it", english="italian"),
    "ja": Language(iso="ja", english="japanese"),
    "ka": Language(iso="ka", english="georgian"),
    "kk": Language(iso="kk", english="kazakh"),
    "km": Language(iso="km", english="khmer"),
    "ko": Language(iso="ko", english="korean"),
    "lb": Language(iso="lb", english="luxembourgish"),
    "lo": Language(iso="lo", english="lao"),
    "lt": Language(iso="lt", english="lithuanian"),
    "lv": Language(iso="lv", english="latvian"),
    "mk": Language(iso="mk", english="macedonian"),
    "mn": Language(iso="mn", english="mongolian"),
    "ms": Language(iso="ms", english="malay"),
    "mt": Language(iso="mt", english="maltese"),
    "my": Language(iso="my", english="burmese"),
    "ne": Language(iso="ne", english="nepali"),
    "nl": Language(iso="nl", english="dutch"),
    "no": Language(iso="no", english="norwegian"),
    "pl": Language(iso="pl", english="polish"),
    "pt": Language(iso="pt", english="portuguese"),
    "ro": Language(iso="ro", english="romanian"),
    "ru": Language(iso="ru", english="russian"),
    "si": Language(iso="si", english="sinhala"),
    "sk": Language(iso="sk", english="slovak"),
    "sl": Language(iso="sl", english="slovenian"),
    "sq": Language(iso="sq", english="albanian"),
    "sr": Language(iso="sr", english="serbian"),
    "sv": Language(iso="sv", english="swedish"),
    "sw": Language(iso="sw", english="swahili"),
    "th": Language(iso="th", english="thai"),
    "tl": Language(iso="tl", english="filipino"),
    "tr": Language(iso="tr", english="turkish"),
    "uk": Language(iso="uk", english="ukrainian"),
    "ur": Language(iso="ur", english="urdu"),
    "uz": Language(iso="uz", english="uzbek"),
    "vi": Language(iso="vi", english="vietnamese"),
    "zh": Language(iso="zh", english="chinese"),
}


class Lang(Enum):
    AF = "af"
    AM = "am"
    AR = "ar"
    AZ = "az"
    BE = "be"
    BG = "bg"
    BN = "bn"
    BS = "bs"
    CA = "ca"
    CS = "cs"
    DA = "da"
    DE = "de"
    EL = "el"
    EN = "en"
    ES = "es"
    ET = "et"
    FA = "fa"
    FI = "fi"
    FR = "fr"
    GA = "ga"
    HE = "he"
    HI = "hi"
    HR = "hr"
    HU = "hu"
    HY = "hy"
    ID = "id"
    IS = "is"
    IT = "it"
    JA = "ja"
    KA = "ka"
    KK = "kk"
    KM = "km"
    KO = "ko"
    LB = "lb"
    LO = "lo"
    LT = "lt"
    LV = "lv"
    MK = "mk"
    MN = "mn"
    MS = "ms"
    MT = "mt"
    MY = "my"
    NE = "ne"
    NL = "nl"
    NO = "no"
    PL = "pl"
    PT = "pt"
    RO = "ro"
    RU = "ru"
    SI = "si"
    SK = "sk"
    SL = "sl"
    SQ = "sq"
    SR = "sr"
    SV = "sv"
    SW = "sw"
    TH = "th"
    TL = "tl"
    TR = "tr"
    UK = "uk"
    UR = "ur"
    UZ = "uz"
    VI = "vi"
    ZH = "zh"

    @property
    def language(self) -> Language:
        return mapping[self.value]


def guess_lang(text: str) -> Lang | None:
    languages = "|".join({lang.value for lang in Lang})
    pattern = re.compile(r"\.(" + languages + r")\.")
    matches = pattern.findall(text)
    if matches:
        return Lang(matches[-1])

    return None
