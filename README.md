# subt-ai-tles
A simple API/webpage wrapper for subtitles translation using various existing language models.

##### Con
```dotenv
# VARS needed for OpenAI models
OPENAI_API_KEY=<your-key-here>
OPENAPI_ORG_ID=<your-org-id-here>

# URL for you self-hosted Libretranslate instance
LIBRETRANSLATE_BASE_URL=http://localhost:5000

# VARS needed for the Deepl.io model
DEEPL_AUTH_KEY=96a44c58-a208-8a15-3175-c3a2087f80e2:fx
```

##### ...and run
```shell
poetry install
subtaitles --help

# cli tool
subtaitles translate --help

# server/webpage
subtaitles serve --help
```