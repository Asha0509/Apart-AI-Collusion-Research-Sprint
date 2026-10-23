#!/usr/bin/env bash
# 5-round smoke test (~$0.01): proves the key, model id and harness work. Run from repo root.
set -euo pipefail
MODEL="${1:-anthropic/claude-haiku-5.5}"
cd "$(dirname "$0")/../starter/algorithmic-pricing-llms"
echo "Smoke test with $MODEL (5 rounds)…"
uv run python experiments_synthetic/duopoly.py --model "$MODEL" --rounds 5 --seeds 0 --plot-every 0 -y
echo "OK. Output in starter/algorithmic-pricing-llms/experiments_synthetic/experiments_runs/2_agents/"
