#!/usr/bin/env just --justfile
export PATH := join(justfile_directory(), ".env", "bin") + ":" + env_var('PATH')

test:
  uv run pytest

upgrade:
  uv lock --upgrade