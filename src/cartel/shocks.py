"""Forced price shocks in counterfactual copies (PRD FR-7; Tran & Yu 2610.28787 protocol).

At post-swap round `at_round` of a BRANCH, the incumbent's price is forced to factor x its price in the round
before (0.9 = cut, 1.1 = raise placebo) for that one round, then `follow_rounds` more rounds are played.
The copy resumes from the branch's own history, so the branch directory is never modified and rounds before
the shock are identical. Conditions 1-3 only (the bot control has no LLM incumbent).
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from cartel.fork import fork_run_async
from cartel.metrics import matching_ratio


def _other(firm: str, names) -> str:
    (inc,) = [n for n in names if n != firm]
    return inc


async def run_shock_async(
    branch_run_dir: str, at_round: int = 30, factor: float = 0.9, follow_rounds: int = 20, seed: int = 2000, **fork_kw
) -> str:
    d = Path(branch_run_dir)
    f = json.loads((d / "metadata.json").read_text())["fork"]
    if f.get("bot_price") is not None:
        raise ValueError("shocks need an LLM incumbent; this branch uses the bot control")
    hist = json.loads((d / "results.json").read_text())
    incumbent = _other(f["firm"], hist)
    shock_round = f["swap_round"] + at_round
    resume = shock_round - 1
    pre = hist[incumbent][str(resume)]["chosen_price"]
    return await fork_run_async(
        base_run_dir=str(d), swap_round=f["swap_round"], firm=f["firm"], successor_model=f["successor_model"],
        history=f["history"], notes=f["notes"], pinned_notes=f["pinned_notes"], seed=seed,
        post_rounds=follow_rounds + 1, resume_round=resume, forced_prices={shock_round: factor * pre},
        condition=f"shock{factor}", **fork_kw,
    )


def run_shock(*args, **kwargs) -> str:
    return asyncio.run(run_shock_async(*args, **kwargs))


def shock_response(shock_run_dir: str) -> dict:
    """Successor's reaction in the round after the shock, as a matching ratio vs the forced change."""
    d = Path(shock_run_dir)
    m = json.loads((d / "metadata.json").read_text())["fork"]
    hist = json.loads((d / "results.json").read_text())
    inc = _other(m["firm"], hist)
    shock_round = max(m["forced_prices"], key=int)
    sr = int(shock_round)
    px = lambda firm, r: hist[firm][str(r)]["chosen_price"]  # noqa: E731
    forced_change = px(inc, sr) - px(inc, sr - 1)
    succ_change = px(m["firm"], sr + 1) - px(m["firm"], sr - 1)  # reaction, vs its pre-shock price
    return {
        "shock_round": sr, "forced_change": forced_change, "successor_change": succ_change,
        "matching_ratio": matching_ratio(succ_change, forced_change),
    }
