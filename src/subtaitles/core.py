from copy import deepcopy
from pathlib import Path

import pysrt
from pysrt import SubRipFile
from rich import print

from subtaitles.translate import Engine, LANG, translate


async def translate_srt(path: Path, engine: Engine, source: LANG, target: LANG):
    filename, ext = path.name.rsplit(".", 1)
    new_path = path.parent / f"{filename}-{target}.{ext}"

    srt = pysrt.open(path.absolute())
    translations = await translate([item.text for item in srt], source.obj, target.obj, engine)

    result = SubRipFile(items=[])
    for item, translation in zip(srt, translations):
        new_item = deepcopy(item)
        new_item.text = translation
        result.append(new_item)

    with open(new_path, mode="w") as file:
        result.write_into(file)

    print(f"[green]Translated subtitles saved to {new_path}")
    return new_path
