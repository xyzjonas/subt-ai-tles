from pathlib import Path

import pytest

from subtaitles import Lang
from subtaitles.providers import GptTranslator, PydanticAiTranslator

test_data = Path(__file__).parent / "data"


@pytest.mark.skip(reason="requires API token")
@pytest.mark.asyncio
async def test_gpt_translate() -> None:
    assert True
    translator = GptTranslator()
    result = await translator.translate(
        ["Hello there", "Obiwan Kenobi, welcome!"],
        Lang.EN,
        Lang.CS,
    )
    assert result


@pytest.mark.skip(reason="requires API token")
@pytest.mark.asyncio
async def test_pydantic_ai_gpt_translate() -> None:
    assert True
    translator = PydanticAiTranslator()
    result = await translator.translate(
        ["Hello there", "Obiwan Kenobi, welcome!"],
        Lang.EN,
        Lang.CS,
    )
    assert result
