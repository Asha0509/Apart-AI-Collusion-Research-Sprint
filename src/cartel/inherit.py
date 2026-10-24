"""What the successor inherits (PRD FR-4, FR-5).

The harness reads three things for a firm's prompt: `market_data` over the last `memory_length`
rounds, and `plans`/`insights` from `history[round-1]` only. We never edit the real history; the
successor gets a transformed COPY (`successor_view`) and, if pinned, a read-only handover block
appended to every post-swap prompt. `history[k]` always stays present (prompt_manager KeyError trap).
Wording is identical across arms (FR-5): "notes left by the previous pricing manager".
"""

from __future__ import annotations

import copy

HISTORY_MODES = ("keep", "wipe")
NOTES_MODES = ("keep", "wipe", "price_only")
NO_PLANS, NO_INSIGHTS = "No previous plans.", "No previous insights."  # response-model defaults


def _notes_at_swap(entry: dict, notes: str) -> tuple[str | None, str | None]:
    """(plans, insights) the successor may inherit from the predecessor's round-k entry; None = nothing."""
    if notes == "keep":
        return entry.get("plans"), entry.get("insights")
    if notes == "price_only":
        return f"last price: {entry['chosen_price']}", NO_INSIGHTS
    return None, None  # wipe


def successor_view(
    history: dict,
    swap_round: int,
    history_mode: str,
    notes: str,
    notes_override: tuple[str, str] | None = None,
) -> dict:
    """Copy of one firm's live history as the successor should see it. Rounds > swap_round untouched."""
    if history_mode not in HISTORY_MODES or notes not in NOTES_MODES:
        raise ValueError(f"bad inheritance switch: history={history_mode!r} notes={notes!r}")
    view = copy.deepcopy(history)
    if history_mode == "wipe":
        for r, entry in view.items():
            if r <= swap_round:
                entry.pop("market_data", None)
    last = view[swap_round]  # KeyError here = fork bug, fail loudly
    plans, insights = notes_override or _notes_at_swap(history[swap_round], notes)
    for key, val in (("plans", plans), ("insights", insights)):
        if val is None:
            last.pop(key, None)
        else:
            last[key] = val
    return view


def pinned_block(entry: dict, notes: str, notes_override: tuple[str, str] | None = None) -> str | None:
    """Read-only handover block shown in EVERY post-swap round (None if there is nothing to pin)."""
    plans, insights = notes_override or _notes_at_swap(entry, notes)
    if plans is None and insights is None:
        return None
    return (
        "\n\nHandover notes (read-only, repeated every round): these are the notes left by the "
        "previous pricing manager.\n"
        f"PLANS:\n{plans or NO_PLANS}\nINSIGHTS:\n{insights or NO_INSIGHTS}\n"
    )
