import pysrt
import srt

from subtaitles.translate import strip_srt_markup


def test_parse_srt(data):
    with open(data / "Middlemarch S01E01.srt") as file:
        content = file.read()

    file = list(srt.parse(content))
    file_stripped = [strip_srt_markup(line.content) for line in file]
    assert len(file) == len(file_stripped)
