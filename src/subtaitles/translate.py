from __future__ import annotations

import logging
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import pysrt
from pysrt import SubRipFile

from .exceptions import FailedToTranslateError
from .models import Segment, TranslationRequest
from .providers import Engine, TranslateProtocol, get_translator
from .srt import reapply_whole_line_markup, strip_srt_markup

if TYPE_CHECKING:
    from .language import Lang
    from .providers.protocol import Progress


logger = logging.getLogger(__name__)


async def translate_srt(
    srt: SubRipFile,
    source: Lang,
    target: Lang,
    translator: Engine | TranslateProtocol,
    progress: Progress | None = None,
) -> SubRipFile:
    """Translate subtitle file (.srt) a parsed SubRipFile object.

    :param srt: parsed srt file
    :param source: source language
    :param target: target language
    :param translator: translation engine or translator instance
    :param progress: progress object
    :return: translated subtitle file as SubRipFile object
    """
    if not hasattr(translator, "translate"):
        translator = get_translator(translator)

    segments = tuple(
        Segment(
            index=i,
            text=strip_srt_markup(item.text),
            raw=item.text,
            start=timedelta(
                hours=item.start.hours,
                minutes=item.start.minutes,
                seconds=item.start.seconds,
                milliseconds=item.start.milliseconds,
            ),
            end=timedelta(
                hours=item.end.hours,
                minutes=item.end.minutes,
                seconds=item.end.seconds,
                milliseconds=item.end.milliseconds,
            ),
        )
        for i, item in enumerate(srt)
    )

    request = TranslationRequest(segments=segments, source=source, target=target)
    response = await translator.translate(request, progress)

    by_index = response.by_index()
    seg_by_index = {seg.index: seg for seg in segments}

    result = SubRipFile(items=[])
    for i, item in enumerate(srt):
        new_item = deepcopy(item)
        translated = by_index.get(i)
        if translated:
            text = translated.translation
            raw = seg_by_index[i].raw
            if raw:
                text = reapply_whole_line_markup(raw, text)
            new_item.text = text
        result.append(new_item)

    return result


async def translate_srt_file(  # noqa: PLR0913
    path: Path | str,
    source: Lang,
    target: Lang,
    translator: Engine | TranslateProtocol,
    new_path: Path | str | None = None,
    progress: Progress | None = None,
) -> Path:
    """Translate subtitle file (.srt) given a path on the local filesystem.

    :param path: filesystem path to the srt source file
    :param source: source language
    :param target: target language
    :param translator: translation engine type or translator instance
    :param new_path: arbitrary path to the new file with translated subtitles
    :param progress: progress object
    :return: path to the new file with translated subtitles
    """
    try:
        path = Path(path)
        logger.info("Translating subtitle file %s", path)
        filename, ext = path.name.rsplit(".", 1)
        new_path = Path(new_path) or path.parent / f"{filename}-{target}.{ext}"
        srt = pysrt.open(path.absolute())

        result = await translate_srt(srt, source, target, translator, progress)
        with new_path.open("w") as file:
            result.write_into(file)

        logger.info("Translated subtitles written to %s", new_path)
    except ValueError as exc:
        raise FailedToTranslateError(path, new_path, f"Translator failed: {exc}") from exc
    except Exception as exc:
        raise FailedToTranslateError(path, new_path, f"Unexpected error: {exc}") from exc
    else:
        return new_path
