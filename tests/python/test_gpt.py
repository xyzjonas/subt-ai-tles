import os
import pytest

from pathlib import Path

from subtaitles.translate import Engine, LANG
from subtaitles.core import translate_srt


test_data = Path(os.path.dirname(__file__)).parent / "data"


@pytest.mark.asyncio
async def test_translate_with_gpt():
    assert await translate_srt(test_data / "sub-short.srt", Engine.GPT, LANG.EN, LANG.CS)
