#!/usr/bin/env bash
# Full local check: lint, types, tests (free). Run before every commit.
set -uo pipefail
cd "$(dirname "$0")/.."
uv run ruff check . && uv run pyright && uv run pytest -q -m "not slow"
# harness-dependent tests (fork, inherit, shocks, sanitiser, parsing, usage) skip in the root env: run them in the harness env
(cd starter/algorithmic-pricing-llms && PYTHONPATH=../../src uv run --with pytest --with pandas python -m pytest -q -W ignore \
  ../../tests/test_fork_inherit.py ../../tests/test_agent_parse.py ../../tests/test_per_firm.py \
  ../../tests/test_fr5_wording.py ../../tests/test_sanitiser.py ../../tests/test_usage_tracking.py)
