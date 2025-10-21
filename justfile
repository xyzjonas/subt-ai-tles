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
  uv sync --group dev

test:
  uv run pytest

tox:
  uv run tox -p

lint *ARGS:
  uv run ruff check {{ARGS}}

format:
  uv run ruff format

upgrade:
  uv lock --upgrade

publish:
  uv build
  uv publish
