import asyncio
import sys
from argparse import ArgumentParser
from collections.abc import Iterable
from pathlib import Path

from subtaitles import Engine, Lang
from subtaitles.cache import disk_cache
from subtaitles.filesystem import translate_directory
from subtaitles.language import guess_lang
from subtaitles.task import TranslateTask, get_translate_task


def tasks_done(tasks: Iterable[TranslateTask]) -> bool:
    return all(task.is_done for task in tasks)


def print_task(task: TranslateTask) -> None:
    # mark = "x" if task.exception else "✓" if task.is_done else " "
    # print(  # noqa: T201
    #     f"[{mark}] {task.progress.current}/{task.progress.total} {task.task_data.path} "
    #     f"-> {task.task_data.new_path} ({task.task_data.target.language.english})\033[K"
    # )
    pass


def print_tasks(tasks: Iterable[TranslateTask]) -> None:
    """Print the whole status list. completed is a set of indices marked done."""
    for task in tasks:
        print_task(task)


async def translate_dir_cmd(
    input_path: Path, lang_from: Lang, lang_to: Lang, engine: Engine
) -> None:
    tasks = translate_directory(input_path, lang_from, lang_to, engine)
    while True:
        # print(f"\033[{len(tasks)}A", end="")  # noqa: T201
        # print_tasks(tasks)
        await asyncio.sleep(0.5)

        if tasks_done(tasks):
            break

    if not tasks:
        print(f"Nothing to translate in {input_path}\033[K")  # noqa: T201


async def translate_single_cmd(
    input_path: Path, new_path: Path, lang_from: Lang, lang_to: Lang, engine: Engine
) -> TranslateTask:
    task = get_translate_task(input_path, new_path, lang_from, lang_to, engine)
    task.run()
    while True:
        print_task(task)
        await asyncio.sleep(0.1)

        if task.is_done:
            break
    return task


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "input",
        metavar="INPUT_PATH",
        type=Path,
        help="Path to a .srt file to be translated",
    )
    parser.add_argument(
        "--output",
        metavar="OUTPUT_PATH",
        type=Path,
        default=None,
        help="Path to where the resulting file will be stored, if omitted new file will be created next to the input one.",
    )
    parser.add_argument(
        "--lang-from",
        metavar="LANGUAGE_FROM",
        type=Lang,
        help="Language to be translated from, gets deduced from the file extension or defaults to english.",
    )
    parser.add_argument(
        "lang_to",
        metavar="LANGUAGE_TO",
        type=Lang,
        help="Target language for the translation.",
    )
    parser.add_argument("--dir", action="store_true")
    parser.add_argument(
        "--engine",
        type=Engine,
        help="Translation engine to be used",
        default=Engine.OPEN_AI,
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear cached results.",
    )
    parser.add_argument(
        "--log-level",
        "-l",
        help="loglevel",
        default="INFO",
    )

    args = parser.parse_args()

    lang_from = args.lang_from
    if not lang_from:
        lang_from = guess_lang(str(args.input))
    if not lang_from:
        lang_from = Lang.EN

    if args.clear_cache:
        disk_cache.clear()
        print("✅ Cached results cleared.")

    if args.dir:
        asyncio.run(translate_dir_cmd(args.input, lang_from, args.lang_to, args.engine))
        sys.exit(0)

    output = args.output
    if not output:
        output = Path(args.input).parent

    asyncio.run(
        translate_single_cmd(
            args.input,
            output,
            lang_from,
            args.lang_to,
            args.engine,
        )
    )


if __name__ == "__main__":
    main()
