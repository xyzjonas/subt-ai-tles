from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from openai import AsyncOpenAI

from subtaitles.environment import env
from subtaitles.imports import batched

if TYPE_CHECKING:
    from collections.abc import Iterable

    from subtaitles.language import Lang


logger = logging.getLogger(__name__)

DELIMITER = "---"


class OpenAiTranslator:
    context = """Translate subtitles from {lang_from} to {lang_to} accurately while
maintaining the original meaning and tone. Use natural-sounding phrases and idioms
that accurately convey the meaning of the original text. KEEP the delimiters '{delimiter}'
in place to indicate item borders! Response can't start or end with a {delimiter}.
Make sure that the number of lines separated by {delimiter} is equal.
"""

    def __init__(self, model: str | None = None) -> None:
        self.model = model or env.OPENAI_MODEL(strict=True)
        self.client = AsyncOpenAI(
            api_key=env.OPENAI_API_KEY(strict=True),
            organization=env.OPENAI_ORG_ID(strict=True),
        )

    def get_completion(
        self,
        lang_from: Lang,
        lang_to: Lang,
        items: Iterable[str],
    ) -> dict:
        return {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.context.format(
                        lang_from=lang_from.language.english,
                        lang_to=lang_to.language.english,
                        delimiter=DELIMITER,
                    ),
                },
                {"role": "user", "content": "---".join(items)},
            ],
        }

    async def process_batch(
        self,
        text: list[str] | tuple[str],
        language_from: Lang,
        language_to: Lang,
        retries_left: int = 10,
        batch_id: int = 0,
    ) -> list[str]:
        logger.info("Processing batch %d retries-left=%d", batch_id, retries_left)
        completion = self.get_completion(language_from, language_to, text)
        response = await self.client.chat.completions.create(**completion)
        if not response.choices:
            if retries_left > 0:
                return await self.process_batch(
                    text, language_from, language_to, retries_left - 1
                )
            msg = "GPT returned no predictions, unexpected..."
            raise ValueError(msg)

        res = [line for line in response.choices[0].message.content.split(DELIMITER) if line]
        if len(res) != len(text):
            if retries_left > 0:
                return await self.process_batch(
                    text, language_from, language_to, retries_left - 1
                )
            msg = f"Input lines count doesn't match output's line count! {text} --> {res}"
            raise ValueError(msg)

        logger.info("[OK] batch %d completed, retries-left=%d", batch_id, retries_left)
        return res

    async def translate(
        self,
        text: list[str],
        language_from: Lang,
        language_to: Lang,
        batch_size: int = 10,
    ) -> list[str]:
        text = [line.strip() for line in text]
        translated_lines = []

        tasks = []
        for index, batch in enumerate(batched(text, batch_size, strict=False)):
            logger.info(
                "Running batch (%d/%d), size=%d items",
                (index + 1) * batch_size,
                len(text),
                batch_size,
            )
            tasks.append(
                self.process_batch(list(batch), language_from, language_to, batch_id=index)
            )

        for result in await asyncio.gather(*tasks):
            translated_lines.extend(result)

        return translated_lines
