import os
from pathlib import Path

import pytest
from subtaitles import Engine, Lang
from subtaitles.cli import translate_single_cmd

SOURCE = Path("/home/jonas/Videos/series/House/Season 01/House S01E01 - Pilot.srt")


@pytest.mark.skipif(
    not (os.environ.get("RUN_E2E") and SOURCE.is_file()),
    reason="opt-in (RUN_E2E=1): needs a local subtitle file and real OpenAI access",
)
@pytest.mark.asyncio
async def test_translate_e2e(data):

    result = await translate_single_cmd(
        SOURCE,
        data.parent,
        Lang.CS,
        Engine.OPEN_AI,
    )
    assert result.is_done
    assert result.progress.total > 0
    assert result.progress.current == result.progress.total
