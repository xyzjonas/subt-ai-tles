import os

from loguru import logger
from openai import OpenAI

from subtaitles.translate import Lang


def init() -> OpenAI:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    org_id = os.environ.get("OPENAPI_ORG_ID")
    if not org_id:
        raise RuntimeError("OPENAPI_ORG_ID is not set")

    return OpenAI(api_key=key, organization=org_id)


def completion(lang_from: Lang, lang_to: Lang, items: list[str]):
    return {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": f"Translate subtitles from {lang_from.english} to {lang_to.english} accurately while "
                           "maintaining the original meaning and tone. Use natural-sounding phrases and idioms "
                           "that accurately convey the meaning of the original text. Imagine you are the linguist "
                           "responsible for translating the subtitles."
                           "\n"
                           "Further instructions:\n"
                           "- Given text is in English.\n"
                           "- Generate natural-sounding translations that accurately convey the meaning of the "
                           "original text\n."
                           "- Check the accuracy and naturalness of the translations"
                           "before submitting them to the user.",
            },
            {
                "role": "user",
                "content": "Translate the following:"
                           "\n"
                           f"{'\n\n'.join(items)}"
            }
        ]
    }


async def translate(items: list[str], lang_from: Lang, lang_to: Lang) -> list[str]:
    # Instructions:
    # - The given .srt text delimited by triple backticks is the subtitle for the video.
    # - User Inputs any language of subtitles they want to translate one at a time.
    # - Given text is in English.
    # - Generate natural-sounding translations that accurately convey the meaning of the original text.
    # - Check the accuracy and naturalness of the translations before submitting them to the user.",
    raise NotImplementedError("rework in progress")

    # todo: parallelize (max token limit), async
    client = init()
    total_size = len("\n\n".join(items))
    if total_size > 15000:
        middle = int(len(items)/2)

        first = items[:middle]
        translated_first = client.chat.completions.create(**completion(lang_from, lang_to, first))

        second = items[middle+1:]
        translated_second = client.chat.completions.create(**completion(lang_from, lang_to, second))

        result = [
            *translated_first.choices[0].message.content.split("\n\n"),
            *translated_second.choices[0].message.content.split("\n\n")
        ]

    else:

        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"Translate subtitles from {lang_from.english} to {lang_to.english} accurately while "
                               "maintaining the original meaning and tone. Use natural-sounding phrases and idioms "
                               "that accurately convey the meaning of the original text. Imagine you are the linguist "
                               "responsible for translating the subtitles."
                               "\n"
                               "Further instructions:\n"
                               "- Given text is in English.\n"
                               "- Generate natural-sounding translations that accurately convey the meaning of the "
                               "original text\n."
                               "- Check the accuracy and naturalness of the translations"
                               "before submitting them to the user.",
                },
                {
                    "role": "user",
                    "content": "Translate the following:"
                               "\n"
                               f"{'\n\n'.join(items)}"
                }
            ]
        )

        if not chat_completion.choices:
            raise ValueError("GPT returned no predictions, unexpected...")

        result = chat_completion.choices[0].message.content.split("\n\n")

    return result
