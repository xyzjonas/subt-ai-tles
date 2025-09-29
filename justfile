#!/usr/bin/env just --justfile
export PATH := join(justfile_directory(), ".env", "bin") + ":" + env_var('PATH')

default:
  just lint
  just format
  just test
  just tox

install:
  uv sync --group dev

test:
  uv run pytest

tox:
  uv run tox -p

lint:
  uv run ruff check

format:
  uv run ruff format

upgrade:
  uv lock --upgrade

publish:
  uv build
  uv publish
