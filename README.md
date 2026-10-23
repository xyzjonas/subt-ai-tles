# SUBT-AI-TLES

Translate movie and show subtitles (`.srt`) with an LLM, without breaking the timings. SUBT-AI-TLES ships as a
self-hosted web app and as a Python library/CLI.

## The app

Upload a subtitle file, pick the target language and let the LLM translate it in the background. Review and fix
the result cue by cue in the editor, then download the finished `.srt`.

- Background translation jobs with live progress (Celery + Redis)
- Cue-by-cue editor to review and correct the translation
- Per-user monthly credit quotas and token usage tracking
- Admin-managed users and per-model credit rates
- Translation cache, so re-running a failed or repeated job doesn't pay for the same lines twice
- Movie/show metadata lookup via TMDB

<p align="center">
  <img src="https://github.com/user-attachments/assets/f76df118-fbb4-4bb1-8476-13b1b0106d8a" alt="Homepage" width="32%">
  <img src="https://github.com/user-attachments/assets/98f25b2d-ba46-418b-aeda-8202fd3760b6" alt="Detail and editor" width="32%">
  <img src="https://github.com/user-attachments/assets/0e6a1964-978b-4653-9b2c-73640e03da36" alt="Quotas" width="32%">
</p>
<p align="center"><sub>Homepage · Detail / editor · Quotas</sub></p>

### Running it
Set `OPENAI_API_KEY` and `TMDB_API_KEY` (optionally `ADMIN_USERNAME` / `ADMIN_PASSWORD`) in a `.env` file, then:
```bash
docker compose up -d --build   # or: just up
```
The app is served on http://localhost:9142.

## Library

The translation engine behind the app is also available as a standalone Python package: a simple wrapper around
your LLM for movie subtitles translation.

### What does it do?
- Parses the .srt
- Requests individual lines to be translated by the LLM
- Puts it all back together, making sure the sentences match the srt structure/timings
- Caches results - which makes rerunning failed runs a possibility

### Provided adapters
> So far OpenAI API is the only supported/pre-implemented 'backend'

Setup required environment variables and then simply import and invoke the function. 
```python
import asyncio
from subtaitles import translate_srt_file, Engine, Lang

# use predefined translators from the Engine enum
asyncio.run(
    translate_srt_file(
        path="/tmp/subtitles.en.srt",
        new_path="/tmp/subtitles.de.srt",
        translator=Engine.OPEN_AI,
        target=Lang.DE,
    )
)
```

```python
# behavior and configuration is controlled via environment variables
# all the used variables are defined int the environment module
from subtaitles import env
```


### Directory mode
A directory mode is included as well that tries to translate ALL the `.srt` files it can find in the supplied directory
path. Locale extension are used to avoid re-running the translation over and over, e.g.:
> If  `sub-1.de.srt` already exists in the directory and translation from `en -> de` is to be performed on it, 
> the file `sub-1.srt` will be skipped altogether.
 
```python
import asyncio
from subtaitles import Lang, Engine
from subtaitles.filesystem import translate_directory

asyncio.run(
    translate_directory(
        path="/tmp/data/shows/foo/season-01",
        translator=Engine.OPEN_AI,
        target=Lang.DE,
    )
)
```

### Custom implementations
An arbitrary class that implements the `TranslateProtocol` can be passed to both
the `translate_srt_file()` and `translate_srt()`. It receives a `TranslationRequest` (segments, target language,
optional title metadata and story summary) and returns a `TranslationResponse`. `summarize()` produces the story
brief that is shared with every batch of a request.
```python
import asyncio
from subtaitles import (
    Lang,
    TranslatedSegment,
    TranslationRequest,
    TranslationResponse,
    translate_srt_file,
)
from subtaitles.providers.protocol import Progress


class MyCustomTranslator:
    async def translate(
        self,
        request: TranslationRequest,
        progress: Progress | None = None,
    ) -> TranslationResponse:
        # <implement whatever floats your boat>
        return TranslationResponse(
            segments=tuple(
                TranslatedSegment(
                    index=segment.index,
                    source=segment.text,
                    translation=segment.text,  # call your backend here
                    status="translated",
                )
                for segment in request.segments
            ),
            target=request.target,
        )

    async def summarize(self, request: TranslationRequest) -> str:
        # short story brief (characters, plot, settings), may be empty
        return ""


asyncio.run(
    translate_srt_file(
        path="/tmp/subtitles.en.srt",
        new_path="/tmp/subtitles.de.srt",
        translator=MyCustomTranslator(),
        target=Lang.DE,
    )
)
```

### CLI
`translate_srt_file` is exposed as a utility command for command line usage:
```bash
translate_subtitles --help
translate_subtitles --engine openai --output /tmp/subtitles.de.srt /tmp/subtitles.en.srt de
```
