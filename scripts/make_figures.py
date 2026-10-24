"""Figures 2-4 from results/processed/ + the copied raw runs (PRD FR-13). Run scripts/analyse.py first.

  uv run python scripts/make_figures.py
Figure 1 (schematic) is drawn separately; this script never invents data: an empty input skips that figure.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cartel import figures
from cartel.stats import cluster_bootstrap_ci

ROOT = Path(__file__).resolve().parents[1]
PROC, RAW = ROOT / "results/processed", ROOT / "results/raw"
LABELS = {  # plain-language names (CLAUDE.md §7)
    "no_swap": "No swap", "full_inheritance": "Keeps notes + history", "notes_only": "Keeps notes only",
    "history_only": "Keeps history only", "clean_slate": "Clean slate", "price_only": "Last price only (placebo)",
    "sanitised": "Sanitised notes", "bot_full": "Scripted rival (notes + history)", "bot_notes": "Scripted rival (notes)",
    "fresh_same_notes": "Same model, fresh, keeps notes", "fresh_same_clean": "Same model, fresh, clean slate",
}
MAIN = ["no_swap", "fresh_same_notes", "notes_only", "clean_slate", "full_inheritance"]  # <=5 lines + bot (PRD FR-13)


def successor_paths(branches: pd.DataFrame) -> dict:
    """Mean successor price by round per condition (incumbent's pre-swap rounds included for context)."""
    out = {}
    for cond in MAIN + ["bot_full"]:
        runs = branches.loc[branches.condition == cond, "run"]
        series = []
        for r in runs:
            f = RAW / r / "environment_history.parquet"
            if f.exists():
                df = pd.read_parquet(f)
                series.append(df[df.agent == "Firm A"].set_index("round")["price"])
        if series:
            out[LABELS[cond]] = pd.concat(series, axis=1).mean(axis=1)
    return out


def fig1() -> None:
    """Schematic (no data): cartel forms, one firm's model is replaced, what the successor may inherit, outcomes."""
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    fig, ax = plt.subplots(figsize=(7, 2.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")

    def box(x, y, w, h, text, fc="0.93"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05", fc=fc, ec="0.3", lw=0.8))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=6.5, wrap=True)

    def arrow(x0, y0, x1, y1):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=8, lw=0.8, color="0.2"))

    ax.text(1.5, 3.75, "Rounds 1-150: a cartel forms", ha="center", fontsize=7, weight="bold")
    box(0.2, 2.4, 2.6, 1.0, "Firm A and Firm B\n(same model, gpt-oss-120b)\nraise prices above\nthe competitive level")
    ax.text(5.0, 3.75, "Round 150: Firm A's model is replaced", ha="center", fontsize=7, weight="bold")
    box(3.6, 2.4, 2.8, 1.0, "Successor model\n- another company's model\n- or a fresh copy of the same model")
    box(3.6, 0.6, 2.8, 1.3, "What the successor inherits\n(switched on or off):\n- handover notes left by the\n  previous pricing manager\n- price history", fc="0.98")
    ax.text(8.5, 3.75, "Rounds 151-250: outcome", ha="center", fontsize=7, weight="bold")
    box(7.3, 2.75, 2.5, 0.65, "Cartel continues")
    box(7.3, 1.85, 2.5, 0.65, "Prices fall back to competition")
    box(7.3, 0.95, 2.5, 0.65, "Overshoot above the monopoly price")
    arrow(2.8, 2.9, 3.6, 2.9)
    arrow(5.0, 1.9, 5.0, 2.4)
    for y in (3.07, 2.17, 1.27):
        arrow(6.4, 2.9, 7.3, y)
    ax.text(5.0, 0.25, "Firm B keeps its model and memory in every condition", ha="center", fontsize=6, style="italic")
    figures.save(fig, "fig1_schematic")


def fig2(branches: pd.DataFrame, swap_round: int) -> None:
    paths = successor_paths(branches)
    if not paths:
        return print("fig2 skipped: no branch runs")
    fig, ax = plt.subplots(figsize=(6, 3.2))
    figures.trajectory(ax, paths, swap_round=swap_round)
    ax.set_title("Price set by the replaced firm, before and after the swap", fontsize=8)
    figures.save(fig, "fig2_trajectory")


def fig3(tab: pd.DataFrame) -> None:
    if tab.empty or "clean_slate" not in tab:
        return print("fig3 skipped: no clean-slate arm")
    conds = [c for c in ["full_inheritance", "notes_only", "fresh_same_notes", "fresh_same_clean", "history_only", "price_only", "sanitised", "no_swap"] if c in tab]
    means, errs = [], []
    for c in conds:
        d = (tab[c] - tab["clean_slate"]).dropna().to_numpy()
        if len(d) < 2:
            means.append(np.nan)
            errs.append((0, 0))
            continue
        lo, hi = cluster_bootstrap_ci(d)
        means.append(d.mean())
        errs.append((d.mean() - lo, hi - d.mean()))
    fig, ax = plt.subplots(figsize=(5, 3))
    y = np.arange(len(conds))
    ax.barh(y, means, xerr=np.array(errs).T, color="0.6")
    ax.axvline(0, c="k", lw=0.8)
    ax.set_yticks(y, [LABELS[c] for c in conds], fontsize=7)
    ax.set_xlabel("Price premium above clean slate (0 = competitive, 1 = monopoly gap)")
    figures.save(fig, "fig3_inheritance_effect")


def fig4(shocks: pd.DataFrame) -> None:
    if shocks.empty:
        return print("fig4 skipped: no shock runs")
    fig, ax = plt.subplots(figsize=(4, 3))
    for cond, g in shocks.groupby("condition"):
        ax.scatter([cond] * len(g), g.matching_ratio, s=12)
    ax.axhline(0.37, ls=":", c="grey")
    ax.text(-0.4, 0.37, "best response", fontsize=6, va="bottom", c="grey")
    ax.axhline(1.0, ls=":", c="grey")
    ax.text(-0.4, 1.0, "full match", fontsize=6, va="bottom", c="grey")
    ax.set_ylabel("Successor's response / forced price change")
    figures.save(fig, "fig4_forced_cut")


def main() -> None:
    (ROOT / "figures").mkdir(exist_ok=True)
    import os

    os.chdir(ROOT)  # figures.save writes to ./figures
    fig1()
    br = pd.read_csv(PROC / "branches.csv") if (PROC / "branches.csv").stat().st_size > 1 else pd.DataFrame()
    tab = pd.read_csv(PROC / "premium_by_base.csv", index_col=0) if (PROC / "premium_by_base.csv").exists() else pd.DataFrame()
    sh = pd.read_csv(PROC / "shocks.csv") if (PROC / "shocks.csv").stat().st_size > 1 else pd.DataFrame()
    swap = 150
    if not br.empty:
        raw = RAW / br.run.iloc[0] / "metadata.json"
        swap = json.loads(raw.read_text())["fork"]["swap_round"] if raw.exists() else swap
    fig2(br, swap)
    fig3(tab)
    fig4(sh)


if __name__ == "__main__":
    main()
