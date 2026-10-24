#!/usr/bin/env bash
# Launch pilot cartels in the background for the Sat 08:00 IST gate.
# GATE-ONLY: they pick the base model. NOT reused as base runs.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
H="$ROOT/starter/algorithmic-pricing-llms"
mkdir -p "$ROOT/logs/pilot"
ROUNDS="${ROUNDS:-150}"
read -r -a MODELS <<< "${PILOT_MODELS:?set PILOT_MODELS to space-separated model ids}"
SEEDS="${SEEDS:-0 1 2 3}"
cd "$H"
for m in "${MODELS[@]}"; do
  tag=$(echo "$m" | tr '/:' '__')
  nohup uv run python experiments_synthetic/duopoly.py --model "$m" --rounds "$ROUNDS" \
        --seeds $SEEDS --plot-every 25 -y > "$ROOT/logs/pilot/$tag.log" 2>&1 &
  echo "  launched (seeds $SEEDS): $m  (pid $!, log logs/pilot/$tag.log)"
  sleep 5  # belt-and-braces with the pid patch in storage.py
done
echo "$(date '+%Y-%m-%d %H:%M') pilots launched: ${MODELS[*]} seeds $SEEDS, $ROUNDS rounds" >> "$ROOT/logs/PLANNING_LOG.md"
echo "Progress: tail -f logs/pilot/*.log    Gate: uv run python scripts/gate.py"
