#!/usr/bin/env just --justfile
export PATH := join(justfile_directory(), ".env", "bin") + ":" + env_var('PATH')

default:
  just lint
  just format
  just test
  just tox

translate-dir DIR:
  uv run translate_subtitles --dir --engine=openai --log-level=DEBUG {{ DIR }} '' en cs

install:
  uv sync --all-packages --group dev

test:
  uv run pytest

test-translate:
  uv run translate_subtitles --log-level=DEBUG src/lib/tests/data/rick-and-morty-S01E01.en.srt cs

tox:
  uv run tox -p

lint *ARGS:
  uv run ruff check {{ARGS}}

format:
  uv run ruff format

upgrade:
  uv lock --upgrade

publish:
  @rm -rf ./dist
  uv version --package subt-ai-tles --bump patch
  uv build --package subt-ai-tles
  uv publish dist/*

dev: db-upgrade
  uv run --package subt-ai-tles-app uvicorn app.main:app --reload

# Apply database migrations (DATABASE_URL from .env or the environment).
db-upgrade:
  uv run --package subt-ai-tles-app alembic -c src/app/backend/alembic.ini upgrade head

# Generate a migration from model changes: just db-revision "add foo column"
db-revision MESSAGE:
  uv run --package subt-ai-tles-app alembic -c src/app/backend/alembic.ini revision --autogenerate -m "{{ MESSAGE }}"

[working-directory: 'src/app/frontend']
ui:
    npm run dev

[working-directory: 'src/app/frontend']
app-frontend:
  npm run dev

docker-build:
  docker build -t subt-ai-tles-app .
