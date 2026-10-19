from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Language

# (ISO 639-1 code, English name, native name, ISO 3166-1 country whose flag represents it)
_SEED: list[tuple[str, str, str | None, str]] = [
    ("af", "Afrikaans", None, "ZA"),
    ("sq", "Albanian", "shqip", "AL"),
    ("am", "Amharic", "አማርኛ", "ET"),
    ("ar", "Arabic", "العربية", "SA"),
    ("hy", "Armenian", "հայերեն", "AM"),
    ("az", "Azerbaijani", "azərbaycan", "AZ"),
    ("be", "Belarusian", "беларуская", "BY"),
    ("bn", "Bangla", "বাংলা", "BD"),
    ("bs", "Bosnian", "bosanski", "BA"),
    ("bg", "Bulgarian", "български", "BG"),
    ("my", "Burmese", "မြန်မာ", "MM"),
    ("ca", "Catalan", "català", "AD"),
    ("zh", "Chinese", "中文", "CN"),
    ("hr", "Croatian", "hrvatski", "HR"),
    ("cs", "Czech", "čeština", "CZ"),
    ("da", "Danish", "dansk", "DK"),
    ("nl", "Dutch", "Nederlands", "NL"),
    ("en", "English", None, "GB"),
    ("et", "Estonian", "eesti", "EE"),
    ("tl", "Filipino", None, "PH"),
    ("fi", "Finnish", "suomi", "FI"),
    ("fr", "French", "français", "FR"),
    ("ka", "Georgian", "ქართული", "GE"),
    ("de", "German", "Deutsch", "DE"),
    ("el", "Greek", "Ελληνικά", "GR"),
    ("he", "Hebrew", "עברית", "IL"),
    ("hi", "Hindi", "हिन्दी", "IN"),
    ("hu", "Hungarian", "magyar", "HU"),
    ("is", "Icelandic", "íslenska", "IS"),
    ("id", "Indonesian", "Indonesia", "ID"),
    ("ga", "Irish", "Gaeilge", "IE"),
    ("it", "Italian", "italiano", "IT"),
    ("ja", "Japanese", "日本語", "JP"),
    ("kk", "Kazakh", "қазақ тілі", "KZ"),
    ("km", "Khmer", "ខ្មែរ", "KH"),
    ("ko", "Korean", "한국어", "KR"),
    ("lo", "Lao", "ລາວ", "LA"),
    ("lv", "Latvian", "latviešu", "LV"),
    ("lt", "Lithuanian", "lietuvių", "LT"),
    ("lb", "Luxembourgish", "Lëtzebuergesch", "LU"),
    ("mk", "Macedonian", "македонски", "MK"),
    ("ms", "Malay", "Bahasa Melayu", "MY"),
    ("mt", "Maltese", "Malti", "MT"),
    ("mn", "Mongolian", "монгол", "MN"),
    ("ne", "Nepali", "नेपाली", "NP"),
    ("no", "Norwegian", "norsk", "NO"),
    ("fa", "Persian", "فارسی", "IR"),
    ("pl", "Polish", "polski", "PL"),
    ("pt", "Portuguese", "português", "PT"),
    ("ro", "Romanian", "română", "RO"),
    ("ru", "Russian", "русский", "RU"),
    ("sr", "Serbian", "српски", "RS"),
    ("si", "Sinhala", "සිංහල", "LK"),
    ("sk", "Slovak", "slovenčina", "SK"),
    ("sl", "Slovenian", "slovenščina", "SI"),
    ("es", "Spanish", "español", "ES"),
    ("sw", "Swahili", "Kiswahili", "KE"),
    ("sv", "Swedish", "svenska", "SE"),
    ("th", "Thai", "ไทย", "TH"),
    ("tr", "Turkish", "Türkçe", "TR"),
    ("uk", "Ukrainian", "українська", "UA"),
    ("ur", "Urdu", "اردو", "PK"),
    ("uz", "Uzbek", "o'zbek", "UZ"),
    ("vi", "Vietnamese", "Tiếng Việt", "VN"),
]


def _flag_emoji(country: str) -> str:
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in country)


def list_all(db: Session) -> list[Language]:
    return list(db.scalars(select(Language).order_by(Language.name)))


def get(db: Session, code: str) -> Language | None:
    return db.get(Language, code)


def seed(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(Language)):
        return
    db.add_all(
        Language(code=code, name=name, native=native, flag=_flag_emoji(country))
        for code, name, native, country in _SEED
    )
    db.commit()
