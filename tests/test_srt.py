from pathlib import Path

import srt

from subtaitles.srt import strip_srt_markup


def test_parse_srt(data: Path) -> None:
    with (data / "Middlemarch S01E01.srt").open("r") as file:
        content = file.read()

    file = list(srt.parse(content))
    file_stripped = [strip_srt_markup(line.content) for line in file]
    assert len(file) == len(file_stripped)
