#!/usr/bin/env bash
# Full local check: lint, types, tests (free). Run before every commit.
set -uo pipefail
cd "$(dirname "$0")/.."
uv run ruff check . && uv run pyright && uv run pytest -q -m "not slow"
