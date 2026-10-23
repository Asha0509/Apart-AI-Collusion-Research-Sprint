"""Figure helpers (PRD FR-13). One style for every figure; plain-language labels only."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import scienceplots  # noqa: E402,F401  (registers styles)

from .metrics import MONOPOLY, NASH  # noqa: E402

plt.style.use(["science", "no-latex", "bright"])


def trajectory(ax, series_by_label: dict, swap_round: int | None = 150) -> None:
    """Price paths with Nash/monopoly bands and an 'agent replaced' marker. Labels drawn on lines."""
    for label, s in series_by_label.items():
        (line,) = ax.plot(s.index, s.values, lw=1.4)
        ax.annotate(
            label,
            (s.index[-1], s.values[-1]),
            xytext=(4, 0),
            textcoords="offset points",
            color=line.get_color(),
            fontsize=7,
            va="center",
        )
    ax.axhline(NASH, ls=":", c="grey", lw=0.8)
    ax.axhline(MONOPOLY, ls=":", c="grey", lw=0.8)
    ax.text(ax.get_xlim()[0], NASH, " competitive", fontsize=6, va="bottom", c="grey")
    ax.text(ax.get_xlim()[0], MONOPOLY, " monopoly", fontsize=6, va="bottom", c="grey")
    if swap_round is not None:
        ax.axvline(swap_round, c="k", lw=0.8)
        ax.text(swap_round, ax.get_ylim()[1], " agent replaced", fontsize=7, va="top")
    ax.set_xlabel("Round")
    ax.set_ylabel("Price")


def save(fig, name: str) -> None:
    fig.savefig(f"figures/{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(f"figures/{name}.pdf", bbox_inches="tight")
