import tempfile
from pathlib import Path

import pytest

from subtaitles import Lang
from subtaitles.filesystem import (
    TranslateTaskData,
    find_srt_files,
    get_new_language_file_path,
    get_translate_tasks,
    is_already_translated,
    translate_directory,
)
from tests.utils import MockedTranslator

TOTAL_TEST_FILE_COUNT = 5


def test_find_srt_files(data: Path) -> None:
    found_srts = find_srt_files(data)
    assert len(found_srts) == TOTAL_TEST_FILE_COUNT
    assert all(isinstance(srt, Path) for srt in found_srts), (
        f"Not all items are paths: {[type(srt) for srt in found_srts]}"
    )


@pytest.mark.parametrize(
    ("filename", "lang"),
    [
        ("just_some_file.en.srt", Lang.EN),
        ("just_some_file.cz.srt", Lang.CS),
        ("just_some_file.cze.srt", Lang.CS),
        ("just_some_file.cs.srt", Lang.CS),
        ("just_some_file.de.srt", Lang.DE),
        ("/path/to/some/file.it.srt", Lang.IT),
        ("Scrubs S01E01 - My First Day.cs.srt", Lang.CS),
    ],
)
def test_is_already_translated(filename: str, lang: Lang) -> None:
    assert is_already_translated(filename, lang)


@pytest.mark.parametrize(
    ("filename", "lang"),
    [
        ("just_some_file.srt", Lang.EN),
        ("just_some_file.de.srt", Lang.EN),
    ],
)
def test_is_not_already_translated(filename: str, lang: Lang) -> None:
    assert not is_already_translated(filename, lang)


@pytest.mark.parametrize(
    ("filename", "lang_from", "lang_to", "expected"),
    [
        ("/absolute/to/some_file.en.srt", Lang.EN, Lang.CS, "/absolute/to/some_file.cs.srt"),
        ("just_some_file.en.srt", Lang.EN, Lang.CS, "just_some_file.cs.srt"),
        ("just_some_file.srt", Lang.DE, Lang.CS, "just_some_file.cs.srt"),
        ("just_some_file.cze.srt", Lang.CS, Lang.DE, "just_some_file.de.srt"),
        ("just_some_file.srt", Lang.EN, Lang.CS, "just_some_file.cs.srt"),
        ("just_some_file.subrip.srt", Lang.EN, Lang.CS, "just_some_file.subrip.cs.srt"),
    ],
)
def test_get_new_language_file_name(
    filename: str, lang_from: Lang, lang_to: Lang, expected: str
) -> None:
    assert (
        str(get_new_language_file_path(path=filename, lang_from=lang_from, lang_to=lang_to))
        == expected
    )


def test_get_translate_tasks(data: Path) -> None:
    target_dir = data / "nested_dir"

    tasks = get_translate_tasks(
        path=target_dir, source=Lang.EN, target=Lang.CS, translator=MockedTranslator
    )
    assert [t.task_data for t in tasks] == [
        TranslateTaskData(
            path=target_dir / "sub-short.srt",
            new_path=target_dir / "sub-short.cs.srt",
            source=Lang.EN,
            target=Lang.CS,
        )
    ]


async def test_translate_directory_which_is_file(data: Path) -> None:
    with pytest.raises(FileNotFoundError):
        translate_directory(
            data / "sub.srt", source=Lang.EN, target=Lang.CS, translator=MockedTranslator
        )


async def test_translate_directory(data: Path) -> None:
    with tempfile.TemporaryDirectory() as directory:
        temp_dir = Path(directory)

        with (data / "nested_dir" / "sub-short.srt").open("r") as source_file:  # noqa: SIM117
            with (temp_dir / "sub-short.srt").open("w") as dest_file:
                dest_file.write(source_file.read())

        tasks = translate_directory(
            temp_dir, source=Lang.EN, target=Lang.CS, translator=MockedTranslator
        )

        assert len(tasks) == 1
        task = tasks[0]

        await task.task
        dest_srt = tasks[0].task_data.new_path
        assert dest_srt.is_file()
        assert dest_srt.name == "sub-short.cs.srt"
        assert dest_srt.read_text()
