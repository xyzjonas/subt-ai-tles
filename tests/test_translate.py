import tempfile
from pathlib import Path
from unittest import mock

import pytest

from subtaitles import Engine, Lang
from subtaitles.translate import translate_srt_file
from tests.utils import MockedTranslator


@pytest.mark.asyncio
async def test_translate_srt_file(data: Path) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        filename = "sub-short.srt"
        input_path = data / filename
        output = Path(temp_dir) / filename
        with mock.patch(
            "subtaitles.translate.get_translator", return_value=MockedTranslator()
        ):
            output_path = await translate_srt_file(
                input_path, Lang.EN, Lang.EN, Engine.OPEN_AI, output
            )

        assert output == output_path
        assert output.exists()
        assert output.is_file()
        with output.open("r") as output_file, input_path.open("r") as input_file:
            assert input_file.readlines()[1:] == output_file.readlines()[1:-1]
