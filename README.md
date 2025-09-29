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


## Directory mode
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
        source=Lang.EN,
        target=Lang.DE
    )
)
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
