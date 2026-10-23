#!/usr/bin/env bash
# Launch 8 pilot cartels in the background for the Sat 08:00 IST gate (~$1-2 total).
# Pilots are GATE-ONLY: they pick the base model. They are NOT reused as base runs
# (base runs need the FR-5 notes-wording patch first).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
H="$ROOT/starter/algorithmic-pricing-llms"
mkdir -p "$ROOT/logs/pilot"
ROUNDS="${ROUNDS:-150}"
MODELS=("anthropic/claude-haiku-5.5" "google/gemini-2.5-flash-lite")
echo "Checking model ids on OpenRouter…"
ids=$(curl -s https://openrouter.ai/api/v1/models | jq -r '.data[].id')
for m in "${MODELS[@]}"; do grep -qx "$m" <<<"$ids" && echo "  ✔ $m" || { echo "  ✘ $m not on OpenRouter — edit MODELS in this script"; exit 1; }; done
cd "$H"
for m in "${MODELS[@]}"; do
  tag=$(echo "$m" | tr '/:' '__')
  nohup uv run python experiments_synthetic/duopoly.py --model "$m" --rounds "$ROUNDS" \
        --seeds 0 1 2 3 --plot-every 25 -y > "$ROOT/logs/pilot/$tag.log" 2>&1 &
  echo "  launched 4 pilots: $m  (pid $!, log logs/pilot/$tag.log)"
done
echo "$(date '+%Y-%m-%d %H:%M') pilots launched: ${MODELS[*]} x seeds 0-3, $ROUNDS rounds" >> "$ROOT/logs/PLANNING_LOG.md"
echo "Check progress:  tail -f logs/pilot/*.log     Gate summary at 08:00:  uv run python scripts/gate.py"
