"""Sat 08:00 IST gate: summarise pilot runs against the pre-registered branch rule.

uv run python scripts/gate.py
"""

from pathlib import Path

import pandas as pd

from cartel.metrics import overshoot, passes_branch_rule, premium

HARNESS = Path(__file__).resolve().parents[1] / "starter/algorithmic-pricing-llms"
RUNS = HARNESS / "experiments_synthetic/experiments_runs/2_agents"

rows = []
for d in sorted(RUNS.glob("*")):
    f = d / "environment_history.parquet"
    if not f.exists():
        continue
    df = pd.read_parquet(f)
    meta = (d / "metadata.json").read_text()[:4000] if (d / "metadata.json").exists() else ""
    mean_price = pd.Series(df.groupby("round")["price"].mean())
    last = int(mean_price.index.to_numpy().max())
    ok = passes_branch_rule(mean_price, swap_round=min(150, last)) if last >= 30 else False
    tail = mean_price.loc[max(1, last - 29) : last].to_numpy(dtype=float)
    prices = df["price"].to_numpy(dtype=float)
    hint = next((m for m in ["haiku", "gemini", "gpt"] if m in meta), "?")
    rows.append(
        {
            "run": d.name,
            "rounds_done": last,
            "premium_last30": round(float(premium(tail).mean()), 3),
            "overshoot_any": bool(overshoot(prices).any()),
            "passes_rule": ok,
            "model_hint": hint,
        }
    )
out = pd.DataFrame(rows)
print(out.to_string(index=False) if not out.empty else "no runs found yet")
if not out.empty:
    print("\nGate G1: >=6 of 8 pilots on ONE model pass the rule (premium>=0.40, SD<0.05, no overshoot).")
    print(out.groupby("model_hint")["passes_rule"].agg(["sum", "count"]))
