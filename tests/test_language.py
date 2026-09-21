import pytest

from subtaitles.language import guess_lang, Lang


@pytest.mark.parametrize(
    "text,lang", [("foo.en.srt", Lang.EN), ("hotline.cs.miami.en.srt", Lang.EN)]
)
def test_guess_lang(text, lang) -> None:
    assert guess_lang(text) == lang
