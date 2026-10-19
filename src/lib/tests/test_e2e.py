from pathlib import Path

import pytest

from subtaitles import Lang, Engine
from subtaitles.cli import translate_single_cmd


@pytest.mark.asyncio
async def test_translate_e2e(data):

    result = await translate_single_cmd(
        # data / "rick-and-morty-S01E01.en.srt",
        Path("/home/jonas/Videos/series/House/Season 01/House S01E01 - Pilot.srt"),
        data.parent,
        Lang.EN,
        Lang.CS,
        Engine.OPEN_AI,
    )
    assert result.is_done
    assert result.progress.total == 1030
    assert result.progress.current == 1030
