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
BUDGET_USD = 65.0  # OpenRouter hard cap for the whole project
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


def spent_so_far() -> float:
    if not COSTLOG.exists():
        return 0.0
    with COSTLOG.open() as f:
        rows = list(csv.DictReader(f))
    return sum(float(r["actual_usd"] or r["est_usd"] or 0) for r in rows)


def guard_batch(batch: str, est_usd: float, approved: bool = False) -> None:
    """Call BEFORE launching a paid batch. Raises if over budget or needs approval."""
    total = spent_so_far()
    if total + est_usd > BUDGET_USD:
        raise RuntimeError(f"budget cap: spent ${total:.2f} + est ${est_usd:.2f} > ${BUDGET_USD}")
    if est_usd > ASK_ABOVE_USD and not approved:
        raise RuntimeError(
            f"batch '{batch}' est ${est_usd:.2f} > ${ASK_ABOVE_USD}: ask a human, "
            "then call guard_batch(..., approved=True)"
        )
    log_cost(batch, est_usd, actual_usd=None, notes="pre-launch estimate")


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
