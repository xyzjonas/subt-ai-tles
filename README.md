# SUBT-AI-TLES
A simple wrapper around LLMs that provides language translation interface for subtitles (.srt). 

## Predefined implementations
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
        source=Lang.EN,
        target=Lang.DE
    )
)
```

```python
# behavior and configuration is controlled via environment variables
# all the used variables are defined int the environment module
from subtaitles import env
```

## Custom implementations
An arbitrary class that implements the `TranslateProtocol` can be passed to both 
the `translate_srt_file()` and `translate_srt()`
```python
import asyncio
from subtaitles import Lang, translate_srt_file

class MyCustomTranslator:
     async def translate(
        self, text: list[str], language_from: Lang, language_to: Lang,
    ) -> list[str]:
        # <implement whatever floats your boat>
        ...

asyncio.run(
    translate_srt_file(
        path="/tmp/subtitles.en.srt",
        new_path="/tmp/subtitles.de.srt",
        translator=MyCustomTranslator(),
        source=Lang.EN,
        target=Lang.DE
    )
)
```

## CLI
`translate_srt_file` is exposed as a utility command for command line usage:
```bash
translate_subtitles --help
translate_subtitles --engine openai /tmp/subtitles.en.srt /tmp/subtitles.de.srt en de
```
