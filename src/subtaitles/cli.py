import asyncio
import sys
from copy import deepcopy
from pathlib import Path

import pysrt
import typer
import uvicorn
from dotenv import load_dotenv
from rich import print
from rich.console import Console

from subtaitles.app import app
from subtaitles.core import translate_srt
from subtaitles.translate import LANG, Engine

load_dotenv()

console = Console()

cli_app = typer.Typer()


def strip_srt(path: str):
    srt = pysrt.open(path)
    items = [it for it in srt]
    result = [it.text for it in items]
    yield result

    for index, item in items:
        new_item = deepcopy(item)
        new_item.text = result[index]
        result[index] = new_item


@cli_app.command(name="translate")
def main_wrapper(
        source: LANG,
        target: LANG,
        path: Path,
        engine: Engine = Engine.LIBRE,
):
    if not path.is_file():
        print(f"[bold red]{str(path.absolute())!r} does not exist or is not a file!")
        sys.exit(1)
    asyncio.run(translate_srt(path, engine, source, target))


@cli_app.command()
def serve(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run(app, host=host, port=port)


def start_app():
    cli_app()


if __name__ == "__main__":
    # uvicorn.run(app)
    start_app()
