"""Build results/processed/ from raw run dirs (KICKOFF prompt 8). Primary test ONLY via cartel.stats.declare_inheritance.

  uv run python scripts/analyse.py [--runs DIR]   (default: the harness runs dir)
Includes a branch only if its registry status (latest row) is "done" and its condition is a PRD arm; smoke and
dry-run runs are never counted. Every included run dir is copied to results/raw/ (never edited).
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from cartel.metrics import mean_premium, overshoot, passes_branch_rule, rounds_to_recover
from cartel.stats import cluster_bootstrap_ci, declare_inheritance, sign_flip_permutation

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "starter/algorithmic-pricing-llms/experiments_synthetic/experiments_runs/2_agents"
OUT = ROOT / "results/processed"
ARMS = {"no_swap", "full_inheritance", "notes_only", "history_only", "clean_slate", "price_only", "sanitised",
        "bot_full", "bot_notes", "fresh_same_notes", "fresh_same_clean"}
POST = 100  # pre-registered: successor's mean over post-swap rounds 1-100


def latest_registry(path: Path = ROOT / "logs/RUN_REGISTRY.csv") -> dict[str, dict]:
    with path.open() as f:
        return {r["run_id"]: r for r in csv.DictReader(f)}  # later rows overwrite earlier ones


def prices(run: Path) -> pd.DataFrame:
    """round x agent price table."""
    df = pd.read_parquet(run / "environment_history.parquet")
    return df.pivot_table(index="round", columns="agent", values="price")


def branch_rows(runs: list[Path], reg: dict) -> pd.DataFrame:
    rows = []
    for d in runs:
        meta = json.loads((d / "metadata.json").read_text())
        f = meta.get("fork")
        r = reg.get(d.name, {})
        if not f or f.get("forced_prices") or r.get("status") != "done" or f.get("condition") not in ARMS:
            continue
        k, firm = f["swap_round"], f["firm"]
        p = prices(d)
        prof = pd.read_parquet(d / "environment_history.parquet").pivot_table(index="round", columns="agent", values="profit")
        rows.append(dict(
            run=d.name, base=Path(f["base_run_dir"]).name, condition=f["condition"], seed=f["seed"],
            successor=f["successor_model"],
            premium=mean_premium(p[firm], k + 1, k + POST),
            overshoot_share=float(overshoot(p[firm].loc[k + 1:k + POST]).mean()),
            successor_profit=float(prof[firm].loc[k + 1:k + POST].mean()),
        ))
    return pd.DataFrame(rows)


def per_base(df: pd.DataFrame) -> pd.DataFrame:
    """Unit of analysis = base run: average replicates within base x condition."""
    return df.groupby(["base", "condition"])["premium"].mean().unstack("condition")


def paired(tab: pd.DataFrame, a: str, b: str) -> np.ndarray:
    if a not in tab or b not in tab:
        return np.array([])
    both = tab[[a, b]].dropna()
    return (both[a] - both[b]).to_numpy()


def primary(tab: pd.DataFrame) -> dict:
    need = tab[["notes_only", "clean_slate", "price_only"]].dropna() if {"notes_only", "clean_slate", "price_only"} <= set(tab) else pd.DataFrame()
    if len(need) < 2:
        return {"status": "not enough complete bases", "n_bases": int(len(need))}
    res = declare_inheritance((need.notes_only - need.clean_slate).to_numpy(), (need.notes_only - need.price_only).to_numpy())
    return res | {"n_bases": int(len(need)), "bases": list(need.index)}


def contrast(tab: pd.DataFrame, a: str, b: str) -> dict:
    d = paired(tab, a, b)
    if len(d) < 2:
        return {"n_bases": int(len(d))}
    lo, hi = cluster_bootstrap_ci(d)
    return {"n_bases": int(len(d)), "mean_diff": float(d.mean()), "ci95": (lo, hi), "p_two_sided": sign_flip_permutation(d, "two-sided")}


def shocks(runs: list[Path], reg: dict) -> pd.DataFrame:
    from cartel.shocks import shock_response

    rows = []
    for d in runs:
        f = json.loads((d / "metadata.json").read_text()).get("fork") or {}
        if not f.get("forced_prices") or reg.get(d.name, {}).get("status") != "done":
            continue
        r = shock_response(str(d))
        p = prices(d)[f["firm"]]
        rows.append(r | {"run": d.name, "condition": f.get("condition"), "base": Path(f["base_run_dir"]).name,
                         "rounds_to_recover": rounds_to_recover(p, r["shock_round"], p.loc[r["shock_round"] - 1])})
    return pd.DataFrame(rows)


def table1(runs: list[Path], reg: dict) -> pd.DataFrame:
    """Positive control: every launched base run (registry condition == base)."""
    rows = []
    for d in runs:
        meta = json.loads((d / "metadata.json").read_text())
        if meta.get("fork") or "seed" not in meta:
            continue
        r = next((x for x in reg.values() if x["condition"] == "base" and x["seed"] == str(meta["seed"])
                  and x["model_A"] in meta["agents_models"].values()), None)
        if r is None:
            continue
        p = prices(d).mean(axis=1)
        last = int(p.index.max())
        rows.append(dict(run=d.name, model=r["model_A"], seed=meta["seed"], rounds=last,
                         formed_cartel=bool(last >= 150 and passes_branch_rule(p, 150)),
                         overshot=bool(overshoot(p.loc[121:150]).any()) if last >= 150 else None,
                         price_r150=float(p.loc[150]) if last >= 150 else None))
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=str(RUNS))
    args = ap.parse_args()
    runs = sorted(Path(args.runs).glob("*"))
    reg = latest_registry()
    OUT.mkdir(parents=True, exist_ok=True)
    br = branch_rows(runs, reg)
    br.to_csv(OUT / "branches.csv", index=False)
    tab = per_base(br) if not br.empty else pd.DataFrame()
    tab.to_csv(OUT / "premium_by_base.csv")
    out = {"primary": primary(tab) if not tab.empty else {"status": "no branches"}}
    for name, (a, b) in {"full_vs_bot": ("full_inheritance", "bot_full"), "sanitiser_reduction": ("notes_only", "sanitised"),
                         "notes_vs_history": ("notes_only", "history_only"), "noswap_vs_clean": ("no_swap", "clean_slate"),
                         "fresh_same_notes_vs_clean": ("fresh_same_notes", "fresh_same_clean"),
                         "different_vs_same_model_notes": ("notes_only", "fresh_same_notes")}.items():
        out[name] = contrast(tab, a, b) if not tab.empty else {}
    sh = shocks(runs, reg)
    sh.to_csv(OUT / "shocks.csv", index=False)
    t1 = table1(runs, reg)
    t1.to_csv(OUT / "table1_positive_control.csv", index=False)
    (OUT / "summary.json").write_text(json.dumps(out, indent=2, default=str))
    used = set(br.get("run", [])) | set(br.get("base", [])) | set(sh.get("run", [])) | set(t1.get("run", []))
    for name in used:
        src, dst = Path(args.runs) / name, ROOT / "results/raw" / name
        if src.exists() and not dst.exists():
            shutil.copytree(src, dst)
    print(json.dumps(out, indent=2, default=str))
    print(f"branches={len(br)} shocks={len(sh)} table1_rows={len(t1)} -> {OUT}")


if __name__ == "__main__":
    main()
