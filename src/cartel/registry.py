"""Run registry + cost guard (PRD FR-12, NFR-2). Every run/branch gets a row before launch."""

from __future__ import annotations

import csv
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = Path(os.environ.get("CARTEL_REGISTRY") or ROOT / "logs" / "RUN_REGISTRY.csv")  # env override: dry runs
COSTLOG = ROOT / "logs" / "COST_LOG.csv"
FIELDS = [
    "run_id",
    "parent_id",
    "condition",
    "model_A",
    "model_B",
    "successor",
    "seed",
    "swap_round",
    "flags",
    "cost_usd",
    "status",
    "exclusion_reason",
    "output_path",
]
ASK_ABOVE_USD = 5.0  # batches above this need a human OK (CLAUDE.md rule 5)
IST = timezone(timedelta(hours=5, minutes=30))


def now_ist() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M IST")


def register_run(**row: object) -> None:
    unknown = set(row) - set(FIELDS)
    if unknown:
        raise ValueError(f"unknown registry fields: {unknown}")
    with REGISTRY.open("a", newline="") as f:
        csv.DictWriter(f, fieldnames=FIELDS).writerow({k: row.get(k, "") for k in FIELDS})


# Per-provider caps = REMAINING credit when caps were reset (human-reported dashboard balances, 24 Oct 21:00 IST).
# Only rows tagged `provider=<name>` in notes count, so older untagged rows (mixed estimates + dashboard actuals,
# which double-counted) do not. A batch's estimate counts until its actual is logged under the same batch name.
CAPS = {"modal": 73.0, "nebius": 7.0}


def spent_so_far(provider: str | None = None) -> float:
    if not COSTLOG.exists():
        return 0.0
    with COSTLOG.open() as f:
        rows = [r for r in csv.DictReader(f) if provider is None or f"provider={provider}" in (r.get("notes") or "")]
    by_batch: dict[str, float] = {}
    for r in rows:  # actual replaces estimate for the same batch
        if r["actual_usd"]:
            by_batch[r["batch"]] = float(r["actual_usd"])
        elif r["batch"] not in by_batch:
            by_batch[r["batch"]] = float(r["est_usd"] or 0)
    return sum(by_batch.values())


def guard_batch(batch: str, est_usd: float, approved: bool = False, provider: str = "modal") -> None:
    """Call BEFORE launching a paid batch. Raises if over the provider's cap or needs approval."""
    if provider not in CAPS:
        raise ValueError(f"unknown provider {provider!r}; caps: {CAPS}")
    total = spent_so_far(provider)
    if total + est_usd > CAPS[provider]:
        raise RuntimeError(f"{provider} cap: spent ${total:.2f} + est ${est_usd:.2f} > ${CAPS[provider]}")
    if est_usd > ASK_ABOVE_USD and not approved:
        raise RuntimeError(
            f"batch '{batch}' est ${est_usd:.2f} > ${ASK_ABOVE_USD}: ask a human, "
            "then call guard_batch(..., approved=True)"
        )
    log_cost(batch, est_usd, actual_usd=None, notes=f"pre-launch estimate; provider={provider}")


def log_cost(batch: str, est_usd: float, actual_usd: float | None, notes: str = "") -> None:
    total = spent_so_far() + (actual_usd if actual_usd is not None else 0.0)
    with COSTLOG.open("a", newline="") as f:
        csv.writer(f).writerow(
            [
                now_ist(),
                batch,
                f"{est_usd:.4f}",
                "" if actual_usd is None else f"{actual_usd:.4f}",
                f"{total:.4f}",
                notes,
            ]
        )
