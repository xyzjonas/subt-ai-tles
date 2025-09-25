#!/usr/bin/env just --justfile
export PATH := join(justfile_directory(), ".env", "bin") + ":" + env_var('PATH')

install:
  uv sync --group dev

test:
  uv run pytest

lint:
  uv run ruff check

format:
  uv run ruff format

upgrade:
  uv lock --upgrade

publish:
  uv build
  uv publish