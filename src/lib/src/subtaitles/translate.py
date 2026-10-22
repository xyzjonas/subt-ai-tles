from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import pysrt
from loguru import logger
from pysrt import SubRipFile

from subtaitles.srt import strip_newlines

from .environment import env
from .exceptions import FailedToTranslateError
from .models import Segment, SummaryStatus, TitleMetadata, TranslationRequest
from .providers import Engine, TranslateProtocol, get_translator
from .srt import reapply_whole_line_markup, strip_srt_markup

if TYPE_CHECKING:
    from . import TranslationResponse
    from .language import Lang
    from .providers.protocol import Progress, SummaryStoreProtocol


def _media_key(kind: str, title: str, suffix: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return f"{kind}:{slug}:{suffix}"


async def add_summary(
    request: TranslationRequest,
    translator: TranslateProtocol,
    store: SummaryStoreProtocol | None,
) -> tuple[TranslationRequest, SummaryStatus]:
    """Attach the story brief of a recognized title, summarizing (and storing) it on a miss.

    Best effort: without a key (media not recognized) or on failure the request is unchanged.
    """
    key = request.metadata.key if request.metadata else None
    if not key:
        return request, SummaryStatus.SKIPPED

    try:
        summary = await store.get(key) if store else None
        if summary:
            logger.debug(f"Story brief for {key} found in store.")
            status = SummaryStatus.STORED
        else:
            logger.debug(f"Summarizing {key}.")
            summary = await translator.summarize(request)
            status = SummaryStatus.GENERATED
            if store:
                await store.put(key, summary)
    except Exception as e:  # noqa: BLE001 - the brief is optional, never fail the job
        logger.warning(f"Can't summarize {key}: {e}")
        return request, SummaryStatus.FAILED
    return replace(request, summary=summary), status


async def get_translation_request(
    srt: SubRipFile,
    target: Lang,
    translator: Engine | TranslateProtocol,
) -> tuple[TranslateProtocol, TranslationRequest]:
    if not hasattr(translator, "translate"):
        translator = get_translator(translator)

    meta = None
    try:
        from mediasorter import TvShowMetadata, whats_this  # noqa: PLC0415
        from mediasorter.lib.config import default_config  # noqa: PLC0415

        for provider in default_config.api:
            if provider.name == "tmdb":
                provider.key = env.TMDB_API_KEY

        fetched_meta = await whats_this(str(Path(srt.path)), config=default_config)
        if isinstance(fetched_meta, TvShowMetadata):
            logger.debug(
                f"Recognized as {fetched_meta.type}: {fetched_meta.series_title}, "
                "adding to context."
            )
            meta = TitleMetadata(
                title=fetched_meta.series_title,
                description=fetched_meta.episode_summary,
                key=_media_key(
                    "tv",
                    fetched_meta.series_title,
                    f"s{fetched_meta.season_id:02d}e{fetched_meta.episode_id:02d}",
                ),
            )
        else:
            logger.debug(
                f"Recognized as {fetched_meta.type}: {fetched_meta.title}, adding to context."
            )
            meta = TitleMetadata(
                title=fetched_meta.title,
                description=fetched_meta.summary,
                key=_media_key("movie", fetched_meta.title, str(fetched_meta.year)),
            )
    except Exception as e:  # noqa: BLE001 - metadata is optional, translate without it
        logger.warning(f"Can't fetch media metadata: {e}")

    segments = tuple(
        Segment(
            index=i,
            text=strip_newlines(strip_srt_markup(item.text)),
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

    return translator, TranslationRequest(segments=segments, target=target, metadata=meta)


def get_translated_srt(
    srt: SubRipFile, request: TranslationRequest, response: TranslationResponse
) -> SubRipFile:
    by_index = response.by_index()
    seg_by_index = {seg.index: seg for seg in request.segments}
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


async def translate_srt(
    srt: SubRipFile,
    target: Lang,
    translator: Engine | TranslateProtocol,
    progress: Progress | None = None,
    summaries: SummaryStoreProtocol | None = None,
) -> SubRipFile:
    """Translate subtitle file (.srt) a parsed SubRipFile object.

    :param srt: parsed srt file
    :param target: target language
    :param translator: translation engine or translator instance
    :param progress: progress object
    :param summaries: optional store to persist story briefs of recognized titles
    :return: translated subtitle file as SubRipFile object
    """
    translator, request = await get_translation_request(srt, target, translator)
    request, _ = await add_summary(request, translator, summaries)

    response = await translator.translate(request, progress)

    return get_translated_srt(srt, request, response)


async def translate_srt_file(  # noqa: PLR0913, PLR0917
    path: Path | str,
    target: Lang,
    translator: Engine | TranslateProtocol,
    new_path: Path | str | None = None,
    progress: Progress | None = None,
    summaries: SummaryStoreProtocol | None = None,
) -> Path:
    """Translate subtitle file (.srt) given a path on the local filesystem.

    :param path: filesystem path to the srt source file
    :param target: target language
    :param translator: translation engine type or translator instance
    :param new_path: arbitrary path to the new file with translated subtitles
    :param progress: progress object
    :param summaries: optional store to persist story briefs of recognized titles
    :return: path to the new file with translated subtitles
    """
    try:
        path = Path(path)
        logger.info(f"Translating subtitle file {path}")
        filename, ext = path.name.rsplit(".", 1)
        new_path = Path(new_path) if new_path else path.parent
        if new_path.is_dir():
            new_path = new_path / f"{filename}.{target.value}.{ext}"
        srt = pysrt.open(path.absolute())

        result = await translate_srt(srt, target, translator, progress, summaries)
        with new_path.open("w") as file:
            result.write_into(file)

        logger.info(f"Translated subtitles written to {new_path}")
    except ValueError as exc:
        raise FailedToTranslateError(path, new_path, f"Translator failed: {exc}") from exc
    except Exception as exc:
        raise FailedToTranslateError(path, new_path, f"Unexpected error: {exc}") from exc
    else:
        return new_path
