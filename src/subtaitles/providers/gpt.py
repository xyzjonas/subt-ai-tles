from __future__ import annotations

from typing import TYPE_CHECKING

from openai import OpenAI

from subtaitles.environment import env
from subtaitles.imports import batched

if TYPE_CHECKING:
    from collections.abc import Iterable

    from subtaitles.language import Lang

DELIMITER = "---"


class OpenAiTranslator:
    context = """Translate subtitles from {lang_from} to {lang_to} accurately while
maintaining the original meaning and tone. Use natural-sounding phrases and idioms
that accurately convey the meaning of the original text.
KEEP the delimiters '{delimiter}' in place to indicate item borders!
"""

    def __init__(self, model: str | None = None) -> None:
        self.model = model or env.OPENAI_MODEL(strict=True)
        self.client = OpenAI(
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

    async def translate(
        self,
        text: list[str],
        language_from: Lang,
        language_to: Lang,
        batch_size: int = 100,
    ) -> list[str]:
        result_chunks = []
        for batch in batched(text, batch_size, strict=False):
            completion = self.get_completion(language_from, language_to, batch)
            response = self.client.chat.completions.create(**completion)
            if not response.choices:
                msg = "GPT returned no predictions, unexpected..."
                raise ValueError(msg)

            result_chunks.extend(response.choices[0].message.content.split(DELIMITER))

        return result_chunks
