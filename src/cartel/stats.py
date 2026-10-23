"""Statistics (PRD FR-11). Unit of analysis = base run. Never treat rounds as samples."""

from __future__ import annotations

import itertools
import math

import numpy as np


def sign_flip_permutation(diffs: np.ndarray, alternative: str = "greater") -> float:
    """Exact sign-flip permutation test on paired per-base-run differences.

    diffs[i] = metric(arm A, base i) - metric(arm B, base i). Exact for n <= 20 (2^n flips).
    """
    d = np.asarray(diffs, dtype=float)
    n = len(d)
    if n == 0:
        raise ValueError("no differences")
    if n > 20:
        raise ValueError("use a Monte-Carlo version for n > 20")
    obs = d.mean()
    flips = np.array(list(itertools.product([1, -1], repeat=n)))
    null = (flips * d).mean(axis=1)
    if alternative == "greater":
        return float((null >= obs - 1e-12).mean())
    if alternative == "less":
        return float((null <= obs + 1e-12).mean())
    return float((np.abs(null) >= abs(obs) - 1e-12).mean())


def cluster_bootstrap_ci(
    per_base_values: np.ndarray, n_resamples: int = 10_000, level: float = 0.95, seed: int = 0
) -> tuple[float, float]:
    """Percentile CI for the mean, resampling whole base runs (clusters) with replacement.
    Pass one value per base run (e.g. the paired difference averaged over that base's replicates)."""
    v = np.asarray(per_base_values, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(v), size=(n_resamples, len(v)))
    means = v[idx].mean(axis=1)
    a = (1 - level) / 2
    return float(np.quantile(means, a)), float(np.quantile(means, 1 - a))


def minimum_detectable_effect(sd_of_diffs: float, n: int, alpha: float = 0.05, power: float = 0.8) -> float:
    """Approximate one-sided MDE for a paired design (normal approximation). Fill into PREREG.md."""
    from scipy.stats import norm

    return float((norm.ppf(1 - alpha) + norm.ppf(power)) * sd_of_diffs / math.sqrt(n))


def declare_inheritance(diffs: np.ndarray, placebo_diffs: np.ndarray, min_effect: float = 0.15) -> dict:
    """Apply the pre-registered decision rule exactly as written in PREREG.md.

    diffs = premium(notes only) - premium(clean slate), per base run.
    placebo_diffs = premium(notes only) - premium(price-only placebo), per base run.
    """
    p = sign_flip_permutation(diffs)
    lo, hi = cluster_bootstrap_ci(diffs)
    effect = float(np.mean(diffs))
    beats_placebo = float(np.mean(placebo_diffs)) > 0
    return {
        "effect": effect,
        "p_value": p,
        "ci95": (lo, hi),
        "beats_placebo": beats_placebo,
        "declared": bool(p < 0.05 and lo > 0 and effect >= min_effect and beats_placebo),
    }
