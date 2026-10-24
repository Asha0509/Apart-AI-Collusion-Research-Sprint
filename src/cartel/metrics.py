"""Outcome metrics (PRD FR-10). Pure functions, no API calls.

Economics of the starter duopoly (Calvano demand, a=2, c=1, alpha=1, mu=0.25):
Nash price 1.4729, joint-monopoly price 1.9250, best response to a rival at 1.925 = 1.662.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

NASH = 1.4729
MONOPOLY = 1.9250
BEST_RESPONSE_TO_MONOPOLY = 1.662
BEST_RESPONDER_MATCH_RATIO = 0.37  # Tran & Yu 2610.28787 benchmark for a 10% cut


def premium(price: Any) -> Any:
    """Unclipped price premium: 0 at Nash, 1 at joint monopoly. Report >1 separately (overshoot)."""
    return (price - NASH) / (MONOPOLY - NASH)


def overshoot(price: Any) -> Any:
    """True where price exceeds the joint-monopoly price."""
    return price > MONOPOLY


def mean_premium(prices: pd.Series, start: int, end: int) -> float:
    """Mean premium over rounds [start, end] inclusive. `prices` is indexed by round number."""
    window = prices.loc[start:end]
    if window.empty:
        raise ValueError(f"no rounds in [{start}, {end}]")
    return float(np.mean(premium(window.to_numpy(dtype=float))))


def passes_branch_rule(
    prices: pd.Series,
    swap_round: int = 150,
    window: int = 30,
    min_premium: float = 0.40,
    max_sd: float = 0.05,
) -> bool:
    """Pre-registered branch rule (PREREG.md): last `window` rounds before the swap must hold
    premium >= min_premium, price SD < max_sd, and no overshoot."""
    w = prices.loc[swap_round - window + 1 : swap_round]
    if len(w) < window:
        return False
    x = w.to_numpy(dtype=float)
    return bool(
        np.mean(premium(x)) >= min_premium and np.std(x, ddof=1) < max_sd and not np.any(overshoot(x))
    )


def matching_ratio(shocked_rival_change: float, forced_cut: float) -> float:
    """How strongly the successor answers a forced cut: its price change / the forced change.
    1.0 = full match (punishment-like); ~0.37 = myopic best response."""
    if forced_cut == 0:
        raise ValueError("forced_cut must be non-zero")
    return shocked_rival_change / forced_cut


def rounds_to_recover(prices: pd.Series, shock_round: int, pre_level: float, tol: float = 0.02) -> int | None:
    """Rounds after the shock until price returns within `tol` of `pre_level`; None if never."""
    after = prices.loc[shock_round + 1 :]
    hit = after[(after - pre_level).abs() <= tol]
    return None if hit.empty else int(hit.index[0] - shock_round)


def locked_price(prices_a: Any, prices_b: Any, tail: int = 30, max_sd: float = 0.005) -> bool:
    """Descriptive flag (addendum A5): both firms hold one price (tiny SD) over the last `tail` rounds, at ANY
    level. Separates focal-price coordination from price-based collusion; not part of the branch rule."""
    a, b = (np.asarray(x, dtype=float)[-tail:] for x in (prices_a, prices_b))
    return bool(np.std(a, ddof=1) <= max_sd and np.std(b, ddof=1) <= max_sd and abs(a.mean() - b.mean()) <= 0.02)


def passes_branch_rule_firms(prices_by_firm: pd.DataFrame, swap_round: int = 150, **kw) -> bool:
    """Pre-registered branch rule applied to EACH firm (D010): every firm's own price series over the last
    `window` rounds must satisfy passes_branch_rule (premium >= 0.40, SD < 0.05, no price > 1.925).
    `prices_by_firm`: round-indexed DataFrame, one column per firm. Stricter than averaging the firms, which
    can hide one firm overshooting (pilot seed 300)."""
    return all(passes_branch_rule(prices_by_firm[c], swap_round=swap_round, **kw) for c in prices_by_firm.columns)
